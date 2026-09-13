# Config: H-E1 Compression Ordering Effect Existence

**Type**: EXISTENCE (PoC) | **Tier**: LIGHT | **Applied**: Standard PyTorch dataclass config (no KB match; used pytorch/pytorch config.py as style reference)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1..A-6: Single Fixed Config [Complexity: LIGHT tier, Budget: 4 subtasks]

**Applied**: Standard PyTorch dataclass defaults, all values fixed from PRD (no tuning/grid for EXISTENCE test)

### Configuration (Python Dataclass)

```python
# config.py
from dataclasses import dataclass, field

@dataclass
class Config:
    # Reproducibility
    seeds: tuple[int, ...] = (42, 123, 456)

    # Compression
    prune_amount: float = 0.5          # global unstructured L1, Conv2d only
    quant_backend: str = "fbgemm"      # x86 PTQ backend
    calibration_samples: int = 1024

    # Fine-tuning
    finetune_epochs: int = 5
    batch_size: int = 64
    lr: float = 1e-4

    # Data
    data_root: str = "./data"
    train_fraction: float = 0.1        # 10% stratified subset
    image_size: int = 224
    resize_size: int = 256             # val resize-before-crop
    num_workers: int = 8

    # Normalization (ImageNet stats)
    norm_mean: tuple[float, ...] = (0.485, 0.456, 0.406)
    norm_std: tuple[float, ...] = (0.229, 0.224, 0.225)

    # Output
    output_dir: str = "./results"
    checkpoint_dir: str = "./results/checkpoints"

    # Stats
    alpha: float = 0.05                # significance threshold for gate
    effect_size_threshold: float = 0.5 # percentage points
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Data pipeline | ImageNet 10% stratified train subset, full val loader, calibration loader (A-1) |
| C-2 | Compression primitives | Global L1 pruning + fbgemm PTQ + sparsity extraction (A-2) |
| C-3 | Ordering pipelines | prune->finetune->quantize and quantize->prune->finetune (A-3, A-4) |
| C-4 | Run + analyze | 6-run orchestration + paired t-test + gate decision (A-5, A-6) |

---

## Notes

- No hyperparameter search: PRD fixes all compression/training values directly.
- `train_fraction=0.1` and `finetune_epochs=5` are PRD-specified, not tuned.
- 3 seeds is the full PRD requirement (not a subset/sample).
