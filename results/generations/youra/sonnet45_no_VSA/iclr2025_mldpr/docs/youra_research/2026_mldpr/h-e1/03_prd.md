# Product Requirements Document: H-E1 - Documentation Gap Validation Study

**Date:** 2026-07-12  
**Hypothesis:** H-E1 (EXISTENCE - FOUNDATION)  
**Author:** Anonymous  
**Status:** DRAFT v1.0  

---

## Executive Summary

### Purpose

Implement an observational study to measure documentation completeness in HuggingFace dataset repositories at T0 + 90 days, validating whether a framework-to-practice documentation gap exists despite standardized documentation frameworks.

### Hypothesis Statement

Among ML dataset repositories on HuggingFace created 2022–2024 with ≥10 stars, ≤40% achieve DCS_3 ≥ 2.4 within 90 days of first release, demonstrating that a significant framework-to-practice compliance gap exists despite standardized documentation frameworks.

### Success Criteria (MUST_WORK Gate)

- **Primary:** 95% CI upper bound < 60% (rejects H0: π ≥ 0.70, confirms gap exists)
- **Secondary:** Component breakdown shows non-uniform distribution (χ² p < 0.05)
- **Quality Gate:** Inter-rater reliability κ ≥ 0.70

### Scope

**In Scope:**
- Repository sampling from HuggingFace Datasets Hub (2022-2024, ≥10 stars)
- T0 detection via 3-tier fallback (release tags → dataset commits → repo creation)
- Documentation cloning at T0 + 90 days
- DCS_3 manual coding (3-component rubric)
- Statistical analysis (binomial proportion test + chi-square)
- Inter-rater reliability validation

**Out of Scope:**
- Predictive modeling or machine learning training
- Automated documentation quality assessment
- Longitudinal tracking beyond T0 + 90 days
- Causal mechanism testing (deferred to H-M1)

---

## Problem Statement

### Background

Recent literature (Gim 2025, Rondina 2025, Oreamuno 2024) identifies severe documentation gaps in ML dataset repositories despite the availability of standardized frameworks (Datasheets, Data Cards). However, prior studies measure documentation quality at current state, not at T0 + 90 days (early release window), leaving temporal precedence unvalidated.

### Core Problem

Without temporal precedence validation, we cannot determine whether:
1. Repositories were non-compliant from the start (fundamental gap)
2. Documentation degraded over time (maintenance gap)

H-E1 provides the foundational evidence by measuring documentation at T0 + 90 days to validate that the gap exists from initial release.

### Research Gap

**Novel Contribution:**
- First study to measure DCS_3 at T0 + 90 days (temporal precedence validation)
- 3-tier T0 detection fallback for robust temporal anchoring
- Stratified sampling across 3-year window (2022-2024) for temporal representativeness

---

## Functional Requirements

### FR-1: Repository Sampling and Filtering

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
Sample N=120 dataset repositories from HuggingFace Datasets Hub with stratification by creation year (2022, 2023, 2024) to achieve target N=100 after T0 detection failures.

**Acceptance Criteria:**
- Query HuggingFace Hub API for all dataset repositories created 2022-01-01 to 2024-12-31
- Filter for repositories with ≥10 stars (`likes >= 10`)
- Exclude non-dataset repositories (models, spaces)
- Stratify by year: ~40 repositories per year (2022, 2023, 2024)
- Export sampled repository IDs to CSV: `sampled_repositories.csv`

**Dependencies:**
- `huggingface_hub` library (HfApi)
- pandas for stratification logic

**Inputs:**
- Date range: 2022-01-01 to 2024-12-31
- Star threshold: 10
- Sample size: 120 (oversample)

**Outputs:**
- `sampled_repositories.csv` with columns: `repo_id`, `created_at`, `stars`, `sample_year`

---

### FR-2: T0 Detection via 3-Tier Fallback

**Priority:** P0 (Critical)  
**Complexity:** High  

**Description:**  
Detect T0 (initial release date) for each sampled repository using 3-tier fallback strategy: (1) release tags, (2) first dataset commit, (3) repository creation date.

**Acceptance Criteria:**
- **Tier 1 (Preferred):** Extract first release tag timestamp via GitHub API (`repo.get_tags()`)
- **Tier 2 (Fallback):** Identify first commit matching dataset upload pattern (e.g., "add dataset", "upload data")
- **Tier 3 (Last Resort):** Use repository creation date (`repo.created_at`)
- Record T0 method used (tier 1/2/3) for each repository
- Achieve ≥95% T0 detection success rate across N=120 sample

**Dependencies:**
- PyGithub library
- GitHub API access token (rate limit: 5000 requests/hour)
- Regex patterns for dataset commit detection

**Inputs:**
- `sampled_repositories.csv` (repo_id list)

**Outputs:**
- Updated CSV with columns: `t0`, `t0_method` (tier1/tier2/tier3), `t0_success` (boolean)

**Risk Mitigation:**
- Oversample to N=120 to accommodate 5% T0 detection failure (Risk R3)
- Validate ≥95% success rate before proceeding to FR-3

---

### FR-3: Repository Cloning at T0 + 90 Days

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
Clone each repository's state at T0 + 90 days by retrieving the commit SHA closest to `t0 + 90 days` and downloading repository snapshot.

**Acceptance Criteria:**
- Calculate target date: `target_date = t0 + timedelta(days=90)`
- Find commit SHA closest to `target_date` via GitHub API
- Download repository snapshot at specific revision using `snapshot_download(revision=commit_sha)`
- Store each repository in `./data/repos/{repo_id}/`
- Verify download success: README.md exists in cloned directory

**Dependencies:**
- `huggingface_hub.snapshot_download`
- GitHub API for commit SHA retrieval
- Disk space: ~10 MB per repository × 100 = 1 GB estimated

**Inputs:**
- CSV with `repo_id`, `t0`, `t0_method`

**Outputs:**
- Cloned repositories in `./data/repos/{repo_id}/` (100 directories)
- Updated CSV with column: `commit_sha_t0_plus_90`, `clone_success`

---

### FR-4: Documentation File Extraction

**Priority:** P0 (Critical)  
**Complexity:** Low  

**Description:**  
Extract relevant documentation files from cloned repositories for DCS_3 coding.

**Acceptance Criteria:**
- Locate `README.md` (required)
- Locate `DATASET_CARD.md` or `.huggingface.yaml` (optional)
- Locate `LICENSE` or `LICENSE.md` (required for licensing component)
- Extract any additional markdown files in root directory
- Record file existence status for each repository

**Dependencies:**
- File system operations (os, pathlib)

**Inputs:**
- Cloned repositories in `./data/repos/{repo_id}/`

**Outputs:**
- CSV with columns: `has_readme`, `has_dataset_card`, `has_license`, `has_other_md`

---

### FR-5: DCS_3 Manual Coding Protocol

**Priority:** P0 (Critical)  
**Complexity:** High (Manual Labor)  

**Description:**  
Apply DCS_3 3-component rubric (Rondina et al. 2025) to assess documentation completeness via manual coding.

**Acceptance Criteria:**
- Code all N=100 repositories (after excluding T0 detection failures)
- **Component 1 - Data Collection Context (0-1 scale):**
  - 0.0: No mention of data sources or collection methodology
  - 0.5: Partial mention (sources OR methodology)
  - 1.0: Clear description of both sources AND methodology
- **Component 2 - Preprocessing Transparency (0-1 scale):**
  - 0.0: No documentation of cleaning, augmentation, or splits
  - 0.5: Partial documentation (1-2 aspects)
  - 1.0: Comprehensive (cleaning + augmentation + splits)
- **Component 3 - Licensing Clarity (0-1 scale):**
  - 0.0: No license file or statement
  - 0.5: License mentioned in README but no LICENSE file
  - 1.0: Clear LICENSE file or SPDX identifier
- Calculate `DCS_3_total = component1 + component2 + component3` (0-3 scale)
- Determine compliance: `compliant = (DCS_3_total >= 2.4)`

**Dependencies:**
- Coding template (Excel/Google Sheets)
- 2 independent coders for 20% dual-coded sample

**Inputs:**
- Extracted documentation files from FR-4

**Outputs:**
- `dcs_coding_results.csv` with columns: `repo_id`, `dcs_data_context`, `dcs_preprocessing`, `dcs_licensing`, `dcs_3_total`, `compliant`
- Dual-coded sample: `dcs_dual_coded_sample.csv` (N=20, 2 coders)

**Estimated Effort:**
- 5 minutes per repository × 100 = 8.3 hours
- Dual coding: 5 minutes × 20 × 2 coders = 3.3 hours
- Total manual coding: ~12 hours

---

### FR-6: Inter-Rater Reliability (IRR) Validation

**Priority:** P0 (Critical - Quality Gate)  
**Complexity:** Low  

**Description:**  
Calculate Cohen's kappa (κ) for dual-coded sample to validate coding reliability.

**Acceptance Criteria:**
- Select 20% random sample (N=20 repositories) for dual coding
- Calculate Cohen's kappa for each component: `κ_data_context`, `κ_preprocessing`, `κ_licensing`
- Calculate overall kappa for binary compliance: `κ_overall = cohen_kappa_score(coder1_compliant, coder2_compliant)`
- **Quality Gate:** κ ≥ 0.70 required to proceed
- If κ < 0.70: Refine rubric operationalization and re-code sample

**Dependencies:**
- `sklearn.metrics.cohen_kappa_score`

**Inputs:**
- `dcs_dual_coded_sample.csv` (2 coders × 20 repos)

**Outputs:**
- IRR report with κ values for each component
- Pass/Fail status for quality gate

---

### FR-7: Statistical Analysis - Compliance Rate

**Priority:** P0 (Critical)  
**Complexity:** Medium  

**Description:**  
Calculate compliance rate (proportion achieving DCS_3 ≥ 2.4) with 95% Wilson score confidence interval.

**Acceptance Criteria:**
- Count compliant repositories: `compliant_count = sum(DCS_3 >= 2.4)`
- Calculate compliance rate: `π = compliant_count / N`
- Compute 95% CI using Wilson score interval: `(ci_lower, ci_upper)`
- **Primary Success Criterion:** `ci_upper < 0.60` (rejects H0: π ≥ 0.70)

**Dependencies:**
- `statsmodels.stats.proportion.proportion_confint` (method='wilson')

**Inputs:**
- `dcs_coding_results.csv` with `compliant` column

**Outputs:**
- Compliance rate: π (point estimate)
- 95% CI: (ci_lower, ci_upper)
- Gate pass: boolean (ci_upper < 0.60)

---

### FR-8: Statistical Analysis - Component Breakdown

**Priority:** P1 (Required for Secondary Criterion)  
**Complexity:** Medium  

**Description:**  
Test whether component-level compliance rates are non-uniformly distributed using chi-square goodness-of-fit test.

**Acceptance Criteria:**
- Count repositories achieving ≥0.5 for each component:
  - `n_data_context = sum(dcs_data_context >= 0.5)`
  - `n_preprocessing = sum(dcs_preprocessing >= 0.5)`
  - `n_licensing = sum(dcs_licensing >= 0.5)`
- Perform chi-square test against uniform distribution: `expected = [N/3, N/3, N/3]`
- **Secondary Success Criterion:** χ² p-value < 0.05

**Dependencies:**
- `scipy.stats.chi2_contingency`

**Inputs:**
- `dcs_coding_results.csv` with component scores

**Outputs:**
- Component counts: `[n_data_context, n_preprocessing, n_licensing]`
- Chi-square statistic: χ²
- p-value
- Non-uniform: boolean (p < 0.05)

---

### FR-9: Visualization - Compliance Rate Chart

**Priority:** P1 (Required Figure)  
**Complexity:** Low  

**Description:**  
Generate bar chart showing observed compliance rate vs H0 threshold (70%) and H1 prediction (40%) with 95% CI error bars.

**Acceptance Criteria:**
- X-axis: Categories ("H0: 70%", "H1: 40%", "Observed")
- Y-axis: Compliance rate (0-1 scale)
- Bars: Heights = [0.70, 0.40, observed_rate]
- Error bars on "Observed" bar: 95% CI range
- Horizontal line at 60% (gate threshold)
- Save to `figures/compliance_rate.png`

**Dependencies:**
- matplotlib or plotly

**Inputs:**
- Compliance rate π, CI bounds (ci_lower, ci_upper) from FR-7

**Outputs:**
- `figures/compliance_rate.png`

---

### FR-10: Visualization - Component Breakdown

**Priority:** P2 (Additional Figure)  
**Complexity:** Low  

**Description:**  
Generate stacked bar chart showing distribution of scores (0, 0.5, 1.0) for each DCS component.

**Acceptance Criteria:**
- X-axis: Components ("Data Context", "Preprocessing", "Licensing")
- Y-axis: Percentage of repositories
- Stacks: 0 (red), 0.5 (yellow), 1.0 (green)
- Save to `figures/component_breakdown.png`

**Dependencies:**
- matplotlib

**Inputs:**
- `dcs_coding_results.csv` component columns

**Outputs:**
- `figures/component_breakdown.png`

---

### FR-11: Visualization - T0 Detection Methods

**Priority:** P2 (Additional Figure)  
**Complexity:** Low  

**Description:**  
Generate pie chart showing breakdown of T0 detection methods used (Tier 1/2/3).

**Acceptance Criteria:**
- Slices: Tier 1 (%), Tier 2 (%), Tier 3 (%)
- Labels with counts: "Tier 1: N=X (Y%)"
- Save to `figures/t0_detection_breakdown.png`

**Dependencies:**
- matplotlib

**Inputs:**
- CSV with `t0_method` column from FR-2

**Outputs:**
- `figures/t0_detection_breakdown.png`

---

### FR-12: Visualization - DCS Distribution Histogram

**Priority:** P2 (Additional Figure)  
**Complexity:** Low  

**Description:**  
Generate histogram of DCS_3 total scores with threshold line at 2.4.

**Acceptance Criteria:**
- X-axis: DCS_3 score (0-3 scale, bins=0.5 width)
- Y-axis: Frequency (count of repositories)
- Vertical line at 2.4 (compliance threshold, dashed red)
- Save to `figures/dcs_distribution.png`

**Dependencies:**
- matplotlib

**Inputs:**
- `dcs_coding_results.csv` with `dcs_3_total` column

**Outputs:**
- `figures/dcs_distribution.png`

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Priority:** P0  

**Requirements:**
- All sampling must use fixed random seed (seed=42) for stratified sampling
- Document exact Python library versions in `requirements.txt`
- Save all intermediate CSVs (sampled_repositories, t0_detection, dcs_coding)
- Include data provenance: API query timestamps, commit SHAs

### NFR-2: Data Management

**Priority:** P0  

**Requirements:**
- Disk space: Reserve 2 GB for cloned repositories
- Data retention: Keep cloned repositories for potential re-coding
- Privacy: No PII collection (public repositories only)

### NFR-3: Ethical Compliance

**Priority:** P0  

**Requirements:**
- Use only public repositories (no authentication beyond API token)
- Respect HuggingFace/GitHub rate limits (5000 requests/hour)
- No automated scraping beyond official APIs

### NFR-4: Performance

**Priority:** P1  

**Requirements:**
- Total runtime: ≤4 hours (excluding manual coding)
  - Repository sampling: ~10 minutes
  - T0 detection: ~1 hour (120 repos × 30 sec/repo)
  - Cloning: ~2 hours (100 repos × 1 min/repo)
  - Statistical analysis: ~5 minutes
- Manual coding: ~12 hours (separate from automated pipeline)

---

## Data Requirements

### Input Data

**Source 1: HuggingFace Datasets Hub**
- Endpoint: `HfApi().list_datasets()`
- Fields required: `repo_id`, `created_at`, `likes`, `tags`
- Volume: ~10,000 total dataset repositories (estimated)

**Source 2: GitHub API**
- Endpoint: `Github().get_repo()`
- Fields required: `created_at`, `tags`, `commits`
- Rate limit: 5000 requests/hour (requires token)

### Output Data

**Primary Outputs:**
- `sampled_repositories.csv` (120 rows)
- `dcs_coding_results.csv` (100 rows after filtering)
- `dcs_dual_coded_sample.csv` (20 rows × 2 coders)

**Figures:**
- `compliance_rate.png`
- `component_breakdown.png`
- `t0_detection_breakdown.png`
- `dcs_distribution.png`

**Final Report:**
- `04_validation.md` (Phase 4 output with gate pass/fail)

---

## Dependencies

### External Libraries

**Required:**
- `huggingface_hub` (>=0.17.0) - Repository access
- `PyGithub` (>=2.0.0) - GitHub API
- `pandas` (>=2.0.0) - Data manipulation
- `numpy` (>=1.24.0) - Numerical operations
- `scipy` (>=1.11.0) - Statistical tests
- `statsmodels` (>=0.14.0) - Proportion CI
- `scikit-learn` (>=1.3.0) - Cohen's kappa
- `matplotlib` (>=3.7.0) - Visualization

### External Services

**HuggingFace Hub API:**
- Authentication: Optional (public datasets accessible without token)
- Rate limit: No strict limit for list operations

**GitHub API:**
- Authentication: Required (Personal Access Token)
- Rate limit: 5000 requests/hour (authenticated)

---

## Success Metrics

### MUST_WORK Gate Criteria

**Primary (Required):**
- 95% CI upper bound < 60% → **Gate PASS**
- 95% CI upper bound ≥ 60% → **Gate FAIL** → Route to Phase 0

**Secondary (Required):**
- Component breakdown χ² p < 0.05 → **Supports hypothesis**
- χ² p ≥ 0.05 → **Uniform distribution** → Partial evidence

**Quality Gate (Required):**
- Inter-rater reliability κ ≥ 0.70 → **Quality PASS**
- κ < 0.70 → **Quality FAIL** → Refine rubric and re-code

### Additional Metrics

- T0 detection success rate ≥ 95% (Risk R3 mitigation)
- Repository cloning success rate ≥ 98%
- Manual coding completion: 100% of successfully cloned repositories

---

## Risk Mitigation

### Risk R3: T0 Detection Failure

**Mitigation:** Oversample to N=120 (target N=100 after 5% failure)

### Risk R5: Inter-Rater Disagreement

**Mitigation:** Dual-code 20% sample, require κ ≥ 0.70, refine rubric if needed

### Risk R6: API Rate Limits

**Mitigation:** Implement exponential backoff retry logic, spread requests over time

---

## Appendix: Detailed Rubric

### DCS_3 Coding Guidelines

**Component 1: Data Collection Context (0-1)**

- **1.0:** README explicitly documents:
  - Data sources (e.g., "Scraped from Twitter API", "Curated from ImageNet")
  - Collection methodology (e.g., "Random sampling", "Expert curation")
  
- **0.5:** Partial documentation:
  - Sources mentioned but no methodology, OR
  - Methodology mentioned but no sources
  
- **0.0:** No mention of sources or methodology

**Component 2: Preprocessing Transparency (0-1)**

- **1.0:** README documents ALL of:
  - Data cleaning (e.g., "Removed duplicates", "Handled missing values")
  - Augmentation (if applicable, e.g., "Applied rotation/flip")
  - Split ratios (e.g., "80/10/10 train/val/test")
  
- **0.5:** Documents 1-2 aspects (e.g., mentions splits but not cleaning)
  
- **0.0:** No preprocessing documentation

**Component 3: Licensing Clarity (0-1)**

- **1.0:** Clear LICENSE file present (e.g., MIT, Apache 2.0, CC-BY 4.0)
  
- **0.5:** License mentioned in README but no separate LICENSE file
  
- **0.0:** No license information

---

## Traceability

| FR/NFR | Phase 2C Source | Priority |
|--------|-----------------|----------|
| FR-1 | Dataset specification (02c line 249-259) | P0 |
| FR-2 | Temporal measurement (02c line 261-268) | P0 |
| FR-3 | Repository cloning (02c line 280-315) | P0 |
| FR-4 | Documentation files (02c line 269-275) | P0 |
| FR-5 | DCS_3 rubric (02c line 329-344) | P0 |
| FR-6 | IRR protocol (02c line 346-350) | P0 |
| FR-7 | Primary success criteria (02c line 512-515) | P0 |
| FR-8 | Secondary criteria (02c line 517-521) | P1 |
| FR-9 | Visualization requirements (02c line 565) | P1 |
| FR-10-12 | Additional figures (02c line 570-573) | P2 |

---

**Document Version:** 1.0  
**Next Phase:** Phase 3 - Architecture Design  
**Output Location:** `/workspace/TEST_mldpr/docs/youra_research/h-e1/03_prd.md`
