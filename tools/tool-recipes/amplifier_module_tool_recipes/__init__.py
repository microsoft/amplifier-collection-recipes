"""Amplifier tool-recipes module - Execute multi-step AI agent recipes."""

from pathlib import Path
from typing import Any

from .executor import RecipeExecutor
from .models import Recipe, Step
from .session import SessionManager
from .validator import ValidationResult, validate_recipe

__all__ = [
    "mount",
    "Recipe",
    "Step",
    "RecipeExecutor",
    "SessionManager",
    "validate_recipe",
    "ValidationResult",
]


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> "RecipesTool":
    """
    Mount tool-recipes module.

    Args:
        coordinator: Amplifier coordinator
        config: Optional tool configuration

    Returns:
        RecipesTool instance
    """
    config = config or {}

    # Initialize session manager
    base_dir = Path(config.get("session_dir", "~/.amplifier/projects")).expanduser()
    auto_cleanup_days = config.get("auto_cleanup_days", 7)
    session_manager = SessionManager(base_dir, auto_cleanup_days)

    # Initialize executor
    executor = RecipeExecutor(coordinator, session_manager)

    # Create and return tool instance
    tool = RecipesTool(executor, session_manager, coordinator, config)

    return tool


class RecipesTool:
    """Tool for executing, resuming, and managing recipe workflows."""

    def __init__(
        self, executor: RecipeExecutor, session_manager: SessionManager, coordinator: Any, config: dict[str, Any]
    ):
        """Initialize tool."""
        self.executor = executor
        self.session_manager = session_manager
        self.coordinator = coordinator
        self.config = config

    def get_schemas(self) -> list[dict[str, Any]]:
        """Return tool schemas for all operations."""
        return [
            {
                "name": "recipe_execute",
                "description": "Execute a recipe from YAML file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipe_path": {
                            "type": "string",
                            "description": "Path to recipe YAML file",
                        },
                        "context": {
                            "type": "object",
                            "description": "Context variables for recipe execution",
                        },
                    },
                    "required": ["recipe_path"],
                },
            },
            {
                "name": "recipe_resume",
                "description": "Resume interrupted recipe session",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to resume",
                        },
                    },
                    "required": ["session_id"],
                },
            },
            {
                "name": "recipe_list",
                "description": "List active recipe sessions",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "recipe_validate",
                "description": "Validate recipe YAML without executing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipe_path": {
                            "type": "string",
                            "description": "Path to recipe YAML file to validate",
                        },
                    },
                    "required": ["recipe_path"],
                },
            },
        ]

    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Execute tool operation.

        Args:
            tool_name: Name of tool operation
            arguments: Tool arguments

        Returns:
            Tool result dict
        """
        if tool_name == "recipe_execute":
            return await self._execute_recipe(arguments)
        elif tool_name == "recipe_resume":
            return await self._resume_recipe(arguments)
        elif tool_name == "recipe_list":
            return await self._list_sessions(arguments)
        elif tool_name == "recipe_validate":
            return await self._validate_recipe(arguments)
        else:
            raise ValueError(f"Unknown tool operation: {tool_name}")

    async def _execute_recipe(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute recipe from YAML file."""
        recipe_path = Path(arguments["recipe_path"])
        context_vars = arguments.get("context", {})

        # Determine project path (current working directory)
        project_path = Path.cwd()

        # Load recipe
        recipe = Recipe.from_yaml(recipe_path)

        # Validate recipe
        validation = validate_recipe(recipe, self.coordinator)
        if not validation.is_valid:
            return {
                "status": "error",
                "message": "Recipe validation failed",
                "errors": validation.errors,
                "warnings": validation.warnings,
            }

        # Execute recipe
        final_context = await self.executor.execute_recipe(recipe, context_vars, project_path, recipe_path=recipe_path)

        return {
            "status": "success",
            "message": f"Recipe '{recipe.name}' completed successfully",
            "context": final_context,
            "session_id": final_context["session"]["id"],
        }

    async def _resume_recipe(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Resume interrupted recipe session."""
        session_id = arguments["session_id"]
        project_path = Path.cwd()

        # Load session state
        if not self.session_manager.session_exists(session_id, project_path):
            return {
                "status": "error",
                "message": f"Session not found: {session_id}",
            }

        state = self.session_manager.load_state(session_id, project_path)

        # Load recipe from session
        session_dir = self.session_manager.get_session_dir(session_id, project_path)
        recipe_file = session_dir / "recipe.yaml"

        if not recipe_file.exists():
            return {
                "status": "error",
                "message": f"Recipe file not found in session: {session_id}",
            }

        recipe = Recipe.from_yaml(recipe_file)

        # Resume execution
        final_context = await self.executor.execute_recipe(
            recipe, context_vars={}, project_path=project_path, session_id=session_id
        )

        return {
            "status": "success",
            "message": f"Session '{session_id}' resumed and completed",
            "context": final_context,
            "session_id": session_id,
        }

    async def _list_sessions(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """List active recipe sessions."""
        project_path = Path.cwd()

        sessions = self.session_manager.list_sessions(project_path)

        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions),
        }

    async def _validate_recipe(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate recipe without executing."""
        recipe_path = Path(arguments["recipe_path"])

        try:
            # Load recipe
            recipe = Recipe.from_yaml(recipe_path)

            # Validate
            validation = validate_recipe(recipe, self.coordinator)

            if validation.is_valid:
                return {
                    "status": "success",
                    "message": f"Recipe '{recipe.name}' is valid",
                    "warnings": validation.warnings,
                }
            else:
                return {
                    "status": "error",
                    "message": "Recipe validation failed",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load recipe: {str(e)}",
                "errors": [str(e)],
            }
