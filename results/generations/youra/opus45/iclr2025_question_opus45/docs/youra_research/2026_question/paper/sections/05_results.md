# Results

Our experiments reveal a fundamental failure: both SEP and SEDP perform no better than random guessing on SE prediction. This section presents the evidence supporting this conclusion.

## Main Results

Table 1 presents our core findings on the TruthfulQA test set.

| Method | Spearman ρ | p-value | AUROC |
|--------|------------|---------|-------|
| SEP (baseline) | 0.0835 | 0.288 | 0.5214 |
| SEDP (proposed) | 0.0843 | 0.283 | 0.5219 |
| SEDP - SEP | +0.0009 | — | +0.0004 |
| **MUST_WORK threshold** | **≥ 0.30** | **< 0.05** | — |
| Random baseline | 0.00 | — | 0.50 |

**Key Observations**:

1. **SEDP fails the MUST_WORK gate by 72%**: The achieved correlation ρ = 0.0843 falls far short of the required threshold ρ ≥ 0.3. This is not a marginal miss—it represents near-complete failure to capture SE signal.

2. **Correlation is not statistically significant**: With p = 0.283, we cannot reject the null hypothesis that the true correlation is zero. The observed ρ = 0.0843 is indistinguishable from random noise.

3. **AUROC is essentially random**: Both methods achieve AUROC ≈ 0.52, barely above the random baseline of 0.50. For practical hallucination detection, these probes provide no useful signal.

4. **Similarity augmentation provides negligible benefit**: SEDP outperforms SEP by only +0.0009 in correlation and +0.0004 in AUROC. While the effect direction is positive (as hypothesized), the magnitude is meaningless.

## Visualization of Failure

Figure 1 presents the gate metrics comparison, clearly showing both methods far below the MUST_WORK threshold.

![Gate Metrics Comparison](figures/gate_metrics.png)

*Figure 1: Spearman correlation for SEP and SEDP methods. The horizontal line indicates the MUST_WORK threshold (ρ = 0.3). Both methods fail dramatically, achieving ρ ≈ 0.08.*

Figure 2 shows the scatter plot of predicted vs. true SE values, revealing no discernible correlation.

![Predicted vs True SE](figures/scatter.png)

*Figure 2: Scatter plot of probe predictions versus true semantic entropy. The lack of any visible trend confirms the near-zero correlation.*

Figure 3 presents ROC curves for both methods, hugging the diagonal (random classifier line).

![ROC Curves](figures/roc_curves.png)

*Figure 3: ROC curves for SEP and SEDP. Both curves lie close to the diagonal, indicating near-random classification performance (AUROC ≈ 0.52).*

## Comparison with Published Results

Our results diverge dramatically from published SEP benchmarks:

| Source | AUROC on TruthfulQA |
|--------|---------------------|
| Kossen et al. (2024) | ~0.85 |
| This work (SEP baseline) | 0.52 |
| **Gap** | **39%** |

This 39% gap is the most striking finding of our work. We followed published guidance:
- Layer 25 (middle-to-late range recommended)
- TBG token position (standard choice)
- Logistic regression probe (same architecture)
- TruthfulQA dataset (same benchmark)

Yet we achieved near-random performance. Possible explanations include:

1. **Layer selection sensitivity**: Layer 25 may not be optimal for Llama-3-8B-Instruct; systematic ablation across layers 20-31 may be required.

2. **Token position differences**: The TBG position may miss critical information captured by alternative positions (SLT, pooling).

3. **Implementation details**: Subtle differences in response generation, SE computation, or preprocessing may accumulate to large performance gaps.

4. **Model-specific behavior**: Published results may use different model versions or configurations not fully specified.

## Effect Direction Analysis

Despite the absolute failure, we examine whether similarity augmentation helps directionally:

| Metric | SEP | SEDP | Delta | Direction |
|--------|-----|------|-------|-----------|
| Spearman ρ | 0.0835 | 0.0843 | +0.0009 | ✓ Positive |
| AUROC | 0.5214 | 0.5219 | +0.0004 | ✓ Positive |

The effect direction is positive, consistent with our hypothesis that similarity features provide additional information. However, the magnitude is so small (< 1% relative improvement) that it provides no practical benefit. When the base signal is absent, auxiliary features cannot compensate.

## Interpretation

These results demonstrate that:

1. **Hidden states at layer 25 do not encode SE information** accessible to linear probes, at least for Llama-3-8B-Instruct on TruthfulQA.

2. **The failure is fundamental, not marginal**: ρ = 0.08 is not "almost 0.3"—it is effectively zero correlation.

3. **Similarity augmentation cannot rescue a failed base approach**: Adding 4 dimensions of similarity features to 4096 dimensions of uninformative hidden states does not help.

4. **Configuration sensitivity is a first-order concern**: The gap with published results indicates that SE probing is not plug-and-play; systematic validation is required.
