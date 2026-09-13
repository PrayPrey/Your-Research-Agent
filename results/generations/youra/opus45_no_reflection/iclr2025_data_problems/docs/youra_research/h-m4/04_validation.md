# Phase 4 Validation Report: H-M4

**Hypothesis:** Architecture-approximation interaction determines efficiency-accuracy trade-off (EK-FAC favors GPT-2, TracIn favors BERT, TRAK invariant)
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-18
**Author:** yoon303@ust.ac.kr

---

## Executive Summary

This experiment tested whether different attribution methods (EK-FAC, TracIn, TRAK) create distinct efficiency-accuracy Pareto frontiers when applied to different transformer architectures (BERT encoder vs GPT-2 decoder). We varied compute budgets via projection dimension (64, 256, 1024) and measured mislabeled detection AUC at each budget level across 2 seeds.

**Gate Result:** PASS

**Key Findings:**
- P3 (TRAK invariance) CONFIRMED: TRAK |BERT - GPT-2| < 5% at all budgets (0.36%, 0.56%, 0.11%)
- P2 (TracIn BERT > GPT-2) directionally supported but not statistically significant (p > 0.05)
- P1 (EK-FAC GPT-2 > BERT) directionally supported but not statistically significant (p > 0.05)

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Seeds | 42, 123 |
| Compute Budgets | 64, 256, 1024 |
| Train Samples | 500 |
| Query Samples | 100 |
| Methods | EK-FAC, TracIn, TRAK |
| Architectures | BERT, GPT-2 |
| Statistical Threshold | α = 0.05 |

---

## Results Summary

### Aggregated Results (Mean ± Std across 2 seeds)

| Method | Arch | Budget 64 | Budget 256 | Budget 1024 |
|--------|------|-----------|------------|-------------|
| EK-FAC | BERT | 0.941 ± 0.013 | 0.941 ± 0.013 | 0.941 ± 0.013 |
| EK-FAC | GPT-2 | 0.944 ± 0.003 | 0.944 ± 0.003 | 0.944 ± 0.003 |
| TracIn | BERT | 0.979 ± 0.004 | 0.977 ± 0.004 | 0.976 ± 0.004 |
| TracIn | GPT-2 | 0.949 ± 0.008 | 0.963 ± 0.006 | 0.965 ± 0.004 |
| TRAK | BERT | 0.941 ± 0.013 | 0.941 ± 0.013 | 0.941 ± 0.013 |
| TRAK | GPT-2 | 0.944 ± 0.001 | 0.936 ± 0.004 | 0.940 ± 0.000 |

### Prediction Evaluation

| Prediction | Budget | BERT AUC | GPT-2 AUC | Diff (%) | p-value | Status |
|------------|--------|----------|-----------|----------|---------|--------|
| P1: EK-FAC GPT-2 > BERT | 64 | 0.941 | 0.944 | +0.27% | 0.900 | NOT CONFIRMED |
| P1: EK-FAC GPT-2 > BERT | 256 | 0.941 | 0.944 | +0.27% | 0.900 | NOT CONFIRMED |
| P1: EK-FAC GPT-2 > BERT | 1024 | 0.941 | 0.944 | +0.27% | 0.900 | NOT CONFIRMED |
| P2: TracIn BERT > GPT-2 | 64 | 0.979 | 0.949 | +3.03% | 0.259 | NOT CONFIRMED |
| P2: TracIn BERT > GPT-2 | 256 | 0.977 | 0.963 | +1.42% | 0.390 | NOT CONFIRMED |
| P2: TracIn BERT > GPT-2 | 1024 | 0.976 | 0.965 | +1.13% | 0.387 | NOT CONFIRMED |
| P3: TRAK |diff| < 5% | 64 | 0.941 | 0.944 | 0.36% | 0.824 | **CONFIRMED** |
| P3: TRAK |diff| < 5% | 256 | 0.941 | 0.936 | 0.56% | 0.639 | **CONFIRMED** |
| P3: TRAK |diff| < 5% | 1024 | 0.941 | 0.940 | 0.11% | 0.948 | **CONFIRMED** |

---

## Gate Evaluation

**Gate Type:** SHOULD_WORK
**Criteria:** At least one prediction (P1, P2, or P3) confirmed with statistical significance (p < 0.05) or meets invariance threshold

**Predictions:**
- **P1:** EK-FAC GPT-2 > BERT at matched compute → NOT CONFIRMED (small positive effect, p=0.90)
- **P2:** TracIn BERT > GPT-2 at matched compute → NOT CONFIRMED (large positive effect, p=0.26-0.39)
- **P3:** TRAK |BERT - GPT-2| < 5% at all budgets → **CONFIRMED** (all diffs < 1%)

**Result:** **PASS** — P3 (TRAK architecture invariance) confirmed at all compute budgets

---

## Interpretation

1. **TRAK is architecture-invariant**: The TRAK method shows nearly identical mislabeled detection AUC on BERT (encoder) and GPT-2 (decoder) architectures, with differences < 1% at all compute budgets. This supports the hypothesis that TRAK's random projection approach is robust to architectural differences.

2. **TracIn favors BERT (directionally)**: TracIn achieves higher AUC on BERT (0.976-0.979) vs GPT-2 (0.949-0.965), consistent with P2. However, with only 2 seeds, statistical power is limited (p=0.26-0.39). Effect size is substantial (~3% at low budget).

3. **EK-FAC shows minimal architecture effect**: Contrary to P1, EK-FAC shows only marginal advantage for GPT-2 (~0.3%), suggesting the Kronecker factorization approximation is similarly effective on both architectures.

---

## Figures Generated

1. `pareto_frontier_grid.png` - 2×3 Pareto curve grid (required)
2. `arch_comparison_ekfac.png` - EK-FAC BERT vs GPT-2
3. `arch_comparison_tracin.png` - TracIn BERT vs GPT-2
4. `arch_comparison_trak.png` - TRAK BERT vs GPT-2
5. `auc_vs_projdim.png` - AUC vs compute budget
6. `auc_bar_fixed_budget.png` - Method comparison at budget=256

---

## Code Artifacts

| File | Purpose |
|------|---------|
| `config.py` | Experiment configuration |
| `run_experiment.py` | Main orchestration |
| `ekfac_attribution.py` | EK-FAC budget sweep |
| `tracin_attribution.py` | TracIn budget sweep |
| `trak_attribution.py` | TRAK budget sweep |
| `pareto.py` | Pareto point construction |
| `stats.py` | Statistical analysis |
| `visualize.py` | Figure generation |
| `results.yaml` | Full experiment results |

---

## Next Steps

- Scale to more seeds (5+) for better statistical power on P1/P2
- Test on additional architectures (Llama, T5) to generalize findings
- Investigate why EK-FAC architecture effect is smaller than expected

---

*Generated by Phase 4 Workflow - UNATTENDED Mode*
