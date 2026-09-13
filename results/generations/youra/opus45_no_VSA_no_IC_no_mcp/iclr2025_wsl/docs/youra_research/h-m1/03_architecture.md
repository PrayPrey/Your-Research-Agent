# Architecture: h-m1 (MECHANISM)

**Hypothesis**: DWS (equivariant, local) vs NFT (attention, global) encode different inductive biases, visible in gradient flow and weight update dynamics during training.
**Type**: MECHANISM — extends h-e1 codebase with training dynamics tracking (3 models, 3 seeds, gradient/weight/attention logging every epoch)

Applied: training-dynamics-tracking-pattern (per-epoch gradient norm + weight delta hooks around existing train loop)
Applied: distributional-comparison-pattern (Wasserstein distance + coefficient-of-variation over per-layer time series)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual h-e1 code inspected directly (`Read`, not Serena — Serena MCP unavailable in this environment, base code read manually instead per fallback: file structure is small and fully readable).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- h-e1 code uses a **synthetic MNIST-INR 10-class classification** setup (`data/mnist_inrs/weights/*.pt`), NOT TrojAI/binary backdoor as PRD prose implies. `DWSModel`/`NFTModel` operate on `List[Tensor]` per-layer weights with `weight_shapes: List[Tuple[int,int]]`, output `num_classes=10` logits, `CrossEntropyLoss`.
- `train_model(model, train_loader, cfg) -> nn.Module` is a plain loop with no hooks for gradient/weight tracking — h-m1 must wrap/extend it, not reuse verbatim.
- `NFTModel.get_attention_weights` and `DWSModel.get_layer_activations` already expose the introspection points needed for h-m1 tracking.
- **Decision**: h-m1 reuses `models.py`, `data.py`, `config.py` (Config extended, not replaced) unchanged; reuses `metrics.py` functions as building blocks; replaces `train.py` with an instrumented version (`train_tracked.py`) since gradient/weight-delta capture must live inside the training loop.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| FlattenedMLP, DWSModel, NFTModel | `from h_e1.models import FlattenedMLP, DWSModel, NFTModel` | `h-e1/code/models.py` |
| MNISTINRDataset, get_dataloaders, get_weight_shapes | `from h_e1.data import get_dataloaders, get_weight_shapes` | `h-e1/code/data.py` |
| attention_entropy, layer_activation_variance | `from h_e1.metrics import attention_entropy, layer_activation_variance` | `h-e1/code/metrics.py` |
| Config (base fields) | `from h_e1.config import Config as BaseConfig` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, read directly)

**Note**: `h-e1/code/` has no `__init__.py`/package name — Phase 4 Coder should copy or symlink needed files into `h-m1/code/` rather than rely on cross-package import (simplest: copy `models.py`, `data.py`, `metrics.py` into `h-m1/code/` and extend `config.py` there, since h-e1 code is not installed as a package).

---

## File Structure

```
h-m1/code/
  config.py         # extends h-e1 Config: adds seeds list, track_every, snapshot_every
  data.py            # copied from h-e1 (unchanged)
  models.py          # copied from h-e1 (unchanged)
  metrics.py         # copied from h-e1 + new: wasserstein_grad_distance, weight_update_cov, locality_score
  tracker.py         # NEW: TrainingDynamicsTracker (grad norms, weight deltas, attention entropy per epoch)
  train_tracked.py   # NEW: instrumented train loop wrapping train_model, calls tracker each epoch
  run_seeds.py       # NEW: runs DWS/NFT (+MLP) x 3 seeds, collects per-seed dynamics
  visualize.py       # NEW: 4 figures (grad heatmap, locality evolution, attention entropy curve, layer boxplots)
  main.py            # NEW: entrypoint — load cfg, run_seeds, aggregate, check success criteria, visualize
```

---

## Module Definitions

### config.py

**Dependencies**: none

```python
@dataclass
class Config(BaseConfig):  # inherits h-e1 fields (lr, batch_size, epochs, d_model, ...)
    epochs: int = 100
    lr: float = 1e-4
    seeds: list = field(default_factory=lambda: [42, 123, 7])
    track_every: int = 1          # epoch interval for grad norm tracking
    snapshot_every: int = 10      # epoch interval for weight snapshots
    wasserstein_threshold: float = 0.1
    early_signature_epoch: int = 20
```

### tracker.py

**Dependencies**: models.py

```python
class TrainingDynamicsTracker:
    def __init__(self, model: nn.Module, model_type: str): ...
    def track_gradients(self, epoch: int) -> None: ...              # per-layer grad norm -> self.grad_norms[name]
    def track_weight_updates(self, prev_weights: dict, epoch: int) -> None: ...  # delta norm -> self.weight_updates
    def track_attention(self, sample_input: list[Tensor]) -> None: ...  # NFT only, appends entropy
    def snapshot_weights(self) -> dict[str, Tensor]: ...
    def to_dict(self) -> dict: ...  # {grad_norms, weight_updates, attention_entropy}
```

### metrics.py (extends h-e1 metrics.py)

**Dependencies**: scipy.stats

```python
# h-e1 functions reused unchanged: attention_entropy, layer_activation_variance

def wasserstein_grad_distance(dws_norms: list[float], nft_norms: list[float]) -> float: ...
def weight_update_cov(layer_updates: dict[str, list[float]]) -> float: ...  # std/mean across layers
def locality_score(layer_updates: dict[str, list[float]], epoch: int) -> float: ...
def check_success_criteria(dws_stats: dict, nft_stats: dict, cfg: Config) -> dict[str, bool]: ...
```

### train_tracked.py

**Dependencies**: models.py, data.py, tracker.py, config.py

```python
def train_model_tracked(model: nn.Module, model_type: str, train_loader: DataLoader, cfg: Config) -> tuple[nn.Module, TrainingDynamicsTracker]: ...
```

### run_seeds.py

**Dependencies**: train_tracked.py, models.py, data.py, config.py

```python
def run_single(model_type: str, seed: int, cfg: Config, weight_shapes: list) -> dict: ...  # trains + returns tracker.to_dict() + eval acc
def run_all_seeds(cfg: Config) -> dict: ...  # {model_type: [per-seed results]} for mlp/dws/nft
```

### visualize.py

**Dependencies**: metrics.py

```python
def plot_gradient_heatmap(dws_grads: dict, nft_grads: dict, out_path: str) -> None: ...
def plot_locality_evolution(dws_updates: dict, out_path: str) -> None: ...
def plot_attention_entropy_curve(nft_entropy: list[float], out_path: str) -> None: ...
def plot_layerwise_update_boxplot(dws_updates: dict, nft_updates: dict, out_path: str) -> None: ...
def plot_gate_metrics(results: dict, out_path: str) -> None: ...  # required gate figure
```

### main.py

**Dependencies**: all modules

```python
def main() -> None: ...  # cfg -> run_all_seeds -> aggregate stats -> check_success_criteria -> visualize -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Port base code | Copy models.py/data.py/metrics.py from h-e1, extend Config | 5 | 2+1+1+1 |
| M-2 | TrainingDynamicsTracker | Gradient norm + weight delta + attention entropy hooks | 12 | 3+2+4+3 |
| M-3 | Instrumented training loop | train_model_tracked wrapping base loop with tracker calls, weight snapshotting every 10 epochs | 11 | 3+3+3+2 |
| M-4 | Distributional metrics | wasserstein_grad_distance, weight_update_cov, locality_score, check_success_criteria | 8 | 2+2+3+1 |
| M-5 | Multi-seed runner | run_single/run_all_seeds across MLP/DWS/NFT x 3 seeds | 9 | 2+3+2+2 |
| M-6 | Early-signature detection | Verify architecture-specific signatures detectable within 20 epochs (subset analysis on tracked data) | 6 | 1+2+2+1 |
| M-7 | Visualization suite | 5 figures: grad heatmap, locality evolution, attention entropy curve, layer boxplot, gate metrics | 10 | 3+2+2+3 |
| M-8 | Main orchestration + results | main.py wiring, results.json with PASS/FAIL per criterion | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-3, M-5, M-7], Low(4-8): [M-1, M-4, M-6, M-8]

---

## Notes

- PRD mentions TrojAI dataset; actual h-e1 code uses synthetic MNIST-INR data. Per base-code-trust rule, architecture reuses the actual MNIST-INR pipeline. Phase 4 Coder should flag this PRD/code mismatch; TrojAI download (FR-1.1) is out of scope unless base data pipeline is swapped — default: keep MNIST-INR pipeline, note deviation in implementation report.
- `weight_shapes` obtained via `get_weight_shapes(cfg)` from h-e1 `data.py`, passed to `DWSModel`/`NFTModel`/`FlattenedMLP` constructors identically to h-e1.
- 3-model comparison (MLP baseline + DWS + NFT) retained from h-e1 for consistency, though PRD success criteria only concern DWS vs NFT.
