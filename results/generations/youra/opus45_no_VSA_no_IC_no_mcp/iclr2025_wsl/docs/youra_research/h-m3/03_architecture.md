# Architecture: h-m3 (MECHANISM)

**Hypothesis**: Architecture x task interaction — DWS (local bias) should win on backdoor-style local-anomaly detection; NFT (global attention) should win on accuracy-style global-statistic prediction.
**Type**: MECHANISM — reuses h-m1/h-m2 weight-space models (FlattenedMLP, DWSModel, NFTModel) unchanged; adds two synthetic task datasets + 2x3 factorial sweep + interaction-effect stats.

Applied: factorial-interaction-design-pattern (2 tasks x 3 architectures x 3 seeds, mean+-std, two-way ANOVA interaction term)
Applied: shared-model-shared-metrics-pattern (single weight-space backbone reused across differently-headed tasks via num_classes=1 output)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual h-m1/h-m2 code inspected directly (Serena MCP unavailable in this environment; base code read manually per fallback).
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m2/03_architecture.md`
**Findings**:
- `FlattenedMLP`, `DWSModel`, `NFTModel` in `h-m1/code/models.py` take `List[Tensor]` per-layer weights + `weight_shapes: List[Tuple[int,int]]`, output `(B, num_classes)` logits — setting `num_classes=1` gives exactly the scalar output PRD FR-3/FR-5 need for both binary backdoor logit and continuous accuracy regression. **No model changes needed.**
- `MNISTINRDataset`/`normalize_weights`/`collate_fn`/`get_weight_shapes` in `h-m1/code/data.py` load `.pt` files of per-layer weight tensors + label; this loader shape (list-of-layer-weight-tensors + scalar label) is exactly what TrojAI/CNN-Zoo would need to expose too.
- **No TrojAI or CNN-Zoo downloader/loader exists anywhere in the codebase** (confirmed again — h-m2 already hit and documented this gap). PRD FR-1/FR-2 (real dataset download, 600+200 TrojAI models, 1000+300 CNN-Zoo models) is unimplemented and out of scope for this budget; no download credentials/access configured.
- **Decision** (same class of deviation h-m1/h-m2 already documented and accepted): h-m3 uses two **synthetic weight-population generators** built on the same INR-weight-list format, each designed to structurally isolate one type of statistical signal so the DWS-vs-NFT locality/global inductive-bias question can still be tested without real datasets:
  - `backdoor` task: synthetic weight sets where label=1 sets get a small localized perturbation injected into one weight tensor at a random layer/position (local anomaly) — tests DWS's locality bias.
  - `accuracy` task: synthetic weight sets where the continuous target is a function of aggregate statistics across *all* layers (global mean/norm interaction) — tests NFT's global attention advantage.
  - This preserves the mechanism under test (interaction effect between architectural bias and local-vs-global signal structure) while being honest that it is a controlled proxy, not real TrojAI/CNN-Zoo data. Flagged clearly in Notes for Phase 4/5.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| FlattenedMLP, DWSModel, NFTModel | `from models import FlattenedMLP, DWSModel, NFTModel` | `h-m1/code/models.py` (copy into `h-m3/code/`) |
| normalize_weights, collate_fn | `from data import normalize_weights, collate_fn` | `h-m1/code/data.py` (copy into `h-m3/code/`, only these two helpers reused) |
| train_model_tracked | `from train_tracked import train_model_tracked` | `h-m1/code/train_tracked.py` (copy, reused for backdoor task loss=BCE; new minimal regression loop for accuracy task) |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, read directly)

**Note**: `train_model_tracked` in h-m1 hardcodes `CrossEntropyLoss` for multi-class — reused as-is only for a binary variant is not directly compatible; h-m3 adds a small `train_task(model, loader, cfg, loss_fn) -> (model, history)` wrapper instead of forking `train_tracked.py`, so both BCE (backdoor) and MSE (accuracy) losses share one loop.

---

## File Structure

```
h-m3/code/
  config.py          # NEW: ExperimentConfig (tasks, architectures, seeds, epochs, lr, batch_size, dims)
  models.py           # copied from h-m1 unchanged (FlattenedMLP, DWSModel, NFTModel)
  synth_data.py        # NEW: synthetic backdoor + accuracy weight-population generators
  train_task.py        # NEW: generic train_task loop (loss_fn injected), shared by both tasks
  metrics.py            # NEW: compute_auc, compute_rmse_r2, run_interaction_anova
  run_sweep.py           # NEW: trains 3 archs x 2 tasks x 3 seeds = 18 runs, collects ExperimentResult rows
  visualize.py            # NEW: 2x2 bar chart, interaction plot, training curves, diff heatmap
  main.py                  # NEW: entrypoint — cfg -> run_sweep -> aggregate -> anova -> check_success_criteria -> visualize -> results.json
```

---

## Module Definitions

### config.py

**Dependencies**: none

```python
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
    weight_shapes: list = None       # set at runtime from synth_data
    results_path: str = ".../h-m3/code/outputs/results.json"
    fig_dir: str = ".../h-m3/figures"

@dataclass
class ExperimentResult:
    task: str
    architecture: str
    seed: int
    metric_value: float      # AUC (backdoor) or RMSE (accuracy)
    secondary_metric: float = None  # R2 (accuracy only)
    train_time: float = 0.0
```

### synth_data.py

**Dependencies**: torch, models.py (weight_shapes convention)

```python
def make_backdoor_dataset(n: int, weight_shapes: list, seed: int) -> tuple[list, list]: ...
    # returns (weight_lists, binary_labels); label=1 sets get one localized perturbed tensor
def make_accuracy_dataset(n: int, weight_shapes: list, seed: int) -> tuple[list, list]: ...
    # returns (weight_lists, continuous_targets); target = f(global norm/mean stats across all layers) + noise
def default_weight_shapes(hidden_dim: int = 128, n_layers: int = 4) -> list: ...
def build_dataloader(weight_lists: list, labels: list, batch_size: int, shuffle: bool) -> DataLoader: ...
    # wraps in-memory TensorDataset-like list, uses collate_fn from data.py
```

### train_task.py

**Dependencies**: torch, models.py

```python
def build_model(architecture: str, weight_shapes: list, hidden_dim: int, num_classes: int = 1) -> nn.Module: ...
    # dispatch: "mlp"->FlattenedMLP, "dws"->DWSModel, "nft"->NFTModel; matches param count within 10% via hidden_dim tuning
def train_task(model: nn.Module, train_loader, cfg: ExperimentConfig, loss_fn: nn.Module) -> tuple[nn.Module, dict]: ...
    # AdamW + CosineAnnealingLR, cfg.epochs, returns (trained_model, history{epoch: loss})
def predict(model: nn.Module, loader) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (predictions, labels) as numpy
```

### metrics.py

**Dependencies**: sklearn.metrics, scipy.stats, numpy

```python
def compute_auc(preds: np.ndarray, labels: np.ndarray) -> float: ...        # roc_auc_score, sigmoid(preds)
def compute_rmse_r2(preds: np.ndarray, targets: np.ndarray) -> tuple[float, float]: ...
def run_interaction_anova(results: list[ExperimentResult]) -> dict: ...
    # two-way ANOVA (task x architecture) on normalized metric, returns {f_stat, p_value, significant}
def check_success_criteria(stats: dict) -> dict[str, bool]: ...
    # DWS_AUC>NFT_AUC(backdoor), NFT_RMSE<DWS_RMSE(accuracy), both>MLP on >=1 task
```

### run_sweep.py

**Dependencies**: synth_data.py, train_task.py, metrics.py, config.py

```python
def run_single(task: str, architecture: str, seed: int, cfg: ExperimentConfig) -> ExperimentResult: ...
def run_sweep(cfg: ExperimentConfig) -> list[ExperimentResult]: ...   # 2 tasks x 3 archs x 3 seeds = 18 runs
```

### visualize.py

**Dependencies**: metrics.py, matplotlib

```python
def plot_gate_2x2_bar(stats: dict, out_path: str) -> None: ...       # required gate figure: DWS vs NFT x Backdoor vs Accuracy
def plot_interaction(stats: dict, out_path: str) -> None: ...        # architecture x performance, one line per task
def plot_training_curves(histories: dict, out_path: str) -> None: ...  # all 6 conditions
def plot_diff_heatmap(stats: dict, baseline: str, out_path: str) -> None: ...
```

### main.py

**Dependencies**: all modules

```python
def main() -> None: ...  # cfg -> run_sweep -> aggregate -> run_interaction_anova -> check_success_criteria -> visualize -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Port base models | Copy models.py, normalize_weights/collate_fn from h-m1 unchanged; verify num_classes=1 forward works for all 3 archs | 5 | 2+1+1+1 |
| M-2 | Config + weight shape setup | ExperimentConfig, ExperimentResult dataclasses; default_weight_shapes matching param counts within 10% across archs | 6 | 2+1+2+1 |
| M-3 | Synthetic backdoor dataset | make_backdoor_dataset: localized perturbation injection, label balance, build_dataloader | 8 | 2+1+3+2 |
| M-4 | Synthetic accuracy dataset | make_accuracy_dataset: global-stat-driven continuous target with noise | 7 | 2+1+3+1 |
| M-5 | Generic training loop | train_task with injectable loss_fn (BCE/MSE), AdamW+cosine, predict() | 8 | 2+2+2+2 |
| M-6 | Metrics + interaction stats | compute_auc, compute_rmse_r2, run_interaction_anova (two-way ANOVA), check_success_criteria | 9 | 2+2+4+1 |
| M-7 | Sweep runner | run_single/run_sweep across 2 tasks x 3 archs x 3 seeds = 18 runs, param-count verification pre-check | 11 | 3+3+2+3 |
| M-8 | Visualization suite | 4 figures: gate 2x2 bar, interaction plot, training curves (6 conditions), diff heatmap | 9 | 3+2+2+2 |
| M-9 | Main orchestration + results | main.py wiring, results.json with per-task/arch PASS/FAIL against success criteria | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-6, M-7, M-8], Low(4-8): [M-1, M-2, M-3, M-4, M-5, M-9]

---

## Notes

- **Dataset deviation (critical, same class as h-m1/h-m2)**: PRD FR-1/FR-2 require real TrojAI (600+200 models) and CNN-Zoo (1000+300 models) downloads; no such loader/access exists in this codebase or environment. h-m3 substitutes two **synthetic weight-population generators** structurally designed to isolate local-anomaly vs global-statistic signal, preserving the interaction-effect mechanism under test. This is a controlled proxy, not real-world validation — Phase 5 analysis MUST report this as a limitation, matching h-m2's LIMITATION_RECORDED pattern. If real datasets become available in a future hypothesis, only `synth_data.py` needs replacing — model/train/metrics/sweep interfaces are dataset-agnostic.
- `num_classes=1` on all three existing models covers both binary (BCEWithLogitsLoss on raw logit) and regression (MSE on raw output) — no model architecture changes required, only the loss function and target dtype differ per task.
- Param-count matching (PRD FR-3, "within 10%") is enforced via `hidden_dim`/`d_model` tuning in `build_model`, verified once in M-7 pre-check before the 18-run sweep.
- 18 total runs (3 archs x 2 tasks x 3 seeds) at 100 epochs on small synthetic weight sets is well within the 8-hour NFR budget on GPU.
</content>
