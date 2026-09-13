# Product Requirements Document: H-M1 - Community Engagement Correlation Study

**Date:** 2026-07-12  
**Hypothesis:** H-M1 (MECHANISM - INCREMENTAL)  
**Author:** Anonymous  
**Status:** DRAFT v1.0  

---

## Executive Summary

### Purpose

Implement an observational correlation study to test whether repository community engagement metrics (commits/month, contributors, issue responsiveness) positively correlate with documentation quality (DCS_3), investigating the mechanism behind the documentation gap identified in H-E1.

### Hypothesis Statement

Repository community engagement (commits/month, contributors, issue responsiveness) positively correlates with documentation quality (DCS_3) with Spearman ρ ≥ 0.30 (p < 0.05), demonstrating that documentation gaps arise from lack of community pressure rather than framework inadequacy.

### Success Criteria (SHOULD_WORK Gate)

- **Primary:** Spearman ρ (commits_per_month vs DCS_3) ≥ 0.30 AND p < 0.05 (one-tailed)
- **Secondary:** Partial correlation (age-controlled) ρ ≥ 0.25 AND p < 0.05
- **Quality Gate:** Data collection success rate ≥ 95% (≥95/100 repositories with complete metrics)

### Scope

**In Scope:**
- Reuse N=100 repositories from H-E1 (same sample, matched analysis)
- GitHub activity metrics collection (commits, contributors, issue response time)
- Spearman rank correlation analysis (activity vs DCS_3)
- Partial correlation analysis (controlling for repository age)
- Bootstrap confidence intervals for ρ estimates
- Scatter plots and correlation matrices

**Out of Scope:**
- Causal inference or intervention testing (observational study only)
- Predictive modeling or machine learning
- Longitudinal tracking beyond T0+90 window
- Alternative documentation quality metrics beyond DCS_3

---

## Problem Statement

### Background

H-E1 validated that ≤40% of ML dataset repositories achieve adequate documentation quality (DCS_3 ≥ 2.4) within 90 days, confirming a significant framework-to-practice gap. However, the MECHANISM driving this gap remains unknown. Two competing explanations exist:

1. **Community Pressure Mechanism:** Active repositories with high engagement produce better documentation (testable via correlation)
2. **Framework Inadequacy:** Standardized frameworks are too complex or poorly designed (alternative mechanism)

### Core Problem

Without identifying the mechanism, interventions cannot be targeted effectively:
- If community pressure drives quality → Solution: Incentivize community engagement
- If framework design is inadequate → Solution: Redesign documentation frameworks

H-M1 tests the community pressure mechanism via correlation analysis.

### Research Gap

**Novel Contribution:**
- First study to quantify correlation between early-stage activity metrics (T0-T90) and documentation quality at T0+90
- Matched sample design (reuses H-E1 repositories) eliminates confounding from repository heterogeneity
- Partial correlation to control for repository age (maturity confounder)

---

## Functional Requirements

### FR-1: Load H-E1 DCS_3 Scores

**Priority:** P0 (Critical)  
**Complexity:** Low  

**Description:**  
Load documentation quality scores (DCS_3) from H-E1 validation results for matched sample analysis.

**Acceptance Criteria:**
- Read H-E1 validation results file: `../h-e1/validation_results.csv`
- Extract columns: `repo_id`, `dcs_3_score`, `t0_date`
- Verify N=100 repositories loaded
- Validate DCS_3 scores in range [0, 3]

**Dependencies:**
- pandas for CSV loading

**Inputs:**
- `../h-e1/validation_results.csv`

**Outputs:**
- DataFrame with columns: `repo_id`, `dcs_3_score`, `t0_date`

---

### FR-2: GitHub API Client Initialization

**Priority:** P0 (Critical)  
**Complexity:** Low  

**Description:**  
Initialize authenticated GitHub API client using PyGitHub library with proper rate limit handling.

**Acceptance Criteria:**
- Load GitHub Personal Access Token from environment variable (`GITHUB_ACCESS_TOKEN`)
- Initialize `Github()` client with token
- Verify authentication: `client.get_rate_limit()` succeeds
- Implement exponential backoff retry for rate limit errors

**Dependencies:**
- PyGitHub library
- Environment variable: `GITHUB_ACCESS_TOKEN`

**Inputs:**
- GitHub token (environment variable)

**Outputs:**
- Authenticated `Github` client object

**Risk Mitigation:**
- Rate limit: 5000 requests/hour (sufficient for ~100 repos × 5 API calls/repo)
- Implement sleep(60) if rate limit approached

---

### FR-3: Collect Commits Per Month Metric

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
For each repository, count commits in the T0 to T0+90 window and calculate average commits per month.

**Acceptance Criteria:**
- For each repo_id from H-E1:
  - Retrieve commits using `repo.get_commits(since=t0, until=t0+90d)`
  - Count total commits in window
  - Calculate `commits_per_month = total_commits / 3` (90 days = 3 months)
- Handle API errors gracefully (mark as missing data if fails)
- Store result in DataFrame column: `commits_per_month`

**Dependencies:**
- PyGitHub `repo.get_commits()`
- t0_date from H-E1

**Inputs:**
- Repository list with `repo_id`, `t0_date`

**Outputs:**
- DataFrame with added column: `commits_per_month`

---

### FR-4: Collect Unique Contributors Metric

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
For each repository, count unique contributors (distinct commit authors) in the T0 to T0+90 window.

**Acceptance Criteria:**
- For each repo_id:
  - Retrieve commits in T0-T90 window (reuse from FR-3 if possible)
  - Extract unique author logins: `set(c.author.login for c in commits if c.author)`
  - Count unique contributors: `unique_contributors = len(author_set)`
- Handle None authors gracefully (exclude from set)
- Store result in column: `unique_contributors`

**Dependencies:**
- PyGitHub commit.author attribute
- Commits already fetched in FR-3

**Inputs:**
- Commits list from FR-3

**Outputs:**
- DataFrame with added column: `unique_contributors`

---

### FR-5: Collect Median Issue Response Time Metric

**Priority:** P1 (Required for comprehensive analysis)  
**Complexity:** High  

**Description:**  
Calculate median time between issue creation and first response (comment or close event) for issues created in T0-T90 window.

**Acceptance Criteria:**
- For each repo_id:
  - Query issues created in T0-T90: `repo.get_issues(since=t0, state='all')`
  - For each issue with ≥1 comment or close event:
    - Calculate response_time = (first_comment_date OR closed_date) - created_date
    - Convert to days
  - Compute median response time
  - If <5 issues in window: Mark as `None` (insufficient data)
- Store result in column: `median_issue_response_time`

**Dependencies:**
- PyGitHub `repo.get_issues()`, `issue.get_comments()`

**Inputs:**
- Repository list with `repo_id`, `t0_date`

**Outputs:**
- DataFrame with added column: `median_issue_response_time` (nullable)

**Edge Cases:**
- Repositories with <5 issues → Set to None
- Issues with no responses → Exclude from median calculation

---

### FR-6: Calculate Repository Age

**Priority:** P0 (Critical - Required for partial correlation)  
**Complexity:** Low  

**Description:**  
Calculate repository age at T0+90 for use as control variable in partial correlation.

**Acceptance Criteria:**
- For each repo_id:
  - Retrieve repository creation date: `repo.created_at`
  - Calculate `repo_age_days = (t0 + 90 days) - repo.created_at` (in days)
- Store result in column: `repo_age_days`

**Dependencies:**
- PyGitHub `repo.created_at`

**Inputs:**
- Repository list with `t0_date`

**Outputs:**
- DataFrame with added column: `repo_age_days`

---

### FR-7: Data Validation and Cleaning

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
Validate collected metrics, detect outliers, handle missing values, and prepare dataset for statistical analysis.

**Acceptance Criteria:**
- **Completeness Check:**
  - Count repositories with complete data (non-null commits_per_month, unique_contributors, dcs_3_score)
  - Require ≥95/100 repositories with complete data (Quality Gate)
- **Outlier Detection:**
  - Calculate z-scores for `commits_per_month`, `unique_contributors`, `repo_age_days`
  - Flag outliers (|z| > 3) but DO NOT remove (report as flagged)
- **Missing Value Handling:**
  - `median_issue_response_time`: Allow null values (exclude from specific analyses)
  - Other metrics: Must be non-null (repository excluded if missing)
- Export cleaned dataset to CSV: `activity_metrics_cleaned.csv`

**Dependencies:**
- scipy.stats.zscore
- pandas

**Inputs:**
- DataFrame with all metrics from FR-3 to FR-6

**Outputs:**
- `activity_metrics_cleaned.csv` (N≥95 rows)
- Data quality report: missing count, outlier count

---

### FR-8: Spearman Correlation Analysis

**Priority:** P0 (Critical - Primary Gate)  
**Complexity:** Medium  

**Description:**  
Compute Spearman rank correlations between each activity metric and DCS_3 score.

**Acceptance Criteria:**
- **Test 1:** Commits/month vs DCS_3
  - `rho_commits, p_commits = spearmanr(commits_per_month, dcs_3_score)`
  - Convert to one-tailed p-value: `p_one_tailed = p_commits / 2`
- **Test 2:** Contributors vs DCS_3
  - `rho_contrib, p_contrib = spearmanr(unique_contributors, dcs_3_score)`
- **Test 3:** Issue response time vs DCS_3 (if sufficient data)
  - Exclude repositories with null `median_issue_response_time`
  - `rho_issues, p_issues = spearmanr(median_issue_response_time, dcs_3_score)`
- **Primary Gate Check:**
  - `gate_pass = (abs(rho_commits) >= 0.30) AND (p_one_tailed < 0.05)`
- Export results to CSV: `correlation_results.csv`

**Dependencies:**
- scipy.stats.spearmanr

**Inputs:**
- `activity_metrics_cleaned.csv`

**Outputs:**
- `correlation_results.csv` with columns: `metric`, `rho`, `p_value_two_tailed`, `p_value_one_tailed`, `sample_size`

---

### FR-9: Partial Correlation Analysis (Age-Controlled)

**Priority:** P0 (Critical - Secondary Gate)  
**Complexity:** Medium  

**Description:**  
Compute partial correlation between commits_per_month and DCS_3, controlling for repository age.

**Acceptance Criteria:**
- Use pingouin library: `partial_corr(data=df, x='commits_per_month', y='dcs_3_score', covar='repo_age_days')`
- Extract partial ρ and p-value from result DataFrame
- **Secondary Gate Check:**
  - `secondary_gate_pass = (abs(partial_rho) >= 0.25) AND (partial_p < 0.05)`
- Export result to CSV: `partial_correlation_results.csv`

**Dependencies:**
- pingouin library

**Inputs:**
- `activity_metrics_cleaned.csv`

**Outputs:**
- `partial_correlation_results.csv` with columns: `partial_rho`, `partial_p`, `controlled_variable`

---

### FR-10: Bootstrap Confidence Intervals

**Priority:** P1 (Required for robust inference)  
**Complexity:** Medium  

**Description:**  
Compute 95% bootstrap confidence intervals for Spearman ρ estimates.

**Acceptance Criteria:**
- For primary correlation (commits_per_month vs DCS_3):
  - Generate 10,000 bootstrap resamples with replacement
  - Compute Spearman ρ for each resample
  - Calculate 95% CI: (2.5th percentile, 97.5th percentile)
- Report CI alongside point estimate
- Export to CSV: `bootstrap_ci.csv`

**Dependencies:**
- numpy.random.choice (for resampling)
- scipy.stats.spearmanr

**Inputs:**
- `activity_metrics_cleaned.csv`

**Outputs:**
- `bootstrap_ci.csv` with columns: `metric`, `rho_point_estimate`, `ci_lower`, `ci_upper`

---

### FR-11: Visualization - Scatter Plot (Primary Correlation)

**Priority:** P0 (Critical - Required Figure)  
**Complexity:** Medium  

**Description:**  
Generate scatter plot showing commits_per_month vs DCS_3 with regression line and annotated ρ and p-value.

**Acceptance Criteria:**
- X-axis: `commits_per_month` (log scale if large range)
- Y-axis: `dcs_3_score` (0-3 scale)
- Points: Each repository as a dot
- Regression line: Best-fit line from scipy.stats.linregress or lowess
- Annotation: Display ρ and p-value in top-left corner
- Title: "H-M1: Commits per Month vs Documentation Quality"
- Save to `figures/h1_primary_correlation.png`

**Dependencies:**
- matplotlib or seaborn

**Inputs:**
- `activity_metrics_cleaned.csv`
- ρ and p-value from FR-8

**Outputs:**
- `figures/h1_primary_correlation.png`

---

### FR-12: Visualization - Correlation Matrix Heatmap

**Priority:** P1 (Additional Figure)  
**Complexity:** Low  

**Description:**  
Generate heatmap showing pairwise Spearman correlations for all activity metrics vs DCS_3.

**Acceptance Criteria:**
- Variables: `commits_per_month`, `unique_contributors`, `median_issue_response_time` (if available), `dcs_3_score`
- Cells: Annotated with ρ values
- Color scale: -1 (red) to +1 (blue), diverging colormap
- Significance stars: * (p<0.05), ** (p<0.01), *** (p<0.001)
- Save to `figures/correlation_matrix.png`

**Dependencies:**
- seaborn.heatmap
- scipy.stats.spearmanr

**Inputs:**
- `activity_metrics_cleaned.csv`

**Outputs:**
- `figures/correlation_matrix.png`

---

### FR-13: Visualization - Partial Correlation Comparison

**Priority:** P1 (Additional Figure)  
**Complexity:** Medium  

**Description:**  
Generate bar chart comparing raw ρ vs partial ρ (age-controlled) to show impact of controlling for repository age.

**Acceptance Criteria:**
- X-axis: Categories ("Raw ρ", "Partial ρ (age-controlled)")
- Y-axis: Correlation coefficient (-1 to 1)
- Bars: Heights = [rho_commits, partial_rho]
- Error bars: 95% CI from bootstrap (if computed)
- Horizontal line at ρ = 0.30 (gate threshold)
- Save to `figures/partial_correlation_comparison.png`

**Dependencies:**
- matplotlib

**Inputs:**
- `correlation_results.csv`, `partial_correlation_results.csv`

**Outputs:**
- `figures/partial_correlation_comparison.png`

---

### FR-14: Visualization - Component-Level Correlation

**Priority:** P2 (Optional - Exploratory)  
**Complexity:** Medium  

**Description:**  
Generate scatter plots showing commits_per_month vs individual DCS components (data_context, preprocessing, licensing) to identify which dimensions drive the correlation.

**Acceptance Criteria:**
- 3 subplots (1 row, 3 columns)
- Each subplot: commits_per_month vs component score (0-1 scale)
- Annotate with ρ and p-value for each component
- Save to `figures/component_level_correlation.png`

**Dependencies:**
- matplotlib subplots
- DCS component scores from H-E1

**Inputs:**
- `activity_metrics_cleaned.csv` merged with H-E1 component scores

**Outputs:**
- `figures/component_level_correlation.png`

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Priority:** P0  

**Requirements:**
- Fixed random seed for bootstrap resampling (seed=42)
- Document exact Python library versions in `requirements.txt`
- Save all intermediate CSVs (activity_metrics, correlation_results)
- Log GitHub API query timestamps and rate limit status

### NFR-2: Data Management

**Priority:** P0  

**Requirements:**
- Disk space: ~10 MB for CSV files
- Data retention: Keep all intermediate CSVs for potential re-analysis
- Privacy: Only public repository metadata (no PII)
- Dependency on H-E1: Verify H-E1 validation_results.csv exists before proceeding

### NFR-3: Ethical Compliance

**Priority:** P0  

**Requirements:**
- Use only public repositories (same sample as H-E1)
- Respect GitHub rate limits (5000 requests/hour with token)
- No automated scraping beyond official GitHub API

### NFR-4: Performance

**Priority:** P1  

**Requirements:**
- Total runtime: ≤2 hours
  - H-E1 data loading: ~1 minute
  - GitHub API data collection: ~1 hour (100 repos × 30 sec/repo)
  - Statistical analysis: ~5 minutes
  - Visualization: ~10 minutes
- No manual coding required (fully automated pipeline)

---

## Data Requirements

### Input Data

**Source 1: H-E1 Validation Results**
- File: `../h-e1/validation_results.csv`
- Fields required: `repo_id`, `dcs_3_score`, `t0_date`
- Volume: N=100 repositories

**Source 2: GitHub API**
- Endpoint: `Github().get_repo()`
- Fields required: `commits`, `contributors`, `issues`, `created_at`
- Rate limit: 5000 requests/hour (requires token)

### Output Data

**Primary Outputs:**
- `activity_metrics_cleaned.csv` (≥95 rows)
- `correlation_results.csv` (3-4 rows, one per metric)
- `partial_correlation_results.csv` (1 row)
- `bootstrap_ci.csv` (1-3 rows)

**Figures:**
- `h1_primary_correlation.png` (required)
- `correlation_matrix.png` (required)
- `partial_correlation_comparison.png` (required)
- `component_level_correlation.png` (optional)

**Final Report:**
- `04_validation.md` (Phase 4 output with gate pass/fail)

---

## Dependencies

### External Libraries

**Required:**
- `pandas` (>=2.0.0) - Data manipulation
- `numpy` (>=1.24.0) - Numerical operations
- `scipy` (>=1.11.0) - Spearman correlation, bootstrap
- `pingouin` (>=0.5.0) - Partial correlation
- `PyGithub` (>=2.0.0) - GitHub API
- `matplotlib` (>=3.7.0) - Visualization
- `seaborn` (>=0.12.0) - Heatmap visualization

### External Services

**GitHub API:**
- Authentication: Required (Personal Access Token)
- Rate limit: 5000 requests/hour (authenticated)

### Internal Dependencies

**H-E1 Validation Results:**
- File: `../h-e1/validation_results.csv`
- Critical dependency: Pipeline MUST fail if H-E1 not completed

---

## Success Metrics

### SHOULD_WORK Gate Criteria

**Primary (Required):**
- Spearman ρ ≥ 0.30 AND p < 0.05 (one-tailed) → **Gate PASS**
- If ρ < 0.30 OR p ≥ 0.05:
  - If 0.10 ≤ ρ < 0.30 → **Gate PARTIAL** (weak correlation) → MODIFY hypothesis
  - If ρ < 0.10 → **Gate FAIL** → Route to Phase 2A-Dialogue (explore alternative mechanisms)

**Secondary (Required):**
- Partial correlation ρ ≥ 0.25 AND p < 0.05 (age-controlled remains significant) → **Supports hypothesis**
- If partial ρ < 0.25 OR p ≥ 0.05 → **Age confounding detected** → PARTIAL result

**Quality Gate (Required):**
- Data collection success rate ≥ 95% (≥95/100 repositories with complete metrics) → **Quality PASS**
- If success rate < 95% → **Quality FAIL** → Investigate API errors

### Additional Metrics

- GitHub API data collection success rate ≥ 95%
- Bootstrap CI width < 0.40 (precision requirement)
- Outlier count ≤ 5 repositories (data quality check)

---

## Risk Mitigation

### Risk R1: GitHub API Rate Limit

**Mitigation:** Implement exponential backoff retry logic, use authenticated token (5000 requests/hour sufficient)

### Risk R2: H-E1 Dependency

**Mitigation:** Check for `../h-e1/validation_results.csv` existence at pipeline start, fail early if missing

### Risk R3: Null Result (ρ ≈ 0)

**Mitigation:** This is a valid scientific result (mechanism hypothesis rejected), not a pipeline failure

---

## Appendix: Correlation Analysis Pseudo-Code

### Main Analysis Pipeline

```python
import pandas as pd
from scipy.stats import spearmanr
from pingouin import partial_corr
import numpy as np

# Step 1: Load H-E1 DCS_3 scores
h_e1_results = pd.read_csv("../h-e1/validation_results.csv")
dcs_scores = h_e1_results[['repo_id', 'dcs_3_score', 't0_date']]

# Step 2: Collect GitHub activity metrics
from github import Github
g = Github("GITHUB_ACCESS_TOKEN")

activity_metrics = []
for _, row in dcs_scores.iterrows():
    repo = g.get_repo(row['repo_id'])
    t0 = pd.to_datetime(row['t0_date'])
    t90 = t0 + pd.Timedelta(days=90)
    
    # Commits per month
    commits = list(repo.get_commits(since=t0, until=t90))
    commits_per_month = len(commits) / 3
    
    # Unique contributors
    authors = set(c.author.login for c in commits if c.author)
    unique_contributors = len(authors)
    
    # Repository age
    repo_age_days = (t90 - repo.created_at).days
    
    activity_metrics.append({
        'repo_id': row['repo_id'],
        'commits_per_month': commits_per_month,
        'unique_contributors': unique_contributors,
        'repo_age_days': repo_age_days
    })

# Step 3: Merge datasets
df = pd.merge(dcs_scores, pd.DataFrame(activity_metrics), on='repo_id')

# Step 4: Spearman correlation
rho, p_value = spearmanr(df['commits_per_month'], df['dcs_3_score'])
p_one_tailed = p_value / 2

# Step 5: Partial correlation (age-controlled)
partial_result = partial_corr(
    data=df, 
    x='commits_per_month', 
    y='dcs_3_score', 
    covar='repo_age_days'
)
partial_rho = partial_result['r'].values[0]
partial_p = partial_result['p-val'].values[0]

# Step 6: Gate check
primary_pass = (abs(rho) >= 0.30) and (p_one_tailed < 0.05)
secondary_pass = (abs(partial_rho) >= 0.25) and (partial_p < 0.05)
gate_result = "PASS" if (primary_pass and secondary_pass) else "FAIL"

print(f"Primary ρ = {rho:.3f}, p = {p_one_tailed:.4f} (one-tailed)")
print(f"Partial ρ = {partial_rho:.3f}, p = {partial_p:.4f}")
print(f"Gate: {gate_result}")
```

---

## Traceability

| FR/NFR | Phase 2C Source | Priority |
|--------|-----------------|----------|
| FR-1 | Reuse H-E1 data (02c line 44-52) | P0 |
| FR-2 | GitHub API authentication (02c line 186-195) | P0 |
| FR-3 | Commits metric (02c line 176-180) | P0 |
| FR-4 | Contributors metric (02c line 176-180) | P0 |
| FR-5 | Issue response time (02c line 176-180) | P1 |
| FR-6 | Repository age control (02c line 49, 263) | P0 |
| FR-7 | Data validation (02c line 220-227) | P0 |
| FR-8 | Spearman correlation (02c line 236-256, 296-325) | P0 |
| FR-9 | Partial correlation (02c line 263, 314-318) | P0 |
| FR-10 | Bootstrap CI (02c line 354) | P1 |
| FR-11 | Primary scatter plot (02c line 386-388) | P0 |
| FR-12-14 | Additional figures (02c line 389-409) | P1-P2 |

---

**Document Version:** 1.0  
**Next Phase:** Phase 3 - Architecture Design  
**Output Location:** `/workspace/TEST_mldpr/docs/youra_research/h-m1/03_prd.md`
