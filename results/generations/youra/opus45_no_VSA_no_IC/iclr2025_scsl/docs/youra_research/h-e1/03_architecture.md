# Architecture: H-E1 Compression Ordering Effect Existence

**Type**: EXISTENCE (PoC) | **Tier**: LIGHT | **Applied**: Standard train/eval script pattern (KB: pytorch-labs/ao quantization+pruning composition)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
experiments/h_e1_ordering_effect/
├── config.py
├── compression.py
├── pipeline.py
├── train.py
├── analyze_results.py
└── requirements.txt
```

No `model.py` needed — uses `torchvision.models.resnet18` directly (no architecture modification, only weight-level pruning/quantization).

---

## Modules

### config.py

**Dependencies**: none

```python
@dataclass
class Config:
    seeds: list[int] = (42, 123, 456)
    prune_amount: float = 0.5
    calibration_samples: int = 1024
    finetune_epochs: int = 5
    batch_size: int = 64
    lr: float = 1e-4
    data_root: str = "./data"
    train_fraction: float = 0.1
    output_dir: str = "./results"
```

### compression.py

**Dependencies**: torch, torchvision

```python
def apply_pruning(model: nn.Module, amount: float = 0.5) -> nn.Module: ...
def remove_pruning_reparam(model: nn.Module) -> nn.Module: ...  # make sparsity permanent
def apply_quantization(model: nn.Module, calib_loader: DataLoader,
                        n_calib_samples: int) -> nn.Module: ...
def get_layer_sparsity(model: nn.Module) -> dict[str, float]: ...  # for h-m1 CSV
```

### pipeline.py

**Dependencies**: compression, config

```python
def run_prune_first(model: nn.Module, cfg: Config, seed: int,
                     train_loader, calib_loader) -> nn.Module: ...
def run_quantize_first(model: nn.Module, cfg: Config, seed: int,
                        train_loader, calib_loader) -> nn.Module: ...
```

### train.py

**Dependencies**: pipeline, compression, config, torchmetrics

```python
def load_data(cfg: Config) -> tuple[DataLoader, DataLoader, DataLoader]:
    ... # train_subset, calib, val

def finetune(model: nn.Module, loader: DataLoader, cfg: Config) -> nn.Module: ...

def evaluate(model: nn.Module, val_loader: DataLoader) -> dict:
    ... # {"top1": float, "top5": float}

def set_seed(seed: int) -> None: ...

def main() -> None:
    ... # loop over 2 orderings x 3 seeds, save checkpoints + per-run results.json
```

### analyze_results.py

**Dependencies**: scipy, numpy

```python
def load_results(output_dir: str) -> pd.DataFrame: ...
def paired_ttest(prune_first: list[float], quant_first: list[float]) -> dict:
    ... # {"t_stat", "p_value", "effect_size"}
def gate_decision(stats: dict) -> str:  # "PASS" | "FAIL"
    ...
def export_layer_sparsity_csv(runs: list[dict], path: str) -> None: ...  # for h-m1
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | ImageNet 10% train subset, val loader, calibration loader | 9 | 2+2+3+2 |
| A-2 | Compression primitives | Global L1 pruning + INT8 PTQ (fbgemm), sparsity extraction | 12 | 3+2+4+3 |
| A-3 | Prune-first pipeline | Compose prune -> finetune -> quantize -> eval | 8 | 2+3+1+2 |
| A-4 | Quantize-first pipeline | Compose quantize -> prune -> finetune -> eval | 8 | 2+3+1+2 |
| A-5 | Multi-seed runner | 6-run orchestration (2 orderings x 3 seeds), checkpointing | 7 | 2+2+1+2 |
| A-6 | Statistical analysis | Paired t-test, effect size, gate decision, per-layer CSV export | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2], Low(4-8): [A-3, A-4, A-5, A-6]

---

## Dependencies

- torch>=2.0.0, torchvision>=0.15.0, torchmetrics>=1.0.0, numpy>=1.24.0, scipy>=1.10.0, pyyaml>=6.0, tqdm>=4.65.0
- Execution order: A-1, A-2 → A-3, A-4 (parallel) → A-5 → A-6
