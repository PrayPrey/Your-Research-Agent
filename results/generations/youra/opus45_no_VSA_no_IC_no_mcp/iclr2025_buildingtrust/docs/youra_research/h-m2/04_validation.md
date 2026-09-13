# Phase 4 Validation Report: h-m2

**Hypothesis**: Pareto-optimal models (no model dominates on both TruthfulQA and AdvGLUE) have significantly lower average ECE than non-Pareto models (t-test p < 0.05).

**Gate Type**: SHOULD_WORK

**Date**: 2026-08-28

---

## Validation Result

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| N(Pareto) | ≥ 3 | 1 | ❌ FAIL |
| N(Non-Pareto) | ≥ 5 | 13 | ✅ PASS |
| t-test p-value | < 0.05 | NaN | ❌ N/A |
| Mean ECE(Pareto) < Mean ECE(Non-Pareto) | - | NaN | ❌ N/A |
| Cohen's d | > 0.5 | NaN | ❌ N/A |

**Gate Verdict**: NOT PASSED (insufficient sample size for Pareto group)

---

## Key Findings

1. **Single Pareto-optimal model**: Only `meta-llama/Llama-2-70b-hf` is non-dominated
   - Highest TruthfulQA MC1: 0.45
   - Highest AdvGLUE avg: 0.84
   - Strictly dominates all other models on BOTH axes

2. **Statistical tests not applicable**: With N=1 for Pareto group, Welch's t-test and Cohen's d cannot be computed

3. **Size-matched baseline (control analysis)**:
   - Split by median log_params: t=0.826, p=0.425
   - No significant ECE difference by model size alone
   - Suggests ECE is not purely confounded by model size

---

## Data Summary

| Group | Count | Models |
|-------|-------|--------|
| Pareto-optimal | 1 | Llama-2-70b-hf |
| Non-Pareto | 13 | All others |

---

## Interpretation

The hypothesis cannot be meaningfully tested with current data because:
1. The evaluation dataset (14 models from h-e1) produces a degenerate Pareto frontier
2. Llama-2-70b-hf dominates all other models on both axes
3. A single-point "frontier" provides no group variance for statistical comparison

**This is a legitimate experimental outcome, not a code error.** The SHOULD_WORK gate permits continuation with limitation noted.

---

## Outputs

- `code/results/results.json` - Full analysis results
- `figures/pareto_frontier.png` - Scatter plot showing single Pareto point
- `figures/ece_comparison.png` - ECE boxplot (1 vs 13 split)

---

## Next Steps

Per SHOULD_WORK gate semantics:
- **Route**: Continue to Phase 5 with limitation noted
- **Limitation**: h-m2 hypothesis untestable with current model sample
- **Recommendation**: Future work should use models with more diverse Truthfulness-Robustness tradeoffs to create meaningful Pareto frontier
