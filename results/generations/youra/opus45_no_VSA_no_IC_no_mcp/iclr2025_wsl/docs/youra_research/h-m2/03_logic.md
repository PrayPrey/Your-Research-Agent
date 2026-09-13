# Logic: h-m2 (MECHANISM)

Applied: sample-efficiency-curve-pattern (subsample train set, retrain from scratch, eval on fixed test set)
Applied: one-vs-rest-macro-auc-pattern (sklearn `roc_auc_score(multi_class='ovr')` on softmax probs for multiclass ROC-AUC)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code (Serena MCP unavailable; `Read` used directly on `h-m1/code/*.py` — files small and fully readable).
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `FlattenedMLP.forward`, `DWSModel.forward`, `NFTModel.forward`, `train_model_tracked`, `get_dataloaders`, `get_weight_shapes`, `MNISTINRDataset`, `collate_fn`, `Config` (all read from actual `.py` files).

**Key finding vs PRD**: h-m1 pipeline is 10-class MNIST-INR classification (`CrossEntropyLoss`, `weight_list: List[Tensor]` → `[B, 10]` logits), not TrojAI binary backdoor detection. No TrojAI loader exists. Per architecture decision, "ROC-AUC" is redefined as one-vs-rest macro-AUC over 10-class softmax probs; TrojAI download (FR-1) is out of scope for this budget.

---

## External Dependencies API (From Actual h-m1 Code)

```python
# From: h-m1/code/models.py (ACTUAL CODE) — copy into h-m2/code/, unchanged
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

# From: h-m1/code/data.py (ACTUAL CODE) — copy into h-m2/code/, unchanged
class MNISTINRDataset(Dataset):
    def __init__(self, data_dir: str): ...
    def __getitem__(self, idx: int) -> Tuple[List[Tensor], int]: ...  # normalized weight_list, label

def collate_fn(batch) -> Tuple[List[Tensor], Tensor]: ...  # weight_list[i]: [B, in_c, out_c]; labels: [B]
def get_dataloaders(cfg: Config) -> Tuple[DataLoader, DataLoader]: ...  # fixed seeded 80/20 split
def get_weight_shapes(cfg: Config) -> List[Tuple[int, int]]: ...

# From: h-m1/code/train_tracked.py (ACTUAL CODE) — copy into h-m2/code/, reused as-is
def train_model_tracked(
    model: nn.Module,
    model_type: str,          # 'mlp' | 'dws' | 'nft'
    train_loader: DataLoader,
    cfg: Config,
    sample_input: List[Tensor] = None,
) -> Tuple[nn.Module, TrainingDynamicsTracker]: ...  # tracker output discarded by h-m2

# From: h-m1/code/config.py (ACTUAL CODE) — copy, h-m2 adds `fractions` field
@dataclass
class Config:
    data_dir: str; batch_size: int = 64; num_workers: int = 2; train_split: float = 0.8
    d_model: int = 128; nhead: int = 4; num_layers: int = 2
    dws_hidden: int = 128; mlp_hidden: List[int]; dropout: float = 0.1; num_classes: int = 10
    lr: float = 1e-4; weight_decay: float = 1e-2; epochs: int = 30; cosine_t_max: int = 30
    device: str = "cuda"; seed: int = 42
    results_path: str; fig_dir: str
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, read directly). No parameter-name mismatches found vs h-m1's `03_logic.md`.

**Note**: `train_model_tracked` uses `CrossEntropyLoss` (multiclass), not the PRD's `BCEWithLogitsLoss` (binary) — consistent with the 10-class task; h-m2 keeps CE loss unchanged.

---

## S-2+S-3+S-4: Subsampling + Metrics + Success Criteria [Complexity: 6+7+5, Budget: 1 subtask]

**Applied**: deterministic-fraction-subsampling (per-seed `torch.Generator` for reproducible subsets)

### API Signatures

```python
# data.py additions (MNISTINRDataset, normalize_weights, collate_fn, get_dataloaders, get_weight_shapes reused unchanged)
def subsample_train(train_ds: Dataset, fraction: float, seed: int) -> Subset:
    """Deterministic random subset of size round(len(train_ds) * fraction), seeded by `seed`."""
    ...

def get_fraction_loader(train_ds: Dataset, fraction: float, seed: int, cfg: Config) -> DataLoader:
    """subsample_train then wrap in DataLoader(shuffle=True, collate_fn=collate_fn, batch_size=cfg.batch_size)."""
    ...

# metrics.py
def macro_auc_ovr(y_true: np.ndarray, probs: np.ndarray) -> float:
    """sklearn.metrics.roc_auc_score(y_true, probs, multi_class='ovr', average='macro')."""
    ...

def gap_closure(dws_aucs: dict[float, float], nft_aucs: dict[float, float]) -> dict[float, float]:
    """{fraction: dws_aucs[fraction] - nft_aucs[fraction] for fraction in dws_aucs}."""
    ...

def aggregate_stats(results: dict) -> dict:
    """results: {fraction: {model_type: [per-seed {'auc': float, 'train_time': float}, ...]}}
    Returns {fraction: {model_type: {'auc_mean': float, 'auc_std': float, 'time_mean': float}}}."""
    ...

def check_success_criteria(stats: dict, cfg: Config) -> dict[str, bool]:
    """Returns {'dws_gt_nft_at_25pct': bool, 'gap_narrows_at_100pct': bool, 'both_gt_mlp': bool}."""
    ...
```

### Pseudo-code (check_success_criteria)

```
1. dws_gt_nft_at_25pct = stats[0.25]['dws']['auc_mean'] > stats[0.25]['nft']['auc_mean']
2. gap_25  = stats[0.25]['dws']['auc_mean'] - stats[0.25]['nft']['auc_mean']
   gap_100 = stats[1.0]['dws']['auc_mean']  - stats[1.0]['nft']['auc_mean']
   gap_narrows_at_100pct = abs(gap_100) < abs(gap_25)
3. both_gt_mlp = all(stats[f][m]['auc_mean'] > stats[f]['mlp']['auc_mean']
                      for f in cfg.fractions for m in ('dws', 'nft'))
4. return {'dws_gt_nft_at_25pct': ..., 'gap_narrows_at_100pct': ..., 'both_gt_mlp': ...}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| probs | [N, 10] | softmax(logits), passed to `macro_auc_ovr` |
| y_true | [N] | int class labels 0-9 |

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1 | data.py + metrics.py | subsample_train, get_fraction_loader, macro_auc_ovr, gap_closure, aggregate_stats, check_success_criteria |

---

## S-1+S-5+S-6+S-7+S-8: Port + Sweep Runner + Visualization + Orchestration [Budget: 1 subtask]

### API Signatures

```python
# config.py (extends h-m1 Config)
@dataclass
class Config(BaseConfig):
    epochs: int = 100
    lr: float = 1e-4
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    fractions: list = field(default_factory=lambda: [0.25, 0.50, 1.0])
    results_path: str = ".../h-m2/code/outputs/results.json"
    fig_dir: str = ".../h-m2/figures"

# run_sweep.py
def run_single(
    model_type: str, fraction: float, seed: int, cfg: Config,
    weight_shapes: List[Tuple[int, int]], train_ds: Dataset, test_loader: DataLoader,
) -> dict:
    """Builds model by type, get_fraction_loader(train_ds, fraction, seed, cfg),
    trains via train_model_tracked, evals softmax probs on test_loader via macro_auc_ovr.
    Returns {'model': model_type, 'fraction': fraction, 'seed': seed, 'auc': float, 'train_time': float}."""
    ...

def run_sweep(cfg: Config) -> dict:
    """Loops fractions x model_types x seeds (3x3x3=27 runs), calls run_single, times via time.perf_counter().
    Returns {fraction: {model_type: [per-seed result dict, ...]}}."""
    ...

# visualize.py
def plot_learning_curves(stats: dict, out_path: str) -> None: ...   # AUC vs fraction, error bars, 3 models
def plot_25pct_bar(stats: dict, out_path: str) -> None: ...
def plot_gap_closure(gap: dict, out_path: str) -> None: ...
def plot_auc_boxplots(results: dict, out_path: str) -> None: ...
def plot_gate_metrics(stats: dict, out_path: str) -> None: ...      # required gate figure

# main.py
def main() -> None:
    """cfg -> get_dataloaders(cfg) [fixed test_loader] -> run_sweep -> aggregate_stats ->
    check_success_criteria -> visualize(5 plots) -> save results.json."""
    ...
```

### Pseudo-code (run_sweep)

```
1. train_loader_full, test_loader = get_dataloaders(cfg)  # test_loader fixed across all runs
2. train_ds = train_loader_full.dataset
3. weight_shapes = get_weight_shapes(cfg)
4. results = {}
5. for fraction in cfg.fractions:
     results[fraction] = {}
     for model_type in ('mlp', 'dws', 'nft'):
       results[fraction][model_type] = []
       for seed in cfg.seeds:
         results[fraction][model_type].append(
           run_single(model_type, fraction, seed, cfg, weight_shapes, train_ds, test_loader))
6. return results  # 27 total runs
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-2 | config.py + run_sweep.py + visualize.py + main.py | Port config; sweep runner (3 models x 3 fractions x 3 seeds); 5 plots; orchestration + results.json |

---

## Total Subtasks: 2/2 used
