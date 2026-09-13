# Product Requirements Document: H-M1
# Cox Proportional Hazards — Diversity Predictor Significance Test

**Hypothesis:** H-M1 — MECHANISM
**Date:** 2026-08-03
**Author:** YouRA Research Pipeline
**Phase:** 3 — Implementation Planning
**Tier:** FULL (max 30 tasks)
**Base Hypothesis:** H-E1 (INCREMENTAL — consumes H-E1 output panel)

---

## 1. Executive Summary

H-M1 tests whether `log_unique_paper_count_at_intro_z` (community breadth diversity at benchmark introduction) significantly predicts plurality-benchmark displacement hazard. The experiment fits two nested Cox Proportional Hazards models on the H-E1 validated panel (`h_e2_panel_with_diversity.csv`, 345 rows, 87 benchmarks), executes a Likelihood Ratio Test (LRT), and interprets the Hazard Ratio (HR) direction. Gate: LRT p < 0.05 AND |HR-1| ≥ 0.10.

---

## 2. Problem Statement

H-E1 validated the data panel and confirmed that `log_unique_paper_count_at_intro_z` is time-independent and has sufficient variance (G1 partial_r²=0.6053, G3 std=0.2462). The research question is whether this diversity predictor causally predicts *when* a plurality-benchmark gets displaced by a new SOTA.

Two competing theoretical directions:
- **H1 (breadth → resistance):** HR < 1.0 → diverse community networks slow displacement
- **H2 (saturation → replacement):** HR > 1.0 → diversity signals overuse, accelerates displacement
- **H0 (null):** p ≥ 0.05 → community breadth does not predict displacement timing

---

## 3. Scope

**In scope:**
- Loading `h_e2_panel_with_diversity.csv` (H-E1 output, 345 rows)
- Fitting CoxPHFitter(penalizer=0.1) for M0 (controls only) and M1 (+ diversity predictor)
- Nested LRT: chi2(df=1) comparison M0 vs M1
- HR extraction with 95% CI for `log_unique_paper_count_at_intro_z`
- Direction interpretation (pre-specified H1/H2/H0 routing)
- Diagnostic: concordance index, PH assumption check (Schoenfeld residuals)
- Visualization (4 figures + 1 mandatory gate bar chart)
- Saving results to `experiment_results.json`

**Out of scope:**
- Re-running H-E1 data pipeline (panel already validated)
- Additional covariates beyond H-E1 schema
- Kaplan-Meier analysis (H-M2)
- Paper writing (Phase 6)

---

## 4. Data Specification

### 4.1 Primary Dataset — H-E1 Output Panel

| Field | Value |
|-------|-------|
| Source | H-E1 output: `docs/youra_research/h-e1/h_e2_panel_with_diversity.csv` |
| Load method | `pd.read_csv(...)` — local file, no download needed |
| Size | 345 rows × 12 columns |
| License | Derived from CC-BY-SA-4.0 (pwc-archive/evaluation-tables) |
| Key columns | `task_path`, `duration`, `event`, `task_age`, `log_publication_volume`, `benchmark_introduction_year`, `log_unique_paper_count_at_intro_z`, `paper_diversity_ratio_at_intro_z` |
| Download | **No download required** — local CSV from H-E1 output |

### 4.2 Column Schema

| Column | Type | Role |
|--------|------|------|
| `duration` | float | Survival time (years from benchmark intro to displacement or censoring) |
| `event` | int (0/1) | 1 = displaced, 0 = censored |
| `task_age` | float | Control covariate |
| `log_publication_volume` | float | Control covariate |
| `benchmark_introduction_year` | float | Control covariate |
| `log_unique_paper_count_at_intro_z` | float | PRIMARY diversity predictor (H-M1) |
| `paper_diversity_ratio_at_intro_z` | float | Secondary diversity predictor (future H-M2) |

### 4.3 No Manual Download Required

The H-E1 panel is a local CSV. No environment setup for dataset acquisition needed.

---

## 5. Functional Requirements

### FR-1: Load and Validate Panel

- Load `docs/youra_research/h-e1/h_e2_panel_with_diversity.csv`
- Assert shape: (345, ≥8 columns)
- Assert required columns exist: `duration`, `event`, `task_age`, `log_publication_volume`, `benchmark_introduction_year`, `log_unique_paper_count_at_intro_z`
- Assert no NaN in analysis columns
- Log: `Panel loaded: {n} rows, {k} columns`

### FR-2: Fit Null Model (M0)

- `M0 = CoxPHFitter(penalizer=0.1)`
- Covariates: `[task_age, log_publication_volume, benchmark_introduction_year]`
- `M0.fit(df[base_cols], duration_col='duration', event_col='event')`
- Extract: `M0.log_likelihood_`
- Log: `M0 fitted: log_likelihood={M0.log_likelihood_:.4f}`

### FR-3: Fit Full Model (M1)

- `M1 = CoxPHFitter(penalizer=0.1)`
- Covariates: M0 covariates + `log_unique_paper_count_at_intro_z`
- `M1.fit(df[full_cols], duration_col='duration', event_col='event')`
- Extract: `M1.log_likelihood_`, `M1.hazard_ratios_`, `M1.confidence_intervals_`, `M1.concordance_index_`

### FR-4: Nested Likelihood Ratio Test

- `lrt_stat = -2 * (M0.log_likelihood_ - M1.log_likelihood_)`
- `p_value = stats.chi2.sf(lrt_stat, df=1)`
- Assert: `M1.log_likelihood_ >= M0.log_likelihood_`
- Log: `LRT stat={lrt_stat:.4f}, p={p_value:.4f}`

### FR-5: Hazard Ratio Extraction

- `HR = float(M1.hazard_ratios_['log_unique_paper_count_at_intro_z'])`
- `CI_lower = float(np.exp(M1.confidence_intervals_.loc['log_unique_paper_count_at_intro_z', 'lower 0.95']))`
- `CI_upper = float(np.exp(M1.confidence_intervals_.loc['log_unique_paper_count_at_intro_z', 'upper 0.95']))`
- `abs_effect = abs(HR - 1.0)`
- Log: `HR={HR:.4f}, CI=[{CI_lower:.4f}, {CI_upper:.4f}], |HR-1|={abs_effect:.4f}`

### FR-6: Gate Evaluation (MUST_WORK)

- PASS condition: `p_value < 0.05 AND abs_effect >= 0.10`
- FAIL condition: `p_value >= 0.05 OR abs_effect < 0.10` (meaningful null, still routes to Phase 6)
- Print gate result clearly with both metric values vs thresholds

### FR-7: Direction Interpretation (Pre-specified)

- `HR < 1.0 AND p < 0.05` → H1: breadth→resistance (Ott 2022)
- `HR > 1.0 AND p < 0.05` → H2: saturation→replacement (Koch 2021)
- `p >= 0.05` → H0: null result (community breadth does not predict displacement)

### FR-8: Diagnostics

- `concordance = M1.concordance_index_` (report, no threshold)
- PH assumption check: `M1.check_assumptions(panel_df, p_value_threshold=0.05, show_plots=False)` — log any violations

### FR-9: Visualization

Required figures (saved to `docs/youra_research/h-m1/figures/`):

| # | Figure | Method | Description |
|---|--------|--------|-------------|
| 1 | Gate metrics bar chart (MANDATORY) | matplotlib | LRT p-value vs 0.05, \|HR-1\| vs 0.10 thresholds |
| 2 | Kaplan-Meier by diversity quartile | lifelines KaplanMeierFitter | Q1 vs Q4 `log_unique_paper_count_at_intro` |
| 3 | Partial effects plot | `M1.plot_partial_effects_on_outcome(...)` | Survival curves across diversity levels [-2,-1,0,1,2] |
| 4 | Forest plot (HR with 95% CI) | matplotlib | All M1 covariates, color by significance |
| 5 | Schoenfeld residuals | `M1.check_assumptions(...)` | PH assumption diagnostic |

### FR-10: Results Serialization

- Save JSON to `docs/youra_research/h-m1/experiment_results.json`:
```json
{
  "hypothesis_id": "H-M1",
  "gate_passed": true/false,
  "lrt_stat": ...,
  "p_value": ...,
  "HR": ...,
  "CI_lower": ...,
  "CI_upper": ...,
  "abs_effect": ...,
  "concordance_M1": ...,
  "M0_log_likelihood": ...,
  "M1_log_likelihood": ...,
  "direction": "H1|H2|H0",
  "timestamp": "..."
}
```

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | ≤ 2 minutes (deterministic MLE on 345 rows) |
| Reproducibility | Deterministic — MLE optimization, no random seed needed |
| Memory | < 500 MB RAM |
| Error handling | Convergence warnings → increase penalizer to 0.5, refit |
| Logging | Print each step result with metric values |
| Failsafe | If NaN in p_value → check panel for NaN, drop rows and refit |

---

## 7. Dependencies

### 7.1 Python Packages

```
lifelines>=0.30.0
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 Internal Dependencies

| Resource | Path | Purpose |
|----------|------|---------|
| H-E1 output panel | `docs/youra_research/h-e1/h_e2_panel_with_diversity.csv` | Primary input dataset |
| H-E1 config | `docs/youra_research/h-e1/code/config.py` | Reference for column names |

### 7.3 External References

| Resource | URL | Purpose |
|----------|-----|---------|
| lifelines CoxPHFitter | https://lifelines.readthedocs.io/en/stable/ | Canonical Cox PH API |
| tooluniverse/cox_regression.md | https://github.com/mims-harvard/tooluniverse | Nested LRT pattern |

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| Code runs without error | lifelines fits M0 and M1 without crash |
| LRT computed | `lrt_stat` and `p_value` are finite floats |
| HR extracted | `HR`, `CI_lower`, `CI_upper` are finite, HR > 0 |
| Gate evaluated | Both thresholds reported (PASS or meaningful null) |
| M1 ≥ M0 | `M1.log_likelihood_ >= M0.log_likelihood_` |
| Figures generated | 5 figures saved to `h-m1/figures/` |
| Results serialized | `experiment_results.json` written |

**PoC Pass:** All 7 criteria satisfied. Gate outcome (PASS or meaningful null) both route to Phase 6.

---

## 9. Phase 2C Completeness Verification

| Phase 2C Item | Covered in PRD |
|---------------|---------------|
| Dataset: h_e2_panel_with_diversity.csv | FR-1, Section 4.1 ✓ |
| M0: CoxPHFitter(penalizer=0.1), controls | FR-2 ✓ |
| M1: M0 + log_unique_paper_count_at_intro_z | FR-3 ✓ |
| Nested LRT (scipy chi2.sf) | FR-4 ✓ |
| HR and 95% CI extraction | FR-5 ✓ |
| Gate: p<0.05 AND \|HR-1\|≥0.10 | FR-6 ✓ |
| Direction interpretation protocol | FR-7 ✓ |
| Concordance + PH assumption check | FR-8 ✓ |
| Visualization (5 figures) | FR-9 ✓ |
| Results JSON serialization | FR-10 ✓ |
| All pip dependencies | Section 7.1 ✓ |
| Failure detection (convergence, NaN) | Section 6 ✓ |
