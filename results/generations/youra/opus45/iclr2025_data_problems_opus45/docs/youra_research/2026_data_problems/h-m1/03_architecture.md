# Architecture: H-M1 Convex Metric Coupling

**Date:** 2026-03-26
**Hypothesis:** H-M1 (MECHANISM)
**Gate:** MUST_WORK

Applied: logistic-regression-influence-functions-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found via direct file reads (Serena MCP inactive - no active project set)
**Analyzed Path**: `docs/youra_research/20260323_data_problems/h-e1/code/`
**Findings**: H-E1 uses flat module layout (config.py, data.py, model.py, train.py, evaluate.py, attribution.py). Attribution methods use `AttributionMethod` ABC with `compute_scores(model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray`. Metrics use `MetricResult` dataclass (rho_r, rho_m, S, CIs). Config uses `ExperimentConfig` dataclass. H-M1 reuses attribution.py directly via import path.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| AttributionMethod | `sys.path.insert(0, '../h-e1/code'); from attribution import AttributionMethod, get_method, BUDGET_MAP` | `h-e1/code/attribution.py` |
| MetricResult | `from evaluate import MetricResult, compute_metrics` | `h-e1/code/evaluate.py` |
| ExperimentConfig (reference) | `from config import ExperimentConfig` | `h-e1/code/config.py` |
| build_model | `from model import build_model` | `h-e1/code/model.py` |

**Verified from**: `docs/youra_research/20260323_data_problems/h-e1/code/` (actual implementation)

---

## File Organization

```
h-m1/code/
├── config.py           # H-M1 config dataclass
├── features.py         # Feature extraction from H-E1 ResNet-18
├── convex_model.py     # Logistic regression + Hessian verification
├── loo_influence.py    # Closed-form LOO via Hessian inversion
├── attribution_convex.py  # Adapt H-E1 attribution methods for linear model
├── metrics_analysis.py # Partial correlation + single-error-axis R^2
├── visualize.py        # Gate figures + supplementary plots
└── run_experiment.py   # Top-level orchestration
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: dataclasses

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM1Config:
    # Data
    data_root: str = './data'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    he1_code_path: str = '../../h-e1/code'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42
    feature_dim: int = 512
    n_classes: int = 10

    # Logistic Regression
    C: float = 100.0           # lambda = 0.01
    lr_solver: str = 'lbfgs'
    lr_max_iter: int = 1000

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    n_bootstrap: int = 1000

    # Success thresholds
    partial_corr_threshold: float = 0.95
    r2_threshold: float = 0.95

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'

def get_config() -> HM1Config: ...
```

---

### FeatureExtractor (`features.py`)

**Dependencies**: torch, torchvision, sklearn, h-e1/code/model.py

```python
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from config import HM1Config

class FeatureExtractor:
    def __init__(self, cfg: HM1Config, device: str = 'cuda'): ...

    def load_resnet(self) -> nn.Module:
        """Load H-E1 ResNet-18 from cfg.he1_checkpoint."""
        ...

    def extract(
        self,
        dataloader: torch.utils.data.DataLoader,
        model: nn.Module,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Remove FC layer, extract 512-dim penultimate features.
        Returns: (features: np.ndarray[N, 512], labels: np.ndarray[N])
        """
        ...

    def get_features(
        self, cfg: HM1Config
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Full pipeline: load data -> extract -> StandardScaler normalize.
        Returns: (X_train, y_train, X_test, y_test), shapes (5000,512), (5000,), (100,512), (100,)
        Caches to cfg.results_dir/features_cache.npz
        """
        ...
```

---

### ConvexModel (`convex_model.py`)

**Dependencies**: numpy, scipy, sklearn, config

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from config import HM1Config

class ConvexLogisticModel:
    def __init__(self, cfg: HM1Config): ...

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> 'ConvexLogisticModel':
        """Fit sklearn LogisticRegression(C=cfg.C, solver=lbfgs, max_iter=cfg.lr_max_iter)."""
        ...

    def get_theta(self) -> np.ndarray:
        """Returns weight matrix (D, C) for Hessian computation."""
        ...

    def compute_hessian(
        self, X: np.ndarray, lambda_reg: float = 0.01
    ) -> np.ndarray:
        """
        H = (1/N) * X^T @ W @ X + lambda * I
        where W = diag(p * (1-p)) aggregated across classes.
        Returns: H (D, D)
        """
        ...

    def verify_convexity(self, X: np.ndarray) -> dict:
        """
        Compute Hessian eigenvalues, assert all > 0.
        Returns: {'min_eigenvalue': float, 'max_eigenvalue': float, 'is_convex': bool}
        """
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Softmax probabilities. Returns (N, C)."""
        ...
```

---

### LOOInfluence (`loo_influence.py`)

**Dependencies**: numpy, scipy.linalg, convex_model

```python
import numpy as np
from convex_model import ConvexLogisticModel
from config import HM1Config

class ClosedFormLOO:
    def __init__(self, model: ConvexLogisticModel, cfg: HM1Config): ...

    def compute_hessian_inverse(
        self, X_train: np.ndarray, lambda_reg: float = 0.01
    ) -> np.ndarray:
        """
        Compute H^{-1} via scipy.linalg.inv.
        H shape: (D, D), D=512. O(D^3) exact inversion.
        Returns: H_inv (D, D)
        """
        ...

    def compute_train_gradients(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> np.ndarray:
        """
        grad_i = x_i * (p_i - e_{y_i})  where e_{y_i} is one-hot.
        Returns: grad_train (N, D)
        """
        ...

    def compute_influence(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        H_inv: np.ndarray,
    ) -> np.ndarray:
        """
        I(z_i, z_test) = grad_test^T @ H_inv @ grad_i
        Returns: influences (N_train, N_test)
        Cached at cfg.results_dir/loo_exact_cache.npy
        """
        ...
```

---

### AttributionConvex (`attribution_convex.py`)

**Dependencies**: numpy, h-e1/code/attribution.py, config

```python
import numpy as np
from typing import Dict
from config import HM1Config

# Reuse H-E1 budget map and method registry via sys.path injection

BUDGET_MAP_CONVEX: Dict = {
    'TRAK':   {10: {'proj_dim': 10},  25: {'proj_dim': 25},  50: {'proj_dim': 50},
               75: {'proj_dim': 75},  100: {'proj_dim': 100}},
    'TracIn': {10: {'scale': 1}, 25: {'scale': 2}, 50: {'scale': 3},
               75: {'scale': 4}, 100: {'scale': 5}},
    'IF':     {10: {'depth': 10}, 25: {'depth': 25}, 50: {'depth': 50},
               75: {'depth': 75}, 100: {'depth': 100}},
    'FastIF': {10: {'scale': 1}, 25: {'scale': 2}, 50: {'scale': 3},
               75: {'scale': 4}, 100: {'scale': 5}},
}

class LinearAttributionRunner:
    """Run H-E1 attribution methods adapted for linear (feature-space) model."""

    def __init__(self, cfg: HM1Config): ...

    def compute_method_scores(
        self,
        method_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        budget: int,
        seed: int,
    ) -> np.ndarray:
        """
        Compute attribution scores for a linear model in feature space.
        Returns: scores (N_train, N_test)
        """
        ...

    def run_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Dict[int, list]]:
        """
        Full grid: 4 methods x 5 budgets x 3 seeds.
        Returns: results[method][budget] = List[np.ndarray(N_train, N_test)]
        """
        ...
```

---

### MetricsAnalysis (`metrics_analysis.py`)

**Dependencies**: numpy, scipy, pingouin, sklearn, pandas, h-e1/code/evaluate.py

```python
import numpy as np
import pandas as pd
import pingouin as pg
from typing import Dict, List
from config import HM1Config

def compute_rho_r_rho_m(
    pred_scores: np.ndarray,
    loo_ground_truth: np.ndarray,
) -> dict:
    """
    Compute rank (Spearman) and magnitude (Pearson) fidelity over flattened arrays.
    Returns: {'rho_r': float, 'rho_m': float}
    """
    ...

def build_metrics_dataframe(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,
) -> pd.DataFrame:
    """
    Build DataFrame with columns: [method, budget, seed, rho_r, rho_m, error_norm]
    where error_norm = ||scores - loo_exact||_2
    """
    ...

def compute_partial_correlation(
    metrics_df: pd.DataFrame,
    budget_level: int,
) -> float:
    """
    pg.partial_corr(data=df_at_budget, x='rho_r', y='rho_m', covar='budget')
    Returns partial correlation r at the given budget level.
    """
    ...

def compute_partial_correlations_all_budgets(
    metrics_df: pd.DataFrame,
    budgets: List[int],
) -> Dict[int, float]:
    """
    Compute partial corr at each budget level.
    Returns: {budget: partial_corr}
    """
    ...

def compute_single_error_axis_r2(
    metrics_df: pd.DataFrame,
) -> dict:
    """
    Regress rho_r and rho_m on error_norm via sklearn LinearRegression.
    Returns: {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    """
    ...

def check_success_criteria(
    partial_corrs: Dict[int, float],
    r2_results: dict,
    cfg: HM1Config,
) -> dict:
    """
    Returns: {'gate_pass': bool, 'partial_corr_pass': bool, 'r2_pass': bool,
              'partial_corrs': dict, 'r2_results': dict}
    """
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, numpy, pandas, config

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict
from config import HM1Config

def plot_gate_metric(
    partial_corrs: Dict[int, float],
    cfg: HM1Config,
) -> None:
    """
    Bar chart: partial corr per budget. Horizontal line at 0.95 threshold.
    Saves: cfg.figures_dir/gate_partial_correlation.png
    """
    ...

def plot_scatter_rho_r_rho_m(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    rho_r vs rho_m scatter, colored by method, faceted by budget.
    Saves: cfg.figures_dir/scatter_metrics.png
    """
    ...

def plot_error_axis_regression(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    Metrics vs approximation error norm with regression line and R^2 annotation.
    Saves: cfg.figures_dir/error_axis_regression.png
    """
    ...

def plot_method_comparison(
    metrics_df: pd.DataFrame,
    cfg: HM1Config,
) -> None:
    """
    Bar chart: rho_r and rho_m per method at each budget.
    Saves: cfg.figures_dir/method_comparison.png
    """
    ...

def plot_hessian_eigenspectrum(
    eigenvalues: np.ndarray,
    cfg: HM1Config,
) -> None:
    """
    Log-scale histogram of Hessian eigenvalues.
    Saves: cfg.figures_dir/hessian_eigenspectrum.png
    """
    ...

def plot_all(
    partial_corrs: Dict[int, float],
    metrics_df: pd.DataFrame,
    eigenvalues: np.ndarray,
    cfg: HM1Config,
) -> None:
    """Call all figure functions above."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules above

```python
import os
import sys
import json
import numpy as np
import pandas as pd
from config import get_config, HM1Config
from features import FeatureExtractor
from convex_model import ConvexLogisticModel
from loo_influence import ClosedFormLOO
from attribution_convex import LinearAttributionRunner
from metrics_analysis import (
    build_metrics_dataframe, compute_partial_correlations_all_budgets,
    compute_single_error_axis_r2, check_success_criteria
)
from visualize import plot_all

def main() -> None:
    """
    Full pipeline:
    1. Extract ResNet-18 features from CIFAR-10
    2. Fit logistic regression, verify convexity
    3. Compute closed-form LOO via Hessian inversion
    4. Run all attribution methods (4 x 5 x 3 grid)
    5. Build metrics DataFrame
    6. Compute partial correlations per budget
    7. Compute single-error-axis R^2
    8. Check success criteria, save results
    9. Generate all figures
    """
    ...

if __name__ == '__main__':
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config dataclass, sys.path integration with h-e1 | 6 | 1+1+2+2 |
| A-2 | Feature Extraction | Load H-E1 ResNet-18 checkpoint, remove FC, extract 512-dim features, StandardScaler, cache | 10 | 2+3+3+2 |
| A-3 | Convex Model | Fit sklearn LogisticRegression, compute Hessian, verify positive-definite eigenvalues | 10 | 2+2+4+2 |
| A-4 | Closed-Form LOO | Exact H^{-1} inversion (scipy.linalg.inv), gradient computation, influence matrix (5000x100), cache | 14 | 3+3+5+3 |
| A-5 | Linear Attribution Methods | Adapt H-E1 TRAK/TracIn/IF/FastIF for feature-space linear model, full 4x5x3 grid | 14 | 3+4+4+3 |
| A-6 | Metrics DataFrame | Build flat DataFrame (method, budget, seed, rho_r, rho_m, error_norm) from all scores | 8 | 2+2+2+2 |
| A-7 | Partial Correlation Analysis | pingouin.partial_corr per budget, check >= 0.95 threshold at all 5 budgets | 10 | 2+2+4+2 |
| A-8 | Single-Error-Axis R^2 | Regress rho_r/rho_m on error_norm, compute R^2, check >= 0.95 | 9 | 2+2+3+2 |
| A-9 | Visualization | 5 figures: gate bar chart, scatter, error-axis regression, method comparison, eigenspectrum | 9 | 2+1+3+3 |
| A-10 | Orchestration & Results | run_experiment.py main(), save metrics.csv, success criteria report, 04_validation.md prep | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-5], Medium(9-13): [A-2, A-3, A-7, A-8, A-9], Low(4-8): [A-1, A-6, A-10]

---

## Module Dependency Graph

- `run_experiment.py` -> all modules
- `metrics_analysis.py` -> `attribution_convex.py`, `loo_influence.py`, h-e1/evaluate.py
- `attribution_convex.py` -> `features.py`, h-e1/attribution.py
- `loo_influence.py` -> `convex_model.py`
- `convex_model.py` -> `features.py`
- `features.py` -> h-e1/model.py (build_model)
- `visualize.py` -> `metrics_analysis.py`
- all -> `config.py`
