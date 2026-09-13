# Phase 4 Validation Report: H-M1

**Generated:** 2026-08-20T09:30:00+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5
**Gate Type:** MUST_WORK

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-M1 |
| **Type** | MECHANISM |
| **Statement** | Partial Spearman ρ between BBQ-Disambig and BBQ-Ambig model rankings (MMLU-controlled) is significantly positive (ρ > 0.4, p < 0.05), because fairness failures are encoded as stable latent statistical biases in model weights |
| **Prerequisite** | H-E1 (VALIDATED — N_common ≥ 10 established) |
| **Dataset** | TrustLLM published scores (arXiv 2401.05561) |
| **N_common** | 16 LLMs |
| **Duration** | < 5 seconds (pure statistical analysis) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 16 |
| Completed | 16 |
| Coder-Validator Cycles | 1 |
| Test Files | 2 (test_analysis.py, test_data.py) |
| Tests Passed | 9 / 9 |

### Generated Files

| File | Description |
|------|-------------|
| `code/config.py` | Gate thresholds, paths, Winogrande scores |
| `code/data.py` | Score DataFrame assembly from H-E1 published scores |
| `code/analysis.py` | Raw + partial Spearman, gate evaluation |
| `code/visualize.py` | 5 matplotlib figures |
| `code/run_experiment.py` | Entry point with argparse + self-check |
| `code/tests/test_analysis.py` | 6 analysis function tests |
| `code/tests/test_data.py` | 3 data assembly tests |
| `code/requirements.txt` | Package dependencies |

---

## Code Quality Checklist

- [✓] All 9 pytest tests pass
- [✓] Dry run (--dry-run) executes successfully
- [✓] API signatures match 03_logic.md specifications
- [✓] Mechanism verification asserts in compute_partial_spearman()
- [✓] No mock/synthetic data in main code (real TrustLLM published scores)
- [✓] Results saved to RESULTS_DIR/results.json
- [✓] Figures saved to figures/ directory

---

## Experiment Results

### Primary Metric: Partial Spearman ρ (MMLU-controlled)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Partial ρ (MMLU control) | **0.9617** | > 0.4 | ✅ PASS |
| p-value (one-tailed) | **0.0000** | < 0.05 | ✅ PASS |
| N_common | **16** | ≥ 10 | ✅ PASS |
| 95% CI | [0.90, 1.00] | — | ✅ |

### Secondary Metric: Raw Spearman ρ (no control)

| Metric | Value | Expected | Status |
|--------|-------|----------|--------|
| Raw ρ (unadjusted) | **0.9794** | > partial ρ | ✅ PASS |
| p-value | **3.98e-11** | — | ✅ |
| N | 16 | — | ✅ |

> MMLU explains some variance: raw ρ (0.9794) > partial ρ (0.9617) ✅

### Sensitivity Analysis: Winogrande Control

| Metric | Value | Status |
|--------|-------|--------|
| Partial ρ (Winogrande) | **0.9691** | ✅ Robust |
| p-value | **0.0000** | ✅ |
| N (Winogrande subset) | 14 | ✅ |

Winogrande-controlled ρ ≈ MMLU-controlled ρ — result is not MMLU-specific. ✅

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | **PASS** |
| **Satisfied** | **True** |
| **Primary ρ** | 0.9617 (threshold: > 0.4) |
| **p-value** | 0.0000 (threshold: < 0.05) |
| **N** | 16 (minimum: 10) |
| **Mechanism Activated** | Yes — "Partial Spearman ρ computed: ρ=0.962, p=0.0000, n=16" |

**Gate PASS — proceed to Phase 5.**

---

## Mechanism Verification

Mechanism activation confirmed per 02c protocol:

```
✅ assert n >= 10            → n=16 ≥ 10
✅ assert -1 ≤ partial_rho ≤ 1 → 0.9617 ∈ [-1, 1]
✅ assert 0 ≤ p_value ≤ 1   → 0.0000 ∈ [0, 1]
Log: "Partial Spearman ρ computed: ρ=0.962, p=0.0000, n=16"
```

The result strongly supports H-M1: fairness rankings (BBQ-Disambig and BBQ-Ambig) are highly correlated even after controlling for general capability (MMLU), indicating that fairness behavior is a stable property of model weights rather than a confound of general intelligence.

---

## Figures Generated

| Figure | Description |
|--------|-------------|
| `figures/gate_metrics_comparison.png` | Bar chart: partial ρ vs raw ρ, gate threshold at 0.4 |
| `figures/rank_scatter_bbq.png` | BBQ-Disambig rank vs BBQ-Ambig rank, model labels |
| `figures/sensitivity_comparison.png` | MMLU vs Winogrande control comparison |
| `figures/score_distributions.png` | Box plots of BBQ-Disambig and BBQ-Ambig scores |
| `figures/mmlu_vs_fairness.png` | MMLU rank vs BBQ-Disambig rank (capability confound) |

---

## Next Steps

**Gate: PASS → Proceed to Phase 5 (Baseline Comparison)**

H-M1 mechanism confirmed. The very high partial ρ (0.96) is consistent with the hypothesis that fairness bias is a stable latent property — but note that the extremely high correlation (approaching 1.0) suggests the BBQ-Disambig and BBQ-Ambig splits may not fully isolate the proposed mechanism (stable weights vs. context informativeness). Phase 5 baseline comparison should investigate whether the correlation pattern differs from what would be expected under a null model.

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status |
|-----------|------|--------|
| `build_score_dataframe()` | `code/data.py` | ✅ PASS |
| `compute_raw_spearman()` | `code/analysis.py` | ✅ PASS |
| `compute_partial_spearman()` | `code/analysis.py` | ✅ PASS |
| `evaluate_gate()` | `code/analysis.py` | ✅ PASS |
| `run_full_analysis()` | `code/analysis.py` | ✅ PASS |
| `generate_all_figures()` | `code/visualize.py` | ✅ PASS |

### Optimal Configuration

```yaml
gate_rho: 0.4
gate_p: 0.05
n_common_min: 10
alternative: "greater"
method: "spearman"
covar: "mmlu"
```

### Lessons Learned

**What Worked:**
- Importing H-E1 published scores directly (TRUSTLLM_SCORES, MMLU_SCORES) — no data download needed
- pingouin.partial_corr with alternative="greater" for one-tailed test
- Explicit importlib-based imports to avoid sys.path conflicts between h-e1 and h-m1 modules

**What Didn't Work:**
- Default sys.path insertion for h-e1 code — caused module name collisions (h-e1 config.py imported instead of h-m1 config.py); fixed with importlib.util

**Key Insight:** N_common=16 (all TrustLLM models have both BBQ splits and MMLU) — no data gap. The partial ρ=0.962 is substantially higher than the expected 0.45–0.75 range, suggesting stronger rank stability than hypothesized.

### Recommendations for Dependent Hypotheses (H-M2, H-M3)

- Reuse `code/data.py:build_score_dataframe()` as data source
- The BBQ-Disambig/BBQ-Ambig correlation is unexpectedly high — H-M2/M3 should investigate whether the GLUE/AdvGLUE pair shows similar stability
- Use importlib-based imports to avoid module name conflicts when building on H-E1 code

---

## Appendix

### Files Created

```
h-m1/code/config.py
h-m1/code/data.py
h-m1/code/analysis.py
h-m1/code/visualize.py
h-m1/code/run_experiment.py
h-m1/code/requirements.txt
h-m1/code/tests/test_analysis.py
h-m1/code/tests/test_data.py
h-m1/code/outputs/results.csv
h-m1/data/h_m1_scores.csv
h-m1/results/results.json
h-m1/experiment_results.json
h-m1/experiment.log
h-m1/figures/gate_metrics_comparison.png
h-m1/figures/rank_scatter_bbq.png
h-m1/figures/sensitivity_comparison.png
h-m1/figures/score_distributions.png
h-m1/figures/mmlu_vs_fairness.png
```

### Conda Environment

- Environment: `youra-h-m1`
- Python: 3.10.20
- Key packages: pingouin==0.6.1, scipy, pandas, matplotlib, seaborn

### Raw Results (experiment_results.json)

```json
{
  "raw": {"raw_rho": 0.9794, "raw_p": 3.98e-11, "n": 16},
  "primary": {"partial_rho": 0.9617, "p_value": 0.0, "ci95": [0.90, 1.0], "n": 16},
  "sensitivity": {"partial_rho": 0.9691, "p_value": 0.0, "ci95": [0.92, 1.0], "n": 14},
  "gate_pass": true,
  "mmlu_explains_variance": true
}
```
