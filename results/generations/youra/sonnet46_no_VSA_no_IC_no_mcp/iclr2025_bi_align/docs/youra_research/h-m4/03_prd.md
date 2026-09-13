# Product Requirements Document: H-M4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 — Cross-dataset OLS Replication (Gao et al. 2023)
**Phase:** 3 — Implementation Planning

---

## 1. Objective

Apply the identical OLS regression pipeline from H-M3 to Gao et al. 2023 (arXiv 2210.10760) digitized data to test whether the calibration-alignment divergence slope (β > 0, p < 0.05) replicates in an independent dataset with a different model family and scale. Gate type: SHOULD_WORK.

---

## 2. Background

H-M3 validated β = 0.1433 (p = 8.89e-07, R² = 0.9577) in Coste et al. 2023 data (N = 10 KL checkpoints). H-M4 tests generalizability by running the same pipeline on Gao et al. 2023 Figure 1 — a different paper, GPT-2 family models, RM sizes up to 3B parameters. If β > 0 and p < 0.05 in Gao et al. data, the calibration-alignment divergence mechanism is confirmed as general to RLHF optimization rather than specific to Coste et al.'s model family.

Failure action: scope claim to Coste et al. only; document as replication caveat. Does NOT block H-BiAlign-v1 paper.

---

## 3. Scope

### In Scope
- Manual digitization of Gao et al. 2023 Figure 1 (6B RM size curves; fallback: mean of 302M–3B) via WebPlotDigitizer v4.6
- Double-digitize protocol (two independent passes, mean per point)
- Min-max normalization identical to H-M2/H-M3 protocol
- OLS regression: scipy.stats.linregress + statsmodels.OLS
- Bootstrap CI: n_boot = 10,000; seed = 42; percentile method
- SHOULD_WORK gate check: β > 0 AND p < 0.05
- Cross-dataset slope comparison: |β_Gao / β_Coste| ∈ [0.1, 10.0]
- 5 figures (1 mandatory gate figure + 4 recommended)
- Results JSON + CSV output
- Validation report (04_validation.md)

### Out of Scope
- Neural network training
- New dataset collection beyond Gao et al. Figure 1 digitization
- Analysis of RM sizes other than 6B (unless 6B curves not clearly separable)
- Modifications to the OLS pipeline (methodological consistency with H-M3 required)

---

## 4. Functional Requirements

### FR-1: Data Acquisition
- Digitize Gao et al. 2023 arXiv 2210.10760 Figure 1 using WebPlotDigitizer v4.6
- Target: 6B RM size proxy RM score and gold human preference curves
- Fallback: mean of 302M–3B RM size curves if 6B not clearly separable
- Double-digitize protocol; mean per point; record deviation as digitization uncertainty
- Precision target: ±3% per point
- Output: `docs/youra_research/h-m4/data/gao_2023_raw.csv` (kl_budget, proxy_raw, gold_raw)

### FR-2: Data Processing
- Apply min-max normalization: `proxy_norm = (proxy_raw - min) / (max - min)`, same for gold
- Compute gap = proxy_norm - gold_norm ∈ [-1, +1]
- Assert N ≥ 6, no NaN, gap.std() > 0.01, kl_budget monotonically increasing
- Output: `docs/youra_research/h-m4/data/gao_2023_gap.csv` (kl_budget, proxy_norm, gold_norm, gap)

### FR-3: OLS Regression
- Run fit_ols_regression(kl_values, gap_values) — reused verbatim from H-M3
- Output: slope β, intercept β₀, R², p-value, SE, t-stat, CI parametric + bootstrap

### FR-4: Gate Evaluation
- Run check_gate(results): β > 0 AND p < 0.05
- Run compare_with_coste(β_Gao, β_Coste=0.1433): ratio within [0.1, 10.0]?
- Emit gate_pass: True/False with reason string

### FR-5: Mechanism Verification
- Run verify_mechanism_activated(results, data_path) — all indicators must pass
- Log all activation indicators to stdout

### FR-6: Visualization
- Generate 5 figures saved to `docs/youra_research/h-m4/figures/`
  - fig1: Gate metrics bar chart (β and p vs thresholds; H-M3 reference bars)
  - fig2: Regression scatter + OLS fit line + 95% CI band for Gao et al. data
  - fig3: Cross-dataset slope comparison bar chart (β_Coste vs β_Gao with 95% CI error bars)
  - fig4: Dual regression overlay (both datasets on single plot)
  - fig5: Bootstrap slope histogram for Gao et al. data

### FR-7: Results Persistence
- Save `docs/youra_research/h-m4/results/h_m4_results.json` with all metrics + gate outcome
- Save processed CSV to `docs/youra_research/h-m4/results/gao_2023_gap_final.csv`
- Print summary table to stdout

---

## 5. Non-Functional Requirements

- **Reproducibility:** Seed = 42 for all random operations; deterministic output
- **Runtime:** < 30 seconds total (digitization is manual; code runs < 5 seconds)
- **Dependencies:** Python 3.10, scipy ≥ 1.10, statsmodels ≥ 0.14, numpy ≥ 1.24, matplotlib ≥ 3.7, pandas ≥ 2.0
- **Environment:** Clone of youra-h-m3 conda environment (or reuse directly)
- **Methodological consistency:** All analysis code functionally identical to H-M3; only input CSV path changes

---

## 6. Acceptance Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| β (slope) | > 0 | Gate (SHOULD_WORK) |
| p-value | < 0.05 | Gate (SHOULD_WORK) |
| Code runs without error | TRUE | Required |
| gao_2023_gap.csv loaded (N ≥ 6) | TRUE | Required |
| verify_mechanism_activated() passes | TRUE | Required |
| 5 figures generated | TRUE | Required |
| h_m4_results.json saved | TRUE | Required |
| |β_Gao / β_Coste| ∈ [0.1, 10.0] | Informational | Secondary |

Failure of gate (β ≤ 0 or p ≥ 0.05): document scope boundary; continue pipeline.

---

## 7. Deliverables

1. `docs/youra_research/h-m4/data/gao_2023_raw.csv` — digitized Gao et al. Figure 1 data
2. `docs/youra_research/h-m4/data/gao_2023_gap.csv` — processed gap data
3. `docs/youra_research/h-m4/code/` — runnable Python package (reusing H-M3 structure)
4. `docs/youra_research/h-m4/figures/` — 5 figures (PNG)
5. `docs/youra_research/h-m4/results/h_m4_results.json` — all metrics
6. `docs/youra_research/h-m4/04_validation.md` — Phase 4 validation report

---

## 8. Implementation Budget

**Tier:** FULL
**Budget:** 25 implementation tasks
**Timeline:** Phase 4 execution (automated)
