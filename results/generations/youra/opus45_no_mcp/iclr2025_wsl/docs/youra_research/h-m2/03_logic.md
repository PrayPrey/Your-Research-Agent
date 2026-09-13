# Logic Design: H-M2 (Alignment Preprocessing Benefit)

**Applied**: Git Re-Basin greedy weight matching (correlation argmax), reuses H-M1 encoder/train/eval infra

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — spec-only reference (no `h-m1/code/` files present on disk to verify)
**Status**: No actual H-M1 code directory found; signatures taken from `h-m1/03_logic.md` spec as-is. Flagged risk below.
**Analyzed Path**: docs/youra_research/h-m1/03_logic.md (spec, not code)
**Relevant Symbols**: `LayerWiseEncoder`, `AccuracyPredictor`, `FullModel`, `train_model`, `predict`, `compute_pearson`, `compare_methods`, `set_seed`, `run_seed` (from spec)

**Risk note**: Per rules, spec params may differ from actual implementation. Since `h-m1/code/` does not exist yet (H-M1 presumably implemented in a separate run), Phase 4 Coder MUST verify actual H-M1 code signatures at build time if available; otherwise implement per spec below as ground truth.

---

## A-1: Alignment Module (alignment.py) [Complexity: 12, Budget: 12]

**Applied**: Git Re-Basin weight matching, greedy correlation argmax (Hungarian as ablation)

### API Signatures

```python
import torch
from typing import Dict, List
from scipy.optimize import linear_sum_assignment

def detect_permutable_layers(state_dict: Dict[str, torch.Tensor]) -> List[str]:
    """Return sorted names of conv/fc weight layers eligible for output-dim permutation (excludes final output layer, biases, norm params)."""
    ...

def get_next_layer(layer_name: str, state_dict: Dict[str, torch.Tensor]) -> str | None:
    """Return next weight layer name in sorted-key order after layer_name, or None if last."""
    ...

def reorder_input_dim(w: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Reorder dim=1 (input channels) of w by perm. w: [out, in, ...] -> [out, in, ...]"""
    ...

def align_to_reference(
    model_sd: Dict[str, torch.Tensor],
    reference_sd: Dict[str, torch.Tensor],
    perm_layers: List[str],
    algorithm: str = "greedy",  # "greedy" | "hungarian"
) -> Dict[str, torch.Tensor]:
    """Align model_sd to reference_sd via weight matching. Returns aligned state dict (copy)."""
    ...

def compute_alignment_batch(
    model_zoo: List[Dict[str, torch.Tensor]],
    reference_idx: int = 0,
    algorithm: str = "greedy",
) -> List[Dict[str, torch.Tensor]]:
    """Align all models in zoo to model_zoo[reference_idx]. Returns aligned list (same order, same length)."""
    ...

def verify_alignment(aligned_sd: Dict[str, torch.Tensor], reference_sd: Dict[str, torch.Tensor]) -> float:
    """Mean cosine similarity across permutable layers (flattened) between aligned_sd and reference_sd. Higher = better aligned."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| w_ref, w_model | [out, in, kH, kW] or [out, in] | conv or fc weight |
| w_ref_flat, w_model_flat | [out, in*kH*kW] | `.view(out, -1)` |
| corr | [out_ref, out_model] | `w_ref_flat @ w_model_flat.T` |
| perm (greedy) | [out] | `argmax(corr, dim=1)`, int64 |
| perm (hungarian) | [out] | `linear_sum_assignment(-corr.numpy())[1]` |
| aligned weight | [out, in, kH, kW] | `w_model[perm]` (output-dim reorder) |
| next layer weight | [out_next, in_next, ...] | `in_next` reordered by same `perm` |

### Pseudo-code (greedy correlation matching)

```
align_to_reference(model_sd, reference_sd, perm_layers, algorithm):
  1. aligned_sd = model_sd.copy()
  2. for layer_name in perm_layers (sorted order, shallow -> deep):
       w_ref = reference_sd[layer_name]                  # [out, in, ...]
       w_model = aligned_sd[layer_name]
       w_ref_flat = w_ref.view(w_ref.size(0), -1)
       w_model_flat = w_model.view(w_model.size(0), -1)
       corr = w_ref_flat @ w_model_flat.T                # [out, out]
       if algorithm == "greedy":
         perm = argmax(corr, dim=1)                       # [out], may have duplicates
       else:  # hungarian
         row_ind, col_ind = linear_sum_assignment(-corr.numpy())
         perm = tensor(col_ind)[argsort(row_ind)]          # [out], 1-to-1 optimal
       aligned_sd[layer_name] = w_model[perm]
       next_layer = get_next_layer(layer_name, model_sd)
       if next_layer is not None:
         aligned_sd[next_layer] = reorder_input_dim(aligned_sd[next_layer], perm)
  3. return aligned_sd

verify_alignment(aligned_sd, reference_sd):
  1. sims = []
  2. for layer_name in detect_permutable_layers(reference_sd):
       a = aligned_sd[layer_name].flatten()
       r = reference_sd[layer_name].flatten()
       sims.append(cosine_similarity(a, r, dim=0))
  3. return mean(sims)

compute_alignment_batch(model_zoo, reference_idx, algorithm):
  1. reference_sd = model_zoo[reference_idx]
  2. perm_layers = detect_permutable_layers(reference_sd)
  3. aligned_zoo = []; convergence_count = 0
  4. for i, model_sd in enumerate(model_zoo):
       if i == reference_idx: aligned_zoo.append(model_sd); convergence_count += 1; continue
       aligned_sd = align_to_reference(model_sd, reference_sd, perm_layers, algorithm)
       if verify_alignment(aligned_sd, reference_sd) > verify_alignment(model_sd, reference_sd):
         convergence_count += 1
       aligned_zoo.append(aligned_sd)
  5. print(f"Alignment convergence: {convergence_count/len(model_zoo):.2%}")
  6. return aligned_zoo
```

### Subtasks [7/12 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | detect_permutable_layers | sorted-key scan, filter conv/fc weight tensors (ndim>=2), exclude last layer + bias/norm keys |
| L-1-2 | get_next_layer / reorder_input_dim | sorted-key successor lookup; `w[:, perm]` reorder |
| L-1-3 | align_to_reference (greedy) | corr matrix + argmax per layer, propagate perm to next layer input dim |
| L-1-4 | align_to_reference (hungarian branch) | `scipy.optimize.linear_sum_assignment(-corr)` for ablation flag |
| L-1-5 | compute_alignment_batch | loop zoo, align each to reference, track convergence_count |
| L-1-6 | verify_alignment | mean cosine similarity over permutable layers |
| L-1-7 | alignment caching | pickle/torch.save aligned_zoo to disk keyed by (reference_idx, algorithm) per NFR-2 |

---

## A-2: Data Pipeline Extension [Complexity: 5, Budget: 5]

**Applied**: Wraps H-M1 `load_model_zoo` with alignment preprocessing step

### API Signatures

```python
def load_and_align(
    split: str,
    reference_idx: int = 0,
    algorithm: str = "greedy",
    cache_path: str | None = None,
) -> tuple[List[Dict[str, torch.Tensor]], torch.Tensor]:
    """Reuse H-M1 load_model_zoo(split) then compute_alignment_batch. Returns (aligned_state_dicts, labels[N])."""
    ...
```

### Pseudo-code

```
load_and_align(split, reference_idx, algorithm, cache_path):
  1. models, labels = load_model_zoo(split=split)        # H-M1 reuse
  2. if cache_path exists: return torch.load(cache_path), labels
  3. aligned = compute_alignment_batch(models, reference_idx, algorithm)
  4. if cache_path: torch.save(aligned, cache_path)
  5. return aligned, labels
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_and_align | compose load_model_zoo + compute_alignment_batch + cache read/write |
| L-2-2 | make_dataloaders reuse | pass aligned state_dicts into H-M1 `make_dataloaders` (LayerWiseEncoder collate unchanged) |

---

## A-3: Two-Method Orchestration (baseline vs GRB) [Complexity: 8, Budget: 8]

**Applied**: Extends H-M1 `run_seed`/`main` pattern with alignment toggle

### API Signatures

```python
def run_seed_grb(
    use_alignment: bool, seed: int,
    train_loader, val_loader, test_loader, cfg: "Config",
) -> dict:
    """use_alignment=False -> H-M1 layerwise baseline; True -> GRB-aligned layerwise. Returns {'pearson_r': float, 'history': dict}."""
    ...
```

### Pseudo-code

```
run_seed_grb(use_alignment, seed, train_loader, val_loader, test_loader, cfg):
  1. set_seed(seed)                                       # H-M1 reuse
  2. encoder = LayerWiseEncoder(num_layers, 4, cfg.hidden_dim, cfg.embed_dim)  # H-M1 reuse
  3. predictor = AccuracyPredictor(cfg.embed_dim, cfg.predictor_hidden)        # H-M1 reuse
  4. model = FullModel(encoder, predictor, method="layerwise").to(cfg.device) # H-M1 reuse
  5. model, history = train_model(model, train_loader, val_loader, ...)       # H-M1 reuse
  6. preds, targets = predict(model, test_loader, cfg.device)                 # H-M1 reuse
  7. return {'pearson_r': compute_pearson(preds, targets)['pearson_r'], 'history': history}

main():
  1. train_aligned, labels_train = load_and_align('train', cache_path='cache/train_aligned.pt')
  2. val_aligned, labels_val = load_and_align('val', cache_path='cache/val_aligned.pt')
  3. test_aligned, labels_test = load_and_align('test', cache_path='cache/test_aligned.pt')
  4. train_raw, _ = load_model_zoo(split='train')  # unaligned, for baseline
  5. for use_alignment, (models_tr, models_val, models_te) in [
         (False, (train_raw, val_raw, test_raw)),
         (True,  (train_aligned, val_aligned, test_aligned))]:
       for seed in cfg.seeds:
         loaders = make_dataloaders(models_tr, models_val, models_te, labels)
         result = run_seed_grb(use_alignment, seed, *loaders, cfg)
         collect r-value into baseline_rs / grb_rs
  6. gate = compare_methods(baseline_rs, grb_rs)          # H-M1 reuse
  7. PASS if gate['delta_r'] > 0.05 and gate['p_value'] < 0.05
  8. generate figures (gate bar chart, scatter, per-seed line, alignment histogram), write results.json
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | run_seed_grb | H-M1 run_seed reused as-is with pre-aligned weights_dict list |
| L-3-2 | main dual-loop | baseline vs GRB x 5 seeds, reuse H-M1 loaders/model builders |
| L-3-3 | gate decision | `compare_methods` + threshold 0.05 (differs from H-M1's 0.1) per PRD FR-6.4 |
| L-3-4 | alignment diagnostic figure | histogram of `verify_alignment` pre/post distances collected during `compute_alignment_batch` |

---

## External Dependencies (H-M1, spec-verified only)

```python
# From: h-m1/03_logic.md (SPEC — actual code not found on disk; verify at Phase 4 if code/ exists)
from data import load_model_zoo, make_dataloaders
from models import LayerWiseEncoder, AccuracyPredictor, FullModel
from train import set_seed, train_model, save_checkpoint
from evaluate import predict, compute_pearson, compare_methods

def load_model_zoo(split: str) -> tuple[list[dict], list[float]]: ...
def make_dataloaders(train_models, val_models, test_models, labels) -> tuple[DataLoader, DataLoader, DataLoader]: ...
class LayerWiseEncoder(nn.Module):
    def __init__(self, num_layers: int, stats_per_layer: int = 4, hidden_dim: int = 256, embed_dim: int = 128): ...
    def forward(self, weights_dict: dict[str, Tensor]) -> Tensor: ...  # -> [embed_dim]
class AccuracyPredictor(nn.Module):
    def __init__(self, embed_dim: int = 128, hidden_dim: int = 64): ...
    def forward(self, embedding: Tensor) -> Tensor: ...  # [B, embed_dim] -> [B]
class FullModel(nn.Module):
    def __init__(self, encoder: nn.Module, predictor: AccuracyPredictor, method: str): ...
    def forward(self, weights_input) -> Tensor: ...
def train_model(model, train_loader, val_loader, lr=1e-3, weight_decay=1e-4,
                 max_epochs=50, early_stop_patience=10, device="cuda") -> tuple[nn.Module, dict]: ...
def predict(model, loader, device) -> tuple[np.ndarray, np.ndarray]: ...
def compute_pearson(preds, targets) -> dict: ...  # {'pearson_r','p_value'}
def compare_methods(baseline_results, treatment_results) -> dict: ...  # {'delta_r','t_stat','p_value'}
```

**Verified from**: `h-m1/03_logic.md` (spec only — `h-m1/code/` not present; Phase 4 must re-verify if actual code exists by the time this hypothesis builds).
