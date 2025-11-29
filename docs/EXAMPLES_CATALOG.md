# Examples Catalog

**Browse working recipe examples**

This catalog describes all example recipes included in the collection. Each example demonstrates different patterns and use cases.

## Quick Reference

| Recipe | Domain | Steps | Duration | Agents Used |
|--------|--------|-------|----------|-------------|
| [code-review](#code-review) | Code Quality | 4 | ~5-10 min | zen-architect (3 modes) |
| [dependency-upgrade](#dependency-upgrade) | DevOps | 4 | ~10-15 min | zen-architect, integration-specialist |
| [test-generation](#test-generation) | Testing | 3 | ~5-10 min | zen-architect, test-coverage |
| [documentation-evolution](#documentation-evolution) | Documentation | 4 | ~10-20 min | zen-architect (multiple modes) |
| [security-audit](#security-audit) | Security | 4 | ~10-15 min | security-guardian, zen-architect |
| [bug-investigation](#bug-investigation) | Debugging | 3 | ~5-10 min | bug-hunter, zen-architect |
| [refactoring-planning](#refactoring-planning) | Architecture | 4 | ~10-15 min | zen-architect (multiple modes) |
| [research-synthesis](#research-synthesis) | Research | 4 | ~15-25 min | zen-architect (multiple modes) |
| [comprehensive-review](#comprehensive-review) | Code Quality | 3 | ~20-30 min | zen-architect, security-guardian |

---

## Comprehensive Review

**File:** `examples/comprehensive-review.yaml`

### Description

Demonstrates recipe composition - combining code review and security audit by invoking them as sub-recipes with isolated context and recursion protection.

### Use Cases

- Combined code quality and security analysis
- Modular workflow design using existing recipes
- Unified reports from multiple analysis types
- DRY principle (reuse existing recipes instead of duplicating steps)

### Workflow

```
1. Code Review (sub-recipe)
   → Runs code-review-recipe.yaml with file_path
   → Returns full code review results

2. Security Audit (sub-recipe)
   → Runs security-audit-recipe.yaml with file_path and severity
   → Returns security findings

3. Synthesize Comprehensive Report
   → Combines results from both sub-recipes
   → Creates prioritized action plan
```

### Key Recipe Structure

```yaml
name: "comprehensive-review"
description: "Combined code quality and security analysis using recipe composition"
version: "1.0.0"

context:
  file_path: ""
  security_severity: "medium"

recursion:
  max_depth: 3
  max_total_steps: 50

steps:
  - id: "code-review"
    type: "recipe"
    recipe: "code-review-recipe.yaml"
    context:
      file_path: "{{file_path}}"
    output: "code_review_results"

  - id: "security-audit"
    type: "recipe"
    recipe: "security-audit-recipe.yaml"
    context:
      file_path: "{{file_path}}"
      severity_threshold: "{{security_severity}}"
    output: "security_results"

  - id: "synthesize-comprehensive"
    agent: "developer-expertise:zen-architect"
    mode: "ARCHITECT"
    prompt: |
      Create comprehensive review combining:
      Code Review: {{code_review_results}}
      Security: {{security_results}}
    output: "comprehensive_report"
```

### Required Context

```yaml
file_path: "path/to/code.py"  # Required
security_severity: "medium"   # Optional, defaults to "medium"
```

### Example Usage

```bash
amplifier run "execute comprehensive-review.yaml with file_path=src/auth.py"
```

### What You'll Get

- Complete code review (structure, issues, improvements)
- Security audit results (vulnerabilities, configuration, dependencies)
- Unified prioritized action plan (critical → low priority)
- Conflict resolution between quality and security recommendations

### Key Learnings

- **Recipe composition**: Reuse existing recipes as workflow components
- **Context isolation**: Sub-recipes receive ONLY explicitly passed context
- **Recursion protection**: Built-in limits prevent runaway nesting
- **Output chaining**: Sub-recipe results available to subsequent steps
- **DRY principle**: No duplication of steps from other recipes

---

## Code Review

**File:** `examples/code-review-recipe.yaml`

### Description

Multi-stage code review workflow that analyzes code for quality, maintainability, and philosophy alignment, then provides actionable improvement suggestions.

### Use Cases

- Pre-merge code review
- Architecture assessment
- Technical debt identification
- Onboarding code walkthroughs

### Workflow

```
1. Analyze (ANALYZE mode)
   → Extract code structure, patterns, complexity

2. Identify Issues (ANALYZE mode)
   → Find specific problems and anti-patterns

3. Suggest Improvements (ARCHITECT mode)
   → Design concrete solutions

4. Validate Suggestions (REVIEW mode)
   → Assess feasibility and priority
```

### Required Context

```yaml
file_path: "path/to/code.py"  # Required
```

### Example Usage

```bash
amplifier run "execute examples/code-review-recipe.yaml with file_path=src/auth.py"
```

### What You'll Get

- Code structure analysis
- Identified issues with severity ratings
- Concrete improvement suggestions
- Prioritized action items

### Key Learnings

- **Multi-mode agent usage**: Shows zen-architect in ANALYZE, ARCHITECT, REVIEW modes
- **Context accumulation**: Each step builds on previous results
- **Progressive refinement**: Analysis → Issues → Solutions → Validation

---

## Dependency Upgrade

**File:** `examples/dependency-upgrade-recipe.yaml`

### Description

Systematic dependency upgrade workflow with audit, planning, validation, and application phases.

### Use Cases

- Monthly dependency updates
- Security vulnerability remediation
- Major version upgrades
- Dependency conflict resolution

### Workflow

```
1. Audit Current Dependencies
   → List current versions, check for updates

2. Plan Upgrade Strategy
   → Determine upgrade order, identify risks

3. Validate Compatibility
   → Check breaking changes, test compatibility

4. Generate Upgrade Commands
   → Create specific upgrade commands and scripts
```

### Required Context

```yaml
project_path: "path/to/project"  # Required
package_manager: "pip"           # Optional, default: "pip"
```

### Example Usage

```bash
amplifier run "execute examples/dependency-upgrade-recipe.yaml with project_path=. package_manager=pip"
```

### What You'll Get

- Current dependency audit
- Upgrade plan with risk assessment
- Compatibility analysis
- Ready-to-run upgrade commands

### Key Learnings

- **Domain-specific agents**: integration-specialist for dependency work
- **Risk assessment**: Planning step evaluates upgrade risks
- **Actionable output**: Final step produces executable commands

---

## Test Generation

**File:** `examples/test-generation-recipe.yaml`

### Description

Analyze code and generate comprehensive test suite with unit, integration, and edge case tests.

### Use Cases

- Adding tests to legacy code
- Improving test coverage
- TDD verification (generate tests from implementation)
- Test maintenance

### Workflow

```
1. Analyze Code Structure
   → Understand functions, classes, dependencies

2. Design Test Strategy
   → Determine test types, coverage goals

3. Generate Test Code
   → Create actual test implementations
```

### Required Context

```yaml
file_path: "path/to/code.py"    # Required
test_framework: "pytest"        # Optional, default: "pytest"
coverage_target: 80             # Optional, default: 80
```

### Example Usage

```bash
amplifier run "execute examples/test-generation-recipe.yaml with file_path=src/utils.py test_framework=pytest"
```

### What You'll Get

- Code analysis with test opportunities
- Test strategy document
- Complete test file ready to use

### Key Learnings

- **Specialized agents**: test-coverage agent for test design
- **Configurable output**: Framework and coverage target configurable
- **Complete artifacts**: Generates ready-to-use test code

---

## Documentation Evolution

**File:** `examples/documentation-evolution-recipe.yaml`

### Description

Tutorial improvement workflow that simulates learner experience, identifies issues, and generates improvements.

### Use Cases

- Improving tutorials and guides
- Documentation testing
- Learning experience optimization
- Accessibility improvements

### Workflow

```
1. Analyze Content
   → Extract structure, identify teaching approach

2. Simulate Learner
   → Experience content as beginner

3. Diagnose Issues
   → Identify confusion points, gaps

4. Generate Improvements
   → Create enhanced version addressing issues
```

### Required Context

```yaml
document_path: "path/to/tutorial.md"  # Required
target_audience: "beginners"          # Optional, default: "beginners"
```

### Example Usage

```bash
amplifier run "execute examples/documentation-evolution-recipe.yaml with document_path=docs/tutorial.md"
```

### What You'll Get

- Content analysis
- Learner simulation report
- Issue diagnosis with severity
- Improved documentation version

### Key Learnings

- **Perspective shifting**: Agent simulates different viewpoint (learner)
- **Multi-stage refinement**: Analysis → Simulation → Diagnosis → Improvement
- **Empathy-driven**: Focuses on learner experience, not just technical accuracy

---

## Security Audit

**File:** `examples/security-audit-recipe.yaml`

### Description

Comprehensive security analysis covering vulnerabilities, configurations, and best practices.

### Use Cases

- Pre-production security review
- Security compliance checks
- Vulnerability assessment
- Penetration test preparation

### Workflow

```
1. Vulnerability Scan
   → Static analysis for common vulnerabilities

2. Configuration Review
   → Check security configurations and settings

3. Dependency Audit
   → Identify vulnerable dependencies

4. Synthesize Findings
   → Prioritize and create action plan
```

### Required Context

```yaml
file_path: "path/to/code.py"         # Required
severity_threshold: "high"           # Optional, default: "high"
include_dependencies: true           # Optional, default: true
```

### Example Usage

```bash
amplifier run "execute examples/security-audit-recipe.yaml with file_path=src/api.py severity_threshold=medium"
```

### What You'll Get

- Vulnerability scan results
- Configuration issues
- Dependency security report
- Prioritized remediation plan

### Key Learnings

- **Specialized agent**: security-guardian for security analysis
- **Multi-perspective**: Different security aspects in separate steps
- **Actionable output**: Prioritized remediation plan

---

## Bug Investigation

**File:** `examples/bug-investigation-recipe.yaml`

### Description

Systematic bug investigation workflow for root cause analysis and solution design.

### Use Cases

- Production bug triage
- Complex bug debugging
- Root cause analysis
- Fix validation

### Workflow

```
1. Reproduce Bug
   → Understand symptoms, create reproduction steps

2. Investigate Root Cause
   → Analyze code, identify actual cause

3. Design Solution
   → Create fix with minimal impact
```

### Required Context

```yaml
bug_description: "Description of bug"  # Required
file_path: "path/to/buggy/code.py"    # Optional
error_message: "Error text"           # Optional
```

### Example Usage

```bash
amplifier run "execute examples/bug-investigation-recipe.yaml with bug_description='Login fails with NullPointerException' file_path=src/auth.py"
```

### What You'll Get

- Bug reproduction steps
- Root cause analysis
- Solution design with rationale
- Validation strategy

### Key Learnings

- **Specialized agent**: bug-hunter for systematic debugging
- **Evidence-based**: Focuses on reproduction and verification
- **Solution design**: Not just "fix it" but designed solution

---

## Refactoring Planning

**File:** `examples/refactoring-planning-recipe.yaml`

### Description

Architecture assessment and refactoring plan creation for code improvements.

### Use Cases

- Technical debt reduction
- Architecture evolution
- Code modernization
- Performance optimization

### Workflow

```
1. Assess Current Architecture
   → Understand structure, patterns, issues

2. Identify Refactoring Opportunities
   → Find improvement areas

3. Design Refactoring Plan
   → Create step-by-step plan

4. Validate Plan
   → Assess risks and feasibility
```

### Required Context

```yaml
file_path: "path/to/code.py"    # Required
focus_area: "structure"         # Optional: "structure", "performance", "maintainability"
```

### Example Usage

```bash
amplifier run "execute examples/refactoring-planning-recipe.yaml with file_path=src/legacy.py focus_area=structure"
```

### What You'll Get

- Architecture assessment
- Refactoring opportunities
- Detailed refactoring plan
- Risk assessment

### Key Learnings

- **Multi-mode usage**: zen-architect in different modes for different phases
- **Strategic planning**: Focus on plan, not immediate execution
- **Risk awareness**: Validates plan for feasibility

---

## Research Synthesis

**File:** `examples/research-synthesis-recipe.yaml`

### Description

Multi-document analysis and synthesis workflow for research and knowledge extraction.

### Use Cases

- Literature review
- Competitive analysis
- Knowledge base creation
- Research paper writing

### Workflow

```
1. Extract Key Concepts
   → Identify main ideas from each document

2. Compare Perspectives
   → Find agreements, contradictions, gaps

3. Synthesize Findings
   → Create coherent narrative

4. Generate Summary
   → Executive summary with citations
```

### Required Context

```yaml
document_paths: ["doc1.md", "doc2.md", ...]  # Required: list of documents
research_question: "What to investigate?"     # Optional
```

### Example Usage

```bash
amplifier run "execute examples/research-synthesis-recipe.yaml with document_paths=['paper1.pdf','paper2.pdf','paper3.pdf'] research_question='What are best practices for API design?'"
```

### What You'll Get

- Concept extraction from each document
- Comparative analysis
- Synthesized findings
- Executive summary with citations

### Key Learnings

- **Multi-document processing**: Handles multiple inputs
- **Comparative analysis**: Identifies patterns across sources
- **Knowledge synthesis**: Creates new understanding from sources

---

## Using Examples

### Copy and Customize

```bash
# Copy example to your recipes directory
cp examples/code-review-recipe.yaml my-recipes/custom-review.yaml

# Edit as needed
# Run your custom version
amplifier run "execute my-recipes/custom-review.yaml with file_path=src/mycode.py"
```

### Study Pattern

Each example demonstrates specific patterns:

- **code-review**: Multi-mode agent usage
- **dependency-upgrade**: Domain-specific agents
- **test-generation**: Artifact generation
- **documentation-evolution**: Perspective shifting
- **security-audit**: Multi-perspective analysis
- **bug-investigation**: Systematic debugging
- **refactoring-planning**: Strategic planning
- **research-synthesis**: Multi-document processing

### Mix and Match

Combine steps from different examples:

```yaml
name: "custom-workflow"
steps:
  # From code-review: analysis
  - id: "analyze"
    agent: "zen-architect"
    mode: "ANALYZE"
    prompt: "Analyze {{file_path}}"
    output: "analysis"

  # From security-audit: security check
  - id: "security-check"
    agent: "security-guardian"
    prompt: "Security audit: {{file_path}}"
    output: "security_findings"

  # From code-review: synthesize
  - id: "synthesize"
    agent: "zen-architect"
    mode: "ARCHITECT"
    prompt: "Synthesize: {{analysis}} and {{security_findings}}"
```

---

## Contributing Examples

Have a useful recipe? Share it!

1. **Test thoroughly** with multiple inputs
2. **Document well** (context vars, usage, expected output)
3. **Follow best practices** (see [Best Practices](BEST_PRACTICES.md))
4. **Submit PR** with:
   - Recipe YAML file
   - Description for this catalog
   - Example usage

See [Contributing Guidelines](../CONTRIBUTING.md) for details.

---

## Example Categories

### By Domain

**Code Quality:**
- code-review
- refactoring-planning

**Security:**
- security-audit

**Testing:**
- test-generation

**DevOps:**
- dependency-upgrade

**Documentation:**
- documentation-evolution

**Debugging:**
- bug-investigation

**Research:**
- research-synthesis

### By Pattern

**Sequential Analysis:**
- code-review
- security-audit
- research-synthesis

**Multi-Perspective:**
- security-audit (vulnerability, config, dependencies)
- research-synthesis (multiple documents)

**Planning/Execution:**
- dependency-upgrade (plan → execute)
- refactoring-planning (assess → plan → validate)

**Artifact Generation:**
- test-generation (generates test code)
- documentation-evolution (generates improved docs)

**Recipe Composition:**
- comprehensive-review (combines code review + security audit via sub-recipes)

---

## Next Steps

1. **Browse examples** in `examples/` directory
2. **Try an example** with your data
3. **Customize** for your needs
4. **Create your own** using patterns learned
5. **Share** useful recipes with community

---

**Questions about examples?** Ask in [GitHub Discussions](https://github.com/microsoft/amplifier-collection-recipes/discussions)!
