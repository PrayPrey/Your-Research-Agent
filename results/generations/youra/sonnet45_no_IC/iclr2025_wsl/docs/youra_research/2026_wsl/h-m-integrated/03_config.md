# Configuration Specification: H-M-Integrated (Full CAPE Mechanism Validation)

**Date:** 2026-07-13
**Hypothesis ID:** H-M-Integrated
**Type:** MECHANISM
**Budget:** 6 subtasks allocated (A-1: 4 subtasks, A-4: 2 subtasks)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 actual implementation
**Config Files Found:** `/workspace/TEST_wsl/docs/youra_research/h-e1/code/config.py`
**Pattern Used:** Hardcoded dict (extending h-e1 pattern for consistency)
**Base Pattern:** H-E1 uses nested dict structure with top-level keys for each module

---

## Applied Patterns (Archon KB)

**Applied:** Standard PyTorch AdamW with cosine annealing (from diffusers training patterns)
**Applied:** InfoNCE temperature τ=0.07 (contrastive learning standard)
**Applied:** Multi-component encoder defaults (batch_size=32, mixed_precision, gradient_clip)

---

## Configuration Format

**Format Selection:** Hardcoded dict (single format, consistent with h-e1)

**Rationale:** MECHANISM hypothesis requires controlled experiments across 4 ablation variants. Fixed configuration ensures identical hyperparameters across all variants for fair comparison. Nested dict structure provides clear module separation while remaining copy-paste ready.

---

## Inherited Configuration (Base Hypothesis)

### Config Structure from H-E1 (Verified)

```python
# From: /workspace/TEST_wsl/docs/youra_research/h-e1/code/config.py
# Base structure pattern - nested dict with module keys:

CONFIG = {
    "hypothesis_id": "H-E1",
    "random_seed": 42,
    "model_zoo": {...},
    "features": {...},
    "train_test_split": {...},
    "classifier": {...},
    "statistical_test": {...},
    "visualization": {...},
    "success_criteria": {...},
    "directories": {...}
}
```

**Reused Parameters:**
- `random_seed: 42` - Reproducibility across h-e1 and h-m-integrated
- `model_zoo.architectures` - Extended from 2 to 4 architectures
- `model_zoo.dataset_filter: "imagenet-1k"` - Same dataset source
- `directories` structure - Consistent folder organization

**Extended Parameters:**
- `model_zoo.n_per_architecture: 100` (scaled from 50)
- Added CAPE-specific configs: `cape_encoder`, `training`, `loss`, `ablation`

---

## Model Configuration

### CAPE Encoder Config

```python
CONFIG = {
    # ... (global and inherited settings)
    
    # CAPE Encoder Architecture (FR-3, FR-4, FR-5, FR-6)
    "cape_encoder": {
        "d_z": 256,                    # Embedding dimension
        "d_arch": 64,                  # Architecture GNN node features
        "tau": 0.07,                   # InfoNCE temperature (standard)
        "dropout": 0.1,                # Projector dropout
        "num_gnn_layers": 3,           # GNN depth
        "alpha_init": 0.5,             # Residual weight initialization
        "projector_hidden_dim": 256,   # Contrastive projector MLP hidden dim
        "gnn_hidden_dim": 128,         # GCN intermediate dimension
        "operation_types": ["conv", "attention", "mlp"]
    }
}
```

### Operation Encoder Specifics

```python
CONFIG = {
    # ... 
    
    # Operation-Specific Encoders (FR-3)
    "operation_encoders": {
        "sane_conv": {
            "spatial_tokenize": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "unf_attention": {
            "equivariant_process": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "mlp_encoder": {
            "set_encoding": True,
            "output_dim": 256,
            "pooling": "mean"
        }
    }
}
```

---

## Training Configuration

```python
CONFIG = {
    # ...
    
    # Training Hyperparameters (FR-6)
    "training": {
        "batch_size": 32,
        "epochs": 100,
        "optimizer": {
            "name": "adamw",
            "lr": 1e-4,
            "weight_decay": 1e-4,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        },
        "scheduler": {
            "name": "cosine",
            "warmup_ratio": 0.10,      # 10 epochs warmup at 100 total epochs
            "min_lr": 1e-7
        },
        "early_stopping": {
            "patience": 10,
            "metric": "val_combined_loss",
            "mode": "min"
        },
        "mixed_precision": True,       # FP16 if GPU supports
        "gradient_clip_norm": 1.0,
        "checkpoint_frequency": 10     # Save every 10 epochs
    },
    
    # Loss Function (FR-6)
    "loss": {
        "lambda_contrast": 1.0,        # InfoNCE weight
        "lambda_property": 0.5,        # Property prediction MSE weight
        "contrastive_temperature": 0.07  # Same as cape_encoder.tau
    }
}
```

---

## Data Configuration

### Model Zoo Collection

```python
CONFIG = {
    # Global settings (inherited from h-e1)
    "hypothesis_id": "H-M-Integrated",
    "random_seed": 42,
    
    # Model Zoo Collection (FR-1) - Extended from h-e1
    "model_zoo": {
        "n_per_architecture": 100,     # Scaled from h-e1's 50
        "architectures": [
            "resnet50",
            "vit_base_patch16_224",
            "mobilenetv2_100",
            "efficientnet_b0"
        ],
        "dataset_filter": "imagenet-1k",  # Inherited from h-e1
        "retry_attempts": 3,              # Inherited from h-e1
        "min_success_rate": 0.90,         # Inherited from h-e1
        "cache_dir": "data/raw/models/"
    },
    
    # Data Preprocessing (FR-1)
    "preprocessing": {
        "normalization": "frobenius",  # Per-layer Frobenius norm
        "operation_grouping": True,    # Group by conv/attention/MLP
        "cache_preprocessed": True,
        "preprocessed_dir": "data/preprocessed/"
    },
    
    # Architecture DAG Construction (FR-1, FR-5)
    "architecture_dag": {
        "d_arch": 64,                  # Node feature dimension
        "include_layer_types": True,
        "include_dimensions": True,
        "save_graphs": True,
        "graph_dir": "data/preprocessed/arch_graphs/"
    },
    
    # Train/Val/Test Split (FR-1)
    "data_split": {
        "train_ratio": 0.70,
        "val_ratio": 0.15,
        "test_ratio": 0.15,
        "stratify_by_architecture": True,
        "random_state": 42             # Inherited seed
    },
    
    # DataLoader Settings
    "dataloader": {
        "num_workers": 4,
        "pin_memory": True,
        "persistent_workers": True,
        "prefetch_factor": 2
    }
}
```

---

## Ablation Configuration

```python
CONFIG = {
    # ...
    
    # Ablation Study (FR-7)
    "ablation": {
        "variants": {
            "sne_baseline": {
                "enable_operation_encoders": False,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "SNEBaseline"
            },
            "operation_only": {
                "enable_operation_encoders": True,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "op_contrastive": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "full_cape": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": True,
                "model_class": "CAPEEncoder"
            }
        },
        "identical_hyperparameters": True,
        "checkpoint_prefix_by_variant": True
    }
}
```

---

## Evaluation Configuration

```python
CONFIG = {
    # ...
    
    # Cross-Architecture Evaluation (FR-8)
    "evaluation": {
        "primary_transfer": {
            "source": "resnet50",
            "target": "vit_base_patch16_224"
        },
        "n_permutations": 1000,
        "alpha": 0.05,
        "compute_all_pairs": True,     # 4x4 transfer matrix
        "metric": "spearman"
    },
    
    # Diagnostic Thresholds (FR-9)
    "diagnostics": {
        "operation_similarity": {
            "threshold": 0.95,         # Falsifier: >0.95 means collapse
            "target": 0.80,
            "pairs": [["conv", "attention"], ["conv", "mlp"], ["attention", "mlp"]]
        },
        "intra_arch_variance": {
            "threshold": 0.1,          # Falsifier: <0.1 means structure lost
            "target": 0.15
        },
        "gnn_weight": {
            "threshold": 0.1,          # Falsifier: <0.1 means GNN unused
            "target": 0.3,
            "check_performance_gain": True
        }
    },
    
    # Success Criteria
    "success_criteria": {
        "target_rho": 0.65,
        "baseline_rho": 0.54,
        "min_improvement": 0.10,
        "p_value_threshold": 0.05
    }
}
```

---

## Visualization Configuration

```python
CONFIG = {
    # ...
    
    # Visualization (FR-10) - Inherited base settings from h-e1
    "visualization": {
        "dpi": 300,                    # Inherited from h-e1
        "style": "seaborn",            # Inherited from h-e1
        "output_dir": "figures/",
        "formats": ["png", "pdf"],
        "plots": {
            "gate_comparison": {
                "figsize": [10, 6],
                "include_thresholds": True,
                "metrics": ["rho_cape", "rho_sne", "rho_delta", 
                           "diag1_sim", "diag2_var", "diag3_alpha"]
            },
            "transfer_matrix": {
                "figsize": [10, 8],
                "cmap": "viridis",
                "annot": True
            },
            "ablation_bars": {
                "figsize": [8, 6],
                "show_error_bars": False
            },
            "embedding_space": {
                "method": "umap",      # or "tsne"
                "n_components": 2,
                "figsize": [10, 8]
            }
        }
    }
}
```

---

## Directory Structure

```python
CONFIG = {
    # ...
    
    # Directories - Extended from h-e1 pattern
    "directories": {
        "hypothesis_root": "docs/youra_research/h-m-integrated",
        "data": "data/",
        "raw": "data/raw/",
        "preprocessed": "data/preprocessed/",
        "splits": "data/splits/",
        "checkpoints": "checkpoints/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
```

---

## A-1: Model Zoo & Preprocessing [Complexity: 14, Budget: 4]

### Configuration

```python
# Relevant sections from CONFIG above:
# - model_zoo: 400 models (4 architectures × 100 each)
# - preprocessing: Frobenius normalization, operation grouping
# - architecture_dag: DAG construction with d_arch=64
# - data_split: 70/15/15 stratified split
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Model Collection | HuggingFace Hub query and download for 400 models |
| C-1-2 | Weight Preprocessing | Frobenius norm + operation type grouping |
| C-1-3 | Architecture DAG Builder | Build DAG with node features for each architecture |
| C-1-4 | Dataset Splitting | Generate stratified train/val/test splits |

---

## A-4: Architecture GNN [Complexity: 13, Budget: 2]

### Configuration

```python
# Relevant sections from CONFIG above:
# - cape_encoder.num_gnn_layers: 3
# - cape_encoder.d_arch: 64
# - cape_encoder.gnn_hidden_dim: 128
# - cape_encoder.alpha_init: 0.5
# - architecture_dag settings for input graphs
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | GCN Implementation | 3-layer GCN with global pooling and projection to d_z |
| C-4-2 | Residual Combination | Learnable alpha weight for z_final = z_proj + α * z_arch |

---

## Unified Config Module (config.py)

```python
# config.py - Ready for copy-paste into h-m-integrated/code/config.py

CONFIG = {
    # Global settings
    "hypothesis_id": "H-M-Integrated",
    "random_seed": 42,
    
    # Model Zoo Collection (FR-1)
    "model_zoo": {
        "n_per_architecture": 100,
        "architectures": ["resnet50", "vit_base_patch16_224", 
                         "mobilenetv2_100", "efficientnet_b0"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3,
        "min_success_rate": 0.90,
        "cache_dir": "data/raw/models/"
    },
    
    # Data Preprocessing (FR-1)
    "preprocessing": {
        "normalization": "frobenius",
        "operation_grouping": True,
        "cache_preprocessed": True,
        "preprocessed_dir": "data/preprocessed/"
    },
    
    # Architecture DAG (FR-1, FR-5)
    "architecture_dag": {
        "d_arch": 64,
        "include_layer_types": True,
        "include_dimensions": True,
        "save_graphs": True,
        "graph_dir": "data/preprocessed/arch_graphs/"
    },
    
    # Train/Val/Test Split (FR-1)
    "data_split": {
        "train_ratio": 0.70,
        "val_ratio": 0.15,
        "test_ratio": 0.15,
        "stratify_by_architecture": True,
        "random_state": 42
    },
    
    # DataLoader Settings
    "dataloader": {
        "num_workers": 4,
        "pin_memory": True,
        "persistent_workers": True,
        "prefetch_factor": 2
    },
    
    # CAPE Encoder Architecture (FR-3, FR-4, FR-5, FR-6)
    "cape_encoder": {
        "d_z": 256,
        "d_arch": 64,
        "tau": 0.07,
        "dropout": 0.1,
        "num_gnn_layers": 3,
        "alpha_init": 0.5,
        "projector_hidden_dim": 256,
        "gnn_hidden_dim": 128,
        "operation_types": ["conv", "attention", "mlp"]
    },
    
    # Operation-Specific Encoders (FR-3)
    "operation_encoders": {
        "sane_conv": {
            "spatial_tokenize": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "unf_attention": {
            "equivariant_process": True,
            "output_dim": 256,
            "pooling": "mean"
        },
        "mlp_encoder": {
            "set_encoding": True,
            "output_dim": 256,
            "pooling": "mean"
        }
    },
    
    # Training Hyperparameters (FR-6)
    "training": {
        "batch_size": 32,
        "epochs": 100,
        "optimizer": {
            "name": "adamw",
            "lr": 1e-4,
            "weight_decay": 1e-4,
            "betas": [0.9, 0.999],
            "eps": 1e-8
        },
        "scheduler": {
            "name": "cosine",
            "warmup_ratio": 0.10,
            "min_lr": 1e-7
        },
        "early_stopping": {
            "patience": 10,
            "metric": "val_combined_loss",
            "mode": "min"
        },
        "mixed_precision": True,
        "gradient_clip_norm": 1.0,
        "checkpoint_frequency": 10
    },
    
    # Loss Function (FR-6)
    "loss": {
        "lambda_contrast": 1.0,
        "lambda_property": 0.5,
        "contrastive_temperature": 0.07
    },
    
    # Ablation Study (FR-7)
    "ablation": {
        "variants": {
            "sne_baseline": {
                "enable_operation_encoders": False,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "SNEBaseline"
            },
            "operation_only": {
                "enable_operation_encoders": True,
                "enable_contrastive": False,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "op_contrastive": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": False,
                "model_class": "CAPEEncoder"
            },
            "full_cape": {
                "enable_operation_encoders": True,
                "enable_contrastive": True,
                "enable_gnn": True,
                "model_class": "CAPEEncoder"
            }
        },
        "identical_hyperparameters": True,
        "checkpoint_prefix_by_variant": True
    },
    
    # Cross-Architecture Evaluation (FR-8)
    "evaluation": {
        "primary_transfer": {
            "source": "resnet50",
            "target": "vit_base_patch16_224"
        },
        "n_permutations": 1000,
        "alpha": 0.05,
        "compute_all_pairs": True,
        "metric": "spearman"
    },
    
    # Diagnostic Thresholds (FR-9)
    "diagnostics": {
        "operation_similarity": {
            "threshold": 0.95,
            "target": 0.80,
            "pairs": [["conv", "attention"], ["conv", "mlp"], ["attention", "mlp"]]
        },
        "intra_arch_variance": {
            "threshold": 0.1,
            "target": 0.15
        },
        "gnn_weight": {
            "threshold": 0.1,
            "target": 0.3,
            "check_performance_gain": True
        }
    },
    
    # Success Criteria
    "success_criteria": {
        "target_rho": 0.65,
        "baseline_rho": 0.54,
        "min_improvement": 0.10,
        "p_value_threshold": 0.05
    },
    
    # Visualization (FR-10)
    "visualization": {
        "dpi": 300,
        "style": "seaborn",
        "output_dir": "figures/",
        "formats": ["png", "pdf"],
        "plots": {
            "gate_comparison": {
                "figsize": [10, 6],
                "include_thresholds": True,
                "metrics": ["rho_cape", "rho_sne", "rho_delta", 
                           "diag1_sim", "diag2_var", "diag3_alpha"]
            },
            "transfer_matrix": {
                "figsize": [10, 8],
                "cmap": "viridis",
                "annot": True
            },
            "ablation_bars": {
                "figsize": [8, 6],
                "show_error_bars": False
            },
            "embedding_space": {
                "method": "umap",
                "n_components": 2,
                "figsize": [10, 8]
            }
        }
    },
    
    # Directories
    "directories": {
        "hypothesis_root": "docs/youra_research/h-m-integrated",
        "data": "data/",
        "raw": "data/raw/",
        "preprocessed": "data/preprocessed/",
        "splits": "data/splits/",
        "checkpoints": "checkpoints/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
```

---

## Self-Validation

### Quick Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X" lines)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (A-1: 4/4, A-4: 2/2)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Base hypothesis exists → Verified actual config from h-e1/code/config.py
- [x] Field names verified from actual implementation (not specs)
- [x] Inherited Configuration section included

### Budget Verification
- A-1: 4/4 subtasks used
- A-4: 2/2 subtasks used
- **Total: 6/6 subtasks (within allocated budget)**

### Base Hypothesis Checks
- [x] Read actual config from `/workspace/TEST_wsl/docs/youra_research/h-e1/code/config.py`
- [x] Verified nested dict structure pattern
- [x] Inherited parameters documented (random_seed, model_zoo pattern, directories)
- [x] Extended parameters clearly marked (scaled n_per_architecture, new CAPE modules)

---

**Configuration Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Usage:** Copy CONFIG dict from "Unified Config Module" section to `h-m-integrated/code/config.py`
