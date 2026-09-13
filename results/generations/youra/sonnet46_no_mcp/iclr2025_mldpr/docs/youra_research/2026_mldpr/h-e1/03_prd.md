# Product Requirements Document: H-E1

**Hypothesis:** H-E1 — FAIR Score Variance Existence (Foundation)
**Type:** EXISTENCE (PoC)
**Generated:** 2026-05-04
**Phase:** 3 — Implementation Planning
**Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This PRD specifies the implementation requirements for verifying the existence of sufficient FAIR compliance score variance in the OpenML post-2018 tabular dataset cohort. The experiment applies the F-UJI automated FAIR assessment tool to ~3,000–5,000 OpenML dataset landing pages via batch REST API calls, computes the Coefficient of Variation (CV) of aggregate FAIR scores, and verifies that both the high-FAIR (≥0.5) and low-FAIR (<0.5) groups contain at least 500 datasets — a prerequisite for downstream matched-pairs survival analysis (H-M1–H-M4).

**Gate:** MUST_WORK — CV > 0.15 AND n_high ≥ 500 AND n_low ≥ 500

---

## 2. Problem Statement

The main hypothesis (H-FAIROutcomes-v1) requires that FAIR compliance scores vary sufficiently across OpenML datasets to enable propensity-matched survival analysis. Without variance confirmation (H-E1), the downstream mechanism hypotheses cannot proceed. This PoC experiment determines whether F-UJI automated scoring applied to the OpenML post-2018 cohort produces a heterogeneous distribution, and whether both FAIR groups have adequate sample size.

**Research Question:** Does the OpenML post-2018 tabular cohort exhibit sufficient FAIR score variance (CV > 0.15) and adequate group sizes (n_high, n_low ≥ 500) to enable matched-pairs analysis?

---

## 3. Functional Requirements

### FR-1: OpenML Cohort Construction
- **Description:** Enumerate all tabular datasets uploaded to OpenML from 2018-01-01 to present using the official `openml` Python API.
- **Filter criteria:**
  - `upload_date >= '2018-01-01'`
  - task type ∈ {supervised_classification, supervised_regression}
  - Deduplicate: keep latest version per dataset name
- **Output:** DataFrame with columns: `{did, name, upload_date, NumberOfInstances, NumberOfFeatures, MajorityClassPercentage, landing_page_url}`
- **Expected size:** 3,000–5,000 rows
- **Source:** OpenML Python API (`openml.datasets.list_datasets`)

### FR-2: F-UJI Batch FAIR Scoring
- **Description:** Score all cohort dataset landing pages via F-UJI REST API in async batch mode.
- **Endpoint:** POST `/fuji/api/v1/evaluate`
- **Payload:** `{"object_identifier": "https://www.openml.org/d/{did}", "object_type": "landing_page"}`
- **Concurrency:** `asyncio.Semaphore(10)` — 10 concurrent requests
- **Retry:** Exponential backoff (3 retries, base=2s) on HTTP errors
- **Output:** Per-dataset JSON with 17 sub-criteria scores → aggregate FAIR score = mean(17 sub-criteria)
- **Fallback (pre-registered):** If F-UJI API unavailable, use OpenML machine-computed qualities as FAIR proxy
- **Source:** F-UJI REST API documentation (pangaea-data-publisher/fuji)

### FR-3: FAIR Score Computation
- **Description:** Compute aggregate FAIR score per dataset and derive group membership.
- **Aggregate:** `fair_score = mean(17 sub-criteria scores)` ∈ [0, 1]
- **Group assignment:**
  - High-FAIR: aggregate score ≥ 0.5
  - Low-FAIR: aggregate score < 0.5
- **Output columns:** `{did, fair_aggregate, fair_F, fair_A, fair_I, fair_R, group, upload_date_ordinal}`

### FR-4: Statistical Existence Metrics
- **Description:** Compute primary and secondary gate metrics.
- **Primary metrics:**
  - `CV = std(fair_aggregate) / mean(fair_aggregate)` — gate threshold: > 0.15
  - `n_high = sum(fair_aggregate >= 0.5)` — gate threshold: ≥ 500
  - `n_low = sum(fair_aggregate < 0.5)` — gate threshold: ≥ 500
- **Secondary metrics (instrument validity):**
  - `r_quality = spearmanr(fair_aggregate, openml_metadata_richness)` — threshold: > 0.10
  - `r_date = spearmanr(fair_aggregate, upload_date_ordinal)` — threshold: < 0.20 (retroactive tagging diagnostic)
- **Bimodality:** Hartigan's dip test + bimodality coefficient (BC > 5/9)
- **Source:** scipy.stats, numpy, diptest

### FR-5: Baseline Comparison
- **Description:** Compute unadjusted distribution as comparison anchor.
- **Baseline model:** Raw CV without propensity matching or covariate adjustment
  - `cv_baseline = std(all_fair_scores) / mean(all_fair_scores)`
  - `r_baseline, _ = spearmanr(all_fair_scores, upload_dates)`
- **Proposed:** Same metrics computed on full cohort (both are full-cohort for EXISTENCE — baseline shows pre-registered confound check)
- **Success:** Proposed CV > 0.15 confirms real variance, not age-driven artifact

### FR-6: Visualization Generation
- **Required figure:** Gate Metrics Bar Chart — CV vs 0.15 threshold, n_high vs 500, n_low vs 500
- **Additional figures (Phase 4 coder autonomous):**
  1. FAIR Score Distribution Histogram (full distribution, 0.5 threshold line)
  2. Sub-criteria Heatmap (17 F-UJI sub-criteria mean scores per F/A/I/R dimension)
  3. Temporal Diagnostic Plot (FAIR score vs upload_date, Spearman r annotation)
  4. Instrument Validity Scatter (FAIR score vs OpenML metadata_richness, r annotation)
  5. High/Low Group Size Bar Chart (n_high, n_low with 500 threshold)
- **Output path:** `docs/youra_research/20260504_mldpr/h-e1/figures/`

### FR-7: Results Persistence
- **Description:** Save all results to structured output files for Phase 4 validation and downstream hypotheses.
- **Outputs:**
  - `h-e1/results/fair_scores.csv` — per-dataset FAIR scores and group membership
  - `h-e1/results/existence_metrics.json` — gate metrics (CV, n_high, n_low, r_quality, r_date)
  - `h-e1/results/gate_result.json` — pass/fail with values
  - `h-e1/figures/` — all generated figures (PNG)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | OpenML Post-2018 Tabular Cohort |
| **Type** | programmatic-api |
| **Source** | OpenML Python API (openml.org) |
| **Access** | `pip install openml` + API key optional for public data |
| **Expected Size** | 3,000–5,000 datasets |
| **Download Method** | `openml.datasets.list_datasets(upload_date_from='2018-01-01', output_format='dataframe')` |

**Preprocessing Steps:**
1. Filter: `upload_date >= '2018-01-01'`
2. Filter: task_type ∈ {supervised_classification, supervised_regression}
3. Deduplicate: keep latest version per dataset name
4. Construct URL: `https://www.openml.org/d/{did}`
5. Extract machine-computed qualities: NumberOfInstances, NumberOfFeatures, MajorityClassPercentage

**Note:** No synthetic data used. Dataset is real OpenML repository data (programmatic-api type).

### 4.2 External Tool (F-UJI)

| Field | Value |
|-------|-------|
| **Name** | F-UJI FAIR Assessment Tool |
| **Type** | REST API (external tool) |
| **Source** | pangaea-data-publisher/fuji (GitHub) |
| **Access** | Self-hosted or FAIRsFAIR public instance |
| **Endpoint** | POST `/fuji/api/v1/evaluate` |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Total execution time: ≤ 30 minutes (dominated by F-UJI API calls)
- F-UJI batch scoring: ≤ 15 minutes at 10 req/sec for 5,000 URLs

### NFR-2: Reliability
- Retry on HTTP failure: 3 retries with exponential backoff (base=2s)
- Cache F-UJI responses to disk (avoid re-scoring on re-runs)
- Save intermediate results after each batch of 100 datasets

### NFR-3: Reproducibility
- Fixed seed: 1 (deterministic — no random sampling)
- Full cohort used (no subsampling)
- All parameters hardcoded in config (LIGHT tier — argparse/hardcoded acceptable)

### NFR-4: Compute
- CPU only — no GPU required
- Single process (asyncio for concurrency within process)
- Memory: ≤ 2GB (DataFrame for 5,000 datasets with scores is small)

---

## 6. Success Criteria

### Primary Gate (MUST_WORK — all required)

| Metric | Threshold | Consequence if Failed |
|--------|-----------|----------------------|
| CV (Coefficient of Variation) | **> 0.15** | STOP — pivot to OpenML machine-computed qualities as FAIR proxy |
| n_high (datasets with FAIR ≥ 0.5) | **≥ 500** | STOP — insufficient matched pairs |
| n_low (datasets with FAIR < 0.5) | **≥ 500** | STOP — insufficient matched pairs |

### Secondary Metrics (Instrument Validity)

| Metric | Threshold | Notes |
|--------|-----------|-------|
| r_quality (Spearman FAIR vs metadata_richness) | > 0.10 | F-UJI instrument validity |
| r_date (Spearman FAIR vs upload_date) | < 0.20 | Retroactive tagging diagnostic |

### Expected Performance (from domain knowledge)
- CV: ~0.20–0.45 (Devaraju & Huber 2021 report CV ~0.28 for Zenodo)
- n_high proportion: ~30–50% of cohort
- Both thresholds expected to pass given OpenML documentation heterogeneity

---

## 7. Technical Dependencies

### 7.1 Python Packages

```
openml>=0.14.0          # OpenML API client
aiohttp>=3.9.0          # Async HTTP for F-UJI batch scoring
asyncio                 # Standard library — async concurrency
numpy>=1.24.0           # Numerical computation
pandas>=2.0.0           # DataFrame operations
scipy>=1.11.0           # Statistical tests (spearmanr)
matplotlib>=3.7.0       # Visualization
seaborn>=0.12.0         # Statistical visualization
diptest>=0.7.0          # Hartigan's dip test (optional, bimodality)
pyyaml>=6.0.0           # Config and results serialization
```

### 7.2 External Services

| Service | URL | Purpose | Fallback |
|---------|-----|---------|---------|
| F-UJI REST API | `/fuji/api/v1/evaluate` | FAIR scoring | OpenML machine-computed qualities |
| OpenML API | `openml.org` | Dataset enumeration | N/A |

### 7.3 Infrastructure (LIGHT tier)
- No WandB required
- No complex logging — print statements + CSV output
- No unit test suite required — smoke test sufficient
- Config: argparse or hardcoded constants

---

## 8. Out of Scope

- Propensity matching (H-M1 prerequisite, not part of H-E1)
- Kaplan-Meier survival analysis (H-M1)
- HuggingFace dataset analysis (H-M4)
- Model training or fine-tuning
- Multi-GPU or distributed computation
- Production deployment

---

## 9. Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| CV > 0.15 threshold | Devaraju & Huber (2021), verification_plan §2.2 |
| n_high/n_low ≥ 500 | lifelines power analysis, verification_plan §C |
| F-UJI REST API | fuji GitHub, verification_plan §1.3 |
| OpenML post-2018 cohort | Vanschoren (2019), verification_plan §1.3 |
| r_quality > 0.10 | Devaraju & Huber (2021) |
| r_date < 0.20 | verification_plan §4.2 R1 (retroactive tagging diagnostic) |
| asyncio Semaphore(10) | F-UJI rate limiting recommendation |
| EXISTENCE PoC constraints | Phase 2C experiment brief §PoC Rules |
