# Methodology

Our methodology is designed to answer a specific question: *Does RLHF cause scalar or geometric distortion of confidence signals?* Building on our observation that RLHF rewards decisive responses regardless of correctness, we hypothesize that margin inflation occurs disproportionately for incorrect predictions, creating geometric distortion that degrades discriminative ability. We operationalize this hypothesis through four complementary measurements, each addressing a distinct aspect of the discriminative degradation phenomenon.

## Overview

We structure our analysis around a causal chain:

1. **Existence (H-E1):** Does discriminative degradation occur? (AUROC comparison)
2. **Mechanism (H-M1):** What causes it? (Conditional margin analysis)
3. **Characterization (H-M2):** Is it geometric or scalar? (Percentile-normalized monotonicity)
4. **Confirmation (H-M3):** Does Brier decomposition agree? (Refinement component analysis)

Each measurement provides independent evidence that converges on the same conclusion, strengthening the overall claim through triangulation.

## Confidence Operationalization

We operationalize model confidence using the logit margin for multiple-choice questions:

$$\text{margin} = \text{logit}_{(1)} - \text{logit}_{(2)}$$

where $\text{logit}_{(1)}$ and $\text{logit}_{(2)}$ are the highest and second-highest logits among answer options (A, B, C, D). This choice follows standard practice in the calibration literature and has several advantages:

**Rationale:** (1) Logit margin captures the model's relative confidence in its top choice versus alternatives, which is more informative than raw softmax probability for discrimination. (2) Margin is invariant to temperature scaling of the softmax—a property we exploit to isolate geometric effects. (3) For MCQ tasks, margin directly relates to the softmax probability via the logistic function, enabling principled statistical analysis.

**Alternatives considered:** We considered using softmax top-1 probability (p_max), but this loses information about the gap to the second choice. Verbalized confidence was rejected because it requires generation and may not reflect internal model states.

## H-E1: Discriminative Degradation Measurement

To measure discriminative quality, we compute AUROC for the binary classification task: predicting correctness from margin.

$$\text{AUROC} = P(\text{margin}_{\text{correct}} > \text{margin}_{\text{incorrect}})$$

AUROC ranges from 0.5 (random) to 1.0 (perfect discrimination). Unlike ECE, AUROC directly measures the model's ability to rank predictions by correctness probability—a higher margin should indicate higher probability of being correct.

**Statistical inference:** We compute bootstrap confidence intervals (n=1,000 iterations) for the AUROC difference between instruction-tuned and base models:

$$\Delta\text{AUROC} = \text{AUROC}_{\text{base}} - \text{AUROC}_{\text{instruct}}$$

If the 95% CI for $\Delta\text{AUROC}$ excludes zero and is positive, discriminative degradation is statistically significant.

## H-M1: Conditional Margin Analysis

To identify the mechanism, we analyze conditional margin distributions separately for correct and incorrect predictions:

$$E[\text{margin} | \text{incorrect}]_{\text{instruct}} \quad \text{vs.} \quad E[\text{margin} | \text{incorrect}]_{\text{base}}$$

**Hypothesis:** If RLHF inflates margins uniformly including for errors, we expect:

$$\frac{E[\text{margin} | \text{incorrect}]_{\text{instruct}}}{E[\text{margin} | \text{incorrect}]_{\text{base}}} > 1$$

We call this the *margin inflation ratio*. Large inflation ratios for incorrect predictions explain AUROC degradation: when errors have inflated margins, the confidence-correctness boundary becomes blurred.

**Statistical inference:** We use permutation tests (n=10,000) to assess whether the inflation ratio significantly exceeds 1. Effect sizes are reported as Cohen's d for practical significance assessment.

## H-M2: Percentile-Normalized Monotonicity

The critical methodological contribution is separating scale effects from shape effects using percentile normalization.

**Intuition:** If RLHF simply shifts all margins by a constant factor (scalar distortion), then normalizing margins to the same scale (via percentile transformation) should eliminate the difference between base and instruct models. If the difference persists after normalization, the distortion is geometric.

**Procedure:**
1. Transform margins to percentile ranks within each model's distribution
2. Fit logistic regression: $P(\text{correct}) = \sigma(\alpha + \beta \cdot z(\text{margin}))$ where $z(\cdot)$ is the percentile z-score
3. Compare $\beta_{\text{base}}$ vs. $\beta_{\text{instruct}}$

**Interpretation:** The coefficient $\beta$ measures the sensitivity of correctness probability to percentile-normalized margin. If $\beta_{\text{instruct}} < \beta_{\text{base}}$ (the slope is attenuated), then:

- The confidence-correctness relationship is *flatter* in instruct models
- This flatness persists even after removing scale differences
- Therefore, the distortion is geometric (shape change), not scalar (scale change)

**Statistical inference:** We compute bootstrap CIs for $\Delta\beta = \beta_{\text{base}} - \beta_{\text{instruct}}$ and report effect sizes via the Wald z-statistic ratio.

## H-M3: Brier Score Decomposition

As independent confirmation, we apply Murphy's decomposition of the Brier score [Murphy, 1973]:

$$\text{Brier} = \text{Reliability} - \text{Refinement} + \text{Uncertainty}$$

where:
- **Reliability (REL):** Calibration error—how well probabilities match observed frequencies
- **Refinement (RES):** Discrimination—how well predictions distinguish outcomes
- **Uncertainty (UNC):** Base rate entropy—inherent unpredictability (constant for same dataset)

**Key insight:** Temperature scaling (scalar correction) primarily affects Reliability by shifting probabilities toward or away from extremes. Geometric distortion affects Refinement by degrading the model's ability to discriminate correct from incorrect predictions.

**Procedure:**
1. Convert margins to probabilities via calibrated softmax
2. Bin predictions into K=15 confidence bins
3. Compute decomposition components
4. Compare $\text{Refinement}_{\text{base}}$ vs. $\text{Refinement}_{\text{instruct}}$

**Interpretation:** If $\text{Refinement}_{\text{instruct}} < \text{Refinement}_{\text{base}}$, the model has lost discriminative ability—confirming geometric distortion independent of the monotonicity analysis.

## Experimental Controls

To isolate the effect of RLHF instruction tuning, we implement several controls:

**Paired comparison design:** We compare base and instruction-tuned versions within the same model family (e.g., Qwen2.5-7B vs. Qwen2.5-7B-Instruct), controlling for architecture and pretraining data.

**Inference settings:** All models use greedy decoding (T=0) to eliminate sampling variance. The same prompts and questions are used for both base and instruct models.

**Cross-family validation:** We test across multiple model families (Qwen, Mistral) to distinguish RLHF effects from vendor-specific implementation details. Consistent effects across families suggest RLHF is the cause.

**Statistical rigor:** All comparisons use bootstrap confidence intervals (for AUROC, β) or permutation tests (for conditional means) with n≥1,000 iterations. We report effect sizes alongside p-values to assess practical significance.

## Summary

Our methodology provides four complementary perspectives on the same phenomenon:

| Measurement | What it tests | Positive result indicates |
|-------------|---------------|---------------------------|
| H-E1 (AUROC) | Discriminative degradation exists | AUROC drops after RLHF |
| H-M1 (Margin inflation) | Mechanism is margin inflation | E[margin\|incorrect] increases disproportionately |
| H-M2 (β_percentile) | Distortion is geometric | Slope attenuates even after percentile normalization |
| H-M3 (Brier refinement) | Independent confirmation | Refinement component degrades |

This triangulation design ensures that our conclusions are robust: each measurement could fail independently, and agreement across all four provides strong evidence for the geometric distortion hypothesis.
