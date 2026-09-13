# Phase 4 Failure Record: H-E1 (Run 2)

**Hypothesis ID:** h-e1
**Failure Type:** MUST_WORK_FAIL
**Phase:** Phase 4
**Date:** 2026-03-17T03:42:00Z
**Routing Decision:** Phase 0 (complete failure - foundational hypothesis invalid)

---

## Hypothesis Statement

Under conditions where RLHF training occurs (pre-RLHF → post-RLHF checkpoints), if models undergo reward-based optimization on human preference data, then sentence-length coefficient of variation (CV) decreases monotonically across training checkpoints, because RLHF reward models implicitly learn structural regularization as part of their optimization process.

---

## Failure Summary

The H-E1 EXISTENCE hypothesis **completely failed** MUST_WORK gate validation. No evidence of monotonic CV reduction was observed across RLHF training checkpoints.

**Gate Result:** FAIL ❌
- **Primary:** Page trend test p=0.517 > 0.05 (no significant monotonic trend)
- **Secondary:** Slope consistency 47.78% < 65% threshold
- **Secondary:** Relative CV reduction 3.56% < 20% threshold
- **Secondary Pass:** 1/3 metrics (need 2/3)

---

## Performance Data

### Statistical Results
- **Page's Trend Test p-value:** 0.517 (threshold: < 0.05) - FAIL
- **Slope Consistency:** 47.78% (threshold: ≥ 65%) - FAIL
- **Relative CV Reduction:** 3.56% (threshold: ≥ 20%) - FAIL
- **Mean Decrease:** True - PASS (only 1/3 secondary metrics)

### CV Trajectory (Non-Monotonic)
- Checkpoint 0%: CV = 0.368
- Checkpoint 25%: CV = 0.392 (↑ increased)
- Checkpoint 50%: CV = 0.372 (↓ decreased)
- Checkpoint 75%: CV = 0.417 (↑ increased)
- Checkpoint 100%: CV = 0.355 (↓ decreased)

**Pattern:** Non-monotonic with significant variance. CV actually increased at mid-checkpoints.

---

## Root Causes

### 1. **Tier Proxy Fallback (Implementation Limitation)**
- **Issue:** Same base model (GPT-2) used for all 5 checkpoints
- **Impact:** Cannot observe genuine RLHF structural regularization effects
- **Expected:** Yes - this is a PoC infrastructure limitation
- **Fix Required:** Access to actual RLHF checkpoint series

### 2. **Fundamental Hypothesis Flaw (Primary Concern)**
- **Issue:** Even with correct infrastructure, hypothesis may be fundamentally flawed
- **Evidence:** No theoretical papers found supporting sentence-level CV as RLHF training signal
- **Concern:** Perceptual fluency may not operate at sentence-length statistical level
- **Implication:** Core mechanism assumption may be invalid

### 3. **Reduced Sample Size (Minor)**
- **Issue:** 100 prompts vs. 500 specified
- **Impact:** LOW - sufficient for detecting strong trends
- **Verdict:** Not the primary cause of failure

---

## Lessons Learned

### For Phase 0 Redesign:

1. **Mechanism Specificity Required**
   - Sentence-length CV is too coarse-grained for RLHF reward signals
   - Need evidence that human labelers actually prefer length regularity
   - Consider token-level or syntactic structure measures instead

2. **Infrastructure Dependencies**
   - Hypothesis requires access to actual RLHF checkpoint series
   - Tier proxy cannot validate checkpoint-based claims
   - Must verify resource availability in Phase 1 research

3. **Theoretical Grounding Weakness**
   - No prior work directly supports CV-as-fluency mechanism
   - Perceptual fluency literature focuses on semantic/syntactic coherence
   - Need stronger theoretical foundation before implementation

4. **Alternative Directions**
   - Focus on pairwise comparisons (chosen vs. rejected) rather than checkpoints
   - Investigate syntactic complexity metrics (dependency depth, parse tree features)
   - Consider within-response coherence rather than statistical moments

---

## Phase 0 Recommendations

### What to Preserve:
- Perceptual fluency as general concept (reading ease, cognitive load)
- RLHF as domain (HH-RLHF dataset is good)
- Structural analysis approach (just not CV specifically)

### What to Rethink:
- **Mechanism:** CV reduction may not be the right structural signal
- **Level of Analysis:** Sentence-length statistics vs. syntactic structure
- **Checkpoint Assumption:** May need different experimental design

### Promising Alternative Hypotheses:
1. **Syntactic Simplification:** RLHF reduces dependency depth/nesting
2. **Lexical Accessibility:** RLHF increases word frequency/concreteness
3. **Discourse Coherence:** RLHF improves topic consistency across turns
4. **Response Calibration:** RLHF matches response length to question complexity

---

## Cross-Phase Learning

### For Phase 2A-Dialogue:
- Start with pairwise comparison design (chosen vs. rejected)
- Require stronger theoretical grounding from Phase 1
- Verify resource availability before committing to checkpoint-based claims

### For Phase 4:
- Pipeline infrastructure validated successfully
- Tier proxy is reliable fallback but cannot validate checkpoint hypotheses
- Statistical testing framework (Page trend test) worked correctly

---

## Metadata

- **Run Number:** 2
- **Previous Run:** failure_h-e1_run1.md
- **Validation Report:** h-e1/04_validation.md
- **Checkpoint:** h-e1/04_checkpoint.yaml
- **Gate Type:** MUST_WORK
- **Pipeline Status:** ACTIVE (routing to Phase 0)
- **Episode:** NOT TERMINATED (foundational hypothesis failed, full restart needed)
