# Product Requirements Document: H-E1
# RLHF Dual-Signal Co-existence Verification

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Tier:** LIGHT (max 15 tasks)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Status:** Phase 3 — Implementation Planning

---

## 1. Executive Summary

H-E1 is a data re-analysis experiment that verifies whether RM (reward model) score and held-out gold human preference co-exist as separable time-series in the same published RLHF datasets. The experiment digitizes published figures from Coste et al. 2023 and Gao et al. 2023, then programmatically confirms both signals are present at ≥5 KL divergence levels in each dataset. No model training is required. Success unblocks the downstream mechanism hypotheses H-M1 through H-M4.

---

## 2. Problem Statement

RLHF overoptimization research (Coste et al. 2023, Gao et al. 2023) tracks both proxy reward (RM score) and gold human preference across KL budget levels. Before designing mechanism tests (H-M1–H-M4), we must confirm these two signals co-exist as extractable, paired time-series in ≥2 independent published datasets. If digitization fails or only one signal is recoverable, downstream hypotheses must pivot to author data requests.

---

## 3. Functional Requirements

### FR-1: Data Ingestion — Coste et al. 2023

- **FR-1.1:** Load `data/coste2023_kl_curves.csv` produced by WebPlotDigitizer from arXiv:2310.02743 Figure 1
- **FR-1.2:** Required columns: `kl_budget` (float), `rm_score` (float), `gold_preference` (float)
- **FR-1.3:** Validate ≥5 non-null paired rows exist
- **FR-1.4:** Validate `rm_score` and `gold_preference` each have range > 0.01 (non-constant signal)

### FR-2: Data Ingestion — Gao et al. 2023

- **FR-2.1:** Load `data/gao2023_kl_curves.csv` produced by WebPlotDigitizer from arXiv:2210.10760 main reward-vs-KL figure
- **FR-2.2:** Required columns: same as FR-1.2
- **FR-2.3:** Validate ≥5 non-null paired rows
- **FR-2.4:** Same variation check as FR-1.4

### FR-3: Co-existence Verification

- **FR-3.1:** Implement `verify_signal_coexistence(df, dataset_name) -> dict` as specified in 02c_experiment_brief.md
- **FR-3.2:** Return dict with keys: `dataset`, `passed`, `n_kl_levels`, `rm_variation`, `gold_variation`, `gate_satisfied`
- **FR-3.3:** H-E1 PASS condition: both `result_coste["passed"]` and `result_gao["passed"]` are True

### FR-4: Visualization

- **FR-4.1:** Generate dual-axis time-series plot per dataset (KL on x; RM score left y, gold preference right y)
- **FR-4.2:** Generate side-by-side comparison figure (mandatory gate metrics figure)
- **FR-4.3:** Save all figures to `docs/youra_research/h-e1/figures/`

### FR-5: Reporting

- **FR-5.1:** Print structured pass/fail report to stdout
- **FR-5.2:** Save results to `docs/youra_research/h-e1/results/h_e1_results.json`
- **FR-5.3:** Include per-dataset details: n_kl_levels, rm_variation, gold_variation, passed

---

## 4. Data Specification

### 4.1 Primary Dataset: Coste et al. 2023

| Field | Value |
|-------|-------|
| Name | Coste2023 RLHF KL-budget curves |
| Source | arXiv:2310.02743, Figure 1 |
| Extraction Method | WebPlotDigitizer (manual, browser-based) |
| Expected rows | ≥5 |
| Columns | kl_budget, rm_score, gold_preference |
| Precision | ±5% of axis range per point |
| Storage path | `data/coste2023_kl_curves.csv` |

### 4.2 Secondary Dataset: Gao et al. 2023

| Field | Value |
|-------|-------|
| Name | Gao2023 RLHF overoptimization curves |
| Source | arXiv:2210.10760, main reward-vs-KL figure |
| Extraction Method | WebPlotDigitizer (manual, browser-based) |
| Expected rows | ≥5 |
| Columns | kl_budget, rm_score, gold_preference |
| Precision | ±5% |
| Storage path | `data/gao2023_kl_curves.csv` |

### 4.3 Data Acquisition Steps (Manual — Phase 4 human action required)

1. Download PDFs: arXiv:2310.02743, arXiv:2210.10760
2. Export target figures as 300+ DPI PNG
3. Open WebPlotDigitizer (https://automeris.io/WebPlotDigitizer), calibrate axes
4. Digitize RM score curve → save, then gold preference curve → save
5. Export merged CSV with columns: kl_budget, rm_score, gold_preference
6. Place files at `data/coste2023_kl_curves.csv` and `data/gao2023_kl_curves.csv`

**Note:** Auto-download not possible — data comes from published figures, not public APIs.

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Deterministic (seed=1, no stochastic ops) |
| Dependencies | pandas, numpy, matplotlib only |
| Runtime | < 5 seconds (no model inference) |
| File organization | All outputs under `docs/youra_research/h-e1/` |
| Python version | ≥3.9 |

---

## 6. Success Criteria

| Criterion | Target |
|-----------|--------|
| Code runs without error | Required |
| Coste2023: both signals present, ≥5 KL levels | PASS |
| Gao2023: both signals present, ≥5 KL levels | PASS |
| Visualization generated | Required |
| Results JSON saved | Required |

**H-E1 Gate:** MUST_WORK — if either dataset fails, contact authors for raw data and reassess scope before H-M1.

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
```

### 7.2 External Tools / Repositories

| Tool | URL | Purpose |
|------|-----|---------|
| WebPlotDigitizer | https://automeris.io/WebPlotDigitizer | Figure digitization |
| openai/lm-human-preferences | https://github.com/openai/lm-human-preferences | Fallback raw data source |

### 7.3 Reference Papers

| Paper | arXiv | Role |
|-------|-------|------|
| Coste et al. 2023 | 2310.02743 | Primary dataset source |
| Gao et al. 2023 | 2210.10760 | Secondary dataset source |

---

## 8. Out of Scope

- Model training or fine-tuning
- Re-running RLHF experiments from scratch
- Statistical significance testing beyond co-existence check
- Ablation variants (EXISTENCE PoC only)

---

*Applied: EXISTENCE PoC template — minimal scope, binary success criterion*
*Codebase Analysis (Serena): Skipped — no existing code to analyze (green-field data extraction pipeline)*
