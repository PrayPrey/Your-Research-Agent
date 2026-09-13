# Architecture: H-M1
# SGD Gradient Structure Analysis — Gradient Dominance Ratio (GDR)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-05-04

Applied: DL incremental extension pattern (gradient instrumentation on existing ERM codebase)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (H-E1)
**Analyzed Path**: `h-e1/code/`
**Findings**: Flat layout, dict-based batch items (`image`, `core_label`, `spurious_label`), dataclass configs loaded via YAML, all imports relative. H-E1 `WaterbirdsDataset` already provides `spurious_label` per sample — reusable directly.

---

## File Organization

```
h-m1/code/
  config.py               # ExperimentConfig (extends H-E1 config + GDR fields)
  train.py                # ERM trainer (identical to H-E1)
  gradient_analyzer.py    # GradientAlignmentAnalyzer (NEW — core mechanism)
  analyze.py              # GDR computation, Wilcoxon test, Pearson correlation
  visualize.py            # 4 required figures
  run_experiment.py       # Multi-seed orchestration + PASS/FAIL gate
  data/
    __init__.py
    waterbirds.py         # Copied from H-E1 (no changes needed)
  configs/
    waterbirds.yaml       # Single fixed config
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | `from data.waterbirds import WaterbirdsDataset, get_waterbirds_loader` | `h-e1/code/data/waterbirds.py` |
| build_model | `from train import build_model` | `h-e1/code/train.py` |
| TrainConfig | `from config import TrainConfig` | `h-e1/code/config.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Note**: H-M1 copies `data/waterbirds.py` and `train.py` directly from H-E1 with no modification. Import paths remain relative.

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TrainConfig:
    dataset: str
    data_root: str
    checkpoint_dir: str
    epochs: int
    checkpoint_interval: int = 2
    batch_size: int = 64
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4

@dataclass
class GDRConfig:
    early_window_epochs: List[int] = field(default_factory=lambda: [2, 4, 6])
    p_threshold: float = 0.05
    min_seeds_pass: int = 2
    he1_delta_path: Optional[str] = None   # path to H-E1 delta(t) JSON for correlation

@dataclass
class ExperimentConfig:
    train: TrainConfig
    gdr: GDRConfig
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./figures"

def load_config(config_path: str) -> ExperimentConfig: ...
```

---

### GradientAlignmentAnalyzer (`gradient_analyzer.py`)

**Dependencies**: config.TrainConfig, data.waterbirds.get_waterbirds_loader, train.build_model

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Tuple, Dict, List

class GradientAlignmentAnalyzer:
    def __init__(self, model: nn.Module, device: str): ...

    def extract_features(self, loader: DataLoader) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Returns (features, core_labels, spurious_labels) — backbone frozen, no_grad."""
        ...

    def compute_label_gradient_norm(
        self,
        features: torch.Tensor,
        label_tensor: torch.Tensor,
        criterion: nn.Module,
    ) -> float:
        """Single backward pass on fc layer only. Returns grad norm as float."""
        ...

    def log_epoch_gradients(
        self,
        loader: DataLoader,
        criterion: nn.Module,
    ) -> Dict[str, float]:
        """
        Returns dict: {spurious_grad_norm, core_grad_norm, gdr}
        Uses extract_features + two compute_label_gradient_norm calls.
        """
        ...

    def get_history(self) -> Dict[str, List[float]]:
        """Returns {spurious_grad_norms, core_grad_norms, gdr_series} accumulated across epochs."""
        ...
```

---

### Train (`train.py`)

**Dependencies**: config.TrainConfig, data.waterbirds.get_waterbirds_loader, gradient_analyzer.GradientAlignmentAnalyzer

```python
import torch.nn as nn
from config import TrainConfig
from gradient_analyzer import GradientAlignmentAnalyzer
from typing import Dict, Any

def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module: ...

def train_one_seed(
    cfg: TrainConfig,
    seed: int,
    device: str,
    analyzer: GradientAlignmentAnalyzer,
) -> Dict[str, Any]:
    """
    Trains ResNet-50 ERM (identical to H-E1).
    At each checkpoint_interval epoch, calls analyzer.log_epoch_gradients().
    Returns per-seed GDR history dict.
    """
    ...

def main(cfg: TrainConfig, device: str) -> Dict[int, Dict[str, Any]]:
    """Runs train_one_seed for each seed. Returns {seed: gdr_history}."""
    ...
```

---

### Analyze (`analyze.py`)

**Dependencies**: config.GDRConfig

```python
import numpy as np
from typing import Dict, List, Any
from config import GDRConfig

def compute_mean_early_gdr(
    gdr_series: List[float],
    early_epochs: List[int],
    checkpoint_interval: int,
) -> float: ...

def run_wilcoxon_test(
    spurious_norms_early: np.ndarray,
    core_norms_early: np.ndarray,
) -> Dict[str, float]:
    """Returns {stat, p_value}. alternative='greater'."""
    ...

def run_pearson_correlation(
    gdr_series: np.ndarray,
    delta_series: np.ndarray,
) -> Dict[str, float]:
    """Returns {r, p_value}."""
    ...

def load_he1_delta(delta_path: str) -> np.ndarray:
    """Loads H-E1 delta(t) from JSON results file."""
    ...

def run_analysis(
    seed_results: Dict[int, Dict[str, Any]],
    cfg: GDRConfig,
    delta_path: str = None,
) -> Dict[str, Any]:
    """
    Aggregates across seeds: mean_early_GDR, std_early_GDR, per-seed Wilcoxon,
    Pearson correlation with H-E1 delta(t), PASS/FAIL gate.
    Returns full summary dict.
    """
    ...

def check_gate(analysis: Dict[str, Any], cfg: GDRConfig) -> bool:
    """Returns True if mean_early_GDR > 1.0 in >= min_seeds_pass seeds and Wilcoxon p < p_threshold."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: analyze (analysis dict)

```python
import matplotlib.pyplot as plt
from typing import Dict, Any
import numpy as np

def plot_mean_early_gdr_bar(
    analysis: Dict[str, Any],
    figures_dir: str,
) -> str:
    """Figure 1 (required): Bar chart mean Early GDR vs 1.0 with error bars. Returns fig path."""
    ...

def plot_gdr_timeline(
    seed_results: Dict[int, Dict[str, Any]],
    delta_series: np.ndarray,
    figures_dir: str,
) -> str:
    """Figure 2: GDR(t) line plot overlaid with delta(t) from H-E1. Returns fig path."""
    ...

def plot_grad_norm_dual_axis(
    seed_results: Dict[int, Dict[str, Any]],
    figures_dir: str,
) -> str:
    """Figure 3: Dual-axis spurious_grad_norm(t) and core_grad_norm(t) with seed bands. Returns fig path."""
    ...

def plot_early_late_violin(
    seed_results: Dict[int, Dict[str, Any]],
    early_epochs: list,
    figures_dir: str,
) -> str:
    """Figure 4: Violin plots GDR early window vs late (epochs 25-30). Returns fig path."""
    ...

def generate_all_figures(
    seed_results: Dict[int, Dict[str, Any]],
    analysis: Dict[str, Any],
    delta_series: np.ndarray,
    figures_dir: str,
) -> None: ...
```

---

### Run Experiment (`run_experiment.py`)

**Dependencies**: config.load_config, train, analyze, visualize

```python
import argparse
from config import load_config

def main(config_path: str, device: str, skip_train: bool = False) -> dict:
    """
    Steps:
    1. ERM Training (3 seeds) with gradient logging at each checkpoint
    2. Statistical analysis (Wilcoxon, Pearson corr with H-E1 delta)
    3. PASS/FAIL gate evaluation
    4. Generate 4 figures
    5. Write results/summary.json
    """
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--skip-train", action="store_true")
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Copy H-E1 data/waterbirds.py, create config.py with GDRConfig, create configs/waterbirds.yaml with 3 seeds / 30 epochs / batch=64 | 5 | 1+1+1+2 |
| A-2 | Data Loader Verification | Verify WaterbirdsDataset returns `spurious_label` per batch; write smoke test confirming dict keys and label ranges | 5 | 1+1+1+2 |
| A-3 | ERM Trainer (Copy + Extend) | Copy H-E1 train.py; add `analyzer` parameter to `train_one_seed`; call `analyzer.log_epoch_gradients()` at each checkpoint epoch | 8 | 2+2+2+2 |
| A-4 | GradientAlignmentAnalyzer | Implement `extract_features` (frozen backbone), `compute_label_gradient_norm` (fc-only backward), `log_epoch_gradients` (GDR = spurious/core norm ratio), `get_history` | 14 | 3+3+4+4 |
| A-5 | GDR Metric & Wilcoxon | Implement `compute_mean_early_gdr`, `run_wilcoxon_test` (scipy.stats, alternative='greater'), `check_gate`; save per-seed GDR CSVs | 10 | 2+2+3+3 |
| A-6 | Pearson Temporal Alignment | Implement `load_he1_delta` (JSON loader), `run_pearson_correlation`, integrate into `run_analysis` | 9 | 2+2+3+2 |
| A-7 | Visualization (4 Figures) | Implement all 4 figure functions in visualize.py: bar chart (required), GDR timeline + delta overlay, dual-axis grad norm, violin early/late | 10 | 2+2+3+3 |
| A-8 | Experiment Runner & Gate Report | Implement run_experiment.py orchestrating train → analyze → gate → visualize → summary.json; PASS/FAIL printed with all metrics | 9 | 2+2+2+3 |
| A-9 | End-to-End Validation (3 seeds) | Run full experiment, verify all 3 seeds complete, confirm GDR logging outputs, assert mean_early_GDR > 1.0 gate | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-6, A-7, A-8, A-9], Low(4-8): [A-1, A-2, A-3]

**Total Complexity**: 80 | **Task Count**: 9 (within 6-12 range)
