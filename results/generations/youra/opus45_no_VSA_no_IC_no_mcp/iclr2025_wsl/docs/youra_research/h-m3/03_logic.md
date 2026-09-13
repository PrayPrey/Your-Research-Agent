# Logic: h-m3 (MECHANISM)

Applied: factorial-interaction-design-pattern (2 tasks x 3 archs x 3 seeds, two-way ANOVA)
Applied: injectable-loss-function-training-loop-pattern (single train_task loop parameterized by loss_fn, shared across BCE/MSE)
Applied: shared-model-shared-metrics-pattern (num_classes=1 reused for both binary logit and scalar regression output)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code (Serena MCP unavailable; read `models.py`/`data.py` directly).
**Analyzed Path**: `docs/youra_research/h-m1/code/models.py`, `docs/youra_research/h-m1/code/data.py`
**Relevant Symbols**: `FlattenedMLP.__init__/forward`, `DWSModel.__init__/forward`, `NFTModel.__init__/forward`, `normalize_weights`, `collate_fn`

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/models.py (ACTUAL CODE, copy unchanged into h-m3/code/)
class FlattenedMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int] = None, num_classes: int = 10, dropout: float = 0.1): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]

class DWSModel(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], hidden: int = 128, num_classes: int = 10): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]

class NFTModel(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], d_model: int = 128, nhead: int = 4,
                 num_layers: int = 2, num_classes: int = 10): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]

# From: h-m1/code/data.py (ACTUAL CODE, only these two helpers reused)
def normalize_weights(weight_list: List[Tensor]) -> List[Tensor]: ...   # per-tensor z-score
def collate_fn(batch) -> Tuple[List[Tensor], Tensor]: ...
    # batch: List[(weight_list, label)] -> (List[Tensor[B,in,out]] per layer, labels[B])
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, read directly)

**Deviation**: all 3 models take `num_classes=10` by default in h-m1; h-m3 always instantiates with `num_classes=1` — no source change, just the constructor kwarg. `weight_list[i]` shape is `[in_c, out_c]` per-sample (`[B, in_c, out_c]` after `collate_fn`) — matches `weight_shapes: List[Tuple[int,int]]`.

---

## M-1/M-2: Port base models + Config [Complexity: 5+6, Budget: 3 total]

**Applied**: shared-model-shared-metrics-pattern

### API Signatures

```python
# config.py — no deps
@dataclass
class ExperimentConfig:
    tasks: list = field(default_factory=lambda: ["backdoor", "accuracy"])
    architectures: list = field(default_factory=lambda: ["mlp", "dws", "nft"])
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    n_train: int = 600
    n_test: int = 200
    epochs: int = 100
    lr: float = 1e-4
    batch_size: int = 32
    hidden_dim: int = 128
    weight_shapes: list = None          # List[Tuple[int,int]], set from synth_data.default_weight_shapes
    results_path: str = "h-m3/code/outputs/results.json"
    fig_dir: str = "h-m3/figures"

@dataclass
class ExperimentResult:
    task: str
    architecture: str
    seed: int
    metric_value: float          # AUC (backdoor) or RMSE (accuracy)
    secondary_metric: float = None  # R2, accuracy task only
    train_time: float = 0.0
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-1 | Port models.py | Copy `FlattenedMLP`/`DWSModel`/`NFTModel` from h-m1 unchanged, verify `num_classes=1` forward on dummy weight_list |
| L-M1-2 | Port data helpers | Copy `normalize_weights`, `collate_fn` from h-m1/code/data.py into h-m3/code/synth_data.py |
| L-M2-1 | Config + param-count matching | `ExperimentConfig`/`ExperimentResult` dataclasses; `default_weight_shapes(hidden_dim, n_layers) -> List[Tuple[int,int]]`; tune `hidden_dim`(DWS)/`d_model`(NFT) so param counts land within 10% of MLP baseline |

---

## M-3/M-4: Synthetic datasets [Complexity: 8+7, Budget: 3 total]

**Applied**: factorial-interaction-design-pattern (structural signal isolation: local vs global)

### API Signatures

```python
# synth_data.py — deps: torch
def default_weight_shapes(hidden_dim: int = 128, n_layers: int = 4) -> List[Tuple[int, int]]: ...

def make_backdoor_dataset(n: int, weight_shapes: List[Tuple[int, int]], seed: int) -> Tuple[List[List[Tensor]], List[int]]:
    """label=1 (50%): inject localized perturbation into one random (layer, row-slice) of one weight tensor."""
    ...

def make_accuracy_dataset(n: int, weight_shapes: List[Tuple[int, int]], seed: int) -> Tuple[List[List[Tensor]], List[float]]:
    """target = sigmoid(a * mean(all-layer norms) + b * mean(all-layer means)) * 100 + gaussian noise."""
    ...

def build_dataloader(weight_lists: List[List[Tensor]], labels: List, batch_size: int, shuffle: bool) -> DataLoader:
    """Wraps (weight_lists, labels) in a list-backed Dataset; uses collate_fn from data.py."""
    ...
```

### Pseudo-code

```
make_backdoor_dataset(n, weight_shapes, seed):
  rng = Generator(seed)
  for i in range(n):
    weights = [randn(in_c, out_c) for (in_c, out_c) in weight_shapes]  # [in_c, out_c] each
    label = i % 2
    if label == 1:
      layer_idx = rng.randint(len(weight_shapes))
      row = rng.randint(weight_shapes[layer_idx][0])
      weights[layer_idx][row, :] += 5.0 * randn_like(weights[layer_idx][row, :])  # localized spike
    weight_lists.append(normalize_weights(weights)); labels.append(label)
  shuffle(weight_lists, labels, seed)
  return weight_lists, labels

make_accuracy_dataset(n, weight_shapes, seed):
  for i in range(n):
    weights = [randn(in_c, out_c) * scale_i for (in_c,out_c) in weight_shapes]  # scale_i varies per sample
    global_norm = mean([w.norm() for w in weights])
    global_mean = mean([w.mean() for w in weights])
    target = sigmoid(0.3*global_norm + 0.1*global_mean) * 100 + N(0, 2.0)  # global-stat signal + noise
    weight_lists.append(normalize_weights(weights)); targets.append(target)
  return weight_lists, targets
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight_lists[i][l] | [in_c_l, out_c_l] | per-sample, per-layer, pre-collate |
| batched_weights[l] | [B, in_c_l, out_c_l] | post `collate_fn` |
| labels (backdoor) | [B] int64 | 0/1 |
| labels (accuracy) | [B] float32 | 0-100 |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | Backdoor generator | `make_backdoor_dataset` with balanced labels + localized row-slice perturbation |
| L-M4-1 | Accuracy generator | `make_accuracy_dataset` with global-norm/mean-driven continuous target + gaussian noise |
| L-M34-1 | Dataloader wrapper | `build_dataloader` using `collate_fn` from ported data helpers |

---

## M-5/M-6: Training loop + metrics [Complexity: 8+9, Budget: 3 total]

**Applied**: injectable-loss-function-training-loop-pattern

### API Signatures

```python
# train_task.py — deps: torch, models.py
def build_model(architecture: str, weight_shapes: List[Tuple[int,int]], hidden_dim: int, num_classes: int = 1) -> nn.Module:
    """dispatch: "mlp"->FlattenedMLP(input_dim=sum(in*out)), "dws"->DWSModel, "nft"->NFTModel."""
    ...

def train_task(model: nn.Module, train_loader: DataLoader, cfg: ExperimentConfig, loss_fn: nn.Module) -> Tuple[nn.Module, dict]:
    """AdamW(lr=cfg.lr) + CosineAnnealingLR(T_max=cfg.epochs), runs cfg.epochs. Returns (model, history={epoch: avg_loss})."""
    ...

def predict(model: nn.Module, loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
    """model.eval(); returns (preds.squeeze(-1), labels) as numpy, preds are raw logits/regression outputs."""
    ...

# metrics.py — deps: sklearn.metrics, scipy.stats, numpy
def compute_auc(preds: np.ndarray, labels: np.ndarray) -> float: ...          # roc_auc_score(labels, sigmoid(preds))
def compute_rmse_r2(preds: np.ndarray, targets: np.ndarray) -> Tuple[float, float]: ...  # sqrt(MSE), r2_score
def run_interaction_anova(results: List[ExperimentResult]) -> dict: ...
    # two-way ANOVA (task x architecture) on z-normalized metric_value -> {f_stat, p_value, significant}
def check_success_criteria(stats: dict) -> Dict[str, bool]: ...
    # {"dws_beats_nft_backdoor":.., "nft_beats_dws_accuracy":.., "equivariant_beats_mlp":.., "interaction_significant":..}
```

### Pseudo-code

```
train_task(model, loader, cfg, loss_fn):
  opt = AdamW(model.parameters(), lr=cfg.lr)
  sched = CosineAnnealingLR(opt, T_max=cfg.epochs)
  for epoch in range(cfg.epochs):
    for weight_list, labels in loader:
      preds = model(weight_list).squeeze(-1)          # [B]
      loss = loss_fn(preds, labels.float())
      loss.backward(); opt.step(); opt.zero_grad()
    sched.step()
    history[epoch] = avg_loss
  return model, history
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M5-1 | build_model dispatch | Instantiate MLP/DWS/NFT with `num_classes=1`, tune dim for param parity |
| L-M5-2 | train_task + predict | Injectable-loss training loop (AdamW+cosine) shared by BCE and MSE tasks |
| L-M6-1 | Metrics + ANOVA | `compute_auc`, `compute_rmse_r2`, `run_interaction_anova`, `check_success_criteria` |

---

## M-7/M-8/M-9: Sweep + visualization + orchestration [Complexity: 11+9+5, Budget: 3 total]

**Applied**: factorial-interaction-design-pattern

### API Signatures

```python
# run_sweep.py — deps: synth_data, train_task, metrics, config
def run_single(task: str, architecture: str, seed: int, cfg: ExperimentConfig) -> ExperimentResult: ...
def run_sweep(cfg: ExperimentConfig) -> List[ExperimentResult]: ...   # 2 tasks x 3 archs x 3 seeds = 18 runs

# visualize.py — deps: metrics, matplotlib
def plot_gate_2x2_bar(stats: dict, out_path: str) -> None: ...
def plot_interaction(stats: dict, out_path: str) -> None: ...
def plot_training_curves(histories: dict, out_path: str) -> None: ...
def plot_diff_heatmap(stats: dict, baseline: str, out_path: str) -> None: ...

# main.py
def main() -> None: ...
    # cfg -> run_sweep -> aggregate(mean/std per task,arch) -> run_interaction_anova ->
    # check_success_criteria -> visualize(4 figs) -> save results.json
```

### Pseudo-code

```
run_single(task, architecture, seed, cfg):
  set_seed(seed)
  if task == "backdoor":
    train_w, train_y = make_backdoor_dataset(cfg.n_train, cfg.weight_shapes, seed)
    test_w, test_y = make_backdoor_dataset(cfg.n_test, cfg.weight_shapes, seed + 1000)
    loss_fn = BCEWithLogitsLoss()
  else:
    train_w, train_y = make_accuracy_dataset(cfg.n_train, cfg.weight_shapes, seed)
    test_w, test_y = make_accuracy_dataset(cfg.n_test, cfg.weight_shapes, seed + 1000)
    loss_fn = MSELoss()
  model = build_model(architecture, cfg.weight_shapes, cfg.hidden_dim)
  train_loader = build_dataloader(train_w, train_y, cfg.batch_size, shuffle=True)
  test_loader = build_dataloader(test_w, test_y, cfg.batch_size, shuffle=False)
  model, history = train_task(model, train_loader, cfg, loss_fn)
  preds, labels = predict(model, test_loader)
  if task == "backdoor":
    metric, secondary = compute_auc(preds, labels), None
  else:
    metric, secondary = compute_rmse_r2(preds, labels)
  return ExperimentResult(task, architecture, seed, metric, secondary, train_time), history
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M7-1 | run_single/run_sweep | 18-run loop over (task x arch x seed), param-count pre-check before sweep starts |
| L-M8-1 | Visualization suite | 4 required figures (2x2 bar, interaction, training curves, diff heatmap) |
| L-M9-1 | main.py + results.json | Wire sweep->aggregate->anova->criteria->visualize->save, PASS/FAIL per criterion |
