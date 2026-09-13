# Logic Design: h-e1
# Horizontal Flip Augmentation Semantic Validity Study

**Date:** 2026-07-11
**Hypothesis:** h-e1 (EXISTENCE - PoC)
**Author:** Logic Agent (Phase 3)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - existing h-e1 code is for different hypothesis (SAM-SWA compressibility)
**Analyzed Path**: experiments/h-e1/ (contains SAM+DRO code, not flip augmentation)
**Relevant Symbols**: None - designing new APIs for flip augmentation experiment

**Note**: Existing h-e1 folder contains unrelated experiment. This is fresh implementation for flip augmentation semantic validity.

---

## A-1: Setup Project Structure [Complexity: 5, Budget: 4]

**Applied**: Standard Python project structure

### API Signatures

```python
# config.py
class ExperimentConfig:
    """Configuration constants."""
    # Model
    CONV1_OUT: int = 32
    CONV2_OUT: int = 64
    FC1_OUT: int = 128
    DROPOUT1: float = 0.25
    DROPOUT2: float = 0.5
    
    # Training
    BATCH_SIZE: int = 64
    EPOCHS: int = 14
    LR: float = 1.0
    STEP_SIZE: int = 1
    GAMMA: float = 0.7
    SEED: int = 42
    
    # Data
    MNIST_MEAN: float = 0.1307
    MNIST_STD: float = 0.3081
    
    # Symmetry groups
    SYMMETRIC_DIGITS: list = [0, 1, 8]
    ASYMMETRIC_DIGITS: list = [2, 3, 5, 6, 7, 9]
    
    # Conditions
    CONDITIONS: list = ["baseline", "flip30", "flip50", "flip90", "rotation"]
    
    # Paths
    OUTPUT_DIR: str = "docs/youra_research/h-e1"
    FIGURES_DIR: str = "docs/youra_research/h-e1/figures"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Create file structure | code/, figures/ directories |
| L-1-2 | Write config.py | Configuration constants |
| L-1-3 | Create __init__.py | Package initialization |
| L-1-4 | Setup imports | Verify torch, torchvision, matplotlib |

---

## A-2: Implement Data Pipeline [Complexity: 8, Budget: 4]

**Applied**: PyTorch transforms composition pattern

### API Signatures

```python
# data.py
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from typing import Tuple

def get_mnist_loaders(
    condition: str,
    batch_size: int = 64,
    data_root: str = "./data"
) -> Tuple[DataLoader, DataLoader]:
    """
    Get train/test dataloaders.
    
    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
    
    Returns:
        (train_loader, test_loader)
    """
    train_transform = get_transform(condition, train=True)
    test_transform = get_transform(condition, train=False)
    ...

def get_transform(condition: str, train: bool = True) -> transforms.Compose:
    """
    Get transform pipeline.
    
    Args:
        condition: Augmentation condition
        train: If False, return baseline transform (test always clean)
    
    Returns:
        Transform pipeline
    """
    base = [
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ]
    
    if not train:
        return transforms.Compose(base)
    
    if condition == "baseline":
        return transforms.Compose(base)
    elif condition.startswith("flip"):
        p = float(condition[4:]) / 100  # flip30 -> 0.3
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=p),
            *base
        ])
    elif condition == "rotation":
        return transforms.Compose([
            transforms.RandomRotation(degrees=15),
            *base
        ])
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Implement get_transform | Transform factory for 5 conditions |
| L-2-2 | Implement get_mnist_loaders | DataLoader creation |
| L-2-3 | Test augmentation | Verify flip applied correctly |
| L-2-4 | Validate splits | 60K train, 10K test |

---

## A-3: Implement Model + Training [Complexity: 10, Budget: 4]

**Applied**: PyTorch official MNIST example architecture

### API Signatures

```python
# model.py
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

class MNISTNet(nn.Module):
    """CNN from PyTorch official example."""
    
    def __init__(
        self,
        conv1_out: int = 32,
        conv2_out: int = 64,
        fc1_out: int = 128,
        dropout1: float = 0.25,
        dropout2: float = 0.5
    ):
        """Initialize layers."""
        super().__init__()
        self.conv1 = nn.Conv2d(1, conv1_out, kernel_size=3, stride=1)
        self.conv2 = nn.Conv2d(conv1_out, conv2_out, kernel_size=3, stride=1)
        self.dropout1 = nn.Dropout(dropout1)
        self.dropout2 = nn.Dropout(dropout2)
        self.fc1 = nn.Linear(9216, fc1_out)  # 64*12*12 after pooling
        self.fc2 = nn.Linear(fc1_out, 10)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        x: [B, 1, 28, 28] -> [B, 10] log_softmax
        """
        x = self.conv1(x)  # [B, 32, 26, 26]
        x = F.relu(x)
        x = self.conv2(x)  # [B, 64, 24, 24]
        x = F.relu(x)
        x = F.max_pool2d(x, 2)  # [B, 64, 12, 12]
        x = self.dropout1(x)
        x = torch.flatten(x, 1)  # [B, 9216]
        x = self.fc1(x)  # [B, 128]
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)  # [B, 10]
        return F.log_softmax(x, dim=1)
```

```python
# train.py
import torch
import torch.optim as optim
from typing import Dict
from torch.utils.data import DataLoader

def train_condition(
    condition: str,
    epochs: int = 14,
    lr: float = 1.0,
    seed: int = 42,
    device: str = "cuda"
) -> Dict:
    """
    Train model for single condition.
    
    Returns:
        {
            'model': trained_model,
            'train_losses': list of epoch losses,
            'test_accs': list of epoch accuracies
        }
    """
    torch.manual_seed(seed)
    model = MNISTNet().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.7)
    
    train_loader, test_loader = get_mnist_loaders(condition)
    
    train_losses = []
    test_accs = []
    
    for epoch in range(epochs):
        loss = train_epoch(model, train_loader, optimizer, device)
        acc = test_epoch(model, test_loader, device)
        scheduler.step()
        
        train_losses.append(loss)
        test_accs.append(acc)
    
    return {'model': model, 'train_losses': train_losses, 'test_accs': test_accs}

def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    device: str
) -> float:
    """Single epoch training. Returns average loss."""
    model.train()
    total_loss = 0.0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)  # [B, 10] log_softmax
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)

def test_epoch(
    model: nn.Module,
    test_loader: DataLoader,
    device: str
) -> float:
    """Single epoch evaluation. Returns accuracy (%)."""
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
    return 100.0 * correct / len(test_loader.dataset)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Implement MNISTNet | Conv layers + forward |
| L-3-2 | Implement train_epoch | Single epoch training loop |
| L-3-3 | Implement test_epoch | Evaluation loop |
| L-3-4 | Implement train_condition | End-to-end training orchestration |

---

## A-4: Implement Evaluation [Complexity: 7, Budget: 4]

**Applied**: Per-class accuracy computation pattern

### API Signatures

```python
# evaluate.py
import torch
import numpy as np
from typing import Dict
from torch.utils.data import DataLoader

def compute_per_class_accuracy(
    model: nn.Module,
    test_loader: DataLoader,
    device: str
) -> Dict:
    """
    Compute per-class accuracy.
    
    Returns:
        {
            'per_class': [acc_0, ..., acc_9],  # 10 floats
            'overall': float
        }
    """
    model.eval()
    class_correct = np.zeros(10)
    class_total = np.zeros(10)
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            
            for i in range(10):
                mask = (target == i)
                class_total[i] += mask.sum().item()
                class_correct[i] += (pred[mask] == i).sum().item()
    
    per_class = (class_correct / (class_total + 1e-8) * 100).tolist()
    overall = class_correct.sum() / class_total.sum() * 100
    
    return {'per_class': per_class, 'overall': overall}

def group_by_symmetry(per_class_acc: Dict) -> Dict:
    """
    Group accuracies by symmetry.
    
    Args:
        per_class_acc: Output from compute_per_class_accuracy
    
    Returns:
        {
            'symmetric_mean': float,
            'asymmetric_mean': float,
            'per_class': list
        }
    """
    per_class = per_class_acc['per_class']
    symmetric = [per_class[i] for i in [0, 1, 8]]
    asymmetric = [per_class[i] for i in [2, 3, 5, 6, 7, 9]]
    
    return {
        'symmetric_mean': np.mean(symmetric),
        'asymmetric_mean': np.mean(asymmetric),
        'per_class': per_class,
        'overall': per_class_acc['overall']
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Implement compute_per_class_accuracy | Per-class metrics |
| L-4-2 | Implement group_by_symmetry | Symmetric/asymmetric grouping |
| L-4-3 | Test accuracy computation | Verify on dummy data |
| L-4-4 | Validate grouping logic | Check indices [0,1,8] vs [2,3,5,6,7,9] |

---

## A-5: Implement Visualization [Complexity: 9, Budget: 4]

**Applied**: Matplotlib/seaborn heatmap patterns

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict
from pathlib import Path

def plot_heatmap(results: Dict, save_path: str):
    """
    Generate conditions × digits accuracy heatmap.
    
    Args:
        results: {
            'baseline': {'per_class': [...]},
            'flip30': {'per_class': [...]},
            ...
        }
        save_path: Output file path
    """
    conditions = ['baseline', 'flip30', 'flip50', 'flip90', 'rotation']
    data = np.array([results[c]['per_class'] for c in conditions])  # [5, 10]
    
    plt.figure(figsize=(10, 4))
    sns.heatmap(
        data,
        annot=True,
        fmt='.1f',
        cmap='viridis',
        xticklabels=range(10),
        yticklabels=conditions,
        cbar_kws={'label': 'Accuracy (%)'}
    )
    plt.xlabel('Digit')
    plt.ylabel('Condition')
    plt.title('Per-Class Accuracy by Condition')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_group_comparison(results: Dict, save_path: str):
    """
    Generate symmetric vs asymmetric bar chart.
    
    Args:
        results: Same format as plot_heatmap
    """
    conditions = ['baseline', 'flip30', 'flip50', 'flip90', 'rotation']
    symmetric = [results[c]['symmetric_mean'] for c in conditions]
    asymmetric = [results[c]['asymmetric_mean'] for c in conditions]
    
    x = np.arange(len(conditions))
    width = 0.35
    
    plt.figure(figsize=(8, 5))
    plt.bar(x - width/2, symmetric, width, label='Symmetric (0,1,8)')
    plt.bar(x + width/2, asymmetric, width, label='Asymmetric (2,3,5,6,7,9)')
    
    plt.xlabel('Condition')
    plt.ylabel('Mean Accuracy (%)')
    plt.title('Symmetric vs Asymmetric Digit Accuracy')
    plt.xticks(x, conditions, rotation=15)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_dose_response(results: Dict, save_path: str):
    """
    Generate flip probability vs accuracy plot.
    
    Args:
        results: Same format as plot_heatmap
    """
    flip_conditions = [
        ('baseline', 0.0),
        ('flip30', 0.3),
        ('flip50', 0.5),
        ('flip90', 0.9)
    ]
    
    probs = [p for _, p in flip_conditions]
    symmetric = [results[c]['symmetric_mean'] for c, _ in flip_conditions]
    asymmetric = [results[c]['asymmetric_mean'] for c, _ in flip_conditions]
    
    plt.figure(figsize=(7, 5))
    plt.plot(probs, symmetric, 'o-', label='Symmetric', linewidth=2, markersize=8)
    plt.plot(probs, asymmetric, '^-', label='Asymmetric', linewidth=2, markersize=8)
    
    plt.xlabel('Horizontal Flip Probability')
    plt.ylabel('Mean Accuracy (%)')
    plt.title('Dose-Response: Flip Probability Effect')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Implement plot_heatmap | Conditions × digits heatmap |
| L-5-2 | Implement plot_group_comparison | Bar chart for groups |
| L-5-3 | Implement plot_dose_response | Flip probability line plot |
| L-5-4 | Test visualizations | Verify with dummy data |

---

## A-6: Run Experiments + Validate [Complexity: 11, Budget: 4]

**Applied**: Experiment orchestration pattern

### API Signatures

```python
# run_experiment.py
import json
from pathlib import Path
from typing import Dict

def run_all_conditions(
    epochs: int = 14,
    device: str = "cuda",
    seed: int = 42
) -> Dict:
    """
    Execute all 5 experimental conditions.
    
    Returns:
        {
            'baseline': {
                'per_class': [...],
                'symmetric_mean': float,
                'asymmetric_mean': float,
                'overall': float
            },
            'flip30': {...},
            ...
        }
    """
    results = {}
    conditions = ['baseline', 'flip30', 'flip50', 'flip90', 'rotation']
    
    for condition in conditions:
        print(f"\nTraining {condition}...")
        train_result = train_condition(condition, epochs, device=device, seed=seed)
        
        # Evaluate
        test_loader = get_mnist_loaders(condition)[1]
        per_class_acc = compute_per_class_accuracy(train_result['model'], test_loader, device)
        grouped = group_by_symmetry(per_class_acc)
        
        results[condition] = grouped
        print(f"{condition}: Symmetric={grouped['symmetric_mean']:.2f}%, Asymmetric={grouped['asymmetric_mean']:.2f}%")
    
    return results

def validate_gate_criteria(results: Dict) -> Dict:
    """
    Check MUST_WORK gate criteria.
    
    Returns:
        {
            'passed': bool,
            'checks': {
                'baseline_quality': bool,
                'asymmetric_degradation': bool,
                'symmetric_stability': bool,
                'rotation_control': bool
            },
            'action': 'PROCEED' | 'ABANDON'
        }
    """
    baseline = results['baseline']
    flip50 = results['flip50']
    rotation = results['rotation']
    
    checks = {
        'baseline_quality': baseline['overall'] >= 98.0,
        'asymmetric_degradation': baseline['asymmetric_mean'] > flip50['asymmetric_mean'],
        'symmetric_stability': abs(baseline['symmetric_mean'] - flip50['symmetric_mean']) < 1.0,
        'rotation_control': abs(rotation['asymmetric_mean'] - baseline['asymmetric_mean']) < 1.0
    }
    
    return {
        'passed': all(checks.values()),
        'checks': checks,
        'action': 'PROCEED' if all(checks.values()) else 'ABANDON'
    }

def save_results(results: Dict, output_dir: str):
    """Save JSON results and generate figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    with open(output_path / "results_accuracy.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate figures
    figures_dir = output_path / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    plot_heatmap(results, str(figures_dir / "heatmap.png"))
    plot_group_comparison(results, str(figures_dir / "group_comparison.png"))
    plot_dose_response(results, str(figures_dir / "dose_response.png"))

def main():
    """Main execution: train → evaluate → visualize → save."""
    print("Starting H-E1 Experiment: Horizontal Flip Semantic Validity")
    
    # Run experiments
    results = run_all_conditions(epochs=14, device="cuda", seed=42)
    
    # Validate gate
    gate = validate_gate_criteria(results)
    print(f"\nGate Status: {gate['action']}")
    print(f"Checks: {gate['checks']}")
    
    # Save results
    save_results(results, "docs/youra_research/h-e1")
    
    # Save gate decision
    with open("docs/youra_research/h-e1/gate_decision.json", "w") as f:
        json.dump({
            'hypothesis': 'h-e1',
            'gate_type': 'MUST_WORK',
            'criteria_passed': gate['passed'],
            'action': gate['action'],
            'results_summary': {
                'baseline_acc': results['baseline']['overall'],
                'flip50_asymmetric_degradation': 
                    results['baseline']['asymmetric_mean'] - results['flip50']['asymmetric_mean'],
                'symmetric_stability': 
                    abs(results['baseline']['symmetric_mean'] - results['flip50']['symmetric_mean']),
                'rotation_control': 
                    abs(results['rotation']['asymmetric_mean'] - results['baseline']['asymmetric_mean'])
            }
        }, f, indent=2)
    
    print("\nResults saved to docs/youra_research/h-e1/")
    return 0 if gate['passed'] else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Implement run_all_conditions | Loop over 5 conditions |
| L-6-2 | Implement validate_gate_criteria | MUST_WORK gate checks |
| L-6-3 | Implement save_results | JSON + figures persistence |
| L-6-4 | Implement main | Entry point orchestration |

---

## Summary

**Total Tasks**: 6
**Total Subtasks**: 24/24 used (4 per task)
**Architecture**: Single-file modules, no base hypothesis dependencies
**Key Patterns**:
- PyTorch official MNIST example (model + training)
- torchvision transforms composition (augmentation)
- Matplotlib/seaborn visualization patterns

**Critical Implementation Notes**:
- Test set ALWAYS uses baseline transform (no augmentation)
- Flip probability extracted from condition string: "flip30" → 0.3
- Gate validation requires ALL 4 checks to pass
- Per-class accuracy computed before grouping
- Figures saved at 300 DPI for publication quality

**PoC Simplifications Applied**:
- Single seed (n=1)
- No statistical tests (directional evidence only)
- Fixed hyperparameters from PyTorch official example
- Simple file structure (7 modules total)

---

*Logic design optimized for rapid EXISTENCE validation*
*Estimated implementation time: 4-6 hours (single developer)*
*Next Phase: Configuration Design (hyperparameters, paths, logging)*
