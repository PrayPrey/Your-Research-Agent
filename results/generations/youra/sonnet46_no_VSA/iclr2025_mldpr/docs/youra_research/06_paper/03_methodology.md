# 3. Methodology

## 3.1 Dataset: h-e2 Survival Panel

Our analysis is based on the **h-e2 panel**, a validated survival dataset constructed from Papers With Code (PWC). The panel covers 87 parent tasks from the Koch et al. [CITATION:Koch2021] 87-task taxonomy, spanning 2015–2023. Each row corresponds to a benchmark that achieved plurality status (highest SOTA score for its task) at some point in the observation window. The outcome variable is *plurality benchmark displacement*: the event where a different benchmark achieves plurality for the same task.

**Panel statistics:**
- Rows: 345 (benchmark-level observations)
- Tasks: 87
- Temporal window: 2015–2023
- Event rate: 100% (all plurality benchmarks are subject to displacement risk)
- Panel source: pwc-archive (CC-BY-SA-4.0), validated across 10 prior pipeline attempts (14/14 unit tests pass)

**Survival variables:**
- `duration`: years the benchmark held plurality status
- `event`: 1 if displaced (different benchmark achieved plurality for same task), 0 if right-censored

**Baseline covariates:**
- `task_age`: age of the parent task at benchmark introduction year (years since task first appeared in PWC)
- `log_publication_volume`: log of total paper count for the parent task (controls for task popularity)
- Note: `benchmark_introduction_year` is excluded from Cox models due to perfect collinearity with `task_age` (|r| = 1.000); this was detected and handled automatically by the VIF gate (G4).

## 3.2 Diversity Predictor Construction

We construct diversity predictors from **pwc-archive/evaluation-tables** (HuggingFace, CC-BY-SA-4.0, 326k rows after PyArrow flattening of nested list structure). The key field is `paper_url`, which identifies distinct paper submissions per benchmark.

**Primary predictor:** `log_unique_paper_count_at_intro_z`
- For each benchmark, count distinct `paper_url` values submitted through the plurality introduction year: `unique_count = df.groupby('task_path')['paper_url'].nunique()`
- Apply log1p transformation to reduce right skew
- Z-standardize across the 87-task panel
- Interpretation: breadth of community participation (unique papers) at the benchmark's introduction year

**Secondary predictor:** `paper_diversity_ratio_at_intro_z`
- `diversity_ratio = unique_paper_count_at_intro / total_evaluation_table_rows_at_intro`
- Normalizes by total submission volume, removing the time-accumulation effect
- Z-standardized across benchmarks

**Join procedure:** Task paths in evaluation-tables are matched to h-e2 panel benchmark identifiers using fuzzy matching (rapidfuzz `token_sort_ratio`, threshold = 85), achieving 86.2% coverage (75/87 benchmarks matched). Collinearity between predictors: Pearson r(log_count_z, diversity_ratio_z) = −0.324 — independent constructs, no collinearity failsafe needed.

## 3.3 5-Gate FAIL FAST Pre-Validation Protocol

A key methodological contribution is the **FAIL FAST protocol** (H-E1), which validates data quality *before* any Cox regression. Gates are evaluated in order; failure at any gate routes to Attempt 12 (hypothesis revision). The protocol prevents the scenario observed in prior attempts where a Cox regression runs on a predictor that is effectively a temporal proxy.

| Gate | Name | Criterion | Value | Status |
|------|------|-----------|-------|--------|
| G0 | Join Coverage | ≥ 80% h-e2 benchmarks with non-null paper_url after join | 0.862 | PASS |
| G1 | Primary Time-Independence | partial r²(log_count_z ~ [task_age, intro_year]) > 0.01 | 0.605 | PASS |
| G2 | Secondary Time-Independence | partial r²(diversity_ratio_z ~ [task_age, intro_year]) > 0.01 | 0.975 | PASS |
| G3 | Variance | std(paper_diversity_ratio_at_intro) > 0.10 | 0.246 | PASS |
| G4 | Multicollinearity | max VIF < 10 for active covariates | 2.14 | PASS |

**Partial R² computation:** For gate G1, we regress `log_unique_paper_count_at_intro_z` on `[task_age, benchmark_introduction_year]` via OLS and take the R² of residuals. A partial R² >> 0.01 indicates the predictor retains substantial information beyond temporal trend — ruling out the time-proxy collapse that invalidated prior attempts.

All five gates pass by wide margins (see Figure 1). The partial R² values of 0.605 (G1) and 0.975 (G2) indicate that both diversity predictors are strongly time-independent — containing genuine cross-benchmark information that is not simply a proxy for how recently the benchmark was introduced.

## 3.4 Cox Proportional Hazards Model

We use **CoxPHFitter(penalizer=0.1)** from the lifelines library [CITATION:Davidson-Pilon2019] for all Cox regressions. The L2 penalizer achieves clean convergence (validated across 14/14 unit tests on the h-e2 panel).

**Model M0 (null/baseline):**

`h(t) = h₀(t) · exp(β₁·task_age + β₂·log_publication_volume)`

**Model M1 (diversity predictor added):**

`h(t) = h₀(t) · exp(β₁·task_age + β₂·log_publication_volume + β₃·log_unique_paper_count_at_intro_z)`

**Likelihood Ratio Test (LRT):** LRT statistic = −2 · (ℓ(M0) − ℓ(M1)), df = 1; p-value from chi-squared distribution. Tests whether adding the diversity predictor significantly improves model fit.

**Success criteria (pre-specified, no post-hoc modification):**
- P1 (primary): LRT p < 0.05 AND |HR−1| ≥ 0.10
- P2 (secondary): 95% CI of HR excludes 1.0
- P3 (secondary): Kaplan-Meier Q1 vs Q4 log-rank p < 0.05

**Direction interpretation protocol (pre-specified to prevent HARKing):**
- HR < 1.0, p < 0.05 → H1 lock-in mechanism
- HR > 1.0, p < 0.05 → H2 saturation mechanism
- p > 0.05 (conditional on G0–G4 pass) → H0 null: community-breadth predictor class ruled out

**Complete-case analysis:** 87 of 345 rows dropped due to NaN in analysis columns (primarily 12 unmatched benchmarks from fuzzy join + additional NaN propagation). Final analysis: 258 complete-case rows, EPV (events-per-variable) ≈ 86, providing adequate statistical power to detect |HR−1| ≥ 0.10 at α = 0.05.
