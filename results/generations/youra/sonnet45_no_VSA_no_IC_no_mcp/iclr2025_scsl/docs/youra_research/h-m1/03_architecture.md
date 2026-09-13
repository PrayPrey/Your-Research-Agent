# Architecture Document: h-m1

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Tier**: 1.5 (Simple-to-Moderate)  
**Budget**: 350-550 tokens  
**Prerequisite**: h-e1 (VALIDATED)

**Applied**: Backward hooks pattern, group-stratified gradient analysis  
**Codebase**: Reuses h-e1 data loader, models, training scaffold (80% reuse)

---

## System Overview

Tests whether BN amplifies spurious learning via batch-level statistics by measuring gradient flow to spurious vs core features during epochs 1-20. Extends h-e1 training loop with backward hooks to capture gradient norms on majority/minority groups.

**Core Addition**: Gradient measurement infrastructure on top of h-e1 baseline.

---

## Module Breakdown

### M1: Gradient Hooks (`gradient_hooks.py`)

**Dependencies**: torch

```python
class GradientTracker:
    def __init__(self, model: nn.Module, track_layers: list[str]):
        self.model = model
        self.track_layers = track_layers
        self.gradient_norms = {}
        self.hooks = []
    
    def register_hooks(self) -> None: ...
    def remove_hooks(self) -> None: ...
    def get_gradient_norms(self) -> dict[str, float]: ...
    def reset(self) -> None: ...
```

**Tracked Layers**:
- `conv1.weight` (first conv, spurious-sensitive)
- First normalization layer (BN/LN)
- Last normalization layer (BN/LN)

---

### M2: Group-Stratified Gradient Analysis (`group_gradients.py`)

**Dependencies**: torch, M1

```python
def split_by_spurious_alignment(group_ids: Tensor) -> tuple[Tensor, Tensor]:
    """Split into majority (groups 0,3) and minority (groups 1,2)."""
    ...

def compute_group_gradient_norms(
    model: nn.Module,
    dataloader: DataLoader,
    device: str,
    majority_groups: list[int],
    minority_groups: list[int]
) -> dict[str, float]:
    """
    Returns:
        {
            'grad_majority_norm': float,
            'grad_minority_norm': float,
            'grad_ratio': float,
            'conv1_grad_norm': float,
            'first_norm_grad_norm': float,
            'last_norm_grad_norm': float
        }
    """
    ...
```

---

### M3: Training with Gradient Logging (`train_with_gradients.py`)

**Dependencies**: h-e1 modules, M1, M2

```python
def train_with_gradient_measurement(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: Optimizer,
    criterion: nn.Module,
    num_epochs: int,
    device: str,
    seed: int,
    gradient_measurement_epochs: range = range(1, 21)
) -> pd.DataFrame:
    """
    Extended training loop from h-e1.
    
    On epochs 1-20: measure gradients via backward hooks.
    On epochs 21-100: standard training (hooks removed).
    
    Returns:
        DataFrame with columns: epoch, seed, arch, avg_acc, worst_group_acc,
        worst_group_gap, group_0_acc, group_1_acc, group_2_acc, group_3_acc,
        grad_majority_norm, grad_minority_norm, grad_ratio, conv1_grad_norm,
        first_norm_grad_norm, last_norm_grad_norm
    """
    ...
```

**Integration Points**:
- Reuses `h-e1/train.py::evaluate_groups()` for per-group accuracy
- Adds gradient measurement after each validation epoch (epochs 1-20)
- Hooks removed after epoch 20 to reduce overhead

---

### M4: Statistical Analysis (`analyze_gradients.py`)

**Dependencies**: scipy, numpy, pandas

```python
def compute_gradient_statistics(
    metrics_df: pd.DataFrame,
    epochs_range: range = range(1, 21)
) -> dict:
    """
    Compute mean gradient ratio per architecture across 10 seeds.
    
    Returns:
        {
            'bn_mean_ratio': float,
            'ln_mean_ratio': float,
            'ratio_difference': float,
            't_statistic': float,
            'p_value': float,
            'cohens_d': float,
            'success': bool
        }
    """
    ...

def independent_t_test(
    bn_samples: np.ndarray,
    ln_samples: np.ndarray
) -> tuple[float, float, float]:
    """Returns (t_stat, p_value, cohens_d)."""
    ...
```

---

### M5: Visualization (`plot_gradients.py`)

**Dependencies**: matplotlib, pandas

```python
def plot_gradient_ratio_over_time(
    metrics_df: pd.DataFrame,
    output_path: str
) -> None:
    """Line plot with ±1 std shaded region (epochs 1-20)."""
    ...

def plot_gradient_ratio_boxplot(
    metrics_df: pd.DataFrame,
    output_path: str
) -> None:
    """Box plot: 10 points per architecture."""
    ...

def plot_layer_gradient_heatmap(
    metrics_df: pd.DataFrame,
    output_path: str
) -> None:
    """Heatmap: layers × epochs (1-20) for BN and LN."""
    ...
```

---

## Reused Modules from h-e1

**No modifications needed:**

| Module | Path | Usage |
|--------|------|-------|
| Data Loader | `h-e1/data_loader.py` | Waterbirds dataset (synthetic) with group labels |
| Models | `h-e1/models.py` | ResNet-18-BN, ResNet-18-LN, He init |
| Evaluation | `h-e1/train.py::evaluate_groups()` | Per-group accuracy computation |

**Import Paths**:
```python
from h-e1.data_loader import get_waterbirds_dataloader
from h-e1.models import get_resnet18_bn, get_resnet18_ln
```

---

## Data Flow

```
[Waterbirds Dataset (h-e1)]
         ↓
[ResNet-BN / ResNet-LN (h-e1)]
         ↓
[Training Loop] ← [Gradient Hooks (M1)] (epochs 1-20 only)
         ↓
[Validation] → [Group Split (M2)] → [Gradient Norms (M2)]
         ↓
[Metrics CSV] → [Statistical Test (M4)] → [Visualization (M5)]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-HOOKS | Gradient tracking infrastructure | Implement backward hooks for gradient norm capture | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |
| M2-GROUP | Group-stratified gradient analysis | Split majority/minority, compute gradient ratio | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| M3-TRAIN | Extended training loop | Integrate gradient measurement into h-e1 training | 12 | Module(3) + Deps(3) + Algo(2) + Integ(4) |
| M4-STATS | Statistical analysis | T-test, Cohen's d, success criterion evaluation | 7 | Module(2) + Deps(1) + Algo(3) + Integ(1) |
| M5-VIZ | Visualization | 3 plots (line, box, heatmap) | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| M6-EXEC | Experiment execution | Run 20 experiments (2 archs × 10 seeds) | 5 | Module(1) + Deps(1) + Algo(1) + Integ(2) |

**Distribution**: High(9-13): [M2-GROUP, M3-TRAIN], Medium(6-8): [M1-HOOKS, M4-STATS], Low(4-5): [M5-VIZ, M6-EXEC]

**Total Complexity**: 48 (Tier 1.5 appropriate)

---

## Quality Gates

### Pre-Implementation
- [ ] h-e1 codebase accessible and validated
- [ ] Import paths verified (h-e1 modules loadable)

### Implementation
- [ ] Hooks capture non-zero gradient norms
- [ ] Majority/minority split correct (groups 0,3 vs 1,2)
- [ ] No division by zero in gradient ratio
- [ ] Gradient measurement epochs 1-20 only
- [ ] Hooks removed after epoch 20

### Validation
- [ ] All 20 runs complete without errors
- [ ] Gradient ratio shows non-zero variance
- [ ] CSV includes gradient columns for epochs 1-20
- [ ] Statistical test outputs t-stat, p-value, Cohen's d
- [ ] Success criterion evaluated (BN ratio ≥ 20% higher, p < 0.05, d ≥ 0.5)

---

## File Structure

```
h-m1/
├── gradient_hooks.py          # M1: Backward hook registration
├── group_gradients.py          # M2: Group-stratified gradient computation
├── train_with_gradients.py    # M3: Training loop with gradient logging
├── analyze_gradients.py        # M4: Statistical test
├── plot_gradients.py           # M5: Visualization
├── run_experiment.sh           # M6: Execution script
└── results/
    └── h-m1/
        ├── training_metrics.csv
        ├── gradient_analysis.txt
        ├── gradient_ratio_over_time.png
        ├── gradient_ratio_boxplot.png
        └── layer_gradient_heatmap.png
```

---

## Implementation Notes

### Gradient Measurement Strategy

**Backward Hook Approach** (simplest):
```python
def register_hook(param, name, storage):
    def hook(grad):
        storage[name] = grad.norm().item()
    param.register_hook(hook)
```

**Group-Stratified Loss**:
1. Forward pass on validation set
2. Compute loss separately for majority/minority groups
3. Single backward pass on combined loss
4. Hooks capture gradient norms during backward

**Efficiency**:
- Gradient measurement only on validation set (not train)
- Hooks active epochs 1-20 only (~20% overhead)
- Hooks removed after epoch 20 (no memory leak)

### Statistical Test Design

**Independent t-test** (not paired):
- BN gradient ratios: 10 samples (one per seed)
- LN gradient ratios: 10 samples (one per seed)
- Each sample: mean gradient ratio over epochs 1-20

**Success Criterion**:
```python
success = (
    bn_mean_ratio >= ln_mean_ratio * 1.2 and
    p_value < 0.05 and
    cohens_d >= 0.5
)
```

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Gradient noise | Average over 10 seeds, 20 epochs |
| Spurious/core proxy invalid | Validate: majority ≠ minority gradient |
| Gradient vanishing | Use gradient norm (not raw), log scale plots |
| Computational overhead | Measure on val only, remove hooks after epoch 20 |

---

**Architecture Status**: READY FOR IMPLEMENTATION  
**Code Reuse**: 80% (h-e1 components)  
**New Code Estimate**: ~400 LoC (5 modules)
