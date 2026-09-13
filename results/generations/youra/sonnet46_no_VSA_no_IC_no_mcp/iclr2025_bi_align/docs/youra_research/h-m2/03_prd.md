# Product Requirements Document: H-M2
# Calibration-Alignment Divergence Gap Verification

**Hypothesis ID:** H-M2
**Type:** MECHANISM (PoC)
**Tier:** FULL (max 30 tasks)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Status:** Phase 3 — Implementation Planning
**Prerequisite:** H-M1 (VALIDATED, PASS — rho=1.000, reversal confirmed, N=10 KL levels)

---

## 1. Executive Summary

H-M2 formalizes the calibration-alignment divergence gap by applying min-max normalization to the RM score from H-M1's validated output, computing the normalized gap (RM_norm − gold_preference), and verifying that the gap is strictly positive at ≥3 high-KL levels (KL > median = 3.75 nats) and grows monotonically with KL budget. The experiment extends H-M1's proxy-gold divergence confirmation (raw units) into normalized [0,1] space, providing a calibration-ready metric for H-M3 regression. No model training required. Pre-computed expected values confirm all gate conditions will be met (n_positive_high_kl=5, rho_gap_kl≈1.000).

---

## 2. Problem Statement

H-M1 confirmed RM score monotone increase and gold preference peak-reversal in raw digitized units. However, the raw RM score (range [0.12, 2.08]) is not directly comparable to gold preference (already in [0,1]). H-M2 tests the MECHANISM formalization: when both proxies are placed on the same [0,1] scale via min-max normalization, does the calibration-alignment divergence gap (RM_norm − gold) become strictly positive at high KL levels and grow monotonically with optimization pressure? Confirming this normalized divergence unlocks H-M3 (OLS scaling law regression on the gap) and establishes the divergence as a well-calibrated measurement artifact of proxy-gold decoupling.

---

## 3. Functional Requirements

### FR-1: Data Ingestion (Reuse H-M1 Output CSV)

- **FR-1.1:** Load `docs/youra_research/h-m1/results/h_m1_divergence_curve.csv`
- **FR-1.2:** Validate required columns present: `kl_budget`, `rm_score`, `gold_preference`
- **FR-1.3:** Validate N=10 rows with no NaN values
- **FR-1.4:** Sort by `kl_budget` ascending before analysis
- **FR-1.5:** Validate RM range is non-degenerate: `rm.max() > rm.min()` (expected: 2.08 > 0.12)

### FR-2: RM Score Normalization

- **FR-2.1:** Apply min-max normalization: `rm_norm = (rm - rm.min()) / (rm.max() - rm.min())`
- **FR-2.2:** Validate `rm_norm` range: all values in [0, 1]; `rm_norm[0] ≈ 0.0`, `rm_norm[-1] ≈ 1.0`
- **FR-2.3:** Store `rm_norm` as numpy array shape `(10,)`
- **FR-2.4:** Record normalization parameters: `rm_min = 0.12`, `rm_max = 2.08`

### FR-3: Calibration-Alignment Divergence Gap Computation

- **FR-3.1:** Compute `gap = rm_norm - gold_preference` (element-wise; shape `(10,)`)
- **FR-3.2:** Identify high-KL levels: `high_kl_mask = kl_budget > np.median(kl_budget)` (threshold ≈ 3.75 nats)
- **FR-3.3:** Extract `gap_high_kl = gap[high_kl_mask]` (expected shape: `(5,)` for KL ∈ {4,5,6,7,8})
- **FR-3.4:** Compute `n_positive_high_kl = np.sum(gap_high_kl > 0)`

### FR-4: Gate Condition Verification

- **FR-4.1 (Primary Gate 1):** Assert `n_positive_high_kl >= 3` — gap strictly positive at ≥3 high-KL levels
- **FR-4.2 (Primary Gate 2):** Compute `rho_gap_kl, p_rho_gap = scipy.stats.spearmanr(kl_budget, gap)` and assert `rho_gap_kl > 0`
- **FR-4.3 (Secondary):** Compute `max_gap = np.max(gap)` and assert `max_gap > 0`
- **FR-4.4 (Secondary):** Compute `mean_gap_high_kl = np.mean(gap_high_kl)` and assert `mean_gap_high_kl > 0`
- **FR-4.5 (Secondary):** Compute `prop_positive = np.mean(gap > 0)` and assert `prop_positive > 0.5`
- **FR-4.6:** H-M2 gate PASS condition: FR-4.1 AND FR-4.2 both satisfied

### FR-5: Visualization

- **FR-5.1 (Mandatory):** Gate metrics bar chart — `n_positive_high_kl` (5) vs threshold (3), `rho_gap_kl` (≈1.0) vs threshold (0), `prop_positive` (0.70) vs threshold (0.5)
- **FR-5.2:** Normalized gap curve — `gap = RM_norm − gold_preference` vs. KL budget; horizontal zero line; shade positive region (KL≥3); annotate max_gap
- **FR-5.3:** Dual-line comparison — RM_norm and gold_preference on same [0,1] y-axis vs. KL budget; annotate crossover point
- **FR-5.4:** Gap growth scatter — gap vs. KL budget with Spearman ρ annotation; high-KL points marked distinctly
- **FR-5.5:** Normalization summary table — raw RM, RM_norm, gold, gap for all 10 KL levels
- **FR-5.6:** Save all figures to `docs/youra_research/h-m2/figures/`

### FR-6: Reporting

- **FR-6.1:** Print structured pass/fail report to stdout with all gate metrics
- **FR-6.2:** Save results to `docs/youra_research/h-m2/results/h_m2_results.json`
- **FR-6.3:** JSON must include: `n_positive_high_kl`, `rho_gap_kl`, `p_rho_gap`, `max_gap`, `mean_gap_high_kl`, `prop_positive`, `gate_pass`, `rm_min`, `rm_max`, `median_kl`, `dataset_n`
- **FR-6.4:** Save normalized data to `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv` with columns: `kl_budget`, `rm_score`, `rm_norm`, `gold_preference`, `gap`
- **FR-6.5:** Exit code 0 if gate passes, 1 if gate fails

### FR-7: H-M2 Gate Check

- **FR-7.1:** PASS condition (both required): `n_positive_high_kl >= 3` AND `rho_gap_kl > 0`
- **FR-7.2:** On FAIL: print diagnostic (which condition failed); if gap negative at high KL, suggest reframing as convergence; check normalization denominator
- **FR-7.3:** Failure response = EXPLORE (recheck normalization; contact authors for raw data if disputed)

---

## 4. Data Specification

### 4.1 Primary Dataset: H-M1 Output CSV

| Field | Value |
|-------|-------|
| Name | Coste2023 RLHF KL-RM-Gold (H-M1 validated output) |
| Source | `docs/youra_research/h-m1/results/h_m1_divergence_curve.csv` |
| Type | Programmatic-api (real published data, previously digitized and validated) |
| Acquisition | Auto-accessible — produced by H-M1 Phase 4 (no manual download) |
| N | 10 KL-level observations |
| Columns | `kl_budget` (float, nats), `rm_score` (float, [0.12, 2.08]), `gold_preference` (float, [0,1]), `divergence_gap` (float, raw) |
| Splits | Single time-series; no train/val/test split |
| Missing values | None (confirmed in H-M1 validation) |

**Loading:**
```python
import pandas as pd
df = pd.read_csv("../../h-m1/results/h_m1_divergence_curve.csv")
# Columns: kl_budget, rm_score, gold_preference, divergence_gap
# N=10 rows, KL range [0, 8] nats
```

**Note:** No manual data acquisition required. H-M1 result file is the sole input.

### 4.2 No Additional Datasets

H-M2 is a normalization + gap analysis on H-M1's validated output. No secondary datasets required.

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Deterministic (no stochastic operations; seed not required) |
| Dependencies | pandas, numpy, scipy, matplotlib |
| Runtime | < 1 second (vectorized numpy on N=10) |
| File organization | All outputs under `docs/youra_research/h-m2/` |
| Python version | ≥3.9 |
| H-M1 dependency | Requires `h-m1/results/h_m1_divergence_curve.csv` to exist |

---

## 6. Success Criteria

| Criterion | Target |
|-----------|--------|
| Code runs without error | Required |
| `n_positive_high_kl >= 3` | PASS (primary gate 1) |
| `rho_gap_kl > 0` | PASS (primary gate 2) |
| `max_gap > 0` | Expected (secondary) |
| `mean_gap_high_kl > 0` | Expected (secondary) |
| `prop_positive > 0.5` | Expected (secondary) |
| All 5 figures generated | Required |
| Results JSON saved | Required |
| `h_m2_normalized_gap.csv` saved | Required |

**H-M2 Gate:** MUST_WORK — if either primary gate condition fails, EXPLORE: recheck normalization range; if gap negative at all high-KL levels, hypothesis may need reframing.

---

## 7. Dependencies

### 7.1 Python Packages

```
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
matplotlib>=3.6.0
```

### 7.2 External Repositories (Reference Only)

| Repo | Purpose |
|------|---------|
| numpy/numpy | Min-max normalization: `(x - x.min()) / (x.max() - x.min())` |
| scipy/scipy | Spearman ρ: `scipy.stats.spearmanr(kl, gap)` |
| matplotlib/matplotlib | Dual-axis and gap visualization |

### 7.3 Reference Papers

| Paper | arXiv | Role |
|-------|-------|------|
| Coste et al. 2023 | 2310.02743 | Source of primary data (via H-M1 digitization) |

### 7.4 H-M1 Dependency

H-M2 builds directly on H-M1:
- Input: `h-m1/results/h_m1_divergence_curve.csv` (RM score + gold preference time-series)
- Normalization parameters derived from H-M1 data (rm_min=0.12, rm_max=2.08)
- Can import data loader from H-M1's `src/analysis/` if available

---

## 8. Out of Scope

- Model training or fine-tuning
- Re-digitization of Coste et al. figures (H-M1 already validated)
- OLS regression / scaling law fitting (reserved for H-M3)
- Cross-scale replication (reserved for H-M4)
- Ablation variants (MECHANISM PoC only)
- Secondary dataset (Gao et al.) analysis — that is H-M4 scope

---

*Applied: MECHANISM PoC template — extends H-M1 raw divergence confirmation with [0,1]-normalized gap formalization*
*Codebase Analysis (Serena): H-M1 code at h-m1/code/ available for import; src/analysis/trajectory.py provides data loading pattern*
