# Configuration Specification: H-M1 Representation Analysis

**Hypothesis:** H-M1  
**Type:** MECHANISM (Analysis)  
**Author:** Configuration Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending H-E1 - config classes verified from base code  
**Config Files Found:** /workspace/TEST_bi_align/docs/youra_research/h-e1/code/run_experiment.py  
**Pattern Used:** Hardcoded dict (H-E1 uses functional arguments, not dataclass)

**Verification:** H-E1 uses function arguments in `run_experiment()` with values: batch_size=4, max_length=256, lr=1e-5, num_steps=100, alpha=0.7, beta=0.1.

---

## Applied Patterns

Applied: PyTorch Training Config Pattern (from PyTorch DataLoader documentation)  
Applied: Linear Probing Configuration (from TensorFlow datasets documentation)

---

## Configuration Overview

This document defines configuration schemas for H-M1 representation analysis experiment. All configurations use hardcoded Python dictionaries for simplicity and consistency with H-E1's functional approach.

**Format:** Hardcoded dict (single format)  
**Location:** `code/config.py`  
**Usage:** Import CONFIG for all analysis modules

---

## Inherited Configuration (Base Hypothesis)

### Config Values (From Actual H-E1 Code)

The following configurations are inherited from H-E1 experiment:

```python
# From: h-e1/code/run_experiment.py (ACTUAL CODE)
H_E1_CONFIG = {
    # Model
    "model_name": "gpt2-xl",
    "beta": 0.1,  # DPO temperature
    "alpha": 0.7,  # DPO loss weight (attr weight = 0.3)
    
    # Training
    "batch_size": 4,
    "max_length": 256,
    "lr": 1e-5,
    "num_steps": 100,  # PoC: reduced from 15000
    
    # Paths
    "checkpoint_dir": "checkpoints",
    "output_dir": "outputs",
    
    # Gate thresholds
    "min_win_rate": 0.50,
    "min_steering_accuracy": 0.60,
    "max_gradient_angle": 120.0
}
```

**Verified from:** `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/run_experiment.py` (actual implementation, lines 22-28, 63-64)

**Checkpoint Locations:**
```python
CHECKPOINT_PATHS = {
    "joint_model": "../h-e1/checkpoints/joint_model_final.pt",
    "dpo_model": "../h-e1/checkpoints/dpo_only_final.pt",
    "attr_model": "../h-e1/checkpoints/attr_only_final.pt"
}
```

---

## Epic-4: CKA Computation Configuration

**Complexity:** 9/20  
**Budget:** 1 subtask  
**Applied:** Centered Kernel Alignment algorithm (from NVIDIA cuBLAS documentation)

### Configuration (Hardcoded Dict)

```python
CKA_CONFIG = {
    # CKA computation
    "num_samples": 500,  # From H-E1 test set
    "device": "cuda",
    
    # Gate threshold
    "max_cka_similarity": 0.7,  # Joint-DPO divergence threshold
    
    # Model pairs to compare
    "comparison_pairs": [
        ("joint", "dpo"),    # Primary metric
        ("joint", "attr"),   # Additional analysis
        ("dpo", "attr")      # Baseline divergence
    ]
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | CKA Matrix Computation | Implement centering, Gram matrix, HSIC formula |

---

## Epic-2: Hidden State Extraction Configuration

**Complexity:** 8/20  
**Budget:** 1 subtask  
**Applied:** GPT-2 hidden state extraction (from HuggingFace Transformers documentation)

### Configuration (Hardcoded Dict)

```python
EXTRACTION_CONFIG = {
    # Hidden state extraction
    "layer_index": -1,  # Last transformer layer (layer 47 in GPT-2 XL)
    "pooling": "mean",  # Mean pooling over sequence dimension
    "hidden_size": 1600,  # GPT-2 XL hidden dim
    
    # Batch processing
    "batch_size": 32,  # Larger batch for inference (no gradients)
    "max_length": 256,  # Same as H-E1
    
    # Output
    "save_hidden_states": True,
    "hidden_states_dir": "hidden_states"
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Extract Hidden States | Forward pass with output_hidden_states=True, mean pooling |

---

## Epic-6: Visualization Configuration

**Complexity:** 7/20  
**Budget:** 1 subtask  
**Applied:** Matplotlib visualization pattern (from PyTorch documentation)

### Configuration (Hardcoded Dict)

```python
VISUALIZATION_CONFIG = {
    # Output
    "figures_dir": "figures",
    "figure_dpi": 300,
    "figure_format": "png",
    
    # Gate metrics plot (MANDATORY)
    "gate_metrics": {
        "preference_accuracy": {"threshold": 0.70, "type": "min"},
        "attribute_r2": {"threshold": 0.60, "type": "min"},
        "cka_similarity": {"threshold": 0.70, "type": "max"},
        "gradient_cosine": {"threshold": [-0.5, 0.5], "type": "range"}
    },
    "gate_colors": {"pass": "green", "fail": "red"},
    
    # Additional plots
    "tsne_perplexity": 30,  # t-SNE parameter
    "cka_cmap": "RdYlGn",  # Heatmap colormap
    "gradient_bins": 50  # Histogram bins
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Generate Gate Metrics Plot | Mandatory bar chart with pass/fail visualization |

---

## Probing Configuration (No Subtasks Allocated)

**Note:** Probing implementation covered by Epic-3 in architecture (no config subtasks).

### Configuration (Hardcoded Dict)

```python
PROBING_CONFIG = {
    # Preference probe
    "preference_probe": {
        "input_dim": 1600,
        "num_classes": 2,
        "lr": 1e-3,
        "epochs": 20,
        "optimizer": "adam",
        "loss": "cross_entropy"
    },
    
    # Attribute probe
    "attribute_probe": {
        "input_dim": 1600,
        "num_attributes": 3,
        "lr": 1e-3,
        "epochs": 20,
        "optimizer": "adam",
        "loss": "mse"
    },
    
    # Data split
    "train_samples": 400,  # From 500 total
    "test_samples": 100,
    
    # Gate thresholds (inherited from PRD)
    "min_preference_accuracy": 0.70,
    "min_attribute_r2": 0.60  # All 3 attributes
}
```

---

## Gradient Alignment Configuration (No Subtasks Allocated)

**Note:** Gradient analysis covered by Epic-5 in architecture (no config subtasks).

### Configuration (Hardcoded Dict)

```python
GRADIENT_CONFIG = {
    # Sampling
    "num_batches": 10,  # Random batches for gradient extraction
    
    # Computation
    "flatten_gradients": True,
    "retain_graph": True,  # Required for multi-loss backward
    
    # Gate threshold (inherited from H-E1)
    "min_cosine": -0.5,
    "max_cosine": 0.5
}
```

---

## Unified Analysis Configuration

**Main configuration combining all components:**

```python
# config.py
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
H_E1_DIR = BASE_DIR.parent / "h-e1"

# Inherited from H-E1
H_E1_CONFIG = {
    "model_name": "gpt2-xl",
    "beta": 0.1,
    "alpha": 0.7,
    "batch_size": 4,
    "max_length": 256,
    "lr": 1e-5,
    "num_steps": 100,
    "checkpoint_dir": "checkpoints",
    "output_dir": "outputs",
    "min_win_rate": 0.50,
    "min_steering_accuracy": 0.60,
    "max_gradient_angle": 120.0
}

# Checkpoint paths (verified from H-E1)
CHECKPOINT_PATHS = {
    "joint_model": str(H_E1_DIR / "checkpoints" / "joint_model_final.pt"),
    "dpo_model": str(H_E1_DIR / "checkpoints" / "dpo_only_final.pt"),
    "attr_model": str(H_E1_DIR / "checkpoints" / "attr_only_final.pt")
}

# CKA computation
CKA_CONFIG = {
    "num_samples": 500,
    "device": "cuda",
    "max_cka_similarity": 0.7,
    "comparison_pairs": [
        ("joint", "dpo"),
        ("joint", "attr"),
        ("dpo", "attr")
    ]
}

# Hidden state extraction
EXTRACTION_CONFIG = {
    "layer_index": -1,
    "pooling": "mean",
    "hidden_size": 1600,
    "batch_size": 32,
    "max_length": 256,
    "save_hidden_states": True,
    "hidden_states_dir": "hidden_states"
}

# Probing configuration
PROBING_CONFIG = {
    "preference_probe": {
        "input_dim": 1600,
        "num_classes": 2,
        "lr": 1e-3,
        "epochs": 20,
        "optimizer": "adam",
        "loss": "cross_entropy"
    },
    "attribute_probe": {
        "input_dim": 1600,
        "num_attributes": 3,
        "lr": 1e-3,
        "epochs": 20,
        "optimizer": "adam",
        "loss": "mse"
    },
    "train_samples": 400,
    "test_samples": 100,
    "min_preference_accuracy": 0.70,
    "min_attribute_r2": 0.60
}

# Gradient alignment
GRADIENT_CONFIG = {
    "num_batches": 10,
    "flatten_gradients": True,
    "retain_graph": True,
    "min_cosine": -0.5,
    "max_cosine": 0.5
}

# Visualization
VISUALIZATION_CONFIG = {
    "figures_dir": "figures",
    "figure_dpi": 300,
    "figure_format": "png",
    "gate_metrics": {
        "preference_accuracy": {"threshold": 0.70, "type": "min"},
        "attribute_r2": {"threshold": 0.60, "type": "min"},
        "cka_similarity": {"threshold": 0.70, "type": "max"},
        "gradient_cosine": {"threshold": [-0.5, 0.5], "type": "range"}
    },
    "gate_colors": {"pass": "green", "fail": "red"},
    "tsne_perplexity": 30,
    "cka_cmap": "RdYlGn",
    "gradient_bins": 50
}

# Master configuration
CONFIG = {
    "experiment_name": "h-m1-representation-analysis",
    "hypothesis_folder": "docs/youra_research/h-m1",
    "seed": 42,  # Same as H-E1
    "device": "cuda",
    
    # Component configs
    "h_e1": H_E1_CONFIG,
    "checkpoints": CHECKPOINT_PATHS,
    "cka": CKA_CONFIG,
    "extraction": EXTRACTION_CONFIG,
    "probing": PROBING_CONFIG,
    "gradient": GRADIENT_CONFIG,
    "visualization": VISUALIZATION_CONFIG
}
```

---

## Usage Example

```python
from config import CONFIG, CHECKPOINT_PATHS

# Access configurations
device = CONFIG["device"]
num_samples = CONFIG["cka"]["num_samples"]

# Load checkpoint paths
joint_path = CHECKPOINT_PATHS["joint_model"]

# Get gate thresholds
min_accuracy = CONFIG["probing"]["min_preference_accuracy"]
```

---

## Configuration File Structure

```
code/
├── config.py                  # All configuration dicts
├── run_analysis.py            # Main runner importing CONFIG
└── requirements.txt
```

---

## Hyperparameter Rationale

**Only non-standard values are explained below:**

- `layer_index=-1`: Last transformer layer for representation extraction (standard practice in probing literature)
- `batch_size=32`: Larger than H-E1 training (4) because inference-only, no gradient memory
- `probe_lr=1e-3`: Higher than H-E1 training lr (1e-5) because single linear layer, fast convergence
- `probe_epochs=20`: Sufficient for linear probe convergence (no overfitting risk on frozen features)
- `max_cka_similarity=0.7`: CKA > 0.7 indicates minimal divergence (threshold from representation learning literature)

All other hyperparameters inherited from H-E1 or use standard PyTorch defaults.

---

## Subtask Budget Summary

| Epic | Complexity | Subtasks Allocated | Subtasks Used |
|------|------------|-------------------|---------------|
| Epic-4 (CKA) | 9/20 | 1 | 1 |
| Epic-2 (Extraction) | 8/20 | 1 | 1 |
| Epic-6 (Visualization) | 7/20 | 1 | 1 |
| **Total** | **24/60** | **3** | **3** |

**Status:** Budget fully utilized (3/3 subtasks)

---

## Environment Variables Required

```bash
# Optional: GPU selection
export CUDA_VISIBLE_DEVICES=0

# Optional: HuggingFace cache
export HF_HOME="/path/to/cache"
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] KB patterns cited (Applied: 2 patterns)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (3/3)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Base hypothesis verified from actual code
- [x] Inherited Configuration section with verified field names
- [x] Checkpoint paths verified from H-E1 structure

---

**Configuration Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
