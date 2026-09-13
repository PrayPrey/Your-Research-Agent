# Architecture Design: h-e1
# Horizontal Flip Augmentation Semantic Validity Study

**Date:** 2026-07-11
**Hypothesis:** h-e1 (EXISTENCE - PoC)
**Author:** Architecture Agent (Phase 3)

Applied: Minimal PoC module structure

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase
**Status**: existing patterns found - previous h-e1 experiment exists
**Analyzed Path**: experiments/h-e1/
**Findings**: Existing h-e1 implementation found with different hypothesis (SAM-SWA compressibility). Current h-e1 (flip augmentation) is NEW experiment - green-field implementation required.

**Note**: This is a DIFFERENT h-e1 hypothesis (flip augmentation semantic validity) from existing code (SAM-SWA). Creating fresh implementation.

---

## System Overview

**Architecture Type**: EXISTENCE (PoC)
**Core Mechanism**: Data augmentation (horizontal flip) - NOT model architecture
**Implementation Scope**: Single-file proof-of-concept

This is a data-level experiment testing augmentation semantic validity. The "proposed model" is identical to baseline - only the training data differs.

---

## Module Definitions

### 1. Data Module (`data.py`)

**Dependencies**: torchvision.datasets, torchvision.transforms

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def get_mnist_loaders(condition: str, batch_size: int = 64) -> tuple[DataLoader, DataLoader]:
    """Get train/test dataloaders for specified condition."""
    ...

def get_transform(condition: str) -> transforms.Compose:
    """
    Get augmentation transform for condition.
    
    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
    
    Returns:
        Transform pipeline
    """
    ...
```

### 2. Model Module (`model.py`)

**Dependencies**: torch.nn, torch.nn.functional

```python
import torch.nn as nn
import torch.nn.functional as F

class MNISTNet(nn.Module):
    """Standard CNN from PyTorch official MNIST example."""
    
    def __init__(self):
        """Initialize layers: Conv1(32), Conv2(64), FC1(128), FC2(10)."""
        ...
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with log_softmax output."""
        ...
```

### 3. Training Module (`train.py`)

**Dependencies**: Model, Data, torch.optim

```python
def train_condition(condition: str, epochs: int = 14, seed: int = 42) -> dict:
    """
    Train model for single condition.
    
    Returns:
        dict: {model, train_losses, test_accs}
    """
    ...

def train_epoch(model, train_loader, optimizer, device) -> float:
    """Single epoch training."""
    ...

def test_epoch(model, test_loader, device) -> float:
    """Single epoch evaluation."""
    ...
```

### 4. Evaluation Module (`evaluate.py`)

**Dependencies**: torch, numpy

```python
def compute_per_class_accuracy(model, test_loader, device) -> dict:
    """
    Compute per-class accuracy.
    
    Returns:
        dict: {0: acc_0, 1: acc_1, ..., 9: acc_9}
    """
    ...

def group_by_symmetry(per_class_acc: dict) -> dict:
    """
    Group accuracies by symmetry.
    
    Returns:
        dict: {symmetric_mean, asymmetric_mean, per_class}
    """
    ...
```

### 5. Visualization Module (`visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_heatmap(results: dict, save_path: str):
    """Generate conditions × digits accuracy heatmap."""
    ...

def plot_group_comparison(results: dict, save_path: str):
    """Generate symmetric vs asymmetric bar chart."""
    ...

def plot_dose_response(results: dict, save_path: str):
    """Generate flip probability vs accuracy plot."""
    ...
```

### 6. Experiment Runner (`run_experiment.py`)

**Dependencies**: All modules

```python
def run_all_conditions() -> dict:
    """
    Execute all 5 experimental conditions.
    
    Returns:
        dict: {baseline: {...}, flip30: {...}, ...}
    """
    ...

def save_results(results: dict, output_dir: str):
    """Save JSON results and generate figures."""
    ...

def main():
    """Main execution: train → evaluate → visualize → save."""
    ...
```

### 7. Configuration Module (`config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    """Centralized configuration."""
    
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
    
    # Output
    OUTPUT_DIR: str = "docs/youra_research/h-e1"
    FIGURES_DIR: str = "docs/youra_research/h-e1/figures"
```

---

## File Structure

```
docs/youra_research/h-e1/
├── code/
│   ├── config.py          # Configuration constants
│   ├── data.py            # MNIST loading + augmentation
│   ├── model.py           # MNISTNet CNN architecture
│   ├── train.py           # Training loop
│   ├── evaluate.py        # Per-class accuracy computation
│   ├── visualize.py       # Figure generation
│   ├── run_experiment.py  # Main orchestrator
│   └── __init__.py
├── figures/               # Generated visualizations
│   ├── heatmap.png
│   ├── group_comparison.png
│   └── dose_response.png
├── results_accuracy.json  # Per-class results
└── training_logs.txt      # Epoch-wise logs
```

---

## Data Flow

1. **Configuration** → Load ExperimentConfig
2. **Data Loading** → For each condition: get_mnist_loaders(condition)
3. **Training** → For each condition: train_condition(condition, epochs=14)
4. **Evaluation** → For each trained model: compute_per_class_accuracy()
5. **Grouping** → Group by symmetry: group_by_symmetry()
6. **Visualization** → Generate 3 figures
7. **Persistence** → Save JSON results + figures

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Create files, config, dependencies | 5 | 1+1+1+2 (files+deps+imports+test) |
| A-2 | Implement data pipeline | MNIST loading + 5 augmentation transforms | 8 | 2+2+2+2 (loader+baseline+flip+rotation) |
| A-3 | Implement model + training | MNISTNet architecture + training loop | 10 | 3+3+2+2 (model+train_epoch+test_epoch+integration) |
| A-4 | Implement evaluation | Per-class accuracy + symmetry grouping | 7 | 2+2+2+1 (per_class+grouping+testing+integration) |
| A-5 | Implement visualization | Heatmap + bar chart + dose-response | 9 | 3+3+2+1 (heatmap+bar+dose+save) |
| A-6 | Run experiments + validate | Execute 5 conditions, verify MUST_WORK gate | 11 | 3+3+3+2 (run+results+gate_check+debug) |

**Total Complexity**: 50 points

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-3, A-5, A-6]
- Low (4-8): [A-1, A-2, A-4]

**Rationale for 6 Tasks (PoC Adjusted)**:
- EXISTENCE hypothesis requires minimal structure
- Single-file integration possible, but split for clarity
- Focus on execution speed over modularity
- Each task produces testable output

---

## Integration Points

### External Dependencies

**Python Packages**:
```
torch>=1.10
torchvision>=0.11
numpy>=1.20
matplotlib>=3.4
seaborn>=0.11
```

**PyTorch Official MNIST Example Reference**:
- Source: https://github.com/PyTorch/examples/blob/main/mnist/main.py
- Used for: Model architecture, optimizer config, training hyperparameters
- Validation: ~99% test accuracy baseline

### Mechanism Integration

**Core Mechanism**: Horizontal flip augmentation
**Implementation**: `transforms.RandomHorizontalFlip(p)`
**Integration Point**: Data pipeline (get_transform function)

```python
# Integration example
def get_transform(condition: str) -> transforms.Compose:
    base = [
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ]
    
    if condition == "flip50":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),  # ← Core mechanism
            *base
        ])
    ...
```

**Mechanism Location**: Applied BEFORE ToTensor in transform pipeline
**Effect**: Training data only - test set uses baseline transform

---

## MUST_WORK Gate Validation

**Success Criteria** (from PRD):

1. Code executes without errors
2. Baseline model achieves ~99% test accuracy
3. `Baseline.asymmetric_mean > Flip50.asymmetric_mean` (directional effect)
4. `Baseline.symmetric_mean ≈ Flip50.symmetric_mean` (stability)
5. `Rotation.asymmetric_mean ≈ Baseline.asymmetric_mean` (control)

**Validation Implementation** (in run_experiment.py):

```python
def validate_gate_criteria(results: dict) -> dict:
    """
    Check MUST_WORK gate criteria.
    
    Returns:
        dict: {passed, failures, details}
    """
    baseline = results['baseline']
    flip50 = results['flip50']
    rotation = results['rotation']
    
    checks = {
        'baseline_quality': baseline['overall_acc'] >= 98.0,  # ~99% target
        'asymmetric_degradation': baseline['asymmetric_mean'] > flip50['asymmetric_mean'],
        'symmetric_stability': abs(baseline['symmetric_mean'] - flip50['symmetric_mean']) < 1.0,
        'rotation_control': abs(rotation['asymmetric_mean'] - baseline['asymmetric_mean']) < 1.0
    }
    
    return {
        'passed': all(checks.values()),
        'checks': checks,
        'action': 'PROCEED' if all(checks.values()) else 'ABANDON'
    }
```

---

## Design Decisions

**Why single model architecture?**
- Hypothesis tests augmentation semantics, not model architecture
- PyTorch official example provides validated baseline
- Reduces implementation complexity for EXISTENCE level

**Why 5 conditions instead of 2?**
- Dose-response (flip probability) strengthens causal claim
- Rotation control validates measurement specificity
- Minimal overhead (same training code, different transform)

**Why per-class accuracy over overall?**
- Hypothesis predicts differential effect by digit symmetry
- Overall accuracy masks effect (asymmetric digits = 6/10 classes)
- Per-class enables visual inspection of pattern

---

## Output Artifacts

**Phase 4.5 Synthesis Inputs**:

1. `results_accuracy.json` - Structured results for all conditions
2. `figures/heatmap.png` - Visual evidence of differential effect
3. `figures/group_comparison.png` - Hypothesis test visualization
4. `figures/dose_response.png` - Dose-response relationship
5. `training_logs.txt` - Training convergence verification

**Gate Decision File** (generated by run_experiment.py):
```json
{
  "hypothesis": "h-e1",
  "gate_type": "MUST_WORK",
  "criteria_passed": true,
  "action": "PROCEED",
  "results_summary": {
    "baseline_acc": 99.1,
    "flip50_asymmetric_degradation": 3.2,
    "symmetric_stability": 0.3,
    "rotation_control": 0.5
  }
}
```

---

## Implementation Notes

**EXISTENCE (PoC) Simplifications Applied**:
- Single seed (n=1) - directional evidence only
- No statistical tests (optional for PoC)
- No hyperparameter tuning (use PyTorch defaults)
- Simple file structure (flat, not nested packages)

**From PyTorch Official Example**:
- Model architecture: Conv1(32), Conv2(64), FC1(128), FC2(10)
- Optimizer: Adadelta (lr=1.0)
- Scheduler: StepLR (step_size=1, gamma=0.7)
- Training: 14 epochs, batch_size=64
- Expected: ~99% test accuracy (validates implementation)

**Critical Insight from Research**:
- Kaggle competition winners (99.689% accuracy) use extensive augmentation BUT avoid horizontal flip
- Confirms hypothesis premise: practitioners implicitly understand semantic invalidity
- This experiment formalizes that intuition

---

## Risk Mitigation

**High Risk**: Baseline fails to reach 99% accuracy
- **Mitigation**: Use exact PyTorch official architecture + hyperparameters
- **Detection**: A-6 checks baseline accuracy before comparing conditions

**Medium Risk**: Effect size too small (noise dominates signal)
- **Mitigation**: Include Flip90 (extreme condition) to amplify effect
- **Detection**: If Flip90 shows no degradation, hypothesis is falsified

**Low Risk**: Visualization errors
- **Mitigation**: Use standard matplotlib patterns, test on dummy data
- **Fallback**: Manual plots in Phase 4.5 if needed

---

*Architecture optimized for rapid EXISTENCE validation*
*Total estimated implementation: 4-6 hours (single developer)*
*Next Phase: Logic Design (execution flow specifications)*
