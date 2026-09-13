# H-M2 Validation Report

**Generated:** 2026-08-24 04:32:33
**Hypothesis:** HaluEval measures generation coherence/consistency, distinct from TruthfulQA's misconception resistance

## Gate Result: PASS

| Condition | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| r(HaluEval, TruthfulQA) | 0.162 | < 0.7 | PASS |
| r_intra > r_cross | 0.645 > 0.162 | - | PASS |

## Summary Statistics

- **N models analyzed:** 50
- **Primary correlation:** r(HaluEval_agg, TruthfulQA) = 0.162 (p = 0.2614)
- **95% Bootstrap CI:** [-0.095, 0.395]
- **Intra-HaluEval mean correlation:** 0.645

## Cross-Benchmark Correlations (HaluEval subtask vs TruthfulQA)

| Subtask | Spearman r | p-value |
|---------|-----------|---------|
| Qa | 0.153 | 0.2878 |
| Dialogue | 0.148 | 0.3062 |
| Summarization | 0.222 | 0.1216 |
| Halueval Ci | -0.095 | 0.3951 |

## Intra-HaluEval Correlations

| Pair | Spearman r | p-value |
|------|-----------|---------|
| Qa Vs Dialogue | 0.692 | 0.0000 |
| Qa Vs Summarization | 0.601 | 0.0000 |
| Dialogue Vs Summarization | 0.641 | 0.0000 |

## Interpretation

The cross-benchmark correlation r = 0.162 is below the 0.7 threshold,
indicating that HaluEval and TruthfulQA measure partially distinct capabilities.

The intra-HaluEval correlation (mean r = 0.645) is higher than
the cross-benchmark correlation, supporting the hypothesis that HaluEval subtasks
share a common coherence/consistency dimension that is distinct from misconception resistance.

## Figures

- `figures/correlation_heatmap.png`: Pairwise correlation matrix
- `figures/scatter_halueval_truthfulqa.png`: HaluEval vs TruthfulQA scatter
- `figures/gate_metrics.png`: Cross vs intra correlation comparison
