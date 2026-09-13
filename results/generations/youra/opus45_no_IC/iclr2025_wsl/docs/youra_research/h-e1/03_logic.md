# Logic: H-E1 (EXISTENCE / PoC)

**Hypothesis:** NFN R² > MLP-Matched R² + 0.05 at N=1K

Applied: PyTorch standard Dataset/DataLoader + AdamW/CosineAnnealingLR training loop pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs (H-E1 is foundation hypothesis, no prior code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1/A-2/A-3/A-4: Data + Model + Baseline + Training [Complexity: 36, Budget: 2 subtasks]

**Applied**: torch.utils.data.Dataset/DataLoader pattern; AdamW + CosineAnnealingLR

### API Signatures

```python
# data.py
def download_model_zoo(dest_dir: str) -> str: ...
def load_models(zoo_dir: str, n: int) -> list[dict]:  # each: {"state_dict":..., "label": float}
def filter_homogeneous(models: list[dict]) -> list[dict]: ...
def normalize_weights(models: list[dict]) -> list[dict]:  # per-layer zero mean/unit var
def split_train_test(models: list[dict], train_frac: float, seed: int) -> tuple[list, list]: ...

class WeightSpaceDataset(torch.utils.data.Dataset):
    def __init__(self, models: list[dict]): ...
    def __getitem__(self, idx: int) -> tuple[dict, float]: ...  # (state_dict, label)
    def __len__(self) -> int: ...

def make_collate_fn(network_spec) -> Callable[[list[tuple[dict, float]]], tuple["WeightSpaceFeatures", Tensor]]:
    # builds WeightSpaceFeatures via nfn.common.state_dict_to_tensors, stacks labels -> (B,)


# model.py
class NFNRegressor(nn.Module):
    def __init__(self, network_spec, nfn_channels: int = 32): ...
    def forward(self, wsfeat: "WeightSpaceFeatures") -> Tensor: ...  # -> (B, 1)

class MLPMatched(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor: ...  # (B, D) -> (B, 1)

def flatten_weights(wsfeat: "WeightSpaceFeatures") -> Tensor:  # concat all weights/biases -> (B, D)
def count_params(model: nn.Module) -> int: ...
def match_mlp_dim(nfn_param_count: int, hidden_dim: int, num_layers: int) -> int:  # binary/linear search over input_dim


# train.py
def set_seed(seed: int) -> None: ...
def build_optimizer(model: nn.Module, cfg: "Config") -> torch.optim.AdamW: ...
def build_scheduler(optimizer, cfg: "Config") -> torch.optim.lr_scheduler.CosineAnnealingLR: ...

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    cfg: "Config",
    model_kind: Literal["nfn", "mlp"],
) -> dict:  # {"train_loss": list[float], "val_loss": list[float]}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| wsfeat (NFN input) | per-layer weight/bias tensors, batched dim B | from `state_dict_to_tensors` |
| flatten_weights output | (B, D) | D = total concatenated weight+bias count |
| NFNRegressor output | (B, 1) | regression logit |
| MLPMatched output | (B, 1) | regression logit |
| labels | (B,) | accuracy targets, 0-1 range |

### Pseudo-code: NFN Forward (FR-2.2 architecture)

```
1. h = NPLinear(wsfeat, nfn_channels)      # equivariant, channels=32
2. h = ReLU(h)
3. h = NPLinear(h, nfn_channels)
4. h = ReLU(h)
5. pooled = HNPPool(h)                     # invariant pooling -> (B, C)
6. out = Linear(pooled, 1)                 # -> (B, 1)
```

### Pseudo-code: MLP-Matched dim search (FR-3.1)

```
def match_mlp_dim(nfn_param_count, hidden_dim, num_layers):
    for input_dim in increasing candidates:
        mlp = build MLP(input_dim, hidden_dim, num_layers)
        if count_params(mlp) >= nfn_param_count:
            return input_dim
    # fallback: use actual flattened weight dim D (may exceed match)
```

### Pseudo-code: train_model loop

```
optimizer = build_optimizer(model, cfg)
scheduler = build_scheduler(optimizer, cfg)  # T_max=cfg.epochs, eta_min=1e-6
loss_fn = MSELoss()
for epoch in range(cfg.epochs):
    model.train()
    for batch, labels in train_loader:
        x = flatten_weights(batch) if model_kind == "mlp" else batch
        pred = model(x).squeeze(-1)        # (B,)
        loss = loss_fn(pred, labels)
        backward + optimizer.step(); optimizer.zero_grad()
    scheduler.step()
    val_loss = eval MSE on test_loader (no grad)
    record train_loss, val_loss
return {"train_loss": [...], "val_loss": [...]}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A-1 | Data + Model APIs | data.py (download/filter/normalize/split/Dataset/collate) + model.py (NFNRegressor, MLPMatched, flatten_weights, count_params, match_mlp_dim) |
| L-A-2 | Training loop | train.py (set_seed, build_optimizer, build_scheduler, train_model for both model_kind branches) |

---

## Evaluation & Visualization (A-5/A-6/A-7) — Reference Only (already fully specified in architecture, no additional logic needed)

```python
# evaluate.py
def compute_r2(model: nn.Module, loader: DataLoader, model_kind: str) -> tuple[np.ndarray, np.ndarray, float]:
    # preds: (N,), targets: (N,), r2: float

def compare_models(nfn_result: tuple, mlp_result: tuple) -> dict:
    # {"nfn_r2": float, "mlp_r2": float, "difference": float, "hypothesis_supported": bool}
    # hypothesis_supported = (nfn_r2 - mlp_r2) > 0.05

def plot_r2_comparison(nfn_r2: float, mlp_r2: float, threshold: float, out_path: str) -> None: ...
def plot_scatter(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None: ...
def plot_residuals(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None: ...
def plot_learning_curves(history: dict, title: str, out_path: str) -> None: ...
def save_results_json(results: dict, out_path: str) -> None: ...
```

No subtasks allocated to evaluate.py — signatures unchanged from architecture (low complexity, straightforward sklearn/matplotlib usage).
