"""Recipe execution engine."""

import asyncio
import datetime
import re
from pathlib import Path
from typing import Any

from .models import Recipe, Step
from .session import SessionManager


class SkipRemainingError(Exception):
    """Raised when step fails with on_error='skip_remaining'."""

    pass


class RecipeExecutor:
    """Executes recipe workflows with checkpointing and resumption."""

    def __init__(self, coordinator: Any, session_manager: SessionManager):
        """
        Initialize executor.

        Args:
            coordinator: Amplifier coordinator for agent spawning
            session_manager: Session persistence manager
        """
        self.coordinator = coordinator
        self.session_manager = session_manager

    async def execute_recipe(
        self,
        recipe: Recipe,
        context_vars: dict[str, Any],
        project_path: Path,
        session_id: str | None = None,
        recipe_path: Path | None = None,
    ) -> dict[str, Any]:
        """
        Execute recipe with checkpointing and resumption.

        Args:
            recipe: Recipe to execute
            context_vars: Initial context variables (merged with recipe.context)
            project_path: Current project directory
            session_id: Optional session ID to resume
            recipe_path: Optional path to recipe file (saved to session)

        Returns:
            Final context dict with all step outputs
        """
        # Create or resume session
        is_resuming = session_id is not None

        if is_resuming:
            state = self.session_manager.load_state(session_id, project_path)
            current_step_index = state["current_step_index"]
            context = state["context"]
            completed_steps = state.get("completed_steps", [])
            session_started = state["started"]
        else:
            session_id = self.session_manager.create_session(recipe, project_path, recipe_path)
            current_step_index = 0
            context = {**recipe.context, **context_vars}
            completed_steps = []
            session_started = datetime.datetime.now().isoformat()

        # Add metadata to context
        context["recipe"] = {
            "name": recipe.name,
            "version": recipe.version,
            "description": recipe.description,
        }
        context["session"] = {
            "id": session_id,
            "started": session_started,
            "project": str(project_path.resolve()),
        }

        try:
            # Execute remaining steps
            for i in range(current_step_index, len(recipe.steps)):
                step = recipe.steps[i]

                # Add step metadata to context
                context["step"] = {"id": step.id, "index": i}

                # Execute step with retry
                try:
                    result = await self.execute_step_with_retry(step, context)

                    # Store output if specified
                    if step.output:
                        context[step.output] = result

                    # Update completed steps and session state
                    completed_steps.append(step.id)

                    state = {
                        "session_id": session_id,
                        "recipe_name": recipe.name,
                        "recipe_version": recipe.version,
                        "started": context["session"]["started"],
                        "current_step_index": i + 1,
                        "context": context,
                        "completed_steps": completed_steps,
                        "project_path": str(project_path.resolve()),
                    }

                    # Checkpoint after each step
                    self.session_manager.save_state(session_id, project_path, state)

                except SkipRemainingError:
                    # Skip remaining steps
                    break

        except Exception as e:
            # Save state even on error for resumption
            if "state" in locals():
                self.session_manager.save_state(session_id, project_path, state)
            raise

        # Cleanup old sessions
        self.session_manager.cleanup_old_sessions(project_path)

        return context

    async def execute_step_with_retry(self, step: Step, context: dict[str, Any]) -> Any:
        """
        Execute step with retry logic.

        Args:
            step: Step to execute
            context: Current context variables

        Returns:
            Step result

        Raises:
            Exception if all retries fail and on_error='fail'
            SkipRemainingError if on_error='skip_remaining'
        """
        retry_config = step.retry or {}
        max_attempts = retry_config.get("max_attempts", 1)
        backoff = retry_config.get("backoff", "exponential")
        delay = retry_config.get("initial_delay", 5)
        max_delay = retry_config.get("max_delay", 300)

        last_error = None

        for attempt in range(max_attempts):
            try:
                result = await self.execute_step(step, context)
                return result

            except Exception as e:
                last_error = e

                # If final attempt or not retryable
                if attempt == max_attempts - 1:
                    # Handle based on on_error strategy
                    if step.on_error == "fail":
                        raise
                    elif step.on_error == "continue":
                        return None  # Continue with None result
                    elif step.on_error == "skip_remaining":
                        raise SkipRemainingError() from e

                # Wait before retry
                await asyncio.sleep(min(delay, max_delay))

                # Adjust delay for next attempt
                if backoff == "exponential":
                    delay *= 2
                # Linear backoff keeps same delay

        # Shouldn't reach here, but handle just in case
        if step.on_error == "fail":
            raise last_error
        return None

    async def execute_step(self, step: Step, context: dict[str, Any]) -> Any:
        """
        Execute single step by spawning sub-agent.

        Args:
            step: Step to execute
            context: Current context variables

        Returns:
            Step result from agent
        """
        # Substitute variables in prompt
        prompt = self.substitute_variables(step.prompt, context)

        # Build agent spawn parameters
        agent_params = {"prompt": prompt}

        # Add mode if specified (via context injection)
        if step.mode:
            mode_instruction = f"MODE: {step.mode}\n\n"
            agent_params["prompt"] = mode_instruction + prompt

        # Add agent config overrides if specified
        if step.agent_config:
            agent_params["config"] = step.agent_config

        # Spawn sub-agent via coordinator
        # Note: Actual coordinator.spawn_agent API may differ
        # This follows the pattern from planning docs
        result = await self.coordinator.spawn_agent(agent_name=step.agent, **agent_params)

        return result

    def substitute_variables(self, template: str, context: dict[str, Any]) -> str:
        """
        Replace {{variable}} references with context values.

        Args:
            template: String with {{variable}} placeholders
            context: Dict with variable values

        Returns:
            String with variables substituted

        Raises:
            ValueError if variable undefined
        """
        pattern = r"\{\{(\w+(?:\.\w+)?)\}\}"

        def replace(match: re.Match) -> str:
            var_ref = match.group(1)

            # Handle nested references (recipe.name, session.id, etc.)
            if "." in var_ref:
                parts = var_ref.split(".")
                value = context
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        raise ValueError(
                            f"Undefined variable: {{{{{var_ref}}}}}. "
                            f"Available variables: {', '.join(sorted(context.keys()))}"
                        )
                return str(value)

            # Handle direct references
            if var_ref not in context:
                available = ", ".join(sorted(context.keys()))
                raise ValueError(f"Undefined variable: {{{{{var_ref}}}}}. Available variables: {available}")

            return str(context[var_ref])

        return re.sub(pattern, replace, template)
