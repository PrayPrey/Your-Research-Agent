# Tasks: H-E1 (Model Zoo Dataset Validity)

**Hypothesis:** H-E1 | **Type:** EXISTENCE | **Tier:** LIGHT | **Budget:** 15 tasks max

## Task List

| ID | Module | Task | Description | Complexity | Est. Hours |
|----|--------|------|-------------|------------|------------|
| T-1 | data | `load_accuracies()` | HuggingFace primary loader with .pt fallback | 3 | 2 |
| T-2 | data | NaN filtering | Filter corrupted/NaN entries, normalize to [0,100] | 2 | 1 |
| T-3 | analysis | `validate_model_zoo_variance()` | Compute mean/std/min/max/quartiles | 2 | 1 |
| T-4 | analysis | Shapiro-Wilk test | Add normality test to validation | 1 | 0.5 |
| T-5 | analysis | IQR outlier detection | Compute outliers using 1.5×IQR rule | 2 | 1 |
| T-6 | analysis | Gate check | gate_passed = std > 10.0 | 1 | 0.5 |
| T-7 | visualize | Gate bar chart | Plot gate comparison (threshold vs actual) | 2 | 1 |
| T-8 | visualize | Histogram | Accuracy distribution histogram with stats overlay | 2 | 1 |

**Total Tasks:** 8 | **Budget Remaining:** 7

## Dependencies

```
T-1 → T-2 → T-3 → T-4, T-5, T-6 (parallel)
T-3 → T-7, T-8 (parallel)
```

## Execution Order

1. T-1, T-2 (data loading)
2. T-3, T-4, T-5, T-6 (analysis)
3. T-7, T-8 (visualization)

## Gate Criteria

- **PASS:** σ(accuracy) > 10% across Model Zoo dataset
- **FAIL:** σ(accuracy) ≤ 10% indicates insufficient variance
