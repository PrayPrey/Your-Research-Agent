# Configuration: H-M1 Convex Metric Coupling

**Date:** 2026-03-26
**Hypothesis:** H-M1 (MECHANISM)
**Gate:** MUST_WORK

Applied: dataclass-config-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (h-e1/code/config.py read directly)
**Config Files Found**: `h-e1/code/config.py` (ExperimentConfig dataclass)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256
    epochs: int = 200
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    lr_milestones: List[int] = field(default_factory=lambda: [100, 150])
    lr_gamma: float = 0.1
    n_loo_retrains: int = 10
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## A-1: Setup & Config [Complexity: 6, Budget: 1 subtask]

Applied: dataclass-config-pattern

### Configuration (Python Dataclass)

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
    test_subset_size: int = 100  # matches h-e1 loo_test_size=100
    subset_seed: int = 42
    feature_dim: int = 512
    n_classes: int = 10

    # Logistic Regression
    C: float = 100.0              # lambda_reg = 1/C = 0.01
    lr_solver: str = 'lbfgs'
    lr_max_iter: int = 1000

    # Experiment
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    n_bootstrap: int = 1000

    # Success thresholds
    # Non-standard: 0.95 set by hypothesis gate criteria (MUST_WORK)
    partial_corr_threshold: float = 0.95
    r2_threshold: float = 0.95

    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> HM1Config:
    return HM1Config()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config dataclass | Implement HM1Config with get_config(), verify sys.path injection for h-e1 |

---

## A-2: Feature Extraction [Complexity: 10, Budget: 1 subtask]

Applied: standard-pytorch-feature-extraction

### Configuration

Uses `HM1Config` fields: `he1_checkpoint`, `he1_code_path`, `data_root`, `train_subset_size`, `test_subset_size`, `subset_seed`, `feature_dim`, `results_dir`.

Feature cache path: `{results_dir}/features_cache.npz`

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | FeatureExtractor | Load ResNet-18, remove FC, extract 512-dim, StandardScaler, cache to npz |

---

## A-3: Convex Model [Complexity: 10, Budget: 1 subtask]

Applied: sklearn-logistic-regression-pattern

### Configuration

Uses `HM1Config` fields: `C=100.0`, `lr_solver='lbfgs'`, `lr_max_iter=1000`.
Hessian regularization: `lambda_reg = 1/C = 0.01`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ConvexLogisticModel | Fit LR, compute Hessian H=(1/N)X^TWX + lambda*I, verify PD eigenvalues |

---

## A-4: Closed-Form LOO [Complexity: 14, Budget: 1 subtask]

Applied: influence-function-hessian-inversion-pattern

### Configuration

Uses `HM1Config` fields: `results_dir`.
LOO influence cache: `{results_dir}/loo_exact_cache.npy`
Hessian shape: (512, 512) - exact inversion via `scipy.linalg.inv`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | ClosedFormLOO | H^{-1} exact inversion, grad computation, influence matrix (5000x100), cache |

---

## A-5: Linear Attribution Methods [Complexity: 14, Budget: 1 subtask]

Applied: logistic-regression-influence-functions-pattern

### Configuration

Uses `HM1Config` fields: `methods`, `compute_budgets`, `seeds`.

BUDGET_MAP_CONVEX (hardcoded in attribution_convex.py):
```python
BUDGET_MAP_CONVEX = {
    'TRAK':   {10: {'proj_dim': 10},  25: {'proj_dim': 25},  50: {'proj_dim': 50},
               75: {'proj_dim': 75},  100: {'proj_dim': 100}},
    'TracIn': {10: {'scale': 1}, 25: {'scale': 2}, 50: {'scale': 3},
               75: {'scale': 4}, 100: {'scale': 5}},
    'IF':     {10: {'depth': 10}, 25: {'depth': 25}, 50: {'depth': 50},
               75: {'depth': 75}, 100: {'depth': 100}},
    'FastIF': {10: {'scale': 1}, 25: {'scale': 2}, 50: {'scale': 3},
               75: {'scale': 4}, 100: {'scale': 5}},
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | LinearAttributionRunner | Adapt TRAK/TracIn/IF/FastIF for feature-space; run 4x5x3 grid |

---

## A-6 through A-10: Metrics, Analysis, Visualization, Orchestration [Budget: 2 subtasks]

Applied: standard-metrics-reporting-pattern

### Configuration

Uses `HM1Config` fields: `partial_corr_threshold=0.95`, `r2_threshold=0.95`, `n_bootstrap=1000`, `results_dir`, `figures_dir`.

Output files:
- `{results_dir}/metrics.csv` - DataFrame (method, budget, seed, rho_r, rho_m, error_norm)
- `{results_dir}/success_criteria.json` - gate pass/fail + partial_corrs + r2_results
- `{figures_dir}/gate_partial_correlation.png`
- `{figures_dir}/scatter_metrics.png`
- `{figures_dir}/error_axis_regression.png`
- `{figures_dir}/method_comparison.png`
- `{figures_dir}/hessian_eigenspectrum.png`

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Metrics & Analysis | build_metrics_dataframe, partial_corr per budget (pingouin), R^2 regression, check_success_criteria |
| C-6-2 | Visualization & Orchestration | 5 figures (visualize.py), run_experiment.py main(), save CSV + JSON results |
