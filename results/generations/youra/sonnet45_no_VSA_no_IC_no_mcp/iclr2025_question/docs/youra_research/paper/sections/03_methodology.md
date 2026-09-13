# 3. Methodology

Building on our observation that computational overhead scales predictably from micro-pilot to full dataset, we design Pilot-Driven Viability Gates as an incremental empirical validation framework. The framework combines three mechanisms: (M1) linear overhead extrapolation from micro-pilot measurements, (M2) Bayesian posterior refinement through sequential observations, and (M3) threshold-based viability classification. We describe each mechanism's theoretical foundation, implementation details, and design rationale.

## 3.1 Framework Overview

The framework structures hypothesis validation as a three-stage process:

**Gate 1 (Micro-Pilot)**: Measure overhead O₁₀ on 10 samples. Extrapolate to full-scale via O_pred = k × O₁₀ where k is the scaling factor. Compare O_pred to user-specified threshold T. If O_pred > T, stop (hypothesis non-viable). If O_pred ≤ T, continue to Gate 2.

**Gate 2 (Mid-Scale)**: Measure overhead O₁₀₀ on 100 samples. Apply Bayesian update combining Gate 1 prior P(O_full | O₁₀) with Gate 2 likelihood P(O₁₀₀ | O_full) to compute posterior P(O_full | O₁₀, O₁₀₀). Repeat threshold comparison. If posterior mean > T, stop. Otherwise, continue to Gate 3.

**Gate 3 (Full-Scale)**: Measure ground truth overhead O_full on complete dataset. Validate viability decision and update scaling factor k for future hypotheses.

**Rationale**: The staged design enables fail-fast at minimal cost. Gate 1 requires <1 hour (10 samples) vs days for full implementation. Early stops avoid wasted effort while incremental refinement (Gate 2) reduces false negatives.

## 3.2 Mechanism M1: Linear Overhead Scaling

**Theoretical Basis**: Many ML operations exhibit linear or near-linear scaling with sample count. Matrix multiplication, attention mechanisms (O(n²) in sequence length but O(n) in batch size), and gradient computations scale predictably. We model this as:

$$O_{full} = k \times O_{10} + \epsilon$$

where k is the scaling factor (ratio of full dataset size to micro-pilot size) and ε represents measurement noise.

**Implementation**: At Gate 1, measure wall-clock time for hypothesis implementation on 10 randomly sampled datapoints. Normalize by baseline (vanilla model without hypothesis) to compute overhead percentage. Fit linear regression across observed (sample size, overhead) pairs to estimate k. For new hypotheses, predict O_full = k × O₁₀.

**Design Decision**: We use Pearson correlation r as a validation metric. The framework assumes r ≥ 0.7 between O₁₀ and O_full across a corpus of past hypotheses. If r < 0.7, linear extrapolation breaks down and the framework requires recalibration (e.g., per-hypothesis-type scaling factors or non-linear models).

**Complexity Analysis**: Gate 1 overhead measurement requires O(10 × hypothesis_complexity) time. For typical ML operations (forward pass, gradient computation), this translates to seconds to minutes rather than hours required for full-scale experiments.

## 3.3 Mechanism M2: Bayesian Posterior Refinement

**Theoretical Basis**: Bayesian inference reduces prediction uncertainty by combining prior beliefs with new evidence. We model overhead as a Gaussian random variable: O_full ~ N(μ, σ²). Gate 1 provides prior: μ_prior = k × O₁₀, σ²_prior = estimated from historical variance. Gate 2 provides likelihood: μ_likelihood = k × O₁₀₀, σ²_likelihood = measurement uncertainty. The posterior combines both:

$$\frac{1}{\sigma^2_{post}} = \frac{1}{\sigma^2_{prior}} + \frac{1}{\sigma^2_{likelihood}}$$

$$\mu_{post} = \sigma^2_{post} \left( \frac{\mu_{prior}}{\sigma^2_{prior}} + \frac{\mu_{likelihood}}{\sigma^2_{likelihood}} \right)$$

**Implementation**: We use scipy.stats Gaussian conjugate update. Prior variance σ²_prior estimated from residuals in linear regression fit (M1). Likelihood variance σ²_likelihood estimated from measurement stability across 3 repeated runs at 100-sample scale.

**Design Decision**: Bayesian updates are optional (SHOULD_WORK gate). If Gate 2 data is unavailable or error reduction is minimal (<20%), the framework degrades gracefully to Gate 1-only prediction. This design prioritizes practical deployment over theoretical completeness.

## 3.4 Mechanism M3: Viability Classification

**Theoretical Basis**: Viability is a binary decision: hypothesis overhead O_full either exceeds threshold T (non-viable) or remains within bounds (viable). We classify based on posterior mean:

$$\text{viable} = \begin{cases} 
\text{True} & \text{if } \mu_{post} \leq T \\
\text{False} & \text{if } \mu_{post} > T
\end{cases}$$

Confidence intervals provide uncertainty quantification: if 95% confidence interval [μ - 1.96σ, μ + 1.96σ] straddles T, the decision is borderline and warrants Gate 2 refinement.

**Implementation**: Gate 1 predicts viability using O_pred = k × O₁₀. For borderline cases (within 10% of threshold), we recommend proceeding to Gate 2 for refined prediction. High-confidence cases (O_pred < 0.9T or O_pred > 1.1T) can stop/continue immediately.

**Design Decision**: We prioritize recall over precision—minimizing false negatives (viable hypotheses incorrectly stopped) at the cost of occasional false positives (non-viable hypotheses continuing to Gate 2). Rationale: A viable hypothesis stopped at Gate 1 is a missed opportunity; a non-viable hypothesis caught at Gate 2 wastes only 1 hour rather than days.

## 3.5 Scaling Factor Calibration

The scaling factor k depends on hypothesis type and dataset characteristics. We consider three calibration strategies:

**Global k (simplest)**: Use single k across all hypotheses. Our validation tests this approach with synthetic data.

**Type-specific k (moderate complexity)**: Learn separate k_attention, k_gradient, k_regularization factors. Requires stratified historical corpus.

**Per-hypothesis k (most accurate, least practical)**: Estimate k from micro-pilot + 100-sample pair for each new hypothesis. Requires 100-sample investment before viability decision.

Our validation uses global k. Future work (FD5) explores whether type-specific calibration improves accuracy when scaling variance (CV) exceeds 30% within types.

## 3.6 Algorithm Summary

```
Input: Hypothesis H, threshold T, micro-pilot size n_micro=10
Output: Viability decision (STOP / CONTINUE / CONTINUE_TO_GATE2)

# Gate 1: Micro-Pilot
O_10 = measure_overhead(H, n_micro)
O_pred = k × O_10
if O_pred > 1.1 × T:
    return STOP  # High confidence non-viable
if O_pred < 0.9 × T:
    return CONTINUE  # High confidence viable
return CONTINUE_TO_GATE2  # Borderline case

# Gate 2: Bayesian Update (if reached)
O_100 = measure_overhead(H, n_mid=100)
μ_prior, σ²_prior = k × O_10, estimate_variance(history)
μ_likelihood, σ²_likelihood = k × O_100, measurement_noise
μ_post, σ²_post = bayesian_update(μ_prior, σ²_prior, μ_likelihood, σ²_likelihood)
if μ_post > T:
    return STOP
return CONTINUE  # Proceed to Gate 3 (full implementation)
```

This methodology provides a systematic protocol for early viability assessment, addressing the gap identified in Section 2 where ablation studies test variations but lack formalized early-stop criteria. The framework's empirical foundation (M1 scaling measurement) captures constant factors missed by Big-O analysis, while Bayesian refinement (M2) quantifies prediction uncertainty and enables incremental decision-making.
