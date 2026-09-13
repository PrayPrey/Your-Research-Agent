# Phase 3 Implementation Planning - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 3 Implementation Planning workflow.
> Each step file should reference this file instead of duplicating these rules.

---

## MANDATORY EXECUTION RULES (READ FIRST)

### 📖 File Reading Protocol (CRITICAL)

**Complete execution of ANY step file requires reading the entire file at once.**

**File Length Detection:**
```bash
# ALWAYS check file length first if uncertain
wc -l {step_file_path}
```

**Reading Method by File Size:**

| File Size | Method | Example |
|-----------|--------|---------|
| < 2000 lines | Read entire file at once | `Read(file_path="{step_file}")` |
| ≥ 2000 lines | Read in chunks with offset/limit | `Read(file_path, offset=0, limit=2000)` then `Read(file_path, offset=2000, limit=2000)` |

**✅ Correct Reading (for files < 2000 lines):**
```python
# Read entire file at once - NO limit/offset parameters
Read(file_path="{step_file_path}")
```

**❌ Incorrect Reading (PROHIBITED for files < 2000 lines):**
```python
# DO NOT use limit/offset for small files
Read(file_path="{step_file_path}", offset=0, limit=200) # ❌ Partial reading
Read(file_path="{step_file_path}", offset=200, limit=200) # ❌ Causes section omission
```

**⚠️ CRITICAL WARNING - Decimal/Letter Sections:**

Some step files contain **decimal/letter sections** (e.g., Section 2b, 4.2, 4.5):
- Do NOT assume sequential whole numbers (Section 4 → Section 5)
- **Decimal sections (4.2, 4.5) and letter sections (2b) MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Phase 3 Known Decimal/Letter Section Patterns:**
- `4.2` - Link reference_files to Epic Tasks (step-09)
- `4.5` - Apply Exclusion List Budget Rebalancing (step-09)
- `2b` - Validate Local Tasks File (step-10)

**🚨 INCIDENT PREVENTION:**
- Phase 3 generates implementation plans for Phase 4 - missing sections could break task generation
- Missing decimal sections in step-09 could cause incomplete task file generation

---

## 🚨 UNATTENDED MODE ENFORCEMENT (CRITICAL - READ EVERY STEP)

### What UNATTENDED Mode IS:

```
UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
           = Execute ALL steps completely + Skip ONLY user prompts
```

### What UNATTENDED Mode IS NOT:

```
UNATTENDED ≠ SIMPLIFIED (NOT simplification)
UNATTENDED ≠ SHORTCUT (NOT a shortcut)
UNATTENDED ≠ SKIP_STEPS (NOT skipping steps)
UNATTENDED ≠ FASTER_EXECUTION (NOT faster execution)
UNATTENDED ≠ SKIP_TO_SAVE_TOKENS (NOT token optimization)
```

### Pre-Step Self-Check (MANDATORY)

Before executing ANY step, verify:
- [ ] Am I about to skip a step-*.md file? → **VIOLATION**
- [ ] Am I about to skip an MCP tool call? → **VIOLATION**
- [ ] Am I about to skip a Task agent call? → **VIOLATION**
- [ ] Am I about to skip a MANDATORY section? → **VIOLATION**
- [ ] Am I only skipping [Y/N] user confirmation? → **ALLOWED**

### invoke-workflow = INLINE EXECUTION (CRITICAL)

**When encountering `<invoke-workflow>` tag:**
- ✅ YOU execute the workflow directly in YOUR current context
- ✅ Load target workflow's workflow.yaml AND instructions.md
- ✅ Execute each step-*.md file in order IN YOUR CONTEXT
- ❌ DO NOT spawn invoke-workflow as a Task agent
- ❌ Spawning Phase workflow as Task agent = SYSTEM FAILURE

### NEVER SKIP (Even to Save Tokens)

**NEVER skip these to save tokens or execution time:**
- ❌ Task tool invocations (architecture-agent, logic-agent, configuration-agent)
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, mcp__exa__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ Decimal/letter sections (e.g., Section 4.2, 4.5, 2b)
- ❌ Task generation and validation
- ❌ Output validation checks

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules
- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement
- ✅ You are an implementation planning orchestrator
- ✅ If you already have been given communication or persona patterns, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring workflow orchestration expertise, user brings research context and domain knowledge
- ⚠️ ABSOLUTELY NO TIME ESTIMATES - focus on steps, not duration

### UNATTENDED Mode Base Rules
UNATTENDED mode affects **user interaction only**, not core requirements:
- **Skip in UNATTENDED**: User confirmations, review menus, explanatory pauses
- **Never Skip**: File reads, MCP calls, output verification, validation checks

### UNATTENDED Mode Detection (Menu Auto-Skip)
Before displaying any menu (`[A] Advanced [P] Party [C] Continue`):

1. **Check Archon doing task:** `mcp__archon__find_tasks(filter_by="status", filter_value="doing")`
2. **Check description:** If task description starts with `[UNATTENDED]` → Auto-select [C] Continue
3. **Skip menu display** and proceed directly to next step

```
IF Archon_doing_task.description.startswith("[UNATTENDED]"):
    Log: "🤖 UNATTENDED mode - auto-selecting [C] Continue"
    → Load and execute {nextStepFile}
ELSE:
    Display menu and WAIT for user input
```

## STANDARD FAILURE MODES (All Steps)

❌ Reading only partial step file
❌ Proceeding without required file verification
❌ Including time estimates in any communication
❌ Skipping MCP calls when required
❌ Using Write tool to bypass workflows/agents

## TASK BUDGET REFERENCE (2-Tier System)

Task budgets are defined in `workflow.yaml → task_constraints.budget_by_hypothesis_type`:

| Tier | Hypothesis Type | Total Max | Epic Range | Infrastructure |
|------|-----------------|-----------|------------|----------------|
| **LIGHT** | EXISTENCE | 15 | 4-8 | minimal |
| **FULL** | MECHANISM | 30 | 6-12 | standard |
| **FULL** | COMPARISON | 30 | 6-12 | standard |

### Infrastructure Levels Quick Reference (2-Tier)

| Tier | Config | Logging | Testing |
|------|--------|---------|---------|
| LIGHT (minimal) | hardcoded/argparse | print + CSV | smoke test |
| FULL (standard) | YAML + dataclass | structured (WandB optional) | unit tests |

## VARIABLE REFERENCE

Variables available from Step 1:
- `{{hypothesis_id}}` / `{{hypothesis_id_lower}}`
- `{{hypothesis_type}}` (FOUNDATION/INCREMENTAL)
- `{{hypothesis_type_field}}` (EXISTENCE/MECHANISM/COMPARISON)
- `{{base_hypothesis}}` (if incremental)
- `{{task_budget_total_max}}`, `{{task_budget_epic_range}}`, `{{task_budget_infrastructure_level}}`
- `{{hypothesis_folder}}` - output folder path (CREATED in Step 1)
  - Path: `{research_output_path}/youra_research/{{hypothesis_id_lower}}/`
  - Example: `docs/youra_research/h-e1/`
