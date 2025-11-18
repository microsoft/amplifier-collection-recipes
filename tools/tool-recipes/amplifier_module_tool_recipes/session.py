"""Session management and persistence."""

import datetime
import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from .models import Recipe


def generate_session_id() -> str:
    """Generate unique session ID following W3C Trace Context pattern.

    Format: {span}-{timestamp}_{identifier}
    Example: 7cc787dd22d54f6c-20251118-114317_recipe

    This follows the same W3C Trace Context principles as sub-sessions:
    - Span ID (16 hex chars) for distributed tracing compatibility
    - Timestamp for human readability and chronological sorting
    - Identifier suffix ("recipe") for session type clarity
    - Underscore separator before identifier (consistent with sub-session agent names)

    Returns:
        Session ID string in W3C Trace Context compatible format
    """
    # Generate 16-char hex span ID (W3C Trace Context standard)
    span_id = uuid.uuid4().hex[:16]

    # Human-readable timestamp (YYYYMMDD-HHMMSS)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # Format: {span}-{timestamp}_{identifier}
    # Underscore before identifier (consistent with sub-session agent names)
    return f"{span_id}-{timestamp}_recipe"


def get_project_slug(project_path: Path) -> str:
    """Convert project path to slug for session directory."""
    # Convert absolute path to slug
    abs_path = project_path.resolve()
    slug = str(abs_path).replace("/", "-").replace("\\", "-")

    # Remove leading dash
    if slug.startswith("-"):
        slug = slug[1:]

    return slug


class SessionManager:
    """Manages recipe session persistence and cleanup."""

    def __init__(self, base_dir: Path, auto_cleanup_days: int = 7):
        """
        Initialize session manager.

        Args:
            base_dir: Base directory for all sessions (~/.amplifier/projects)
            auto_cleanup_days: Auto-delete sessions older than N days
        """
        self.base_dir = Path(base_dir).expanduser()
        self.auto_cleanup_days = auto_cleanup_days

    def get_sessions_dir(self, project_path: Path) -> Path:
        """Get sessions directory for project."""
        slug = get_project_slug(project_path)
        return self.base_dir / slug / "recipe-sessions"

    def create_session(self, recipe: Recipe, project_path: Path, recipe_path: Path | None = None) -> str:
        """
        Create new session.

        Args:
            recipe: Recipe being executed
            project_path: Current project directory
            recipe_path: Optional path to recipe file (will be copied to session)

        Returns:
            session_id: Unique session identifier
        """
        session_id = generate_session_id()
        session_dir = self.get_session_dir(session_id, project_path)

        # Create session directory
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save copy of recipe to session directory
        if recipe_path and recipe_path.exists():
            import shutil

            shutil.copy2(recipe_path, session_dir / "recipe.yaml")

        # Initialize state
        state = {
            "session_id": session_id,
            "recipe_name": recipe.name,
            "recipe_version": recipe.version,
            "started": datetime.datetime.now().isoformat(),
            "current_step_index": 0,
            "context": recipe.context.copy(),
            "completed_steps": [],
            "project_path": str(project_path.resolve()),
        }

        # Save initial state
        self.save_state(session_id, project_path, state)

        return session_id

    def get_session_dir(self, session_id: str, project_path: Path) -> Path:
        """Get session directory path."""
        sessions_dir = self.get_sessions_dir(project_path)
        return sessions_dir / session_id

    def save_state(self, session_id: str, project_path: Path, state: dict[str, Any]) -> None:
        """Save session state to disk."""
        session_dir = self.get_session_dir(session_id, project_path)
        state_file = session_dir / "state.json"

        # Write with retry (cloud sync issues)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_state(self, session_id: str, project_path: Path) -> dict[str, Any]:
        """Load session state from disk."""
        session_dir = self.get_session_dir(session_id, project_path)
        state_file = session_dir / "state.json"

        if not state_file.exists():
            raise FileNotFoundError(f"Session state not found: {session_id}")

        with open(state_file, encoding="utf-8") as f:
            return json.load(f)

    def session_exists(self, session_id: str, project_path: Path) -> bool:
        """Check if session exists."""
        session_dir = self.get_session_dir(session_id, project_path)
        state_file = session_dir / "state.json"
        return state_file.exists()

    def list_sessions(self, project_path: Path) -> list[dict[str, Any]]:
        """
        List all sessions for project.

        Returns list of session info dicts with:
        - session_id
        - recipe_name
        - started
        - current_step_index
        - completed_steps
        """
        sessions_dir = self.get_sessions_dir(project_path)

        if not sessions_dir.exists():
            return []

        sessions = []
        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue

            state_file = session_dir / "state.json"
            if not state_file.exists():
                continue

            try:
                with open(state_file, encoding="utf-8") as f:
                    state = json.load(f)

                sessions.append(
                    {
                        "session_id": state.get("session_id", session_dir.name),
                        "recipe_name": state.get("recipe_name", "unknown"),
                        "started": state.get("started"),
                        "current_step_index": state.get("current_step_index", 0),
                        "completed_steps": state.get("completed_steps", []),
                    }
                )
            except Exception:
                # Skip corrupted sessions
                continue

        # Sort by started time (newest first)
        sessions.sort(key=lambda s: s.get("started", ""), reverse=True)

        return sessions

    def cleanup_old_sessions(self, project_path: Path) -> int:
        """
        Delete sessions older than auto_cleanup_days.

        Returns number of sessions deleted.
        """
        sessions_dir = self.get_sessions_dir(project_path)

        if not sessions_dir.exists():
            return 0

        cutoff = datetime.datetime.now() - datetime.timedelta(days=self.auto_cleanup_days)
        deleted_count = 0

        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue

            state_file = session_dir / "state.json"
            if not state_file.exists():
                continue

            try:
                with open(state_file, encoding="utf-8") as f:
                    state = json.load(f)

                started_str = state.get("started")
                if not started_str:
                    continue

                started = datetime.datetime.fromisoformat(started_str.replace("Z", "+00:00"))

                if started < cutoff:
                    # Delete old session
                    shutil.rmtree(session_dir)
                    deleted_count += 1

            except Exception:
                # Skip problematic sessions
                continue

        return deleted_count
