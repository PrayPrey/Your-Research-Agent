# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-04-21T02:30:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** IMPLEMENTATION_INCOMPLETE

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Implementation Completion | 0/15 tasks | N/A | N/A |
| Code Generation | 0% | N/A | Complete failure |
| Experiment Execution | Not run | N/A | N/A |

## Root Cause Analysis

1. **Workflow Interruption:** Phase 4 workflow stopped after Step 1a (data setup) without proceeding to code generation (Step 2)
   
2. **Complexity Mismatch:** Hypothesis h-e1 classified as EXISTENCE but has MECHANISM-tier implementation complexity:
   - 15 tasks across 6 epics (EXISTENCE typical: ≤8 tasks, ≤3 epics)
   - 20 model training requirement (40+ GPU hours)
   - Complex alignment algorithm (Hungarian algorithm, layer-wise permutation)
   - Statistical analysis with bootstrap confidence intervals
   
3. **Scope Underestimation:** Phase 2C experiment design underestimated implementation burden:
   - Standard EXISTENCE: baseline vs. proposed (1-2 models, quick PoC)
   - This hypothesis: 20 models + permutation alignment + CKA computation + correlation analysis
   - More appropriate for MECHANISM classification or multi-phase research project

4. **Resource Planning Gap:** Implementation requirements not properly assessed:
   - Each ResNet-20 model: ~2 hours training (200 epochs on CIFAR-10)
   - 20 models total: 40+ hours GPU time
   - Additional time for alignment, CKA, and analysis
   - Not suitable for "quick validation" - this is a substantial experiment

## Lessons Learned

1. **Hypothesis Classification Matters:**
   - EXISTENCE hypotheses should be simple PoCs (< 5 hours implementation + validation)
   - Complex multi-model experiments belong in MECHANISM tier
   - Task count is a good proxy: >10 tasks suggests MECHANISM, not EXISTENCE

2. **Model Count Drives Complexity:**
   - N=20 models for correlation analysis is research-scale, not PoC-scale
   - For EXISTENCE validation, N=3-5 models sufficient to test "does it work?"
   - Scale to N=20 only if initial PoC passes (progressive validation)

3. **Git Re-Basin Alignment is Non-Trivial:**
   - Permutation finding via Hungarian algorithm is complex implementation
   - Layer-wise activation extraction requires careful hook management
   - Should be tested on 2 models first before scaling to 20

4. **Training Time is Real Cost:**
   - 200 epochs × 20 models = substantial GPU investment
   - For PoC, reduce epochs (50-100) and models (3-5)
   - Use smaller architecture (ResNet-8) if speed matters more than realism

5. **Scope Creep in Experiment Design:**
   - Phase 2C added "complete correlation study" scope
   - Should have been "does alignment improve correlation at all?" (simpler)
   - Full study (20 models, strict threshold Δρ ≥ +0.3) appropriate for MECHANISM

## Recommendations for Phase 0 Re-design

### Option 1: Simplify h-e1 to True EXISTENCE PoC

**Revised Hypothesis:**
- **Statement:** "Permutation alignment improves weight-space correlation with CKA"
- **Model Count:** 3-5 models (not 20)
- **Architecture:** ResNet-8 or ResNet-20 with 100 epochs (not 200)
- **Gate:** Δρ > 0 (any improvement), not Δρ ≥ +0.3
- **Implementation:** 6-8 tasks, 3 epics
- **Timeline:** 1-2 days (not 1+ weeks)

**Rationale:**
- Answers core question: "Does the methodology work?"
- If passes, scale to full study in h-m1 (MECHANISM tier)
- If fails with N=3, no point trying N=20

### Option 2: Reclassify as MECHANISM Hypothesis

**Keep Current Scope, Change Classification:**
- **Type:** MECHANISM (not EXISTENCE)
- **All specs unchanged:** 20 models, Δρ ≥ +0.3, full alignment
- **Expectations:** This is a substantial experiment (5-7 days)
- **Gate:** SHOULD_WORK or DETERMINES_SUCCESS (not MUST_WORK)
- **Dependencies:** Consider h-e1-simple as prerequisite

**Rationale:**
- Current design is already MECHANISM-tier work
- Acknowledge reality instead of forcing EXISTENCE label
- Set appropriate expectations for timeline and resources

### Option 3: Progressive Validation (Pilot + Full)

**Split into Two Hypotheses:**

**h-e1-pilot (EXISTENCE):**
- 3 models, 100 epochs, ResNet-8
- Basic permutation alignment (no scaling)
- Gate: Δρ > +0.1 (promising signal)
- Timeline: 1-2 days

**h-e1-full (MECHANISM, prereq: h-e1-pilot):**
- 20 models, 200 epochs, ResNet-20
- Full alignment (permutation + scaling)
- Gate: Δρ ≥ +0.3 (strong result)
- Timeline: 5-7 days
- Only run if h-e1-pilot passes

**Rationale:**
- Fail fast if methodology fundamentally broken
- Invest GPU time only if pilot shows promise
- Two smaller chunks easier than one large failure

## What NOT To Do (Anti-Patterns)

❌ **Don't:** Keep EXISTENCE label with 20-model requirement
- This creates false expectations ("quick PoC")
- Sets up for repeated failures

❌ **Don't:** Add more retries without scope change
- Problem is scope, not execution
- More attempts won't fix design mismatch

❌ **Don't:** Skip pilot and go straight to 20 models
- If alignment doesn't work, wastes 40+ GPU hours
- Pilot with N=3 costs 6 hours, fails fast if broken

❌ **Don't:** Lower quality to hit EXISTENCE timeline
- Reducing epochs to 50 may not converge properly
- Using toy dataset invalidates scientific validity
- Better to reclassify than compromise rigor

## What Showed Promise

✅ **Data Setup Worked:** CIFAR-10 download, conda environment, GPU verification all succeeded
- Infrastructure is solid
- Problem is scope, not execution capability

✅ **Experiment Design Clear:** Phase 2C spec is detailed and implementable
- If scope were smaller, implementation would succeed
- Design quality is not the issue

✅ **Phase 3 Planning Thorough:** 15 tasks well-defined with dependencies
- Task breakdown is professional
- Just too many tasks for EXISTENCE tier

## Feedback for Next Phase

### Phase 0 (Brainstorming)

**Context to Provide:**
- Original hypothesis h-e1 attempted but failed due to scope mismatch
- Core question valid: "Does symmetry normalization improve correlation?"
- Implementation design solid, just too large for EXISTENCE tier
- Need decision: Simplify, Reclassify, or Split?

**Questions to Answer:**
1. Is N=3-5 model pilot acceptable to validate methodology?
2. If pilot fails, is full N=20 study still worth pursuing?
3. Should Git Re-Basin alignment be simplified (permutation-only)?
4. Is Δρ ≥ +0.3 threshold negotiable, or just existence of improvement?

### Phase 2A (If Re-attempting)

**Recommended Changes:**
- Explicitly note if choosing "Simplified PoC" path
- Call out model count (N) as critical scope parameter
- Estimate GPU hours before finalizing design
- Consider pilot-then-scale approach

### Phase 2C (Experiment Design)

**Scope Boundaries:**
- EXISTENCE: N ≤ 5 models, ≤ 8 tasks, < 10 GPU hours
- MECHANISM: N ≤ 20 models, ≤ 15 tasks, < 50 GPU hours
- If exceeding MECHANISM bounds, split into multiple hypotheses

---

## Technical Details (For Reference)

### What Was Attempted

**Phase 4 Steps Completed:**
- ✅ Step 1: Initialize (load checkpoint, connect to Archon)
- ✅ Step 1a: Data Setup (CIFAR-10 download, conda env, GPU check)
- ❌ Step 2: Coder Loop (NOT STARTED - no code generated)
- ❌ Step 3-8: All subsequent steps skipped

**Checkpoint State at Failure:**
- `current_step: 2` (should start Coder loop)
- `tasks.completed: 0/15`
- `coder_validator_cycles: 0/5`
- `data_setup.status: completed`
- `code_files_generated: []`

### Why Step 2 Didn't Execute

**Most Likely Causes:**
1. Session interruption (timeout, resource limit, manual stop)
2. UNATTENDED mode issue (workflow didn't auto-proceed)
3. Context loss (checkpoint loaded but execution didn't continue)

**Not Due To:**
- ❌ Code errors (no code was generated to error)
- ❌ Data issues (data setup completed successfully)
- ❌ Environment problems (conda env created, GPU available)

### If Retrying With Same Scope

**Pre-Execution Checklist:**
1. Allocate 50+ GPU hours for full run
2. Enable session persistence (avoid interruptions)
3. Monitor Step 1 → Step 2 transition
4. Set execution timeout > 48 hours
5. Consider running Phase 4 in dedicated session

**Expected Timeline (If Implementation Completes):**
- Step 2 (Coder Loop): 4-6 hours (15 tasks, complex implementations)
- Step 3 (Validator): 1-2 hours
- Step 5 (Model Training): 40-50 hours (20 models × 2 hours each)
- Step 6-8 (Analysis, Report): 2-3 hours
- **Total: 47-61 hours**

---

*For cross-phase reference*
*Written at: 2026-04-21T02:30:00Z*
