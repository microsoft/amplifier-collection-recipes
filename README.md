# Amplifier Recipes Collection

**Multi-step AI agent orchestration for repeatable workflows**

The Recipes Collection provides a tool and agent for creating, executing, and managing multi-step AI agent workflows. Define once, run anywhere, resume anytime.

## What Are Recipes?

**Recipes** are declarative YAML specifications that define multi-step agent workflows with:

- **Sequential execution** - Steps run in order, each building on the previous
- **Agent delegation** - Each step spawns a sub-agent with specific capabilities
- **State persistence** - Sessions automatically checkpoint for resumability
- **Context accumulation** - Later steps access earlier results
- **Conditional routing** - Branch based on step outcomes (future enhancement)

**Use cases:**

- Code review workflows (analyze → identify issues → suggest fixes)
- Dependency upgrades (audit → plan → validate → apply)
- Test generation (analyze code → generate tests → validate coverage)
- Documentation evolution (analyze → simulate learner → improve)
- Research synthesis (extract → compare → synthesize → validate)

## Components

This collection provides:

1. **tool-recipes** - Tool module for executing recipes
2. **recipe-author** - Agent for conversational recipe creation
3. **Complete documentation** - Schema, guide, best practices, troubleshooting
4. **Examples** - 10+ working recipes across domains
5. **Templates** - Starter recipes for common patterns

## Installation

Install the collection using Amplifier's collection management:

```bash
# Install from GitHub
amplifier collection add git+https://github.com/microsoft/amplifier-collection-recipes@main

# Or install from local path during development
amplifier collection add /path/to/amplifier-collection-recipes
```

This installs:

- tool-recipes module (available to all profiles)
- recipe-author agent (available globally for conversational authoring)

## Using the Collection

After installation, you need to activate recipe capabilities in your profile.

### Use the Provided Profile (Recommended)

The collection includes a `recipe-dev` profile that bundles the tool configuration and AI context:

```bash
amplifier profile use recipes:recipe-dev
```

This profile extends `developer-expertise:dev` and adds recipe execution capabilities.

### Add to Your Existing Profile

Alternatively, add the tool to your own profile by editing your profile file:

```yaml
tools:
  - module: tool-recipes
    source: recipes:modules/tool-recipes
    config:
      session_dir: ~/.amplifier/projects
      auto_cleanup_days: 7
```

### Verify Installation

Check that the tool is available:

```bash
# Validate a recipe to confirm tool is working
amplifier run "validate recipe examples/simple-analysis-recipe.yaml"

# List available profiles
amplifier profile list
```

## Quick Start

### Execute a Recipe

Use natural language via your main profile:

```bash
amplifier run "execute the recipe at examples/code-review-recipe.yaml on src/auth.py"
```

The main profile interprets your request and invokes the tool-recipes module with the recipe path.

### Create a Recipe

Use the recipe-author agent conversationally:

```bash
amplifier run "I need to create a recipe for upgrading Python dependencies"
```

The agent guides you through:

1. Understanding your workflow
2. Defining steps and agent capabilities
3. Generating the YAML specification
4. Validating and saving the recipe

### Recipe Example

```yaml
name: "code-review-flow"
description: "Multi-stage code review with analysis, feedback, and validation"
version: "1.0.0"

steps:
  - id: "analyze"
    agent: "zen-architect"
    mode: "ANALYZE"
    prompt: "Analyze the code at {{file_path}} for complexity, maintainability, and philosophy alignment"
    output: "analysis"

  - id: "suggest-improvements"
    agent: "zen-architect"
    mode: "ARCHITECT"
    prompt: "Based on this analysis: {{analysis}}, suggest concrete improvements"
    output: "improvements"

  - id: "validate-suggestions"
    agent: "zen-architect"
    mode: "REVIEW"
    prompt: "Review these improvement suggestions: {{improvements}} for feasibility and value"
    output: "validation"
```

Run it:

```bash
amplifier run "execute examples/code-review-recipe.yaml with file_path=src/auth.py"
```

## Session Management

### Persistence

Recipe sessions persist to:

```
~/.amplifier/projects/<slugified-project-path>/recipe-sessions/
  recipe_20251118_143022_a3f2/
    state.json        # Current state and step outputs
    recipe.yaml       # The recipe being executed
```

### Resumability

If execution is interrupted, resume from last checkpoint:

```bash
amplifier run "resume recipe session recipe_20251118_143022_a3f2"
```

### Auto-Cleanup

Sessions older than 7 days are automatically cleaned up (configurable via tool config).

## Documentation

- **[Recipe Schema Reference](docs/RECIPE_SCHEMA.md)** - Complete YAML specification
- **[Recipes Guide](docs/RECIPES_GUIDE.md)** - Concepts and patterns
- **[Best Practices](docs/BEST_PRACTICES.md)** - Design guidelines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Examples Catalog](docs/EXAMPLES_CATALOG.md)** - Browse all example recipes

## Examples

The `examples/` directory includes working recipes for:

- **Code Review** - Multi-stage analysis and improvement suggestions
- **Dependency Upgrade** - Audit, plan, validate, and apply upgrades
- **Test Generation** - Analyze code and generate comprehensive tests
- **Documentation Evolution** - Improve tutorials based on learner simulation
- **Research Synthesis** - Extract, compare, and synthesize research
- **Bug Investigation** - Systematic root cause analysis
- **Refactoring Planning** - Architecture assessment and refactor plans
- **Security Audit** - Multi-perspective security analysis

See [Examples Catalog](docs/EXAMPLES_CATALOG.md) for complete descriptions.

## Templates

The `templates/` directory provides starter recipes:

- **simple-recipe.yaml** - Basic sequential workflow
- **multi-step-recipe.yaml** - Complex multi-stage processing
- **error-handling-recipe.yaml** - Retry and error handling patterns

See `examples/conditional-workflow.yaml` for conditional execution patterns.

Copy, customize, and run.

## Creating Your Own Recipes

### Option 1: Use recipe-author Agent (Recommended)

```bash
amplifier run "create a recipe for analyzing API documentation"
```

The agent guides you conversationally through recipe creation.

### Option 2: Manual YAML Creation

1. Copy a template from `templates/`
2. Customize steps, agents, and prompts
3. Validate with recipe-author: `amplifier run "validate recipe.yaml"`
4. Execute: `amplifier run "execute recipe.yaml"`

See [Recipes Guide](docs/RECIPES_GUIDE.md) for detailed instructions.

## Advanced Features

### Context Variables

Steps access previous outputs via template variables:

```yaml
steps:
  - id: "analyze"
    prompt: "Analyze {{file_path}}"
    output: "analysis"

  - id: "improve"
    prompt: "Given this analysis: {{analysis}}, suggest improvements"
    output: "improvements"
```

### Custom Agent Configurations

Override agent settings per-step:

```yaml
steps:
  - id: "creative-brainstorm"
    agent: "zen-architect"
    agent_config:
      providers:
        - module: "provider-anthropic"
          config:
            temperature: 0.8 # More creative
    prompt: "Brainstorm alternative architectures"
```

### Parallel foreach

Run iterations concurrently for faster multi-perspective analysis:

```yaml
context:
  perspectives: ["security", "performance", "maintainability"]

steps:
  - id: "multi-analysis"
    foreach: "{{perspectives}}"
    as: "perspective"
    parallel: true  # All perspectives analyzed simultaneously
    collect: "analyses"
    agent: "zen-architect"
    prompt: "Analyze code from {{perspective}} perspective"
```

## Tool Configuration

Configure tool-recipes in your profile:

```yaml
tools:
  - module: tool-recipes
    source: git+https://github.com/microsoft/amplifier-collection-recipes@main
    config:
      session_dir: ~/.amplifier/projects # Base directory for sessions
      auto_cleanup_days: 7 # Auto-delete sessions after N days
      checkpoint_frequency: "per_step" # Checkpoint after each step
```

## Philosophy

Recipes follow Amplifier's core principles:

- **Mechanism, not policy** - Tool executes recipes; recipes define policy
- **Composable** - Steps are independent, reusable across recipes
- **Observable** - Full event logging of execution
- **Resumable** - Checkpointing enables recovery from failures
- **Declarative** - YAML specification separates intent from execution

## Troubleshooting

**Issue: "Recipe session not found"**

- Session may have been auto-cleaned (>7 days old)
- Check session dir: `~/.amplifier/projects/<slug>/recipe-sessions/`
- List active sessions: `amplifier run "list recipe sessions"`

**Issue: "Agent not found: agent-name"**

- Ensure agent is installed and available in your profile
- List available agents: `amplifier agents list`
- Add agent to your profile or install required collection

**Issue: "Step failed: connection timeout"**

- Recipe resumes from last checkpoint
- Re-run: `amplifier run "resume recipe session <session-id>"`
- Failed step will retry automatically

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for complete solutions.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

---

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
