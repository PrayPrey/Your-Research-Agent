# Architecture: H-E1
# DTS-Weighted Documentation Completeness Scoring System (EXISTENCE PoC)

**Date:** 2026-03-15
**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC) — LIGHT tier

Applied: rate-limited-api-collection-with-json-cache
Applied: binary-field-presence-scoring-pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code. All modules defined fresh per PRD specifications.

---

## File Structure

```
h-e1/code/
  collect_hf.py       # HuggingFace Hub API collection + caching
  collect_openml.py   # OpenML API collection + caching
  collect_uci.py      # UCI ML Repository collection + caching
  scorer.py           # DTS weighted + unweighted scoring
  validation.py       # Human-automated Pearson r + bootstrap CI
  visualization.py    # 5 required figures
  evaluate.py         # Gate metrics + mechanism activation check
  experiment.py       # Main entry point (pipeline orchestration)
h-e1/data/
  raw_cache/          # JSON cache: {repo}_{dataset_id}.json
  corpus.csv          # Processed metadata (all repos, one row per dataset)
  validation/
    human_annotation_template.csv
    human_annotations.csv
h-e1/results/
  h_e1_results.json
h-e1/figures/
  gate_metrics_comparison.png
  per_section_coverage_heatmap.png
  dts_score_distribution.png
  human_automated_scatter.png
  missing_field_analysis.png
```

---

## Module Definitions

### HFCollector (`collect_hf.py`)

**Dependencies**: huggingface_hub, pandas, json, time, tqdm

```python
SEED = 42
HF_RATE_LIMIT = 1.0  # req/sec unauthenticated; 0.2 authenticated

def collect_hf_datasets(
    n_samples: int = 500,
    cache_dir: str = "data/raw_cache",
    hf_token: str | None = None,
    pilot: bool = False,
) -> pd.DataFrame: ...
# Returns DataFrame with columns: dataset_id, repository, task_category,
# upload_year, [18 binary field columns], in_human_subsample

def load_or_fetch_hf(
    dataset_id: str,
    cache_dir: str,
    api: "HfApi",
) -> dict: ...
# Returns raw metadata dict; reads from JSON cache if exists

def stratified_sample_hf(
    dataset_list: list,
    n: int,
    seed: int = SEED,
) -> list: ...
# Stratifies by task_category × upload_year bins (8 bins)
```

---

### OpenMLCollector (`collect_openml.py`)

**Dependencies**: openml, pandas, json, tqdm

```python
def collect_openml_datasets(
    n_samples: int = 200,
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame: ...

def load_or_fetch_openml(
    dataset_id: int,
    cache_dir: str,
) -> dict: ...

def stratified_sample_openml(
    df: pd.DataFrame,
    n: int,
    seed: int = 42,
) -> pd.DataFrame: ...
# Stratifies by task_type
```

---

### UCICollector (`collect_uci.py`)

**Dependencies**: ucimlrepo, requests, pandas, json, time, tqdm

```python
UCI_RATE_LIMIT = 2.0  # seconds between requests

def collect_uci_datasets(
    cache_dir: str = "data/raw_cache",
    pilot: bool = False,
) -> pd.DataFrame: ...
# Full population approach (~100 datasets)

def load_or_fetch_uci(
    dataset_id: int,
    cache_dir: str,
) -> dict: ...
# Tries ucimlrepo first; falls back to UCI REST API

def fetch_uci_rest_fallback(dataset_id: int) -> dict: ...
# GET /static/public/{id}/ fallback
```

---

### DTSScorer (`scorer.py`)

**Dependencies**: numpy, pandas

```python
DTS_SECTIONS: dict[str, list[str]] = {
    "motivation":    ["task_categories", "language", "tags", "license"],
    "composition":   ["size_categories", "num_rows", "num_columns", "features"],
    "collection":    ["source_datasets", "annotations_creators", "original_data_url"],
    "preprocessing": ["preprocessing_steps", "data_augmentation", "data_splits"],
    "uses":          ["known_limitations", "out_of_scope_use", "discussion_best_use"],
    "distribution":  ["license", "citation", "contact", "maintenance_plan"],
}

DTS_WEIGHTS: dict[str, float] = {
    "motivation": 1.0, "composition": 0.9, "collection": 2.1,
    "preprocessing": 1.8, "uses": 1.5, "distribution": 0.7,
}

def compute_dts_score(metadata: dict) -> tuple[float, dict[str, float]]: ...
# Returns (weighted_dts_score, {section: coverage_rate})

def compute_unweighted_score(metadata: dict) -> float: ...
# sum(field_present) / total_fields_queried

def score_corpus(df: pd.DataFrame) -> pd.DataFrame: ...
# Applies both scorers; adds weighted_dts_score, unweighted_dts_score,
# per_section_* columns to df

def compute_coverage_rate(df: pd.DataFrame, repo: str | None = None) -> float: ...
# Fraction of datasets with weighted_dts_score > 0; optionally filtered by repo
```

---

### HumanValidator (`validation.py`)

**Dependencies**: pandas, numpy, scipy.stats

```python
def generate_annotation_template(
    corpus: pd.DataFrame,
    n: int = 120,
    per_repo: int = 40,
    seed: int = 42,
    output_path: str = "data/validation/human_annotation_template.csv",
) -> pd.DataFrame: ...
# Stratified subsample; writes CSV for human annotators

def compute_human_dts_scores(
    annotations: pd.DataFrame,
) -> pd.Series: ...
# Applies DTS_SECTIONS + DTS_WEIGHTS to human binary annotations

def compute_pearson_correlation(
    auto_scores: np.ndarray,
    human_scores: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict: ...
# Returns {pearson_r, p_value, ci_lower, ci_upper}
```

---

### Visualizer (`visualization.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def plot_gate_metrics(results: dict, output_path: str) -> None: ...
# FR-V1: bar chart actual vs target (0.70 threshold lines)

def plot_section_coverage_heatmap(df: pd.DataFrame, output_path: str) -> None: ...
# FR-V2: 6 sections × 3 repos heatmap

def plot_dts_distribution(df: pd.DataFrame, output_path: str) -> None: ...
# FR-V3: violin/box plot per repository

def plot_human_automated_scatter(
    auto_scores: np.ndarray,
    human_scores: np.ndarray,
    pearson_r: float,
    output_path: str,
) -> None: ...
# FR-V4: scatter with r annotation

def plot_missing_field_analysis(df: pd.DataFrame, output_path: str) -> None: ...
# FR-V5: per-repo missing field frequency bar chart

def generate_all_figures(
    df: pd.DataFrame,
    results: dict,
    figures_dir: str = "figures",
) -> None: ...
# Calls all 5 plot functions
```

---

### Evaluator (`evaluate.py`)

**Dependencies**: numpy, json

```python
COVERAGE_THRESHOLD = 0.70
PEARSON_THRESHOLD = 0.70
PILOT_MIN_COVERAGE = 0.30

def check_pilot_coverage(pilot_df: pd.DataFrame) -> None: ...
# Raises PilotCoverageFailedError if any repo < 0.30

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]: ...
# Returns (success, indicators_dict) — all 4 indicators must be True

def evaluate_gate(results: dict) -> dict: ...
# Returns {gate_passed, failure_code, failure_message}

def build_results_dict(
    df: pd.DataFrame,
    pearson_stats: dict,
    mechanism_indicators: dict,
) -> dict: ...
# Assembles h_e1_results.json payload

def save_results(results: dict, output_path: str = "results/h_e1_results.json") -> None: ...
```

---

### Experiment (`experiment.py`)

**Dependencies**: all modules above, argparse, os, pathlib

```python
def run_pilot(args: argparse.Namespace) -> None: ...
# 50 datasets per repo; calls check_pilot_coverage; logs estimates

def run_full_collection(args: argparse.Namespace) -> pd.DataFrame: ...
# HF: 500, OpenML: 200, UCI: ~100; caches JSON; returns corpus df

def run_pipeline(args: argparse.Namespace) -> None: ...
# Orchestrates: pilot → collection → scoring → validation template →
# [human annotation pause] → correlation → visualization → results

def parse_args() -> argparse.Namespace: ...
# --pilot-only, --skip-pilot, --hf-token, --cache-dir,
# --human-annotations (path to completed CSV), --output-dir

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args)
```

---

## Module Dependency Graph

```
experiment.py
  -> collect_hf.py    (HFCollector)
  -> collect_openml.py (OpenMLCollector)
  -> collect_uci.py   (UCICollector)
  -> scorer.py        (DTSScorer)
  -> validation.py    (HumanValidator)
  -> visualization.py (Visualizer)
  -> evaluate.py      (Evaluator)
```

scorer.py has no dependencies on other local modules (standalone).
validation.py depends on scorer.py (DTS_SECTIONS, DTS_WEIGHTS for human score computation).
evaluate.py depends on scorer.py constants for threshold checks.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup + Data Collection Infrastructure | Directory structure, requirements.txt, JSON cache layer, rate-limit utilities shared across 3 collectors | 8 | 2+2+2+2 |
| A-2 | Implement HF Collector | HFApi list_datasets, stratified sampling (task_category × year), card_data field extraction, pilot mode | 12 | 3+2+4+3 |
| A-3 | Implement OpenML + UCI Collectors | OpenML bulk listing + stratified sample; UCI ucimlrepo + REST fallback; rate limiting | 11 | 3+2+3+3 |
| A-4 | Implement DTS Scorer | Weighted + unweighted scoring functions, corpus-level application, coverage rate computation | 9 | 2+2+3+2 |
| A-5 | Human Validation + Correlation | Annotation template generation, human DTS score computation, Pearson r + bootstrap CI | 10 | 2+2+4+2 |
| A-6 | Visualization + Evaluation + Results | All 5 figures, mechanism activation check, gate evaluation, results JSON, experiment.py orchestration | 13 | 3+2+4+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-6], Low(4-8): [A-1]

---

## Configuration (Inline — No YAML Required)

Constants defined at module top-level (argparse for runtime overrides):

```python
# experiment.py / scorer.py constants
SEED = 42
N_HF = 500
N_OPENML = 200
N_PILOT_PER_REPO = 50
N_HUMAN_SUBSAMPLE = 120
N_HUMAN_PER_REPO = 40
COVERAGE_THRESHOLD = 0.70
PEARSON_THRESHOLD = 0.70
PILOT_MIN_COVERAGE = 0.30
N_BOOTSTRAP = 1000
HF_RATE_LIMIT_SEC = 1.0   # unauthenticated
HF_RATE_LIMIT_AUTH = 0.2  # authenticated (5 req/sec)
UCI_RATE_LIMIT_SEC = 2.0
```

---

## Execution Flow

1. `python experiment.py --pilot-only` — runs 150-dataset pilot, checks coverage >= 0.30 per repo
2. `python experiment.py` — full collection (800 datasets), scoring, generates `human_annotation_template.csv`
3. Human annotator completes `human_annotations.csv` (offline)
4. `python experiment.py --human-annotations data/validation/human_annotations.csv` — computes Pearson r, generates all figures, saves `h_e1_results.json`

---

*Architecture for H-E1 EXISTENCE PoC — LIGHT tier*
*No neural network training — CPU-only statistical pipeline*
*Green-field implementation from Rondina et al. 2025 + Oreamuno et al. 2024 specifications*
