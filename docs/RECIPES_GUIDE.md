# Recipes Guide

**Conceptual guide to creating and using Amplifier recipes**

This guide explains what recipes are, when to use them, and how to design effective multi-step workflows.

## Table of Contents

- [What Are Recipes?](#what-are-recipes)
- [When to Use Recipes](#when-to-use-recipes)
- [Core Concepts](#core-concepts)
- [Design Patterns](#design-patterns)
- [Creating Your First Recipe](#creating-your-first-recipe)
- [Advanced Techniques](#advanced-techniques)
- [Testing and Validation](#testing-and-validation)

---

## What Are Recipes?

**Recipes** are declarative YAML specifications that orchestrate multi-step AI agent workflows. They define what should happen, not how to implement it.

### Key Characteristics

**Declarative:**
- You specify the desired outcome
- Tool handles execution details
- Focus on "what" not "how"

**Composable:**
- Steps are independent units
- Steps can be reused across recipes
- Recipes can invoke other recipes as sub-steps

**Resumable:**
- Automatic checkpointing after each step
- Resume from last successful step on failure
- No lost work from transient errors

**Observable:**
- Complete event logging
- Track execution in real-time
- Debug with session replay

### Anatomy of a Recipe

```yaml
name: "example-recipe"           # What it's called
description: "What it does"      # Why it exists
version: "1.0.0"                # How it evolves

context:                        # Initial variables
  input_file: "README.md"

steps:                          # The workflow
  - id: "analyze"               # Step 1: Analyze
    agent: "analyzer"
    prompt: "Analyze {{input_file}}"
    output: "analysis"

  - id: "improve"               # Step 2: Improve
    agent: "improver"
    prompt: "Improve based on: {{analysis}}"
    output: "improvements"
```

**What happens:**
1. Tool reads recipe YAML
2. Validates structure and dependencies
3. Creates session with persistence
4. Executes steps sequentially
5. Each step spawns sub-agent with context
6. Results accumulate in context
7. Session checkpointed after each step
8. Final results returned

---

## When to Use Recipes

### ✅ Good Use Cases

**Repeatable multi-step workflows:**
- Code review → analysis → suggestions → validation
- Dependency upgrade → audit → plan → test → apply
- Documentation → analyze → simulate learner → improve

**Complex orchestration:**
- Multiple agents with different specializations
- Context accumulation across steps
- Error handling and retry logic

**Team collaboration:**
- Shared workflows across team
- Consistent process enforcement
- Audit trail of executions

**Long-running processes:**
- Steps may take minutes/hours
- Need resumability on interruption
- Progress tracking important

### ❌ Not Ideal For

**Simple single-agent tasks:**
- One-off questions
- Quick analysis without follow-up
- Tasks that don't need orchestration

**Highly dynamic workflows:**
- Logic depends on real-time user input at every step
- Unpredictable branching
- Better suited for interactive session

**Exploratory work:**
- Unknown structure upfront
- Learning as you go
- Recipe implies known process

### Decision Framework

Ask yourself:
1. **Do I repeat this workflow?** → Recipe makes sense
2. **Are there multiple distinct steps?** → Recipe provides structure
3. **Do later steps depend on earlier results?** → Recipe manages context
4. **Might execution be interrupted?** → Recipe enables resumption
5. **Do others need to run this?** → Recipe enables sharing

If 3+ answers are "yes", use a recipe.

---

## Core Concepts

### Steps

**A step is one agent invocation:**

```yaml
- id: "analyze"              # Unique identifier
  agent: "zen-architect"     # Which agent to spawn
  mode: "ANALYZE"            # Agent mode (if supported)
  prompt: "Analyze {{file}}" # What to ask the agent
  output: "analysis"         # Where to store result
```

**Key properties:**
- **Independence**: Each step is self-contained
- **Ordering**: Steps execute in YAML order (currently sequential)
- **Context**: Steps can access all previous outputs
- **Isolation**: Each step gets fresh sub-agent instance

### Context Variables

**Context is the shared state across steps:**

**Sources:**
1. **Recipe `context` dict** - Initial values
2. **Step outputs** - Results from `output` field
3. **Recipe metadata** - `recipe.*` variables
4. **Session metadata** - `session.*` variables

**Example:**

```yaml
context:
  file_path: "src/auth.py"  # Initial value
  severity: "high"

steps:
  - id: "scan"
    prompt: "Scan {{file_path}} for {{severity}} issues"
    output: "findings"       # Adds {{findings}} to context

  - id: "report"
    prompt: "Report on {{findings}} from {{file_path}}"
    # Has access to: file_path, severity, findings
```

**Scoping:**
- Variables defined in `context` available to all steps
- Variables from `output` available to subsequent steps
- Variables shadowing: step outputs override context values

### Agent Delegation

**Each step spawns a sub-agent:**

**What gets inherited:**
- Orchestrator (execution loop)
- Context manager (memory strategy)
- Hooks (logging, security)
- Baseline providers and tools

**What can be overridden:**
- Providers (different model per step)
- Tools (subset or addition)
- Configuration (temperature, system prompt)

**Example:**

```yaml
- id: "creative-step"
  agent: "zen-architect"
  agent_config:
    providers:
      - module: "provider-anthropic"
        config:
          temperature: 0.8   # Override for creativity
          model: "claude-opus-4"
  prompt: "Brainstorm alternatives"
```

### Session Persistence

**Sessions persist to disk:**

```
~/.amplifier/projects/<project-slug>/recipe-sessions/
  recipe_20251118_143022_a3f2/
    state.json        # Current state, step outputs
    recipe.yaml       # The recipe being executed
    events.jsonl      # Execution event log
```

**State includes:**
- Current step index
- All context variables
- Step outputs
- Timestamps and metadata

**Resumption:**
```bash
# Recipe interrupted? Resume:
amplifier run "resume recipe session recipe_20251118_143022_a3f2"
```

**Auto-cleanup:**
- Sessions older than 7 days auto-deleted (configurable)
- Prevent accumulation of stale sessions
- Configure via tool config: `auto_cleanup_days`

---

## Design Patterns

### Pattern 1: Sequential Analysis Pipeline

**Use case:** Each step builds on previous analysis.

```yaml
name: "sequential-analysis"
steps:
  - id: "extract"
    agent: "analyzer"
    prompt: "Extract key concepts from {{document}}"
    output: "concepts"

  - id: "categorize"
    agent: "analyzer"
    prompt: "Categorize these concepts: {{concepts}}"
    output: "categories"

  - id: "synthesize"
    agent: "synthesizer"
    prompt: "Synthesize: {{concepts}} into {{categories}}"
    output: "synthesis"
```

**When to use:**
- Linear dependency chain
- Each step refines previous results
- Clear progression from raw to refined

### Pattern 2: Multi-Perspective Analysis

**Use case:** Analyze from different viewpoints, then converge.

```yaml
name: "multi-perspective-review"
steps:
  - id: "security-review"
    agent: "security-guardian"
    prompt: "Security audit: {{code}}"
    output: "security_findings"

  - id: "performance-review"
    agent: "performance-optimizer"
    prompt: "Performance audit: {{code}}"
    output: "performance_findings"

  - id: "maintainability-review"
    agent: "zen-architect"
    prompt: "Maintainability audit: {{code}}"
    output: "maintainability_findings"

  - id: "synthesize-findings"
    agent: "zen-architect"
    prompt: |
      Synthesize findings:
      Security: {{security_findings}}
      Performance: {{performance_findings}}
      Maintainability: {{maintainability_findings}}
    output: "final_report"
```

**When to use:**
- Multiple independent analyses
- Different specialized agents
- Converge at end for holistic view

**Tip:** For same-agent multi-perspective analysis, consider using foreach with `parallel: true` (see Pattern 3).

### Pattern 3: Bulk Processing with foreach

**Use case:** Process multiple items with the same analysis pattern.

```yaml
name: "multi-file-analysis"
context:
  # Files provided as list - override at invocation time
  files:
    - "src/auth.py"
    - "src/models.py"
    - "src/utils.py"
  focus: "code quality"

steps:
  - id: "analyze-each"
    foreach: "{{files}}"
    as: "current_file"
    agent: "zen-architect"
    prompt: "Analyze {{current_file}} for {{focus}} issues"
    collect: "file_analyses"

  - id: "synthesize"
    agent: "zen-architect"
    prompt: |
      Create summary report from analyses:
      {{file_analyses}}
    output: "final_report"
```

**Usage:**
```bash
# Use defaults
amplifier run "execute multi-file-analysis.yaml"

# Override files at runtime
amplifier run "execute multi-file-analysis.yaml with files=['api.py','db.py']"
```

**When to use:**
- Processing multiple items with the same pattern
- Collecting results for later synthesis
- Batch operations where item list is known

**Behavior:**
- `foreach` specifies the list variable to iterate over
- `as` sets the loop variable name (default: "item")
- `collect` aggregates all iteration results into a list
- `parallel: true` runs all iterations concurrently (faster for independent analyses)
- Empty list skips the step (no error)
- Any iteration failure stops the recipe (fail-fast)

**See also:** [Looping and Iteration](RECIPE_SCHEMA.md#looping-and-iteration) for complete syntax reference.
**Working example:** [multi-file-analysis.yaml](../examples/multi-file-analysis.yaml)

### Pattern 4: Conditional Processing

**Use case:** Different paths based on step results.

```yaml
name: "conditional-processing"
version: "1.0.0"
description: "Route processing based on classification"

steps:
  - id: "classify"
    agent: "classifier"
    prompt: "Classify {{input}} as: simple, medium, complex"
    output: "classification"

  - id: "simple-process"
    condition: "{{classification}} == 'simple'"
    agent: "simple-processor"
    prompt: "Process simple case: {{input}}"
    output: "result"

  - id: "medium-process"
    condition: "{{classification}} == 'medium'"
    agent: "medium-processor"
    prompt: "Process medium complexity case: {{input}}"
    output: "result"

  - id: "complex-process"
    condition: "{{classification}} == 'complex'"
    agent: "complex-processor"
    prompt: "Process complex case: {{input}}"
    output: "result"
```

**When to use:**
- Routing based on prior analysis
- Severity-based processing
- Optional steps that depend on prior results

**Behavior:**
- Condition is `true` → Step executes
- Condition is `false` → Step skips, continues to next
- Undefined variable → Recipe fails with clear error

**See also:** [Condition Expressions](RECIPE_SCHEMA.md#condition-expressions) for complete syntax reference.

### Pattern 5: Error-Tolerant Pipeline

**Use case:** Continue processing even if some steps fail.

```yaml
name: "error-tolerant"
steps:
  - id: "critical-analysis"
    agent: "analyzer"
    prompt: "Core analysis"
    output: "analysis"
    # Default: on_error="fail"

  - id: "optional-enhancement"
    agent: "enhancer"
    prompt: "Enhance: {{analysis}}"
    output: "enhanced"
    on_error: "continue"  # Don't fail recipe if this fails

  - id: "final-report"
    agent: "reporter"
    prompt: |
      Report:
      Analysis: {{analysis}}
      Enhanced: {{enhanced}}  # May be empty if enhancement failed
```

**When to use:**
- Some steps are optional/nice-to-have
- Partial results acceptable
- Graceful degradation preferred

---

## Creating Your First Recipe

### Step-by-Step Guide

#### 1. Define the Workflow

**Ask:**
- What's the goal?
- What are the distinct steps?
- What information flows between steps?
- Which agents handle which steps?

**Example:** Code review workflow
- Goal: Get comprehensive code review
- Steps: Security scan → Performance analysis → Maintainability review → Synthesis
- Flow: Each scan produces findings → Synthesis combines them
- Agents: security-guardian, performance-optimizer, zen-architect

#### 2. Choose a Template

Start with a template from `templates/`:

```bash
cp templates/multi-step-recipe.yaml my-review-recipe.yaml
```

Or use recipe-author agent:

```bash
amplifier run "create a code review recipe"
```

#### 3. Customize Steps

**For each step, define:**
- `id`: Descriptive identifier
- `agent`: Which specialized agent
- `prompt`: Clear instructions with context variables
- `output`: Name for storing results (if needed by later steps)

**Example:**

```yaml
- id: "security-scan"
  agent: "security-guardian"
  prompt: "Scan {{file_path}} for security vulnerabilities"
  output: "security_findings"
```

#### 4. Define Context Variables

**Add to `context` dict:**
- Required inputs (will be provided at runtime)
- Default values (can be overridden)
- Shared configuration

**Example:**

```yaml
context:
  file_path: ""              # Required: must provide at runtime
  severity_threshold: "high" # Default: can override
  auto_fix: false            # Shared config
```

#### 5. Test Execution

**Run with test inputs:**

```bash
amplifier run "execute my-review-recipe.yaml with file_path=src/test.py"
```

**Check:**
- Does each step complete?
- Are outputs correct?
- Does context flow properly?
- Any errors in logs?

#### 6. Iterate

**Based on test results:**
- Adjust prompts for clarity
- Add/remove steps as needed
- Tune agent configurations
- Add error handling (`on_error`, `retry`)

#### 7. Document and Share

**Add to recipe:**
- Clear `description`
- Helpful `tags`
- Usage examples in comments

**Example:**

```yaml
name: "code-security-review"
description: "Comprehensive security audit with vulnerability scanning and fix suggestions"
tags: ["security", "code-review", "python"]

# Usage:
#   amplifier run "execute code-security-review.yaml with file_path=src/auth.py"
#
# Context variables:
#   - file_path (required): Path to file to review
#   - severity_threshold (optional): Minimum severity to report (default: "high")
```

---

## Advanced Techniques

### Custom Agent Configurations

**Override agent behavior per-step:**

```yaml
- id: "creative-brainstorm"
  agent: "zen-architect"
  agent_config:
    providers:
      - module: "provider-anthropic"
        config:
          model: "claude-opus-4"
          temperature: 0.8        # Very creative
          max_tokens: 4000
    tools:
      - module: "tool-web-search"  # Add web search
  prompt: "Research and brainstorm innovative solutions"
```

**Use cases:**
- Temperature tuning per cognitive role
- Different models for different steps
- Add tools for specific steps

### Timeout and Retry Configuration

**Handle long-running or flaky steps:**

```yaml
- id: "external-api-call"
  agent: "data-fetcher"
  prompt: "Fetch data from external API"
  timeout: 300       # 5 minutes max
  retry:
    max_attempts: 5
    backoff: "exponential"
    initial_delay: 10
    max_delay: 300
```

**When to use:**
- Network operations
- External service calls
- Long-running analyses
- Known intermittent failures

### Multi-Line Prompts

**Use YAML literal block syntax for complex prompts:**

```yaml
- id: "detailed-analysis"
  agent: "analyzer"
  prompt: |
    Perform detailed analysis of {{file_path}}:

    1. Code structure and organization
    2. Naming conventions and clarity
    3. Error handling patterns
    4. Performance considerations
    5. Security implications

    Previous findings: {{previous_analysis}}

    Focus particularly on {{focus_area}}.
```

**Benefits:**
- More readable in YAML
- Clear multi-part instructions
- Easy to iterate and refine

### Recipe Metadata Usage

**Access recipe info in prompts:**

```yaml
- id: "generate-report"
  agent: "reporter"
  prompt: |
    Generate review report:

    Recipe: {{recipe.name}} v{{recipe.version}}
    Session: {{session.id}}
    Started: {{session.started}}
    Project: {{session.project}}

    Findings: {{findings}}

    Include this metadata in report header.
```

**Use cases:**
- Audit trails
- Report headers
- Debugging context
- Version tracking

---

## Testing and Validation

### Pre-Execution Validation

**Tool validates before running:**

- ✅ YAML syntax correct
- ✅ Required fields present
- ✅ Step IDs unique
- ✅ Variable references valid
- ✅ Agents available
- ✅ No circular dependencies

**Get validation without execution:**

```bash
amplifier run "validate recipe my-recipe.yaml"
```

### Test Execution

**Start with minimal test:**

```yaml
context:
  test_input: "small test case"

steps:
  - id: "test-step"
    agent: "test-agent"
    prompt: "Process: {{test_input}}"
    output: "result"
```

**Gradually expand:**
1. One step → validates agent delegation
2. Two steps with context flow → validates variable substitution
3. Full workflow → validates complete orchestration

### Debugging

**Check session logs:**

```bash
# Find recent sessions
ls -lt ~/.amplifier/projects/*/recipe-sessions/

# View session state
cat ~/.amplifier/projects/<project>/recipe-sessions/<session-id>/state.json

# View execution log
cat ~/.amplifier/projects/<project>/recipe-sessions/<session-id>/events.jsonl
```

**Common issues:**
- Undefined variable → Check variable sources, dependencies
- Agent not found → Verify agent installed, check spelling
- Step timeout → Increase timeout, simplify prompt
- Unexpected output → Review agent prompt, check agent mode

### Iterative Refinement

**Process:**
1. Run recipe with test input
2. Review outputs at each step
3. Identify issues (wrong output, missing context, unclear prompt)
4. Refine prompts, adjust steps
5. Re-run with same input
6. Compare results
7. Repeat until satisfied

**Use session resumption for faster iteration:**
- Interrupt recipe at problem step
- Fix recipe YAML
- Resume from checkpoint
- Only re-runs modified steps

---

## Next Steps

**Now that you understand recipes:**

1. **Browse examples** - See [Examples Catalog](EXAMPLES_CATALOG.md)
2. **Study best practices** - Read [Best Practices](BEST_PRACTICES.md)
3. **Create your first recipe** - Use recipe-author agent or copy template
4. **Join discussions** - Share recipes, get feedback, learn from others

**Resources:**
- [Recipe Schema Reference](RECIPE_SCHEMA.md) - Complete YAML spec
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Examples](../examples/) - Working recipe files
- [Templates](../templates/) - Starter recipes

---

**Questions? Issues? Ideas?**

- GitHub Issues: [amplifier-collection-recipes/issues](https://github.com/microsoft/amplifier-collection-recipes/issues)
- GitHub Discussions: [amplifier-collection-recipes/discussions](https://github.com/microsoft/amplifier-collection-recipes/discussions)
