# Configuration: H-M2
## NLI Clustering Aggregation Behavior Analysis

**Hypothesis:** H-M2 (MECHANISM — Causal Step 2)
**Type:** INCREMENTAL (builds on H-M1)
**Date:** 2026-05-11

Applied: pure-analysis-no-training pattern
Applied: bootstrap-percentile-CI pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 + H-E1)
**Status**: config classes verified from base code
**Config Files Found**: `h-m1/code/config.py`, `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    seed: int = 42                              # ← Verified from actual code
    n_bootstrap: int = 1000                     # ← Verified from actual code
    degenerate_threshold: float = 1e-6
    pearson_gate_threshold: float = 0.9
    divergence_sigma_multiplier: float = 1.0
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"
    results_dir: str = "outputs"
    figures_dir: str = "../figures"
    results_file: str = "outputs/experiment_results.json"
    figure_dpi: int = 150
    figure_format: str = "png"
    scatter_figsize: Tuple[int, int] = (8, 8)
    histogram_figsize: Tuple[int, int] = (10, 6)
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

---

## A-7: Gate Evaluation + Results Serialization [Complexity: 9, Budget: 2]

Applied: threshold-decision-tree pattern

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass, field
from typing import Tuple


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
    figure_format: str = "png"
    bar_figsize: Tuple[int, int] = (7, 5)
    histogram_figsize: Tuple[int, int] = (8, 5)
    boxplot_figsize: Tuple[int, int] = (7, 5)
    cdf_figsize: Tuple[int, int] = (8, 5)
    bar_type_figsize: Tuple[int, int] = (9, 5)


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
```

### Gate Decision Logic

```python
# Gate thresholds for evaluate_gate() in analysis.py
# PASS:    aggregation_rate >= 0.50 AND ci_lower >= 0.30
# PARTIAL: 0.30 <= aggregation_rate < 0.50
# PIVOT:   aggregation_rate < 0.30
#
# Non-standard: PARTIAL band [0.30, 0.50) is a weak-pass zone — documents
# borderline cases without triggering full PIVOT.
```

### Results JSON Schema

```python
RESULTS_SCHEMA = {
    "required_keys": [
        "hypothesis_id",       # str: "h-m2"
        "cluster_count_source",# str: "se_json" | "hm1_summary" | "nli_recluster"
        "n_examples",          # int: 2000
        "mean_cluster_count",  # float
        "std_cluster_count",   # float
        "median_cluster_count",# float
        "histogram",           # dict: {"1": int, "2": int, "3": int, "4": int, "5": int}
        "aggregation_rate",    # float [0,1]
        "collapse_rate",       # float [0,1]
        "bootstrap_ci_lower",  # float
        "bootstrap_ci_upper",  # float
        "gate_pass",           # bool
        "gate_result",         # str: "PASS" | "PARTIAL" | "PIVOT"
        "r_pb",                # float
        "p_value",             # float
        "stratified_aggregation", # dict | null
        "timestamp",           # str: ISO-8601
    ]
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Gate logic config | Threshold constants (0.50, 0.30) for PASS/PARTIAL/PIVOT in evaluate_gate(); non-standard PARTIAL band documented |
| C-7-2 | Results JSON schema | Required keys list for validate_results_schema() in run_experiment.py; used by unit tests |

---

## A-9: Figures — Additional [Complexity: 9, Budget: 2]

Applied: matplotlib-seaborn-standard-figure-config pattern

### Visualization Config Table

| Figure | Filename | figsize | DPI | Colors | Labels |
|--------|----------|---------|-----|--------|--------|
| Aggregation rate bar + CI | `aggregation_rate.png` | (7, 5) | 150 | bar: `#4C72B0`; threshold line: `#DD8452` dashed | x: "Metric", y: "Rate", title: "Aggregation Rate vs Gate Threshold" |
| Cluster count histogram | `cluster_count_dist.png` | (8, 5) | 150 | `#4C72B0` | x: "Cluster Count", y: "Frequency", title: "Cluster Count Distribution (N=2000)" |
| Cluster count by label (box) | `cluster_count_by_label.png` | (7, 5) | 150 | hallucinated: `#DD8452`; factual: `#4C72B0` | x: "Hallucination Label (0=Factual, 1=Hallucinated)", y: "Cluster Count", title: "Cluster Count by Hallucination Label" |
| CDF with threshold line | `cluster_count_cdf.png` | (8, 5) | 150 | cdf line: `#4C72B0`; threshold: `#DD8452` dashed | x: "Cluster Count", y: "CDF", title: "CDF of Cluster Counts (threshold=4)" |
| Aggregation by type | `aggregation_by_type.png` | (9, 5) | 150 | `#4C72B0` | x: "Question Type", y: "Aggregation Rate", title: "Aggregation Rate by Question Type" |

### Figure Config Constants

```python
# In visualize.py — use these values directly
FIGURE_COLORS = {
    "primary": "#4C72B0",
    "secondary": "#DD8452",
    "threshold_line": "#DD8452",
}
THRESHOLD_LINESTYLE = "--"
THRESHOLD_LINEWIDTH = 2.0
CDF_THRESHOLD_VALUE = 4   # N-1 = 5-1; vertical line at x=4 in CDF plot
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Per-figure size/color config | figsize, colors, axis labels for all 4 figures; seaborn palette alignment |
| C-9-2 | CDF threshold marker config | CDF_THRESHOLD_VALUE=4 (N-1), linestyle/width for threshold vertical line; skip aggregation_by_type.png if stratified_aggregation is None |

---

## A-11: Unit Tests [Complexity: 10, Budget: 2]

Applied: pytest-fixture-mock-data pattern

### Test Fixture Config

```python
# tests/conftest.py
import numpy as np
import pytest

@pytest.fixture
def cluster_counts_pass():
    """PASS case: low cluster counts → high aggregation rate (~0.80)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([1, 2, 3, 4], size=2000, p=[0.05, 0.15, 0.30, 0.50])
    return counts.astype(int)

@pytest.fixture
def cluster_counts_pivot():
    """PIVOT case: high cluster counts → low aggregation rate (~0.13, H-M1 realistic)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([3, 4, 5], size=2000, p=[0.03, 0.10, 0.87])
    return counts.astype(int)

@pytest.fixture
def cluster_counts_partial():
    """PARTIAL case: medium aggregation rate (~0.38)."""
    rng = np.random.default_rng(42)
    counts = rng.choice([2, 3, 4, 5], size=2000, p=[0.05, 0.10, 0.23, 0.62])
    return counts.astype(int)

@pytest.fixture
def mock_labels():
    """1000 hallucinated (1) + 1000 factual (0), seed=42."""
    rng = np.random.default_rng(42)
    labels = np.array([0] * 1000 + [1] * 1000)
    rng.shuffle(labels)
    return labels
```

### Expected Gate Results per Fixture

| Fixture | Expected aggregation_rate (approx) | Expected gate_result |
|---------|-------------------------------------|----------------------|
| `cluster_counts_pass` | ~0.80 | PASS |
| `cluster_counts_pivot` | ~0.13 | PIVOT |
| `cluster_counts_partial` | ~0.38 | PARTIAL |

### Test File Structure

```python
# tests/test_analysis.py — key assertions
def test_compute_aggregation_rate_pass(cluster_counts_pass):
    rate = compute_aggregation_rate(cluster_counts_pass, n_samples=5)
    assert rate >= 0.50

def test_compute_aggregation_rate_pivot(cluster_counts_pivot):
    rate = compute_aggregation_rate(cluster_counts_pivot, n_samples=5)
    assert rate < 0.30

def test_evaluate_gate_pass(cluster_counts_pass):
    cfg = ExperimentConfig()
    result = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    assert evaluate_gate(result, cfg) == "PASS"

def test_evaluate_gate_pivot(cluster_counts_pivot):
    cfg = ExperimentConfig()
    result = bootstrap_aggregation_ci(cluster_counts_pivot, n_resamples=200, seed=42)
    assert evaluate_gate(result, cfg) == "PIVOT"

def test_compute_collapse_rate(cluster_counts_pivot):
    rate = compute_collapse_rate(cluster_counts_pivot)
    assert 0.0 <= rate <= 1.0

def test_bootstrap_ci_shape(cluster_counts_pass):
    result = bootstrap_aggregation_ci(cluster_counts_pass, n_resamples=200, seed=42)
    assert {"aggregation_rate", "ci_lower", "ci_upper", "gate_pass"} <= result.keys()

# tests/test_data_loader.py — key assertions
def test_validate_cluster_counts_clamp():
    counts = np.array([0, 1, 3, 5, 6])
    validated = validate_cluster_counts(counts, n=5)
    assert validated.min() >= 1
    assert validated.max() <= 5

def test_validate_cluster_counts_length():
    counts = np.ones(2000, dtype=int)
    validated = validate_cluster_counts(counts, n=2000)
    assert len(validated) == 2000
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | Fixture definitions | conftest.py with cluster_counts_pass, cluster_counts_pivot, cluster_counts_partial, mock_labels; seed=42 for all |
| C-11-2 | Test assertions config | Expected gate results per fixture; n_resamples=200 for test bootstrap (fast); key assertion list for test_analysis.py and test_data_loader.py |

---

## YAML Config Schema

```yaml
# h-m2/code/config.yaml (mirrors ExperimentConfig dataclass)
seed: 42
n_bootstrap: 1000
n_samples_per_example: 5
aggregation_gate_threshold: 0.50
aggregation_ci_lower_threshold: 0.30
collapse_rate_threshold: 0.20
correlation_threshold: 0.10

paths:
  se_scores_path: "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
  stochastic_samples_path: "../../h-e1/code/outputs/stochastic_samples.jsonl"
  dataset_path: "../../h-e1/code/data/halueval_qa_2k.json"
  hm1_results_path: "../../h-m1/code/outputs/experiment_results.json"
  h_e1_code_dir: "../../h-e1/code"
  results_dir: "outputs"
  figures_dir: "../figures"

visualization:
  figure_dpi: 150
  figure_format: "png"
  bar_figsize: [7, 5]
  histogram_figsize: [8, 5]
  boxplot_figsize: [7, 5]
  cdf_figsize: [8, 5]
  bar_type_figsize: [9, 5]
  colors:
    primary: "#4C72B0"
    secondary: "#DD8452"
  cdf_threshold_value: 4
```
