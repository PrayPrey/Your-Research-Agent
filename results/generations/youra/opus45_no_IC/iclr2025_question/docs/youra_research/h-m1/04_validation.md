# H-M1 Validation Report

## Hypothesis

**ID:** h-m1  
**Type:** MECHANISM  
**Statement:** LLM uncertainty signals (semantic entropy) correlate with error-generation processes

## Gate Criteria

**Gate Type:** MUST_WORK  
**Pass Condition:** p < 0.05 AND Cohen's d > 0.3  
**Fail Action:** PIVOT

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Sample Size | 100 (smoke test) |
| Generations per Question | 10 |
| Temperature | 0.7 |
| Seed | 42 |
| LLM | Llama-2-7B-Chat |
| NLI Model | MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli |
| Dataset | TriviaQA (rc.nocontext, validation split) |

## Results

### Statistical Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| p-value (Mann-Whitney U) | 0.000144 | < 0.05 | **PASS** |
| Cohen's d | 1.325 | > 0.3 | **PASS** |
| AUROC | 0.793 | (secondary) | Strong |

### Entropy Distribution

| Group | N | Mean Entropy | Std Entropy |
|-------|---|--------------|-------------|
| Correct | 87 | 0.418 | 0.603 |
| Incorrect | 13 | 1.252 | 0.746 |

### Key Finding

Incorrect responses exhibit **3x higher semantic entropy** than correct responses on average. This separation is highly significant (p < 0.001) with a large effect size (d > 1.3).

## Gate Verdict

| Criterion | Required | Observed | Result |
|-----------|----------|----------|--------|
| p < 0.05 | Yes | 0.000144 | PASS |
| Cohen's d > 0.3 | Yes | 1.325 | PASS |

## **GATE PASSED: TRUE**

## Figures

- `figures/gate_bar_chart.png` - Bar chart comparing entropy distributions
- `figures/entropy_violin.png` - Violin plot of entropy by correctness
- `figures/roc_curve.png` - ROC curve (AUROC = 0.793)

## Interpretation

The hypothesis is **confirmed**. Semantic entropy computed via bidirectional entailment clustering reliably separates correct from incorrect LLM responses. The effect size (d=1.33) indicates strong practical significance beyond statistical significance.

This validates the mechanism that LLM uncertainty signals correlate with error-generation processes, supporting the foundation for uncertainty-aware response selection in the YouRA framework.

## Limitations

- Smoke test with 100 samples (full validation would use 500-1000)
- Single model (Llama-2-7B-Chat)
- Single dataset (TriviaQA)

## Next Steps

Proceed to dependent hypotheses (h-m2, h-m3, h-m4) as prerequisites are satisfied.
