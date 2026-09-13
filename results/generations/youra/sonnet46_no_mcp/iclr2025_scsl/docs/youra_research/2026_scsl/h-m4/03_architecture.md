# Architecture: H-M4
# DFR Efficacy Correlation with Backbone Training Depth

**Hypothesis ID:** H-M4
**Type:** MECHANISM (INCREMENTAL, extending H-E1 + H-M3)
**Date:** 2026-05-04

Applied: flat-module-layout (H-E1/H-M3 code structure pattern)
Applied: dataclass-config (H-E1 config.py pattern)
Applied: checkpoint-at-specific-epochs (H-E1 train.py checkpoint_interval pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260504_scsl/h-e1/code/` and `docs/youra_research/20260504_scsl/h-m3/code/`
**Findings**: H-E1 uses flat layout with relative imports (`from config import ...`), `WaterbirdsDataset` returns dicts with `core_label`/`spurious_label` keys (no `group_id`; group must be computed as `2*spurious + core`). `build_model()` and `get_waterbirds_loader()` in h-e1 can be reused by file-copy. H-M3 shows the `ResultsExporter`/`Visualizer` pattern for JSON + matplotlib output.

---

## File Structure

```
h-m4/code/
    run_experiment.py           # main entry point / orchestrator
    train_backbone.py           # ERM training with checkpoint saving at {1,2,10,20,30}
    feature_extractor.py        # frozen ResNet-50 → 2048-dim layer4 features
    dfr_module.py               # LogisticRegression DFR + WGA evaluation
    correlation_analyzer.py     # Pearson r computation + gate check
    visualizer.py               # scatter, bar, WGA curve plots
    results_exporter.py         # JSON save + stdout summary
    config.py                   # ExperimentConfig dataclass
    data/
        waterbirds.py           # copied from h-e1 (with group_id field added)
    configs/
        waterbirds.yaml         # default config
    figures/                    # output figures (auto-created)
    results/                    # output JSON (auto-created)
    checkpoints/                # backbone checkpoints per seed
```

---

## Module Definitions

### ExperimentConfig (`config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass, field
from typing import List
import yaml

@dataclass
class TrainConfig:
    data_root: str = ".data_cache/datasets/waterbirds"
    checkpoint_dir: str = "./checkpoints"
    max_epochs: int = 30
    checkpoint_epochs: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4

@dataclass
class DFRConfig:
    C: float = 1.0
    max_iter: int = 1000
    class_weight: str = "balanced"
    solver: str = "lbfgs"
    dfr_seed: int = 42

@dataclass
class AnalysisConfig:
    t_star_mean: float = 2.0
    pearson_r_threshold: float = 0.7
    conditions: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])

@dataclass
class PathConfig:
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    checkpoint_dir: str = "./checkpoints"

@dataclass
class ExperimentConfig:
    train: TrainConfig
    dfr: DFRConfig
    analysis: AnalysisConfig
    paths: PathConfig

def load_config(config_path: str) -> ExperimentConfig: ...
```

---

### WaterbirdsDataset (`data/waterbirds.py`)

**Dependencies**: torch, torchvision, pandas, PIL

```python
from torch.utils.data import Dataset, DataLoader

class WaterbirdsDataset(Dataset):
    SPLIT_MAP = {"train": 0, "val": 1, "test": 2}

    def __init__(self, root: str, split: str, transform=None): ...

    def __getitem__(self, idx: int) -> dict:
        """Returns: {image, core_label, spurious_label, group_id}
        group_id = 2 * spurious_label + core_label  (0..3)
        """
        ...

def get_waterbirds_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int,
    augment: bool = False,
) -> DataLoader: ...
```

---

### BackboneTrainer (`train_backbone.py`)

**Dependencies**: config, data/waterbirds, torch, torchvision

```python
import torch
import torch.nn as nn
from torchvision import models
from config import ExperimentConfig

def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50 with fc replaced: 2048 → num_classes."""
    ...

def get_transforms(augment: bool) -> object: ...

class BackboneTrainer:
    def __init__(self, cfg: ExperimentConfig, device: str): ...

    def train_seed(self, seed: int) -> dict:
        """Train ResNet-50 ERM for max_epochs, saving checkpoints at
        cfg.train.checkpoint_epochs. Returns {epoch: ckpt_path}.
        Checkpoint path: checkpoints/seed_{seed}/epoch_{epoch:03d}.pt
        """
        ...

    def _save_checkpoint(self, model: nn.Module, epoch: int,
                         seed: int, ckpt_dir: str) -> str: ...

    def _checkpoint_exists(self, epoch: int, seed: int) -> bool:
        """Skip training if all checkpoints already exist."""
        ...
```

---

### FeatureExtractor (`feature_extractor.py`)

**Dependencies**: torch, torchvision, numpy

```python
import numpy as np
import torch
import torch.nn as nn
from typing import Tuple

class FeatureExtractor:
    def __init__(self, checkpoint_path: str, device: str): ...

    def load_backbone(self, checkpoint_path: str) -> nn.Module:
        """Load ResNet-50 from checkpoint, remove fc layer, set eval+frozen."""
        ...

    def extract(self, loader) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extract layer4 pooled features (2048-dim) from all batches.
        Returns: (features [N, 2048], labels [N], group_ids [N])
        Asserts features.shape[1] == 2048.
        """
        ...

    def extract_split(self, root: str, split: str, cfg) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convenience: build loader then call extract()."""
        ...
```

---

### DFRModule (`dfr_module.py`)

**Dependencies**: feature_extractor, config, sklearn, numpy

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict
from config import ExperimentConfig

def worst_group_accuracy(predictions: np.ndarray,
                         labels: np.ndarray,
                         group_ids: np.ndarray) -> float:
    """min accuracy over groups 0..3."""
    ...

class DFRModule:
    def __init__(self, cfg: ExperimentConfig): ...

    def evaluate_checkpoint(
        self,
        checkpoint_path: str,
        val_feats: np.ndarray, val_labels: np.ndarray,
        test_feats: np.ndarray, test_labels: np.ndarray,
        test_groups: np.ndarray,
        device: str,
    ) -> Dict[str, float]:
        """Fit DFR and evaluate.
        Returns: {erm_wga, dfr_wga, wga_improvement, feature_dim}
        Log: 'DFR applied at epoch N: ERM WGA=X, DFR WGA=Y, improvement=Z'
        """
        ...

    def _erm_wga(self, checkpoint_path: str,
                 test_feats: np.ndarray, test_labels: np.ndarray,
                 test_groups: np.ndarray, device: str) -> float:
        """Evaluate ERM fc layer on test features. Returns WGA."""
        ...

    def _fit_dfr(self, val_feats: np.ndarray, val_labels: np.ndarray) -> LogisticRegression:
        """LogisticRegression(C=1.0, class_weight='balanced', solver='lbfgs', max_iter=1000)"""
        ...
```

---

### CorrelationAnalyzer (`correlation_analyzer.py`)

**Dependencies**: numpy, scipy, config

```python
import numpy as np
from scipy.stats import pearsonr
from typing import Dict, List, Tuple
from config import ExperimentConfig

class CorrelationAnalyzer:
    def __init__(self, cfg: ExperimentConfig): ...

    def aggregate_across_seeds(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
    ) -> Dict[int, Dict[str, float]]:
        """Average erm_wga, dfr_wga, wga_improvement over seeds per epoch condition.
        results_per_seed: {seed: {epoch: {erm_wga, dfr_wga, wga_improvement}}}
        Returns: {epoch: {mean_erm_wga, mean_dfr_wga, mean_wga_improvement, std_wga_improvement}}
        """
        ...

    def compute_pearson(
        self,
        aggregated: Dict[int, Dict[str, float]],
        t_star: float,
    ) -> Dict[str, float]:
        """Pearson r between mean_wga_improvement and (epoch - t_star) over 5 conditions.
        Returns: {pearson_r, pearson_p_twotailed, pearson_p_onetailed, epochs_past_tstar, improvements}
        """
        ...

    def evaluate_gate(self, pearson_r: float) -> Dict[str, object]:
        """SHOULD_WORK gate: r > 0.7.
        Returns: {gate_passed, pearson_r, threshold, decision, note}
        """
        ...

    def verify_monotonicity(self, improvements: List[float]) -> Dict[str, object]:
        """Check if improvements are monotonically increasing.
        Returns: {is_monotonic, n_positive_diffs, n_diffs, positive_fraction}
        """
        ...
```

---

### Visualizer (`visualizer.py`)

**Dependencies**: numpy, matplotlib, config

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from config import ExperimentConfig

class Visualizer:
    def __init__(self, cfg: ExperimentConfig): ...

    def plot_gate_metrics(
        self,
        aggregated: Dict[int, Dict[str, float]],
        pearson_r: float,
        t_star: float,
        r_threshold: float = 0.7,
    ) -> str:
        """Bar chart of WGA improvement per epoch condition; annotate Pearson r.
        Returns saved path.
        """
        ...

    def plot_scatter_correlation(
        self,
        epochs_past_tstar: List[float],
        improvements: List[float],
        pearson_r: float,
        pearson_p: float,
    ) -> str:
        """Scatter (epoch-t*) vs improvement with regression line + 95% CI. Returns path."""
        ...

    def plot_wga_curves(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
        conditions: List[int],
    ) -> str:
        """ERM and DFR WGA vs epoch, error bars over 3 seeds. Returns path."""
        ...

    def plot_monotonicity_check(
        self,
        improvements: List[float],
        conditions: List[int],
    ) -> str:
        """Bar chart of diff[t+1]-diff[t] at each step. Returns path."""
        ...

    def save_all(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
        aggregated: Dict[int, Dict[str, float]],
        correlation_results: Dict[str, object],
        t_star: float,
    ) -> List[str]: ...
```

---

### ResultsExporter (`results_exporter.py`)

**Dependencies**: config, json, numpy

```python
import json
from typing import Dict, List
from config import ExperimentConfig

class ResultsExporter:
    def __init__(self, cfg: ExperimentConfig): ...

    def save_json(
        self,
        results_per_seed: Dict,
        aggregated: Dict,
        correlation_results: Dict,
        gate_result: Dict,
        figure_paths: List[str],
    ) -> str:
        """Save to results/h-m4_results.json. Returns path."""
        ...

    def print_summary(
        self,
        correlation_results: Dict,
        gate_result: Dict,
    ) -> None:
        """Print PASS/FAIL gate summary + pearson_r to stdout."""
        ...
```

---

### Main Orchestrator (`run_experiment.py`)

**Dependencies**: all modules

```python
import argparse
from config import load_config
from train_backbone import BackboneTrainer
from feature_extractor import FeatureExtractor
from dfr_module import DFRModule
from correlation_analyzer import CorrelationAnalyzer
from visualizer import Visualizer
from results_exporter import ResultsExporter

def run(config_path: str, device: str) -> dict:
    """
    1. For each seed: train backbone, save checkpoints at {1,2,10,20,30}
    2. Pre-extract val/test features for each (seed, epoch) checkpoint
    3. Apply DFR at each checkpoint, compute wga_improvement
    4. Aggregate over seeds, compute Pearson r
    5. Evaluate gate, visualize, export
    Returns: full results dict
    """
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/waterbirds.yaml")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    run(args.config, args.device)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | file-copy to `h-m4/code/data/waterbirds.py` (add group_id) | `h-e1/code/data/waterbirds.py` |
| build_model | reimplemented in `train_backbone.py` (same signature) | `h-e1/code/train.py:34` |
| get_transforms | reimplemented in `train_backbone.py` (same logic) | `h-e1/code/train.py:15` |
| SGD config | TrainConfig values: lr=1e-3, momentum=0.9, wd=1e-4 | `h-e1/code/config.py:TrainConfig` |

**Verified from**: `h-e1/code/` (actual implementation)

**Key adaptation**: `WaterbirdsDataset.__getitem__` must add `group_id = 2 * spurious_label + core_label` (H-E1 omits group_id; needed for WGA evaluation in H-M4).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Project Setup | config.py, configs/waterbirds.yaml, directory skeleton, requirements | 5 | 1+1+2+1 |
| E-2 | Data Module | Copy+extend WaterbirdsDataset with group_id; loaders for train/val/test | 8 | 2+2+2+2 |
| E-3 | Backbone Trainer | ERM training loop, checkpoint saving at {1,2,10,20,30} epochs, skip-if-exists | 14 | 4+3+4+3 |
| E-4 | Feature Extractor | Load frozen ResNet-50, strip fc, extract 2048-dim layer4 features, shape assert | 11 | 3+2+4+2 |
| E-5 | DFR Module | worst_group_accuracy, ERM WGA eval, DFR LogReg fit+predict, logging | 13 | 3+3+4+3 |
| E-6 | 5-Condition Pipeline | Loop over seeds × epoch conditions; cache val/test features per seed; collect results | 14 | 3+4+4+3 |
| E-7 | Correlation Analyzer | Aggregate over seeds, Pearson r, one/two-tailed p, gate check, monotonicity | 12 | 3+3+4+2 |
| E-8 | Visualizer | 4 plots: bar chart, scatter+regression, WGA curves, monotonicity diff | 10 | 3+2+3+2 |
| E-9 | Results Exporter | JSON save, stdout summary with gate PASS/FAIL | 6 | 2+1+2+1 |
| E-10 | Orchestrator | run_experiment.py full pipeline, argparse, end-to-end flow | 9 | 2+3+2+2 |
| E-11 | Integration Test | Run 1 seed × 2 conditions (epoch 1, 2) in <5 min; verify feature shape, DFR > ERM | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-3, E-6], Medium(9-13): [E-4, E-5, E-7, E-8, E-10, E-11], Low(4-8): [E-1, E-2, E-9]

---

*Architecture for H-M4 — DFR efficacy vs. backbone training depth (t* = 2 epochs from H-M3)*
*Generated: 2026-05-04*
