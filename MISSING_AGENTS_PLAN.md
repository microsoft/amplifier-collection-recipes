# Missing Agents Implementation Plan

**Date:** 2025-11-18
**Status:** Planning

---

## Executive Summary

4 agents referenced in example recipes don't exist yet. This document analyzes each agent, determines where it should live, and provides implementation specs.

**Key Decision:** Collection vs Standalone placement based on agent purpose and reusability.

---

## Missing Agents Analysis

### 1. test-analyzer

**Referenced in:** `minimal-test-recipe.yaml`

**Purpose:** Unclear - appears to be a testing artifact from development

**Analysis:**
- Only used in minimal-test-recipe.yaml (created during testing)
- No clear use case beyond testing
- May not be needed at all

**Recommendation:** ❌ **DELETE minimal-test-recipe.yaml**
- It's a testing artifact, not a real example
- Uses non-existent agent with unclear purpose
- Doesn't demonstrate any valuable pattern
- Already have ultra-minimal-test.yaml as minimal example

**Action:** Remove `examples/minimal-test-recipe.yaml` from collection

---

### 2. integration-specialist

**Referenced in:** `dependency-upgrade-recipe.yaml` (steps 1, 3, 4)

**Purpose:** Integration tasks - dependencies, APIs, external systems

**Use Cases:**
- Dependency auditing and upgrading
- API integration planning
- External system compatibility checking
- Integration testing strategies

**Tools Needed:**
- `tool-filesystem` - Read package files (package.json, pyproject.toml, etc.)
- `tool-bash` - Run dependency commands (pip list, npm outdated, etc.)
- `tool-web` - Check package registries, security advisories

**Where:** 🎯 **developer-expertise collection**
- General-purpose development agent
- Useful across many projects and workflows
- Not specific to recipes
- Complements existing developer-expertise agents (zen-architect, bug-hunter, etc.)

**Agent Spec:**
```yaml
---
meta:
  name: integration-specialist
  description: "Integration expert for dependencies, APIs, and external systems"

tools:
  - module: tool-filesystem
  - module: tool-bash
  - module: tool-web

providers:
  - module: provider-anthropic
    config:
      model: claude-sonnet-4-5
      temperature: 0.3  # Precise for dependency analysis
---

You are an integration specialist focused on system boundaries and external dependencies.

Your expertise:
- **Dependency Management**: Auditing, upgrading, conflict resolution
- **API Integration**: Design, compatibility, error handling
- **External Systems**: Service integration, data exchange, protocols
- **Compatibility Analysis**: Version constraints, breaking changes

When analyzing dependencies:
1. Check current versions and available updates
2. Identify security vulnerabilities
3. Assess breaking changes and migration effort
4. Recommend upgrade strategy with risk levels
5. Provide specific commands to execute

When designing integrations:
1. Understand both systems' capabilities
2. Design clean, minimal interfaces
3. Plan error handling and retry logic
4. Consider rate limits and quotas
5. Document assumptions and constraints

Key principles:
- **Ruthless simplicity**: Minimal adapter layers
- **Fail-fast**: Detect issues early with clear errors
- **Observable**: Log all external interactions
- **Defensive**: Handle failures gracefully
```

---

### 3. test-coverage

**Referenced in:** `test-generation-recipe.yaml` (steps 2, 3)

**Purpose:** Test generation and coverage analysis

**Use Cases:**
- Analyzing code for test opportunities
- Generating test suites (unit, integration, edge cases)
- Assessing test coverage
- Identifying untested code paths
- Suggesting test strategies

**Tools Needed:**
- `tool-filesystem` - Read source code and existing tests
- `tool-bash` - Run coverage tools (pytest --cov, coverage report)

**Where:** 🎯 **developer-expertise collection**
- General-purpose development agent
- Testing is universal across projects
- Not recipe-specific
- Complements zen-architect's ANALYZE mode

**Agent Spec:**
```yaml
---
meta:
  name: test-coverage
  description: "Test generation and coverage analysis expert"

tools:
  - module: tool-filesystem
  - module: tool-bash

providers:
  - module: provider-anthropic
    config:
      model: claude-sonnet-4-5
      temperature: 0.4  # Balanced for test creativity + precision
---

You are a testing expert focused on comprehensive test coverage and quality assurance.

Your expertise:
- **Test Strategy**: Unit, integration, edge case, property-based testing
- **Coverage Analysis**: Identifying untested code paths
- **Test Generation**: Creating complete, runnable test suites
- **Test Quality**: Ensuring tests are valuable, not just numerous

When generating tests:
1. **Analyze code structure**: Functions, classes, dependencies, edge cases
2. **Design test strategy**: What to test, why, at what level
3. **Generate test code**: Complete, runnable tests with fixtures
4. **Focus on value**: Test critical paths, complex logic, edge cases

Test generation principles:
- **AAA pattern**: Arrange, Act, Assert
- **Clear names**: Test names explain what's being tested
- **Isolated tests**: No shared state between tests
- **Comprehensive**: Cover normal cases, edge cases, errors

Testing philosophy:
- **60/30/10 pyramid**: 60% unit, 30% integration, 10% e2e
- **Behavior over implementation**: Test what it does, not how
- **Quality over quantity**: Valuable tests, not 100% coverage
- **Fast feedback**: Unit tests run in milliseconds

When analyzing coverage:
1. Identify critical paths (most important, highest risk)
2. Find untested code (gaps in coverage)
3. Assess test quality (do tests actually catch bugs?)
4. Recommend priorities (what to test first)
5. Avoid over-testing (don't test the framework)
```

---

### 4. security-guardian

**Referenced in:** `security-audit-recipe.yaml` (steps 1, 2, 3)

**Purpose:** Security auditing and vulnerability scanning

**Use Cases:**
- Code vulnerability scanning (SQL injection, XSS, etc.)
- Configuration security review
- Dependency vulnerability checking
- Security best practices validation
- Threat modeling

**Tools Needed:**
- `tool-filesystem` - Read code and config files
- `tool-bash` - Run security tools (bandit, safety, npm audit)
- `tool-web` - Check CVE databases and security advisories

**Where:** 🎯 **developer-expertise collection**
- General-purpose development agent
- Security is critical across all projects
- Not recipe-specific
- Specialized expertise domain

**Agent Spec:**
```yaml
---
meta:
  name: security-guardian
  description: "Security auditing and vulnerability analysis expert"

tools:
  - module: tool-filesystem
  - module: tool-bash
  - module: tool-web

providers:
  - module: provider-anthropic
    config:
      model: claude-sonnet-4-5
      temperature: 0.2  # Very precise for security analysis
---

You are a security expert focused on identifying and mitigating vulnerabilities.

Your expertise:
- **OWASP Top 10**: SQL injection, XSS, CSRF, authentication flaws, etc.
- **Dependency Security**: Known vulnerabilities in third-party packages
- **Configuration Security**: Hardcoded secrets, insecure defaults, permissions
- **Code Analysis**: Security anti-patterns and unsafe practices
- **Threat Modeling**: Attack surfaces and risk assessment

When performing security audits:
1. **Vulnerability Scan**: Check for known security issues
2. **Configuration Review**: Secrets, permissions, security headers
3. **Dependency Audit**: Known CVEs in dependencies
4. **Code Patterns**: Identify security anti-patterns
5. **Prioritize Findings**: Severity (critical/high/medium/low) + exploitability

Security analysis principles:
- **Severity-based**: Focus on critical and high-severity issues first
- **Actionable**: Provide specific fixes, not just problems
- **Context-aware**: Understand false positives vs real threats
- **Defense in depth**: Multiple layers of security

When reporting findings:
- **Location**: Exact file and line numbers
- **Severity**: Critical (immediate fix), High (fix soon), Medium (next sprint), Low (backlog)
- **Explanation**: What's vulnerable and why
- **Fix**: Specific remediation steps
- **Impact**: What's at risk if exploited

Security philosophy:
- **Fail closed**: Deny by default, allow explicitly
- **Least privilege**: Minimal permissions needed
- **Defense in depth**: Multiple security layers
- **Observability**: Log security events
```

---

## Placement Decision Matrix

| Agent | Purpose | Scope | Collection | Rationale |
|-------|---------|-------|------------|-----------|
| test-analyzer | Unclear | Testing artifact | ❌ DELETE | Not a real agent, just testing |
| integration-specialist | Integration & dependencies | General dev | developer-expertise | Universal need across projects |
| test-coverage | Test generation & coverage | General dev | developer-expertise | Universal testing need |
| security-guardian | Security auditing | General dev | developer-expertise | Critical universal concern |

---

## Implementation Plan

### Phase 1: Cleanup (5 minutes)

**Action:** Remove testing artifact

```bash
# Delete minimal-test-recipe.yaml (testing artifact)
git rm amplifier-collection-recipes/examples/minimal-test-recipe.yaml
git commit -m "Remove testing artifact minimal-test-recipe.yaml"
```

**Result:** 3 missing agents remain (all going to developer-expertise)

---

### Phase 2: Agent Creation (2-3 hours)

**Create 3 agents in developer-expertise collection:**

1. **integration-specialist.md** (~30 min)
   - Tools: filesystem, bash, web
   - Focus: Dependencies, APIs, external systems
   - Temperature: 0.3 (precise analysis)

2. **test-coverage.md** (~30 min)
   - Tools: filesystem, bash
   - Focus: Test generation, coverage analysis
   - Temperature: 0.4 (balanced creativity + precision)

3. **security-guardian.md** (~30 min)
   - Tools: filesystem, bash, web
   - Focus: Security audits, vulnerabilities
   - Temperature: 0.2 (very precise, security-critical)

**File Structure:**
```
amplifier-collection-developer-expertise/
  agents/
    zen-architect.md          (existing)
    bug-hunter.md             (existing)
    modular-builder.md        (existing)
    post-task-cleanup.md      (existing)
    researcher.md             (existing)
    integration-specialist.md (NEW)
    test-coverage.md          (NEW)
    security-guardian.md      (NEW)
```

---

### Phase 3: Update Examples (30 minutes)

**Update example recipes to note agent requirements:**

1. **dependency-upgrade-recipe.yaml**
   - Add note: "Requires developer-expertise:integration-specialist"
   - Document that it's from developer-expertise collection
   - Provide installation instructions

2. **test-generation-recipe.yaml**
   - Add note: "Requires developer-expertise:test-coverage"
   - Document collection source

3. **security-audit-recipe.yaml**
   - Add note: "Requires developer-expertise:security-guardian"
   - Document collection source

**Alternative:** Add README in examples/ directory explaining agent dependencies

---

### Phase 4: Documentation (30 minutes)

**Update RECIPE_EXAMPLES_STATUS.md:**
- Move agents from "Missing" to "Available in developer-expertise collection"
- Update working/blocked counts
- Add installation instructions for developer-expertise collection

**Update collection README:**
- Document that some examples require developer-expertise collection
- Provide installation command: `amplifier collection add developer-expertise`
- List which examples need which collections

---

### Phase 5: Testing (1 hour)

**Test each new agent:**

```bash
# Install developer-expertise collection
amplifier collection add developer-expertise

# Test integration-specialist
amplifier run "Audit dependencies in this project"

# Test test-coverage
amplifier run "Generate tests for amplifier_module_tool_recipes/models.py"

# Test security-guardian
amplifier run "Perform security audit on amplifier_module_tool_recipes/__init__.py"

# Test recipes that use new agents
amplifier run "execute dependency-upgrade-recipe.yaml with project_path=. package_manager=uv"
amplifier run "execute test-generation-recipe.yaml with file_path=tools/tool-recipes/amplifier_module_tool_recipes/models.py"
amplifier run "execute security-audit-recipe.yaml with file_path=tools/tool-recipes/amplifier_module_tool_recipes/models.py"
```

---

## Decision: Where Do Agents Live?

### Option A: All in developer-expertise ✅ **RECOMMENDED**

**Agents:**
- integration-specialist
- test-coverage
- security-guardian

**Pros:**
- ✅ These are general-purpose development agents
- ✅ Useful across all projects, not just recipes
- ✅ Complements existing developer-expertise agents
- ✅ Follows principle: collections for reusable expertise
- ✅ Recipes collection stays focused on recipe execution
- ✅ Users can use these agents outside of recipes

**Cons:**
- ⚠️ Requires developer-expertise collection exists
- ⚠️ Recipe examples have external dependency

### Option B: In recipes collection

**Agents:**
- integration-specialist
- test-coverage
- security-guardian

**Pros:**
- ✅ Self-contained recipes collection
- ✅ All example recipes work out of box

**Cons:**
- ❌ Reduces reusability (locked to recipes collection)
- ❌ These aren't recipe-specific agents
- ❌ Bloats recipes collection with general-purpose tools
- ❌ Users can't use agents outside recipes context
- ❌ Violates collection design principle (focused scope)

### Final Decision: **Option A** (developer-expertise collection)

**Rationale:**
- These agents have value beyond recipes
- They're expertise domains (testing, security, integration)
- Recipes collection should focus on recipe execution mechanism
- Better follows modular design philosophy
- Creates healthy dependency (recipes → developer-expertise)

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Cleanup | 5 min | Remove minimal-test-recipe.yaml |
| Phase 2: Agent Creation | 2-3 hours | 3 new agents in developer-expertise |
| Phase 3: Update Examples | 30 min | Document agent dependencies |
| Phase 4: Documentation | 30 min | Updated READMEs and status docs |
| Phase 5: Testing | 1 hour | Verify all agents and recipes work |
| **Total** | **4-5 hours** | Complete, tested, documented |

---

## Success Criteria

**All example recipes work:**
- ✅ ultra-minimal-test.yaml (works now)
- ✅ simple-analysis-recipe.yaml (works now)
- ✅ code-review-recipe.yaml (works now)
- ✅ dependency-upgrade-recipe.yaml (works with developer-expertise)
- ✅ test-generation-recipe.yaml (works with developer-expertise)
- ✅ security-audit-recipe.yaml (works with developer-expertise)

**All agents available:**
- ✅ developer-expertise:zen-architect (exists)
- ✅ developer-expertise:bug-hunter (exists)
- ✅ developer-expertise:modular-builder (exists)
- ✅ developer-expertise:researcher (exists)
- ✅ developer-expertise:integration-specialist (NEW)
- ✅ developer-expertise:test-coverage (NEW)
- ✅ developer-expertise:security-guardian (NEW)
- ✅ recipe-author (exists in recipes collection)

**Documentation complete:**
- ✅ Agent specifications written
- ✅ Example recipes annotated with dependencies
- ✅ Status docs updated
- ✅ Installation instructions provided

---

## Next Steps

1. **Verify developer-expertise collection location/repository**
   - Where does it live?
   - Can we add agents to it?
   - Is it separate repo or part of amplifier-app-cli?

2. **Create agents following specs above**
   - Use AGENT_AUTHORING.md patterns
   - Include proper YAML frontmatter
   - Write comprehensive system instructions

3. **Test agents independently**
   - Verify tool access
   - Check temperature settings
   - Validate model choice

4. **Test with recipes**
   - Execute each recipe end-to-end
   - Verify context accumulation
   - Check output quality

5. **Update all documentation**
   - Collection READMEs
   - Status documents
   - Example annotations

---

## Open Questions

1. **Where is developer-expertise collection?**
   - Is it a separate repo?
   - Part of amplifier-app-cli?
   - Part of amplifier-profiles?
   - Needs to be created?

2. **Should recipe-author move to developer-expertise?**
   - It's currently in recipes collection
   - But it's a general development agent
   - Or is it recipe-specific enough to stay?

3. **Agent vs Profile organization**
   - How do collections relate to profiles?
   - Can profiles load agents from multiple collections?
   - How are collection dependencies expressed?

---

## Conclusion

**Clear path forward:**
1. Delete minimal-test-recipe.yaml (testing artifact)
2. Create 3 new agents in developer-expertise collection
3. Update recipe examples with dependency notes
4. Document installation and usage
5. Test end-to-end

**Result:** All example recipes work, agents reusable across projects, clean collection boundaries.

**Estimated effort:** 4-5 hours to complete all phases.
