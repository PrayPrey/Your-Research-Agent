# Architecture: H-M2
## NLI Clustering Aggregation Behavior Analysis

**Hypothesis:** H-M2 (MECHANISM — Causal Step 2)
**Type:** INCREMENTAL (builds on H-M1, H-E1)
**Date:** 2026-05-11
**Infrastructure:** FULL

Applied: pure-analysis-no-training pattern
Applied: incremental-hypothesis-sys-path-reuse pattern
Applied: bootstrap-percentile-CI pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 + H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `h-m1/code/` and `h-e1/code/`
**Findings**:
- H-M1 flat module structure: `config.py`, `correlation.py`, `divergence.py`, `visualize.py`, `run_experiment.py` — H-M2 mirrors this pattern
- H-E1 data/output paths confirmed: `../../h-e1/code/data/halueval_qa_2k.json`, `../../h-e1/code/outputs/uq_scores/semantic_entropy.json`, `../../h-e1/code/outputs/stochastic_samples.jsonl`
- H-M1 uses `sys.path.insert(0, h_e1_code_dir)` for cross-hypothesis imports — H-M2 reuses same pattern
- `semantic_entropy.json` is a dict keyed by string example ID mapping to float scores; cluster counts are NOT stored per-example — fallback re-clustering from `stochastic_samples.jsonl` is required
- H-M1 `inspect_cluster_distribution()` already implements fallback cluster counting from `stochastic_samples.jsonl`; H-M2 reuses/extends this logic

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_dataset_from_disk | `sys.path + from data import load_dataset_from_disk` | `h-e1/code/data.py` |
| load_nli_pipeline | `sys.path + from uq_signals import load_nli_pipeline, get_semantic_ids_from_pipeline` | `h-e1/code/uq_signals.py` |
| inspect_cluster_distribution | `from correlation import inspect_cluster_distribution` | `h-m1/code/correlation.py` |

**Verified from**: `h-m1/code/` and `h-e1/code/` actual implementation

### Key Data File Paths (relative to `h-m2/code/`)

| File | Relative Path |
|------|---------------|
| HaluEval labels | `../../h-e1/code/data/halueval_qa_2k.json` |
| Semantic entropy scores | `../../h-e1/code/outputs/uq_scores/semantic_entropy.json` |
| Stochastic samples (fallback) | `../../h-e1/code/outputs/stochastic_samples.jsonl` |
| H-M1 cluster summary | `../../h-m1/code/outputs/experiment_results.json` |

---

## File Organization

```
h-m2/
  code/
    config.py          # ExperimentConfig dataclass
    data_loader.py     # Load cluster counts (primary + fallback paths)
    analysis.py        # Aggregation rate, bootstrap CI, correlation, distribution stats
    visualize.py       # All figure generation
    run_experiment.py  # Orchestrator: load → analyze → visualize → save
    tests/
      __init__.py
      test_data_loader.py
      test_analysis.py
      test_visualize.py
  figures/             # Output figures (aggregation_rate.png, etc.)
  outputs/
    experiment_results.json
```

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Analysis parameters
    seed: int = 42
    n_bootstrap: int = 1000
    n_samples_per_example: int = 5
    aggregation_gate_threshold: float = 0.50
    aggregation_ci_lower_threshold: float = 0.30
    collapse_rate_threshold: float = 0.20
    correlation_threshold: float = 0.10

    # Input paths (relative to h-m2/code/)
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"
    hm1_results_path: str = "../../h-m1/code/outputs/experiment_results.json"
    h_e1_code_dir: str = "../../h-e1/code"

    # Output paths (relative to h-m2/code/)
    results_dir: str = "outputs"
    figures_dir: str = "../figures"

    # Visualization
    figure_dpi: int = 150


def get_config() -> ExperimentConfig: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: ExperimentConfig, h-e1/code/uq_signals.py (fallback), h-m1/code/correlation.py (reference)

```python
import numpy as np
from typing import Tuple, List, Dict, Any
from config import ExperimentConfig


def load_labels(cfg: ExperimentConfig) -> np.ndarray:
    """Load hallucination labels from halueval_qa_2k.json. Returns shape (2000,) int array."""
    ...


def load_cluster_counts_from_se_json(se_path: str) -> np.ndarray | None:
    """
    Attempt to extract per-example cluster_count from semantic_entropy.json.
    Returns shape (2000,) int array or None if not stored.
    """
    ...


def load_cluster_counts_from_stochastic_samples(
    samples_path: str,
    nli_pipeline,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """
    Fallback: re-run NLI clustering on stochastic_samples.jsonl using
    bidirectional entailment (lorenzkuhn/semantic_uncertainty pattern).
    Returns shape (2000,) int array.
    """
    ...


def load_cluster_counts(cfg: ExperimentConfig) -> Tuple[np.ndarray, str]:
    """
    Priority loader:
      1. Try load_cluster_counts_from_se_json()
      2. Try H-M1 experiment_results.json cluster_distribution field
      3. Fallback: re-run NLI clustering via load_cluster_counts_from_stochastic_samples()
    Returns (cluster_counts array, source_description string).
    Raises FileNotFoundError if all sources unavailable.
    """
    ...


def validate_cluster_counts(cluster_counts: np.ndarray, n: int = 2000) -> np.ndarray:
    """Assert len==n, clamp values to [1,5], warn on out-of-range. Returns validated array."""
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies**: numpy, scipy.stats, ExperimentConfig

```python
import numpy as np
from typing import Dict, Any
from config import ExperimentConfig


def compute_aggregation_rate(cluster_counts: np.ndarray, n_samples: int = 5) -> float:
    """np.mean(cluster_counts < n_samples)"""
    ...


def compute_collapse_rate(cluster_counts: np.ndarray) -> float:
    """np.mean(cluster_counts == 1)"""
    ...


def compute_distribution_stats(cluster_counts: np.ndarray) -> Dict[str, Any]:
    """
    Returns: mean, std, median, histogram dict {1:int, 2:int, 3:int, 4:int, 5:int}
    """
    ...


def bootstrap_aggregation_ci(
    cluster_counts: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
    n_samples: int = 5,
) -> Dict[str, float]:
    """
    Percentile bootstrap 95% CI on aggregation_rate.
    Returns: {aggregation_rate, ci_lower, ci_upper, gate_pass (bool)}
    gate_pass = aggregation_rate >= 0.50 AND ci_lower >= 0.30
    """
    ...


def compute_pointbiserial_correlation(
    labels: np.ndarray,
    cluster_counts: np.ndarray,
) -> Dict[str, float]:
    """
    scipy.stats.pointbiserialr(labels, cluster_counts).
    Returns: {r_pb, p_value, meaningful (|r_pb| >= 0.10)}
    """
    ...


def stratified_aggregation_by_type(
    cluster_counts: np.ndarray,
    dataset: list,
    n_samples: int = 5,
) -> Dict[str, float] | None:
    """
    If 'question_type' field present in dataset records, compute aggregation_rate per type.
    Returns dict {type: rate} or None if field absent.
    """
    ...


def evaluate_gate(bootstrap_result: Dict[str, Any], cfg: ExperimentConfig) -> str:
    """
    Returns 'PASS', 'PARTIAL', or 'PIVOT' based on aggregation_rate and ci_lower.
    PASS: rate >= 0.50 AND ci_lower >= 0.30
    PARTIAL: 0.30 <= rate < 0.50
    PIVOT: rate < 0.30
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
import numpy as np
from typing import Dict, Any


def plot_aggregation_rate(
    aggregation_rate: float,
    ci_lower: float,
    ci_upper: float,
    gate_threshold: float,
    output_path: str,
) -> None:
    """Bar chart: aggregation rate vs 50% threshold with bootstrap CI error bar."""
    ...


def plot_cluster_count_dist(
    cluster_counts: np.ndarray,
    output_path: str,
) -> None:
    """Histogram of cluster_count values 1–5."""
    ...


def plot_cluster_count_by_label(
    cluster_counts: np.ndarray,
    labels: np.ndarray,
    output_path: str,
) -> None:
    """Box plot of cluster_count for hallucinated (1) vs factual (0)."""
    ...


def plot_cluster_count_cdf(
    cluster_counts: np.ndarray,
    threshold: int,
    output_path: str,
) -> None:
    """CDF of cluster_counts with vertical line at threshold (N-1=4)."""
    ...


def plot_aggregation_by_type(
    type_rates: Dict[str, float],
    output_path: str,
) -> None:
    """Bar chart of aggregation rate by question type. Skipped if type_rates is None."""
    ...
```

---

### run_experiment (`code/run_experiment.py`)

**Dependencies**: all local modules, sys.path for h-e1/code

```python
import sys
from pathlib import Path
from typing import Dict, Any
from config import ExperimentConfig


def run(cfg: ExperimentConfig) -> Dict[str, Any]:
    """
    Orchestrate full H-M2 pipeline:
      [1/6] Load cluster counts (primary → fallback)
      [2/6] Load labels
      [3/6] Validate cluster counts
      [4/6] Compute statistics (aggregation rate, bootstrap CI, distribution, correlation)
      [5/6] Evaluate gate (PASS/PARTIAL/PIVOT)
      [6/6] Generate figures
    Returns complete results dict.
    """
    ...


def save_results(results: Dict[str, Any], results_dir: str) -> None:
    """Serialize to {results_dir}/experiment_results.json."""
    ...


def write_validation_report(results: Dict[str, Any], output_path: str) -> None:
    """Write 04_validation.md with gate decision, all metrics, figure references."""
    ...


if __name__ == "__main__":
    cfg = ExperimentConfig()
    results = run(cfg)
    save_results(results, cfg.results_dir)
    write_validation_report(results, "../../04_validation.md")
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, ExperimentConfig dataclass, path resolution, output dirs | 6 | 2+1+1+2 |
| A-2 | Data Loader — Primary Path | Load cluster counts from semantic_entropy.json or H-M1 results; validate shape and range | 8 | 2+2+2+2 |
| A-3 | Data Loader — Fallback NLI Re-clustering | Re-run bidirectional NLI clustering on stochastic_samples.jsonl via h-e1/uq_signals.py; sys.path injection | 14 | 3+4+4+3 |
| A-4 | Aggregation Rate + Bootstrap CI | np.mean(counts < 5), 1000 bootstrap resamples (seed=42), percentile 95% CI, gate check | 10 | 2+2+4+2 |
| A-5 | Distribution Statistics | Mean, std, median, histogram {1–5}, collapse rate, validate all values | 7 | 2+1+2+2 |
| A-6 | Point-Biserial Correlation | scipy.stats.pointbiserialr(labels, counts), two-tailed p-value, |r| >= 0.10 check | 8 | 2+2+2+2 |
| A-7 | Gate Evaluation + Results Serialization | PASS/PARTIAL/PIVOT logic, experiment_results.json with all metrics, stratified analysis if available | 9 | 2+2+3+2 |
| A-8 | Figures — Required | Aggregation rate bar chart with CI error bar vs 50% threshold; save to figures/ | 7 | 2+1+2+2 |
| A-9 | Figures — Additional | cluster_count_dist.png, cluster_count_by_label.png, cluster_count_cdf.png, aggregation_by_type.png | 9 | 3+1+3+2 |
| A-10 | Validation Report | Write 04_validation.md: gate decision, all metric tables, figure references, PIVOT documentation | 7 | 2+1+2+2 |
| A-11 | Unit Tests | test_data_loader.py, test_analysis.py, test_visualize.py — mock H-E1 outputs, assert shapes and gate logic | 10 | 3+2+3+2 |
| A-12 | End-to-End Integration | run_experiment.py orchestrator, path wiring, error handling for missing files, runtime validation | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-6, A-7, A-9, A-11, A-12], Low(4-8): [A-1, A-2, A-5, A-8, A-10]

---

## Dependency Graph

- A-1 → all
- A-2, A-3 → A-4, A-5, A-6, A-7
- A-4, A-5, A-6 → A-7
- A-7 → A-8, A-9, A-10
- A-2, A-3 → A-11
- A-1 through A-10 → A-12

---

## Results Schema (`experiment_results.json`)

```json
{
  "hypothesis_id": "h-m2",
  "cluster_count_source": "se_json | hm1_summary | nli_recluster",
  "n_examples": 2000,
  "mean_cluster_count": 4.644,
  "std_cluster_count": 0.657,
  "median_cluster_count": 5.0,
  "histogram": {"1": 4, "2": 10, "3": 50, "4": 200, "5": 1736},
  "aggregation_rate": 0.132,
  "collapse_rate": 0.002,
  "bootstrap_ci_lower": 0.115,
  "bootstrap_ci_upper": 0.150,
  "gate_pass": false,
  "gate_result": "PIVOT",
  "r_pb": 0.05,
  "p_value": 0.03,
  "stratified_aggregation": null,
  "timestamp": "2026-05-11T..."
}
```
