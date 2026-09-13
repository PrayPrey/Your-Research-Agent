# Architecture: h-m2 (MECHANISM)

**Hypothesis**: DWS locality bias reduces sample complexity — DWS should match/exceed NFT at low training-data fractions on the shared weight-space classification task.
**Type**: MECHANISM — extends h-m1 codebase with sample-efficiency evaluation (25%/50%/100% data fractions, 3 seeds, 3 models)

Applied: sample-efficiency-curve-pattern (subsample train set at fixed fractions, retrain from scratch, eval on fixed held-out test set)
Applied: distributional-comparison-pattern (mean+-std across seeds, gap-closure metric, reused from h-m1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual h-m1 code inspected directly (Serena MCP unavailable in this environment; base code read manually per fallback — file structure small and fully readable).
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- h-m1 code (and h-e1 before it) uses **synthetic MNIST-INR 10-class classification** (`data/mnist_inrs/weights/*.pt`), NOT TrojAI/binary backdoor detection as this PRD's prose assumes. `DWSModel`/`NFTModel`/`FlattenedMLP` take `List[Tensor]` per-layer weights + `weight_shapes`, output `num_classes=10` logits, trained with `CrossEntropyLoss`.
- No TrojAI download/loader exists anywhere in the codebase; PRD's `trojai_api.download_round` is unimplemented and out of scope for this budget.
- `train_model_tracked(model, model_type, train_loader, cfg) -> (model, tracker)` already does full instrumented training (AdamW, cosine LR, CE loss) — directly reusable, only needs a subsampled `train_loader`.
- `get_dataloaders(cfg) -> (train_loader, test_loader)` does a fixed seeded split; h-m2 needs a variant that keeps `test_loader` fixed but subsamples `train_ds` by fraction before building `train_loader`.
- **Decision**: h-m2 reuses `models.py`, `data.py`, `config.py`, `tracker.py`, `train_tracked.py` unchanged (copied in); replaces multiclass accuracy with **AUC-style evaluation** — since data is 10-class not binary, PRD's ROC-AUC metric is redefined as **one-vs-rest macro-AUC** (`sklearn roc_auc_score(multi_class='ovr')`) applied to softmax probs, preserving the "AUC vs fraction" comparison intent without needing binary labels. This is the same class of PRD/implementation deviation h-m1 already documented and accepted.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| FlattenedMLP, DWSModel, NFTModel | `from models import FlattenedMLP, DWSModel, NFTModel` | `h-m1/code/models.py` (copy into `h-m2/code/`) |
| MNISTINRDataset, normalize_weights, collate_fn, get_weight_shapes | `from data import MNISTINRDataset, collate_fn, get_weight_shapes` | `h-m1/code/data.py` (copy into `h-m2/code/`) |
| Config | `from config import Config` | `h-m1/code/config.py` (copy, extend with fractions field) |
| TrainingDynamicsTracker | `from tracker import TrainingDynamicsTracker` | `h-m1/code/tracker.py` (copy, tracking optional/unused for h-m2) |
| train_model_tracked | `from train_tracked import train_model_tracked` | `h-m1/code/train_tracked.py` (copy, reused as-is) |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, read directly)

**Note**: h-m1 code has no package/`__init__.py` — copy the 5 files above into `h-m2/code/` (same pattern h-m1 used copying from h-e1).

---

## File Structure

```
h-m2/code/
  config.py         # copied from h-m1, adds fractions: List[float]
  data.py            # copied from h-m1 unchanged + new: subsample_train(train_ds, fraction, seed) -> Subset
  models.py          # copied from h-m1 unchanged
  tracker.py         # copied from h-m1 unchanged (unused by h-m2, kept for train_model_tracked signature)
  train_tracked.py   # copied from h-m1 unchanged
  metrics.py         # NEW: macro_auc_ovr, gap_closure, aggregate_stats
  run_sweep.py       # NEW: trains MLP/DWS/NFT x 3 fractions x 3 seeds, collects AUC
  visualize.py       # NEW: learning curve, 25%-fraction bar chart, gap-closure plot, box plots
  main.py            # NEW: entrypoint — cfg -> run_sweep -> aggregate -> check_success_criteria -> visualize -> results.json
```

---

## Module Definitions

### config.py

**Dependencies**: none

```python
@dataclass
class Config:  # copied fields from h-m1 (data_dir, batch_size, d_model, dws_hidden, mlp_hidden, lr, weight_decay, epochs, device, ...)
    epochs: int = 100
    lr: float = 1e-4
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    fractions: list = field(default_factory=lambda: [0.25, 0.50, 1.0])
    results_path: str = ".../h-m2/code/outputs/results.json"
    fig_dir: str = ".../h-m2/figures"
```

### data.py (extends h-m1 data.py)

**Dependencies**: torch.utils.data

```python
# reused unchanged: MNISTINRDataset, normalize_weights, collate_fn, get_dataloaders, get_weight_shapes

def subsample_train(train_ds: Dataset, fraction: float, seed: int) -> Subset: ...  # deterministic random subset of given fraction
def get_fraction_loader(train_ds: Dataset, fraction: float, seed: int, cfg: Config) -> DataLoader: ...
```

### metrics.py

**Dependencies**: sklearn.metrics, numpy

```python
def macro_auc_ovr(y_true: np.ndarray, probs: np.ndarray) -> float: ...  # roc_auc_score(multi_class='ovr', average='macro')
def gap_closure(dws_aucs: dict[float, float], nft_aucs: dict[float, float]) -> dict[float, float]: ...  # dws-nft per fraction
def aggregate_stats(results: dict) -> dict: ...  # mean/std per (model, fraction) across seeds
def check_success_criteria(stats: dict, cfg: Config) -> dict[str, bool]: ...  # DWS>NFT@25%, gap narrows, both>MLP
```

### run_sweep.py

**Dependencies**: models.py, data.py, train_tracked.py, metrics.py, config.py

```python
def run_single(model_type: str, fraction: float, seed: int, cfg: Config, weight_shapes: list, train_ds, test_loader) -> dict: ...  # {auc, train_time}
def run_sweep(cfg: Config) -> dict: ...  # {fraction: {model_type: [per-seed dict, ...]}}
```

### visualize.py

**Dependencies**: metrics.py

```python
def plot_learning_curves(stats: dict, out_path: str) -> None: ...  # AUC vs fraction, error bars, all 3 models
def plot_25pct_bar(stats: dict, out_path: str) -> None: ...
def plot_gap_closure(gap: dict, out_path: str) -> None: ...
def plot_auc_boxplots(results: dict, out_path: str) -> None: ...
def plot_gate_metrics(stats: dict, out_path: str) -> None: ...  # required gate figure
```

### main.py

**Dependencies**: all modules

```python
def main() -> None: ...  # cfg -> run_sweep -> aggregate_stats -> check_success_criteria -> visualize -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| S-1 | Port base code | Copy models.py/data.py/config.py/tracker.py/train_tracked.py from h-m1, extend Config with fractions | 5 | 2+1+1+1 |
| S-2 | Subsampling utility | subsample_train + get_fraction_loader, deterministic per-seed subset | 6 | 2+2+1+1 |
| S-3 | AUC metrics | macro_auc_ovr, gap_closure, aggregate_stats | 7 | 2+1+3+1 |
| S-4 | Success criteria check | check_success_criteria (DWS>NFT@25%, gap narrows, both>MLP) | 5 | 1+2+1+1 |
| S-5 | Sweep runner | run_single/run_sweep: 3 models x 3 fractions x 3 seeds = 27 training runs | 12 | 3+3+2+4 |
| S-6 | Timing instrumentation | Capture train_time per run, verify <4hr NFR budget | 4 | 1+1+1+1 |
| S-7 | Visualization suite | 5 figures: learning curves, 25% bar, gap closure, boxplots, gate metrics | 10 | 3+2+2+3 |
| S-8 | Main orchestration + results | main.py wiring, results.json with per-fraction PASS/FAIL | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [S-5, S-7], Low(4-8): [S-1, S-2, S-3, S-4, S-6, S-8]

---

## Notes

- PRD assumes TrojAI binary backdoor detection; actual reusable pipeline (h-m1/h-e1) is synthetic MNIST-INR 10-class weight classification with no TrojAI loader implemented. Per base-code-trust rule, h-m2 reuses the actual pipeline and redefines "ROC-AUC" as one-vs-rest macro-AUC on the 10-class task, preserving the sample-efficiency comparison intent. Phase 4 Coder should flag this as a continuation of the same deviation h-m1 already documented; TrojAI download (FR-1) is out of scope for this budget.
- `train_model_tracked` already implements the exact optimizer/schedule/loss (AdamW, cosine, lr=1e-4) the PRD specifies — reused verbatim, no new training loop needed.
- Tracker/gradient logging from h-m1 is not needed for h-m2's sample-efficiency question; `tracker.py`/`TrainingDynamicsTracker` is only kept because `train_model_tracked` returns it — its output is simply discarded in `run_single`.
- 27 total training runs (3 models x 3 fractions x 3 seeds) at 100 epochs each on small MNIST-INR data is well within the 4-hour NFR budget on GPU.
