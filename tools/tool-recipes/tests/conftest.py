"""Shared test fixtures for models tests."""

import pytest
from pathlib import Path
from amplifier_module_tool_recipes.models import Step, Recipe


# ===== STEP FIXTURES =====


@pytest.fixture
def valid_step():
    """Minimal valid step."""
    return Step(id="test_step", agent="test_agent", prompt="Test prompt")


@pytest.fixture
def full_step():
    """Step with all fields populated."""
    return Step(
        id="full_step",
        agent="test_agent",
        prompt="Full test",
        mode="chat",
        output="result",
        timeout=300,
        retry={"max_attempts": 3, "backoff": "exponential"},
        on_error="continue",
        agent_config={"model": "gpt-4"},
        depends_on=["step0"],
    )


# ===== RECIPE FIXTURES =====


@pytest.fixture
def valid_recipe():
    """Minimal valid recipe."""
    return Recipe(
        name="test-recipe",
        description="Test description",
        version="1.0.0",
        steps=[Step(id="step1", agent="test", prompt="Test")],
    )


@pytest.fixture
def multi_step_recipe():
    """Recipe with dependency chain."""
    return Recipe(
        name="multi-step",
        description="Multiple steps",
        version="1.0.0",
        steps=[
            Step(id="step1", agent="analyzer", prompt="Analyze"),
            Step(id="step2", agent="synthesizer", prompt="Synthesize", depends_on=["step1"]),
            Step(id="step3", agent="improver", prompt="Improve", depends_on=["step2"]),
        ],
    )


# ===== YAML FIXTURES =====


@pytest.fixture
def valid_recipe_yaml():
    """Valid recipe YAML content."""
    return """name: test-recipe
description: Test description
version: 1.0.0
steps:
  - id: step1
    agent: test_agent
    prompt: Test prompt
"""


@pytest.fixture
def valid_recipe_file(tmp_path, valid_recipe_yaml):
    """Temporary YAML file with valid recipe."""
    file = tmp_path / "recipe.yaml"
    file.write_text(valid_recipe_yaml)
    return file


@pytest.fixture
def invalid_yaml_file(tmp_path):
    """YAML with syntax errors."""
    file = tmp_path / "invalid.yaml"
    file.write_text("name: test\n  bad: indentation:\n[")
    return file


@pytest.fixture
def sample_steps():
    """Collection of test steps."""
    return [
        Step(id="step1", agent="analyzer", prompt="First"),
        Step(id="step2", agent="synthesizer", prompt="Second", depends_on=["step1"]),
        Step(id="step3", agent="improver", prompt="Third", depends_on=["step1", "step2"]),
    ]
