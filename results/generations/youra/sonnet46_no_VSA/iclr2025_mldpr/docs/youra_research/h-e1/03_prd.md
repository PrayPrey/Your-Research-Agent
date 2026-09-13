# Product Requirements Document: H-E1
# Data Pipeline Validation & FAIL FAST Gate Verification

**Hypothesis:** H-E1 — EXISTENCE (PoC)
**Date:** 2026-08-03
**Author:** YouRA Research Pipeline
**Phase:** 3 — Implementation Planning
**Tier:** LIGHT (max 15 tasks)

---

## 1. Executive Summary

H-E1 validates the data pipeline that constructs the enriched survival-analysis panel used by downstream hypotheses (H-M1, H-M2, H-R1). It implements five sequential FAIL FAST gates (G0–G4) that confirm dataset joinability, predictor time-independence, diversity variance sufficiency, and covariate collinearity. All five gates must pass; failure at any gate halts the pipeline.

---

## 2. Problem Statement

The YouRA diversity research hypothesizes that paper diversity at benchmark introduction explains plurality-displacement survival. Before any Cox regression, the input data must satisfy five preconditions:

- **G0** — the pwc-archive/evaluation-tables dataset joins to ≥80% of the 87 h-e2 benchmarks
- **G1/G2** — both diversity predictors are time-independent (partial_r² > 0.01 after removing temporal confounds)
- **G3** — diversity ratio has sufficient cross-benchmark variance (std > 0.10)
- **G4** — all Cox covariates are below the collinearity exclusion threshold (VIF < 10)

Failure to validate any gate would invalidate downstream survival analysis.

---

## 3. Scope

**In scope:**
- Loading `pwc-archive/evaluation-tables` via HuggingFace datasets API
- Fuzzy-joining `task_path` to h-e2 panel (87 benchmarks, threshold=85 token_sort_ratio)
- Computing per-benchmark diversity aggregates and z-standardized predictors
- Executing gates G0–G4 in order, stopping on first failure
- Collinearity failsafe: Pearson r(log_count_z, diversity_ratio_z) > 0.95 → single predictor
- Saving enriched panel as `h_e2_panel_with_diversity.csv`
- Generating visualization figures

**Out of scope:**
- Cox regression fitting (H-M1)
- Kaplan-Meier analysis (H-M2)
- Baseline comparison (Phase 5)

---

## 4. Data Specification

### 4.1 Primary Dataset — pwc-archive/evaluation-tables

| Field | Value |
|-------|-------|
| Source | HuggingFace: `pwc-archive/evaluation-tables` |
| Load method | `load_dataset("pwc-archive/evaluation-tables", split="train")` |
| Size | 2,254 rows (benchmark-level), 138 MB, parquet |
| License | CC-BY-SA-4.0 |
| Key columns | `task_path`, `dataset`, `model_name`, `paper_url`, `metric_name`, `metric_value` |
| Download | **Auto-download via HF datasets API** — no manual download task needed |

### 4.2 Internal Panel — h-e2 Panel

| Field | Value |
|-------|-------|
| Source | Pipeline-internal (constructed from Phase 2B) |
| Size | 87 tasks, 345 plurality-displacement events, 2015–2023 |
| Columns | `task_path`, `duration`, `event`, `task_age`, `log_publication_volume`, `benchmark_introduction_year` (= `intro_year`) |
| Availability | Provided by pipeline; NOT downloaded |

**Note:** The h-e2 panel is an internal artifact. Phase 4 must either construct it from raw data or load from a saved CSV. The experiment brief specifies it as "provided by pipeline" — implementation must generate or load `h_e2_panel.csv`.

### 4.3 Output Artifact

| Field | Value |
|-------|-------|
| File | `h_e2_panel_with_diversity.csv` |
| Location | `h-e1/` experiment output directory |
| Columns added | `log_unique_paper_count_at_intro_z`, `paper_diversity_ratio_at_intro_z`, `paper_diversity_ratio_at_intro` |

---

## 5. Functional Requirements

### FR-1: Dataset Loading

- Load `pwc-archive/evaluation-tables` via HuggingFace datasets API
- Convert to pandas DataFrame
- Verify columns: `task_path`, `paper_url` must exist

### FR-2: Fuzzy Join

- Join `eval_df.task_path` → `h_e2_panel.task_path` using rapidfuzz `token_sort_ratio`
- Threshold: score ≥ 85 → matched; below → unmatched (None)
- Map all 2,254 eval rows to their matched h-e2 benchmark

### FR-3: Temporal Filtering

- Filter to rows where `pub_year ≤ intro_year` (paper published before/at benchmark introduction)
- `pub_year` extracted from `paper_url` or metadata if available; fallback: use all rows

### FR-4: Per-Benchmark Diversity Aggregation

For each matched benchmark:
- `unique_paper_count = nunique(paper_url)`
- `total_rows = count(paper_url)`
- `diversity_ratio = unique_paper_count / total_rows`
- `log_unique_count = log1p(unique_paper_count)`
- Z-standardize: `log_unique_paper_count_at_intro_z`, `paper_diversity_ratio_at_intro_z`

### FR-5: Gate G0 — Coverage

- `n_matched = len(benchmarks with ≥1 non-null paper_url after join)`
- `coverage = n_matched / 87`
- PASS: coverage ≥ 0.80; FAIL → STOP with error message and gate metrics log

### FR-6: Gate G1 — Log-Count Time Independence

- OLS: regress `log_unique_paper_count_at_intro_z` on `[task_age, intro_year]`
- `partial_r² = 1 - rsquared_of_OLS`
- PASS: partial_r² > 0.01; FAIL → STOP

### FR-7: Gate G2 — Diversity Ratio Time Independence

- OLS: regress `paper_diversity_ratio_at_intro_z` on `[task_age, intro_year]`
- `partial_r² = 1 - rsquared_of_OLS`
- PASS: partial_r² > 0.01; FAIL → STOP

### FR-8: Gate G3 — Diversity Variance

- `std_val = std(paper_diversity_ratio_at_intro)` across matched benchmarks
- PASS: std_val > 0.10; FAIL → STOP

### FR-9: Gate G4 — VIF Collinearity Check

- Covariate matrix: `[log_unique_paper_count_at_intro_z, paper_diversity_ratio_at_intro_z, task_age, log_publication_volume, intro_year]`
- Compute VIF for each covariate using `statsmodels.stats.outliers_influence.variance_inflation_factor`
- Warn if any VIF ∈ [5, 10); FAIL → STOP if any VIF ≥ 10

### FR-10: Collinearity Failsafe

- Compute Pearson r between `log_unique_paper_count_at_intro_z` and `paper_diversity_ratio_at_intro_z`
- If |r| > 0.95 → log warning: "High collinearity detected, H-M1 should use single predictor only"

### FR-11: Output Artifact

- Merge computed diversity columns back to h-e2 panel
- Save enriched DataFrame as `h_e2_panel_with_diversity.csv`

### FR-12: Visualization

Required figures (saved to `h-e1/figures/`):
1. **Gate metrics bar chart** — each gate's actual value vs. threshold; green=pass, red=fail
2. **Coverage heatmap** — matched vs. unmatched h-e2 task_paths
3. **Predictor distributions** — histograms of `log_unique_paper_count_at_intro` and `paper_diversity_ratio_at_intro`
4. **Correlation matrix** — Pearson r between all Cox covariates
5. **Partial R² bar chart** — G1 and G2 partial_r² vs. 0.01 threshold

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Runtime | ≤ 10 minutes (HF download + fuzzy matching) |
| Reproducibility | Deterministic — no stochastic elements; seed=1 for any random operations |
| Memory | < 4 GB RAM for 2,254 row dataset |
| Error handling | Gate failures must print gate metrics before stopping |
| Logging | Print gate result (PASS/FAIL + value) for each gate |

---

## 7. Dependencies

### 7.1 Python Packages

```
datasets>=2.0.0
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.7.0
statsmodels>=0.14.0
lifelines>=0.30.0
rapidfuzz>=3.0.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### 7.2 External Repositories / References

| Resource | URL | Purpose |
|----------|-----|---------|
| pwc-archive/evaluation-tables | https://huggingface.co/datasets/pwc-archive/evaluation-tables | Primary dataset |
| lifelines CoxPHFitter | https://lifelines.readthedocs.io/en/latest/ | G4 VIF protocol |
| statsmodels VIF | https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html | G4 implementation |

---

## 8. Success Criteria

| Criterion | Condition |
|-----------|-----------|
| Code runs without error | All Python executes cleanly |
| G0 passes | coverage ≥ 0.80 |
| G1 passes | partial_r²(log_count_z) > 0.01 |
| G2 passes | partial_r²(diversity_ratio_z) > 0.01 |
| G3 passes | std(diversity_ratio) > 0.10 |
| G4 passes | max(VIF) < 10 |
| Output written | `h_e2_panel_with_diversity.csv` with non-null diversity columns for ≥80% benchmarks |
| Figures generated | 5 figures saved to `h-e1/figures/` |

**PoC Pass:** All 8 criteria satisfied.

---

## 9. Phase 2C Completeness Verification

| Phase 2C Item | Covered in PRD |
|---------------|---------------|
| Dataset: pwc-archive/evaluation-tables | FR-1 ✓ |
| Fuzzy join (threshold=85) | FR-2 ✓ |
| G0 coverage gate | FR-5 ✓ |
| G1 partial_r² gate | FR-6 ✓ |
| G2 partial_r² gate | FR-7 ✓ |
| G3 std gate | FR-8 ✓ |
| G4 VIF gate | FR-9 ✓ |
| Collinearity failsafe | FR-10 ✓ |
| Output artifact | FR-11 ✓ |
| Visualization (5 figures) | FR-12 ✓ |
| h-e2 panel (internal) | Section 4.2 ✓ |
| All pip dependencies | Section 7.1 ✓ |
