# Results

## E1: Orthogonality Validation

The collaboration score exhibits near-zero correlation with preference labels, confirming orthogonality.

| Metric | Value |
|--------|-------|
| Pearson r | −0.026 |
| p-value | 0.250 |
| Chosen Mean Score | 0.153 (±0.223) |
| Rejected Mean Score | 0.164 (±0.220) |

**Interpretation:** |r| = 0.026 ≪ 0.7 threshold. The non-significant p-value confirms the null hypothesis of no linear relationship—this is the desired outcome. The collaboration score captures information independent of which response humans preferred.

Notably, rejected responses have marginally higher mean scores (0.164 vs 0.153), but the difference is not significant. This suggests collaboration patterns are orthogonal to, not inversely related to, preference.

**Gate: PASSED.** The agency signal provides non-redundant information for BiDPO training.

## E2: Training Stability

BiDPO training completes without numerical instabilities. Loss decreases over 250 steps.

| Step | DPO Loss | Agency Loss | Total Loss |
|------|----------|-------------|------------|
| 100 | 0.679 | 0.500 | 0.929 |
| 200 | 0.664 | 0.508 | 0.918 |

**Key Metrics:**
- Loss decrease: 0.929 → 0.918 (−1.2%)
- NaN/Inf count: 0
- Gradient norm: 348–366 (stable with clipping)
- Learning rate: cosine decay from 3.75×10⁻⁷ to 5.8×10⁻⁸

**Interpretation:** The auxiliary agency objective integrates stably with DPO. No numerical instabilities occurred. Loss decreased monotonically after warmup, indicating the model learns from both objectives.

**Gate: PASSED.** BiDPO training is stable at PoC scale.

## E3: Generation Transfer (Negative Result)

BiDPO-trained models show only marginal, non-significant improvement in collaboration scores compared to DPO.

| Metric | DPO | BiDPO | Difference |
|--------|-----|-------|------------|
| Mean Score | 0.3728 | 0.3782 | +0.0054 (+0.54%) |
| Std Dev | 0.3294 | 0.3333 | — |
| N Samples | 500 | 500 | — |

**Statistical Tests:**
- t-statistic: 0.684
- p-value (one-sided): 0.247
- Cohen's d: 0.016

**Interpretation:** BiDPO produces marginally higher collaboration scores (+0.54%), but:
1. The difference is not statistically significant (p = 0.247 ≫ 0.05)
2. The effect size is negligible (d = 0.016 ≪ 0.2 threshold)

The distributions are nearly identical (see Figure 3b). Training-time gradient pressure from L_agency did not translate to measurable behavioral change at inference.

**Gate: FAILED.** The generation transfer hypothesis is not supported at PoC scale.

## Summary of Gate Results

| Experiment | Hypothesis | Gate Type | Result |
|------------|------------|-----------|--------|
| E1 | Orthogonality | MUST_WORK | **PASSED** |
| E2 | Training Stability | MUST_WORK | **PASSED** |
| E3 | Generation Transfer | SHOULD_WORK | **FAILED** |
| E4 | MT-Bench/TruthfulQA | SHOULD_WORK | NOT EXECUTED |

Two of three executed experiments passed, validating the BiDPO mechanism (orthogonal signal, stable training). The critical negative result is E3: training-time signals do not transfer to generation at PoC scale.
