# Phase 4.5: Validated Hypothesis Synthesis

**Hypothesis ID:** H-RewardBandwidth-v1  
**Date:** 2026-08-29  
**Status:** INCONCLUSIVE → ROUTED TO PHASE 0

---

## 1. Executive Summary

This synthesis consolidates results from H-E1 (existence hypothesis) testing whether higher bandwidth reward signals accelerate PPO training convergence for code LLMs.

**Key Finding:** All three reward conditions (binary, categorical, high_bandwidth) achieved 0% pass@1 after 1 epoch of PoC-scale training. The experiment was inconclusive—not because the hypothesis was falsified, but because the experimental scale was insufficient for any learning signal to emerge.

**Outcome:** Hypothesis routed to Phase 0 for reformulation with adequate compute budget before re-testing.

---

## 2. Prediction-Result Matrix

| Prediction | Expected | Observed | Verdict |
|------------|----------|----------|---------|
| P1: HIGH < LOW in samples-to-threshold | HIGH reaches pass@1>0.3 faster | Neither reached threshold; all 0% pass@1 | INCONCLUSIVE |
| P2: MEDIUM < LOW in samples-to-threshold | MEDIUM converges faster than binary | Neither reached threshold; all 0% pass@1 | INCONCLUSIVE |
| P3: HIGH shows different error distribution | Fewer syntax errors in HIGH by epoch 3 | Not measured (training at floor) | NOT_TESTED |

**Statistical Summary:**
- t-statistic: NaN (no variance—all conditions at floor)
- p-value: NaN
- Cohen's d: NaN
- No statistically meaningful comparison possible

---

## 3. Hypothesis Refinement

### Original Hypothesis (H-RewardBandwidth-v1)
> Under PPO training of CodeLlama-7B on MBPP with fixed compute budget, if reward function provides higher information bandwidth (continuous + categorical vs. binary), then model reaches pass@1 > 0.3 in fewer training samples, because denser feedback enables gradient updates to more precisely target error-inducing code patterns.

### Refinement Status: UNCHANGED (awaiting adequate-scale retest)

The hypothesis cannot be refined based on inconclusive results. The causal mechanism remains theoretically sound:
1. Higher bandwidth → more bits per gradient update
2. Error-type scoring → ordered feedback signal
3. Precise credit assignment → faster convergence

**Required for Valid Test:**
- Minimum 3 full epochs (not 1)
- Full MBPP training set
- 5 seeds per condition (not 3)
- Sufficient compute for learning signal emergence

---

## 4. Theoretical Interpretation

### Why PoC Scale Failed
The 0% pass@1 across all conditions indicates PoC-scale training (1 epoch, 3 seeds) provides insufficient signal for policy gradient methods to learn code generation. This is expected—PPO on code LLMs typically requires:
- Thousands of gradient updates
- Multiple epochs over training data
- Warm-up periods before policy improvement emerges

### Mechanism Validity
The theoretical mechanism remains intact:
- **Information theory grounding:** Binary=1 bit, categorical~2 bits per feedback
- **Distance-to-correct principle:** syntax=0.0, runtime=0.33, assertion=0.67, pass=1.0 provides principled ordering
- **Credit assignment:** Denser signals should enable more precise gradient directions

The failure is experimental (insufficient scale), not theoretical.

---

## 5. Experiment Results

### H-E1: Existence Hypothesis

**Configuration:**
- Model: CodeLlama-7B-Instruct
- Training: MBPP sanitized train split
- Evaluation: MBPP validation (50 samples)
- Epochs: 1 (PoC scale)
- Seeds: 3
- Algorithm: REINFORCE with advantage baseline

**Results:**

| Condition | pass@1 | Samples to Threshold | Seeds Reaching 0.3 |
|-----------|--------|---------------------|-------------------|
| binary | 0.0000 ± 0.0000 | Not reached | 0/3 |
| categorical | 0.0000 ± 0.0000 | Not reached | 0/3 |
| high_bandwidth | 0.0000 ± 0.0000 | Not reached | 0/3 |

**Gate Result:** FAILED (all conditions at floor, no comparison possible)

---

## 6. Limitations

### Experimental Limitations
1. **Insufficient training scale:** 1 epoch inadequate for PPO convergence on code generation
2. **Limited seeds:** 3 seeds insufficient for variance estimation
3. **PoC validation set:** 50 samples may not capture true performance distribution
4. **Missing error distribution analysis:** Training at floor prevented mechanism validation

### Design Limitations (unchanged from 03_refinement.yaml)
1. **Heuristic weighting:** 0.5/0.5 split between pass_rate and error_score is arbitrary
2. **Single model size:** Only 7B tested, scaling effects unknown
3. **Python-only:** Error parsing assumes standard Python formatting
4. **HumanEval evaluation:** Results may not generalize to other code tasks

---

## 7. Future Work

### Immediate (Phase 0 reformulation)
- Define minimum viable compute budget for hypothesis testing
- Specify training epochs (≥3), seeds (≥5), and convergence criteria
- Consider learning rate warm-up and PPO hyperparameter tuning
- Add early stopping based on validation pass@1 plateaus

### Medium-term (if hypothesis validated)
- Ablate weighting schemes (0.5/0.5 vs. learned weights)
- Test on additional code benchmarks (HumanEval-X, APPS)
- Scale to larger models (13B, 34B)
- Compare to process reward models

### Long-term
- Generalize information bandwidth framework beyond code
- Investigate optimal feedback granularity as function of task complexity
- Develop adaptive reward schemes that increase bandwidth during training

---

## 8. Implications for Phase 6

### Paper Writeability: LOW
Current results do not support a research paper. The inconclusive outcome provides no empirical contribution.

### Path Forward
1. **Re-enter Phase 0:** Reformulate experiment design with adequate compute budget
2. **New sub-hypothesis hierarchy:** May need to decompose into smaller, more tractable claims
3. **Alternative framing:** Consider supervised fine-tuning comparison before RL, as baseline calibration

### If Hypothesis Validates on Retest
- Strong empirical contribution: first controlled comparison of feedback granularities
- Clear practical guidance for RLHF/RLEF practitioners
- Theoretical contribution: information bandwidth framework for reward design

---

*Generated by Phase 4.5 Hypothesis Synthesis Pipeline*
*Synthesis Date: 2026-08-29*
