# Architecture: H-E1 — Activation Sparsity Existence Check for LLaMA-3-8B

**Hypothesis Type**: EXISTENCE (PoC/measurement-only)
**Project Type**: Green-field (foundation hypothesis, no base hypothesis)
**Applied**: PyTorch register_forward_hook layerwise measurement pattern (Accelerate/SparseGPT/TEAL)
**Applied**: Magnitude-based sparsity thresholding |a| < epsilon (TEAL calibration methodology)

Applied: PyTorch register_forward_hook layerwise measurement pattern (Accelerate/SparseGPT/TEAL)
Applied: Magnitude-based sparsity thresholding |a| < epsilon (TEAL calibration methodology)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1 is the foundation hypothesis with no prior code.

---

## File Structure

- `h-e1/code/config.py` — Experiment configuration dataclass
- `h-e1/code/data_utils.py` — Dataset loading and tokenization
- `h-e1/code/measure_sparsity.py` — Hook registration and forward pass measurement
- `h-e1/code/compute_metrics.py` — CV and Kendall's tau computation
- `h-e1/code/visualize.py` — All 5 figure generation functions
- `h-e1/code/run_experiment.py` — Main orchestration entry point
- `h-e1/figures/` — Output directory for saved figures
- `h-e1/results/` — Output directory for JSON results

---

## Module Definitions

### ExperimentConfig (`h-e1/code/config.py`)

**Dependencies**: dataclasses (stdlib)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    n_layers: int = 32
    n_samples: int = 512
    batch_size: int = 8
    seed: int = 42
    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    primary_epsilon: float = 0.01
    short_length: int = 128
    long_length: int = 512
    alpaca_dataset: str = "tatsu-lab/alpaca"
    wikitext_dataset: str = "wikitext"
    wikitext_config: str = "wikitext-103-raw-v1"
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
    cv_threshold: float = 0.3
    tau_threshold: float = 0.6
```

---

### DataUtils (`h-e1/code/data_utils.py`)

**Dependencies**: ExperimentConfig, datasets, transformers, torch

```python
from torch.utils.data import DataLoader
from transformers import PreTrainedTokenizer
from config import ExperimentConfig

def load_alpaca_dataloader(
    tokenizer: PreTrainedTokenizer,
    cfg: ExperimentConfig,
    max_length: int,
) -> DataLoader: ...

def load_wikitext_dataloader(
    tokenizer: PreTrainedTokenizer,
    cfg: ExperimentConfig,
    max_length: int = 512,
) -> DataLoader: ...
```

---

### SparsityMeasurer (`h-e1/code/measure_sparsity.py`)

**Dependencies**: ExperimentConfig, torch, numpy

```python
import numpy as np
import torch
from torch import nn
from transformers import PreTrainedModel
from torch.utils.data import DataLoader
from config import ExperimentConfig

def measure_layer_sparsity(
    model: PreTrainedModel,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray: ...
# Returns: shape (32,) — mean sparsity fraction per layer

def verify_mechanism(
    layer_sparsity: np.ndarray,
    cfg: ExperimentConfig,
) -> tuple[bool, dict]: ...
# Returns: (all_passed, indicators_dict)

def run_all_conditions(
    model: PreTrainedModel,
    alpaca_short: DataLoader,
    alpaca_long: DataLoader,
    wikitext_long: DataLoader,
    cfg: ExperimentConfig,
) -> dict: ...
# Returns: nested dict keyed by (dataset, epsilon, length) -> np.ndarray shape (32,)
```

---

### MetricsComputer (`h-e1/code/compute_metrics.py`)

**Dependencies**: numpy, scipy

```python
import numpy as np
from scipy.stats import kendalltau

def compute_cv(layer_sparsity: np.ndarray) -> float: ...

def compute_kendall_tau(
    sparsity_a: np.ndarray,
    sparsity_b: np.ndarray,
) -> tuple[float, float]: ...
# Returns: (tau_statistic, p_value)

def compute_all_metrics(condition_results: dict, cfg) -> dict: ...
# Computes CV and tau for all epsilon values and condition pairs
# Returns: metrics dict with primary + secondary stats

def check_gate_conditions(metrics: dict, cfg) -> tuple[bool, dict]: ...
# Returns: (passed, {cv_pass, tau_pass, cv_value, tau_value})
```

---

### Visualizer (`h-e1/code/visualize.py`)

**Dependencies**: compute_metrics outputs, matplotlib, numpy, pathlib

```python
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_gate_metrics_bar(
    cv: float,
    tau: float,
    cfg,
    save_path: Path,
) -> None: ...
# Figure 1: CV vs 0.3 threshold, tau vs 0.6 threshold bar chart

def plot_sparsity_profile(
    alpaca_sparsity: np.ndarray,
    wikitext_sparsity: np.ndarray,
    epsilon: float,
    cfg,
    save_path: Path,
) -> None: ...
# Figure 2: Per-layer mean sparsity, Alpaca vs WikiText-103 overlaid

def plot_epsilon_sensitivity(
    metrics: dict,
    cfg,
    save_path: Path,
) -> None: ...
# Figure 3: CV and tau heatmap/table for all epsilon values

def plot_length_sensitivity(
    alpaca_short_sparsity: np.ndarray,
    alpaca_long_sparsity: np.ndarray,
    tau_length: float,
    cfg,
    save_path: Path,
) -> None: ...
# Figure 4: Sparsity profiles 128-token vs 512-token with tau annotation

def plot_rank_correlation_scatter(
    alpaca_sparsity: np.ndarray,
    wikitext_sparsity: np.ndarray,
    tau: float,
    p_value: float,
    cfg,
    save_path: Path,
) -> None: ...
# Figure 5: Alpaca vs WikiText-103 layer rank scatter with tau annotation

def generate_all_figures(
    condition_results: dict,
    metrics: dict,
    cfg,
) -> None: ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: all modules above, transformers, torch, json, pathlib

```python
from config import ExperimentConfig
from data_utils import load_alpaca_dataloader, load_wikitext_dataloader
from measure_sparsity import run_all_conditions, verify_mechanism
from compute_metrics import compute_all_metrics, check_gate_conditions
from visualize import generate_all_figures

def setup_model_and_tokenizer(cfg: ExperimentConfig): ...
# Loads LLaMA-3-8B float16, eval mode, device_map="auto"
# Validates 32 MLP layers with gate_proj; fails explicitly otherwise

def save_results(condition_results: dict, metrics: dict, gate_pass: bool, cfg: ExperimentConfig) -> None: ...
# Saves results.json and per-condition CSV/JSON arrays

def main(cfg: ExperimentConfig = None) -> None: ...
# Full orchestration: setup → data → measure → metrics → visualize → save
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity |
|----|------|-------------|-------|------------|
| E1 | Environment Setup | Install packages, verify HF token, GPU check, create output dirs | `run_experiment.py`, `config.py` | 6/20 = Size:1 + Deps:1 + Algo:1 + Integ:3 |
| E2 | Data Pipeline | Alpaca + WikiText-103 loading, tokenization, 128/512-token batching, DataLoaders | `data_utils.py`, `config.py` | 9/20 = Size:2 + Deps:2 + Algo:2 + Integ:3 |
| E3 | Sparsity Measurement Engine | Hook registration on all 32 gate_proj layers, forward passes, sparsity fraction computation, hook cleanup, all condition sweep | `measure_sparsity.py` | 14/20 = Size:3 + Deps:2 + Algo:4 + Integ:5 |
| E4 | Metrics Computation | CV computation, Kendall's tau (calibration + length), p-values, all epsilon conditions, gate condition check | `compute_metrics.py` | 10/20 = Size:2 + Deps:2 + Algo:4 + Integ:2 |
| E5 | Visualization | All 5 required figures: gate metrics bar, sparsity profile, epsilon sensitivity, length sensitivity, rank scatter | `visualize.py` | 12/20 = Size:3 + Deps:2 + Algo:3 + Integ:4 |
| E6 | Orchestration and Results | Main pipeline wiring, model loading with architecture validation, JSON/CSV save, results table print | `run_experiment.py` | 11/20 = Size:2 + Deps:4 + Algo:2 + Integ:3 |

**Distribution**: High(12-14): [E3, E5, E6], Medium(9-11): [E2, E4], Low(4-8): [E1]

---

## Module Dependencies

```
ExperimentConfig (config.py)
    ↓
DataUtils (data_utils.py)         SparsityMeasurer (measure_sparsity.py)
    ↓                                      ↓
    └──────────── RunExperiment (run_experiment.py) ──────────┐
                        ↓                                      ↓
              MetricsComputer (compute_metrics.py)    Visualizer (visualize.py)
```

---

## Key Interface Notes

- `run_all_conditions()` returns `dict` keyed by `(dataset, epsilon, length)` tuples mapping to `np.ndarray` shape `(32,)`
- `compute_all_metrics()` consumes that dict and returns flat metrics dict with keys like `"cv_alpaca_long_eps0.01"`, `"tau_calibration_eps0.01"`, etc.
- Hook cleanup guaranteed via `try/finally` in `measure_layer_sparsity()`
- Architecture validation in `setup_model_and_tokenizer()` raises `RuntimeError` if `len(model.model.layers) != 32` or `gate_proj` not found
- All figure save paths constructed from `cfg.figures_dir` in `generate_all_figures()`

---

*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
*Architecture: Green-field | Epic Tasks: 6 | Complexity Range: 6-14*
