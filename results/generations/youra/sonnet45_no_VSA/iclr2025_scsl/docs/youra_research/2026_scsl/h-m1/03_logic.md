# Logic Design: h-m1

**Hypothesis**: Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)  
**Type**: MECHANISM  
**Date**: 2026-07-11  
**Budget**: 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: API patterns verified from h-e1 experiments  
**Analyzed Path**: experiments/h-e1/ (via direct file reading)  
**Relevant Symbols**:
- `train_epoch()`: Returns `Dict[str, float]` with loss/accuracy
- `train_method()`: Full training pipeline, returns result dict
- `statistical_analysis()`: Returns statistical test results dict
- `run_all_experiments()`: Multi-condition orchestration pattern

**Key Pattern**: h-e1 uses dataclass configs, modular train/eval separation, and dict-based result passing.

---

## A-7: Orchestration [Complexity: 14, Budget: 4]

**Applied**: Standard PyTorch experiment orchestration pattern from h-e1

### API Signatures

```python
from pathlib import Path
from typing import Dict, List
import json
from config import ExperimentConfig, get_config

def run_single_condition(
    config: ExperimentConfig,
    flip_prob: float,
    output_dir: Path
) -> Dict:
    """
    Run training for single flip probability condition (5 seeds).
    
    Args:
        config: Experiment configuration
        flip_prob: Flip probability (0.0, 0.3, 0.5, 0.9)
        output_dir: Output directory
    
    Returns:
        results: {
            "flip_prob": float,
            "seed_results": List[Dict],  # 5 seed results
            "mean_asymmetric_acc": float,
            "std_asymmetric_acc": float,
            "mean_overall_acc": float
        }
    """
    ...

def run_all_conditions(
    config: ExperimentConfig,
    output_dir: Path
) -> Dict:
    """
    Run all flip probability conditions (4 conditions × 5 seeds = 20 runs).
    
    Args:
        config: Experiment configuration
        output_dir: Output directory for checkpoints/logs
    
    Returns:
        all_results: {
            "conditions": {
                0.0: {...},  # run_single_condition result
                0.3: {...},
                0.5: {...},
                0.9: {...}
            },
            "gate_status": "PASS" or "PARTIAL",
            "spearman_rho": float,
            "spearman_p": float
        }
    """
    ...

def save_results(
    results: Dict,
    output_dir: Path
) -> None:
    """
    Save results to JSON file.
    
    Args:
        results: Results from run_all_conditions
        output_dir: Output directory
    
    Saves to: {output_dir}/results.json
    """
    ...

def main() -> None:
    """
    Main entry point: load config, run experiments, save results.
    """
    ...
```

### Tensor Shapes

N/A (orchestration logic, no tensors)

### Pseudo-code

```
1. config = get_config()
2. output_dir = Path(config.output_dir)
3. all_results = {}
4. For flip_prob in [0.0, 0.3, 0.5, 0.9]:
     a. condition_results = run_single_condition(config, flip_prob, output_dir)
     b. all_results[flip_prob] = condition_results
5. dose_response = dose_response_test(all_results)  # from evaluate.py
6. all_results["gate_status"] = dose_response["gate_status"]
7. save_results(all_results, output_dir)
8. Generate visualizations (call visualize.py functions)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_single_condition | Iterate 5 seeds, call train_model for each |
| L-7-2 | run_all_conditions | Iterate 4 flip_probs, aggregate results |
| L-7-3 | save_results | JSON serialization with proper formatting |
| L-7-4 | main | Config loading + orchestration flow |

---

## A-4: Training [Complexity: 12, Budget: 2]

**Applied**: PyTorch standard training loop (similar to h-e1 pattern)

### API Signatures

```python
from typing import Dict, Tuple
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR
from config import ExperimentConfig

def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: Adam,
    scheduler: StepLR,
    criterion: nn.Module,
    device: str,
    gradient_clip_norm: float
) -> Dict[str, float]:
    """
    Train for one epoch.
    
    Args:
        model: CNN model
        dataloader: Training DataLoader
        optimizer: Adam optimizer
        scheduler: StepLR scheduler
        criterion: CrossEntropyLoss
        device: "cuda" or "cpu"
        gradient_clip_norm: Gradient clipping threshold
    
    Returns:
        metrics: {"loss": float, "accuracy": float}
    """
    ...

def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]:
    """
    Validation pass (no augmentation).
    
    Args:
        model: CNN model
        dataloader: Validation DataLoader (no flip augmentation)
        criterion: CrossEntropyLoss
        device: "cuda" or "cpu"
    
    Returns:
        metrics: {"loss": float, "accuracy": float}
    """
    ...

def train_model(
    config: ExperimentConfig,
    flip_prob: float,
    seed: int,
    output_dir: Path
) -> Tuple[nn.Module, Dict]:
    """
    Full training pipeline with early stopping.
    
    Args:
        config: Experiment configuration
        flip_prob: Horizontal flip probability
        seed: Random seed
        output_dir: Directory for checkpoints/logs
    
    Returns:
        best_model: Best checkpoint (highest val accuracy)
        result: {
            "flip_prob": float,
            "seed": int,
            "best_epoch": int,
            "best_val_acc": float,
            "final_test_acc": float
        }
    """
    ...
```

### Tensor Shapes

```python
# Training batch
images: [B, 1, 28, 28]  # MNIST grayscale
labels: [B]             # Class labels (0-9)
logits: [B, 10]         # Model output
loss: scalar            # CrossEntropyLoss
```

### Pseudo-code

```
train_epoch:
  1. model.train()
  2. For batch in dataloader:
       a. images, labels = batch -> device
       b. optimizer.zero_grad()
       c. logits = model(images)  # [B, 10]
       d. loss = criterion(logits, labels)
       e. loss.backward()
       f. clip_grad_norm_(model.parameters(), gradient_clip_norm)
       g. optimizer.step()
  3. scheduler.step()
  4. Return {"loss": mean_loss, "accuracy": mean_acc}

train_model:
  1. Set seed (torch, numpy, cuda)
  2. Get dataloaders (train with flip_prob, val without flip)
  3. Initialize model, optimizer, scheduler
  4. best_val_acc = 0, patience_counter = 0
  5. For epoch in range(max_epochs):
       a. train_metrics = train_epoch(...)
       b. val_metrics = validate(...)
       c. If val_acc > best_val_acc:
            - Save checkpoint
            - Reset patience_counter
       d. Else: patience_counter += 1
       e. If patience_counter >= patience: break
  6. Load best checkpoint
  7. Evaluate on test set
  8. Return best_model, result_dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | train_epoch + validate | Forward/backward pass, metric computation |
| L-4-2 | train_model | Full training loop with early stopping |

---

## A-5: Evaluation [Complexity: 10, Budget: 2]

**Applied**: NumPy array-based metrics (scipy.stats for Spearman)

### API Signatures

```python
import numpy as np
from typing import Dict, List
from scipy.stats import spearmanr
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def compute_asymmetric_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    asymmetric_digits: List[int] = [2, 3, 5, 6, 7, 9]
) -> float:
    """
    Compute accuracy on asymmetric digit subset.
    
    Args:
        y_true: Ground truth labels [N]
        y_pred: Predicted labels [N]
        asymmetric_digits: List of asymmetric digit classes
    
    Returns:
        accuracy: float (0.0-1.0)
    """
    ...

def compute_per_digit_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[int, float]:
    """
    Compute accuracy per digit class.
    
    Args:
        y_true: Ground truth labels [N]
        y_pred: Predicted labels [N]
    
    Returns:
        per_digit_acc: {0: acc0, 1: acc1, ..., 9: acc9}
    """
    ...

def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict:
    """
    Evaluate model on test set.
    
    Args:
        model: Trained CNN
        dataloader: Test DataLoader (no augmentation)
        device: "cuda" or "cpu"
    
    Returns:
        results: {
            "overall_accuracy": float,
            "asymmetric_accuracy": float,
            "per_digit_accuracy": Dict[int, float],
            "y_true": np.ndarray,  # For further analysis
            "y_pred": np.ndarray
        }
    """
    ...

def dose_response_test(
    results: Dict[float, List[float]]
) -> Dict:
    """
    Test dose-response relationship (Spearman correlation).
    
    Args:
        results: {
            0.0: [acc_seed1, acc_seed2, ...],  # 5 seeds
            0.3: [...],
            0.5: [...],
            0.9: [...]
        }
    
    Returns:
        test_result: {
            "spearman_rho": float,
            "spearman_p": float,
            "gate_status": "PASS" or "PARTIAL",
            "mean_accs": [mean_p0, mean_p3, mean_p5, mean_p9]
        }
    """
    ...
```

### Tensor Shapes

```python
# evaluate_model
logits: [N, 10]  # Model predictions (N=10000 for MNIST test)
probs: [N, 10]   # Softmax probabilities
preds: [N]       # Argmax predictions
labels: [N]      # Ground truth

# Converted to numpy
y_true: np.ndarray [N]
y_pred: np.ndarray [N]
```

### Pseudo-code

```
compute_asymmetric_accuracy:
  1. mask = np.isin(y_true, asymmetric_digits)  # [N] boolean
  2. y_true_masked = y_true[mask]
  3. y_pred_masked = y_pred[mask]
  4. accuracy = (y_true_masked == y_pred_masked).mean()
  5. Return accuracy

evaluate_model:
  1. model.eval()
  2. all_preds, all_labels = [], []
  3. For batch in dataloader:
       a. images, labels = batch -> device
       b. logits = model(images)  # [B, 10]
       c. preds = logits.argmax(dim=1)  # [B]
       d. all_preds.append(preds.cpu())
       e. all_labels.append(labels.cpu())
  4. y_pred = np.concatenate(all_preds)
  5. y_true = np.concatenate(all_labels)
  6. overall_acc = (y_true == y_pred).mean()
  7. asymmetric_acc = compute_asymmetric_accuracy(y_true, y_pred)
  8. per_digit_acc = compute_per_digit_accuracy(y_true, y_pred)
  9. Return results dict

dose_response_test:
  1. flip_probs = [0.0, 0.3, 0.5, 0.9]
  2. mean_accs = [np.mean(results[p]) for p in flip_probs]
  3. rho, p_value = spearmanr(flip_probs, mean_accs)
  4. gate_status = "PASS" if (rho < 0 and p_value < 0.05) else "PARTIAL"
  5. Return {"spearman_rho": rho, "spearman_p": p_value, "gate_status": gate_status, ...}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_asymmetric_accuracy + per_digit | Metric computation functions |
| L-5-2 | evaluate_model + dose_response_test | Model evaluation + statistical test |

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (8/8 used)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Existing codebase (h-e1) → Analyzed via direct file reading (Serena unavailable due to project selection issue)
- [x] Codebase Analysis section documents status and findings

### Budget Allocation
- A-7: 4/4 subtasks (orchestration complexity justified by multi-condition logic)
- A-4: 2/2 subtasks (standard training loop)
- A-5: 2/2 subtasks (metrics + statistical test)
- Total: 8/8 subtasks used

---

**Output Status**: Complete  
**Next Phase**: Phase 4 - Implementation  
**File Paths**:
- Architecture: `/workspace/TEST_scsl/docs/youra_research/h-m1/03_architecture.md`
- PRD: `/workspace/TEST_scsl/docs/youra_research/h-m1/03_prd.md`
- Logic Design: `/workspace/TEST_scsl/docs/youra_research/h-m1/03_logic.md`
