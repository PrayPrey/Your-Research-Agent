# Phase 4 Coding - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 4 Coding workflow.
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

Many step files contain **decimal/letter sections** (e.g., Section 0.5, 2.5, 3.5, 1b, 5a):
- Do NOT assume sequential whole numbers (Section 2 → Section 3)
- **Section 2.5, 3.5, etc. MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Known Decimal Section Patterns:**
- `0.5` - Checkpoint loading (common across many steps)
- `2.5` - Deferred operations execution (step-08-completion.md) ⚠️ **INCIDENT SITE**
- `3.5` - Enhanced validation checks
- `1b`, `2b`, `5a`, `5b`, `5c` - Branching logic sections
- `9.1`, `9.2`, `9.3` - Multi-part completion sections

**🚨 INCIDENT HISTORY:**
- **2026-01-14**: Phase 4 step-08-completion.md Section 2.5 was omitted due to reading only 350/566 lines
- **Impact**: `execute_deferred_archon_operations()` was never called, causing research folder archive failure
- **Root Cause**: Used `Read(file_path, limit=200)` twice instead of reading entire file once
- **2026-01-16**: Phase 4 step-05a Section 1.6 LLM-based mock detection was SKIPPED
- **Impact**: Mock/synthetic data passed as REAL experiment, false PASS gate
- **Root Cause**: LLM self-optimized to "save tokens" by skipping LLM verification

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
- ❌ Task tool invocations for sub-agents (coder-agent, validator-agent)
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, mcp__exa__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ LLM-based verifications (pattern search alone is INSUFFICIENT)
- ❌ Decimal/letter sections (e.g., Section 1.5, 1.6, 2.5, 5a, 5b, 5c)
- ❌ Checkpoint updates (when specified in step files)
- ❌ Output validation checks
- ❌ File verification requirements

**Skipping any of the above = SYSTEM FAILURE**

### Phase 4 Specific MANDATORY Requirements

| Step | MANDATORY Requirements |
|------|----------------------|
| step-02 | Task tool with `subagent_type="coder-agent"` |
| step-03 | Task tool with `subagent_type="validator-agent"` |
| step-05a | Section 1.6 LLM-based mock detection (NOT just pattern search) |
| step-05c | Section 2 LLM-based post-experiment verification |
| step-06 | Gate processing with full metrics validation |

---

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action (see File Reading Protocol above)
- 🔄 CRITICAL: When loading next step, ensure entire file is read (see File Reading Protocol above)
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Save checkpoint after each major action

### Role Reinforcement

- ✅ You are an implementation orchestrator
- ✅ Maintain any existing communication style and persona
- ✅ Execute UNATTENDED - no user interaction required
- ✅ You bring code generation and validation expertise

---

## Execution Mode

Phase 4 runs in **UNATTENDED mode** (Fully Automatic):
- No user confirmations required
- Automatic progression through steps
- Checkpoint-based state persistence
- Automatic error recovery

---

## SDD (Specification-Driven Development) Phases

The Coder Agent follows SDD methodology:
1. **SPEC** - Read and understand specifications from 03_*.md files
2. **TEST** - Generate spec compliance tests
3. **IMPL** - Create implementation to match specs
4. **VERIFY** - Verify spec compliance via pytest

---

## Checkpoint Protocol

Always load checkpoint at step entry to handle context loss:
```python
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")
```

---

## Agent Spawning Protocol

Phase 4 uses Task tool to spawn:
- `coder-agent` (step-02)
- `validator-agent` (step-03)

Always use Task tool with correct `subagent_type` parameter.

---

## Standard Step Navigation

After completing each step:

1. Update checkpoint file (`04_checkpoint.yaml`)
2. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not saving checkpoint after major actions
- Running validation commands directly without Task tool

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
