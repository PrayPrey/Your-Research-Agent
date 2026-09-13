# Validation Report: H-M3
# Per-Pair Adversarial Rank Disruption Analysis

**Date:** 2026-08-20  
**Hypothesis ID:** h-m3  
**Gate Type:** SHOULD_WORK  
**Gate Result:** FAIL  

---

## Hypothesis Statement

Partial Spearman ρ for each adversarial robustness benchmark pair individually (ρ_AdvGLUE and ρ_ANLI, MMLU-controlled) is **not significantly positive** (ρ < 0.4 or p ≥ 0.05), confirming that adversarial benchmark design disrupts cross-split rank stability for both GLUE→AdvGLUE and ANLI R1→R3.

---

## Gate Criteria

Gate PASSES if:
- (rho_AdvGLUE < 0.4 **OR** p_AdvGLUE ≥ 0.05) **AND** (rho_ANLI < 0.4 **OR** p_ANLI ≥ 0.05)

---

## Key Results

| Metric | Value |
|--------|-------|
| N models | 13 |
| rho_AdvGLUE (partial Spearman, MMLU-controlled) | **0.8675** |
| p_AdvGLUE (asymptotic) | 0.0001 |
| CI_AdvGLUE (bootstrap 95%) | [0.877, 1.000] |
| Fisher z_AdvGLUE vs threshold | z=2.843, p=0.9978 (NOT sig) |
| rho_ANLI (partial Spearman, MMLU-controlled) | **0.6835** |
| p_ANLI (asymptotic) | 0.0071 |
| CI_ANLI (bootstrap 95%) | [0.863, 1.000] |
| Fisher z_ANLI vs threshold | z=1.303, p=0.9037 (NOT sig) |
| Rank reversals AdvGLUE | 0 |
| Rank reversals ANLI | 0 |
| rho_fairness_HM1 (reference) | 0.600 |
| gate_passed | **False** |
| mechanism_ok | True |

---

## Gate Evaluation

- **AdvGLUE condition:** rho_AdvGLUE=0.8675 ≥ 0.4 **AND** p=0.0001 < 0.05 → **FAIL**
- **ANLI condition:** rho_ANLI=0.6835 ≥ 0.4 **AND** p=0.0071 < 0.05 → **FAIL**
- **Gate:** FAIL (both conditions failed)

---

## Interpretation

The hypothesis predicted that adversarial benchmark construction would disrupt cross-split rank stability, yielding low or non-significant partial Spearman correlations. The data shows the opposite: both benchmark pairs exhibit **strongly positive** partial Spearman correlations after MMLU control (ρ_AdvGLUE=0.868, ρ_ANLI=0.684), with zero rank reversals.

Models that perform well on GLUE also perform well on AdvGLUE, and models that perform well on ANLI R1 also perform well on ANLI R3, even after controlling for general capability (MMLU). This contradicts the mechanism proposed in h-m3.

Combined with h-m2's finding that ρ_fairness > ρ_robustness (albeit Δρ=0.192 < 0.200 threshold), the overall picture suggests that adversarial benchmark construction preserves — rather than disrupts — cross-split rank stability within robustness domains.

---

## Figures Generated

- `figures/gate_metrics_comparison.png` — bar chart of rho values vs threshold
- `figures/rank_scatter_advglue.png` — rank scatter GLUE vs AdvGLUE
- `figures/rank_scatter_anli.png` — rank scatter ANLI R1 vs ANLI R3
- `figures/rank_reversal_heatmap.png` — model rank position heatmap
- `figures/correlation_summary_table.png` — summary table of all correlations
- `figures/fisher_z_distribution.png` — Fisher z distribution with pair positions

---

## Mechanism Indicators

All 6 mechanism indicators passed: data_complete, n_sufficient, advglue_computed, anli_computed, pairs_differ, reversals_counted.

---

## Conclusion

**Gate: FAIL.** H-M3 is FALSIFIED. Adversarial benchmark pairs show high rank stability (ρ ≫ 0.4, p ≪ 0.05), contradicting the hypothesis that adversarial construction disrupts rank ordering across splits.
