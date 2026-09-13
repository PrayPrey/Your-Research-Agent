# Phase 4 Validation Report: H-M2 — Tag Count Dose-Response

**Date:** 2026-08-05
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS

---

## Executive Summary

H-M2 validates that within the tagged OpenML dataset subset (has_tags=1, N=2,625), datasets with more keyword tags have significantly more registered ML tasks. The continuous IV log(tag_count+1) yields IRR=1.5332 (95% CI: [1.4680, 1.6014], p=1.28e-82) in NB-2 regression with decade fixed effects. The SHOULD_WORK gate (CI_lower ≥ 1.05 AND p < 0.05) is **PASSED**. Dose-response mechanism confirmed.

---

## 1. Hypothesis Statement

Under OpenML context (has_tags=1 subset, N≈2,625), if a dataset has more keyword tags (higher log(tag_count+1)), then it will have more registered ML tasks (N_tasks), because more tags create more search pathways leading to higher discovery probability, with NB-2 IRR for log(tag_count+1) having 95% CI lower ≥ 1.05 and p < 0.05.

**Prerequisites:** H-E1 (MUST_WORK PASS), H-M1 (MUST_WORK PASS)

---

## 2. Gate Evaluation

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| IRR_P2 CI lower bound | ≥ 1.05 | 1.4680 | ✓ PASS |
| p-value | < 0.05 | 1.28e-82 | ✓ PASS |

**Overall Gate: PASS**

---

## 3. Primary Results

| Metric | Value |
|--------|-------|
| IRR_P2 | 1.5332 |
| 95% CI | [1.4680, 1.6014] |
| p-value | 1.28e-82 |
| N (tagged subset) | 2,625 |
| Attenuation ratio | 1.0007 |

**Interpretation:** Each unit increase in log(tag_count+1) is associated with a 53.3% increase in expected N_tasks (IRR=1.5332), with a very narrow CI and vanishingly small p-value. The effect is essentially unattenuated by decade fixed effects (attenuation_ratio=1.0007), confirming no decade-tag_count collinearity concern in the tagged subset.

---

## 4. Model Diagnostics

### 4.1 Overdispersion Test (Cameron-Trivedi LR)

| Metric | Value |
|--------|-------|
| LR statistic | 7357.39 |
| p-value | ~0.0 (machine epsilon) |
| NB-2 appropriate | Yes |

CT LR=7357 >> χ²(1, 0.05)=3.84 confirms NB-2 strongly preferred over Poisson. This is consistent with H-E1's CT LR=7356.36 on the full corpus — overdispersion persists in the tagged subset.

### 4.2 Model Convergence

| Model | Converged | LLF | AIC |
|-------|-----------|-----|-----|
| Baseline (controls-only) | Yes (BFGS) | — | — |
| Proposed with C(decade) | Yes (BFGS) | — | — |
| Proposed without C(decade) | Yes (BFGS) | — | — |

All 3 models converged with BFGS optimizer (consistent with H-E1's all-7-model convergence).

### 4.3 Attenuation Analysis

| Model | IRR_P2 | CI_lower | CI_upper |
|-------|--------|----------|----------|
| With C(decade) FE | 1.5332 | 1.4680 | 1.6014 |
| Without C(decade) FE | 1.5343 | 1.4690 | 1.6025 |

Attenuation ratio = 1.5343 / 1.5332 = **1.0007** (0.07% effect absorbed by decade FE). This is negligible — log(tag_count+1) is essentially orthogonal to decade within the tagged subset. Contrast with H-E1's has_tags attenuation_ratio=1.122 (12.2% absorbed). The continuous IV is more robust to decade collinearity than the binary IV.

---

## 5. Subset Characterization

| Property | Value |
|----------|-------|
| N (has_tags=1) | 2,625 |
| Subset of full corpus | 50.3% (2,625/5,217) |
| tag_count: min | 1 |
| Data source | H-E1 preprocessed.parquet |

The tagged subset (N=2,625) meets the minimum sample requirement (>500) with substantial margin.

---

## 6. Scientific Interpretation

H-M2 confirms that the tag-count dose-response mechanism is real and substantial:

- **Binary vs Continuous:** H-E1 established binary has_tags IRR=1.2263. H-M2 finds continuous log(tag_count+1) IRR=1.5332 within the tagged subset — a stronger effect, consistent with a genuine discovery-pathway amplification mechanism.
- **Mechanism support:** Each additional unit in log(tag_count+1) increases expected task count by 53.3%. This supports the search pathway theory: datasets with more tags appear in more search results, leading to higher discovery and task creation rates.
- **Decade FE independence:** Attenuation ratio=1.0007 shows the tag count effect is not confounded by decade. The dose-response reflects a genuine mechanism, not a temporal trend.

---

## 7. Connection to H-E1 / H-M1

| Hypothesis | IV | IRR | Gate |
|------------|----|-----|------|
| H-E1 | has_tags binary (0/1) | 1.2263 | MUST_WORK PASS |
| H-M1 | has_tags binary, decade FE survival | 1.2263 (same) | MUST_WORK PASS |
| H-M2 | log(tag_count+1) on has_tags=1 subset | 1.5332 | SHOULD_WORK PASS |

H-M2 extends H-E1's binary finding to a continuous dose-response, providing stronger mechanistic evidence for the discovery pathway theory.

---

## 8. Code & Outputs

### Pipeline Scripts

| Script | Status |
|--------|--------|
| `code/01_preprocess.py` | ✓ Completed |
| `code/02_fit_models.py` | ✓ Completed |
| `code/03_generate_figures.py` | ✓ Completed |
| `code/04_evaluate_gate.py` | ✓ Completed |
| `code/05_integration_test.py` | ✓ INTEGRATION TEST PASSED |

### Output Files

| File | Status |
|------|--------|
| `results/tagged_subset.parquet` (N=2,625) | ✓ |
| `results/model_results.json` | ✓ |
| `results/primary_results.json` | ✓ |
| `figures/fig1_gate_metrics.png` | ✓ |
| `figures/fig2_tag_count_distribution.png` | ✓ |
| `figures/fig3_partial_regression.png` | ✓ |
| `figures/fig4_attenuation_forest.png` | ✓ |

---

## 9. Routing Decision

**Gate:** SHOULD_WORK → **PASS**

Proceed to **H-M3** (categorical dose-response: tag count bins 0, 1-2, 3-5, 6+). H-M3 prerequisites (H-E1, H-M1, H-M2) are now all satisfied.

---

## 10. Checklist

- [x] Code runs without errors on df_tagged (N=2,625)
- [x] IRR_P2 = 1.5332 ≥ 1.05
- [x] CI_lower_P2 = 1.4680 ≥ 1.05
- [x] p-value = 1.28e-82 < 0.05
- [x] SHOULD_WORK gate PASS
- [x] All 3 models converged (BFGS)
- [x] CT LR test confirms NB-2 appropriate
- [x] Attenuation check complete (ratio=1.0007)
- [x] 4 figures generated at 300 DPI
- [x] Integration test PASSED
- [x] experiment_results.json saved
- [x] primary_results.json saved
