# Logic: H-M2 Post-Crystallization Feature Commitment (MECHANISM/FULL)

Applied: PyTorch `register_forward_hook` pattern for penultimate-layer feature extraction
Applied: Linear probe training pattern from Kirichenko et al. (2023)

## Codebase Analysis (Serena)

**Project Type**: incremental_hypothesis (base: h-m1)
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/{model,data,config}.py`
**Relevant Symbols**:
- `data.get_loaders(name, batch_size) -> dict[str, DataLoader]`
- `model.build_resnet50(num_classes, pretrained) -> nn.Module`
- `config.Config` dataclass, `CONFIG` instance

**Discrepancy vs spec**: Experiment brief shows metadata access as `metadata[:,0]` for group, but Waterbirds metadata structure is `[group_id]` (single column). Core label = y (bird type), spurious label derived from group_id mapping.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/data.py (ACTUAL CODE)
def get_loaders(name: str, batch_size: int = 128) -> dict[str, DataLoader]:
    """Returns {'train','val','test'}. Batch: (x [B,3,224,224], y [B], metadata [B,1])."""
    ...

# From: h-m1/code/model.py (ACTUAL CODE)
def build_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50, model.fc = Linear(2048, num_classes)."""
    ...

# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    lr: float = 1e-3
    batch_size: int = 128
    seed: int = 42
    epochs_waterbirds: int = 100
    checkpoint_dir: str = "./checkpoints"
    ...
```

**Verified from**: `h-m1/code/*.py` (actual implementation).

---

## A-1: Feature Extraction Mechanism [Complexity: 8, Budget: 8]

**Applied**: PyTorch forward-hook feature extraction pattern

### API Signatures

```python
# feature_extractor.py
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader

class FeatureExtractor:
    """Extracts penultimate-layer features via forward hook."""

    def __init__(self, model: nn.Module, layer_name: str = "avgpool"):
        """Register hook on model.avgpool (before fc)."""
        self.features: Tensor | None = None
        self._hook_handle = getattr(model, layer_name).register_forward_hook(self._hook)

    def _hook(self, module: nn.Module, input: tuple, output: Tensor) -> None:
        """Captures avgpool output [B, 2048, 1, 1] -> [B, 2048]."""
        self.features = output.view(output.size(0), -1).detach()

    def extract_batch(self, model: nn.Module, x: Tensor) -> Tensor:
        """Forward pass, return captured features [B, 2048]."""
        with torch.no_grad():
            _ = model(x)
        return self.features

    def extract_dataset(self, model: nn.Module, dataloader: DataLoader, 
                        device: str) -> tuple[Tensor, Tensor, Tensor]:
        """Extract features for entire dataset.
        Returns (features [N, 2048], core_labels [N], spurious_labels [N])."""
        ...

    def remove(self) -> None:
        """Detach hook."""
        self._hook_handle.remove()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| avgpool output | [B, 2048, 1, 1] | Raw hook output |
| features | [B, 2048] | After view() flatten |
| core_labels (y) | [B] | Bird type: 0=landbird, 1=waterbird |
| metadata | [B, 1] | Group ID: 0-3 |
| spurious_labels | [B] | Derived: group % 2 (background) |

### Pseudo-code

```
extract_dataset(model, dataloader, device):
    model.eval()
    all_features, all_core, all_spurious = [], [], []
    for x, y, metadata in dataloader:
        x = x.to(device)
        features = extract_batch(model, x)  # [B, 2048]
        all_features.append(features.cpu())
        all_core.append(y)  # Bird type
        # Derive spurious label from group_id
        # Group 0,2 = land background, Group 1,3 = water background
        spurious = (metadata[:, 0] % 2)  # 0=land, 1=water
        all_spurious.append(spurious)
    return (cat(all_features), cat(all_core), cat(all_spurious))
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Hook registration | `__init__`: register hook on `model.avgpool`, store handle |
| L-1-2 | Batch extraction | `extract_batch`: forward pass with no_grad, return flattened features |
| L-1-3 | Dataset extraction | `extract_dataset`: iterate dataloader, derive spurious labels from group_id |

---

## A-2: Linear Probe Training [Complexity: 6, Budget: 6]

**Applied**: Standard linear classifier pattern from transfer learning

### API Signatures

```python
# probe.py
import torch
from torch import nn, Tensor
import torch.nn.functional as F

class LinearProbe(nn.Module):
    """Single linear layer for probing representations."""

    def __init__(self, input_dim: int = 2048, num_classes: int = 2):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, input_dim] -> logits [B, num_classes]."""
        return self.fc(x)


def train_probe(probe: LinearProbe, features: Tensor, labels: Tensor,
                lr: float = 0.01, iterations: int = 100, device: str = "cuda") -> LinearProbe:
    """Train probe from scratch using SGD.
    Args:
        features: [N, 2048] float tensor
        labels: [N] long tensor
    Returns:
        Trained probe.
    """
    ...


def evaluate_probe(probe: LinearProbe, features: Tensor, labels: Tensor,
                   device: str = "cuda") -> float:
    """Compute accuracy.
    Returns: accuracy in [0, 1]."""
    ...
```

### Pseudo-code

```
train_probe(probe, features, labels, lr, iterations, device):
    probe.train()
    probe.to(device)
    features, labels = features.to(device), labels.to(device)
    optimizer = SGD(probe.parameters(), lr=lr)
    for _ in range(iterations):
        logits = probe(features)
        loss = cross_entropy(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return probe

evaluate_probe(probe, features, labels, device):
    probe.eval()
    with no_grad():
        logits = probe(features.to(device))
        preds = logits.argmax(dim=1)
        acc = (preds == labels.to(device)).float().mean()
    return acc.item()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | LinearProbe class | `__init__`, `forward`: single Linear layer wrapper |
| L-2-2 | train_probe | SGD training loop, cross-entropy loss, no momentum |
| L-2-3 | evaluate_probe | Inference accuracy computation |

---

## A-3: Probe Analyzer Orchestration [Complexity: 10, Budget: 10]

**Applied**: Checkpoint iteration + temporal tracking pattern

### API Signatures

```python
# analyzer.py
import torch
from torch import nn
from torch.utils.data import DataLoader
from feature_extractor import FeatureExtractor
from probe import LinearProbe, train_probe, evaluate_probe

class FeatureProbeAnalyzer:
    """Orchestrates temporal probe analysis across checkpoints."""

    def __init__(self, model_builder: callable, checkpoint_dir: str,
                 crystallization_epoch: int, final_epoch: int,
                 hidden_dim: int = 2048, probe_lr: float = 0.01,
                 probe_iterations: int = 100):
        self.model_builder = model_builder
        self.checkpoint_dir = checkpoint_dir
        self.crystallization_epoch = crystallization_epoch
        self.final_epoch = final_epoch
        self.hidden_dim = hidden_dim
        self.probe_lr = probe_lr
        self.probe_iterations = probe_iterations
        
        self.spurious_acc_history: list[float] = []
        self.core_acc_history: list[float] = []
        self.epochs_analyzed: list[int] = []

    def analyze_checkpoint(self, epoch: int, val_loader: DataLoader,
                           test_loader: DataLoader, device: str) -> dict:
        """Load checkpoint, extract features, train probes on val, evaluate on test.
        Returns {'epoch', 'spurious_acc', 'core_acc'}."""
        ...

    def analyze_all(self, val_loader: DataLoader, test_loader: DataLoader,
                    device: str) -> dict:
        """Iterate checkpoints crystallization_epoch to final_epoch.
        Returns {'spurious_history': [...], 'core_history': [...], 'epochs': [...]}."""
        ...

    def get_history(self) -> dict:
        """Returns accumulated history for commitment analysis."""
        return {
            'spurious_acc_history': self.spurious_acc_history,
            'core_acc_history': self.core_acc_history,
            'epochs': self.epochs_analyzed
        }
```

### Pseudo-code

```
analyze_checkpoint(epoch, val_loader, test_loader, device):
    # Load model checkpoint
    model = self.model_builder()
    ckpt_path = f"{self.checkpoint_dir}/epoch_{epoch}.pt"
    model.load_state_dict(torch.load(ckpt_path)['model_state_dict'])
    model.to(device)
    model.eval()
    
    # Extract features
    extractor = FeatureExtractor(model)
    val_feats, val_core, val_spurious = extractor.extract_dataset(model, val_loader, device)
    test_feats, test_core, test_spurious = extractor.extract_dataset(model, test_loader, device)
    extractor.remove()
    
    # Train probes on validation, evaluate on test
    spurious_probe = LinearProbe(self.hidden_dim, 2)
    train_probe(spurious_probe, val_feats, val_spurious, self.probe_lr, self.probe_iterations, device)
    spurious_acc = evaluate_probe(spurious_probe, test_feats, test_spurious, device)
    
    core_probe = LinearProbe(self.hidden_dim, 2)
    train_probe(core_probe, val_feats, val_core, self.probe_lr, self.probe_iterations, device)
    core_acc = evaluate_probe(core_probe, test_feats, test_core, device)
    
    return {'epoch': epoch, 'spurious_acc': spurious_acc, 'core_acc': core_acc}

analyze_all(val_loader, test_loader, device):
    for epoch in range(self.crystallization_epoch, self.final_epoch + 1):
        result = analyze_checkpoint(epoch, val_loader, test_loader, device)
        self.spurious_acc_history.append(result['spurious_acc'])
        self.core_acc_history.append(result['core_acc'])
        self.epochs_analyzed.append(epoch)
    return self.get_history()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Checkpoint loading | Load model state dict, handle missing keys |
| L-3-2 | Per-checkpoint analysis | `analyze_checkpoint`: extract, train, evaluate |
| L-3-3 | Temporal iteration | `analyze_all`: loop crystallization to final |
| L-3-4 | History management | Store and return accumulated probe accuracies |

---

## A-4: Commitment Detection [Complexity: 5, Budget: 5]

**Applied**: Statistical trend analysis

### API Signatures

```python
# commitment.py
import numpy as np

def check_commitment(spurious_acc_history: list[float], core_acc_history: list[float],
                     noise_margin: float = 0.02, core_threshold: float = 0.85) -> dict:
    """Evaluate commitment criteria.
    Returns {
        'committed': bool,           # spurious_acc stable/increasing
        'core_suppressed': bool,     # final core_acc < threshold
        'spurious_trend': str,       # 'increasing'|'stable'|'decreasing'
        'core_final': float,
        'spurious_final': float,
        'spurious_initial': float,
        'gate_pass': bool
    }."""
    ...

def compute_trend(history: list[float], noise_margin: float = 0.02) -> str:
    """Analyze trend: 'increasing', 'stable', or 'decreasing'.
    Uses first vs last comparison with noise margin."""
    ...
```

### Pseudo-code

```
check_commitment(spurious_history, core_history, noise_margin, core_threshold):
    if len(spurious_history) < 2:
        return {'committed': None, 'gate_pass': None, 'error': 'insufficient_data'}
    
    spurious_initial = spurious_history[0]
    spurious_final = spurious_history[-1]
    core_final = core_history[-1]
    
    # Commitment = spurious accuracy did not decrease beyond noise margin
    committed = (spurious_final >= spurious_initial - noise_margin)
    
    # Core suppression = core accuracy below threshold
    core_suppressed = (core_final < core_threshold)
    
    # Trend analysis
    spurious_trend = compute_trend(spurious_history, noise_margin)
    
    # Gate pass = committed (primary criterion)
    gate_pass = committed
    
    return {
        'committed': committed,
        'core_suppressed': core_suppressed,
        'spurious_trend': spurious_trend,
        'core_final': core_final,
        'spurious_final': spurious_final,
        'spurious_initial': spurious_initial,
        'gate_pass': gate_pass
    }

compute_trend(history, noise_margin):
    if len(history) < 2:
        return 'unknown'
    delta = history[-1] - history[0]
    if delta > noise_margin:
        return 'increasing'
    elif delta < -noise_margin:
        return 'decreasing'
    else:
        return 'stable'
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | check_commitment | Main commitment logic with noise margin |
| L-4-2 | compute_trend | First-to-last trend analysis |

---

## A-5: Visualization [Complexity: 6, Budget: 6]

**Applied**: matplotlib dual-axis + annotation patterns

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt

def plot_probe_accuracy_timeline(spurious_history: list[float], core_history: list[float],
                                  epochs: list[int], crystallization_epoch: int,
                                  save_path: str) -> None:
    """Dual-line plot: spurious vs core probe accuracy over epochs.
    Vertical line at crystallization epoch."""
    ...

def plot_gate_metrics_comparison(commitment_result: dict, save_path: str) -> None:
    """REQUIRED gate figure: bar chart comparing spurious_initial vs spurious_final,
    annotated with commitment status."""
    ...

def plot_commitment_summary(spurious_history: list[float], core_history: list[float],
                            epochs: list[int], commitment_result: dict,
                            save_path: str) -> None:
    """Combined summary figure with trend annotations."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Timeline plot | `plot_probe_accuracy_timeline` -> `figures/probe_timeline.png` |
| L-5-2 | Gate figure | `plot_gate_metrics_comparison` -> `figures/gate_comparison.png` |
| L-5-3 | Summary figure | `plot_commitment_summary` -> `figures/commitment_summary.png` |

---

## Total Subtasks: 17/30 budget used (FULL tier)
