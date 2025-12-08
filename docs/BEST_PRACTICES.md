# Recipe Best Practices

**Strategic guidance for effective recipe design**

This document provides best practices for creating, maintaining, and using Amplifier recipes effectively.

## Table of Contents

- [Design Principles](#design-principles)
- [Recipe Structure](#recipe-structure)
- [Step Design](#step-design)
- [Context Management](#context-management)
- [Error Handling](#error-handling)
- [Performance](#performance)
- [Testing](#testing)
- [Maintenance](#maintenance)
- [Common Pitfalls](#common-pitfalls)

---

## Design Principles

### 1. Single Responsibility

**Each recipe should have one clear purpose.**

✅ **Good:**
```yaml
name: "security-audit"
description: "Comprehensive security analysis with vulnerability scanning"
```

❌ **Bad:**
```yaml
name: "code-analysis-and-refactoring-and-testing"
description: "Does everything related to code quality"
```

**Why:** Single-purpose recipes are easier to understand, test, and reuse. Complex workflows can compose multiple recipes.

### 2. Composability Over Complexity

**Prefer multiple simple recipes over one complex recipe.**

✅ **Good:**
- `security-audit.yaml` - Security scanning only
- `performance-audit.yaml` - Performance analysis only
- `full-audit.yaml` - Runs security-audit + performance-audit via recipe composition

❌ **Bad:**
- `mega-audit.yaml` - 20 steps covering everything

**Why:** Smaller recipes are easier to maintain, test, and reuse in different contexts.

### 3. Explicit Over Implicit

**Make dependencies and requirements clear.**

✅ **Good:**
```yaml
context:
  file_path: ""         # Required: path to file to analyze
  severity: "high"      # Optional: minimum severity (default: high)
  auto_fix: false       # Optional: apply fixes automatically (default: false)

# Usage example:
#   amplifier run "execute recipe.yaml with file_path=src/auth.py"
```

❌ **Bad:**
```yaml
context: {}  # User has to guess what's needed
```

**Why:** Clear requirements reduce errors and improve user experience.

### 4. Progressive Disclosure

**Start simple, add complexity only when needed.**

**Version 1.0:** Basic workflow
```yaml
steps:
  - id: "analyze"
    agent: "analyzer"
    prompt: "Analyze {{file}}"
```

**Version 1.1:** Add error handling when needed
```yaml
steps:
  - id: "analyze"
    agent: "analyzer"
    prompt: "Analyze {{file}}"
    timeout: 600
    retry:
      max_attempts: 3
```

**Why:** Simple recipes are easier to understand. Add complexity based on real needs, not speculation.

### 5. Fail-Fast Philosophy

**Detect problems early rather than late.**

✅ **Good:**
```yaml
steps:
  - id: "validate-inputs"
    agent: "validator"
    prompt: "Validate that {{file_path}} exists and is readable"
    # Fails fast if inputs invalid

  - id: "expensive-analysis"
    agent: "analyzer"
    prompt: "Deep analysis of {{file_path}}"
    # Only runs if validation passed
```

❌ **Bad:**
```yaml
steps:
  - id: "expensive-analysis"
    # Runs for 10 minutes...
    # THEN discovers file doesn't exist
```

**Why:** Fail fast saves time and provides better user experience.

---

## Recipe Structure

### Naming Conventions

**Recipe names:**
- Lowercase with hyphens
- Descriptive and specific
- Include domain if ambiguous

```yaml
✅ security-audit
✅ python-dependency-upgrade
✅ api-documentation-review

❌ audit
❌ upgrade
❌ review
```

**Step IDs:**
- Verb-noun format
- Descriptive of action
- Keep concise

```yaml
✅ analyze-security
✅ generate-report
✅ validate-results

❌ step1
❌ do-stuff
❌ analyze_security_vulnerabilities_and_generate_comprehensive_report
```

**Context variables:**
- Snake_case
- Descriptive
- Avoid abbreviations

```yaml
✅ file_path
✅ severity_threshold
✅ max_iterations

❌ fp
❌ sev_thresh
❌ maxIter
```

### Versioning

**Follow semantic versioning:**

- **MAJOR (1.x.x → 2.x.x):** Breaking changes
  - Different required inputs
  - Different output format
  - Incompatible behavior

- **MINOR (x.1.x → x.2.x):** Backward-compatible additions
  - New optional steps
  - New optional context variables
  - Enhanced functionality

- **PATCH (x.x.1 → x.x.2):** Bug fixes
  - Prompt improvements
  - Error handling fixes
  - Documentation updates

**Example:**
```yaml
# v1.0.0: Initial release
name: "code-review"
version: "1.0.0"

# v1.1.0: Added optional validation step (backward-compatible)
version: "1.1.0"

# v2.0.0: Changed required inputs (breaking change)
version: "2.0.0"
```

### Documentation

**Include helpful comments:**

```yaml
name: "security-audit"
description: "Comprehensive security analysis with vulnerability scanning"
version: "1.0.0"

# This recipe performs multi-stage security analysis:
# 1. Static analysis for common vulnerabilities
# 2. Dependency audit for known CVEs
# 3. Configuration review for security misconfigurations
#
# Typical runtime: 5-10 minutes
# Requires: security-guardian agent installed
#
# Usage:
#   amplifier run "execute security-audit.yaml with file_path=src/auth.py"
#
# Context variables:
#   - file_path (required): Path to Python file to audit
#   - severity_threshold (optional): Minimum severity to report (default: "high")

context:
  file_path: ""
  severity_threshold: "high"
```

**Why:** Good documentation helps users and future maintainers (including yourself).

---

## Step Design

### Prompt Design

**Be specific and directive:**

✅ **Good:**
```yaml
prompt: |
  Analyze {{file_path}} for SQL injection vulnerabilities.

  Check for:
  1. Unsanitized user input in SQL queries
  2. Dynamic query construction
  3. Missing parameterization

  Output format: List each finding with line number, severity, and explanation.
```

❌ **Bad:**
```yaml
prompt: "Look at {{file_path}}"
```

**Why:** Specific prompts produce better, more consistent results.

### Agent Selection

**Choose agents based on cognitive role:**

```yaml
# Analytical tasks → zen-architect (ANALYZE mode)
- id: "analyze-structure"
  agent: "zen-architect"
  mode: "ANALYZE"

# Design tasks → zen-architect (ARCHITECT mode)
- id: "design-solution"
  agent: "zen-architect"
  mode: "ARCHITECT"

# Debugging → bug-hunter
- id: "investigate-crash"
  agent: "bug-hunter"

# Security → security-guardian
- id: "security-scan"
  agent: "security-guardian"
```

**Why:** Specialized agents produce better results for their domain.

### Step Granularity

**One clear action per step:**

✅ **Good:**
```yaml
- id: "extract-functions"
  prompt: "Extract all function definitions from {{code}}"
  output: "functions"

- id: "analyze-complexity"
  prompt: "Analyze complexity of these functions: {{functions}}"
  output: "complexity_analysis"
```

❌ **Bad:**
```yaml
- id: "extract-and-analyze"
  prompt: "Extract functions from {{code}} and analyze their complexity"
  # Two actions in one step - harder to debug, no intermediate result
```

**Why:** Fine-grained steps enable better debugging, resumption, and reuse.

### Output Management

**Store outputs that later steps need:**

```yaml
- id: "analyze"
  prompt: "Analyze {{code}}"
  output: "analysis"      # ✅ Stored for later

- id: "report"
  prompt: "Generate report"
  # ❌ No output - can't reference result later
```

**When to skip output:**
- Final step (no later steps need it)
- Step is purely side-effect (writing file, notification)
- Result not useful in later steps

---

## Context Management

### Initial Context

**Define all required variables upfront:**

```yaml
context:
  # Required variables (empty string = must provide)
  file_path: ""
  project_name: ""

  # Optional variables (defaults provided)
  severity: "high"
  auto_fix: false
  timeout_minutes: 10

  # Computed variables (derived from others)
  log_file: "{{project_name}}_audit.log"
```

### Variable Naming

**Use consistent prefixes for related variables:**

```yaml
context:
  # Input files
  input_file: "src/main.py"
  input_dir: "src/"

  # Configuration
  config_severity: "high"
  config_timeout: 600
  config_retry_attempts: 3

  # Output locations
  output_report: "report.md"
  output_artifacts: "artifacts/"
```

### Variable Scope

**Understand variable lifecycles:**

```yaml
# Recipe-level: Available to all steps
context:
  global_setting: "value"

steps:
  # Step-level: Only available to subsequent steps
  - id: "step1"
    output: "step1_result"

  - id: "step2"
    # Has access to: global_setting, step1_result
    output: "step2_result"

  - id: "step3"
    # Has access to: global_setting, step1_result, step2_result
```

**Why:** Explicit scoping prevents confusion and errors.

---

## Error Handling

### Error Strategy by Step Criticality

**Critical steps (fail recipe on error):**
```yaml
- id: "validate-inputs"
  agent: "validator"
  # Default: on_error="fail"
  # Recipe stops if validation fails
```

**Optional steps (continue on error):**
```yaml
- id: "optional-enhancement"
  agent: "enhancer"
  on_error: "continue"
  # Recipe continues even if this fails
```

**Guard steps (skip remaining on error):**
```yaml
- id: "check-eligibility"
  agent: "checker"
  on_error: "skip_remaining"
  # If not eligible, skip remaining steps but don't fail recipe
```

### Retry Configuration

**Network operations:**
```yaml
- id: "fetch-external-data"
  agent: "fetcher"
  retry:
    max_attempts: 5
    backoff: "exponential"
    initial_delay: 10
    max_delay: 300
```

**LLM operations (already retried by provider):**
```yaml
- id: "analyze"
  agent: "analyzer"
  # No retry needed - provider handles it
```

**File operations (cloud sync issues):**
```yaml
- id: "read-file"
  agent: "reader"
  retry:
    max_attempts: 3
    backoff: "exponential"
    initial_delay: 5
```

### Timeout Guidelines

**By operation type:**

```yaml
# Quick analysis (< 1 minute)
- timeout: 60

# Standard analysis (1-5 minutes)
- timeout: 300

# Deep analysis (5-10 minutes)
- timeout: 600

# Very long operations (10-30 minutes)
- timeout: 1800
```

**Consider:**
- File size
- Analysis depth
- Agent complexity
- Network latency

---

## Performance

### Minimize Unnecessary Steps

❌ **Wasteful:**
```yaml
- id: "read-file"
  prompt: "Read {{file_path}}"
  output: "file_content"

- id: "analyze"
  prompt: "Analyze: {{file_content}}"
```

✅ **Efficient:**
```yaml
- id: "analyze"
  prompt: "Analyze {{file_path}}"
  # Agent can read file directly
```

### Optimize Context Size

**Keep context lean:**

```yaml
- id: "extract-summary"
  prompt: "Extract 3-sentence summary from {{document}}"
  output: "summary"  # ✅ Store summary, not entire document

- id: "use-summary"
  prompt: "Based on this summary: {{summary}}"
  # Uses small summary instead of large document
```

---

## Testing

### Test Strategy

**1. Unit testing (individual steps):**

```yaml
# Test single step in isolation
name: "test-analyze-step"
steps:
  - id: "analyze"
    agent: "analyzer"
    prompt: "Analyze {{test_file}}"

context:
  test_file: "tests/fixtures/simple.py"
```

**2. Integration testing (full recipe):**

```bash
# Run full recipe with test data
amplifier run "execute my-recipe.yaml with file_path=tests/fixtures/test.py"
```

**3. Validation testing:**

```bash
# Validate without execution
amplifier run "validate recipe my-recipe.yaml"
```

### Test Data

**Create realistic test fixtures:**

```
tests/
  fixtures/
    simple.py      # Minimal test case
    complex.py     # Comprehensive test case
    edge_case.py   # Known edge case
    invalid.py     # Should fail gracefully
```

### Regression Testing

**Document expected behavior:**

```yaml
# my-recipe.yaml

# Expected behavior (for regression testing):
#
# Input: Simple Python file (10 lines)
# Expected steps: 4 steps complete successfully
# Expected duration: ~2 minutes
# Expected outputs: analysis, suggestions, validation, report
#
# Input: Complex Python file (500 lines)
# Expected steps: 4 steps complete successfully
# Expected duration: ~10 minutes
# Expected outputs: analysis, suggestions, validation, report
```

---

## Maintenance

### Versioning Strategy

**When to bump version:**

**Patch (x.x.X):**
- Typo fixes in prompts
- Documentation updates
- Performance improvements (no behavior change)

**Minor (x.X.x):**
- New optional steps
- New optional context variables
- Enhanced error handling

**Major (X.x.x):**
- Changed required context variables
- Removed steps
- Changed output format
- Breaking behavior changes

### Deprecation Process

**1. Announce in comments:**
```yaml
# DEPRECATED: Use security-audit-v2.yaml instead
# This recipe will be removed in v3.0.0
```

**2. Update description:**
```yaml
description: "[DEPRECATED] Use security-audit-v2 instead"
```

**3. Provide migration guide:**
```yaml
# Migration from v1 to v2:
#
# Changed:
#   - Context variable "file" renamed to "file_path"
#   - Added required "project_name" variable
#   - Removed "quick_mode" option
#
# Example v1:
#   amplifier run "execute recipe-v1.yaml with file=auth.py"
#
# Example v2:
#   amplifier run "execute recipe-v2.yaml with file_path=auth.py project_name=myapp"
```

### Documentation Maintenance

**Keep in sync:**
- Recipe YAML
- Usage examples
- Expected behavior
- Dependencies (agent versions)

**Update on changes:**
- Prompt improvements
- New steps added
- Error handling changes
- Performance characteristics

---

## Common Pitfalls

### 1. Overly Generic Prompts

❌ **Problem:**
```yaml
prompt: "Analyze the code"
```

✅ **Solution:**
```yaml
prompt: |
  Analyze {{file_path}} for:
  1. Security vulnerabilities
  2. Performance bottlenecks
  3. Code complexity issues

  For each finding, provide:
  - Line number
  - Severity (critical/high/medium/low)
  - Explanation
  - Suggested fix
```

### 2. Missing Context Variables

❌ **Problem:**
```yaml
steps:
  - prompt: "Analyze {{file_path}}"
    # file_path never defined!
```

✅ **Solution:**
```yaml
context:
  file_path: ""  # Define upfront

steps:
  - prompt: "Analyze {{file_path}}"
```

### 3. Monolithic Steps

❌ **Problem:**
```yaml
- id: "do-everything"
  prompt: "Analyze code, find issues, suggest fixes, generate tests, write documentation"
```

✅ **Solution:**
```yaml
- id: "analyze"
  prompt: "Analyze code"
  output: "analysis"

- id: "suggest-fixes"
  prompt: "Based on {{analysis}}, suggest fixes"
  output: "fixes"

- id: "generate-tests"
  prompt: "Generate tests for {{fixes}}"
```

### 4. Tight Coupling

❌ **Problem:**
```yaml
- id: "step1"
  prompt: "Analyze {{file}} and store in {{step2_input_format}}"
  # Knows too much about step2's requirements
```

✅ **Solution:**
```yaml
- id: "step1"
  prompt: "Analyze {{file}}"
  output: "analysis"
  # Step2 adapts to step1's output format
```

### 5. No Error Handling

❌ **Problem:**
```yaml
- id: "external-api"
  agent: "fetcher"
  # No timeout, no retry, no error handling
```

✅ **Solution:**
```yaml
- id: "external-api"
  agent: "fetcher"
  timeout: 300
  retry:
    max_attempts: 3
    backoff: "exponential"
  on_error: "continue"  # Or "fail" if critical
```

### 6. Hidden Requirements

❌ **Problem:**
```yaml
# Recipe works only if security-guardian is configured with API key
# But this isn't documented anywhere
```

✅ **Solution:**
```yaml
# Requirements:
#   - security-guardian agent installed
#   - Security Guardian API key configured in profile
#   - Internet connection for vulnerability database updates
#
# Setup:
#   1. Install: amplifier collection add amplifier-collection-security
#   2. Configure: Add API key to profile
#   3. Verify: amplifier agents list | grep security-guardian
```

---

## Summary: The Recipe Quality Checklist

Before sharing or using a recipe in production, verify:

### Design
- [ ] Single, clear purpose
- [ ] Appropriate granularity (not too complex, not too simple)
- [ ] Follows semantic versioning
- [ ] Well-documented with usage examples

### Structure
- [ ] All required fields present and valid
- [ ] Descriptive names (recipe, steps, variables)
- [ ] Clear, specific prompts
- [ ] Appropriate agent selection

### Context
- [ ] All required variables defined
- [ ] Defaults provided for optional variables
- [ ] No undefined variable references
- [ ] Variable naming consistent

### Error Handling
- [ ] Timeouts appropriate for operation
- [ ] Retry logic for transient failures
- [ ] Error strategy matches step criticality
- [ ] Graceful degradation where appropriate

### Testing
- [ ] Validated with test data
- [ ] Expected behavior documented
- [ ] Edge cases considered
- [ ] Regression tests possible

### Documentation
- [ ] Purpose clearly stated
- [ ] Usage examples provided
- [ ] Requirements listed
- [ ] Expected runtime documented

---

**See Also:**
- [Recipe Schema Reference](RECIPE_SCHEMA.md) - Technical specification
- [Recipes Guide](RECIPES_GUIDE.md) - Conceptual overview
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Examples Catalog](EXAMPLES_CATALOG.md) - Working examples
