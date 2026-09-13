# Hypothesis Loop - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Hypothesis Loop workflow.
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

**⚠️ CRITICAL WARNING - Sequential Sections:**

Hypothesis Loop step files use **sequential numbered sections** (e.g., Section 1, 2, 3):
- Currently no decimal sections identified, but protocol applies for future-proofing
- All sections must be executed sequentially without omission
- File sizes currently < 500 lines, but may grow

**📋 Hypothesis Loop Section Patterns:**
- Sequential sections (0, 1, 2, 3...) throughout all steps
- No decimal sections currently identified
- Longest file: step-08-phase4-gate.md (322 lines)

**🚨 INCIDENT PREVENTION:**
- Hypothesis Loop orchestrates multiple phases - section omission could break loop logic
- Protocol added preemptively for consistency and future-proofing

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
- [ ] Am I about to skip verification_state.yaml re-read? → **VIOLATION**
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
- ❌ invoke-workflow executions (Phase 2C, 3, 4)
- ❌ verification_state.yaml re-reads before hypothesis transitions
- ❌ Gate processing (MUST_WORK)
- ❌ Prerequisite dependency checks

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step, ensure entire file is read
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Read verification_state.yaml before EVERY hypothesis transition
- 🔁 Follow prerequisite dependencies from verification_state.yaml

### Role Reinforcement

- ✅ You are a hypothesis verification loop orchestrator
- ✅ Maintain any existing communication style and persona
- ✅ Execute UNATTENDED - no user interaction required
- ✅ You bring multi-hypothesis coordination expertise

---

## Execution Mode

Hypothesis Loop runs in **UNATTENDED mode** (Fully Automatic):
- No user confirmations required
- Automatic progression through hypotheses
- Checkpoint-based state persistence
- Three modes: SINGLE (one hypothesis), STEP (manual control), AUTO (continuous)

---

## Standard Step Navigation

After completing each step:

1. Update checkpoint file (if applicable)
2. Re-read verification_state.yaml for current hypothesis status
3. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not re-reading verification_state.yaml before hypothesis transitions
- Ignoring prerequisite dependencies

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
