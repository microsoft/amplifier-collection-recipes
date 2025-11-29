"""Recipe data models and YAML parsing."""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Literal

import yaml


@dataclass
class RecursionConfig:
    """Recursion protection configuration for recipe composition."""

    max_depth: int = 5  # Default: 5, configurable 1-20
    max_total_steps: int = 100  # Default: 100, configurable 1-1000

    def validate(self) -> list[str]:
        """Validate recursion config."""
        errors = []
        if not 1 <= self.max_depth <= 20:
            errors.append(f"recursion.max_depth must be 1-20, got {self.max_depth}")
        if not 1 <= self.max_total_steps <= 1000:
            errors.append(f"recursion.max_total_steps must be 1-1000, got {self.max_total_steps}")
        return errors


@dataclass
class Step:
    """Represents a single step in a recipe workflow."""

    id: str
    # Agent step fields (required when type="agent")
    agent: str | None = None
    prompt: str | None = None
    mode: str | None = None
    agent_config: dict[str, Any] | None = None

    # Recipe composition fields (required when type="recipe")
    type: Literal["agent", "recipe"] = "agent"
    recipe: str | None = None  # Path to sub-recipe file
    step_context: dict[str, Any] | None = None  # Context to pass to sub-recipe (YAML: "context")

    # Common fields
    output: str | None = None
    condition: str | None = None
    foreach: str | None = None
    as_var: str | None = None  # Maps to 'as' in YAML (as is Python reserved)
    collect: str | None = None
    parallel: bool = False  # Run all foreach iterations concurrently
    max_iterations: int = 100
    timeout: int = 600
    retry: dict[str, Any] | None = None
    on_error: str = "fail"
    depends_on: list[str] = field(default_factory=list)

    # Per-step recursion override (for recipe steps only)
    recursion: RecursionConfig | None = None

    def validate(self) -> list[str]:
        """Validate step structure and constraints."""
        errors = []

        # Required fields
        if not self.id:
            errors.append("Step missing required field: id")

        # Type-specific validation
        if self.type == "agent":
            # Agent steps require agent and prompt
            if not self.agent:
                errors.append(f"Step '{self.id}': agent steps require 'agent' field")
            if not self.prompt:
                errors.append(f"Step '{self.id}': agent steps require 'prompt' field")
            # Agent steps cannot have recipe-specific fields
            if self.recipe:
                errors.append(f"Step '{self.id}': agent steps cannot have 'recipe' field")
            if self.step_context:
                errors.append(f"Step '{self.id}': agent steps cannot have 'context' field")
        elif self.type == "recipe":
            # Recipe steps require recipe path
            if not self.recipe:
                errors.append(f"Step '{self.id}': recipe steps require 'recipe' field")
            # Recipe steps cannot have agent-specific fields
            if self.agent:
                errors.append(f"Step '{self.id}': recipe steps cannot have 'agent' field")
            if self.prompt:
                errors.append(f"Step '{self.id}': recipe steps cannot have 'prompt' field")
            if self.mode:
                errors.append(f"Step '{self.id}': recipe steps cannot have 'mode' field")
            # Validate recursion config if present
            if self.recursion:
                errors.extend(self.recursion.validate())
        else:
            errors.append(f"Step '{self.id}': type must be 'agent' or 'recipe', got '{self.type}'")

        # Field constraints (common to both types)
        if self.timeout <= 0:
            errors.append(f"Step '{self.id}': timeout must be positive")

        if self.on_error not in ("fail", "continue", "skip_remaining"):
            errors.append(f"Step '{self.id}': on_error must be 'fail', 'continue', or 'skip_remaining'")

        # Output name validation
        if self.output:
            if not self.output.replace("_", "").isalnum():
                errors.append(f"Step '{self.id}': output name must be alphanumeric with underscores")
            if self.output in ("recipe", "session", "step"):
                errors.append(f"Step '{self.id}': output name '{self.output}' is reserved")

        # Retry validation
        if self.retry:
            max_attempts = self.retry.get("max_attempts", 1)
            if not isinstance(max_attempts, int) or max_attempts <= 0:
                errors.append(f"Step '{self.id}': retry.max_attempts must be positive integer")

            backoff = self.retry.get("backoff", "exponential")
            if backoff not in ("exponential", "linear"):
                errors.append(f"Step '{self.id}': retry.backoff must be 'exponential' or 'linear'")

        # Loop validation
        if self.foreach:
            if "{{" not in self.foreach:
                errors.append(f"Step '{self.id}': foreach must contain a variable reference (e.g., '{{{{items}}}}')")
            if self.as_var and not self.as_var.replace("_", "").isalnum():
                errors.append(f"Step '{self.id}': 'as' must be a valid variable name")
            if self.collect and not self.collect.replace("_", "").isalnum():
                errors.append(f"Step '{self.id}': 'collect' must be a valid variable name")
            if self.max_iterations <= 0:
                errors.append(f"Step '{self.id}': max_iterations must be positive")

        # Parallel validation
        if self.parallel and not self.foreach:
            errors.append(f"Step '{self.id}': parallel requires foreach")

        return errors


@dataclass
class Recipe:
    """Represents a complete recipe specification."""

    name: str
    description: str
    version: str
    steps: list[Step]
    author: str | None = None
    created: str | None = None
    updated: str | None = None
    tags: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    recursion: RecursionConfig | None = None  # Recipe-level recursion config

    @classmethod
    def from_yaml(cls, path: Path) -> "Recipe":
        """Load recipe from YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Recipe file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Recipe YAML must be a dictionary")

        # Parse steps
        steps_data = data.get("steps", [])
        if not isinstance(steps_data, list):
            raise ValueError("'steps' must be a list")

        steps = []
        for step_data in steps_data:
            if not isinstance(step_data, dict):
                raise ValueError("Each step must be a dictionary")
            step_data_copy = dict(step_data)

            # Map 'as' to 'as_var' since 'as' is Python reserved keyword
            if "as" in step_data_copy:
                step_data_copy["as_var"] = step_data_copy.pop("as")

            # Map 'context' to 'step_context' (context at step level is for sub-recipes)
            if "context" in step_data_copy:
                step_data_copy["step_context"] = step_data_copy.pop("context")

            # Parse step-level recursion config if present
            if "recursion" in step_data_copy and isinstance(step_data_copy["recursion"], dict):
                step_data_copy["recursion"] = RecursionConfig(**step_data_copy["recursion"])

            steps.append(Step(**step_data_copy))

        # Parse recipe-level recursion config if present
        recursion_config = None
        if "recursion" in data and isinstance(data["recursion"], dict):
            recursion_config = RecursionConfig(**data["recursion"])

        # Create recipe
        recipe = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", ""),
            steps=steps,
            author=data.get("author"),
            created=data.get("created"),
            updated=data.get("updated"),
            tags=data.get("tags", []),
            context=data.get("context", {}),
            recursion=recursion_config,
        )

        return recipe

    def validate(self) -> list[str]:
        """Validate recipe structure and constraints."""
        errors = []

        # Required fields
        if not self.name:
            errors.append("Recipe missing required field: name")
        if not self.description:
            errors.append("Recipe missing required field: description")
        if not self.version:
            errors.append("Recipe missing required field: version")

        # Name constraints
        if self.name and not self.name.replace("-", "").replace("_", "").isalnum():
            errors.append("Recipe name must be alphanumeric with hyphens/underscores")

        # Version format (strict semver check - MAJOR.MINOR.PATCH only)
        if self.version:
            # Check for v prefix (not allowed)
            if self.version.startswith("v"):
                errors.append("Recipe version must follow semver format without 'v' prefix (use '1.0.0' not 'v1.0.0')")
            # Check for pre-release or build metadata (not allowed for simplicity)
            elif "-" in self.version or "+" in self.version:
                errors.append(
                    "Recipe version must follow simple semver format (MAJOR.MINOR.PATCH only, no pre-release tags)"
                )
            else:
                parts = self.version.split(".")
                if len(parts) != 3:
                    errors.append("Recipe version must follow semver format (MAJOR.MINOR.PATCH)")
                elif not all(part.isdigit() for part in parts):
                    errors.append("Recipe version parts must be numeric (e.g., '1.0.0' not '1.a.0')")

        # Steps
        if not self.steps:
            errors.append("Recipe must have at least one step")

        # Validate each step
        for step in self.steps:
            step_errors = step.validate()
            errors.extend(step_errors)

        # Check step ID uniqueness
        step_ids = [step.id for step in self.steps]
        duplicates = [sid for sid in step_ids if step_ids.count(sid) > 1]
        if duplicates:
            errors.append(f"Duplicate step IDs: {', '.join(set(duplicates))}")

        # Validate depends_on references
        step_id_set = set(step_ids)
        for step in self.steps:
            for dep_id in step.depends_on:
                if dep_id not in step_id_set:
                    errors.append(f"Step '{step.id}': depends_on references unknown step '{dep_id}'")

        # Check for circular dependencies (simple check)
        for step in self.steps:
            if step.id in step.depends_on:
                errors.append(f"Step '{step.id}': cannot depend on itself")

        # Validate recipe-level recursion config
        if self.recursion:
            errors.extend(self.recursion.validate())

        return errors

    def get_step(self, step_id: str) -> Step | None:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
