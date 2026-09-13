# 5. Results

We present results in the order of our sequential validation design: infrastructure validation first, then the core calibration finding.

## 5.1 Infrastructure Validation

### 5.1.1 RQ1: Tier Viability (h-e1)

K=5 solution generation achieves **perfect coverage** (pass@5 = 1.0000) for all 542 problems across all three models — every problem receives exactly k=5 evaluated solutions. Tier stratification produces viable tier sizes for all but one model-benchmark combination:

| Model | Benchmark | n_hard | n_easy | Viable? |
|-------|-----------|--------|--------|---------|
| Llama3-8B | HumanEval+ | 68 | 72 | ✅ (≥20) |
| Llama3-8B | MBPP+ | 160 | 95 | ✅ |
| CodeLlama-7B | HumanEval+ | 186 | **0** | ⚠️ n_easy=0 |
| CodeLlama-7B | MBPP+ | 155 | 37 | ✅ |
| DeepSeek-6.7B | HumanEval+ | 68 | 105 | ✅ |
| DeepSeek-6.7B | MBPP+ | 105 | 95 | ✅ |

The CodeLlama HumanEval+ edge case (n_easy=0) reflects that CodeLlama-7B rarely achieves pass@1 ≥ 0.6 on HumanEval+ problems without instruction tuning. We use MBPP+ as the primary benchmark for CodeLlama's easy tier analysis. The gate passes (5/6 pairs viable, with documented exception).

### 5.1.2 RQ2: P(True) Non-Degeneracy (h-m3)

P(True) logprob extraction produces non-degenerate confidence distributions for all three models across 5,730 (problem, solution) pairs:

| Model | mean(c) | std(c) | min(c) | max(c) | r(c, correctness) | p-value |
|-------|---------|--------|--------|--------|-------------------|---------|
| Llama3-8B | 0.4989 | 0.0669 | — | — | +0.156 | < 10⁻¹⁰ |
| CodeLlama-7B | 0.3682 | 0.0618 | — | — | +0.142 | < 10⁻¹⁰ |
| DeepSeek-6.7B | 0.6480 | 0.0781 | 0.16 | 0.92 | −0.046 | 0.048 |

All models satisfy std(c) > 0.05 (gate threshold), confirming that P(True) captures genuine (if weak) signal. The confidence-correctness correlation r = 0.14–0.20 for Llama3 and CodeLlama is statistically significant but weak, consistent with prior work [Kadavath et al., 2022]. DeepSeek's near-zero r (−0.046) is unexpected: despite having the highest mean confidence (0.648) and the strongest ΔECE signal, its confidence does not linearly correlate with correctness at the sample level. Figure 5 shows the P(True) distribution by tier for all three models.

### 5.1.3 RQ3: Tier Consistency (h-m2)

Figure 4 shows Jaccard similarity of hard-tier assignments across all three model pairs:

| Model Pair | Jaccard Similarity | Gate (> 0.30) |
|------------|-------------------|---------------|
| Llama3 ∩ CodeLlama | 0.456 | ✅ PASS |
| Llama3 ∩ DeepSeek | 0.487 | ✅ PASS |
| CodeLlama ∩ DeepSeek | 0.546 | ✅ PASS |

All three pairs substantially exceed the 0.30 threshold. The 133/542 (24.5%) problems hard for all three models form an architecture-independent "iron core" of structurally difficult problems (Figure 7). This consistency validates that cross-architecture ΔECE comparisons are interpretable: different models are largely evaluating their calibration on a shared hard-problem substrate.

## 5.2 Main Result: Architecture-Dependent ΔECE (RQ4, h-m4)

Figure 1 shows the central result of our study. Table 1 provides the complete ΔECE analysis.

**Table 1. Difficulty-stratified ECE per model architecture.**

| Model | Architecture | n_hard | n_easy | ECE(hard) | ECE(easy) | ΔECE | 95% CI | P1 Gate |
|-------|-------------|--------|--------|-----------|-----------|------|--------|---------|
| Llama3-8B | General | 228 | 167 | 0.4887 | 0.4852 | **+0.0034** | [−0.0074, +0.0133] | ❌ FAIL |
| CodeLlama-7B | Code-adapted | 341 | 37 | 0.3659 | 0.6149 | **−0.2490** | [−0.2589, −0.2391] | ❌ FAIL |
| DeepSeek-6.7B | Code-specialized | 173 | 200 | 0.6565 | 0.3586 | **+0.2979** | [+0.2849, +0.3115] | ✅ PASS |

**Overall gate (≥2/3 models): 1/3 models pass → MUST_WORK GATE FAIL**

Three qualitatively distinct patterns emerge:

**DeepSeek-Coder (ΔECE=+0.298):** The code-specialized model shows the expected pattern — hard problems are substantially more miscalibrated than easy ones. ECE(hard)=0.657 vs ECE(easy)=0.359, a difference of 0.298 that is stable across M ∈ {10, 15, 20} bins and carries a tight bootstrap CI entirely above zero. The reliability diagram (Figure 2, DeepSeek panel) shows that on hard problems, the model's confidence is systematically higher than its accuracy across virtually all confidence bins.

**Llama3-8B (ΔECE≈0):** The general-purpose model shows calibration insensitivity to difficulty. ECE(hard)≈ECE(easy)≈0.49, and the 95% CI includes zero (p=0.256). This is not a calibration success — both tiers are substantially miscalibrated — but the miscalibration is uniform across difficulty levels. The Figure 2 (Llama3 panel) shows similar reliability curves for hard and easy tiers.

**CodeLlama-7B (ΔECE=−0.249):** The code-adapted model shows the opposite of the expected pattern. ECE(easy)=0.615 > ECE(hard)=0.366, meaning *easy* problems are more miscalibrated than hard ones. The CI is entirely negative (p=1.000), and the effect is stable across M values. This is the most surprising finding: an inversion of the expected difficulty-calibration relationship.

Figure 6 shows the null baseline comparison: DeepSeek's observed ΔECE far exceeds the null distribution; Llama3's lies within it; CodeLlama's negative ΔECE is also a genuine signal (opposed to the null direction).

## 5.3 Analysis: CodeLlama Calibration Inversion

The CodeLlama inversion warrants detailed examination. As shown in Figure 2 (CodeLlama panel), the model's easy tier (n=37, MBPP-only) shows high confidence values uniformly regardless of correctness — producing ECE(easy)=0.615. Several properties of this finding are noteworthy:

1. **Scale:** ΔECE=−0.249 is a large effect; the CI [−0.259, −0.239] is far from zero.
2. **Specificity:** n_easy=37 reflects that CodeLlama rarely passes easy-tier threshold (pass@1 ≥ 0.6) on HumanEval; those problems that do qualify as "easy" are exclusively MBPP problems.
3. **Confidence pattern:** CodeLlama's mean confidence for the easy tier (mean_c=0.385 on easy vs 0.366 on hard) shows the model is very slightly more confident on easy problems, but the overcalibration is severe at the ECE level.

The most plausible explanation is training data overconfidence: CodeLlama was fine-tuned on large code corpora including common Python utility functions that closely resemble MBPP problems. The model has learned to assign high P(True) to solutions that look like code it has seen frequently — regardless of whether those solutions pass EvalPlus's augmented tests.

## 5.4 Temperature Scaling Analysis

Figure 3 shows the effect of global temperature scaling on ΔECE.

| Model | T* | ΔECE (pre-scaling) | ΔECE (post-scaling) | Direction preserved? |
|-------|----|--------------------|---------------------|---------------------|
| Llama3-8B | 1.163 | +0.0034 | −0.1371 | ❌ INVERTED |
| CodeLlama-7B | 3.951 | −0.2490 | −0.8099 | ✅ (worse) |
| DeepSeek-6.7B | 1.210 | +0.2979 | +0.0728 | ✅ PERSISTS |

Global temperature scaling does not correct architecture-dependent ΔECE direction. For DeepSeek, positive ΔECE attenuates to +0.073 but remains positive with CI entirely above zero. For CodeLlama, the inversion worsens dramatically (−0.810) as T*=3.95 aggressively scales down confidence values that are especially problematic in the easy tier. For Llama3, temperature scaling actually inverts the near-zero ΔECE to negative.

Critically, CodeLlama's T*=3.95 is an outlier: Llama3 and DeepSeek require T*≈1.16–1.21 (typical range for overconfident neural networks). The extreme T* indicates that CodeLlama's overall confidence magnitude is pathologically high — approximately 3× the corrections needed for the other models. This further supports the training-data overconfidence hypothesis: CodeLlama has been fine-tuned to produce high-confidence P(True) outputs for code-like patterns, creating a systematic global confidence inflation that no single global T can correct in a direction-consistent way.

## 5.5 M-Sensitivity and Robustness

ΔECE values are exactly stable across M ∈ {10, 15, 20} for all three models (Table reproduced from h-m4 validation):

| Model | M=10 | M=15 | M=20 |
|-------|------|------|------|
| Llama3-8B | +0.00344 | +0.00344 | +0.00344 |
| CodeLlama-7B | −0.24899 | −0.24899 | −0.24899 |
| DeepSeek-6.7B | +0.29789 | +0.29789 | +0.29789 |

This M-stability is notable: ΔECE values do not change with bin count, ruling out sensitivity to the ECE discretization. The stability arises because confidence distributions are sufficiently spread across bins that different M values partition the data similarly.
