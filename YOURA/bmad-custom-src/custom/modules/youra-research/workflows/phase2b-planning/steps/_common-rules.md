# Phase 2B Planning - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 2B Planning workflow.
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

**⚠️ CRITICAL WARNING - Decimal Sections:**

Some step files contain **decimal sections** (e.g., Section 1.5, 2.5):
- Do NOT assume sequential whole numbers (Section 1 → Section 2)
- **Decimal sections MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Phase 2B Section Patterns:**
- All step files use sequential whole-number sections only (no decimal sections found)
- Largest file: step-01-init-parsing.md (313 lines)

**🚨 INCIDENT PREVENTION:**
- Phase 2B decomposes hypotheses - missing sections could skip critical planning steps
- Missing steps in hypothesis generation or dependency analysis could cause incomplete verification plans

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
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ Hypothesis decomposition steps
- ❌ verification_state.yaml updates
- ❌ Dependency analysis

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 🛑 NEVER generate content without user input (Interactive mode)
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ⚠️ ABSOLUTELY NO TIME ESTIMATES

### Role Reinforcement

- ✅ You are a verification planning orchestrator
- ✅ If you already have been given a name, communication_style and persona, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring systematic hypothesis decomposition expertise, user brings research context
- ✅ Maintain collaborative professional tone throughout

---

## UNATTENDED Mode Detection

Before displaying any menu (`[A] Advanced [P] Party [C] Continue`):

1. **Check Archon doing task:** `mcp__archon__find_tasks(filter_by="status", filter_value="doing")`
2. **Check description:** If task description starts with `[UNATTENDED]` → Auto-select [C] Continue
3. **Skip menu display** and proceed directly to next step

---

## Menu Options Reference

Standard menu format for Interactive mode:
```
**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue [X] Exit
```

- **[A] Advanced Elicitation**: Invoke advanced questioning workflow
- **[P] Party Mode**: Invoke multi-agent discussion
- **[C] Continue**: Proceed to next step
- **[X] Exit**: Exit workflow gracefully

---

## Standard Step Navigation

After completing each step:

1. Update verification_state.yaml as needed
2. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not updating verification_state.yaml when required
- Not reading complete step file before execution

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
