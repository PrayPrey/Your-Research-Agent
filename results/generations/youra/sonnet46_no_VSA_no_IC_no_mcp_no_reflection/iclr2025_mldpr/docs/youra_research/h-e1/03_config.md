---
title: "Config: H-E1 — Data Acquisition Pipeline Feasibility"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-31"
---

Applied: data-pipeline-sequential-orchestrator pattern
Applied: coverage-audit-script pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: module-level constants (hardcoded dict/list)

---

# Config: H-E1

## Main Config (`config.py`)

```python
import os

RAFF_CSV_PATH: str = "data/raff_corpus.csv"

HF_FIELDS: list[str] = [
    "intended_use",
    "out_of_scope_use",
    "limitations",
    "license",
    "task_categories",
    "dataset_info",
    "provenance",
]

THRESHOLDS: dict = {
    "hf_coverage_rate": 0.50,
    "openml_temporal_filter_success_rate": 0.70,
}

HF_RATE_LIMIT_SEC: float = 1.0
RESULTS_DIR: str = "results"
HF_TOKEN: str | None = os.environ.get("HF_TOKEN", None)
```

---

## C-E1-6-1: Visualizer Configuration [Complexity: 5, Budget: 1]

**Applied**: Standard matplotlib/seaborn defaults

```python
VIZ_CONFIG = {
    "gate_metrics_bar": {
        "figsize": (7, 4),
        "colors": {"pass": "#2ecc71", "fail": "#e74c3c"},   # green / red
        "threshold_linestyle": "--",
        "threshold_color": "black",
        "threshold_linewidth": 1.5,
        "ylabel": "Rate",
        "title": "Gate Metrics vs Thresholds",
    },
    "hf_field_heatmap": {
        "figsize": (12, 8),
        "cmap": "YlGn",
        "xticklabel_rotation": 45,
        "yticklabel_fontsize": 8,
        "title": "HF Field Presence per Dataset",
    },
    "openml_run_histogram": {
        "figsize": (8, 4),
        "bins": 20,
        "xlabel": "Pre-publication OpenML run count",
        "ylabel": "Number of datasets",
        "title": "OpenML Pre-publication Run Distribution",
    },
    "dataset_freq_bar": {
        "figsize": (12, 5),
        "top_n": 30,          # show top-30 datasets by paper frequency
        "xlabel_rotation": 45,
        "ylabel": "Paper count",
        "title": "Dataset Frequency in Raff Corpus (Top 30)",
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-6-1 | Visualizer params | Figure sizes, colors, threshold styling, top-N cutoff for all 4 plots |

---

## C-E1-6-2: Results Output Schema [Complexity: 4, Budget: 1]

**Applied**: Standard JSON schema pattern

### Python dataclass

```python
from dataclasses import dataclass, field

@dataclass
class RaffSection:
    n_papers: int = 0
    n_unique_datasets: int = 0

@dataclass
class HFSection:
    coverage_rate: float = 0.0
    mean_field_score: float = 0.0
    n_found: int = 0
    n_queried: int = 0
    per_dataset: dict = field(default_factory=dict)  # {name: float|None}

@dataclass
class OpenMLSection:
    filter_success_rate: float = 0.0
    n_valid: int = 0
    n_queried: int = 0
    pre_pub_counts: dict = field(default_factory=dict)  # {name: int}

@dataclass
class GateSection:
    pass_: bool = False          # field named pass_ to avoid keyword clash
    hf_coverage_pass: bool = False
    openml_temporal_pass: bool = False
    raff_parseable: bool = False

@dataclass
class ActivationSection:
    raff_n_papers_ok: bool = False
    hf_n_queried_ok: bool = False
    openml_n_queried_ok: bool = False
    hf_coverage_rate_present: bool = False
    all_activated: bool = False

@dataclass
class ResultsSchema:
    hypothesis_id: str = "H-E1"
    date: str = ""
    runtime_sec: float = 0.0
    raff: RaffSection = field(default_factory=RaffSection)
    hf: HFSection = field(default_factory=HFSection)
    openml: OpenMLSection = field(default_factory=OpenMLSection)
    gate: GateSection = field(default_factory=GateSection)
    activation: ActivationSection = field(default_factory=ActivationSection)
```

### Example `results.json`

```json
{
  "hypothesis_id": "H-E1",
  "date": "2026-08-31",
  "runtime_sec": 312.4,
  "raff": {
    "n_papers": 255,
    "n_unique_datasets": 47
  },
  "hf": {
    "coverage_rate": 0.68,
    "mean_field_score": 0.43,
    "n_found": 32,
    "n_queried": 47,
    "per_dataset": {
      "mnist": 0.71,
      "cifar-10": 0.57,
      "imdb": null
    }
  },
  "openml": {
    "filter_success_rate": 0.74,
    "n_valid": 35,
    "n_queried": 47,
    "pre_pub_counts": {
      "mnist": 412,
      "cifar-10": 198
    }
  },
  "gate": {
    "pass": true,
    "hf_coverage_pass": true,
    "openml_temporal_pass": true,
    "raff_parseable": true
  },
  "activation": {
    "raff_n_papers_ok": true,
    "hf_n_queried_ok": true,
    "openml_n_queried_ok": true,
    "hf_coverage_rate_present": true,
    "all_activated": true
  }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-6-2 | Results schema | Dataclass + example JSON for results.json (metadata, raff, hf, openml, gate, activation) |
