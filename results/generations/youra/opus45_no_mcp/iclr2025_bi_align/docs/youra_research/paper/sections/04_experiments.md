# Experimental Setup

## Experimental Questions

Our experiments address five questions corresponding to the mechanism chain:

1. **Existence (H-E1):** Do calibration inversion patterns cluster systematically across RLHF models?
2. **Reward Conflation (H-M1):** Do RLHF models show similar confidence on correctness vs user-modeling tasks?
3. **Annotator Conflation (H-M2):** Do annotators provide indistinguishable ratings for both task types?
4. **Representation Conflation (H-M3):** Do model hidden states fail to separate task types?
5. **Feature Correlation (H-M4):** Do bidirectional features correlate with calibration inversion clusters?

## Datasets

We combine three standard RLHF benchmarks:

| Dataset | Tasks | Purpose | Source |
|---------|-------|---------|--------|
| TruthfulQA | 817 | Factual accuracy | Lin et al. 2021 |
| ETHICS (justice) | ~500 | Moral reasoning | Hendrycks et al. 2021 |
| HH-RLHF (single-turn) | ~200 | Helpfulness/harmlessness | Bai et al. 2022 |
| **Total** | **2,212** | Combined RLHF evaluation | |

**Dataset rationale:** These benchmarks have clear correctness labels enabling calibration computation. They represent diverse RLHF evaluation dimensions (truthfulness, ethics, helpfulness).

## Models

We evaluate three open RLHF models with accessible logprobs:

| Model | Parameters | Training | Source |
|-------|------------|----------|--------|
| Llama-2-7B-Chat | 7B | RLHF | Meta |
| Llama-2-13B-Chat | 13B | RLHF | Meta |
| Mistral-7B-Instruct | 7B | RLHF | Mistral AI |

**Model rationale:** Open models provide logprob access required for calibration computation. Multiple models from different organizations test cross-model generalization.

## Baseline Comparisons

For H-M4 (feature correlation), we compare calibration-based clustering against:

1. **Random stratification:** Randomly assign tasks to clusters
2. **Topic-based stratification:** Group by benchmark-provided topics

These baselines test whether calibration clustering reveals structure beyond random chance or topic assignment.

## Evaluation Metrics

### Clustering Quality (H-E1)
- **Silhouette score:** Measures cluster separation; threshold > 0.3
- **Optimal k:** Number of clusters maximizing silhouette

### Mechanism Verification (H-M1, H-M2, H-M3)
- **Distribution overlap:** Kernel density estimation overlap between Type A/B confidence distributions
- **Mean difference:** Absolute difference in mean confidence
- **Rate difference:** Difference in high-confidence rating frequency
- **Separation score:** Centroid distance in hidden state space
- **Probe accuracy:** Linear probe task-type classification accuracy

### Feature Correlation (H-M4)
- **Point-biserial r:** Correlation between cluster membership (binary) and feature score (continuous)
- **Cohen's d:** Effect size between clusters on feature score
- **Partial r:** Correlation after controlling for confounds (length, topic, format, difficulty)

## Implementation Details

**Inference:**
- Batch size: 8-16 (model-dependent)
- Precision: float16
- Device: Auto-mapped to available GPUs

**Clustering:**
- Algorithm: K-means
- k range: {2, 3, 4, 5}
- Initialization: k-means++ with n_init=10
- Random seed: 42

**Representation analysis:**
- Layer: Final hidden layer
- Dimensionality: Model-specific (4096 for Llama, 4096 for Mistral)
- Probe: Linear classifier with L2 regularization

## Success Criteria

| Hypothesis | Gate Type | Primary Metric | Threshold | Failure Action |
|------------|-----------|----------------|-----------|----------------|
| H-E1 | MUST_WORK | Silhouette | > 0.3 | ABANDON |
| H-M1 | MUST_WORK | Overlap OR mean_diff | > 0.7 OR < 0.1 | PIVOT |
| H-M2 | SHOULD_WORK | rate_diff | < 0.15 | EXPLORE |
| H-M3 | SHOULD_WORK | Separation | < 0.1 | EXPLORE |
| H-M4 | SHOULD_WORK | r, d, partial_r | > 0.4, > 0.3, > 0.3 | ABANDON |

MUST_WORK gates block further mechanism investigation if failed. SHOULD_WORK gates allow exploration of alternative explanations.
