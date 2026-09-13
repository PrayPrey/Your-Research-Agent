# Logic: H-M2 Deep Network Metric Decoupling

**Date:** 2026-03-26
**Hypothesis:** H-M2 (MECHANISM, INCREMENTAL)
**Gate:** MUST_WORK
**Prerequisites:** H-M1 (VALIDATED), H-E1 (VALIDATED)

Applied: mechanism-verification-incremental

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1 and H-M1)
**Status**: API signatures verified from actual implementation (Read/Glob)
**Analyzed Path**: `h-e1/code/`, `h-m1/code/`
**Relevant Symbols**:
- `AttributionMethod.compute_scores(model, train_loader, test_loader, budget, seed, cfg, device)` → `np.ndarray [N_train, N_test]`
- `build_model(device) -> nn.Module` (ResNet-18 CIFAR-10 modified)
- `load_checkpoint(path, device) -> nn.Module`
- `get_cifar10_loaders(cfg: ExperimentConfig) -> Tuple[DataLoader, DataLoader, DataLoader]`
- `compute_rho_r_rho_m(pred_scores, loo_ground_truth) -> dict`
- `build_metrics_dataframe(method_scores, loo_exact) -> pd.DataFrame`
- `compute_single_error_axis_r2(metrics_df) -> dict`
- `compute_partial_correlation(metrics_df, budget_level) -> float`
- `compute_partial_correlations_all_budgets(metrics_df, budgets) -> Dict[int, float]`
- `plot_gate_metric(partial_corrs, cfg)` (h-m1/visualize.py)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/attribution.py
class AttributionMethod(ABC):
    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,  # h-e1 ExperimentConfig, NOT HM2Config
        device: str = 'cuda',
    ) -> np.ndarray:
        """Returns [n_train, n_test] attribution scores."""

BUDGET_MAP: Dict[str, Dict[int, Any]]  # {method: {budget: params}}

# Concrete classes: TRAKMethod, TracInMethod, IFMethod, FastIFMethod

# From: h-e1/code/model.py
def build_model(device: str = 'cuda') -> nn.Module: ...
def load_checkpoint(path: str, device: str = 'cuda') -> nn.Module: ...

# From: h-e1/code/data.py
def get_cifar10_loaders(cfg: ExperimentConfig) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Returns (train_subset_loader, loo_test_loader, full_test_loader)."""

# From: h-m1/code/metrics_analysis.py
def compute_rho_r_rho_m(pred_scores: np.ndarray, loo_ground_truth: np.ndarray) -> dict:
    """Returns {'rho_r': float, 'rho_m': float}."""

def build_metrics_dataframe(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,
) -> pd.DataFrame:
    """Columns: [method, budget, seed, rho_r, rho_m, error_norm]."""

def compute_single_error_axis_r2(metrics_df: pd.DataFrame) -> dict:
    """Returns {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}."""

def compute_partial_correlation(metrics_df: pd.DataFrame, budget_level: int = None) -> float:
    """Partial corr rho_r ~ rho_m, optionally at single budget level."""

def compute_partial_correlations_all_budgets(
    metrics_df: pd.DataFrame,
    budgets: List[int],
) -> Dict[int, float]:
    """Returns {budget: correlation_r}."""

# From: h-m1/code/visualize.py
def plot_gate_metric(partial_corrs: Dict[int, float], cfg: HM1Config) -> None: ...
```

**Verified from**: `h-e1/code/` and `h-m1/code/` actual implementation.

---

## A-1: Project Setup [Complexity: 6, Budget: 1/10]

**Applied**: Standard dataclass config

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM2Config:
    # Data
    data_root: str = './data'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128

    # External paths
    he1_code_path: str = '../../h-e1/code'
    hm1_code_path: str = '../../h-m1/code'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    loo_cache_path: str = '../../h-e1/code/results/loo_cache.npy'
    hm1_results_path: str = '../../h-m1/code/results/metrics.csv'

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Gate thresholds (deep network must fail these)
    r2_threshold: float = 0.80         # SC-2: R2_deep < this
    partial_corr_threshold: float = 0.85  # SC-3: corr < this
    delta_r2_threshold: float = 0.15   # SC-4: delta > this

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM2Config:
    """Return default HM2Config."""
    return HM2Config()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | HM2Config dataclass + get_config(), mkdir results/figures |

---

## A-2: Data & Model Loading [Complexity: 8, Budget: 1/10]

**Applied**: Standard checkpoint load

### API Signatures

```python
# deep_analysis.py (loading section)
import sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def load_deep_model(cfg: HM2Config, device: str) -> nn.Module:
    """Load ResNet-18 from H-E1 checkpoint. Returns eval-mode model."""
    # x: [B, 3, 32, 32] -> [B, 10]

def load_loo_cache(cfg: HM2Config) -> np.ndarray:
    """Load LOO ground truth. Returns [5000, 100]."""

def get_he1_loaders(cfg: HM2Config) -> tuple:
    """
    Wire HM2Config into ExperimentConfig, call h-e1 get_cifar10_loaders.
    Returns (train_loader, test_loader) - drops full_test_loader.
    """
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loo_exact | [5000, 100] | LOO ground truth from H-E1 |
| train images | [B, 3, 32, 32] | CIFAR-10 normalized |
| model output | [B, 10] | class logits |

### Pseudo-code

```
load_deep_model:
  sys.path.insert(0, cfg.he1_code_path)
  from model import build_model
  model = build_model(device)
  model.load_state_dict(torch.load(cfg.he1_checkpoint, map_location=device))
  model.eval()
  return model

get_he1_loaders:
  sys.path.insert(0, cfg.he1_code_path)
  from data import get_cifar10_loaders
  from config import ExperimentConfig
  he1_cfg = ExperimentConfig(data_root=cfg.data_root, ...)
  train_loader, test_loader, _ = get_cifar10_loaders(he1_cfg)
  return train_loader, test_loader
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | loading funcs | load_deep_model, load_loo_cache, get_he1_loaders |

---

## A-3: Attribution Score Computation [Complexity: 14, Budget: 2/10]

**Applied**: Standard PyTorch attribution loop

### API Signatures

```python
# deep_analysis.py
from typing import Dict, List

def compute_deep_attribution_scores(
    cfg: HM2Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str,
) -> Dict[str, Dict[int, List[np.ndarray]]]:
    """
    Run all methods x budgets x seeds via H-E1 AttributionMethod subclasses.
    Returns: {method: {budget: [scores_seed0, scores_seed1, scores_seed2]}}
    Each scores array: [5000, 100]
    """

def _get_method_instance(method_name: str) -> 'AttributionMethod':
    """Factory: return correct AttributionMethod subclass instance."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores (per run) | [5000, 100] | attribution scores per method/budget/seed |
| method_scores output | dict | 4 methods x 5 budgets x 3 seeds = 60 arrays |

### Pseudo-code

```
compute_deep_attribution_scores:
  sys.path.insert(0, cfg.he1_code_path)
  from attribution import TRAKMethod, TracInMethod, IFMethod, FastIFMethod
  from config import ExperimentConfig
  he1_cfg = ExperimentConfig(...)  # minimal config for attribution methods

  method_map = {'TRAK': TRAKMethod(), 'TracIn': TracInMethod(),
                'IF': IFMethod(), 'FastIF': FastIFMethod()}
  results = {}
  for method_name in cfg.methods:
      method_obj = method_map[method_name]
      results[method_name] = {}
      for budget in cfg.compute_budgets:
          seed_scores = []
          for seed in cfg.seeds:
              scores = method_obj.compute_scores(
                  model, train_loader, test_loader,
                  budget=budget, seed=seed, cfg=he1_cfg, device=device
              )  # [5000, 100]
              seed_scores.append(scores)
          results[method_name][budget] = seed_scores
  return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | attribution loop | compute_deep_attribution_scores with method factory |
| L-3-2 | he1_cfg bridge | map HM2Config fields to ExperimentConfig for attribution calls |

---

## A-4: Metrics DataFrame Builder [Complexity: 9, Budget: 1/10]

**Applied**: Standard PyTorch / delegation pattern

### API Signatures

```python
# deep_analysis.py
def build_deep_metrics_df(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,  # [5000, 100]
) -> pd.DataFrame:
    """
    Delegate to h-m1 build_metrics_dataframe.
    Returns DataFrame with columns: [method, budget, seed, rho_r, rho_m, error_norm]
    """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | metrics df | delegate to h-m1 build_metrics_dataframe, validate columns |

---

## A-5 & A-6: R2 and Partial Correlation Analysis [Complexity: 19, Budget: 2/10]

**Applied**: Standard sklearn regression delegation

### API Signatures

```python
# comparison.py
def compute_r2_deep(metrics_df: pd.DataFrame) -> Dict[str, float]:
    """
    Delegate to h-m1 compute_single_error_axis_r2.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    Gate SC-2: r2_rho_r < 0.80 OR r2_rho_m < 0.80
    """

def compute_partial_corr_deep(
    metrics_df: pd.DataFrame,
    cfg: HM2Config,
) -> Dict[int, float]:
    """
    Delegate to h-m1 compute_partial_correlations_all_budgets.
    Returns: {budget: partial_corr}
    Gate SC-3: min value < 0.85
    """
```

### Pseudo-code

```
compute_r2_deep:
  sys.path.insert(0, cfg.hm1_code_path) [done at module level]
  from metrics_analysis import compute_single_error_axis_r2
  return compute_single_error_axis_r2(metrics_df)

compute_partial_corr_deep:
  from metrics_analysis import compute_partial_correlations_all_budgets
  return compute_partial_correlations_all_budgets(metrics_df, cfg.compute_budgets)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | r2 analysis | compute_r2_deep delegating to h-m1 |
| L-6-1 | partial corr | compute_partial_corr_deep delegating to h-m1 |

---

## A-7: Baseline Comparison & Gate [Complexity: 9, Budget: 1/10]

**Applied**: Standard evaluation pattern

### API Signatures

```python
# comparison.py
from typing import Any

def load_hm1_baseline(cfg: HM2Config) -> Dict[str, Any]:
    """
    Load H-M1 convex results. Try CSV first, fallback to hardcoded validated values.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'partial_corr_by_budget': dict}
    """

def evaluate_gate(
    r2_deep: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    cfg: HM2Config,
) -> Dict[str, Any]:
    """
    Check all gate conditions SC-2, SC-3, SC-4.
    Returns: {'gate_pass': bool, 'sc2_pass': bool, 'sc3_pass': bool, 'sc4_pass': bool,
              'r2_deep': dict, 'delta_r2': float, 'min_partial_corr': float, 'details': str}
    """

def save_results(
    metrics_df: pd.DataFrame,
    r2_results: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    gate_results: Dict[str, Any],
    cfg: HM2Config,
) -> None:
    """Save metrics.csv, r2_analysis.csv, comparison.csv to cfg.results_dir."""
```

### Pseudo-code

```
evaluate_gate:
  sc2 = r2_deep['r2_rho_r'] < cfg.r2_threshold OR r2_deep['r2_rho_m'] < cfg.r2_threshold
  sc3 = min(partial_corr_deep.values()) < cfg.partial_corr_threshold
  delta_r2 = hm1_baseline['r2_avg'] - r2_deep['r2_avg']
  sc4 = delta_r2 > cfg.delta_r2_threshold
  gate_pass = sc2 AND sc3 AND sc4
  return gate dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | baseline + gate | load_hm1_baseline, evaluate_gate, save_results |

---

## A-8 & A-9 & A-10: Visualizations [Complexity: 24, Budget: 1/10]

**Applied**: Standard matplotlib/seaborn plotting

### API Signatures

```python
# visualize.py
def plot_gate_r2_comparison(
    r2_convex: Dict[str, float],
    r2_deep: Dict[str, float],
    cfg: HM2Config,
) -> None:
    """Bar chart R2 convex vs deep with 0.80 threshold line. Saves gate_r2_comparison.png"""

def plot_scatter_metrics_vs_error(metrics_df: pd.DataFrame, cfg: HM2Config) -> None:
    """2-subplot scatter rho_r/rho_m vs error_norm, colored by method. Saves scatter_metrics_vs_error.png"""

def plot_correlation_heatmap(
    partial_corr_convex: Dict[int, float],
    partial_corr_deep: Dict[int, float],
    cfg: HM2Config,
) -> None:
    """Side-by-side heatmap corr(rho_r, rho_m) by budget convex vs deep. Saves correlation_heatmap.png"""

def plot_r2_by_method(metrics_df: pd.DataFrame, cfg: HM2Config) -> None:
    """Bar chart R2 per method. Saves r2_by_method.png"""

def plot_r2_vs_budget(
    r2_convex_by_budget: Dict[int, float],
    r2_deep_by_budget: Dict[int, float],
    cfg: HM2Config,
) -> None:
    """Line plot R2 by budget level convex vs deep. Saves r2_vs_budget.png"""

def generate_all_figures(
    metrics_df: pd.DataFrame,
    r2_deep: Dict[str, float],
    partial_corr_deep: Dict[int, float],
    hm1_baseline: Dict[str, Any],
    cfg: HM2Config,
) -> None:
    """Call all plot functions. Convenience entry point from run_experiment."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | all figures | gate_r2_comparison (mandatory) + 4 supplementary figures |

---

## A-11: Orchestrator [Complexity: 12, Budget: 1/10]

**Applied**: Standard main() pipeline pattern

### API Signatures

```python
# run_experiment.py
import argparse

def main() -> None:
    """
    Full H-M2 pipeline:
    1. load config, setup sys.path for h-e1 and h-m1
    2. load model, loo_cache, data loaders
    3. compute_deep_attribution_scores (4 methods x 5 budgets x 3 seeds)
    4. build_deep_metrics_df
    5. compute_r2_deep
    6. compute_partial_corr_deep
    7. load_hm1_baseline
    8. evaluate_gate
    9. save_results
    10. generate_all_figures
    11. print gate pass/fail summary
    """
```

### Pseudo-code

```
main:
  cfg = get_config()
  os.makedirs(cfg.results_dir, exist_ok=True)
  os.makedirs(cfg.figures_dir, exist_ok=True)
  device = 'cuda' if torch.cuda.is_available() else 'cpu'

  model = load_deep_model(cfg, device)
  loo_exact = load_loo_cache(cfg)          # [5000, 100]
  train_loader, test_loader = get_he1_loaders(cfg)

  method_scores = compute_deep_attribution_scores(
      cfg, model, train_loader, test_loader, device
  )  # {method: {budget: [np.ndarray(5000,100)] x 3}}

  metrics_df = build_deep_metrics_df(method_scores, loo_exact)
  r2_deep = compute_r2_deep(metrics_df)
  partial_corr_deep = compute_partial_corr_deep(metrics_df, cfg)
  hm1_baseline = load_hm1_baseline(cfg)
  gate = evaluate_gate(r2_deep, partial_corr_deep, hm1_baseline, cfg)

  save_results(metrics_df, r2_deep, partial_corr_deep, hm1_baseline, gate, cfg)
  generate_all_figures(metrics_df, r2_deep, partial_corr_deep, hm1_baseline, cfg)

  print("=== H-M2 GATE:", "PASS" if gate['gate_pass'] else "FAIL", "===")
  print(f"  SC-2 R2<0.80: {gate['sc2_pass']}, r2_rho_r={r2_deep['r2_rho_r']:.3f}")
  print(f"  SC-3 corr<0.85: {gate['sc3_pass']}, min={gate['min_partial_corr']:.3f}")
  print(f"  SC-4 delta_r2>0.15: {gate['sc4_pass']}, delta={gate['delta_r2']:.3f}")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | main() | full pipeline orchestration with gate summary print |

---

## Subtask Budget Summary

| Task | ID | Budget Used | Subtasks |
|------|----|-------------|----------|
| A-1 Project Setup | L-1-1 | 1 | config.py scaffolding |
| A-2 Data & Model | L-2-1 | 1 | loading functions |
| A-3 Attribution | L-3-1, L-3-2 | 2 | score computation loop |
| A-4 Metrics DF | L-4-1 | 1 | delegation to h-m1 |
| A-5 R2 Analysis | L-5-1 | 1 | r2 delegation |
| A-6 Partial Corr | L-6-1 | 1 | corr delegation |
| A-7 Gate | L-7-1 | 1 | baseline + gate eval |
| A-9/10 Viz | L-9-1 | 1 | all figures |
| A-11 Orchestrator | L-11-1 | 1 | main() |

**Total: 10/10 subtasks used**

---

## Key Data Flow Summary

```
HM2Config
  -> load_deep_model         -> nn.Module (ResNet-18, eval)
  -> load_loo_cache          -> np.ndarray [5000, 100]
  -> get_he1_loaders         -> DataLoader (train 5000), DataLoader (test 100)

(model, loaders) -> compute_deep_attribution_scores
  -> Dict[method, Dict[budget, List[np.ndarray[5000,100]]]]  # 60 arrays

(method_scores, loo_exact) -> build_deep_metrics_df
  -> pd.DataFrame [60 rows x 6 cols: method, budget, seed, rho_r, rho_m, error_norm]

metrics_df -> compute_r2_deep     -> {'r2_rho_r', 'r2_rho_m', 'r2_avg'}
metrics_df -> compute_partial_corr_deep -> {budget: corr}  # 5 entries

(r2_deep, partial_corr, hm1_baseline) -> evaluate_gate -> {'gate_pass', 'sc2_pass', ...}
```
