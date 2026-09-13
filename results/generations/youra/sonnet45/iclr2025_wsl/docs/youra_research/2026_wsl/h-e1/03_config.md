# Configuration Schema: h-e1 CAWE Implementation

**Hypothesis:** h-e1 (EXISTENCE)
**Date:** 2026-03-19
**Type:** PoC Configuration (Minimal)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation - no existing codebase to analyze
**Config Files Found:** None - designing new config
**Pattern Used:** Hardcoded dict (EXISTENCE PoC standard)

**Note:** Green-field EXISTENCE hypothesis. Using minimal hardcoded configuration approach per EXISTENCE rules.

---

## Applied Patterns

**Applied:** PyTorch Standard Defaults + EXISTENCE Minimal Pattern

---

## EXISTENCE Configuration Rules

This is an EXISTENCE (PoC) hypothesis. Configuration contains:
- ✅ Single fixed config (hardcoded dict)
- ✅ Default values from research (no tuning)
- ✅ 1 seed
- ✅ Minimal epochs (enough to see effect)

**OMITTED (per EXISTENCE rules):**
- ❌ Hyperparameter grids
- ❌ Multiple config options
- ❌ Ablation configs

---

## A-1: Dataset Assembly [Complexity: 11, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# cawe/data/config.py or inline in loader.py

DATASET_CONFIG = {
    # Model zoo composition
    "vit_models": 250,
    "cnn_models": 250,
    "mlp_models": 250,
    "total_models": 750,

    # Train/test split
    "train_size": 600,  # 200 per family
    "test_size": 150,   # 50 per family
    "split_ratio": 0.8,
    "seed": 42,

    # Data paths
    "data_dir": "data/model_zoo",
    "vit_subdir": "vit",
    "cnn_subdir": "cnn",
    "mlp_subdir": "mlp",

    # Model sources
    "vit_source": "timm",  # HuggingFace timm library
    "cnn_source": "torchvision",
    "mlp_source": "zenodo_5645138",  # or "generate_local"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Model Zoo Download | Download/generate 750 models from sources (timm, torchvision, Zenodo) |
| C-1-2 | Metadata Extraction | Compute generalization gap metadata for each model |

---

## A-2: Baseline Implementation [Complexity: 6, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# cawe/baselines/config.py or inline in flat_mlp.py

BASELINE_CONFIG = {
    # Architecture
    "hidden_dims": [512, 256, 128],
    "dropout": 0.2,
    "output_dim": 1,  # Regression head

    # Note: input_dim is variable (depends on flattened weight size)
    # Will be computed dynamically from first batch
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | FlatWeightMLP Model | Implement baseline model class with MLP architecture |
| C-2-2 | Weight Flattening Utility | Implement function to flatten heterogeneous state_dicts |

---

## A-3: Tokenizer Implementation [Complexity: 12, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# cawe/tokenizers/config.py or inline in tokenizers.py

TOKENIZER_CONFIG = {
    # Shared tokenization settings
    "token_dim": 128,  # D dimension for shared token space

    # CNN-specific
    "cnn_kernel_flatten": True,

    # Transformer-specific
    "transformer_qkv_mode": "concat",  # or "separate"

    # MLP-specific
    "mlp_weight_mode": "row_wise",  # or "col_wise"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Architecture-Specific Tokenizers | Implement CNNTokenizer, TransformerTokenizer, MLPTokenizer |
| C-3-2 | State Dict Extraction Logic | Extract relevant weights from heterogeneous state_dicts |

---

## A-4: CAWE Model Integration [Complexity: 14, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# cawe/models/config.py or inline in cawe.py

CAWE_CONFIG = {
    # Tokenization (from A-3)
    "token_dim": 128,

    # NFT backbone
    "nft_channels": 64,
    "nft_layers": 3,  # NPLinear(128,64) -> NPLinear(64,128) -> NPLinear(128,128)

    # Regression head
    "head_hidden_dim": 64,
    "head_dropout": 0.1,
    "output_dim": 1,

    # NFN library integration
    "use_io_embed": True,  # Enable IO embedding for NPLinear
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | CAWE Model Class | Integrate tokenizers + NFT backbone + regression head |
| C-4-2 | NFN Library Wrapper | Wrap nfn.layers for tokenized weight processing |

---

## A-5: Training Pipeline [Complexity: 10, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# scripts/train.py (inline config)

TRAINING_CONFIG = {
    # Optimizer
    "optimizer": "AdamW",
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "betas": (0.9, 0.999),

    # Training
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,

    # Loss
    "loss": "MSE",  # Regression loss for generalization gap

    # Reproducibility
    "seed": 42,
    "cudnn_deterministic": True,

    # Checkpointing
    "save_best_model": True,
    "checkpoint_dir": "checkpoints",
    "checkpoint_metric": "val_spearman",  # Save on best validation Spearman
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Training Loop | Implement epoch training with validation monitoring |
| C-5-2 | Early Stopping Logic | Monitor validation Spearman ρ for early stopping |

---

## A-6: Evaluation Pipeline [Complexity: 9, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# scripts/evaluate.py (inline config)

EVALUATION_CONFIG = {
    # Primary metric
    "metric": "spearman",
    "bootstrap_ci": True,
    "n_bootstrap": 1000,
    "ci_percentile": 95,

    # Secondary metrics
    "per_architecture": True,  # Compute per-family Spearman ρ

    # Success thresholds (for reporting only - not used in code logic)
    "primary_threshold": 0.7,
    "secondary_threshold": 0.65,
    "baseline_gap_threshold": 0.15,

    # Results saving
    "results_dir": "results",
    "results_file": "h-e1_metrics.csv",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Spearman Computation | Implement Spearman ρ with bootstrap CI |
| C-6-2 | Per-Architecture Metrics | Compute metrics for CNN/Transformer/MLP subsets |

---

## A-7: Visualization Generation [Complexity: 8, Budget: 2]

### Configuration (Hardcoded Dict)

```python
# scripts/visualize.py (inline config)

VISUALIZATION_CONFIG = {
    # Figure settings
    "dpi": 300,
    "figsize": (10, 6),
    "style": "seaborn-v0_8-darkgrid",

    # Outputs
    "figures_dir": "figures",
    "formats": ["png", "pdf"],

    # Required figures
    "spearman_comparison": True,
    "per_architecture_bar": True,
    "prediction_scatter": True,
    "tsne_clustering": True,

    # t-SNE settings
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "tsne_random_state": 42,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Metric Visualization | Generate Spearman comparison and per-architecture bar charts |
| C-7-2 | Embedding Visualization | Generate scatter plot and t-SNE clustering |

---

## Global Configuration Summary

### Complete Configuration (Copy-Paste Ready)

**File:** `cawe/config.py` (optional central config, or inline in each module)

```python
"""
CAWE Configuration - h-e1 EXISTENCE PoC
Minimal hardcoded configuration for proof-of-concept validation
"""

# Dataset
DATASET_CONFIG = {
    "vit_models": 250,
    "cnn_models": 250,
    "mlp_models": 250,
    "total_models": 750,
    "train_size": 600,
    "test_size": 150,
    "seed": 42,
    "data_dir": "data/model_zoo",
}

# Tokenization
TOKENIZER_CONFIG = {
    "token_dim": 128,
}

# CAWE Model
CAWE_CONFIG = {
    "token_dim": 128,
    "nft_channels": 64,
    "nft_layers": 3,
    "head_hidden_dim": 64,
    "head_dropout": 0.1,
}

# Baseline
BASELINE_CONFIG = {
    "hidden_dims": [512, 256, 128],
    "dropout": 0.2,
}

# Training
TRAINING_CONFIG = {
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,
    "seed": 42,
}

# Evaluation
EVALUATION_CONFIG = {
    "metric": "spearman",
    "n_bootstrap": 1000,
    "ci_percentile": 95,
}

# Visualization
VISUALIZATION_CONFIG = {
    "dpi": 300,
    "figsize": (10, 6),
}
```

---

## Configuration Rationale

### Non-Standard Values Only

**TOKEN_DIM = 128:**
- Standard for NFT backbone (from NFN NeurIPS 2023 paper)

**NFT_CHANNELS = 64:**
- Follows NFN reference implementation for weight-space learning

**LEARNING_RATE = 1e-4:**
- Standard AdamW learning rate for transformer-based models

**EPOCHS = 100, EARLY_STOPPING_PATIENCE = 10:**
- Standard for PoC training with validation monitoring

**N_BOOTSTRAP = 1000:**
- Standard for bootstrap confidence interval estimation

---

## File Integration Notes

### Option 1: Centralized Config (Recommended for Multi-Module Access)

```python
# cawe/config.py - Central configuration
from dataclasses import dataclass

# Use hardcoded dicts as shown above
```

### Option 2: Module-Level Inline (Recommended for LIGHT tier PoC)

```python
# cawe/data/loader.py - Inline constants
TRAIN_SIZE = 600
TEST_SIZE = 150
SEED = 42

# cawe/models/cawe.py - Inline constants
TOKEN_DIM = 128
NFT_CHANNELS = 64

# scripts/train.py - Inline constants
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
EPOCHS = 100
```

**Recommendation for h-e1:** Use **Option 2 (inline)** for minimal PoC infrastructure (LIGHT tier).

---

## GPU Configuration

**Required before running experiments:**

```bash
# Check available GPUs
nvidia-smi

# Set single GPU (user must manually select empty GPU)
export CUDA_VISIBLE_DEVICES=0  # Replace 0 with empty GPU ID
```

**Code-level GPU handling:**

```python
# In train.py or evaluate.py
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Enable deterministic operations
torch.backends.cudnn.deterministic = True
torch.manual_seed(SEED)
```

---

## Dependencies (requirements.txt)

```txt
torch>=2.0
nfn
timm
torchvision
scipy
numpy
pandas
matplotlib
seaborn
scikit-learn
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## Validation

### Configuration Completeness Check

- [x] All 7 epic tasks have configuration
- [x] Each task has 2/2 subtasks (budget satisfied)
- [x] EXISTENCE rules followed (single fixed config, no grids)
- [x] Hardcoded dict format used
- [x] GPU usage instructions included
- [x] Dependencies specified

### Self-Validation

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] KB pattern noted (PyTorch Standard Defaults)
- [x] Rationale only for non-standard values (all standard in this case)
- [x] Subtask count within budget (2/2 for all tasks)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project - Serena skip is acceptable

---

*Generated by Phase 3 Configuration Agent*
*Ready for Phase 4 Implementation*
