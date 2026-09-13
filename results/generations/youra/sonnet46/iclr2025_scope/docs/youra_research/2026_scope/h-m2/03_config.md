# Configuration: h-m2 — Cross-Epsilon Consistency of MLP Activation Sparsity Profiles

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)

Applied: Standard PyTorch dataclass extension pattern (h-e1 verified)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/20260508_scope/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (VERIFIED from actual implementation)
@dataclass
class ExperimentConfig:
    # Model settings
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence lengths
    short_length: int = 128   # replaced by max_length in h-m2
    long_length: int = 512    # replaced by max_length in h-m2

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"   # replaced by results_path in h-m2

    # Gate thresholds
    cv_threshold: float = 0.3    # reused in h-m2
    tau_threshold: float = 0.6   # reused as cross_dist_tau_threshold in h-m2
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

**Key differences in h-m2**:
- `short_length`/`long_length` replaced by single `max_length: int = 512`
- `results_dir` replaced by `results_path` (single JSON file)
- `cv_threshold` retained; `tau_threshold` renamed to `cross_dist_tau_threshold`
- Added: `cv_pass_min_count`, `cross_epsilon_tau_threshold`

---

## A-E2: Config Module [Complexity: 5, Budget: 0 subtasks]

**Applied**: Standard PyTorch defaults

### Configuration (Python Dataclass)

```python
# h-m2/code/config.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-M2 cross-epsilon consistency of activation sparsity profiles."""

    # Model settings
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    n_layers: int = 32
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # Experiment settings
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01

    # Sequence length (single value; h-e1 used short_length/long_length)
    max_length: int = 512

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"

    # Output paths
    figures_dir: str = "h-m2/figures"
    results_path: str = "h-m2/experiment_results.json"

    # Gate thresholds
    cv_threshold: float = 0.3                   # CV gate: profiles must have CV < this
    cv_pass_min_count: int = 3                  # Non-standard: min epsilons that must pass CV gate (out of 4)
    cross_epsilon_tau_threshold: float = 0.7    # Non-standard: Kendall tau threshold for adjacent epsilon pairs
    cross_dist_tau_threshold: float = 0.6       # Secondary metric threshold (renamed from h-e1 tau_threshold)

    def __post_init__(self):
        assert self.n_samples > 0, "n_samples must be positive"
        assert self.batch_size > 0, "batch_size must be positive"
        assert self.n_samples % self.batch_size == 0, (
            f"n_samples ({self.n_samples}) must be divisible by batch_size ({self.batch_size})"
        )
        assert self.primary_epsilon in self.epsilons, (
            f"primary_epsilon ({self.primary_epsilon}) must be in epsilons list {self.epsilons}"
        )
        assert 0.0 < self.cv_threshold < 1.0, "cv_threshold must be in (0, 1)"
        assert 1 <= self.cv_pass_min_count <= len(self.epsilons), (
            f"cv_pass_min_count must be in [1, {len(self.epsilons)}]"
        )
        assert 0.0 < self.cross_epsilon_tau_threshold <= 1.0, (
            "cross_epsilon_tau_threshold must be in (0, 1]"
        )
        assert 0.0 < self.cross_dist_tau_threshold <= 1.0, (
            "cross_dist_tau_threshold must be in (0, 1]"
        )
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
        assert self.n_layers > 0, "n_layers must be positive"
```

---

## YAML Schema

```yaml
# h-m2/code/config.yaml
model:
  name: meta-llama/Meta-Llama-3-8B
  n_layers: 32
  torch_dtype: float16
  device_map: auto

experiment:
  n_samples: 512
  batch_size: 8
  seed: 42
  primary_epsilon: 0.01
  epsilons: [0.001, 0.01, 0.05, 0.1]
  max_length: 512

datasets:
  alpaca:
    name: tatsu-lab/alpaca
  wikitext:
    name: wikitext
    config: wikitext-103-raw-v1

gate_thresholds:
  cv_threshold: 0.3
  cv_pass_min_count: 3
  cross_epsilon_tau_threshold: 0.7
  cross_dist_tau_threshold: 0.6

output:
  figures_dir: h-m2/figures
  results_path: h-m2/experiment_results.json
```

---

## A-8: Visualization Configuration [Complexity: 6, Budget: 2 subtasks]

**Applied**: Standard matplotlib/seaborn defaults

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-8-ST1 | Gate metrics figures | gate_metrics bar chart (2-panel: CV per epsilon + max tau comparison) and cross_epsilon_tau heatmap (4x4 seaborn, vmin=0, vmax=1, annot=True) |
| A-8-ST2 | Profile overlay figures | sparsity_profiles_overlay (4 lines x 32 layers, one color per epsilon) and cv_per_epsilon bar chart with dashed threshold line at 0.3, plus generate_all_figures entry point |

### Visualization Config

```python
# Visualization constants (embed in visualize.py, not a separate config file)
VIZ_CONFIG = {
    # gate_metrics figure
    "gate_metrics_figsize": (12, 5),      # 2-panel side-by-side
    "bar_alpha": 0.8,

    # tau heatmap
    "heatmap_figsize": (8, 6),
    "heatmap_vmin": 0.0,
    "heatmap_vmax": 1.0,
    "heatmap_annot": True,
    "heatmap_fmt": ".2f",
    "heatmap_cmap": "YlOrRd",
    "epsilon_labels": ["0.001", "0.01", "0.05", "0.1"],   # axis tick labels

    # sparsity overlay
    "overlay_figsize": (10, 6),
    "n_layers": 32,
    "layer_x": list(range(32)),           # x-axis: layer indices 0-31
    "overlay_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],  # one per epsilon

    # cv_per_epsilon bar chart
    "cv_bar_figsize": (8, 5),
    "cv_threshold_linestyle": "--",
    "cv_threshold_color": "red",

    # output
    "dpi": 150,
    "bbox_inches": "tight",
}
```

---

## A-11: Unit Test Configuration [Complexity: 4, Budget: 1 subtask]

**Applied**: Standard pytest fixtures with matplotlib Agg backend

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-11-ST1 | Test infrastructure | pytest fixtures with 32-dim mock sparsity arrays; test_compute_metrics.py (cross_epsilon_tau on identical vectors expects tau≈1), test_visualize.py (generate_all_figures creates 4 PNGs), test_run_experiment.py (seed setup + save_results valid JSON) |

### Test Config

```python
# Embed in conftest.py
import pytest
import numpy as np
import matplotlib
matplotlib.use("Agg")   # Non-standard: must be set before any pyplot import in CI

TEST_CONFIG = {
    "n_layers": 32,
    "n_epsilons": 4,
    "epsilons": [0.001, 0.01, 0.05, 0.1],
    "seed": 42,
    "expected_figures": [
        "gate_metrics.png",
        "cross_epsilon_tau_heatmap.png",
        "sparsity_profiles_overlay.png",
        "cv_per_epsilon.png",
    ],
    # Synthetic data: identical vectors → tau should be ≈ 1.0 for all pairs
    "mock_sparsity_shape": (32,),        # one profile per layer
    "tau_tolerance": 0.05,               # allow small numerical deviation from 1.0
}


@pytest.fixture
def mock_sparsity_profiles():
    """Returns dict[epsilon -> np.array shape (32,)] with identical profiles."""
    rng = np.random.default_rng(TEST_CONFIG["seed"])
    base = rng.uniform(0.3, 0.9, size=(TEST_CONFIG["n_layers"],))
    return {eps: base.copy() for eps in TEST_CONFIG["epsilons"]}


@pytest.fixture
def tmp_output_dir(tmp_path):
    figures = tmp_path / "figures"
    figures.mkdir()
    return tmp_path
```

---

## Requirements

```
# h-m2/code/requirements.txt
torch>=2.0
transformers>=4.40
datasets>=2.18
numpy>=1.24
scipy>=1.11
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
pytest>=7.0
```

---

## Environment Setup Instructions

### Step 1: GPU Selection
```bash
nvidia-smi
# Identify GPU with lowest memory usage
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
```

### Step 2: Install Dependencies
```bash
cd /path/to/h-m2/code
pip install -r requirements.txt
```

### Step 3: Verify HuggingFace Model Access
```bash
huggingface-cli login
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B')"
```

### Step 4: Pre-download Datasets
```bash
python -c "
from datasets import load_dataset
load_dataset('tatsu-lab/alpaca', split='train')
load_dataset('wikitext', 'wikitext-103-raw-v1', split='train')
print('All datasets downloaded.')
"
```

---

## Validation Config Constraints

| Field | Constraint | Error if violated |
|-------|-----------|-------------------|
| `n_samples` | > 0 and divisible by batch_size | AssertionError |
| `primary_epsilon` | must be in `epsilons` list | AssertionError |
| `cv_threshold` | in (0, 1) exclusive | AssertionError |
| `cv_pass_min_count` | in [1, len(epsilons)] | AssertionError |
| `cross_epsilon_tau_threshold` | in (0, 1] | AssertionError |
| `cross_dist_tau_threshold` | in (0, 1] | AssertionError |
| `torch_dtype` | one of float16/bfloat16/float32 | AssertionError |
| `n_layers` | > 0 | AssertionError |
