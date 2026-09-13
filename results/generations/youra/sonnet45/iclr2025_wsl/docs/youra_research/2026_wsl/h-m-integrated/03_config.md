# Configuration Schema: h-m-integrated CAWE Mechanism Validation

**Hypothesis:** h-m-integrated (MECHANISM)
**Date:** 2026-03-19
**Type:** FULL Configuration

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 base code
**Config Files Found:** Inline configurations in h-e1/code/scripts/train.py, h-e1/code/cawe/models/cawe.py, h-e1/code/cawe/data/loader.py
**Pattern Used:** Hardcoded dict (following h-e1 pattern)

**Verified from:** h-e1/code/ (actual implementation)

---

## Applied Patterns

**Applied:** PyTorch Standard Defaults + h-e1 CAWE Configuration Pattern

---

## Inherited Configuration (Base Hypothesis)

### Config Values (From Actual h-e1 Code)

The following configuration values are inherited from h-e1 base hypothesis:

```python
# From: h-e1/code/cawe/models/cawe.py (ACTUAL CODE - lines 22-25)
token_dim = 128           # CAWE tokenizer output dimension
nft_channels = 64         # NFT backbone hidden channels

# From: h-e1/code/scripts/train.py (ACTUAL CODE - lines 78-84, 111)
lr = 1e-4                 # Learning rate (argparse default)
batch_size = 16           # Batch size (PoC default, can be increased)
epochs = 10               # Epochs (PoC default)
patience = 5              # Early stopping patience
weight_decay = 1e-2       # AdamW weight decay (line 111)

# From: h-e1/code/cawe/data/loader.py (ACTUAL CODE - lines 377-378)
seed = 42                 # Random seed
train_samples = 600       # Default train samples (full experiment)
val_samples = 150         # Default validation samples
test_samples = 150        # Default test samples

# From: h-e1/code/cawe/models/cawe.py (ACTUAL CODE - lines 46-48)
regression_head_hidden = 64   # Regression head hidden dimension
regression_dropout = 0.1      # Regression head dropout
```

**Verified from**: h-e1/code/ (actual implementation - field names and defaults match exactly)

---

## Extended Configuration (h-m-integrated)

### Modifications for Mechanism Validation

```python
# Training modifications (from PoC → Full experiment)
BATCH_SIZE = 32           # Increased from 16 for efficiency
EPOCHS = 100              # Increased from 10 for full training
EARLY_STOPPING_PATIENCE = 10  # Increased from 5 for full training

# Dataset modifications (per-family ablation support)
PER_FAMILY_TRAIN_SIZE = 200   # Per architecture family
PER_FAMILY_TEST_SIZE = 50     # Per architecture family
FULL_TRAIN_SIZE = 600         # Total: 200×3
FULL_TEST_SIZE = 150          # Total: 50×3
```

---

## B-1: Per-Family Ablation [Complexity: 13, Budget: 3]

**Applied:** Standard training loop with architecture filtering

### Configuration (Hardcoded Dict)

```python
# scripts/train_per_family.py (inline config)

PER_FAMILY_CONFIG = {
    # Inherited from h-e1
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "token_dim": 128,
    "nft_channels": 64,
    "regression_head_hidden": 64,
    "regression_dropout": 0.1,
    "seed": 42,

    # Modified for full training
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,

    # Per-family ablation settings
    "families": ["cnn", "transformer", "mlp"],
    "train_samples_per_family": 200,
    "test_samples_per_family": 50,

    # Success threshold
    "threshold_rho": 0.7,

    # Checkpointing
    "checkpoint_dir": "checkpoints/per_family",
    "save_models": ["cawe_cnn_only.pt", "cawe_transformer_only.pt", "cawe_mlp_only.pt"],
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | PerFamilyTrainer Class | Implement training wrapper with architecture filtering |
| C-1-2 | Family Dataset Filter | Filter ModelZooDataset by architecture family |
| C-1-3 | Per-Family Evaluation | Compute Spearman ρ for each architecture subset |

---

## B-2: Clustering Validation [Complexity: 11, Budget: 2]

**Applied:** sklearn silhouette score with NFT embeddings

### Configuration (Hardcoded Dict)

```python
# cawe/evaluation/clustering.py (inline config)

CLUSTERING_CONFIG = {
    # Embedding extraction
    "embedding_dim": 128,  # NFT backbone output dimension (token_dim)

    # Clustering evaluation
    "num_clusters": 3,  # CNN, Transformer, MLP
    "cluster_labels": {"cnn": 0, "transformer": 1, "mlp": 2},

    # Success threshold
    "threshold_silhouette": 0.5,

    # Visualization
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "tsne_random_state": 42,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Embedding Extraction | Extract NFT backbone outputs for all 750 models |
| C-2-2 | Silhouette Computation | Compute sklearn silhouette score with 3 cluster labels |

---

## B-3: Random Forest Baseline [Complexity: 12, Budget: 2]

**Applied:** sklearn RandomForestRegressor with weight feature engineering

### Configuration (Hardcoded Dict)

```python
# cawe/baselines/random_forest.py (inline config)

RF_CONFIG = {
    # Random Forest model
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,

    # Feature extraction
    "features": [
        "l2_norm",          # Layer-wise L2 norms
        "sparsity",         # % near-zero weights (threshold=1e-5)
        "spectral_radius",  # Largest eigenvalue per layer
        "mean_std_stats",   # Weight mean/std per layer
    ],
    "sparsity_threshold": 1e-5,

    # Dataset
    "train_samples": 600,
    "test_samples": 150,

    # Success threshold
    "threshold_delta_rho": 0.1,  # Δρ = ρ_CAWE - ρ_RF > 0.1
    "p_value_threshold": 0.01,   # Wilcoxon signed-rank test

    # Checkpointing
    "checkpoint_path": "checkpoints/rf_baseline.pkl",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | WeightFeatureExtractor | Extract engineered features from state_dicts |
| C-3-2 | RandomForestBaseline | Train and evaluate sklearn RandomForestRegressor |

---

## B-4: Robustness Validator [Complexity: 14, Budget: 3]

**Applied:** Tokenization variants with alternative hyperparameters

### Configuration (Hardcoded Dict)

```python
# cawe/evaluation/robustness.py (inline config)

ROBUSTNESS_CONFIG = {
    # Inherited base config
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,
    "seed": 42,

    # Tokenization variants (4 total)
    "tokenization_variants": [
        {"name": "D64", "token_dim": 64},
        {"name": "D256", "token_dim": 256},
        {"name": "alt_layer", "token_dim": 128, "layer_selection": "skip_first_last"},
        {"name": "weight_norm", "token_dim": 128, "normalize_weights": True},
    ],

    # Token dimension variants (3 total)
    "dimension_variants": [64, 128, 256],

    # Success thresholds
    "threshold_rho_variant": 0.65,
    "min_tokenization_variants_pass": 2,  # Out of 4
    "min_dimension_variants_pass": 2,     # Out of 3

    # Checkpointing
    "checkpoint_dir": "checkpoints/robustness",
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Tokenization Variant Training | Train CAWE with 4 tokenization variants |
| C-4-2 | Dimension Variant Training | Train CAWE with 3 token dimensions (D=64,128,256) |
| C-4-3 | Robustness Evaluation | Aggregate pass/fail counts across variants |

---

## B-5: Flat Baseline Training [Complexity: 7, Budget: 2]

**Applied:** h-e1 FlatWeightMLP baseline (reused)

### Configuration (Hardcoded Dict)

```python
# scripts/train_flat_baseline.py (inline config)

FLAT_BASELINE_CONFIG = {
    # Inherited from h-e1 baseline
    "hidden_dims": [512, 256, 128],
    "dropout": 0.2,
    "output_dim": 1,

    # Training (same as CAWE for fair comparison)
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,
    "seed": 42,

    # Dataset
    "train_samples": 600,
    "test_samples": 150,

    # Success threshold
    "threshold_delta_rho": 0.15,  # Δρ = ρ_CAWE - ρ_flat > 0.15
    "p_value_threshold": 0.001,   # Paired t-test

    # Checkpointing
    "checkpoint_path": "checkpoints/flat_mlp.pt",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | FlatWeightMLP Training | Train h-e1 baseline on full 600-model dataset |
| C-5-2 | Baseline Comparison | Compute Δρ with paired t-test |

---

## B-6: Full CAWE Training [Complexity: 8, Budget: 2]

**Applied:** h-e1 CAWE training on full dataset

### Configuration (Hardcoded Dict)

```python
# scripts/train_full_cawe.py (inline config)

FULL_CAWE_CONFIG = {
    # Inherited from h-e1
    "learning_rate": 1e-4,
    "weight_decay": 1e-2,
    "token_dim": 128,
    "nft_channels": 64,
    "regression_head_hidden": 64,
    "regression_dropout": 0.1,
    "seed": 42,

    # Modified for full training
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10,

    # Dataset (full heterogeneous model zoo)
    "train_samples": 600,  # 200 per family
    "val_samples": 150,    # 50 per family
    "test_samples": 150,   # 50 per family

    # Checkpointing
    "checkpoint_path": "checkpoints/cawe_full.pt",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Full Dataset Training | Train CAWE on full 600-model heterogeneous dataset |
| C-6-2 | Full Model Evaluation | Evaluate on 150-model test set for clustering/baseline use |

---

## B-7: Mechanism Evaluation Pipeline [Complexity: 15, Budget: 3]

**Applied:** Comprehensive 5-component evaluation orchestration

### Configuration (Hardcoded Dict)

```python
# scripts/evaluate_mechanism.py (inline config)

MECHANISM_EVAL_CONFIG = {
    # Component thresholds (from PRD)
    "thresholds": {
        "per_family_rho": 0.7,
        "silhouette": 0.5,
        "delta_flat": 0.15,
        "delta_rf": 0.1,
        "robustness_tokenization": 2,  # Out of 4
        "robustness_dimensions": 2,    # Out of 3
    },

    # Statistical tests
    "paired_t_test_alpha": 0.001,
    "wilcoxon_alpha": 0.01,

    # Bootstrap CI
    "n_bootstrap": 1000,
    "ci_percentile": 95,

    # Gate condition
    "min_components_pass": 3,  # Out of 5

    # Results output
    "results_file": "results/mechanism_metrics.csv",
    "results_summary": "results/mechanism_summary.json",
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Component Aggregation | Aggregate results from all 5 components |
| C-7-2 | Statistical Testing | Run paired t-test (Component 3), Wilcoxon (Component 4) |
| C-7-3 | Gate Evaluation | Determine pass/fail for each component and overall gate |

---

## B-8: Visualization Suite [Complexity: 10, Budget: 2]

**Applied:** matplotlib + seaborn for 5-component visualization

### Configuration (Hardcoded Dict)

```python
# scripts/visualize_mechanism.py (inline config)

VISUALIZATION_CONFIG = {
    # Figure settings
    "dpi": 300,
    "figsize": (10, 6),
    "style": "seaborn-v0_8-darkgrid",

    # Required figures
    "figures": [
        "component_matrix.png",         # 5-component pass/fail matrix
        "per_family_comparison.png",    # Component 1: Bar chart with threshold
        "clustering_tsne.png",          # Component 2: t-SNE with silhouette
        "baseline_comparison.png",      # Components 3+4: Grouped bar chart
        "robustness_heatmap.png",       # Component 5: Heatmap grid
    ],

    # Output directory
    "figures_dir": "figures",
    "formats": ["png", "pdf"],

    # t-SNE settings (Component 2)
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "tsne_random_state": 42,

    # Heatmap settings (Component 5)
    "heatmap_cmap": "RdYlGn",
    "heatmap_annot": True,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Component Figures | Generate 5 component-specific figures |
| C-8-2 | Pass/Fail Matrix | Generate overall component pass/fail matrix |

---

## Global Configuration Summary

### Complete Configuration (Copy-Paste Ready)

**File:** `config.py` (optional central config, or inline in each module)

```python
"""
h-m-integrated Configuration - CAWE Mechanism Validation
Extends h-e1 configuration with 5-component mechanism validation settings
"""

# ============================================================================
# INHERITED FROM H-E1 (Verified from actual code)
# ============================================================================

# Model architecture (from h-e1/code/cawe/models/cawe.py)
TOKEN_DIM = 128
NFT_CHANNELS = 64
REGRESSION_HEAD_HIDDEN = 64
REGRESSION_DROPOUT = 0.1

# Training (from h-e1/code/scripts/train.py)
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-2
SEED = 42

# Dataset (from h-e1/code/cawe/data/loader.py)
DEFAULT_TRAIN_SAMPLES = 600
DEFAULT_VAL_SAMPLES = 150
DEFAULT_TEST_SAMPLES = 150

# ============================================================================
# EXTENDED FOR H-M-INTEGRATED (Mechanism Validation)
# ============================================================================

# Training modifications (full experiment vs h-e1 PoC)
BATCH_SIZE = 32                    # Increased from 16
EPOCHS = 100                       # Increased from 10
EARLY_STOPPING_PATIENCE = 10       # Increased from 5

# Per-family ablation (Component 1)
PER_FAMILY_CONFIG = {
    "families": ["cnn", "transformer", "mlp"],
    "train_samples_per_family": 200,
    "test_samples_per_family": 50,
    "threshold_rho": 0.7,
}

# Clustering validation (Component 2)
CLUSTERING_CONFIG = {
    "embedding_dim": 128,
    "num_clusters": 3,
    "threshold_silhouette": 0.5,
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
}

# Random Forest baseline (Component 3)
RF_CONFIG = {
    "n_estimators": 100,
    "max_depth": 10,
    "sparsity_threshold": 1e-5,
    "threshold_delta_rho": 0.1,
}

# Robustness validation (Component 4)
ROBUSTNESS_CONFIG = {
    "tokenization_variants": [
        {"name": "D64", "token_dim": 64},
        {"name": "D256", "token_dim": 256},
        {"name": "alt_layer", "token_dim": 128, "layer_selection": "skip_first_last"},
        {"name": "weight_norm", "token_dim": 128, "normalize_weights": True},
    ],
    "dimension_variants": [64, 128, 256],
    "threshold_rho_variant": 0.65,
    "min_tokenization_variants_pass": 2,
    "min_dimension_variants_pass": 2,
}

# Flat baseline (Component 5 - reuse)
FLAT_BASELINE_CONFIG = {
    "hidden_dims": [512, 256, 128],
    "dropout": 0.2,
    "threshold_delta_rho": 0.15,
}

# Mechanism evaluation pipeline
MECHANISM_EVAL_CONFIG = {
    "min_components_pass": 3,
    "paired_t_test_alpha": 0.001,
    "wilcoxon_alpha": 0.01,
    "n_bootstrap": 1000,
}

# Visualization
VISUALIZATION_CONFIG = {
    "dpi": 300,
    "figsize": (10, 6),
    "style": "seaborn-v0_8-darkgrid",
}
```

---

## Configuration Rationale

### Non-Standard Values Only

**BATCH_SIZE = 32 (increased from h-e1's 16):**
- Full experiment requires higher throughput
- 32 is standard for transformer-based models with available GPU memory

**EPOCHS = 100, EARLY_STOPPING_PATIENCE = 10 (increased from h-e1's 10/5):**
- Full training (not PoC) requires convergence
- Early stopping prevents overfitting

**THRESHOLD_RHO = 0.7 (Component 1):**
- Strict per-family performance requirement (from PRD FR-3)

**THRESHOLD_SILHOUETTE = 0.5 (Component 2):**
- Standard moderate cluster separation threshold

**RF_N_ESTIMATORS = 100, MAX_DEPTH = 10 (Component 3):**
- sklearn RandomForest defaults optimized for tabular data

**MIN_COMPONENTS_PASS = 3:**
- Gate condition requires majority (3/5) of components pass

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
# In all training scripts
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

- [x] All 8 epic tasks have configuration
- [x] Subtask budgets satisfied (B-1: 3/3, B-2: 2/2, B-3: 2/2, B-4: 3/3, B-5: 2/2, B-6: 2/2, B-7: 3/3, B-8: 2/2)
- [x] Inherited h-e1 config verified from actual code
- [x] Field names match h-e1 implementation exactly
- [x] Hardcoded dict format used (following h-e1 pattern)
- [x] GPU usage instructions included
- [x] Dependencies specified
- [x] Codebase Analysis section included

### Self-Validation

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] KB pattern noted (PyTorch Standard Defaults)
- [x] Rationale only for non-standard values
- [x] Base hypothesis config verification completed
- [x] "Inherited Configuration" section included
- [x] Total length within budget (~400 lines)

---

*Generated by Phase 3 Configuration Agent*
*Ready for Phase 4 Implementation*
