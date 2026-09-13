# Logic Design: H-E1

**Type:** EXISTENCE (PoC) | **Budget:** 0 subtasks (all modules low complexity)

Applied: torchvision-dataset-transform-pipeline-pattern
Applied: standard-pytorch-sgd-multisteplr-training-loop

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field implementation - new API design, no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: torchvision-dataset-transform-pipeline-pattern

### API Signatures

```python
# data.py
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

def get_transforms(train: bool, mean: tuple[float, float, float], std: tuple[float, float, float]) -> transforms.Compose:
    """Train: RandomCrop+Flip+Normalize. Eval: Normalize only."""
    ...

def load_cifar10(root: str, mean: tuple, std: tuple) -> tuple[Dataset, Dataset]:
    """Returns (train, test)."""
    ...

def load_cinic10(root: str, mean: tuple, std: tuple) -> Dataset:
    """ImageFolder over manually-downloaded CINIC-10 test split. root/cinic-10/test/"""
    ...

def load_svhn(root: str, mean: tuple, std: tuple) -> tuple[Dataset, Dataset, Dataset]:
    """Returns (train, test, extra). SVHN labels: 10 maps to class 0."""
    ...

def sample_svhn_extra(dataset: Dataset, n: int, seed: int) -> Dataset:
    """torch.utils.data.Subset with np.random.RandomState(seed).choice(len(dataset), n, replace=False)."""
    ...

def make_loader(dataset: Dataset, batch_size: int, shuffle: bool) -> DataLoader:
    """num_workers=4, pin_memory=True."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| image (per-sample) | [3, 32, 32] | RGB, post-transform |
| batch x | [B, 3, 32, 32] | B=128 |
| batch y | [B] | int64 class labels 0-9 |

### Notes
- CINIC-10 requires manual download to `root/cinic-10/`; use `torchvision.datasets.ImageFolder(root/cinic-10/test)`.
- CIFAR-10 normalization from config; SVHN uses same normalization stats (per PRD, single `cifar10_norm` constant reused — no separate SVHN stats specified, apply identically).

---

## A-2: Model Module [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch (torchvision.models.resnet18)

### API Signatures

```python
# model.py
import torch.nn as nn

def build_resnet18(num_classes: int = 10) -> nn.Module:
    """torchvision.models.resnet18(weights=None) with fc replaced. x: [B,3,32,32] -> [B,num_classes]"""
    ...
```

---

## A-3: Training Loop [Complexity: 7, Budget: 7]

**Applied**: standard-pytorch-sgd-multisteplr-training-loop

### API Signatures

```python
# train.py
import torch
from torch.utils.data import DataLoader

def train_epoch(model: nn.Module, loader: DataLoader, optimizer: torch.optim.Optimizer,
                 criterion: nn.Module, device: torch.device) -> tuple[float, float]:
    """One epoch. Returns (avg_loss, train_acc_pct)."""
    ...

def train_one_condition(condition: str, config: dict) -> str:
    """condition in {"cifar10", "svhn"}. Builds model/data/optimizer/scheduler,
    runs config['epochs'] epochs, saves checkpoint, returns checkpoint path.
    Also writes per-epoch history to checkpoints/{condition}_history.json."""
    ...

def main() -> None:
    """CLI entry: parse --condition, call train_one_condition."""
    ...
```

### Pseudo-code

```
train_one_condition(condition, config):
    set_seed(config['seed'])
    model = build_resnet18(10).to(device)
    train_ds, test_ds = load_cifar10(...) if condition=="cifar10" else load_svhn(...)[:2]
    train_loader = make_loader(train_ds, config['batch_size'], shuffle=True)
    optimizer = SGD(model.parameters(), lr=config['lr'], momentum=config['momentum'], weight_decay=config['weight_decay'])
    scheduler = MultiStepLR(optimizer, milestones=config['lr_milestones'], gamma=config['lr_gamma'])
    history = []
    for epoch in range(config['epochs']):
        loss, acc = train_epoch(model, train_loader, optimizer, CrossEntropyLoss(), device)
        scheduler.step()
        history.append({"epoch": epoch, "loss": loss, "acc": acc})
    save checkpoint to checkpoints/{condition}.pt
    save history to checkpoints/{condition}_history.json
    return checkpoint_path
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| output | [B, 10] | logits |
| loss | scalar | CrossEntropyLoss |

---

## A-4: Run Both Training Conditions [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch (orchestration, no new pattern)

### API Signatures

```python
# invoked via train.main() per condition, or directly:
def run_all_training(config: dict) -> dict[str, str]:
    """Calls train_one_condition for 'cifar10' and 'svhn'. Returns {condition: checkpoint_path}."""
    ...
```

Reuses `train_one_condition` from A-3; no new module needed beyond a loop over `["cifar10", "svhn"]`.

---

## A-5: Evaluation + Gap Computation [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch (torchmetrics Accuracy)

### API Signatures

```python
# evaluate.py
import torch
from torch.utils.data import DataLoader

def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    """model.eval(), no_grad. Returns accuracy in percent (0-100)."""
    ...

def compute_generalization_gap(model: nn.Module, in_domain_loader: DataLoader,
                                 held_out_loader: DataLoader, device: torch.device) -> dict:
    """Returns {"in_domain_acc": float, "held_out_acc": float, "gap": float}.
    gap = in_domain_acc - held_out_acc"""
    ...
```

---

## A-6: Statistical Comparison [Complexity: 4, Budget: 4]

**Applied**: Standard scipy.stats

### API Signatures

```python
# stats.py
def cohens_d(a: list[float], b: list[float]) -> float:
    """Pooled-std Cohen's d: (mean(a)-mean(b)) / pooled_std."""
    ...

def compare_gaps(gaps_high: list[float], gaps_low: list[float]) -> dict:
    """Returns {"d": float, "t": float, "p": float}. Uses scipy.stats.ttest_ind."""
    ...
```

Note: PoC uses single seed -> `gaps_high`/`gaps_low` are single-element lists. Cohen's d/t-test on n=1 each is degenerate (std undefined); PoC gate primarily checks direction (`gap_high > gap_low`) per PRD FR success criteria. Compute d/p defensively (return `nan` if variance undefined) and report alongside direction check.

---

## A-7: Visualization [Complexity: 5, Budget: 5]

**Applied**: Standard matplotlib

### API Signatures

```python
# visualize.py
def plot_gap_comparison(gap_high: float, gap_low: float, out_path: str) -> None:
    """Bar chart, 2 bars (high-use, low-use), saved to out_path."""
    ...

def plot_accuracy_comparison(results: dict, out_path: str) -> None:
    """results: {"cifar10": {"in_domain_acc":.., "held_out_acc":..}, "svhn": {...}}.
    Grouped bar chart."""
    ...

def plot_training_curves(history: dict, out_path: str) -> None:
    """history: {"cifar10": [{"epoch","loss","acc"},...], "svhn": [...]}.
    Line plot, loss+acc subplots."""
    ...
```

---

## A-8: End-to-End Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch (orchestration script)

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """
    1. Load CONFIG from config.py
    2. ckpts = run_all_training(CONFIG)  # A-4
    3. Build eval loaders (in-domain test + held-out) per condition
    4. gap_high = compute_generalization_gap(cifar10_model, cifar10_test_loader, cinic10_loader, device)
    5. gap_low = compute_generalization_gap(svhn_model, svhn_test_loader, svhn_extra_loader, device)
    6. stats = compare_gaps([gap_high['gap']], [gap_low['gap']])
    7. plot_gap_comparison, plot_accuracy_comparison, plot_training_curves -> figures/
    8. Write results.json: {gap_high, gap_low, stats, poc_pass: gap_high['gap'] > gap_low['gap']}
    """
    ...
```

### Tensor Shapes (results.json structure)

| Key | Type | Note |
|-----|------|------|
| results["cifar10"]["gap"] | float | in_domain_acc - held_out_acc |
| results["svhn"]["gap"] | float | in_domain_acc - held_out_acc |
| results["stats"] | dict | {d, t, p} |
| results["poc_pass"] | bool | gap_high > gap_low |
