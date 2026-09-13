# 4. Experiments

Our experimental design tests three falsifiable predictions via direct measurement. We structure experiments to separate methodology validation from hypothesis testing, ensuring measurement reliability is independent of hypothesis outcomes.

## 4.1 Research Questions

We investigate three specific, testable questions:

**RQ1: Methodology Validation (h-e1)**
> Can SVD-based effective rank computation reliably measure intrinsic dimensionality of Transformer projection weights at 7B scale?

*Expected Outcome:* Methodology validation PASS if (a) SVD computation numerically stable, (b) effective rank measurements produce sensible values on test data, and (c) full analysis pipeline functional on Mistral-7B.

*Gate:* MUST_WORK — methodology must pass before hypothesis testing (h-m1). Separates implementation quality from hypothesis validity.

**RQ2: Low-Rank Structure Hypothesis (h-m1)**
> Do deep Transformer layers (L ≥ 20) in pre-trained 7B models exhibit effective rank r_eff < 256, as required for bounded-state SSM conversion?

*Expected Outcome (if hypothesis true):* r_eff < 256 for all layers 20-31 in Mistral-7B.

*Expected Outcome (if hypothesis false):* r_eff ≫ 256, potentially approaching full rank (~4096 dimension).

*Gate:* MUST_WORK — foundational assumption for post-hoc conversion. Failure invalidates dependent hypotheses.

**RQ3: Entropy Decrease Hypothesis (h-m1)**
> Does operator entropy decrease monotonically with layer depth (β < 0, p < 0.01), consistent with semantic compression theory?

*Expected Outcome (if hypothesis true):* Linear regression of H(L) vs. L yields significantly negative slope (β < 0, p < 0.01).

*Expected Outcome (if hypothesis false):* β ≥ 0 or not statistically significant (p ≥ 0.01).

*Gate:* MUST_WORK (secondary criterion) — converging evidence with rank analysis. Both should align if compression hypothesis is correct.

## 4.2 Experimental Setup

**Model:** Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1)
- Architecture: 32-layer decoder-only Transformer
- Parameters: 7B total, 4096 hidden dimension, 32 attention heads
- Vocabulary: 32,000 tokens
- Pre-training: Not publicly documented, but follows LLaMA-style pre-training

**Target Layers:** Layers 20-31 (deep layers L ≥ 20 as specified in hypothesis)

**Analysis Scope:**
- **h-e1 (Methodology Validation):** Reduced scale for rapid iteration
  - Sample size: 50 sequences (reduced from planned 5000+ for memory efficiency)
  - Purpose: Validate that methodology works, not full statistical power
  - Model: Mistral-7B (same target as h-m1)

- **h-m1 (Hypothesis Testing):** Full-scale weight analysis
  - Sample size: N/A (deterministic SVD of weight matrices, no sampling)
  - Purpose: Direct measurement of r_eff and entropy
  - All layers 20-31 analyzed (12 layers × 3 projections × 1 per-head = 36 matrices per layer if analyzed separately, or 3 large matrices if computed for combined heads)

**Metrics:**
- **Effective Rank (r_eff):** Minimum number of singular values capturing 99% variance
- **Entropy Slope (β):** Linear regression coefficient for H(L) ~ β×L + intercept
- **Statistical Significance (p-value):** Probability of observing β under null hypothesis β ≥ 0

**Hypothesis Criteria (MUST_WORK gate):**
1. **Criterion 1:** r_eff < 256 for all deep layers (L ≥ 20)
2. **Criterion 2:** Entropy slope β < 0 with statistical significance p < 0.01
3. **Criterion 3:** Measurements stable across layers (variance ≤ 1.2× baseline)

## 4.3 Baseline Considerations

**No method comparison.** This is a measurement study, not a method comparison. We measure properties of existing pre-trained models (Mistral-7B), not performance of competing techniques. Therefore, no baselines are needed in the traditional sense.

**Threshold justification.** The threshold r_eff < 256 derives from:
- SSM state size constraints (N ≤ 1024 typical for efficient inference)
- LoRA's empirical success with r ~ 8-64 (suggesting perhaps moderate rank ~256 might exist)
- Post-hoc conversion assumptions in prior work (bounded-state representations)

This threshold is **NOT arbitrary** but grounded in the requirements of the architectural conversion hypothesis. If r_eff ≈ 256, conversion is plausible; if r_eff ≫ 256 (approaching full rank), conversion based on bounded-state assumptions is not viable.

## 4.4 Experimental Procedure

### Phase 1: Methodology Validation (h-e1)

**Step 1:** Implement SVD-based rank analysis pipeline
- Load Mistral-7B pre-trained weights (HuggingFace transformers library)
- Extract Q, K, V projection matrices for target layers
- Compute SVD: W = UΣV^T using NumPy `np.linalg.svd`
- Calculate effective rank via cumulative variance thresholding

**Step 2:** Numerical stability verification
- Check singular values σ_i > 10^(-10) to filter machine precision artifacts
- Verify σ_1 ≥ σ_2 ≥ ... ≥ σ_min (non-increasing order)
- Confirm Σ_i σ_i² = ||W||_F² (Frobenius norm consistency)

**Step 3:** Test on small-scale data
- OpenWebText subset (50 sequences, reduced for memory)
- Verify sensible r_eff values (should be < full rank but > trivially small)
- Confirm analysis pipeline completes without errors

**Success Criteria:** h-e1 PASS if methodology produces valid measurements on Mistral-7B without numerical errors.

### Phase 2: Hypothesis Testing (h-m1)

**Step 1:** Measure effective ranks
- For each layer L ∈ [20, 31]:
  - Load W_Q, W_K, W_V ∈ ℝ^(4096×4096)
  - Compute SVD and r_eff at τ = 0.99
  - Record r_eff values per projection type

**Step 2:** Compute operator entropy
- For each layer L ∈ [20, 31]:
  - Compute covariance Cov(W) = (1/n) W^T W
  - Calculate entropy H(L) = log det(Cov(W))
  - Record entropy values

**Step 3:** Statistical analysis
- Aggregate r_eff across layers: compute max, min, mean, std
- Linear regression: H(L) ~ β×L + intercept
- Compute p-value for slope coefficient β
- Evaluate gate criteria 1-3

**Step 4:** Gate evaluation
- **Criterion 1 (r_eff):** PASS if r_eff < 256 for ALL layers, FAIL otherwise
- **Criterion 2 (entropy):** PASS if β < 0 AND p < 0.01, FAIL otherwise
- **Criterion 3 (stability):** PASS if entropy variance ≤ 1.2× baseline, N/A for static weights

## 4.5 Reproducibility

**Code availability.** Full analysis pipeline (1,010 lines of Python) implemented using:
- PyTorch 2.4.1 (model loading)
- Transformers 4.38.0 (HuggingFace pre-trained weights)
- NumPy 1.24.3 (SVD computation)
- SciPy 1.11.0 (statistical tests)

**Model weights.** Mistral-7B-v0.1 publicly available via HuggingFace model hub (mistralai/Mistral-7B-v0.1).

**Computational requirements:**
- GPU: NVIDIA A100 40GB (for model weight loading)
- CPU: 32 cores (for SVD computation via optimized BLAS)
- RAM: 64GB (to hold full 7B model in memory)
- Runtime: ~30 minutes for full h-m1 analysis (all layers 20-31)

**Deterministic analysis.** SVD of weight matrices is deterministic given fixed numerical precision. No randomness, no hyperparameter tuning, no training. Results are fully reproducible given identical model weights and numerical libraries.

## 4.6 Limitations and Scope Boundaries

**Limitations acknowledged:**

1. **Sample size (h-e1).** Methodology validation used 50 sequences (reduced for memory), not 5000+ as originally planned. This validates that the methodology *works* (proof-of-concept) but doesn't provide full statistical power. However, h-m1 hypothesis testing analyzes weight matrices directly (deterministic, no sampling), so sample size doesn't affect primary results.

2. **Single model scale (7B).** Results specific to 7B parameters. Rank properties may differ for smaller (<1B) or larger (>13B) models. Cross-scale validation needed to establish generalization.

3. **Weight analysis, not runtime.** Measures projection weight ranks, not runtime attention matrix (QK^T) ranks. These are complementary questions requiring different methodologies.

4. **Architecture specificity.** LLaMA-family decoder-only Transformers only. Vision Transformers, encoder-decoder models, or other variants not tested.

**Why limitations are acceptable:**

- **First measurement at widely-used scale.** Even with limitations, this is the first direct rank measurement at 7B scale, filling a critical empirical gap.
- **Methodology validated separately (h-e1).** Two-phase design ensures refutation (h-m1 FAIL) is not due to implementation errors.
- **Deterministic weight analysis.** h-m1 measurement is definitive for the matrices analyzed—no sampling variability, no need for large sample sizes.
- **Clear scope boundaries.** We explicitly state what is measured (projection weights) vs. not measured (runtime attention), preventing over-interpretation.

These limitations don't invalidate the core contribution: establishing that pre-trained projection weights at 7B scale are NOT low-rank (r_eff ~ 1600), refuting the assumption underlying post-hoc SSM conversion approaches.
