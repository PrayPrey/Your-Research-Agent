# Phase 6.5 Adversarial Review - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 6.5 Adversarial Review workflow.
> Each step file should reference this file instead of duplicating these rules.

---

## ISSUE SEVERITY

### FATAL Issues
- **Definition:** Fundamental contradiction or impossible claim
- **Action:** MUST fix or WITHDRAW claim
- **Blocks Convergence:** YES

### MAJOR Issues
- **Definition:** Significant weakness attackable by reviewers
- **Action:** MUST fix with evidence
- **Blocks Convergence:** YES

### ~~MINOR Issues~~ → human_review_notes

**IMPORTANT:** MINOR issues are NO LONGER auto-fixed.

**Instead, they are:**
1. **Collected** in `065_human_review_notes.md`
2. **Categorized** by type: typo, grammar, style, clarity, formatting
3. **Left for human review** after workflow completes

**Rationale:**
- AI auto-fixing style/grammar can introduce new errors
- Minor issues don't block acceptance
- Human can review and fix more carefully
- Reduces unnecessary paper churn

**Categories for human_review_notes:**
- `typo`: Spelling errors, misspellings
- `grammar`: Subject-verb agreement, tense issues
- `style`: Awkward phrasing, wordiness
- `clarity`: Ambiguous sentences, unclear references
- `formatting`: Inconsistent formatting, minor layout issues

---

## CONVERGENCE CRITERIA

### Automatic Convergence

```yaml
auto_converge:
  conditions:
    - fatal_issues == 0 # MUST be true
    - major_issues == 0
    - persuasiveness_passed == true
    - round_number >= 2 # Minimum 2 rounds

  force_stop:
    - max_rounds: 3
    - same_issues_repeated: 2 # Same issue found twice = needs human
```

### Convergence Recommendations

| Condition | Recommendation |
|-----------|----------------|
| FATAL=0, MAJOR=0, persuasive | `CONDITIONAL_ACCEPT` |
| FATAL=0, MAJOR>0 OR not persuasive | `MINOR_REVISION` |
| FATAL>0 | `MAJOR_REVISION` |

---

## THREE-PERSONA ADVERSARY REVIEW

### Persona 1: Accuracy Checker
- **Role:** Fact-checker and claim verifier
- **Focus:** Numbers match ground truth, methodology accurate, baselines fair
- **Uses:** `065_ground_truth.yaml`, Phase 4/5 files

### Persona 2: Bored Reviewer
- **Role:** Busy NeurIPS reviewer with 5 papers to review today
- **Focus:** Would I continue reading? Problem clear? Novelty clear?
- **Uses:** `06_narrative_blueprint.yaml`

### Persona 3: Skeptical Expert
- **Role:** Domain expert looking for holes in claims
- **Focus:** Is this novel? Fair baselines? Overclaims? Missing limitations?
- **Uses:** Section files, references

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

Many step files contain **decimal/letter sections** (e.g., Section 2.1, 3.2, 4.1-4.8):
- Do NOT assume sequential whole numbers (Section 2 → Section 3)
- **Decimal sections MUST NOT be skipped**
- All sections must be executed sequentially without omission

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
- ❌ Task tool invocations (adversary-agent-v2, revision-agent)
- ❌ MCP tool calls (mcp__archon__*, mcp__serena__*, etc.)
- ❌ MANDATORY sections (clearly marked in step files)
- ❌ Multi-round review iterations
- ❌ Checkpoint updates
- ❌ human_review_notes collection

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step, ensure entire file is read
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Save checkpoint after each major action

### Role Reinforcement

- ✅ You are an adversarial review specialist with three personas
- ✅ Maintain any existing communication style and persona
- ✅ Execute UNATTENDED - no user interaction required
- ✅ You bring critical analysis and improvement expertise

---

## Execution Mode

Phase 6.5 runs in **UNATTENDED mode** (Fully Automatic):
- No user confirmations required
- Automatic progression through steps
- Checkpoint-based state persistence
- Multi-round adversarial review loop

---

## Agent Spawning Protocol

Phase 6.5 uses Task tool to spawn:
- `adversary-agent-v2` (steps 02, 05) - **Updated agent**
- `revision-agent` (steps 03, 06)

Always use Task tool with correct `subagent_type` parameter.

**Agent File Locations:**
- `agents/adversary-agent-v2.md` - Three-persona adversary
- `agents/revision-agent.md` - Revision agent

---

## Standard Step Navigation

After completing each step:

1. Update checkpoint file (`065_review_checkpoint.yaml`)
2. : Update `human_review_notes` if MINOR issues found
3. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Not detecting paper quality issues
- Missing checkpoint updates

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
