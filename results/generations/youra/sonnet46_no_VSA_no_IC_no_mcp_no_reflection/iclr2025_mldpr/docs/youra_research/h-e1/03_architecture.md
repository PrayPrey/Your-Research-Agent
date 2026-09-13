---
title: "Architecture: H-E1 — Data Acquisition Pipeline Feasibility"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
---

Applied: data-pipeline-sequential-orchestrator pattern
Applied: coverage-audit-script pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

# Architecture: H-E1

## File Structure

```
docs/youra_research/h-e1/code/
├── pipeline.py        # main orchestrator + all module classes
├── config.py          # thresholds, field lists, paths
├── requirements.txt   # pinned dependencies
└── results/           # auto-created at runtime
    ├── results.json
    └── figures/
        ├── gate_metrics.png
        ├── hf_field_heatmap.png
        ├── openml_run_dist.png
        └── dataset_freq.png
```

All logic lives in `pipeline.py` — single file is sufficient for a deterministic script of this scope.

---

## Modules

### RaffParser (`pipeline.py`)

**Dependencies**: pandas

```python
class RaffParser:
    def __init__(self, csv_path: str): ...
    def load(self) -> pd.DataFrame: ...          # returns 255-row df, raises if != 255
    def unique_datasets(self) -> list[str]: ...  # unique dataset names
    def paper_years(self) -> dict[str, int]: ... # dataset -> earliest paper year
```

### HFCoverageChecker (`pipeline.py`)

**Dependencies**: huggingface_hub, config.HF_FIELDS

```python
class HFCoverageChecker:
    def __init__(self, fields: list[str], token: str | None = None): ...
    def check_all(self, dataset_names: list[str]) -> dict: ...
    # returns: {name: float|None} — float=field_score, None=not found
    def aggregate(self, scores: dict) -> dict: ...
    # returns: {coverage_rate, mean_field_score, n_found, n_queried, per_dataset: dict}
```

### OpenMLTemporalChecker (`pipeline.py`)

**Dependencies**: openml, pandas

```python
class OpenMLTemporalChecker:
    def __init__(self): ...
    def fetch_all(self) -> pd.DataFrame: ...         # single bulk API call
    def check_all(self, dataset_names: list[str],
                  paper_years: dict[str, int],
                  openml_df: pd.DataFrame) -> dict: ...
    # returns: {filter_success_rate, n_valid, n_queried, pre_pub_counts: dict}
```

### MetricsAggregator (`pipeline.py`)

**Dependencies**: config.THRESHOLDS

```python
class MetricsAggregator:
    def __init__(self, thresholds: dict): ...
    def compute(self, raff_df: pd.DataFrame,
                hf_result: dict,
                openml_result: dict) -> dict: ...
    # returns full results dict with gate_pass bool
    def verify_pipeline_activated(self, results: dict) -> tuple[bool, dict]: ...
```

### Visualizer (`pipeline.py`)

**Dependencies**: matplotlib, seaborn, results dict

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def gate_metrics_bar(self, results: dict) -> None: ...
    def hf_field_heatmap(self, per_dataset: dict, fields: list[str]) -> None: ...
    def openml_run_histogram(self, pre_pub_counts: dict) -> None: ...
    def dataset_freq_bar(self, raff_df: pd.DataFrame) -> None: ...
```

### PipelineOrchestrator (`pipeline.py`)

**Dependencies**: all above modules, config

```python
class PipelineOrchestrator:
    def __init__(self, config: dict): ...
    def run(self) -> dict: ...   # executes all steps, saves results.json, returns results
```

---

## Config (`config.py`)

```python
RAFF_CSV_PATH: str = "data/raff_corpus.csv"
HF_FIELDS: list[str] = [
    "intended_use", "out_of_scope_use", "limitations",
    "license", "task_categories", "dataset_info", "provenance"
]
THRESHOLDS: dict = {
    "hf_coverage_rate": 0.50,
    "openml_temporal_filter_success_rate": 0.70,
}
HF_RATE_LIMIT_SEC: float = 1.0
RESULTS_DIR: str = "results"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Setup & Config | Project structure, requirements.txt, config.py, results dir, Raff CSV clone | 5 | 1+1+1+2=5 |
| E1-2 | RaffParser | Load CSV, validate 255 rows, extract unique datasets + paper years | 7 | 2+1+2+2=7 |
| E1-3 | HFCoverageChecker | Query HF Hub per dataset, field-presence scoring, rate limiting, 403/404 handling | 12 | 3+2+3+4=12 |
| E1-4 | OpenMLTemporalChecker | Bulk fetch OpenML list, client-side temporal filter per dataset | 10 | 2+2+3+3=10 |
| E1-5 | MetricsAggregator | Compute coverage rates, gate pass/fail, activation verification, JSON output | 8 | 2+2+2+2=8 |
| E1-6 | Visualizer | 4 required figures (bar, heatmap, histogram, freq bar) | 9 | 2+1+3+3=9 |
| E1-7 | PipelineOrchestrator | Wire all modules, end-to-end run, stdout summary, results.json save | 7 | 2+3+1+1=7 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-3, E1-4, E1-6], Low(4-8): [E1-1, E1-2, E1-5, E1-7]

---

## Execution Entry Point

```
python pipeline.py --raff-csv path/to/raff_corpus.csv [--hf-token TOKEN]
```

Pipeline exits with code 0 if gate passes, 1 if gate fails.
