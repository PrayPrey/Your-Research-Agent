---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
document_type: config
created_at: 2026-05-12
author: Phase 3 Configuration Agent
version: 1.0
---

# Configuration Design: H-E1 Quotient Space Existence

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Config Files Found**: None - new config design
**Pattern Used**: Hardcoded dict (EXISTENCE PoC - minimal config)

---

## A-1: Dataset Infrastructure [Complexity: 14, Budget: 3 subtasks]

**Applied**: Standard PyTorch data loading defaults

### Configuration (Hardcoded Dict)

```python
DATASET_CONFIG = {
    # HuggingFace Model Hub settings
    "cache_dir": "./data/model_zoo",
    "architectures": ["CNN", "Transformer", "RNN"],
    "size_range": (10_000_000, 100_000_000),  # 10M-100M parameters
    
    # Dataset splits
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    
    # Preprocessing
    "normalize_per_layer": True,
    "max_weight_dim": 100_000,  # Truncate if larger
    
    # Data loading
    "batch_size": 32,
    "num_workers": 4,
    "pin_memory": True
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Download config | HuggingFace API settings, retry logic params |
| C-1-2 | Preprocessing config | Normalization, padding/truncation parameters |
| C-1-3 | DataLoader config | Batch size, workers, pin_memory |

---

## A-2: Baseline Model [Complexity: 11, Budget: 2 subtasks]

**Applied**: Deep Sets architecture defaults (Zaheer et al. 2017)

### Configuration (Hardcoded Dict)

```python
BASELINE_CONFIG = {
    # Architecture
    "weight_dim": 100_000,  # Max flattened weight vector size
    "hidden_dim": 128,
    "output_dim": 32,  # K = 32 (default)
    
    # Encoder (phi function)
    "encoder_layers": [512, 256, 128],
    "encoder_activation": "relu",
    
    # Decoder (rho function)
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    
    # Reconstruction decoder
    "reconstruct_layers": [256, 512, 100_000],
    
    # Aggregation
    "aggregation": "sum"  # Permutation-invariant pooling
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Encoder architecture | Hidden dims, activations for phi/rho |
| C-2-2 | Reconstruction decoder | Layers for K-dim -> weight space mapping |

---

## A-3: Proposed Model [Complexity: 16, Budget: 3 subtasks]

**Applied**: Deep Sets + architecture embeddings

### Configuration (Hardcoded Dict)

```python
PROPOSED_CONFIG = {
    # Architecture
    "weight_dim": 100_000,
    "K": 32,  # Quotient space dimension (ablation: 16, 32, 64)
    "hidden_dim": 256,
    
    # Architecture embedding
    "num_arch_classes": 3,  # CNN, Transformer, RNN
    "arch_embed_dim": 64,
    
    # Encoder (phi function)
    "encoder_layers": [256, 128],  # After concat with arch_embed
    "encoder_activation": "relu",
    "use_layer_norm": True,  # Stability
    
    # Decoder (rho function)
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    
    # Reconstruction decoder
    "reconstruct_layers": [256, 512, 100_000],
    
    # Aggregation
    "aggregation": "mean"  # Permutation-invariant pooling
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Architecture embedding | Embedding dims for CNN/Transformer/RNN |
| C-3-2 | Encoder config | Hidden dims with LayerNorm for stability |
| C-3-3 | Reconstruction config | K-dim -> weight space decoder layers |

---

## A-4: Training Pipeline [Complexity: 12, Budget: 3 subtasks]

**Applied**: Standard Adam + CosineAnnealing

### Configuration (Hardcoded Dict)

```python
TRAINING_CONFIG = {
    # Optimizer
    "optimizer": "adam",
    "learning_rate": 1e-3,
    "betas": (0.9, 0.999),
    "weight_decay": 1e-4,
    
    # Learning rate schedule
    "scheduler": "cosine_annealing",
    "T_max": 100,  # Total epochs
    
    # Training
    "num_epochs": 100,
    "batch_size": 32,
    
    # Loss weights
    "lambda_equiv": 0.5,  # Equivariance loss weight (ablation: 0.0, 0.25, 0.5, 0.75, 1.0)
    
    # Early stopping
    "patience": 10,
    "min_delta": 1e-4,
    
    # Checkpointing
    "checkpoint_dir": "./checkpoints",
    "save_best_only": True,
    
    # Reproducibility
    "seed": 42,
    "deterministic": True
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Optimizer config | Adam parameters, learning rate schedule |
| C-4-2 | Training loop config | Epochs, loss weights, early stopping |
| C-4-3 | Checkpointing config | Save paths, best model selection |

---

## A-5: Evaluation Metrics [Complexity: 15, Budget: 3 subtasks]

**Applied**: Custom metric thresholds from hypothesis

### Configuration (Hardcoded Dict)

```python
EVALUATION_CONFIG = {
    # Metric computation
    "num_permutations": 1000,  # For kernel robustness
    "divergence_threshold": 0.01,  # D < 0.01 for robustness
    
    # Target thresholds (from hypothesis success criteria)
    "target_reconstruction_error": 10.0,  # <10%
    "target_frozen_k_gen": 10.0,  # R_RNN <10%
    "target_kernel_robustness": 90.0,  # ≥90%
    
    # Frozen-K generalization
    "frozen_k_train_archs": ["CNN", "Transformer"],  # Train on these
    "frozen_k_test_arch": "RNN",  # Test on this
    
    # Output paths
    "results_dir": "./results",
    "metrics_file": "metrics.csv"
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Metric thresholds | Target values from hypothesis criteria |
| C-5-2 | Robustness config | Num permutations, divergence threshold |
| C-5-3 | Output config | Results paths, logging format |

---

## A-6: Ablation Studies [Complexity: 9, Budget: 2 subtasks]

**Applied**: Hyperparameter sweep ranges from hypothesis

### Configuration (Hardcoded Dict)

```python
ABLATION_CONFIG = {
    # λ_equiv ablation (from hypothesis controlled variables)
    "lambda_equiv_values": [0.0, 0.25, 0.5, 0.75, 1.0],
    
    # K dimensionality ablation (from hypothesis controlled variables)
    "K_values": [16, 32, 64],
    
    # Experiment tracking
    "ablation_results_dir": "./results/ablations",
    "save_all_checkpoints": False  # Save only best per config
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | λ_equiv sweep config | Values for equivariance loss weight ablation |
| C-6-2 | K sweep config | Values for quotient space dimensionality ablation |

---

## A-7: Visualization [Complexity: 10, Budget: 2 subtasks]

**Applied**: Matplotlib defaults + scikit-learn

### Configuration (Hardcoded Dict)

```python
VISUALIZATION_CONFIG = {
    # Figure output
    "figures_dir": "./figures",
    "dpi": 300,
    "format": "png",
    
    # t-SNE/UMAP
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "random_state": 42,
    
    # Plot styling
    "figsize": (10, 6),
    "colors": {
        "CNN": "blue",
        "Transformer": "orange",
        "RNN": "green"
    },
    
    # Gate metrics chart
    "gate_metrics_names": [
        "Reconstruction Error (%)",
        "Frozen-K Generalization (%)",
        "Kernel Robustness (%)"
    ]
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Plot config | Figure size, DPI, output format |
| C-7-2 | t-SNE config | Perplexity, iterations, random state |

---

## Master Configuration

**For Phase 4 implementation, combine all configs:**

```python
# config.py - Master configuration file

# Dataset
DATASET_CONFIG = {
    "cache_dir": "./data/model_zoo",
    "architectures": ["CNN", "Transformer", "RNN"],
    "size_range": (10_000_000, 100_000_000),
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "normalize_per_layer": True,
    "max_weight_dim": 100_000,
    "batch_size": 32,
    "num_workers": 4,
    "pin_memory": True
}

# Model - Baseline
BASELINE_CONFIG = {
    "weight_dim": 100_000,
    "hidden_dim": 128,
    "output_dim": 32,
    "encoder_layers": [512, 256, 128],
    "encoder_activation": "relu",
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    "reconstruct_layers": [256, 512, 100_000],
    "aggregation": "sum"
}

# Model - Proposed
PROPOSED_CONFIG = {
    "weight_dim": 100_000,
    "K": 32,
    "hidden_dim": 256,
    "num_arch_classes": 3,
    "arch_embed_dim": 64,
    "encoder_layers": [256, 128],
    "encoder_activation": "relu",
    "use_layer_norm": True,
    "decoder_layers": [128, 256],
    "decoder_activation": "relu",
    "reconstruct_layers": [256, 512, 100_000],
    "aggregation": "mean"
}

# Training
TRAINING_CONFIG = {
    "optimizer": "adam",
    "learning_rate": 1e-3,
    "betas": (0.9, 0.999),
    "weight_decay": 1e-4,
    "scheduler": "cosine_annealing",
    "T_max": 100,
    "num_epochs": 100,
    "batch_size": 32,
    "lambda_equiv": 0.5,
    "patience": 10,
    "min_delta": 1e-4,
    "checkpoint_dir": "./checkpoints",
    "save_best_only": True,
    "seed": 42,
    "deterministic": True
}

# Evaluation
EVALUATION_CONFIG = {
    "num_permutations": 1000,
    "divergence_threshold": 0.01,
    "target_reconstruction_error": 10.0,
    "target_frozen_k_gen": 10.0,
    "target_kernel_robustness": 90.0,
    "frozen_k_train_archs": ["CNN", "Transformer"],
    "frozen_k_test_arch": "RNN",
    "results_dir": "./results",
    "metrics_file": "metrics.csv"
}

# Ablation
ABLATION_CONFIG = {
    "lambda_equiv_values": [0.0, 0.25, 0.5, 0.75, 1.0],
    "K_values": [16, 32, 64],
    "ablation_results_dir": "./results/ablations",
    "save_all_checkpoints": False
}

# Visualization
VISUALIZATION_CONFIG = {
    "figures_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "tsne_perplexity": 30,
    "tsne_n_iter": 1000,
    "random_state": 42,
    "figsize": (10, 6),
    "colors": {
        "CNN": "blue",
        "Transformer": "orange",
        "RNN": "green"
    },
    "gate_metrics_names": [
        "Reconstruction Error (%)",
        "Frozen-K Generalization (%)",
        "Kernel Robustness (%)"
    ]
}
```

---

**Document Status**: Complete
**Format**: Hardcoded dict (EXISTENCE PoC - no dataclass overhead)
**Next Phase**: Phase 4 - Copy-paste these configs into implementation
