# Methodology

Our insight — that API ecosystem selection bias, not implementation error, explains metadata coverage gaps — demands a pipeline design that can distinguish between the two. This section describes the infrastructure feasibility study (H-E1) that implements and executes this distinction.

## Study Design

We design H-E1 as a *gate hypothesis*: a pre-specified infrastructure feasibility check with binary outcome that must pass before any regression analysis proceeds. This design is motivated by the risk of running statistical analysis on severely incomplete data — with 30% independent variable coverage, any regression coefficients would be confounded with the domain distribution of datasets with cards, not the domain distribution of datasets in Raff's corpus.

The gate criteria are pre-specified (not chosen post-hoc):

- **HF Hub coverage threshold:** ≥50% of Raff's unique datasets must return valid dataset cards
- **OpenML temporal filter threshold:** ≥70% of Raff's unique datasets must have pre-publication OpenML entries valid for Herfindahl-Hirschman Index computation

These thresholds are chosen to ensure that the independent variables (documentation completeness IV1, concentration IV2) are computable for a sufficient fraction of the 255-paper corpus to support valid logistic regression without severe survivorship bias.

## Pipeline Architecture

The H-E1 pipeline consists of five modules orchestrated by a single entry-point script (`pipeline.py`):

**RaffParser** loads Raff's CSV (255 papers, binary reproducibility labels, paper-quality features) and extracts the set of unique benchmark datasets (N=50) with their earliest paper publication years. The parser validates that all expected columns are present and that 255 rows are loaded, raising on violation.

**HFCoverageChecker** queries HuggingFace Hub for each of the 50 datasets using `DatasetCard.load(name)` with canonical dataset names (e.g., "cifar10", "imagenet-1k", "coco"). For each returned card, it computes a field-presence score as the fraction of 7 Datasheets for Datasets schema fields present: `{intended_use, out_of_scope_use, limitations, license, task_categories, dataset_info, provenance}`. Rate limiting (1.0s sleep between requests) prevents API throttling. HTTP 403 errors (authentication required) and 404 errors (dataset not found) are explicitly handled and distinguished in the output.

**Rationale for canonical names:** A reproducibility auditing pipeline must be automatable. Canonical dataset names (those used in Raff's CSV) are the correct interface for a scalable pipeline; requiring manual curation of namespace variants defeats the purpose of automated auditing.

**OpenMLTemporalChecker** performs a single bulk API call (`openml.datasets.list_datasets(output_format='dataframe')`) to retrieve all available OpenML datasets with metadata including upload date. It then applies a client-side temporal filter: for each of the 50 Raff datasets, it checks whether a matching OpenML entry exists with `upload_date_year < paper_publication_year`. This filter ensures that pre-publication run counts (the HHI proxy) are computable without contaminating the measurement with post-publication community use.

**Rationale for bulk fetch over per-dataset query:** A single bulk fetch avoids N=50 sequential API calls and provides a complete picture of OpenML's dataset catalog, enabling root-cause analysis of which dataset types are absent.

**MetricsAggregator** computes the two gate metrics from checker outputs and evaluates pass/fail against pre-specified thresholds. It additionally verifies *pipeline activation*: all four activation indicators must be true (HF API reachable, OpenML API reachable, Raff CSV parseable, temporal filter executable) before gate pass/fail is meaningful. A gate fail without all activation indicators is an implementation defect, not an infrastructure finding.

**Visualizer** generates three figures from the measurement results: a gate metrics bar chart (both API coverage rates vs. thresholds), an OpenML pre-publication run count distribution histogram, and an HF card field-presence heatmap (15 found datasets × 7 schema fields).

## Test Suite

An 18-test pytest suite covers all pipeline components. Tests are run against the live pipeline (no mocking) to ensure that the 30% and 22% coverage figures are reproducible by any researcher with API access. Tests verify: correct Raff CSV parsing (255 rows, all columns), HF Hub card loading and field scoring, OpenML temporal filtering, gate evaluation, and figure generation. All 18 tests pass.

**Rationale for no mocking:** Mocking the HF Hub or OpenML API would produce a test suite that validates the pipeline implementation but cannot detect platform scope limitations — precisely the discovery we are trying to make. Live API tests are the only valid approach for an infrastructure feasibility study.

## Experimental Protocol

The pipeline executes end-to-end in a single run:

```
python pipeline.py --raff-csv data/raff_repo/reproducable_blind.csv
```

Runtime: 88.84 seconds on a standard CPU (dominated by 50 × 1.0s HF rate-limit sleeps). Output: `results/results.json` (structured measurement results), three figures in `results/figures/`, and a stdout summary with gate pass/fail verdict.

## Pre-Specified Thresholds and Gate Logic

The gate uses AND logic: *both* HF coverage rate ≥50% AND OpenML temporal filter success rate ≥70% must hold for the gate to pass. A partial pass (one threshold met, one not) would indicate partial infrastructure adequacy; downstream mechanism hypotheses (H-M1, H-M2, H-M3) require both independent variables to be computable.

The hypothesis hierarchy implements cascade blocking: H-M1 (documentation completeness → reproducibility) requires IV1 (completeness), which requires HF coverage ≥50%. H-M2 (concentration HHI → reproducibility) requires IV2 (HHI), which requires OpenML coverage ≥70%. H-M3 (field-level importance ordering) requires both. If H-E1 gate fails, all downstream hypotheses are blocked — running regression on 30% IV1 coverage would produce biased, uninterpretable results.
