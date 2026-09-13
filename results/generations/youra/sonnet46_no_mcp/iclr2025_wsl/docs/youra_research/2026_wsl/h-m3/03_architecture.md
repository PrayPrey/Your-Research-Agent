# Architecture: h-m3
# NFN vs Flat MLP Δρ Controlled Benchmark (MNIST-CNN + CIFAR-10)

Applied: Standard DL Experiment Pattern (multi-encoder checkpoint-reuse comparison)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m1 and h-m2)
**Status**: Patterns found from base code (direct file reads)
**Analyzed Path**: `h-m1/code/` and `h-m2/code/`
**Findings**: h-m1 uses flat `WeightDataset` (flattened vectors, z-score from train). h-m2 uses `NFNWeightDataset` yielding `(weight_list, flat_w, acc)` with custom `collate_nfn`. Both share identical `_load_raw_splits` logic (keys: `trainset/valset/testset`, final-epoch filter). h-m1 checkpoint keys: `model_state_dict`. h-m2 same pattern.

---

## File Organization

- `h-m3/code/`
  - `config.py` — ExperimentConfig (both zoos, all encoders)
  - `data_loader.py` — unified loader for MNIST-CNN and CIFAR-10 (wraps h-m1/h-m2 loaders)
  - `models.py` — DeepSetsEncoder + DeepSetsWithHead (new); import h-m1/h-m2 classes
  - `train.py` — training loop for Deep Sets (MNIST-CNN + CIFAR-10); checkpoint loading for flat/NFN
  - `evaluate.py` — Spearman ρ + bootstrap CI; gate check; tier analysis (P2/P3)
  - `visualize.py` — bar chart, symmetry spectrum, tier Δρ, bootstrap histogram, cross-zoo
  - `run_experiment.py` — orchestrator: data → train → evaluate → visualize → gate
  - `results/` — JSON outputs
  - `figures/` — PNG outputs

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| FlatMLPEncoder | `sys.path.insert(0, "../h-m1/code"); from models import FlatMLPEncoder, FlatMLPWithHead` | `h-m1/code/models.py` |
| WeightDataset | `from data_loader import WeightDataset, load_and_split_dataset, build_dataloaders` | `h-m1/code/data_loader.py` |
| NFNEncoder | `sys.path.insert(0, "../h-m2/code"); from models import NFNEncoder, NFNWithHead` | `h-m2/code/models.py` |
| NFNWeightDataset | `from data_loader import NFNWeightDataset, load_and_split_dataset_nfn, build_dataloaders_nfn, collate_nfn` | `h-m2/code/data_loader.py` |

**Checkpoint paths (verified from h-m1/h-m2 actual results conventions):**
- Flat MLP: `../h-m1/code/results/best_flat_mlp_encoder.pt`
- NFN: `../h-m2/code/results/best_nfn_encoder.pt`

**Verified from**: `h-m1/code/` and `h-m2/code/` (actual implementation)

---

## Modules

### ExperimentConfig (`config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Paths
    mnist_data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    cifar_data_dir: Path = Path("../../.data_cache/datasets/cifar10")
    hm1_code_dir: Path = Path("../../h-m1/code")
    hm2_code_dir: Path = Path("../../h-m2/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")

    # Training (Deep Sets only — flat/NFN reuse checkpoints for MNIST-CNN)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    t_max: int = 150
    eta_min: float = 1e-6

    # Deep Sets capacity grid search
    embed_dim: int = 128
    phi_hidden_candidates: List[int] = field(default_factory=lambda: [64, 96, 128, 160, 192, 256])
    rho_hidden: int = 256
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Bootstrap CI
    n_resamples: int = 1000

    # Gate thresholds
    delta_rho_mnist_threshold: float = 0.05
    delta_rho_cifar_threshold: float = 0.0

def set_seed(seed: int) -> None: ...
```

---

### DataLoader (`data_loader.py`)

**Dependencies**: h-m1/data_loader.py, h-m2/data_loader.py

```python
def load_mnist_flat(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
    """Load MNIST-CNN zoo as flat vectors (for FlatMLP + DeepSets).
    Returns: train_loader, val_loader, test_loader, input_dim
    Delegates to h-m1 load_and_split_dataset + build_dataloaders.
    """
    ...

def load_mnist_nfn(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, List[tuple]]:
    """Load MNIST-CNN zoo as structured weight lists (for NFNEncoder).
    Returns: train_loader, val_loader, test_loader, weight_shapes
    Delegates to h-m2 load_and_split_dataset_nfn + build_dataloaders_nfn.
    """
    ...

def load_cifar_flat(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
    """Load CIFAR-10 zoo as flat vectors (for FlatMLP + DeepSets).
    Same logic as load_mnist_flat but from cfg.cifar_data_dir.
    Returns: train_loader, val_loader, test_loader, input_dim
    """
    ...

def load_cifar_nfn(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, List[tuple]]:
    """Load CIFAR-10 zoo as structured weight lists (for NFNEncoder).
    Returns: train_loader, val_loader, test_loader, weight_shapes
    """
    ...

def download_cifar_zoo(cfg) -> bool:
    """Download CIFAR-10 zoo from ModelZoos/ModelZooDataset if not cached.
    Returns True if available (already cached or freshly downloaded).
    """
    ...
```

---

### Models (`models.py`)

**Dependencies**: h-m1/models.py (FlatMLPEncoder, FlatMLPWithHead), h-m2/models.py (NFNEncoder, NFNWithHead)

```python
import sys
# Imports added at runtime via sys.path:
# from h-m1 models: FlatMLPEncoder, FlatMLPWithHead, count_params
# from h-m2 models: NFNEncoder, NFNWithHead


class DeepSetsEncoder(nn.Module):
    """Permutation-invariant encoder via sum pooling (Zaheer et al. 2017).
    Treats each weight tensor (flattened per-layer) as one set element.
    """
    def __init__(self, element_dim: int, phi_hidden: int, rho_hidden: int, embed_dim: int = 128): ...
    def forward(self, x_elements: torch.Tensor) -> torch.Tensor:
        # x_elements: (B, N_elements, element_dim) → (B, embed_dim)
        ...


class DeepSetsWithHead(nn.Module):
    """DeepSetsEncoder + Linear(embed_dim, 1) prediction head."""
    def __init__(self, encoder: DeepSetsEncoder, embed_dim: int = 128): ...
    def forward(self, x_elements: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Returns (embedding (B, embed_dim), prediction (B, 1))
        ...


def count_params(model: nn.Module) -> int: ...

def grid_search_deep_sets(
    element_dim: int,
    phi_hidden_candidates: List[int],
    rho_hidden: int,
    embed_dim: int,
    target_min: int,
    target_max: int,
) -> Tuple[DeepSetsEncoder, int, int]:
    """Grid search phi_hidden to hit [target_min, target_max] params.
    Returns: (encoder, phi_hidden, param_count)
    """
    ...

def load_flat_mlp_checkpoint(cfg, input_dim: int) -> FlatMLPWithHead:
    """Load h-m1 trained checkpoint. Raises if file missing."""
    ...

def load_nfn_checkpoint(cfg, weight_shapes: List[tuple]) -> NFNWithHead:
    """Load h-m2 trained checkpoint. Raises if file missing."""
    ...
```

---

### Train (`train.py`)

**Dependencies**: config.py, models.py, data_loader.py

```python
def train_deep_sets(
    model: DeepSetsWithHead,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: ExperimentConfig,
    device: torch.device,
    checkpoint_name: str,
) -> Tuple[DeepSetsWithHead, Dict]:
    """Train Deep Sets encoder with AdamW + CosineAnnealingLR.
    Saves best checkpoint by val loss to cfg.results_dir/checkpoint_name.
    Returns: (trained_model, training_metrics_dict)
    """
    ...

def prepare_flat_elements(flat_w: torch.Tensor, weight_shapes: List[tuple]) -> torch.Tensor:
    """Reshape flat weight vector into (N_elements, max_dim) padded tensor for DeepSets.
    Each weight tensor becomes one element; pad to uniform element_dim.
    Returns: (N_elements, element_dim) — caller batches to (B, N, element_dim).
    """
    ...
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: models.py, data_loader.py, config.py

```python
def bootstrap_spearman_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap 95% CI for Spearman ρ.
    Returns: (median_rho, ci_lower_2.5pct, ci_upper_97.5pct)
    """
    ...

def evaluate_flat_encoder(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    n_resamples: int = 1000,
) -> Dict:
    """Run inference with flat weight vector batches; compute ρ + CI.
    Batch format: (flat_w, acc) — h-m1 WeightDataset format.
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float, 'preds': list, 'labels': list}
    """
    ...

def evaluate_deep_sets_encoder(
    model: DeepSetsWithHead,
    loader: DataLoader,
    device: torch.device,
    weight_shapes: List[tuple],
    n_resamples: int = 1000,
) -> Dict:
    """Run inference with element-structured batches; compute ρ + CI.
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float}
    """
    ...

def evaluate_nfn_encoder(
    model: NFNWithHead,
    loader: DataLoader,
    device: torch.device,
    n_resamples: int = 1000,
) -> Dict:
    """Run inference with NFN weight_list batches; compute ρ + CI.
    Batch format: (weight_list, flat_w, acc) — h-m2 NFNWeightDataset format.
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float}
    """
    ...

def compute_delta_rho_ci(
    nfn_preds: np.ndarray,
    flat_preds: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap CI for Δρ = ρ(NFN) − ρ(flat) using paired resampling.
    Returns: (delta_rho, ci_lower, ci_upper)
    """
    ...

def compute_tier_analysis(
    flat_preds: np.ndarray,
    nfn_preds: np.ndarray,
    labels: np.ndarray,
) -> Dict:
    """Partition test set into accuracy terciles; compute Δρ per tier (P3).
    Returns: {'low': delta_rho, 'mid': delta_rho, 'high': delta_rho}
    """
    ...

def check_hm3_gate(results: Dict) -> Tuple[bool, bool]:
    """Evaluate P1 (primary gate) and P2 (symmetry spectrum).
    P1: Δρ(MNIST) ≥ 0.05, CI_lower > 0, Δρ(CIFAR) > 0, CI_lower > 0
    P2: ρ(flat) < ρ(deep_sets) < ρ(NFN) on MNIST-CNN
    Returns: (p1_pass, p2_pass)
    """
    ...

def save_results(results: Dict, cfg: ExperimentConfig) -> None:
    """Save full results dict as h-m3_results.json to cfg.results_dir."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: evaluate.py, config.py

```python
def plot_rho_comparison(results: Dict, figures_dir: Path) -> None:
    """Bar chart: ρ per encoder per zoo with 95% CI error bars and Δρ annotations."""
    ...

def plot_symmetry_spectrum(results: Dict, figures_dir: Path) -> None:
    """Scatter: ρ vs symmetry level (none / invariant / equivariant) — P2 check."""
    ...

def plot_tier_delta_rho(tier_results: Dict, figures_dir: Path) -> None:
    """Bar chart: Δρ(NFN vs flat) per accuracy tercile on MNIST-CNN — P3."""
    ...

def plot_bootstrap_distribution(boot_deltas: np.ndarray, ci: Tuple, figures_dir: Path) -> None:
    """Histogram of bootstrap Δρ distribution with CI shading (MNIST-CNN)."""
    ...

def plot_cross_zoo_consistency(results: Dict, figures_dir: Path) -> None:
    """Side-by-side ρ bars: MNIST-CNN vs CIFAR-10 for all three encoders."""
    ...

def plot_capacity_curve(param_counts: Dict, rho_values: Dict, figures_dir: Path) -> None:
    """Scatter: param count vs ρ for all encoders (if grid search data available)."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None:
    """Orchestrate full h-m3 experiment.

    Steps:
    1. Setup: set_seed, device, dirs
    2. Download CIFAR-10 zoo if not cached
    3. MNIST-CNN flat data → load FlatMLP checkpoint → evaluate
    4. MNIST-CNN NFN data → load NFN checkpoint → evaluate
    5. MNIST-CNN flat data → Deep Sets grid search → train → evaluate
    6. CIFAR-10 flat data → train FlatMLP fresh → evaluate
    7. CIFAR-10 NFN data → train NFN fresh → evaluate
    8. CIFAR-10 flat data → train Deep Sets fresh → evaluate
    9. Tier analysis (P3) on MNIST-CNN test
    10. Gate check (P1, P2)
    11. Visualize all figures
    12. Save results JSON
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data | Config, CIFAR-10 download, unified data_loader.py wrapping h-m1/h-m2 loaders | 10 | 2+2+3+3 |
| A-2 | Deep Sets Model | DeepSetsEncoder, DeepSetsWithHead, grid search for ~500K params, element reshaping for weight-space | 13 | 3+2+4+4 |
| A-3 | Checkpoint Loading | load_flat_mlp_checkpoint + load_nfn_checkpoint with fallback retrain; verify state_dict compatibility | 9 | 2+3+2+2 |
| A-4 | Deep Sets Training (MNIST-CNN) | Train Deep Sets on MNIST-CNN with AdamW+CosineAnnealing; save best checkpoint | 9 | 2+2+3+2 |
| A-5 | CIFAR-10 Training (All Encoders) | Train all 3 encoders fresh on CIFAR-10; handle input_dim difference; Deep Sets grid search on CIFAR shapes | 14 | 3+3+4+4 |
| A-6 | Evaluation & Bootstrap CI | evaluate_flat/deep_sets/nfn_encoder; bootstrap_spearman_ci; compute_delta_rho_ci; tier analysis P3 | 15 | 4+3+4+4 |
| A-7 | Gate Check | check_hm3_gate (P1+P2); save_results JSON; structured results dict aggregation | 7 | 2+1+2+2 |
| A-8 | Visualization | All 5+ figures (bar chart, spectrum, tier, bootstrap hist, cross-zoo); seaborn styling | 11 | 3+2+3+3 |
| A-9 | Orchestration | run_experiment.py: full pipeline sequencing, error handling (CIFAR unavailable), logging | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-6], Medium(9-13): [A-1, A-2, A-3, A-4, A-8, A-9], Low(4-8): [A-7]

---

## Key Interface Notes

- **DeepSets element format**: each weight tensor (from zoo state_dict) is treated as ONE set element after flattening. Use `prepare_flat_elements()` in `train.py` to reshape flat vector `(input_dim,)` → padded `(N_layers, element_dim)`. This differs from Deep Sets over rows — we treat layers as elements for simplicity and capacity matching.
- **NFN CIFAR-10**: `NFNWithHead` must be reconstructed with CIFAR-10 `weight_shapes` (different from MNIST-CNN); load `best_nfn_encoder.pt` only for MNIST-CNN; retrain from scratch for CIFAR-10.
- **FlatMLP CIFAR-10**: same — reconstruct with CIFAR-10 `input_dim`; checkpoint only valid for MNIST-CNN.
- **Paired bootstrap for Δρ CI**: resample `(flat_pred, nfn_pred, label)` triples together to preserve pairing; compute Δρ per resample.
- **Batch format summary**:
  - h-m1 loaders → `(flat_w: Tensor(B, D), acc: Tensor(B,))` — used for FlatMLP and DeepSets
  - h-m2 loaders → `(weight_list: List[Tensor(B,...)], flat_w: Tensor(B,D), acc: Tensor(B,))` — used for NFNEncoder
