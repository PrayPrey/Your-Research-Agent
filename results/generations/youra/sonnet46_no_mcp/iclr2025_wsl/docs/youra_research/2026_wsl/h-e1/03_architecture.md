# Architecture: H-E1 — Permutation Orbit Non-Triviality Analysis

**Hypothesis**: H-E1 (EXISTENCE / MUST_WORK gate)
**Type**: Data analysis — no model training
**Applied**: stratified-analysis-pipeline pattern (data loading → verification → sampling → statistics → visualization)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code to inherit.

---

## File Organization

```
h-e1/code/
  config.py
  data_loader.py
  bn_verify.py
  weight_analysis.py
  orbit_statistics.py
  visualization.py
  utils.py
  run_experiment.py
h-e1/results/
  h_e1_results.yaml
h-e1/figures/
  gate_metrics.png
  cosine_dist_histogram.png
  acc_vs_distance.png
  per_decile_proportion.png
```

---

## Module Definitions

### ExperimentConfig (`h-e1/code/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ExperimentConfig:
    data_dir: Path = Path("./data/model_zoo/")
    results_dir: Path = Path("docs/youra_research/20260505_wsl/h-e1/results/")
    figures_dir: Path = Path("docs/youra_research/20260505_wsl/h-e1/figures/")
    zoo_name: str = "mnist_cnn"
    seed: int = 42
    n_per_decile: int = 50
    n_deciles: int = 10
    acc_threshold: float = 0.01
    cosine_dist_threshold: float = 0.1
    orbit_proportion_gate: float = 0.05
    bn_verify_sample_size: int = 5
```

---

### ModelZooLoader (`h-e1/code/data_loader.py`)

**Dependencies**: config.py

```python
from typing import List, Dict, Any
import torch
from config import ExperimentConfig

def load_zoo_checkpoints(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Returns list of {'state_dict': ..., 'test_accuracy': float}."""
    ...

def load_via_package(cfg: ExperimentConfig) -> List[Dict[str, Any]]: ...
def load_via_files(cfg: ExperimentConfig) -> List[Dict[str, Any]]: ...
```

---

### BNVerifier (`h-e1/code/bn_verify.py`)

**Dependencies**: None

```python
from typing import Dict
import torch

def verify_bn_free(state_dict: Dict[str, torch.Tensor]) -> bool:
    """Returns True if no BatchNorm keys found in state_dict."""
    ...

def verify_zoo_bn_free(
    checkpoints: list,
    sample_size: int = 5,
    seed: int = 42
) -> bool:
    """Samples checkpoints and verifies all are BN-free. Returns True if all pass."""
    ...
```

---

### WeightAnalysis (`h-e1/code/weight_analysis.py`)

**Dependencies**: config.py

```python
from typing import List, Dict, Tuple, Any
import torch
import numpy as np

def flatten_weights(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concatenates weight/bias tensors into 1D float32 CPU tensor."""
    ...

def compute_cosine_distance(w1: torch.Tensor, w2: torch.Tensor) -> float:
    """Returns 1 - cosine_similarity(w1, w2)."""
    ...

def stratified_pair_sample(
    checkpoints: List[Dict[str, Any]],
    n_per_decile: int = 50,
    acc_threshold: float = 0.01,
    seed: int = 42
) -> List[Tuple[Dict, Dict, int]]:
    """Returns list of (model1, model2, decile_index) tuples, 500 total."""
    ...
```

---

### OrbitStatistics (`h-e1/code/orbit_statistics.py`)

**Dependencies**: weight_analysis.py, config.py

```python
from typing import List, Dict, Tuple, Any
import numpy as np

def compute_orbit_statistics(
    pairs: List[Tuple[Dict, Dict, int]]
) -> Tuple[List[Dict], float]:
    """
    Returns (distances, orbit_proportion).
    distances: list of {'decile': int, 'cosine_dist': float, 'is_orbit_candidate': bool}
    orbit_proportion: fraction with cosine_dist > threshold
    """
    ...

def per_decile_proportions(distances: List[Dict]) -> Dict[int, float]:
    """Returns {decile_idx: orbit_proportion} for each decile."""
    ...

def evaluate_gate(
    bn_free: bool,
    orbit_proportion: float,
    threshold: float = 0.05
) -> Dict[str, Any]:
    """Returns gate result dict with 'passed', 'bn_free', 'orbit_proportion'."""
    ...
```

---

### Visualization (`h-e1/code/visualization.py`)

**Dependencies**: orbit_statistics.py, config.py

```python
from typing import List, Dict
from pathlib import Path

def plot_gate_metrics(
    orbit_proportion: float,
    per_decile: Dict[int, float],
    threshold: float,
    save_path: Path
) -> None: ...

def plot_cosine_dist_histogram(
    distances: List[Dict],
    save_path: Path
) -> None: ...

def plot_acc_vs_distance(
    pairs: list,
    distances: List[Dict],
    save_path: Path
) -> None: ...

def plot_per_decile_proportion(
    per_decile: Dict[int, float],
    threshold: float,
    save_path: Path
) -> None: ...

def generate_all_figures(
    distances: List[Dict],
    pairs: list,
    orbit_proportion: float,
    per_decile: Dict[int, float],
    cfg: "ExperimentConfig"
) -> None: ...
```

---

### Utils (`h-e1/code/utils.py`)

**Dependencies**: config.py

```python
import logging
from pathlib import Path
from typing import Any, Dict

def set_seed(seed: int) -> None: ...
def setup_logging(log_level: str = "INFO") -> logging.Logger: ...
def save_results_yaml(results: Dict[str, Any], path: Path) -> None: ...
def ensure_dirs(cfg: "ExperimentConfig") -> None: ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: all modules

```python
from config import ExperimentConfig
from data_loader import load_zoo_checkpoints
from bn_verify import verify_zoo_bn_free
from weight_analysis import stratified_pair_sample
from orbit_statistics import compute_orbit_statistics, per_decile_proportions, evaluate_gate
from visualization import generate_all_figures
from utils import set_seed, setup_logging, save_results_yaml, ensure_dirs
from typing import Dict, Any

def main(cfg: ExperimentConfig) -> Dict[str, Any]: ...

if __name__ == "__main__":
    cfg = ExperimentConfig()
    results = main(cfg)
```

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── utils.py
  ├── data_loader.py      → config.py
  ├── bn_verify.py
  ├── weight_analysis.py  → config.py
  ├── orbit_statistics.py → weight_analysis.py, config.py
  └── visualization.py   → orbit_statistics.py, config.py
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, utils.py, directory structure, requirements.txt | 5 | 1+1+1+2=5 |
| A-2 | Data Loading | data_loader.py: ModelZooDataset pip + file fallback loading of ~4100 checkpoints | 10 | 2+2+2+4=10 |
| A-3 | BN Verification | bn_verify.py: verify_bn_free + verify_zoo_bn_free on sampled checkpoints | 7 | 2+1+2+2=7 |
| A-4 | Weight Analysis Pipeline | weight_analysis.py: flatten_weights, cosine_distance, stratified_pair_sample | 11 | 3+2+3+3=11 |
| A-5 | Orbit Statistics & Gate | orbit_statistics.py: compute_orbit_statistics, per_decile_proportions, evaluate_gate | 10 | 2+3+3+2=10 |
| A-6 | Visualization | visualization.py: 4 figures (gate metrics, histogram, scatter, per-decile bar) | 9 | 2+2+3+2=9 |
| A-7 | Orchestration & Results | run_experiment.py: main() pipeline, YAML output, gate reporting | 8 | 2+3+1+2=8 |

**Distribution**: Very High (18-20): [], High (14-17): [], Medium (9-13): [A-2, A-4, A-5], Low (4-8): [A-1, A-3, A-6, A-7]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=1.12 | Weight tensors, cosine_similarity |
| numpy | >=1.21 | Percentile, statistics, array ops |
| matplotlib | >=3.5 | 4 figure generators |
| pyyaml | >=5.4 | Results YAML output |
| tqdm | >=4.60 | Progress bars for checkpoint loading |
| scipy | >=1.7 | Optional Spearman check |
| model-zoo-dataset | latest | Schurholt zoo loading |
