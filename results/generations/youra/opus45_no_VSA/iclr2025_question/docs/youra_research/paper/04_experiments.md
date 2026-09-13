# 4. Experiments

## 4.1 Implementation

We implement trajectory feature extraction using TransformerLens for hook-based access to intermediate representations. For each prompt-choice pair, we:

1. Run a single forward pass through LLaMA-2-7B
2. Extract hidden states at layers 24-31
3. Project through the unembedding matrix to obtain per-layer logits
4. Compute entropy H_l and answer probability s_l at each layer
5. Aggregate into NTI, CMI, and RCI features

All experiments use float32 precision for entropy computation to avoid numerical underflow. Code artifacts are provided in the supplementary material.

## 4.2 Experiment h-e1: NTI Existence

**Goal**: Validate that NTI alone provides discriminative signal.

**Setup**: 5-fold stratified CV on 4114 prompt-choice pairs. Logistic regression with NTI as the sole feature.

**Metric**: AUROC with threshold > 0.55 (above chance 0.50 with practical margin).

## 4.3 Experiment h-m1: Combined Model

**Goal**: Test whether trajectory features add incremental validity over baseline entropy.

**Setup**: Compare nested models:
- Null model: H_L only (final-layer entropy)
- Full model: H_L + NTI + CMI

**Metric**: AUROC gain ≥ 0.03 and Likelihood Ratio Test p < 0.05.

**Statistical Method**: Per-fold LRT with G statistic = 2(LL_full - LL_null), df=2. Combined p-value via Fisher's method.

## 4.4 Experiment h-m2: Low-Entropy Subset

**Goal**: Test whether trajectory metrics provide signal on "confident but wrong" cases.

**Setup**: Subset samples where H_L < 25th percentile (1029 samples). Evaluate NTI AUROC with bootstrap 95% CI (1000 iterations).

**Success Criterion**: AUROC > 0.55 and CI lower bound > 0.50.

**Rationale**: If NTI adds orthogonal signal to entropy, it should work precisely when entropy is uninformative (low entropy but wrong answer).

## 4.5 Experiment h-m3: RCI Flip Pattern

**Goal**: Test whether top-token competition distinguishes hallucinations.

**Setup**: Count instances where top-1 token changes at least once across layers 24-31. Compute prevalence in hallucinated vs correct responses.

**Success Criterion**: Flip rate ≥ 30% in hallucinations, < 10% in correct responses (separation ≥ 20pp).

**Rationale**: The CLTI hypothesis predicts hallucinations involve competition between plausible alternatives, manifesting as top-token flips.

## 4.6 Computational Cost

| Operation | Time (per sample) |
|-----------|-------------------|
| Forward pass | ~50ms |
| Trajectory feature extraction | ~5ms |
| Total inference | ~55ms |

This compares favorably to semantic entropy (~500ms for 10 samples) and maintains real-time viability.
