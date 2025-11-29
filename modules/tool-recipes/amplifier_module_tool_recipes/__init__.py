"""Amplifier tool-recipes module - Execute multi-step AI agent recipes."""

import logging
from pathlib import Path
from typing import Any

from amplifier_core import ModuleCoordinator
from amplifier_core import ToolResult

from .executor import RecipeExecutor
from .models import Recipe
from .session import SessionManager
from .validator import validate_recipe

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """
    Mount tool-recipes module.

    Args:
        coordinator: Amplifier coordinator
        config: Optional tool configuration
    """
    config = config or {}

    # Initialize session manager
    base_dir = Path(config.get("session_dir", "~/.amplifier/projects")).expanduser()
    auto_cleanup_days = config.get("auto_cleanup_days", 7)
    session_manager = SessionManager(base_dir, auto_cleanup_days)

    # Initialize executor
    executor = RecipeExecutor(coordinator, session_manager)

    # Create tool instance
    tool = RecipesTool(executor, session_manager, coordinator, config)

    # Register tool in mount_points
    coordinator.mount_points["tools"][tool.name] = tool

    logger.info("Mounted tool-recipes")


class RecipesTool:
    """Tool for executing, resuming, and managing recipe workflows."""

    def __init__(
        self,
        executor: RecipeExecutor,
        session_manager: SessionManager,
        coordinator: ModuleCoordinator,
        config: dict[str, Any],
    ):
        """Initialize tool."""
        self.executor = executor
        self.session_manager = session_manager
        self.coordinator = coordinator
        self.config = config

    @property
    def name(self) -> str:
        return "recipes"

    @property
    def description(self) -> str:
        return """Execute multi-step AI agent recipes (workflows).

Recipes are declarative YAML specifications that define multi-step agent workflows with:
- Sequential execution with state persistence
- Agent delegation with context accumulation
- Automatic checkpointing for resumability
- Error handling and retry logic

Operations:
- execute: Run a recipe from YAML file
- resume: Resume interrupted session
- list: List active sessions
- validate: Validate recipe structure

Example:
  Execute recipe: {{"operation": "execute", "recipe_path": "examples/code-review.yaml", "context": {{"file_path": "src/auth.py"}}}}
  Resume session: {{"operation": "resume", "session_id": "recipe_20251118_143022_a3f2"}}
  List sessions: {{"operation": "list"}}
  Validate recipe: {{"operation": "validate", "recipe_path": "my-recipe.yaml"}}"""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["execute", "resume", "list", "validate"],
                    "description": "Operation to perform: execute recipe, resume session, list sessions, or validate recipe",
                },
                "recipe_path": {
                    "type": "string",
                    "description": "Path to recipe YAML file (required for 'execute' and 'validate' operations)",
                },
                "context": {
                    "type": "object",
                    "description": "Context variables for recipe execution (for 'execute' operation)",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID to resume (required for 'resume' operation)",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """
        Execute tool operation.

        Args:
            input: Tool input with 'operation' field

        Returns:
            ToolResult with operation results
        """
        operation = input.get("operation")

        try:
            if operation == "execute":
                return await self._execute_recipe(input)
            if operation == "resume":
                return await self._resume_recipe(input)
            if operation == "list":
                return await self._list_sessions(input)
            if operation == "validate":
                return await self._validate_recipe(input)
            return ToolResult(
                success=False,
                error={"message": f"Unknown operation: {operation}"},
            )
        except Exception as e:
            logger.error(f"Recipe tool error: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error={"message": str(e), "type": type(e).__name__},
            )

    async def _execute_recipe(self, input: dict[str, Any]) -> ToolResult:
        """Execute recipe from YAML file."""
        recipe_path_str = input.get("recipe_path")
        if not recipe_path_str:
            return ToolResult(success=False, error={"message": "recipe_path is required for execute operation"})

        recipe_path = Path(recipe_path_str)
        context_vars = input.get("context", {})

        # Determine project path (current working directory)
        project_path = Path.cwd()

        # Load recipe
        try:
            recipe = Recipe.from_yaml(recipe_path)
        except Exception as e:
            return ToolResult(success=False, error={"message": f"Failed to load recipe: {str(e)}"})

        # Validate recipe
        validation = validate_recipe(recipe, self.coordinator)
        if not validation.is_valid:
            return ToolResult(
                success=False,
                error={
                    "message": "Recipe validation failed",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                },
            )

        # Execute recipe (pass recipe_path for sub-recipe resolution)
        try:
            final_context = await self.executor.execute_recipe(
                recipe, context_vars, project_path, recipe_path=recipe_path
            )

            return ToolResult(
                success=True,
                output={
                    "status": "completed",
                    "recipe": recipe.name,
                    "session_id": final_context["session"]["id"],
                    "context": final_context,
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Recipe execution failed: {str(e)}",
                    "type": type(e).__name__,
                },
            )

    async def _resume_recipe(self, input: dict[str, Any]) -> ToolResult:
        """Resume interrupted recipe session."""
        session_id = input.get("session_id")
        if not session_id:
            return ToolResult(success=False, error={"message": "session_id is required for resume operation"})

        project_path = Path.cwd()

        # Check session exists
        if not self.session_manager.session_exists(session_id, project_path):
            return ToolResult(
                success=False,
                error={"message": f"Session not found: {session_id}"},
            )

        # Validate session exists
        try:
            _ = self.session_manager.load_state(session_id, project_path)
        except Exception as e:
            return ToolResult(success=False, error={"message": f"Failed to load session: {str(e)}"})

        # Load recipe from session
        session_dir = self.session_manager.get_session_dir(session_id, project_path)
        recipe_file = session_dir / "recipe.yaml"

        if not recipe_file.exists():
            return ToolResult(
                success=False,
                error={"message": f"Recipe file not found in session: {session_id}"},
            )

        try:
            recipe = Recipe.from_yaml(recipe_file)
        except Exception as e:
            return ToolResult(success=False, error={"message": f"Failed to load recipe from session: {str(e)}"})

        # Resume execution
        try:
            final_context = await self.executor.execute_recipe(
                recipe, context_vars={}, project_path=project_path, session_id=session_id
            )

            return ToolResult(
                success=True,
                output={
                    "status": "resumed",
                    "recipe": recipe.name,
                    "session_id": session_id,
                    "context": final_context,
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={
                    "message": f"Failed to resume recipe: {str(e)}",
                    "type": type(e).__name__,
                },
            )

    async def _list_sessions(self, input: dict[str, Any]) -> ToolResult:
        """List active recipe sessions."""
        project_path = Path.cwd()

        try:
            sessions = self.session_manager.list_sessions(project_path)

            return ToolResult(
                success=True,
                output={
                    "sessions": sessions,
                    "count": len(sessions),
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": f"Failed to list sessions: {str(e)}"},
            )

    async def _validate_recipe(self, input: dict[str, Any]) -> ToolResult:
        """Validate recipe without executing."""
        recipe_path_str = input.get("recipe_path")
        if not recipe_path_str:
            return ToolResult(success=False, error={"message": "recipe_path is required for validate operation"})

        recipe_path = Path(recipe_path_str)

        try:
            # Load recipe
            recipe = Recipe.from_yaml(recipe_path)

            # Validate
            validation = validate_recipe(recipe, self.coordinator)

            if validation.is_valid:
                return ToolResult(
                    success=True,
                    output={
                        "status": "valid",
                        "recipe": recipe.name,
                        "version": recipe.version,
                        "warnings": validation.warnings,
                    },
                )
            return ToolResult(
                success=False,
                error={
                    "message": "Recipe validation failed",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": f"Failed to validate recipe: {str(e)}"},
            )
