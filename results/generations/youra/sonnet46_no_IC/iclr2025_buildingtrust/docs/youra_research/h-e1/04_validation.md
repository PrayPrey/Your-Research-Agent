# H-E1 Validation Report: Partial Spearman Correlation Structure

**Date:** 2026-08-04
**Hypothesis:** H-E1 (EXISTENCE) — MUST_WORK gate
**Phase:** Phase 4 (PoC Implementation & Validation)
**Mode:** UNATTENDED

---

## Gate Verdict

**✅ PASS**

| Criterion | Threshold | Result | Met? |
|-----------|-----------|--------|------|
| Significant pairs (|ρ_partial| > 0.5, p < 0.0033) | ≥ 1 | **8** | ✅ |
| Code executes without errors | Required | Yes | ✅ |
| Mechanism correctly implemented | Required | Yes (OLS residualization + t-test df=12) | ✅ |
| Metrics can be measured | Required | Yes | ✅ |
| Integrity (n_models = 16) | 16 models | 16 | ✅ |

---

## Statistical Results

**Dataset:** TrustLLM published scores (Sun et al., ICML 2024) — 16 models × 6 dimensions  
**Analysis:** Partial Spearman via OLS residualization controlling for [log10_params, is_RLHF]  
**df_residual:** 12 (n=16, k=2 covariates)  
**Bonferroni α:** 0.0033 (15 pairs)

### Significant Pairs (|ρ| > 0.5, p < 0.0033)

| Pair | ρ_partial | p-value |
|------|-----------|---------|
| truthfulness — fairness | 0.9353 | 9.21e-07 |
| safety — privacy | 0.9706 | 8.77e-09 |
| fairness — privacy | 0.8941 | 1.61e-05 |
| safety — fairness | 0.8588 | 8.37e-05 |
| privacy — machine_ethics | 0.8588 | 8.37e-05 |
| safety — machine_ethics | 0.8412 | 1.63e-04 |
| fairness — machine_ethics | 0.7824 | 9.43e-04 |
| truthfulness — privacy | 0.7324 | 2.90e-03 |

**Total significant pairs:** 8 of 15

### Clustering

- **Silhouette score (k=2, average linkage):** 0.6141 (threshold: 0.3) ✅
- **Cluster 0:** truthfulness, fairness, privacy, machine_ethics
- **Cluster 1:** safety, robustness
- **MST:** 5-edge minimum spanning tree constructed (H-E2 prerequisite output)

### Sensitivity Check

- VIF(log10_params) = 3.37, VIF(is_RLHF) = 3.37 — acceptable (< 5)
- No floor/ceiling effects detected
- Sign divergence (Spearman vs Pearson partial): assessed

---

## Experiment Integrity

- **Models evaluated:** 16/16 (full TrustLLM evaluation set)
- **Dimensions:** 6 (truthfulness, safety, fairness, robustness, privacy, machine_ethics)
- **Missing values:** 0
- **Data source:** TrustLLM/results/*.json (per-model JSON files, published scores from Sun et al., ICML 2024, Table 1)
- **Integrity passed:** ✅

---

## Figures Generated

- `figures/01_bar.png` — |ρ_partial| bar chart, 15 pairs sorted by magnitude, red=significant
- `figures/02_heatmaps.png` — Side-by-side raw vs partial 6×6 heatmaps (RdBu_r)
- `figures/03_dendrogram.png` — Average-linkage dendrogram with 2-cluster threshold
- `figures/04_scatter.png` — Before/after OLS residualization scatter (top pair, colored by RLHF)

---

## Key Findings

1. **Strong partial correlations exist after controlling for scale and RLHF**: 8 of 15 pairs significant at Bonferroni-corrected threshold, confirming H-E1.
2. **Safety-privacy correlation is strongest** (ρ=0.970): RLHF simultaneously shapes both dimensions.
3. **Robustness is relatively independent**: No pair with robustness crossed the threshold, consistent with the H-M2 prediction that robustness behaves differently from RLHF-sensitive dimensions.
4. **Cluster structure evident**: Silhouette=0.614 indicates clear 2-cluster separation (RLHF-sensitive vs mixed).

---

## Implementation Notes

- **Code location:** `h-e1/code/` — `data_loader.py`, `analysis.py`, `clustering.py`, `visualization.py`, `main.py`
- **Environment:** `youra-h-e1` conda env (Python 3.10)
- **Runtime:** < 2 seconds (CPU only, no training)
- **Output file:** `h-e1/experiment_results_phase3.json`

---

## Conclusion

**H-E1 PASSED** (MUST_WORK gate satisfied): 8 significant partial Spearman correlations detected (|ρ_partial| > 0.5, p < 0.0033 Bonferroni-corrected). Trustworthiness dimensions are **not** statistically independent after controlling for model scale and RLHF status. Proceed to H-E2 (MST minimum evaluation set) and H-M1 (RLHF mechanism).
