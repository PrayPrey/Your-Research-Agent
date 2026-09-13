# Logic: h-m3 — NFN vs Flat MLP Δρ Controlled Benchmark

Applied: Standard DL Experiment Pattern (multi-encoder checkpoint-reuse comparison)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m1 and h-m2)
**Status**: API signatures verified from actual code (direct file reads — Serena MCP not available)
**Analyzed Path**: `h-m1/code/` and `h-m2/code/`
**Relevant Symbols**:
- `FlatMLPEncoder.__init__(input_dim, hidden_dims, embed_dim=128, dropout=0.1)`
- `FlatMLPWithHead.forward(x: Tensor) -> Tuple[Tensor(B,128), Tensor(B,1)]`
- `NFNEncoder.__init__(weight_shapes, channel_dim, embed_dim=128, n_layers=3)`
- `NFNWithHead.forward(weights: List[Tensor]) -> Tuple[Tensor(B,128), Tensor(B,1)]`
- `WeightDataset.__getitem__ -> Tuple[flat_w: Tensor(D,), acc: Tensor()]`
- `NFNWeightDataset.__getitem__ -> Tuple[List[Tensor], flat_w: Tensor(D,), acc: Tensor()]`
- `collate_nfn(batch) -> (List[Tensor(B,...)], Tensor(B,D), Tensor(B,))`
- h-m1 checkpoint: **NOT saved to disk** — train_encoder returns model in memory only
- h-m2 checkpoint: saved with keys `encoder_state`, `head_state`, `epoch`, `val_loss`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m1/code/models.py (ACTUAL CODE)
class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int], embed_dim: int = 128, dropout: float = 0.1): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...  # (B, input_dim) → (B, embed_dim)

class FlatMLPWithHead(nn.Module):
    def __init__(self, encoder: FlatMLPEncoder, embed_dim: int = 128): ...
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]: ...
    # Returns (embedding (B, embed_dim), prediction (B, 1))

# From: h-m1/code/data_loader.py (ACTUAL CODE)
class WeightDataset(Dataset):
    # __getitem__ -> Tuple[flat_w: Tensor(D,), acc: Tensor()]
    input_dim: int  # attribute

def load_and_split_dataset(cfg) -> Tuple[WeightDataset, WeightDataset, WeightDataset, Tensor, Tensor, List[Dict]]:
    # cfg must have: cfg.data_dir (Path or str), cfg.batch_size
    # Returns: train_ds, val_ds, test_ds, train_mean, train_std, all_checkpoints

def build_dataloaders(train_ds, val_ds, test_ds, cfg) -> Tuple[DataLoader, DataLoader, DataLoader]:
    # cfg must have: cfg.batch_size

# From: h-m2/code/models.py (ACTUAL CODE)
class NFNEncoder(nn.Module):
    def __init__(self, weight_shapes: List[tuple], channel_dim: int, embed_dim: int = 128, n_layers: int = 3): ...
    def forward(self, weights: List[torch.Tensor]) -> torch.Tensor: ...  # → (B, embed_dim)

class NFNWithHead(nn.Module):
    def __init__(self, encoder: NFNEncoder, embed_dim: int = 128): ...
    def forward(self, weights: List[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]: ...
    # Returns (embedding (B, embed_dim), prediction (B, 1))

# From: h-m2/code/data_loader.py (ACTUAL CODE)
class NFNWeightDataset(Dataset):
    # __getitem__ -> Tuple[List[Tensor], flat_w: Tensor(D,), acc: Tensor()]
    input_dim: int  # attribute

def load_and_split_dataset_nfn(cfg) -> Tuple[NFNWeightDataset, NFNWeightDataset, NFNWeightDataset, Tensor, Tensor, List[Dict]]:
    # cfg must have: cfg.data_dir

def build_dataloaders_nfn(train_ds, val_ds, test_ds, cfg) -> Tuple[DataLoader, DataLoader, DataLoader]:
    # Uses collate_nfn; cfg must have: cfg.batch_size

def collate_nfn(batch) -> Tuple[List[Tensor], Tensor, Tensor]:
    # Returns (List[Tensor(B,...)], Tensor(B, D), Tensor(B,))
```

**CRITICAL — Checkpoint format verified from actual code:**
- h-m1: `train_encoder()` does NOT save to disk. `load_flat_mlp_checkpoint` must retrain or the caller saves manually.
- h-m2: saves `{"encoder_state": ..., "head_state": ..., "epoch": ..., "val_loss": ...}` to `results/best_nfn_encoder.pt`

**Verified from**: actual implementation files (NOT specs)

---

## A-2: Deep Sets Model [Complexity: 13, Budget: 2 subtasks]

Applied: Deep Sets (Zaheer et al. 2017) sum-pooling pattern

### API Signatures

```python
class DeepSetsEncoder(nn.Module):
    """Permutation-invariant encoder: phi per element → sum pool → rho MLP."""

    def __init__(
        self,
        element_dim: int,    # padded per-layer feature size
        phi_hidden: int,     # phi MLP hidden width (grid searched)
        rho_hidden: int,     # rho MLP hidden width
        embed_dim: int = 128,
    ):
        # phi: Linear(element_dim, phi_hidden) → ReLU → Linear(phi_hidden, phi_hidden)
        # rho: Linear(phi_hidden, rho_hidden) → ReLU → Linear(rho_hidden, embed_dim)
        ...

    def forward(self, x_elements: torch.Tensor) -> torch.Tensor:
        # x_elements: (B, N_layers, element_dim) → (B, embed_dim)
        # phi applied elementwise: (B, N, element_dim) → (B, N, phi_hidden)
        # sum pool over N: (B, phi_hidden)
        # rho: (B, phi_hidden) → (B, embed_dim)
        ...


class DeepSetsWithHead(nn.Module):
    """DeepSetsEncoder + Linear(embed_dim, 1) head."""

    def __init__(self, encoder: DeepSetsEncoder, embed_dim: int = 128): ...

    def forward(self, x_elements: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x_elements: (B, N_layers, element_dim) → embedding (B, embed_dim), pred (B, 1)
        ...


def grid_search_deep_sets(
    element_dim: int,
    phi_hidden_candidates: List[int],   # e.g. [64, 96, 128, 160, 192, 256]
    rho_hidden: int,
    embed_dim: int,
    target_min: int,    # 475_000
    target_max: int,    # 525_000
) -> Tuple[DeepSetsEncoder, int, int]:
    """Return first encoder within param budget. Raises ValueError if none fit.
    Returns: (encoder, phi_hidden, param_count)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x_elements | (B, N_layers, element_dim) | N_layers = number of weight tensors in zoo model |
| phi_out | (B, N_layers, phi_hidden) | after elementwise phi |
| pooled | (B, phi_hidden) | sum over N_layers dim |
| embedding | (B, embed_dim) | after rho |
| pred | (B, 1) | scalar accuracy prediction |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | DeepSetsEncoder | forward with phi→sum→rho, element_dim padding logic |
| L-2-2 | grid_search_deep_sets | iterate phi_hidden_candidates, count_params, return first in budget |

---

## A-3: Checkpoint Loading [Complexity: 9, Budget: 1 subtask]

Applied: Standard PyTorch checkpoint loading with key verification

### API Signatures

```python
def load_flat_mlp_checkpoint(
    cfg,            # needs cfg.hm1_code_dir, cfg.embed_dim
    input_dim: int,
    hidden_dims: List[int] = [193],
) -> "FlatMLPWithHead":
    """Reconstruct FlatMLPWithHead and load state_dict from h-m1 checkpoint.

    h-m1 checkpoint path: cfg.hm1_code_dir / "results" / "best_flat_mlp_encoder.pt"
    Checkpoint format: raw state_dict (model.state_dict() directly) OR
                       {"model_state_dict": ...} — probe both keys.
    Raises FileNotFoundError if checkpoint missing.
    """
    # 1. sys.path.insert(0, str(cfg.hm1_code_dir))
    # 2. from models import FlatMLPEncoder, FlatMLPWithHead
    # 3. encoder = FlatMLPEncoder(input_dim, hidden_dims, cfg.embed_dim)
    # 4. model = FlatMLPWithHead(encoder, cfg.embed_dim)
    # 5. ckpt = torch.load(path, map_location="cpu", weights_only=False)
    # 6. if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
    #        state = ckpt["model_state_dict"]
    #    elif isinstance(ckpt, dict) and set(ckpt.keys()) <= set(model.state_dict().keys()):
    #        state = ckpt
    #    else: state = ckpt  # assume raw state_dict
    # 7. model.load_state_dict(state, strict=True)
    ...


def load_nfn_checkpoint(
    cfg,            # needs cfg.hm2_code_dir, cfg.embed_dim
    weight_shapes: List[tuple],
    channel_dim: int = 112,
    n_layers: int = 3,
) -> "NFNWithHead":
    """Reconstruct NFNWithHead and load state from h-m2 checkpoint.

    h-m2 checkpoint path: cfg.hm2_code_dir / "results" / "best_nfn_encoder.pt"
    Checkpoint format (VERIFIED): {"encoder_state": ..., "head_state": ..., "epoch": ..., "val_loss": ...}
    Raises FileNotFoundError if checkpoint missing.
    """
    # 1. sys.path.insert(0, str(cfg.hm2_code_dir))
    # 2. from models import NFNEncoder, NFNWithHead
    # 3. encoder = NFNEncoder(weight_shapes, channel_dim, cfg.embed_dim, n_layers)
    # 4. model = NFNWithHead(encoder, cfg.embed_dim)
    # 5. ckpt = torch.load(path, map_location="cpu", weights_only=False)
    # 6. model.encoder.load_state_dict(ckpt["encoder_state"], strict=True)
    #    model.head.load_state_dict(ckpt["head_state"], strict=True)
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_*_checkpoint | Both loaders with key-probing logic and strict load |

---

## A-5: CIFAR-10 Training (All Encoders) [Complexity: 14, Budget: 4 subtasks]

Applied: Standard PyTorch training loop with AdamW + CosineAnnealingLR

### API Signatures

```python
def get_weight_shapes(dataset: "NFNWeightDataset") -> List[tuple]:
    """Extract per-layer weight shapes from first checkpoint for NFNEncoder construction.
    Returns list of shape tuples, e.g. [(32,1,3,3), (32,), ...] for CIFAR-10 CNN.
    """
    # sample = dataset.checkpoints[0]["state_dict"]
    # return [sample[k].shape for k in dataset.weight_key_order]
    ...


def train_flat_mlp_cifar(
    cfg,
    device: torch.device,
) -> Tuple["FlatMLPWithHead", Dict]:
    """Train FlatMLP fresh on CIFAR-10. Grid search hidden_dims for ~500K params.
    Returns: (trained_model, metrics_dict)
    metrics_dict keys: 'train_loss', 'val_loss', 'val_rho', 'param_count', 'input_dim'
    """
    # 1. load_cifar_flat(cfg) → train_loader, val_loader, test_loader, input_dim
    # 2. grid_search_architecture(input_dim, cfg.hidden_dims_candidates, ...) → encoder, hidden_dims, n_params
    # 3. model = FlatMLPWithHead(encoder)
    # 4. train with AdamW + CosineAnnealingLR (cfg.epochs=150, cfg.lr=1e-3, cfg.weight_decay=1e-4)
    # 5. save checkpoint: cfg.results_dir / "best_flat_mlp_cifar.pt"
    ...


def train_nfn_cifar(
    cfg,
    device: torch.device,
) -> Tuple["NFNWithHead", Dict]:
    """Train NFN fresh on CIFAR-10. Reconstructs NFNWithHead with CIFAR weight_shapes.
    Returns: (trained_model, metrics_dict)
    """
    # 1. load_cifar_nfn(cfg) → train_loader, val_loader, test_loader, weight_shapes
    # 2. NFNEncoder(weight_shapes, channel_dim=112, embed_dim=128, n_layers=3)
    # 3. NFNWithHead(encoder)
    # 4. train with AdamW + CosineAnnealingLR
    # 5. save: cfg.results_dir / "best_nfn_cifar.pt"  (keys: encoder_state, head_state)
    ...


def train_deep_sets_cifar(
    cfg,
    device: torch.device,
) -> Tuple["DeepSetsWithHead", Dict]:
    """Train DeepSets fresh on CIFAR-10. Grid search phi_hidden for CIFAR element_dim.
    Returns: (trained_model, metrics_dict)
    """
    # 1. load_cifar_flat(cfg) → train_loader, val_loader, test_loader, input_dim
    # 2. Determine element_dim and N_layers from CIFAR weight_shapes
    # 3. grid_search_deep_sets(element_dim, cfg.phi_hidden_candidates, ...) → encoder, phi_hidden, n_params
    # 4. train with AdamW + CosineAnnealingLR; elements prepared via prepare_flat_elements
    # 5. save: cfg.results_dir / "best_deep_sets_cifar.pt"
    ...


def train_deep_sets(
    model: "DeepSetsWithHead",
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg,
    device: torch.device,
    checkpoint_name: str,
    weight_shapes: List[tuple],
) -> Tuple["DeepSetsWithHead", Dict]:
    """Core training loop for DeepSetsWithHead (MNIST-CNN or CIFAR-10).
    AdamW + CosineAnnealingLR, MSE loss, saves best-val-loss checkpoint.
    Returns: (trained_model, history_dict)
    """
    ...


def prepare_flat_elements(
    flat_w: torch.Tensor,       # (D,) or (B, D)
    weight_shapes: List[tuple],
) -> torch.Tensor:
    """Reshape flat weight vector into padded element tensor for DeepSets.
    Each layer becomes one element, padded to uniform element_dim = max(prod(shape)).
    Returns: (N_layers, element_dim) for single sample, caller stacks to (B, N, element_dim).
    """
    ...
```

### Tensor Shapes (prepare_flat_elements)

| Variable | Shape | Note |
|----------|-------|------|
| flat_w | (D,) | full flattened weight vector |
| per_layer chunks | List[(n_i,)] | split by prod(shape_i) |
| element_dim | max(n_i) | padding target |
| output | (N_layers, element_dim) | zero-padded per layer |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | train_flat_mlp_cifar | load CIFAR flat data, grid search, train, save checkpoint |
| L-5-2 | train_nfn_cifar | load CIFAR NFN data, reconstruct with CIFAR weight_shapes, train |
| L-5-3 | train_deep_sets_cifar | load CIFAR flat data, grid search element_dim, train DeepSets |
| L-5-4 | get_weight_shapes + prepare_flat_elements | shape extraction and element padding for CIFAR |

---

## A-6: Evaluation & Bootstrap CI [Complexity: 15, Budget: 4 subtasks]

Applied: Paired bootstrap resampling pattern for correlated metric CI

### API Signatures

```python
def bootstrap_spearman_ci(
    y_true: np.ndarray,     # (N,)
    y_pred: np.ndarray,     # (N,)
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
    """Inference on WeightDataset batches: (flat_w, acc).
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float,
              'preds': np.ndarray, 'labels': np.ndarray}
    """
    ...


def evaluate_deep_sets_encoder(
    model: "DeepSetsWithHead",
    loader: DataLoader,
    device: torch.device,
    weight_shapes: List[tuple],
    n_resamples: int = 1000,
) -> Dict:
    """Inference on WeightDataset batches: (flat_w, acc); reshape via prepare_flat_elements.
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float,
              'preds': np.ndarray, 'labels': np.ndarray}
    """
    ...


def evaluate_nfn_encoder(
    model: "NFNWithHead",
    loader: DataLoader,
    device: torch.device,
    n_resamples: int = 1000,
) -> Dict:
    """Inference on NFNWeightDataset batches: (weight_list, flat_w, acc).
    Returns: {'rho': float, 'ci_lower': float, 'ci_upper': float,
              'preds': np.ndarray, 'labels': np.ndarray}
    """
    ...


def compute_delta_rho_ci(
    nfn_preds: np.ndarray,      # (N,)
    flat_preds: np.ndarray,     # (N,)
    labels: np.ndarray,         # (N,)
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Paired bootstrap CI for Δρ = ρ(NFN) − ρ(flat).
    Resamples (nfn_pred_i, flat_pred_i, label_i) triples together.
    Returns: (delta_rho, ci_lower_2.5pct, ci_upper_97.5pct)
    """
    ...


def compute_tier_analysis(
    flat_preds: np.ndarray,     # (N,)
    nfn_preds: np.ndarray,      # (N,)
    deep_sets_preds: np.ndarray,# (N,)
    labels: np.ndarray,         # (N,)
) -> Dict:
    """Tercile partition of test set by label accuracy; compute Δρ(NFN vs flat) per tier.
    Returns: {'low': float, 'mid': float, 'high': float,
              'low_n': int, 'mid_n': int, 'high_n': int}
    """
    ...
```

### Pseudo-code (bootstrap_spearman_ci)

```
rng = np.random.default_rng(seed)
n = len(y_true)
boot_rhos = []
for _ in range(n_resamples):
    idx = rng.integers(0, n, n)
    rho = spearmanr(y_true[idx], y_pred[idx]).statistic
    boot_rhos.append(rho)
return median(boot_rhos), percentile(boot_rhos, 2.5), percentile(boot_rhos, 97.5)
```

### Pseudo-code (compute_delta_rho_ci)

```
rng = np.random.default_rng(seed)
n = len(labels)
boot_deltas = []
for _ in range(n_resamples):
    idx = rng.integers(0, n, n)           # same idx for all three arrays (paired)
    rho_nfn  = spearmanr(labels[idx], nfn_preds[idx]).statistic
    rho_flat = spearmanr(labels[idx], flat_preds[idx]).statistic
    boot_deltas.append(rho_nfn - rho_flat)
delta_rho = spearmanr(labels, nfn_preds).statistic - spearmanr(labels, flat_preds).statistic
return delta_rho, percentile(boot_deltas, 2.5), percentile(boot_deltas, 97.5)
```

### Pseudo-code (compute_tier_analysis)

```
thresholds = np.percentile(labels, [33.3, 66.7])
low_mask  = labels <= thresholds[0]
mid_mask  = (labels > thresholds[0]) & (labels <= thresholds[1])
high_mask = labels > thresholds[1]
for tier, mask in [('low', low_mask), ('mid', mid_mask), ('high', high_mask)]:
    delta = spearmanr(labels[mask], nfn_preds[mask]).statistic
             - spearmanr(labels[mask], flat_preds[mask]).statistic
    result[tier] = delta
    result[f'{tier}_n'] = mask.sum()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | bootstrap_spearman_ci | numpy rng loop, median + percentile CI |
| L-6-2 | evaluate_flat/deep_sets/nfn_encoder | per-encoder inference + CI computation |
| L-6-3 | compute_delta_rho_ci | paired bootstrap Δρ with shared idx |
| L-6-4 | compute_tier_analysis | tercile split by label, Δρ per tier |
