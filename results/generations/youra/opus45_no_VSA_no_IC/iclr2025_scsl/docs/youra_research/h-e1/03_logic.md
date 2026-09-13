# Logic: H-E1 Compression Ordering Effect Existence

**Type**: EXISTENCE (PoC) | **Tier**: LIGHT

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 9, Budget: 9]

**Applied**: Standard torchvision ImageFolder + DataLoader pattern

```python
def load_data(cfg: Config) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Returns (train_subset_loader, calib_loader, val_loader)."""
    ...

def stratified_subset(dataset: ImageFolder, fraction: float, seed: int) -> Subset:
    """Stratified sample per-class. len(dataset) -> len(dataset)*fraction."""
    ...

def get_calibration_loader(train_loader: DataLoader, n_samples: int) -> DataLoader:
    """First n_samples from train set, batch_size=1, no shuffle."""
    ...
```

| Variable | Shape | Note |
|----------|-------|------|
| batch (train/val) | [B, 3, 224, 224] | normalized |
| labels | [B] | int64, 0-999 |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | ImageFolder setup | train/val ImageFolder + transforms from PRD 4.2 |
| L-1-2 | Stratified subset | 10% per-class sampling, seeded |
| L-1-3 | Calibration loader | 1024-sample loader for PTQ |
| L-1-4 | Val loader | full ~50K val set, batch_size=cfg.batch_size |

---

## A-2: Compression Primitives [Complexity: 12, Budget: 12]

**Applied**: torch.nn.utils.prune (global L1 unstructured) + torch.quantization (PTQ, fbgemm)

```python
def apply_pruning(model: nn.Module, amount: float = 0.5) -> nn.Module:
    """Global L1 unstructured pruning on all Conv2d weights. In-place, returns model."""
    ...

def remove_pruning_reparam(model: nn.Module) -> nn.Module:
    """Calls prune.remove() per pruned module to make sparsity permanent (removes weight_mask)."""
    ...

def apply_quantization(model: nn.Module, calib_loader: DataLoader,
                        n_calib_samples: int) -> nn.Module:
    """PTQ static quantization, fbgemm backend. Fuses conv+bn+relu, calibrates, converts."""
    ...

def get_layer_sparsity(model: nn.Module) -> dict[str, float]:
    """Per-Conv2d-layer name -> fraction of zero weights. For h-m1 CSV export."""
    ...
```

### Pseudo-code: apply_pruning

```
1. modules_to_prune = [(m, "weight") for m in model.modules() if isinstance(m, nn.Conv2d)]
2. prune.global_unstructured(modules_to_prune, pruning_method=prune.L1Unstructured, amount=amount)
3. return model  # weight_mask + weight_orig buffers added, use remove_pruning_reparam() to finalize
```

### Pseudo-code: apply_quantization

```
1. model.eval(); model.qconfig = torch.quantization.get_default_qconfig("fbgemm")
2. torch.quantization.fuse_modules(model, [conv+bn+relu groups])  # resnet18 basic blocks
3. torch.quantization.prepare(model, inplace=True)
4. for i, (x, _) in enumerate(calib_loader):
       if i >= n_calib_samples: break
       model(x)  # [1, 3, 224, 224] -> observer stats collected
5. torch.quantization.convert(model, inplace=True)
6. return model
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Global L1 pruning | `apply_pruning` via `prune.global_unstructured` |
| L-2-2 | Prune reparam removal | `remove_pruning_reparam`, permanent sparsity |
| L-2-3 | PTQ fbgemm pipeline | fuse -> prepare -> calibrate -> convert |
| L-2-4 | Layer sparsity extraction | `get_layer_sparsity` dict, zero-count / numel per Conv2d |

---

## A-3: Prune-First Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch (compose A-2 primitives + train.finetune)

```python
def run_prune_first(model: nn.Module, cfg: Config, seed: int,
                     train_loader: DataLoader, calib_loader: DataLoader) -> nn.Module:
    """prune -> finetune -> quantize. Returns final quantized model."""
    ...
```

```
1. set_seed(seed)
2. model = apply_pruning(model, cfg.prune_amount)
3. model = finetune(model, train_loader, cfg)
4. model = remove_pruning_reparam(model)
5. model = apply_quantization(model, calib_loader, cfg.calibration_samples)
6. return model
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Prune step | call `apply_pruning` |
| L-3-2 | Finetune step | call `finetune`, 5 epochs |
| L-3-3 | Reparam + checkpoint | `remove_pruning_reparam`, save checkpoint |
| L-3-4 | Quantize step | call `apply_quantization`, save final checkpoint |

---

## A-4: Quantize-First Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch (compose A-2 primitives + train.finetune)

```python
def run_quantize_first(model: nn.Module, cfg: Config, seed: int,
                        train_loader: DataLoader, calib_loader: DataLoader) -> nn.Module:
    """quantize -> prune -> finetune. Returns final model."""
    ...
```

```
1. set_seed(seed)
2. model = apply_quantization(model, calib_loader, cfg.calibration_samples)
3. model = apply_pruning(model, cfg.prune_amount)  # prune quantized weights
4. model = finetune(model, train_loader, cfg)
5. model = remove_pruning_reparam(model)
6. return model
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Quantize step | call `apply_quantization`, save checkpoint |
| L-4-2 | Prune step | call `apply_pruning` on quantized weights |
| L-4-3 | Finetune step | call `finetune`, 5 epochs |
| L-4-4 | Reparam + checkpoint | `remove_pruning_reparam`, save final checkpoint |

---

## A-5: Multi-Seed Runner [Complexity: 7, Budget: 7]

**Applied**: Standard train/eval script pattern

```python
def set_seed(seed: int) -> None:
    """Sets torch, numpy, CUDA seeds + deterministic flags."""
    ...

def finetune(model: nn.Module, loader: DataLoader, cfg: Config) -> nn.Module:
    """cfg.finetune_epochs epochs, Adam(lr=cfg.lr). Returns trained model."""
    ...

def evaluate(model: nn.Module, val_loader: DataLoader) -> dict:
    """Runs torchmetrics Accuracy(top_k=1,5). Returns {"top1": float, "top5": float}."""
    ...

def main() -> None:
    """Loop 2 orderings x 3 seeds -> 6 runs. Saves checkpoints + results.json per run."""
    ...
```

### Pseudo-code: main

```
1. cfg = Config(); train_loader, calib_loader, val_loader = load_data(cfg)
2. for ordering in ["prune_first", "quantize_first"]:
3.     for seed in cfg.seeds:
4.         model = resnet18(weights="IMAGENET1K_V1")
5.         run_fn = run_prune_first if ordering == "prune_first" else run_quantize_first
6.         model = run_fn(model, cfg, seed, train_loader, calib_loader)
7.         metrics = evaluate(model, val_loader)
8.         sparsity = get_layer_sparsity(model)
9.         save_json({"ordering": ordering, "seed": seed, **metrics, "sparsity": sparsity},
                      f"{cfg.output_dir}/{ordering}_seed{seed}/results.json")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | set_seed | torch/numpy/cuda seeding + deterministic mode |
| L-5-2 | finetune loop | Adam optimizer, cfg.finetune_epochs, log per-epoch acc |
| L-5-3 | evaluate | torchmetrics top1/top5 on val_loader |
| L-5-4 | main orchestration | 6-run loop, checkpoint + results.json per run |

---

## A-6: Statistical Analysis [Complexity: 6, Budget: 6]

**Applied**: scipy.stats.ttest_rel (paired t-test)

```python
def load_results(output_dir: str) -> pd.DataFrame:
    """Reads all results.json into DataFrame: [ordering, seed, top1, top5]."""
    ...

def paired_ttest(prune_first: list[float], quant_first: list[float]) -> dict:
    """scipy.stats.ttest_rel. Returns {"t_stat": float, "p_value": float, "effect_size": float}."""
    ...

def gate_decision(stats: dict) -> str:
    """PASS if abs(effect_size) > 0.5 and p_value < 0.05, else FAIL."""
    ...

def export_layer_sparsity_csv(runs: list[dict], path: str) -> None:
    """Flattens per-run sparsity dicts to CSV: [ordering, seed, layer_name, sparsity]."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | load_results | aggregate 6 results.json -> DataFrame |
| L-6-2 | paired_ttest | `scipy.stats.ttest_rel` on top1 lists, compute effect_size = mean diff |
| L-6-3 | gate_decision | threshold check per PRD section 6 |
| L-6-4 | export_layer_sparsity_csv | for h-m1 downstream consumption |

---

## Notes

- Green-field project, no external hypothesis dependencies.
- `resnet18` used directly from torchvision; no custom `model.py`.
