# Architecture: H-M2 (Alignment Preprocessing Benefit)

**Applied**: Preprocessing-injection pattern - insert alignment step between data loading and encoding, reuse H-M1 encoder/train/eval harness unchanged.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (brownfield, extends H-M1)
**Status**: H-M1 code not yet materialized on disk at analysis time (H-M1 03_architecture.md is the source of truth; H-M1 Phase 4 implementation runs in parallel/prior). Import paths below verified against H-M1's `03_architecture.md` module interfaces (data.py, models.py, train.py, evaluate.py, config.py) rather than live code.
**Analyzed Path**: `h-m1/code/` (spec-level; live Serena symbol scan not possible — no code/ dir present)
**Findings**: H-M1 defines `load_model_zoo`, `make_dataloaders`, `LayerWiseEncoder`, `AccuracyPredictor`, `FullModel`, `train_model`, `set_seed`, `compute_pearson`, `compare_methods`. H-M2 reuses all of these unmodified; only new code is `alignment.py`.

---

## Module Structure

```
h-m2/code/
├── alignment.py       (NEW)
├── config.py           (extends H-M1 Config)
├── run_experiment.py   (NEW orchestration)
```

No new data.py / models.py / train.py / evaluate.py — imported directly from `h-m1/code/`.

### alignment.py (`h-m2/code/alignment.py`)

**Dependencies**: torch (stdlib-adjacent, already installed)

```python
from typing import Dict, List

def detect_permutable_layers(reference_sd: Dict[str, torch.Tensor]) -> List[str]: ...
    # identify conv/fc weight keys eligible for output-channel permutation

def get_next_layer(layer_name: str, sd: Dict[str, torch.Tensor]) -> str | None: ...
    # returns following layer name whose input dim must be reordered, or None

def reorder_input_dim(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor: ...

def align_to_reference(
    model_sd: Dict[str, torch.Tensor],
    reference_sd: Dict[str, torch.Tensor],
    perm_layers: List[str],
) -> Dict[str, torch.Tensor]: ...
    # greedy correlation-based weight matching; ponytail: greedy not Hungarian,
    # upgrade path = Ablation 2 (scipy.optimize.linear_sum_assignment)

def verify_alignment(sd_a: Dict[str, torch.Tensor], sd_b: Dict[str, torch.Tensor]) -> float: ...
    # mean cosine similarity across perm_layers, used for convergence check

def compute_alignment_batch(
    model_zoo: List[Dict[str, torch.Tensor]],
    reference_idx: int = 0,
) -> tuple[List[Dict[str, torch.Tensor]], float]: ...
    # returns (aligned_zoo, convergence_rate)
```

### config.py (`h-m2/code/config.py`)

**Dependencies**: `h_m1.code.config.Config`

```python
from h_m1.code.config import Config as BaseConfig
from dataclasses import dataclass, field

@dataclass
class AlignmentConfig(BaseConfig):
    reference_idx: int = 0
    reference_strategy: str = "first"       # first | random | median_acc | highest_acc
    alignment_algo: str = "greedy"          # greedy | hungarian
    align_layers: str = "all"               # all | conv_only
    aligned_cache_path: str = "data/aligned_weights_cache.pt"
    convergence_threshold: float = 0.95
```

### run_experiment.py (`h-m2/code/run_experiment.py`)

**Dependencies**: alignment.py, config.py, h-m1/code/{data,models,train,evaluate}.py

```python
from h_m1.code.data import load_model_zoo, make_dataloaders
from h_m1.code.models import LayerWiseEncoder, AccuracyPredictor, FullModel
from h_m1.code.train import set_seed, train_model
from h_m1.code.evaluate import predict, compute_pearson, compare_methods, plot_gate_metrics, plot_scatter, plot_per_seed
from alignment import compute_alignment_batch, detect_permutable_layers
from config import AlignmentConfig

def select_reference(train_samples: list, strategy: str) -> int: ...
def build_aligned_dataset(train, val, test, cfg: AlignmentConfig) -> tuple[list, list, list, float]: ...
    # applies compute_alignment_batch to all splits, caches to aligned_cache_path,
    # returns (train_aligned, val_aligned, test_aligned, convergence_rate)

def run_seed(method: str, seed: int, train_loader, val_loader, test_loader, cfg) -> dict: ...
    # method: 'layerwise' (baseline, unaligned) | 'layerwise_grb' (proposed, aligned)

def plot_alignment_diagnostic(pre_dists: list, post_dists: list, save_path: str) -> None: ...

def main() -> None:
    # orchestrates: load full zoo (61,335 models, FULL test=9,345) -> align once (cached) ->
    # 5 seeds x 2 methods -> gate check (Δr>0.05, p<0.05) -> figures -> results.json
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M1 Architecture Spec)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Data loading | `from h_m1.code.data import load_model_zoo, make_dataloaders` | `h-m1/code/data.py` |
| Layer-wise encoder | `from h_m1.code.models import LayerWiseEncoder, AccuracyPredictor, FullModel` | `h-m1/code/models.py` |
| Training loop | `from h_m1.code.train import set_seed, train_model` | `h-m1/code/train.py` |
| Evaluation | `from h_m1.code.evaluate import predict, compute_pearson, compare_methods, plot_gate_metrics, plot_scatter, plot_per_seed` | `h-m1/code/evaluate.py` |
| Base config | `from h_m1.code.config import Config` | `h-m1/code/config.py` |

**Verified from**: `h-m1/03_architecture.md` (H-M1 code not yet on disk — Phase 4 Coder MUST confirm actual import paths/module names once H-M1 `code/` exists; fall back to relative path copy if package import unavailable, e.g. `sys.path.append("../h-m1/code")`).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | detect_permutable_layers + reorder helpers | Identify conv/fc perm layers, get_next_layer, reorder_input_dim | 6 | 2+1+2+1 |
| B-2 | align_to_reference (greedy weight matching) | Correlation-based permutation + input-dim propagation | 9 | 3+2+3+1 |
| B-3 | compute_alignment_batch + verify_alignment | Zoo-wide alignment loop, convergence tracking (target >95%) | 8 | 2+2+2+2 |
| B-4 | Alignment caching layer | Cache aligned weights to disk, load-if-exists to avoid recompute (NFR-1) | 5 | 1+1+1+2 |
| B-5 | AlignmentConfig + reference selection strategies | Extend Config, select_reference (first/random/median/highest) | 5 | 1+1+2+1 |
| B-6 | build_aligned_dataset pipeline | Wire alignment into H-M1 data pipeline for train/val/test (FULL sets) | 6 | 2+2+1+1 |
| B-7 | run_seed dual-method orchestration | Train baseline (unaligned) vs proposed (aligned) per seed, reuse H-M1 train_model | 7 | 2+2+2+1 |
| B-8 | Multi-seed + gate decision | 5 seeds x 2 methods, compare_methods (Δr, paired t-test), gate logic | 8 | 2+3+2+1 |
| B-9 | Visualization: alignment diagnostic + reuse H-M1 plots | plot_alignment_diagnostic (pre/post histogram), wire existing gate/scatter/per-seed plots | 5 | 1+1+2+1 |
| B-10 | Ablation studies (reference/algo/partial) | 3 ablations: reference selection, greedy vs Hungarian, conv-only vs all-layer alignment | 8 | 3+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-2, B-3, B-8, B-10], Low(4-8): [B-1, B-4, B-5, B-6, B-7, B-9]

**Total complexity**: 67 (task count 10, within FULL tier max 30 tasks / 6-12 epics)

---

## Notes

- Only new module is `alignment.py`; everything else is import + thin orchestration (`run_experiment.py`) + config extension.
- Full test set (9,345 models) used for evaluation per experiment brief — no subset sampling.
- Alignment run once, cached (B-4) — avoids re-running GRB per seed (NFR-1: <2hr one-time cost).
- Hungarian algorithm (Ablation 2) deferred to ablation task B-10, not core path — greedy sufficient for PoC per PRD Non-Goals.
