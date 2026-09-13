# Logic Design: H-M1 (NFN Equivariant Feature Extraction)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no base_hypothesis code, no existing src/)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation using official `nfn` PyPI package

---

## A-1: Data Pipeline [Complexity: Medium, Budget: 3]

**Applied**: Standard PyTorch Dataset/DataLoader + `nfn.common.state_dict_to_tensors`

### API Signatures

```python
class ModelZooDataset(Dataset):
    def __init__(self, checkpoint_dir: str, accuracy_csv: str, indices: List[int]):
        """Load state_dict paths + accuracy labels for given indices."""
        ...

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> Tuple[dict, float]:
        """Returns (state_dict, accuracy). state_dict: raw torch state_dict."""
        ...


def nfn_collate_fn(
    batch: List[Tuple[dict, float]]
) -> Tuple[WeightSpaceFeatures, Tensor]:
    """Convert batch of state_dicts -> batched WeightSpaceFeatures + labels [B]."""
    ...


def download_model_zoo(zenodo_record: str = "6620869", dest_dir: str = "./model_zoo") -> None:
    """Download + extract Zenodo checkpoints (idempotent, skip if dest_dir exists)."""
    ...
```

### Pseudo-code (collate)

```
1. state_dicts, accs = zip(*batch)                       # tuples
2. wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]  # per-model (weights, biases)
3. wsfeat = WeightSpaceFeatures(*default_collate(wts_and_bs))      # stacks along batch dim
4. y = torch.tensor(accs, dtype=torch.float32)            # [B]
5. return wsfeat, y
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict tensors | varies per layer | e.g. conv weight [C_out, C_in, k, k] |
| wsfeat (batched) | weights: L × [B, C_out, C_in, k, k], biases: L × [B, C_out] | L = num ResNet-20 layers |
| y | [B] | accuracy 0-100 |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | download_model_zoo | Zenodo fetch + unzip, cache to disk |
| L-1-2 | ModelZooDataset | Lazy-load state_dicts via torch.load per __getitem__ |
| L-1-3 | nfn_collate_fn | Batch collation into WeightSpaceFeatures |

---

## A-2: Baseline Model (Statistics Ridge) [Complexity: Low, Budget: 1]

**Applied**: Reuse H-E1 feature extraction (sklearn RidgeCV)

### API Signatures

```python
def extract_stats_features(state_dict: dict) -> np.ndarray:
    """9 layers x 7 stats (mean,std,min,max,median,skew,kurtosis) -> [63]"""
    ...

def train_baseline(X_train: np.ndarray, y_train: np.ndarray) -> RidgeCV:
    """X_train: [N, 63], y_train: [N]. Returns fitted RidgeCV."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | extract_stats_features + train_baseline | Reuse from H-E1, no changes |

---

## A-3: NFNAccuracyPredictor [Complexity: High, Budget: 5]

**Applied**: Official `nfn` library (`AllanYangZhou/nfn`, NeurIPS 2023) — `NFNBuilder`, `WeightSpaceFeatures`

### API Signatures

```python
from nfn import NFNBuilder, WeightSpaceFeatures
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

class NFNAccuracyPredictor(nn.Module):
    def __init__(
        self,
        network_spec: "NetworkSpec",
        hidden_dim: int = 128,
        num_layers: int = 3,
        invariant_output: bool = True,
    ):
        """NFN backbone (equivariant NF-layers) + linear regression head."""
        super().__init__()
        self.nfn = NFNBuilder(
            network_spec=network_spec,
            hidden_channels=hidden_dim,
            num_layers=num_layers,
            invariant_output=invariant_output,
        ).build()
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, weight_features: WeightSpaceFeatures) -> Tensor:
        """weight_features -> [B] predicted accuracy."""
        invariant_repr = self.nfn(weight_features)   # [B, hidden_dim]
        return self.head(invariant_repr).squeeze(-1)  # [B]
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight_features | WeightSpaceFeatures (per-layer weights/biases, batched) | see A-1 table |
| invariant_repr | [B, hidden_dim] | pooled, permutation-invariant |
| output | [B] | predicted accuracy |

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | NFNAccuracyPredictor | Wraps NFNBuilder + Linear head, build network_spec once from sample state_dict via `network_spec_from_wsfeat` |

---

## A-4: Equivariance Verification [Complexity: Medium, Budget: 2]

**Applied**: Permutation symmetry test per NFN paper (Sec. 3)

### API Signatures

```python
def sample_neuron_permutation(network_spec: "NetworkSpec", seed: int) -> Dict[str, Tensor]:
    """Random permutation per hidden layer (input/output dims fixed). Returns {layer_name: perm_idx}."""
    ...

def apply_permutation(
    wsfeat: WeightSpaceFeatures, permutation: Dict[str, Tensor]
) -> WeightSpaceFeatures:
    """Permute rows/cols of weights & biases consistently across adjacent layers."""
    ...

def verify_equivariance(
    nfn: nn.Module,
    wsfeat: WeightSpaceFeatures,
    permutation: Dict[str, Tensor],
    atol: float = 1e-5,
) -> Tuple[bool, float]:
    """Returns (passed, max_abs_diff)."""
    ...
```

### Pseudo-code

```
1. original_out = nfn(wsfeat)                       # [B, hidden_dim] (invariant repr, pre-head)
2. permuted_wsfeat = apply_permutation(wsfeat, permutation)
3. permuted_out = nfn(permuted_wsfeat)
4. diff = (original_out - permuted_out).abs().max()
5. return diff < atol, diff.item()
```

Note: test on `nfn` output directly (invariant_repr), not `head()` output — invariance is the NFN mechanism, head is just linear readout (equivariance holds through it too but not the property under test).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | sample_neuron_permutation + apply_permutation | Per-layer perm respecting ResNet-20 layer connectivity |
| L-4-2 | verify_equivariance | Runs on all 500 test models, aggregates pass rate + max error |

---

## A-5: Training Loop [Complexity: Medium, Budget: 3]

**Applied**: Standard PyTorch train/eval loop with ReduceLROnPlateau + early stopping

### API Signatures

```python
def train_nfn(
    model: NFNAccuracyPredictor,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = 100,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    patience: int = 20,
    device: str = "cuda",
) -> Dict[str, List[float]]:
    """Returns history: {train_loss, val_loss, val_r2} per epoch."""
    ...

def evaluate(model: nn.Module, loader: DataLoader, device: str) -> Dict[str, float]:
    """Returns {r2, mae}."""
    ...
```

### Pseudo-code (train_nfn)

```
optimizer = Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
scheduler = ReduceLROnPlateau(optimizer, factor=0.5, patience=10)
best_val_loss, epochs_no_improve = inf, 0

for epoch in range(epochs):
    model.train()
    for wsfeat, y in train_loader:
        wsfeat, y = wsfeat.to(device), y.to(device)
        pred = model(wsfeat)              # [B]
        loss = mse_loss(pred, y)
        loss.backward(); optimizer.step(); optimizer.zero_grad()
        assert not torch.isnan(loss)      # NaN/explosion guard (P0 criterion)

    val_metrics = evaluate(model, val_loader, device)
    scheduler.step(val_metrics["mae"])    # or val MSE

    if val_metrics["loss"] < best_val_loss:
        best_val_loss, epochs_no_improve = val_metrics["loss"], 0
        save_checkpoint(model)
    else:
        epochs_no_improve += 1
    if epochs_no_improve >= patience:
        break  # early stopping

return history
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | train_nfn | Main loop, early stopping, checkpoint best |
| L-5-2 | evaluate | R²/MAE via sklearn.metrics on collected preds |
| L-5-3 | run_seeds | Repeat train+eval+equivariance for 3 seeds, aggregate |

---

## A-6: Visualization [Complexity: Low, Budget: 2]

### API Signatures

```python
def plot_gate_metrics(nfn_r2: float, baseline_r2: float, save_path: str) -> None: ...
def plot_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray, r2: float, save_path: str) -> None: ...
def plot_equivariance_check(original_out: Tensor, permuted_out: Tensor, save_path: str) -> None: ...
def plot_training_curves(history: dict, save_path: str) -> None: ...
def plot_residuals(y_true: np.ndarray, y_pred: np.ndarray, save_path: str) -> None: ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | plot_gate_metrics + plot_prediction_scatter | Mandatory gate figure + scatter |
| L-6-2 | plot_equivariance_check + plot_training_curves + plot_residuals | Remaining LLM-autonomous figures |

---

## External Dependencies (Official NFN Library)

```python
# pip install nfn
from nfn import NFNBuilder, WeightSpaceFeatures
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

# NFNBuilder(network_spec, hidden_channels, num_layers, invariant_output=True).build()
#   -> nn.Module: forward(WeightSpaceFeatures) -> Tensor [B, hidden_channels]
```

**Verified from**: package README/example usage in `02c_experiment_brief.md` (official repo `AllanYangZhou/nfn`, not locally installed — install and confirm exact signature of `NFNBuilder`/`network_spec_from_wsfeat` at Phase 4 implementation time; fall back to `examples/basic_cnn/` in repo if signature differs).
