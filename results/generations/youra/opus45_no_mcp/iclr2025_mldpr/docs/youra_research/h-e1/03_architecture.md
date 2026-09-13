# Architecture: H-E1

**Type:** EXISTENCE (PoC)
**Date:** 2026-08-19

Applied: standard-pytorch-training-loop-pattern
Applied: torchvision-dataset-transform-pipeline-pattern

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field implementation - no existing code
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis or existing codebase to analyze.

---

## Module Structure

### data.py

```python
def get_transforms(train: bool, normalize_mean: tuple, normalize_std: tuple) -> transforms.Compose: ...
def load_cifar10(root: str) -> tuple[Dataset, Dataset]: ...
def load_cinic10(root: str) -> Dataset: ...
def load_svhn(root: str) -> tuple[Dataset, Dataset, Dataset]: ...
def sample_svhn_extra(dataset: Dataset, n: int, seed: int) -> Dataset: ...
def make_loader(dataset: Dataset, batch_size: int, shuffle: bool) -> DataLoader: ...
```

### model.py

```python
def build_resnet18(num_classes: int = 10) -> nn.Module: ...
```

### train.py

**Dependencies**: data, model, config

```python
def train_one_condition(condition: str, config: dict) -> str:  # returns checkpoint path
def train_epoch(model, loader, optimizer, criterion, device) -> tuple[float, float]: ...
def main() -> None: ...
```

### evaluate.py

**Dependencies**: data, model

```python
def evaluate(model: nn.Module, loader: DataLoader, device) -> float:  # accuracy %
def compute_generalization_gap(model, in_domain_loader, held_out_loader, device) -> dict: ...
```

### stats.py

**Dependencies**: scipy

```python
def cohens_d(a: list[float], b: list[float]) -> float: ...
def compare_gaps(gaps_high: list[float], gaps_low: list[float]) -> dict:  # {d, t, p}
```

### visualize.py

**Dependencies**: matplotlib

```python
def plot_gap_comparison(gap_high: float, gap_low: float, out_path: str) -> None: ...
def plot_accuracy_comparison(results: dict, out_path: str) -> None: ...
def plot_training_curves(history: dict, out_path: str) -> None: ...
```

### config.py

```python
CONFIG = {
    "seed": 42,
    "batch_size": 128,
    "epochs": 200,
    "lr": 0.1,
    "momentum": 0.9,
    "weight_decay": 5e-4,
    "lr_milestones": [100, 150],
    "lr_gamma": 0.1,
    "cifar10_norm": ((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
}
```

### run_experiment.py

**Dependencies**: train, evaluate, stats, visualize, config

```python
def main() -> None:  # orchestrates: train both -> eval both -> stats -> figures -> save results.json
```

---

## File Organization

```
code/
  config.py
  data.py
  model.py
  train.py
  evaluate.py
  stats.py
  visualize.py
  run_experiment.py
data/            # downloaded datasets (gitignored)
checkpoints/     # saved model .pt files
figures/         # output plots
results.json     # final metrics + gate check
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load CIFAR-10, SVHN, SVHN-Extra, CINIC-10 (manual) with transforms/loaders | 8 | 3+2+2+1 |
| A-2 | Model module | ResNet-18 builder with 10-class head | 3 | 1+1+1+0 |
| A-3 | Training loop | SGD+MultiStepLR training loop for one condition, checkpointing | 7 | 2+2+2+1 |
| A-4 | Run both training conditions | Execute training for CIFAR-10 and SVHN, save checkpoints + loss/acc history | 6 | 2+2+1+1 |
| A-5 | Evaluation + gap computation | Evaluate models on in-domain/held-out sets, compute generalization gaps | 5 | 2+2+1+0 |
| A-6 | Statistical comparison | Cohen's d + t-test on gap_high vs gap_low | 4 | 1+1+2+0 |
| A-7 | Visualization | Gap bar chart, accuracy comparison, training curves | 5 | 2+1+1+1 |
| A-8 | End-to-end orchestration | run_experiment.py wiring all modules, results.json, PoC gate check | 6 | 2+3+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7, A-8], VeryLow(1-3): [A-2]
