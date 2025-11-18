"""Recipe data models and YAML parsing."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Step:
    """Represents a single step in a recipe workflow."""

    id: str
    agent: str
    prompt: str
    mode: str | None = None
    output: str | None = None
    timeout: int = 600
    retry: dict[str, Any] | None = None
    on_error: str = "fail"
    agent_config: dict[str, Any] | None = None
    depends_on: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Validate step structure and constraints."""
        errors = []

        # Required fields
        if not self.id:
            errors.append("Step missing required field: id")
        if not self.agent:
            errors.append(f"Step '{self.id}': missing required field: agent")
        if not self.prompt:
            errors.append(f"Step '{self.id}': missing required field: prompt")

        # Field constraints
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
            steps.append(Step(**step_data))

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

        # Version format (basic semver check)
        if self.version:
            parts = self.version.split(".")
            if len(parts) < 3:
                errors.append("Recipe version must follow semver format (MAJOR.MINOR.PATCH)")

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

        return errors

    def get_step(self, step_id: str) -> Step | None:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
