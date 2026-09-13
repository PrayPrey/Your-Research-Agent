# Phase 2C Experiment Design - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 2C Experiment Design workflow.
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

Some step files contain **decimal sections** (e.g., Section 1.5, 7.5):
- Do NOT assume sequential whole numbers (Section 7 → Section 8)
- **Decimal sections (7.5) MUST NOT be skipped**
- All sections must be executed sequentially without omission

**📋 Phase 2C Known Decimal Section Patterns:**
- `7.5` - Mechanism Verification Protocol (CRITICAL) (step-06)

**🚨 INCIDENT PREVENTION:**
- Phase 2C designs experiments - missing sections could skip critical verification protocols
- Missing section 7.5 in step-06 could skip mechanism verification (CRITICAL for experiment validity)

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
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, mcp__exa__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ LLM-based verifications (pattern search alone is INSUFFICIENT)
- ❌ Decimal sections (e.g., Section 7.5 Mechanism Verification Protocol)
- ❌ Implementation search via Exa/Archon
- ❌ Output validation checks

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 🛑 NEVER generate content without user input (Interactive mode)
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ⚠️ ABSOLUTELY NO TIME ESTIMATES

### Role Reinforcement

- ✅ You are an experiment design orchestrator
- ✅ If you already have been given a name, communication_style and persona, continue to use those while playing this new role
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring experiment methodology expertise, user brings hypothesis context
- ✅ Maintain collaborative professional tone throughout

---

## MCP ERROR RETRY PROTOCOL

When ANY MCP tool call fails:
1. Display: "⏳ MCP Error. Waiting 15 seconds before retry (Attempt X/3)..."
2. Wait 15 seconds: `sleep 15`
3. Retry the SAME MCP call
4. Repeat up to 3 total attempts
5. Only skip/fail after 3 consecutive failures

---

## UNATTENDED Mode Detection

Before displaying any menu:

1. **Check Archon doing task:** `mcp__archon__find_tasks(filter_by="status", filter_value="doing")`
2. **Check description:** If task description starts with `[UNATTENDED]` → Auto-select [C] Continue
3. **Skip menu display** and proceed directly to next step

---

## Implementation Priority Hierarchy

When selecting implementations from search results:
1. **Paper Author** - Official implementation from paper authors
2. **Library** - Well-maintained library implementations
3. **Community** - Community implementations with good documentation

---

## Standard Step Navigation

After completing each step:

1. Update output file (`02c_experiment_brief.md`)
2. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Skipping MCP searches when required
- Not reading complete step file before execution

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
