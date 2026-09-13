# Phase 5 Baseline Comparison - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 5 Baseline Comparison workflow.
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

Many step files contain **decimal/letter sections** (e.g., Section 5.5, 9.4.1, 10a, 10b):
- Do NOT assume sequential whole numbers (Section 9 → Section 10)
- **Decimal sections (5.5, 9.4.1, 9.8.7, 10.5.1) MUST NOT be skipped**
- **Letter sections (10a, 10b) MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Phase 5 Known Decimal/Letter Section Patterns:**
- `5.5` - Baseline environment verification (Mode B)
- `9.4.1`, `9.4.2`, `9.4.3` - Runner script creation (step-09)
- `9.8.1` through `9.8.7` - Figure generation subsections (step-09)
- `10.5.1` - Multi-baseline update (step-10a)
- `10a`, `10b` - Gate evaluation and finalization

**🚨 INCIDENT PREVENTION:**
- Phase 5 is CRITICAL - contains DETERMINES_SUCCESS gate
- Missing sections in Phase 5 can cause incorrect gate evaluation

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
- ❌ Task tool invocations for sub-agents (baseline-validator-agent)
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, mcp__exa__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ LLM-based verifications (pattern search alone is INSUFFICIENT)
- ❌ Decimal/letter sections (e.g., Section 5.5, 9.4.1, 10a, 10b)
- ❌ Checkpoint updates (when specified in step files)
- ❌ Output validation checks
- ❌ DETERMINES_SUCCESS gate processing

**Skipping any of the above = SYSTEM FAILURE**

### Phase 5 Specific MANDATORY Requirements

| Step | MANDATORY Requirements |
|------|----------------------|
| step-07 | Archon KB search BEFORE each code generation (MANDATORY) |
| step-08 | Task tool with `subagent_type="baseline-validator-agent"` (MANDATORY) |
| step-09 | Full figure generation (all 9.8.X subsections) |
| step-10a/10b | DETERMINES_SUCCESS gate processing |

---

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action (see File Reading Protocol above)
- 🔄 CRITICAL: When loading next step, ensure entire file is read (see File Reading Protocol above)
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Save checkpoint after each major action

### Role Reinforcement

- ✅ You are a baseline comparison orchestrator
- ✅ Maintain any existing communication style and persona
- ✅ Execute UNATTENDED - no user interaction required
- ✅ You bring rigorous comparison methodology expertise

---

## Execution Mode

Phase 5 runs in **UNATTENDED mode** (Fully Automatic):
- No user confirmations required
- Automatic progression through steps
- Checkpoint-based state persistence
- Automatic error recovery

---

## Multi-Baseline Schema

Phase 5 supports comparison against multiple baselines:
- Primary: 3 baselines (ideal)
- Fallback: 2 baselines (acceptable)
- Minimum: 1 baseline (graceful degradation)

---

## Graceful Degradation Protocol

If baseline search/adaptation fails:
1. Log the failure reason
2. Reduce baseline count (3 → 2 → 1)
3. Continue with remaining baselines
4. Only fail if ALL baselines fail

---

## Checkpoint Protocol

Always load checkpoint at step entry:
```python
checkpoint = read_yaml(checkpoint_file) # {baseline_folder}/05_baseline_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-init first.")
```

---

## Agent Spawning Protocol

Phase 5 uses Task tool to spawn:
- `baseline-validator-agent` (step-08)

Always use Task tool with correct `subagent_type` parameter.

---

## Standard Step Navigation

After completing each step:

1. Update checkpoint file (`05_baseline_checkpoint.yaml`)
2. Update verification_state.yaml as needed
3. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not detecting hallucination/mock data patterns
- Not saving checkpoint after major actions

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
