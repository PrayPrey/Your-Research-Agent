# Reflection Report: h-m4

**Generated:** 2026-03-18T17:10:00+00:00
**Hypothesis ID:** h-m4
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0
**Reflection Type:** must_work_fail

---

## Summary

h-m4 tested whether DELTA_ECE = ECE(hard) - ECE(easy) >= 0.03 (with bootstrap 95% CI excluding zero) in >=2/3 model families, using M=15-bin ECE computation per difficulty tier using P(True) confidence. The gate FAILED: only 1/3 models (deepseek_6.7b) passed P1.

---

## Experiment Results

| Model | DELTA_ECE | CI Lower | CI Upper | Gate P1 |
|-------|-----------|----------|----------|---------|
| llama3_8b | 0.00344 | -0.00738 | 0.01329 | ❌ FAIL |
| codellama_7b | -0.24899 | -0.25886 | -0.23912 | ❌ FAIL |
| deepseek_6.7b | 0.29790 | 0.28490 | 0.31150 | ✅ PASS |

**Required:** >=2/3 models pass P1 (DELTA_ECE >= 0.03, CI excluding zero)
**Achieved:** 1/3 models pass

---

## Root Cause Analysis

### 1. CodeLlama Anomaly (Critical Failure)
CodeLlama shows **inverted** DELTA_ECE = -0.249, meaning ECE(easy) >> ECE(hard). This is the opposite direction from the hypothesis. The confidence interval [-0.259, -0.239] entirely excludes zero — this is not noise but a systematic inversion. CodeLlama's P(True) confidence signals appear to be better calibrated for "hard" problems (pass@1 ≈ 0) than for "easy" problems.

**Root cause hypothesis:** CodeLlama-7b-hf has degenerate easy-tier behavior — it barely has any easy problems (n_easy=0 on HumanEval, only n=37 on MBPP), forcing it into a regime where calibration statistics are unreliable or systematically different.

### 2. LLaMA3 Near-Zero Effect
LLaMA3 shows DELTA_ECE = 0.0034 with CI [-0.0074, 0.0133] — essentially zero effect. The CI includes zero, indicating no systematic difference in calibration between difficulty tiers for this model.

**Root cause hypothesis:** LLaMA3's P(True) confidence scores may uniformly miscalibrate across all tiers, with no difficulty-dependent structure. The model may use the same calibration "strategy" regardless of problem difficulty.

### 3. DeepSeek Success Does Not Save the Hypothesis
DeepSeek_6.7b shows a strong, consistent DELTA_ECE = 0.2979 (CI far above zero), confirming the mechanism works for at least one model family. However, 1/3 is insufficient for the MUST_WORK gate.

---

## Structured Analysis

### What Worked
- DeepSeek-Coder shows the predicted effect (DELTA_ECE = 0.298, highly significant)
- Bootstrap confidence intervals are tight (±0.01 to ±0.02 range)
- Temperature scaling infrastructure works (T-fitting on 20% holdout)
- ECE computation and tier assignment machinery is correct and validated

### What Failed
- Hypothesis assumes universal applicability across all LLM families — this is false
- CodeLlama's easy-tier sample size is too small (n=37 on MBPP only) for reliable ECE
- The effect direction is model-family-dependent, not universal
- Global temperature scaling cannot fix difficulty-conditioned miscalibration (as predicted)

### Key Insight
The P(True) ECE stratification effect is **model-family dependent**, not universal. DeepSeek-Coder shows the expected pattern strongly; CodeLlama shows the opposite; LLaMA3 shows no effect. This suggests the phenomenon is tied to specific training data / objective characteristics of each model family, not a universal property of LLM calibration.

---

## Decision Rationale

**Outcome: ROUTED_TO_PHASE_0**

This is a MUST_WORK FAIL (gate_result == "FAIL"). Per the routing rules:
- FAIL = complete failure of the primary prediction across the model ensemble
- The methodology does NOT work at all for 2/3 models
- CodeLlama's inversion reveals a **fundamental flaw** in the hypothesis's universality assumption
- This is not a fixable implementation issue — the underlying phenomenon does not hold universally

A SELF_MODIFY route would require evidence that parameter changes could fix CodeLlama's inverted behavior. Given that:
1. The inversion is statistically significant and consistent
2. The easy-tier sample size issue for CodeLlama is a data constraint, not an algorithmic one
3. No parameter adjustment to ECE computation can reverse the direction of the effect

→ Route to Phase 0 for new hypothesis generation.

---

## Lessons Learned for Phase 0

1. **Model-universality assumption is risky:** Never assume a calibration phenomenon holds across all LLM families without model-specific analysis
2. **Degenerate tier assignments invalidate ECE:** CodeLlama has n_easy=0 on HumanEval — models with extreme pass@1 distributions need separate handling
3. **DeepSeek finding is valuable:** The strong DELTA_ECE=0.298 for DeepSeek suggests the phenomenon is real for capable code models; a model-selective hypothesis may succeed
4. **P(True) confidence works:** The confidence elicitation mechanism (h-m3) is validated and reusable
5. **Consider model-conditional hypotheses:** Future hypotheses should explicitly condition on model capability (e.g., "for models with pass@1 > 0.3 on easy tier...")

---

## Deferred Archon Operations

- **Route:** Phase 0
- **Reason:** MUST_WORK FAIL — methodology fails for 2/3 model families
- **Dependents:** None (h-m4 is the terminal hypothesis in the chain)
- **Archon task:** `c887b35f-26fc-4f84-a451-4a6af6e4c705` — to be updated to FAILED/done

---

*Reflection completed: 2026-03-18T17:10:00+00:00*
