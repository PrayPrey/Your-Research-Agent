# Validation Report: h-c1

**Hypothesis**: CONDITION — Scaling law α estimate is consistent (within 0.15) across single-hop (SQuAD-v2) and multi-hop (HotpotQA) QA tasks

**Gate Type**: SHOULD_WORK

**Generated**: 2026-08-24

## Code Implementation Summary

| Module | Status | Description |
|--------|--------|-------------|
| config.py | Complete | HotpotQA paths, max_length=512, ComparisonConfig |
| model.py | Reused | Copied from h-e1 (unchanged) |
| analyze.py | Reused | Copied from h-e1 (title updated) |
| data_hotpot.py | Complete | HotpotQA loader + multi-doc tokenization |
| train_hotpot.py | Complete | Training loop + answer F1 evaluation |
| main.py | Complete | 72-run sweep driver |
| compare.py | Complete | Cross-task comparison + dual plot |

## Test Results

```
tests/test_modules.py::test_config_imports PASSED
tests/test_modules.py::test_data_hotpot_concat PASSED
tests/test_modules.py::test_analyze_compute_r_opt PASSED
tests/test_modules.py::test_analyze_fit_scaling PASSED
tests/test_modules.py::test_compare_alphas PASSED
tests/test_modules.py::test_compare_alphas_fail PASSED

6 passed
```

## Pipeline Validation (Synthetic Data)

Full 72-run sweep requires GPU resources. Pipeline validated with synthetic data following expected scaling pattern.

### Synthetic Results

| Metric | Value |
|--------|-------|
| α_SQuAD (h-e1) | 0.8156 |
| α_HotpotQA (synthetic) | 0.3018 |
| |Δα| | 0.5139 |
| Threshold | 0.15 |
| CI Overlap | False |

### Gate Verdict

**FAIL** — |Δα| = 0.5139 > 0.15 threshold

Note: This is synthetic data for pipeline validation. Actual experiment requires running 72 training runs on HotpotQA.

## Gate Assessment

- **Gate Type**: SHOULD_WORK (non-blocking)
- **Result**: FAIL (synthetic)
- **Interpretation**: If real experiment also fails, scaling law is NOT consistent across task types (interesting finding)

## Files Generated

- `h-c1/code/results/h-c1_rank_sweep.csv` — Sweep results (72 runs)
- `h-c1/code/results/h-c1_optimal_ranks.csv` — Optimal rank per model/seed
- `h-c1/code/results/h-c1_scaling_fit.json` — Scaling law fit (α, CI, R²)
- `h-c1/code/results/h-c1_cross_task_comparison.json` — Cross-task comparison
- `h-c1/code/figures/h-c1_dual_scaling_plot.png` — Dual scaling visualization

## Next Steps

1. Run actual 72-run sweep on HotpotQA with GPU resources
2. Compare real α_HotpotQA with h-e1's α_SQuAD
3. Determine if scaling law generalizes across task types
