# Product Requirements Document: H-M1
# RLHF Proxy-Gold Divergence Mechanism Verification

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC)
**Tier:** FULL (max 30 tasks)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Status:** Phase 3 — Implementation Planning
**Prerequisite:** H-E1 (VALIDATED, PASS)

---

## 1. Executive Summary

H-M1 is a statistical re-analysis experiment that verifies the proxy-gold divergence mechanism in RLHF optimization. Using digitized figure data from Coste et al. 2023 (arXiv:2310.02743), the experiment tests whether RM score increases monotonically with KL budget while gold human preference peaks at intermediate KL then reverses. Success requires Spearman ρ(KL, RM) > 0.8 AND reversal_confirmed == True on Coste data, and provides divergence_final as direct input to H-M2. No model training required. Extends H-E1's digitized CSV files with statistical trajectory analysis.

---

## 2. Problem Statement

H-E1 confirmed that both RM score and gold human preference curves co-exist as extractable paired time-series in Coste et al. 2023 and Gao et al. 2023 at ≥5 KL levels each. H-M1 tests the MECHANISM: under sustained RLHF optimization, does the RM score monotonically increase while gold preference peaks then reverses? This trajectory divergence is the core evidence for reward model overoptimization. Confirming it in digitized data unlocks H-M2 (divergence gap quantification) through H-M4 (cross-scale replication).

---

## 3. Functional Requirements

### FR-1: Data Ingestion (Reuse H-E1 CSVs)

- **FR-1.1:** Load `data/coste_digitized.csv` (primary) — same file as H-E1 `coste2023_kl_curves.csv`, expected columns: `kl_budget`, `rm_score`, `gold_preference`
- **FR-1.2:** Load `data/gao_digitized.csv` (secondary/preliminary) — same file as H-E1 `gao2023_kl_curves.csv`
- **FR-1.3:** Validate ≥5 non-null paired rows in primary (Coste) dataset
- **FR-1.4:** Sort by `kl_budget` ascending before analysis
- **FR-1.5:** Extract baseline values: `baseline_rm`, `baseline_gold` from row where `kl_budget` is minimum

### FR-2: RM Monotonicity Test

- **FR-2.1:** Compute Spearman ρ(kl_budget, rm_score) using `scipy.stats.spearmanr`
- **FR-2.2:** PASS condition: `rho > 0.8` AND `p_rho < 0.05`
- **FR-2.3:** Store result: `rho_rm_kl`, `p_rho`

### FR-3: Gold Preference Peak-Reversal Detection

- **FR-3.1:** Find peak index: `peak_idx = np.argmax(gold_preference)`
- **FR-3.2:** Compute `peak_kl = kl_budget[peak_idx]`
- **FR-3.3:** PASS condition: `gold_preference[peak_idx] > gold_preference[-1]` (reversal_confirmed == True)
- **FR-3.4:** Validate `peak_kl` in range [1.0, 9.0] nats (sanity check for digitization error)
- **FR-3.5:** Store result: `peak_idx`, `peak_kl`, `reversal_confirmed`

### FR-4: Divergence Computation (Feed-forward to H-M2)

- **FR-4.1:** Compute `divergence_final = rm_score[-1] - gold_preference[-1]`
- **FR-4.2:** Assert `divergence_final > 0` (sanity: RM exceeds gold at final KL)
- **FR-4.3:** Compute full divergence trajectory: `divergence_curve = rm_score - gold_preference` (aligned; shape: (N,))
- **FR-4.4:** Save divergence trajectory to `results/h_m1_divergence_curve.csv` for H-M2 consumption

### FR-5: Dual Digitization Precision Reporting

- **FR-5.1:** If two independent digitization columns exist (`rm_score_run1`, `rm_score_run2`), compute per-point mean and std, report average ±σ
- **FR-5.2:** Otherwise, report single-digitization with note in results JSON

### FR-6: Visualization

- **FR-6.1:** Generate dual-axis trajectory plot: RM score (left y, steelblue) + gold preference (right y, crimson) vs. KL budget — mark peak KL with vertical dashed line
- **FR-6.2:** Generate divergence gap curve: (RM − gold) vs. KL budget with horizontal zero line
- **FR-6.3:** Generate Spearman scatter: RM score vs. KL budget with monotone trend line and ρ annotation
- **FR-6.4:** Generate Gao preliminary overlay (separate panel): same dual-axis for Gao et al. data
- **FR-6.5:** Generate gate metrics bar chart: `rho_rm_kl`, `reversal_confirmed` (0/1), `divergence_final` vs. thresholds
- **FR-6.6:** Save all figures to `docs/youra_research/h-m1/figures/`

### FR-7: Reporting

- **FR-7.1:** Print structured pass/fail report to stdout including all gate metrics
- **FR-7.2:** Save results to `docs/youra_research/h-m1/results/h_m1_results.json`
- **FR-7.3:** JSON must include: `rho_rm_kl`, `p_rho`, `reversal_confirmed`, `peak_kl`, `divergence_final`, `gate_pass`, `dataset_n`, `baseline_rm`, `baseline_gold`
- **FR-7.4:** Save `results/h_m1_divergence_curve.csv` with columns: `kl_budget`, `rm_score`, `gold_preference`, `divergence_gap`
- **FR-7.5:** Exit code 0 if gate passes, 1 if gate fails

### FR-8: H-M1 Gate Check

- **FR-8.1:** PASS condition (both required): `rho_rm_kl > 0.8` AND `reversal_confirmed == True`
- **FR-8.2:** On FAIL: print diagnostic (which condition failed + suggested action)
- **FR-8.3:** Failure response = EXPLORE (re-digitize figure; if still fails, request raw data from authors)

---

## 4. Data Specification

### 4.1 Primary Dataset: Coste et al. 2023 (Digitized)

| Field | Value |
|-------|-------|
| Name | Coste2023 RLHF KL-budget curves |
| Source | arXiv:2310.02743, Figures 3–4 |
| Extraction Method | WebPlotDigitizer (manual, browser-based); 2× per figure, mean reported |
| Expected rows | ≥5 |
| Columns | kl_budget (float), rm_score (float), gold_preference (float) |
| Precision | ±2–5% per point |
| Storage path | `data/coste_digitized.csv` |
| Acquisition | **Manual — Phase 4 human action required** |

### 4.2 Secondary Dataset: Gao et al. 2023 (Digitized, Preliminary)

| Field | Value |
|-------|-------|
| Name | Gao2023 RLHF overoptimization curves |
| Source | arXiv:2210.10760, Figure 2 |
| Extraction Method | WebPlotDigitizer |
| Expected rows | ≥5 |
| Columns | kl_budget, rm_score, gold_preference |
| Storage path | `data/gao_digitized.csv` |
| Role in H-M1 | Preliminary pattern check only; primary regression in H-M4 |

### 4.3 Data Acquisition Steps (Manual — Phase 4 human action required)

1. Download PDFs: arXiv:2310.02743 (Coste), arXiv:2210.10760 (Gao)
2. Export Figures 3–4 (Coste) and Figure 2 (Gao) as 300+ DPI PNG
3. Open WebPlotDigitizer, calibrate axes for each figure
4. Digitize RM score curve, then gold preference curve per figure (2 independent passes each)
5. Export merged CSV: kl_budget, rm_score, gold_preference (mean of 2 passes)
6. Place at `data/coste_digitized.csv` and `data/gao_digitized.csv`

**Note:** If H-E1 data files exist at `data/coste2023_kl_curves.csv` / `data/gao2023_kl_curves.csv`, H-M1 may symlink or copy them to `data/coste_digitized.csv` / `data/gao_digitized.csv`.

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Deterministic (seed=1, no stochastic ops) |
| Dependencies | pandas, numpy, scipy, matplotlib |
| Runtime | < 30 seconds (pure statistical computation on N ≤ 20 points) |
| File organization | All outputs under `docs/youra_research/h-m1/` |
| Python version | ≥3.9 |
| H-E1 reuse | Load same CSV files; do not re-digitize if already present |

---

## 6. Success Criteria

| Criterion | Target |
|-----------|--------|
| Code runs without error | Required |
| `rho_rm_kl > 0.8` in Coste data | PASS (gate condition 1) |
| `reversal_confirmed == True` in Coste data | PASS (gate condition 2) |
| `p_rho < 0.05` | PASS (significance) |
| `divergence_final > 0` | Expected (sanity) |
| `peak_kl` in [1.0, 9.0] nats | Expected (sanity) |
| All 5 figures generated | Required |
| Results JSON saved | Required |
| `h_m1_divergence_curve.csv` saved for H-M2 | Required |

**H-M1 Gate:** MUST_WORK — if either gate condition fails, EXPLORE: re-digitize; if confirmed no reversal, request raw data from Coste et al. authors.

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
matplotlib>=3.6.0
```

### 7.2 External Tools / Repositories

| Tool | URL | Purpose |
|------|-----|---------|
| WebPlotDigitizer | https://automeris.io/WebPlotDigitizer | Figure digitization |

### 7.3 Reference Papers

| Paper | arXiv | Role |
|-------|-------|------|
| Coste et al. 2023 | 2310.02743 | Primary dataset; mechanism definition |
| Gao et al. 2023 | 2210.10760 | Preliminary secondary check |

### 7.4 H-E1 Dependency

H-M1 builds directly on H-E1:
- Reuses digitized CSV files (`data/coste_digitized.csv`, `data/gao_digitized.csv`)
- Extends analysis: H-E1 verified co-existence; H-M1 verifies trajectory pattern
- Code can import from H-E1's `src/data/loader.py` for CSV loading

---

## 8. Out of Scope

- Model training or fine-tuning
- Re-running RLHF experiments from scratch
- OLS regression / scaling law fitting (reserved for H-M3)
- Cross-scale replication (reserved for H-M4)
- Ablation variants (MECHANISM PoC only)
- Author raw data request (fallback only, not primary path)

---

*Applied: MECHANISM PoC template — extends EXISTENCE foundation with statistical trajectory analysis*
*Codebase Analysis (Serena): Base code at h-e1/code/ available for import; src/data/loader.py reused*
