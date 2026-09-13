# Experimental Setup

## Research Questions

We investigate whether category-specific calibration can improve LLM truthfulness evaluation through three research questions:

**RQ1:** Does calibration error vary significantly across semantic categories on TruthfulQA?

**RQ2:** Do LLMs produce distinct confidence distributions for different categories?

**RQ3:** Do different confidence distributions require different temperature parameters for optimal calibration?

These questions map directly to hypotheses h-e1, h-m1, and h-m2 respectively, forming a causal chain: if category variation exists (RQ1) and distributions differ (RQ2), then different temperatures should be needed (RQ3).

## Model

We evaluate **Llama-2-7B** (meta-llama/Llama-2-7b-hf), a 7-billion parameter decoder-only transformer. Selection criteria:
- Open weights with accessible logits (required for temperature scaling)
- Representative of modern instruction-tuned LLMs
- Computationally tractable for multiple cross-validation folds

## Dataset Configuration

| Setting | Value |
|---------|-------|
| Benchmark | TruthfulQA (multiple_choice, validation) |
| Total questions | 817 |
| Category clusters | 7 |
| Min cluster size | 70 (Finance/Economics) |
| Max cluster size | 168 (Society/Culture) |
| Cross-validation folds | 5 |

## Baselines

**Uncalibrated:** Raw softmax probabilities from model logits. Expected to show overconfidence based on prior work on RLHF models.

**Global Temperature Scaling:** Single temperature optimized across all predictions. Standard post-hoc calibration baseline per Guo et al. \cite{guo2017calibration}.

**Cluster-Specific Temperature Scaling:** One temperature per cluster. Our proposed method.

## Evaluation Protocol

1. **Logit extraction:** For each question, extract logits for all answer options
2. **Temperature optimization:** Minimize NLL on training folds with bounds [0.1, 10.0]
3. **ECE computation:** 15-bin ECE with 100 bootstrap iterations for 95% CI
4. **Statistical tests:**
   - ANOVA F-test for cluster ECE variation (h-e1)
   - Kolmogorov-Smirnov for pairwise distribution comparison (h-m1)
   - Coefficient of variation for temperature uniformity (h-m2)

## Success Criteria

| Hypothesis | Metric | Target | Actual | Status |
|------------|--------|--------|--------|--------|
| h-e1 | ANOVA p | < 0.05 | 0.00012 | PASS |
| h-e1 | ECE range | > 0.05 | 0.099 | PASS |
| h-m1 | Significant KS pairs | ≥ 11/21 | 17/21 | PASS |
| h-m1 | Confidence range | > 0.1 | 0.4325 | PASS |
| h-m2 | CV(optimal T) | > 0.1 | 0.0 | FAIL |
| h-m2 | Range(optimal T) | > 0.3 | 0.0 | FAIL |

## Hyperparameters

```yaml
model: meta-llama/Llama-2-7b-hf
temperature_bounds: [0.1, 10.0]
ece_bins: 15
bootstrap_iterations: 100
cv_folds: 5
random_seed: 42
```
