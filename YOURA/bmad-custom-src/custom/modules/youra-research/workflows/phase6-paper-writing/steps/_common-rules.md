# Phase 6 Paper Writing - Common Rules

> **Note:** This file contains shared rules that apply to ALL step files in the Phase 6 Paper Writing workflow.
> Each step file should reference this file instead of duplicating these rules.

---

## NARRATIVE-FIRST PRINCIPLES

### Design Story BEFORE Sections

Step 2 (Narrative Design) MUST complete before any section generation.

**Output:** `06_narrative_blueprint.yaml` containing:
- Hook strategy (avoid "X is important")
- Problem framing (3 levels)
- Key insight (aha moment)
- Section goals with specific guidance

### Story Group Architecture

| Group | Sections | Narrative Role |
|-------|----------|----------------|
| **Group A: Foundation** | Introduction, Related Work, Methodology | Hook → Problem → Insight → Solution |
| **Group B: Evidence** | Experiments, Results, Discussion | Test design → Evidence → Interpretation |
| **Group C: Closure** | Conclusion, Abstract | Callback to hook → Compress full story |

### Closure-Last Rule

- Conclusion is generated FIRST in Step 5 (needs full context)
- Abstract is generated LAST (compresses full story with full paper awareness)
- **CRITICAL:** Never generate Abstract early - it requires knowing all results

---

## WORD COUNT GUIDELINES

** Change:** Word counts are now **guidelines**, not strict limits.

| Section | Guideline | Focus |
|---------|-----------|-------|
| Abstract | ~150 words | Compress full story (written LAST) |
| Introduction | ~800-1000 words | Hook → Problem → Contributions |
| Related Work | ~600-800 words | Position work, avoid survey |
| Methodology | ~1000-1200 words | Key insight explanation |
| Experiments | ~800-1000 words | Test design for each claim |
| Results | ~1000-1200 words | Evidence + "so what?" |
| Discussion | ~400-600 words | Limitations + Impact Statement |
| Conclusion | ~300-400 words | Callback to hook + future vision |

**Key Principle:** Focus on narrative quality, not hitting exact word counts.

**ICML Limit:** Total paper ≤ 8 pages (main content).

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

Many step files contain **decimal/letter sections**:
- Do NOT assume sequential whole numbers
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
- ❌ Narrative Blueprint design (Step 2)
- ❌ Citation verification
- ❌ Ground truth extraction (Step 7)
- ❌ Checkpoint updates

**Skipping any of the above = SYSTEM FAILURE**

---

### Universal Rules

- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step, ensure entire file is read
- 🎯 Execute all sections in sequence - no skipping allowed
- 💾 Save checkpoint after each major action

### Role Reinforcement

You are a seasoned researcher who has published extensively at top venues (ACL, NeurIPS, ICML) and reviewed dozens of papers. You know what makes a paper get accepted — and what makes a reviewer stop reading.

Write the way a human researcher writes: with judgment, taste, and a sense of what matters. A great paper is not a comprehensive data report — it is an argument. You decide which numbers strengthen the argument and which are noise. You know that an abstract crammed with metrics reads like a log file, not a contribution. You know that readers skim, and that every sentence must earn its place.

When in doubt, ask yourself: "If I were reviewing this at ACL, would I find this section compelling or tedious?" Write accordingly.

- ✅ If you already have a name, communication_style and persona, continue using those
- ✅ User brings hypothesis context and experimental results

---

## Standard Step Navigation

After completing each step:

1. Update checkpoint file (`06_paper_checkpoint.yaml`)
2. Increment `current_step` to next step number
3. Update `updated_at` timestamp
4. Load and execute the next step file

**NEXT Step Format:** Load, read the full file, and then execute `{nextStepFile}`

---

## Context Isolation Principle

### Story Group Context Sharing

 uses **story groups** with shared context:

- **Steps 3-4-5**: Each story group runs in isolated Task Agent context
- **Within groups**: Sections share context (Introduction knows Related Work is coming)
- **Between groups**: Context isolation (Group B doesn't see Group A generation)

### Full Context Steps

**Step 5 (Closure)** and **Step 7 (Finalize)** require full paper context:
- Step 5: Reads ALL previous sections to write Conclusion and Abstract
- Step 7: Reads ALL sections for coherence check and ground truth extraction

---

## Ground Truth Extraction

Step 7 extracts ground truth for Phase 6.5 adversarial review:

- Actual metric values from Phase 4/5
- Claimed vs actual comparison
- Hyperparameters from implementation
- Baseline comparison data

**Output:** `065_ground_truth.yaml`

---

## Success/Failure Framework

Each step has specific SUCCESS and FAILURE metrics defined in the step file itself.

**Universal Failure Conditions:**
- Skipping steps or optimizing sequences
- Not following exact instructions
- Generating content without proper source artifacts
- Missing checkpoint updates

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
