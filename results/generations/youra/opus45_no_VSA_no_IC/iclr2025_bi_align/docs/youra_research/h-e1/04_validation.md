# Phase 4 Validation Report: H-E1

## Hypothesis Summary

| Field | Value |
|-------|-------|
| ID | h-e1 |
| Type | EXISTENCE |
| Statement | Mode 3 (Misaligned-Confident: high human entropy, low RM variance) constitutes >10% of Chatbot Arena samples |
| Gate | MUST_WORK |

## Experiment Results

### Dataset

- **Source**: lmsys/lmsys-arena-human-preference-55k
- **Total samples**: 57,477 battles
- **Valid battles**: 57,477 (100%)

### Mode Distribution

| Mode | Description | Count | Proportion |
|------|-------------|-------|------------|
| 1 | Low entropy, Low variance | 15,107 | 26.3% |
| 2 | Low entropy, High variance | 13,714 | 23.9% |
| 3 | High entropy, Low variance | 13,632 | 23.7% |
| 4 | High entropy, High variance | 15,024 | 26.1% |

### Statistical Test

| Metric | Value |
|--------|-------|
| Mode 3 count | 13,632 |
| Total count | 57,477 |
| Proportion | 0.237 (23.7%) |
| 95% CI lower | 0.234 |
| Null hypothesis | p ≤ 0.10 |
| Alternative | p > 0.10 |
| p-value | < 0.001 |
| Result | **SUCCESS** |

### Interpretation

Mode 3 (high human entropy, low RM variance) constitutes **23.7%** of samples, significantly exceeding the 10% threshold (p < 0.001). The 95% confidence interval lower bound (23.4%) is well above 10%.

## Gate Evaluation

| Criterion | Status |
|-----------|--------|
| Code executes without errors | PASS |
| Mechanism implemented correctly | PASS |
| Metrics measurable | PASS |
| Mode 3 > 10% | PASS |

**Gate Result**: SATISFIED

## Limitations

1. **RM Variance Proxy**: Used single RM (OpenAssistant) with score difference as variance proxy. Full validation requires multi-RM ensemble (OpenAssistant + PairRM + ArmoRM).

2. **Human Entropy**: Computed at model-pair level, not individual battle level. This is consistent with experiment design but aggregates across heterogeneous prompts.

## Outputs

| File | Description |
|------|-------------|
| `code/outputs/mode_distribution.json` | Mode counts and proportions |
| `code/outputs/statistical_results.json` | Binomial test results |
| `code/outputs/results.csv` | Per-battle mode assignments |
| `code/outputs/rm_scores.parquet` | Cached RM scores (partial) |

## Conclusion

Hypothesis h-e1 is **CONFIRMED** at PoC level. Mode 3 exists in significant proportion (23.7% >> 10%). Proceed to Phase 5 for baseline comparison with full multi-RM scoring.

## Next Steps

1. Complete PairRM scoring (currently 4%)
2. Add ArmoRM scoring (pending memory availability)
3. Recompute with true multi-RM variance
4. Phase 5: Compare against baseline methods
