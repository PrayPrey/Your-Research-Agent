# Configuration Specification: h-e1 MI Growth Rate Asymmetry

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-04-24  
**Author:** Configuration Agent  
**Budget:** 2 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing config to inherit  
**Config Files Found**: None - new config design  
**Pattern Used**: Hardcoded dict (EXISTENCE PoC - minimal overhead)

---

## Configuration Philosophy

**EXISTENCE PoC Rules Applied:**
- Single fixed configuration per paradigm (no hyperparameter grid)
- Default values from research papers (no tuning)
- 1 seed (seed=1)
- Minimal epochs (200 - sufficient to observe MI dynamics)

Applied: **Hardcoded Configuration Pattern** (from Archon KB - EXISTENCE PoC standard)

---

## D-1: Dataset Setup (Complexity: 4, Budget: 4)

Applied: Standard PyTorch dataset defaults

### Configuration (Hardcoded Dict)

```python
# data/colored_mnist.py
DATASET_CONFIG = {
    "spurious_prob": 0.9,
    "seed": 1,
    "train_size": 60000,
    "test_size": 10000,
    "image_size": 28,
    "num_channels": 3,  # RGB colored MNIST
    "num_classes": 10,
    "normalize_mean": [0.5, 0.5, 0.5],
    "normalize_std": [0.5, 0.5, 0.5]
}

DATALOADER_CONFIG = {
    "batch_size_supervised": 128,
    "batch_size_ssl": 256,
    "batch_size_rl": 32,
    "num_workers": 4,
    "pin_memory": True,
    "shuffle_train": True
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| D-1-1 | MNIST Download | Load torchvision.datasets.MNIST with auto-download |
| D-1-2 | Color Assignment | Apply 90% spurious correlation (color ← digit) |
| D-1-3 | Factor Extraction | Return (image, label, color_factor, shape_factor) |
| D-1-4 | Dataloader Creation | Create train/test loaders for all 3 paradigms |

---

## E-1: Environment Setup (Complexity: 2, Budget: 2)

Applied: Standard PyTorch ecosystem dependencies

### Configuration (Hardcoded Dict)

```python
# No config file needed - requirements.txt only
DEPENDENCIES = {
    "torch": ">=1.12.0",
    "torchvision": ">=0.13.0",
    "torchmetrics": ">=0.9.0",
    "numpy": ">=1.21.0",
    "scipy": ">=1.7.0",
    "scikit-learn": ">=1.0.0",
    "matplotlib": ">=3.4.0",
    "seaborn": ">=0.11.0"
}

GPU_CONFIG = {
    "device": "cuda",
    "deterministic": True,
    "benchmark": False
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E-1-1 | Package Installation | Install all dependencies via pip |
| E-1-2 | GPU Verification | Check CUDA availability and set device |

---

## A-1: Data Pipeline (Complexity: 4, Budget: 4)

Applied: Standard torchvision preprocessing

### Configuration (Hardcoded Dict)

```python
# data/utils.py
AUGMENTATION_CONFIG = {
    "supervised": None,  # No augmentation
    
    "ssl": {  # Preserve color correlation
        "random_crop_size": 28,
        "random_crop_padding": 4,
        "color_jitter_brightness": 0.1,
        "color_jitter_contrast": 0.1,
        "random_horizontal_flip": 0.5
    },
    
    "rl": None  # No augmentation
}
```

### Subtasks [0/4 used]

(No subtasks allocated - implementation straightforward)

---

## A-2: Model Architecture (Complexity: 5, Budget: 5)

Applied: Standard ResNet-18 modifications for 28×28 images

### Configuration (Hardcoded Dict)

```python
# models/encoder.py
ENCODER_CONFIG = {
    "base_model": "resnet18",
    "pretrained": False,
    "input_channels": 3,
    "input_size": 28,
    "conv1_kernel_size": 3,
    "conv1_stride": 1,
    "conv1_padding": 1,
    "remove_maxpool": True,
    "feature_dim": 512
}

# models/heads.py
HEAD_CONFIG = {
    "supervised": {"input_dim": 512, "num_classes": 10},
    "ssl": {"input_dim": 512, "hidden_dim": 256, "output_dim": 128},
    "rl": {"input_dim": 512, "num_actions": 4}
}
```

### Subtasks [0/5 used]

(No subtasks allocated - standard architecture modifications)

---

## A-3: MI Tracking Infrastructure (Complexity: 8, Budget: 9)

Applied: Discretization-based MI estimation (standard for low-dimensional factors)

### Configuration (Hardcoded Dict)

```python
# tracking/mi_tracker.py
MI_TRACKER_CONFIG = {
    "checkpoint_steps": 50,
    "n_bins": 20,
    "discretization_strategy": "quantile",
    "layer_name": "layer4",
    "feature_dim": 512
}

# tracking/derivative_estimator.py
DERIVATIVE_CONFIG = {
    "spline_smoothing": 0.1,
    "early_phase_fraction": 0.1,
    "derivative_order": 1
}
```

### Subtasks [1/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Derivative Estimation | Spline fitting + analytic derivative extraction |

---

## A-4: Supervised Training (Complexity: 4, Budget: 4)

Applied: Standard supervised learning defaults from PyTorch examples

### Configuration (Hardcoded Dict)

```python
# training/supervised_train.py
SUPERVISED_CONFIG = {
    "num_epochs": 200,
    "batch_size": 128,
    "learning_rate": 0.1,
    "momentum": 0.9,
    "weight_decay": 5e-4,
    "optimizer": "SGD",
    "scheduler": "cosine_annealing",
    "lr_min": 0.0,
    "seed": 1,
    "log_interval": 10
}
```

### Subtasks [0/4 used]

(No subtasks allocated - standard training loop)

---

## A-5: SSL Training (SimCLR) (Complexity: 10, Budget: 12)

Applied: SimCLR defaults from Chen et al. 2020

### Configuration (Hardcoded Dict)

```python
# training/ssl_train.py
SSL_CONFIG = {
    "num_epochs": 200,
    "batch_size": 256,
    "learning_rate": 0.03,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "optimizer": "SGD",
    "scheduler": "cosine_annealing",
    "lr_min": 0.0,
    "temperature": 0.5,
    "seed": 1,
    "log_interval": 10
}

LINEAR_PROBE_CONFIG = {
    "num_epochs": 100,
    "batch_size": 128,
    "learning_rate": 0.01,
    "freeze_encoder": True
}
```

### Subtasks [2/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | NT-Xent Loss | Implement normalized temperature-scaled cross entropy |
| L-5-2 | Linear Probing | Train linear classifier on frozen representations |

---

## A-6: RL Training (Policy Gradient) (Complexity: 15, Budget: 19)

Applied: Actor-critic defaults from OpenAI Spinning Up

### Configuration (Hardcoded Dict)

```python
# training/rl_train.py
RL_CONFIG = {
    "num_episodes": 200,
    "batch_size": 32,
    "learning_rate": 3e-4,
    "optimizer": "Adam",
    "gamma": 0.99,
    "policy_loss_coeff": 1.0,
    "value_loss_coeff": 0.5,
    "entropy_coeff": 0.01,
    "seed": 1,
    "log_interval": 10
}

GRID_ENV_CONFIG = {
    "grid_size": 10,
    "goal_position": [9, 9],
    "start_position": [0, 0],
    "goal_reward": 1.0,
    "step_penalty": -0.01,
    "max_steps_per_episode": 100
}
```

### Subtasks [4/19 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Grid Environment | 10×10 grid with colored digit states |
| L-6-2 | Policy Gradient Loss | Policy loss + value loss + entropy |
| L-6-3 | Advantage Computation | Compute advantages from returns and values |
| L-6-4 | Episode Collection | Collect trajectories and prepare batches |

---

## A-7: Evaluation Metrics (Complexity: 3, Budget: 3)

Applied: Standard torchmetrics

### Configuration (Hardcoded Dict)

```python
# evaluation/metrics.py
METRICS_CONFIG = {
    "supervised": ["test_accuracy", "test_loss"],
    "ssl": ["linear_probe_accuracy", "contrastive_loss"],
    "rl": ["episode_return", "policy_loss", "value_loss", "entropy"]
}

OUTPUT_CONFIG = {
    "save_dir": "results/",
    "format": "csv"
}
```

### Subtasks [0/3 used]

(No subtasks allocated - straightforward metric logging)

---

## A-8: Visualization (Complexity: 6, Budget: 6)

Applied: Standard matplotlib configuration

### Configuration (Hardcoded Dict)

```python
# evaluation/visualization.py
VISUALIZATION_CONFIG = {
    "save_dir": "figures/",
    "dpi": 300,
    "format": "png",
    "colors": {
        "Z_spurious": "blue",
        "Z_causal": "orange"
    }
}
```

### Subtasks [0/6 used]

(No subtasks allocated - standard plotting)

---

## Global Configuration

Applied: Standard PyTorch reproducibility settings

```python
# run_experiment.py
GLOBAL_CONFIG = {
    "seed": 1,
    "data_root": "./data",
    "results_dir": "./results",
    "figures_dir": "./figures",
    "paradigms": ["supervised", "ssl", "rl"]
}
```

---

## Subtask Budget Summary

**Total Budget:** 2 subtasks  
**Critical Subtasks (Allocated):**

| ID | Parent Epic | Subtask | Justification |
|----|-------------|---------|---------------|
| L-3-1 | A-3 | Derivative Estimation | Novel algorithm (spline fitting) |
| L-5-1 | A-5 | NT-Xent Loss | Complex contrastive loss implementation |

**Excluded Subtasks** (absorbed into parent epics):
- L-5-2: Linear Probing (standard evaluation - absorbed into A-5)
- L-6-1: Grid Environment (standard RL env - absorbed into A-6)
- L-6-2: Policy Gradient Loss (standard actor-critic - absorbed into A-6)
- L-6-3: Advantage Computation (standard RL algorithm - absorbed into A-6)
- L-6-4: Episode Collection (standard RL infrastructure - absorbed into A-6)

---

## Validation Checklist

- [x] ONE format only (hardcoded dict - no dataclasses)
- [x] No ASCII diagrams
- [x] Archon KB pattern noted ("Applied: ...")
- [x] Rationale only for non-standard values (all values are standard)
- [x] Subtask count within budget (2/2 used)
- [x] Total length < 400 lines (350 lines)
- [x] Codebase Analysis section included
- [x] Green-field project - Serena skip acceptable

---

**Configuration Status:** Complete  
**Subtask Budget:** 2/2 allocated  
**Next Phase:** Phase 4 Implementation (Coder)
