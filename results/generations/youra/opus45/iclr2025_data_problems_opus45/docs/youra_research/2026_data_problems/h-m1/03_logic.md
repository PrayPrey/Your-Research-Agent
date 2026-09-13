# Logic: H-M1 Convex Metric Coupling

**Date:** 2026-03-26
**Hypothesis:** H-M1 (MECHANISM)
**Gate:** MUST_WORK

Applied: logistic-regression-influence-functions-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP requires active project selection - API signatures verified via direct file reads
**Analyzed Path**: `docs/youra_research/20260323_data_problems/h-e1/code/`
**Relevant Symbols**:
- `AttributionMethod.compute_scores(model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray`
- `BUDGET_MAP: Dict[str, Dict[int, Any]]` - TracIn/FastIF use `n_ckpts`, not `scale`
- `MetricResult(rho_r, rho_m, S, rho_r_ci, rho_m_ci)` dataclass
- `build_model(device='cuda') -> nn.Module` - ResNet-18 with CIFAR-10 modifications

---

## External Dependencies API (Base Hypothesis)

API signatures verified from `/h-e1/code/` actual implementation:

```python
# From: h-e1/code/attribution.py (ACTUAL CODE)
class AttributionMethod(ABC):
    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,   # ExperimentConfig, NOT HM1Config
        device: str = 'cuda',
    ) -> np.ndarray:
        """Returns [n_train, n_test]."""

# BUDGET_MAP actual structure (TracIn/FastIF use n_ckpts, NOT scale!)
BUDGET_MAP = {
    'TRAK':   {10: {'proj_dim': 10}, ...},
    'TracIn': {10: {'n_ckpts': 1}, ...},   # key = n_ckpts
    'IF':     {10: {'depth': 10}, ...},
    'FastIF': {10: {'n_ckpts': 1}, ...},   # key = n_ckpts
}

# From: h-e1/code/model.py (ACTUAL CODE)
def build_model(device: str = 'cuda') -> nn.Module:
    """ResNet-18 for CIFAR-10; conv1=3x3, no maxpool, fc=512->10."""

# From: h-e1/code/evaluate.py (ACTUAL CODE)
@dataclass
class MetricResult:
    rho_r: float
    rho_m: float
    S: float
    rho_r_ci: Tuple[float, float]
    rho_m_ci: Tuple[float, float]
```

**Verified from**: `docs/youra_research/20260323_data_problems/h-e1/code/` (actual files)

---

## A-1: Setup & Config [Complexity: 6, Budget: 4]

Applied: Standard Python dataclass

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM1Config:
    data_root: str = './data'
    he1_checkpoint: str = '../../h-e1/code/checkpoints/model_seed0_final.pt'
    he1_code_path: str = '../../h-e1/code'
    train_subset_size: int = 5000
    test_subset_size: int = 100
    subset_seed: int = 42
    feature_dim: int = 512
    n_classes: int = 10
    C: float = 100.0
    lr_solver: str = 'lbfgs'
    lr_max_iter: int = 1000
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    n_bootstrap: int = 1000
    partial_corr_threshold: float = 0.95
    r2_threshold: float = 0.95
    results_dir: str = './results'
    figures_dir: str = './figures'

def get_config() -> HM1Config: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HM1Config dataclass | All fields with defaults |
| L-1-2 | get_config() | Returns HM1Config, creates dirs |
| L-1-3 | sys.path injection | Insert h-e1/code for imports |
| L-1-4 | requirements.txt | pingouin, scipy, sklearn, matplotlib |

---

## A-2: Feature Extraction [Complexity: 10, Budget: 10]

Applied: Standard PyTorch

### API Signatures

```python
# features.py
class FeatureExtractor:
    def __init__(self, cfg: HM1Config, device: str = 'cuda'): ...

    def load_resnet(self) -> nn.Module:
        """Load h-e1 ResNet-18 via build_model(), then load_state_dict from checkpoint."""
        ...

    def extract(
        self,
        dataloader: DataLoader,
        model: nn.Module,
    ) -> Tuple[np.ndarray, np.ndarray]:
        # features: [N, 512], labels: [N]
        ...

    def get_features(
        self, cfg: HM1Config
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        # Returns (X_train [5000,512], y_train [5000], X_test [100,512], y_test [100])
        # Caches to cfg.results_dir/features_cache.npz
        ...
```

### Pseudo-code

```
1. model = build_model(device); load_state_dict(checkpoint)
2. feature_extractor = Sequential(*list(model.children())[:-1])  # remove fc
3. for batch in loader: feats = feature_extractor(x).squeeze()  # [B, 512]
4. scaler = StandardScaler().fit(X_train_raw)
5. X_train = scaler.transform(X_train_raw)  # [5000, 512]
6. X_test = scaler.transform(X_test_raw)    # [100, 512]
7. cache to npz; return X_train, y_train, X_test, y_test
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_resnet | build_model + load checkpoint |
| L-2-2 | extract() | Remove FC, forward pass, collect features |
| L-2-3 | CIFAR-10 subsets | 5000 train + 100 test DataLoaders |
| L-2-4 | StandardScaler | Fit on train, transform both |
| L-2-5 | npz cache | Load if exists, else compute |

---

## A-3: Convex Model [Complexity: 10, Budget: 8]

Applied: Standard PyTorch / sklearn

### API Signatures

```python
# convex_model.py
class ConvexLogisticModel:
    def __init__(self, cfg: HM1Config): ...

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> 'ConvexLogisticModel':
        # X_train: [5000, 512], y_train: [5000]
        ...

    def get_theta(self) -> np.ndarray:
        # Returns [512, 10] weight matrix (coef_.T)
        ...

    def compute_hessian(self, X: np.ndarray, lambda_reg: float = 0.01) -> np.ndarray:
        # H = X^T @ W @ X / N + lambda*I; W from p*(1-p) averaged over classes
        # Returns H: [512, 512]
        ...

    def verify_convexity(self, X: np.ndarray) -> dict:
        # Returns {'min_eigenvalue': float, 'max_eigenvalue': float, 'is_convex': bool}
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # Returns [N, 10] softmax probabilities
        ...
```

### Pseudo-code (Hessian)

```
theta = get_theta()          # [D, C]
probs = softmax(X @ theta)   # [N, C]
w = probs * (1 - probs)      # [N, C]
W_agg = w.mean(axis=1)       # [N] scalar weight per sample
H = X.T @ diag(W_agg) @ X / N + lambda_reg * eye(D)  # [D, D]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | fit() | sklearn LogisticRegression(C=100, solver='lbfgs', multi_class='multinomial') |
| L-3-2 | get_theta() | coef_.T -> [D, C] |
| L-3-3 | compute_hessian() | Weighted X^T W X / N + lambda*I |
| L-3-4 | verify_convexity() | eigvalsh, assert all > 0 |

---

## A-4: Closed-Form LOO [Complexity: 14, Budget: 10]

Applied: logistic-regression-influence-functions-pattern

### API Signatures

```python
# loo_influence.py
class ClosedFormLOO:
    def __init__(self, model: ConvexLogisticModel, cfg: HM1Config): ...

    def compute_hessian_inverse(
        self, X_train: np.ndarray, lambda_reg: float = 0.01
    ) -> np.ndarray:
        # H: [512, 512] -> H_inv: [512, 512] via scipy.linalg.inv
        ...

    def compute_train_gradients(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> np.ndarray:
        # grad_i = x_i * (p_i - e_{y_i}); Returns [5000, 512]
        ...

    def compute_influence(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        H_inv: np.ndarray,
    ) -> np.ndarray:
        # I(z_i, z_test) = grad_test^T @ H_inv @ grad_i
        # Returns influences: [5000, 100]
        # Cached at cfg.results_dir/loo_exact_cache.npy
        ...
```

### Pseudo-code

```
H_inv = scipy.linalg.inv(H)                   # [512, 512]
grad_train = compute_train_gradients(...)      # [5000, 512]
grad_test  = compute_train_gradients(X_test, y_test, probs_test)  # [100, 512]
s_test = H_inv @ grad_test.T                  # [512, 100]
influences = grad_train @ s_test              # [5000, 100]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_hessian_inverse() | scipy.linalg.inv on [512, 512] |
| L-4-2 | compute_train_gradients() | x*(p - one_hot(y)), shape [N, 512] |
| L-4-3 | compute_influence() | Vectorized: grad_train @ H_inv @ grad_test.T |
| L-4-4 | npy cache | Skip computation if cache exists |
| L-4-5 | one_hot utility | np.eye(C)[y] -> [N, C] |

---

## A-5: Linear Attribution Methods [Complexity: 14, Budget: 10]

Applied: Standard PyTorch

### API Signatures

```python
# attribution_convex.py
# Note: BUDGET_MAP uses n_ckpts for TracIn/FastIF (verified from h-e1 code)
BUDGET_MAP_CONVEX: Dict[str, Dict[int, Any]] = {
    'TRAK':   {10: {'proj_dim': 10}, 25: {'proj_dim': 25}, 50: {'proj_dim': 50},
               75: {'proj_dim': 75}, 100: {'proj_dim': 100}},
    'TracIn': {10: {'n_ckpts': 1}, 25: {'n_ckpts': 2}, 50: {'n_ckpts': 3},
               75: {'n_ckpts': 4}, 100: {'n_ckpts': 5}},
    'IF':     {10: {'depth': 10}, 25: {'depth': 25}, 50: {'depth': 50},
               75: {'depth': 75}, 100: {'depth': 100}},
    'FastIF': {10: {'n_ckpts': 1}, 25: {'n_ckpts': 2}, 50: {'n_ckpts': 3},
               75: {'n_ckpts': 4}, 100: {'n_ckpts': 5}},
}

class LinearAttributionRunner:
    """Run attribution methods on feature-space logistic regression."""

    def __init__(self, cfg: HM1Config): ...

    def compute_method_scores(
        self,
        method_name: str,
        X_train: np.ndarray,    # [5000, 512]
        y_train: np.ndarray,    # [5000]
        X_test: np.ndarray,     # [100, 512]
        y_test: np.ndarray,     # [100]
        budget: int,
        seed: int,
    ) -> np.ndarray:
        # Returns scores: [5000, 100]
        ...

    def run_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Dict[int, List[np.ndarray]]]:
        # Returns results[method][budget] = List[ndarray(5000, 100)] (len=3 seeds)
        ...
```

### Pseudo-code (compute_method_scores)

```
# Wrap feature-space logistic model as nn.Module for h-e1 AttributionMethod
# Build TensorDataset from X, y; create DataLoader
# Instantiate h-e1 method class (TRAKMethod, TracInMethod, etc.)
# Call method.compute_scores(linear_torch_model, train_loader, test_loader,
#                            budget, seed, cfg_adapter, device)
# cfg_adapter: minimal shim mapping HM1Config -> ExperimentConfig fields
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | LinearTorchWrapper | nn.Module wrapping sklearn weights as fixed Linear layer |
| L-5-2 | ExperimentConfig shim | Adapter exposing fields needed by h-e1 AttributionMethod |
| L-5-3 | compute_method_scores() | Instantiate method, build loaders, call compute_scores |
| L-5-4 | run_all() | 4 methods x 5 budgets x 3 seeds nested loop with caching |

---

## A-6: Metrics DataFrame [Complexity: 8, Budget: 6]

Applied: Standard PyTorch

### API Signatures

```python
# metrics_analysis.py
def compute_rho_r_rho_m(
    pred_scores: np.ndarray,      # [5000, 100] flattened
    loo_ground_truth: np.ndarray, # [5000, 100] flattened
) -> dict:
    # Returns {'rho_r': float, 'rho_m': float}
    ...

def build_metrics_dataframe(
    method_scores: Dict[str, Dict[int, List[np.ndarray]]],
    loo_exact: np.ndarray,  # [5000, 100]
) -> pd.DataFrame:
    # Columns: [method, budget, seed, rho_r, rho_m, error_norm]
    # error_norm = ||scores - loo_exact||_F
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_rho_r_rho_m() | spearmanr + pearsonr on flattened arrays |
| L-6-2 | build_metrics_dataframe() | Nested loop, collect rows |
| L-6-3 | error_norm | np.linalg.norm(scores - loo_exact) |

---

## A-7: Partial Correlation Analysis [Complexity: 10, Budget: 8]

Applied: Standard PyTorch

### API Signatures

```python
# metrics_analysis.py (continued)
def compute_partial_correlation(
    metrics_df: pd.DataFrame,
    budget_level: int,
) -> float:
    # pg.partial_corr(data=df_at_budget, x='rho_r', y='rho_m', covar='budget')['r'][0]
    ...

def compute_partial_correlations_all_budgets(
    metrics_df: pd.DataFrame,
    budgets: List[int],
) -> Dict[int, float]:
    # Returns {budget: partial_corr_r}
    ...

def check_success_criteria(
    partial_corrs: Dict[int, float],
    r2_results: dict,
    cfg: HM1Config,
) -> dict:
    # Returns {'gate_pass': bool, 'partial_corr_pass': bool, 'r2_pass': bool,
    #          'partial_corrs': dict, 'r2_results': dict}
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_partial_correlation() | pingouin.partial_corr per budget |
| L-7-2 | compute_partial_correlations_all_budgets() | Loop over 5 budgets |
| L-7-3 | check_success_criteria() | Gate: all partial_corr >= 0.95 |

---

## A-8: Single-Error-Axis R^2 [Complexity: 9, Budget: 6]

Applied: Standard PyTorch

### API Signatures

```python
# metrics_analysis.py (continued)
def compute_single_error_axis_r2(
    metrics_df: pd.DataFrame,
) -> dict:
    # Regress rho_r ~ error_norm and rho_m ~ error_norm via LinearRegression
    # Returns {'r2_rho_r': float, 'r2_rho_m': float, 'r2_avg': float}
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | compute_single_error_axis_r2() | sklearn LinearRegression + r2_score |
| L-8-2 | gate check | r2_avg >= 0.95 threshold |

---

## A-9: Visualization [Complexity: 9, Budget: 6]

Applied: Standard PyTorch

### API Signatures

```python
# visualize.py
def plot_gate_metric(partial_corrs: Dict[int, float], cfg: HM1Config) -> None:
    # Bar chart partial corr per budget; hline at 0.95
    # Saves: cfg.figures_dir/gate_partial_correlation.png
    ...

def plot_scatter_rho_r_rho_m(metrics_df: pd.DataFrame, cfg: HM1Config) -> None:
    # rho_r vs rho_m scatter, colored by method, faceted by budget
    # Saves: cfg.figures_dir/scatter_metrics.png
    ...

def plot_error_axis_regression(metrics_df: pd.DataFrame, cfg: HM1Config) -> None:
    # Metrics vs error_norm with regression line, R^2 annotation
    # Saves: cfg.figures_dir/error_axis_regression.png
    ...

def plot_method_comparison(metrics_df: pd.DataFrame, cfg: HM1Config) -> None:
    # Bar: rho_r, rho_m per method at each budget
    # Saves: cfg.figures_dir/method_comparison.png
    ...

def plot_hessian_eigenspectrum(eigenvalues: np.ndarray, cfg: HM1Config) -> None:
    # Log-scale histogram of eigenvalues
    # Saves: cfg.figures_dir/hessian_eigenspectrum.png
    ...

def plot_all(
    partial_corrs: Dict[int, float],
    metrics_df: pd.DataFrame,
    eigenvalues: np.ndarray,
    cfg: HM1Config,
) -> None: ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | plot_gate_metric() | MANDATORY gate figure |
| L-9-2 | plot_scatter + method_comparison | Supplementary figures |
| L-9-3 | plot_error_axis_regression + eigenspectrum | Supplementary figures |

---

## A-10: Orchestration & Results [Complexity: 8, Budget: 6]

Applied: Standard PyTorch

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """
    1. Extract features (cached)
    2. Fit ConvexLogisticModel, verify convexity
    3. Compute ClosedFormLOO influences (cached)
    4. Run LinearAttributionRunner.run_all()
    5. build_metrics_dataframe()
    6. compute_partial_correlations_all_budgets()
    7. compute_single_error_axis_r2()
    8. check_success_criteria() -> save JSON
    9. metrics_df.to_csv(results_dir/metrics.csv)
    10. plot_all()
    """
    ...
```

### Tensor Shapes Summary

| Variable | Shape | Description |
|----------|-------|-------------|
| X_train | [5000, 512] | Normalized ResNet-18 features |
| X_test | [100, 512] | Normalized ResNet-18 features |
| theta | [512, 10] | Logistic regression weights |
| H | [512, 512] | Hessian matrix |
| H_inv | [512, 512] | Exact Hessian inverse |
| grad_train | [5000, 512] | Per-sample gradients |
| grad_test | [100, 512] | Per-sample gradients |
| influences | [5000, 100] | Exact LOO influence matrix |
| scores | [5000, 100] | Attribution method scores |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main() orchestration | Sequential pipeline with logging |
| L-10-2 | results saving | metrics.csv, success_criteria.json |
| L-10-3 | 04_validation.md prep | Gate pass/fail, partial corrs, R^2 |
