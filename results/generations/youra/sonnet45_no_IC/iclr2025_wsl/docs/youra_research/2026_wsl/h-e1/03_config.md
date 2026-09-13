# Configuration Specification: H-E1 Operation-Specific Weight Signal Existence

**Date:** 2026-07-13
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Budget:** 2 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch - no existing config patterns to analyze
**Config Files Found:** None - new config design
**Pattern Used:** Hardcoded dict (PoC simplicity)

---

## Applied Patterns (Archon KB)

**Applied:** Standard PyTorch/sklearn PoC defaults

---

## Configuration Format

**Format Selection:** Hardcoded dict (single format for PoC)

**Rationale:** EXISTENCE hypothesis requires minimal, fixed configuration. No hyperparameter tuning or grid search needed for proof-of-concept validation.

---

## A-1: Model Zoo Collection [Complexity: 8, Budget: 2]

### Configuration

```python
MODEL_ZOO_CONFIG = {
    "n_resnet": 50,
    "n_vit": 50,
    "architectures": ["resnet50", "vit_base_patch16_224"],
    "dataset_filter": "imagenet-1k",
    "random_seed": 42,
    "output_dir": "data/",
    "retry_attempts": 3,
    "min_success_rate": 0.90  # Require ≥90 models successfully downloaded
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | HuggingFace Hub Query | Implement model search with filters, sort by downloads |
| C-1-2 | Download + Metadata Storage | Download models, extract accuracy, save to models_metadata.json |

---

## A-2: Feature Extraction Pipeline [Complexity: 10, Budget: 2]

### Configuration

```python
FEATURE_EXTRACTION_CONFIG = {
    "include_spectral": True,
    "top_k_spectral": 5,
    "skip_biases": True,
    "skip_frozen": True,
    "batch_size": 10,  # Process 10 models per batch
    "output_file": "data/weight_features.npz"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Norms + Stats Extraction | Implement L2 norm, mean, std computation per layer |
| C-2-2 | Spectral Norm Extraction | Implement SVD-based top-5 spectral norms for 2D+ parameters |

---

## A-3: Binary Classification Training [Complexity: 9, Budget: 2]

### Configuration

```python
CLASSIFICATION_CONFIG = {
    "train_test_split": {
        "test_size": 0.3,
        "stratify": True,
        "random_state": 42
    },
    "classifier": {
        "algorithm": "LogisticRegression",
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "random_state": 42
    },
    "preprocessing": {
        "scaler": "StandardScaler"
    },
    "ablation": {
        "min_improvement": 0.05  # Require 5% improvement for norms+spectral
    },
    "output_dir": "models/"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Norms-only Baseline | Train LogisticRegression on L2 norms + mean + std |
| C-3-2 | Full Feature Classifier | Train on norms + top-5 spectral norms, compute ablation delta |

---

## A-4: Statistical Testing & Evaluation [Complexity: 11, Budget: 2]

### Configuration

```python
EVALUATION_CONFIG = {
    "statistical_test": {
        "n_permutations": 1000,
        "alpha": 0.05
    },
    "visualization": {
        "dpi": 300,
        "style": "seaborn",
        "output_dir": "figures/"
    },
    "success_criteria": {
        "target_accuracy": 0.80,
        "partial_threshold": 0.70,
        "min_p_value": 0.05,
        "min_ablation_improvement": 0.05
    },
    "output_dir": "results/"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Permutation Test + Metrics | Implement 1000-iteration permutation test, compute p-value and metrics.json |
| C-4-2 | Visualization Generation | Generate gate_comparison.png, confusion_matrix.png, feature_importance.png, permutation_dist.png |

---

## Global Configuration

```python
GLOBAL_CONFIG = {
    "hypothesis_id": "H-E1",
    "random_seed": 42,
    "hypothesis_folder": "docs/youra_research/h-e1",
    "directories": {
        "data": "data/",
        "models": "models/",
        "results": "results/",
        "figures": "figures/"
    }
}
```

---

## Unified Config Module (config.py)

```python
# config.py - Ready for copy-paste

CONFIG = {
    # Global settings
    "hypothesis_id": "H-E1",
    "random_seed": 42,
    
    # Model Zoo Collection (A-1)
    "model_zoo": {
        "n_resnet": 50,
        "n_vit": 50,
        "architectures": ["resnet50", "vit_base_patch16_224"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3,
        "min_success_rate": 0.90
    },
    
    # Feature Extraction (A-2)
    "features": {
        "include_spectral": True,
        "top_k_spectral": 5,
        "skip_biases": True,
        "skip_frozen": True,
        "batch_size": 10
    },
    
    # Classification (A-3)
    "train_test_split": {
        "test_size": 0.3,
        "stratify": True,
        "random_state": 42
    },
    "classifier": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "random_state": 42
    },
    
    # Statistical Testing (A-4)
    "statistical_test": {
        "n_permutations": 1000,
        "alpha": 0.05
    },
    
    # Visualization
    "visualization": {
        "dpi": 300,
        "style": "seaborn"
    },
    
    # Success Criteria
    "success_criteria": {
        "target_accuracy": 0.80,
        "partial_threshold": 0.70,
        "min_p_value": 0.05,
        "min_ablation_improvement": 0.05
    },
    
    # Directory Structure
    "directories": {
        "data": "data/",
        "models": "models/",
        "results": "results/",
        "figures": "figures/"
    }
}
```

---

## Self-Validation

### Quick Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2 per task)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included

### Serena MCP Validation
- [x] Green-field project → Serena skip acceptable (noted in Codebase Analysis)

### Budget Verification
- A-1: 2/2 subtasks used
- A-2: 2/2 subtasks used
- A-3: 2/2 subtasks used
- A-4: 2/2 subtasks used
- **Total: 8/8 subtasks (within 2 per task budget)**

---

**Configuration Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Usage:** Copy CONFIG dict from "Unified Config Module" section
