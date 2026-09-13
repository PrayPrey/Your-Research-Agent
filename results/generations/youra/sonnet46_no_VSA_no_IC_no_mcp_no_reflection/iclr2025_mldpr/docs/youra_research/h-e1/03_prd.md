---
title: "PRD: H-E1 — Data Acquisition Pipeline Feasibility"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: Anonymous
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - nfrs
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
source: "02c_experiment_brief.md"
---

# PRD: H-E1 — Data Acquisition Pipeline Feasibility

## 1. Executive Summary

H-E1 verifies that a data acquisition pipeline connecting three public APIs (Raff 2019 corpus, HuggingFace Hub, OpenML) is operationally feasible. This is a MUST_WORK gate: if the pipeline fails to achieve ≥50% HF card coverage and ≥70% OpenML temporal filter success rate across Raff's 255-paper corpus, all downstream hypotheses (H-M1, H-M2, H-M3) are blocked and the study terminates.

**Scope:** PoC script — not a trained model. Deterministic data pipeline covering N=255 papers.

---

## 2. Problem Statement

### Background

Raff (2019) manually assessed reproducibility for 255 ML papers (1984–2017). To extend this work with documentation and dataset-concentration features, we require:

1. **HuggingFace Hub dataset cards** for datasets referenced in those 255 papers — to compute documentation completeness scores (IV1).
2. **OpenML dataset run counts** with temporal filtering (pre-publication runs only) — to compute dataset concentration scores (IV2).
3. **Raff's reproducibility labels** — the dependent variable (DV).

The feasibility question is: are these three data sources programmatically accessible for the Raff corpus at the coverage levels required by the study design?

### Hypothesis Statement

> Under the condition of top-venue ML papers in Raff's 2019 corpus (N=255), if the data acquisition pipeline is executed (HF Hub API queried for each unique dataset, OpenML API queried for run counts with temporal filtering, Raff 2019 supplementary labels parsed), then the resulting dataset will have ≥50% HF card coverage and functional OpenML timestamp filtering, because these are publicly documented APIs for foundational benchmarks that the research community has retroactively maintained.

### Failure Impact

If gate fails: study terminates. HF coverage <50% OR OpenML temporal filter fails for >30% of datasets = gate NOT satisfied.

---

## 3. Functional Requirements

### FR-1: Raff Corpus Parsing

- **FR-1.1** Load Raff 2019 CSV from local clone of `EdwardRaff/Quantifying-Independently-Reproducible-ML`
- **FR-1.2** Validate exactly 255 paper rows are loaded
- **FR-1.3** Extract `reproducibility_label` column (binary 0/1) as DV
- **FR-1.4** Extract all unique dataset names referenced across papers
- **FR-1.5** Extract `venue`, `year`, `equations`, `pseudocode`, `hyperparameters`, `reference_implementation` columns

### FR-2: HuggingFace Hub Card Coverage Check

- **FR-2.1** For each unique dataset name from FR-1.4, attempt `DatasetCard.load(name)` via `huggingface_hub`
- **FR-2.2** On success: parse `.data.to_dict()` and check presence of 7 fields: `intended_use`, `out_of_scope_use`, `limitations`, `license`, `task_categories`, `dataset_info`, `provenance`
- **FR-2.3** Compute normalized field-presence score per dataset: `n_fields_present / 7`
- **FR-2.4** Compute aggregate `hf_card_coverage_rate = n_found / n_total_unique_datasets`
- **FR-2.5** Handle 403/404 gracefully: mark as "not found", do not crash
- **FR-2.6** Log each query result: `"HF card found: {name}, score={score:.2f}"` or `"HF card not found: {name}"`

### FR-3: OpenML Temporal Coverage Check

- **FR-3.1** Retrieve full OpenML dataset list: `openml.datasets.list_datasets(output_format='dataframe')`
- **FR-3.2** Parse `upload_date` column to datetime (handle NaT/nulls)
- **FR-3.3** For each unique dataset name from FR-1.4, look up matching rows in OpenML by name (case-insensitive)
- **FR-3.4** Filter to pre-publication rows: `upload_date.dt.year < paper_publication_year`
- **FR-3.5** Count datasets with ≥1 pre-publication OpenML entry as "valid"
- **FR-3.6** Compute `openml_temporal_filter_success_rate = n_valid / n_total_unique_datasets`

### FR-4: Mechanism Activation Verification

- **FR-4.1** Implement `verify_pipeline_activated(results)` per Phase 2C spec, checking:
  - `raff_n_papers == 255`
  - `hf_n_queried > 0`
  - `openml_n_queried > 0`
  - `"hf_coverage_rate" in results`

### FR-5: Results Reporting

- **FR-5.1** Output structured results dict with all metrics
- **FR-5.2** Generate gate pass/fail determination
- **FR-5.3** Save results to JSON file for audit
- **FR-5.4** Print human-readable summary to stdout

### FR-6: Visualization

- **FR-6.1** Gate metrics comparison bar chart: `hf_coverage_rate` vs 0.50 threshold; `openml_filter_success_rate` vs 0.70 threshold (green=pass, red=fail)
- **FR-6.2** HF field-presence heatmap: datasets × 7 fields
- **FR-6.3** OpenML pre-publication run count distribution histogram
- **FR-6.4** Raff dataset frequency bar chart (papers per unique dataset)

---

## 4. Data Specification

### DS-1: Raff 2019 Corpus

| Property | Value |
|----------|-------|
| Source | `github.com/EdwardRaff/Quantifying-Independently-Reproducible-ML` |
| Format | CSV/spreadsheet |
| N | 255 papers |
| Key columns | paper_id, reproducibility_label (0/1), dataset, venue, year, equations, pseudocode, hyperparameters, reference_implementation |
| Access | `git clone` → `pd.read_csv()` |
| Split | Full N=255 (no train/test; feasibility check) |

### DS-2: HuggingFace Hub Cards (via API)

| Property | Value |
|----------|-------|
| Source | HuggingFace Hub API (`huggingface_hub`) |
| Access | `DatasetCard.load(name)` per dataset |
| Fields scored | intended_use, out_of_scope_use, limitations, license, task_categories, dataset_info, provenance |
| Rate limit | ~1 req/sec |

### DS-3: OpenML Dataset Registry (via API)

| Property | Value |
|----------|-------|
| Source | OpenML API (`openml`) |
| Access | `list_datasets(output_format='dataframe')` — one bulk call |
| Key field | `upload_date` (for temporal filtering) |
| Temporal filter | Client-side pandas: `upload_date.dt.year < paper_year` |

---

## 5. Non-Functional Requirements

- **NFR-1: Reproducibility** — Script is deterministic; same output given same Raff CSV + API state
- **NFR-2: Error Tolerance** — Individual dataset API failures must not crash pipeline; log and continue
- **NFR-3: Rate Limiting** — HF Hub: 1 req/sec sleep between calls; OpenML: single bulk query
- **NFR-4: Transparency** — All query outcomes logged; fail reasons documented
- **NFR-5: Runtime** — Complete within 60 minutes on standard internet connection
- **NFR-6: Auth Handling** — Attempt `token=None` first; fall back to env `HF_TOKEN` if 403 received

---

## 6. Evaluation Metrics

| Metric | Formula | Pass Threshold | Measurement |
|--------|---------|----------------|-------------|
| `hf_card_coverage_rate` | `n_hf_found / n_unique_datasets` | ≥ 0.50 | FR-2.4 |
| `openml_temporal_filter_success_rate` | `n_valid_openml / n_unique_datasets` | ≥ 0.70 | FR-3.6 |
| `raff_labels_parseable` | CSV loads with 255 rows + required columns | True | FR-1.2 |
| `mechanism_activated` | All 4 activation indicators True | True | FR-4.1 |

**Gate Pass Condition:** ALL of:
1. `raff_labels_parseable == True`
2. `hf_card_coverage_rate >= 0.50`
3. `openml_temporal_filter_success_rate >= 0.70`

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Min Version | Purpose |
|---------|-------------|---------|
| `huggingface_hub` | ≥ 0.20 | HF card API |
| `openml` | ≥ 0.14 | OpenML API |
| `pandas` | ≥ 2.0 | DataFrame ops + temporal filtering |
| `requests` | ≥ 2.28 | HTTP fallback |
| `matplotlib` | ≥ 3.7 | Visualizations |
| `seaborn` | ≥ 0.12 | Heatmap |
| `numpy` | ≥ 1.24 | Numeric ops |
| `pyyaml` | ≥ 6.0 | Results serialization |

### 7.2 External Repositories

| Repo | Purpose |
|------|---------|
| `EdwardRaff/Quantifying-Independently-Reproducible-ML` | Raff corpus CSV (DV + paper list) |

### 7.3 Environment

- Python ≥ 3.9
- Internet access (HF Hub API + OpenML API)
- Optional: `HF_TOKEN` env var for authenticated HF Hub access

---

## 8. Success Criteria

**PoC Pass:**
1. Script executes end-to-end without unhandled exceptions
2. `raff_labels_parseable == True` (255 papers loaded)
3. `hf_card_coverage_rate >= 0.50`
4. `openml_temporal_filter_success_rate >= 0.70`
5. All 4 visualizations generated

**Expected Performance (from research):**
- HF coverage: ~60–80% for well-known benchmarks (CIFAR-10, MNIST, ImageNet, IMDB)
- OpenML temporal filter: ~70–80% (established benchmarks pre-date Raff's 2017 cutoff)

---

## 9. Out of Scope

- Training any ML model
- Computing reproducibility predictions
- Accessing private HF Hub repositories requiring institutional credentials
- Computing final feature vectors for H-M1/M2/M3 (deferred to those hypotheses)
