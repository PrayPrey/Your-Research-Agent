# Configuration Schema: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18
**Author:** Phase 3 Configuration Agent
**Infrastructure:** LIGHT tier (hardcoded constants)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation - no existing config to verify
**Config Files Found:** None - new config design
**Pattern Used:** Hardcoded dict (LIGHT tier requirement)

---

## Knowledge Base Patterns Applied

Applied: Minimal PoC configuration pattern (hardcoded constants for standalone scripts)

---

## Configuration Format

LIGHT tier infrastructure requires hardcoded configuration. Using Python dictionary constants for copy-paste simplicity.

---

## A-1: Environment Setup [Complexity: 5, Budget: 0 subtasks]

**Applied**: Standard package installation defaults

### Configuration (Hardcoded Dict)

```python
# config.py - Environment Configuration
ENV_CONFIG = {
    "python_version": "3.9+",
    "cuda_version": "11.8+",
    "packages": [
        "evalplus",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "radon",
        "lizard",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "pandas",
        "numpy"
    ],
    "min_gpu_vram_gb": 14
}
```

---

## A-2: Data Loading [Complexity: 6, Budget: 0 subtasks]

**Applied**: EvalPlus defaults from documentation

### Configuration (Hardcoded Dict)

```python
# config.py - Data Configuration
DATA_CONFIG = {
    "dataset_name": "evalplus/humanevalplus",
    "num_problems": 164,
    "dataset_split": "test",
    "cache_dir": "./cache/datasets"
}
```

---

## A-3: Model Management [Complexity: 15, Budget: 0 subtasks]

**Applied**: HuggingFace transformers standard generation params

### Configuration (Hardcoded Dict)

```python
# config.py - Model Configuration
MODEL_CONFIG = {
    "models": [
        # Execution-focused (2-3 models)
        ("bigcode/selfcodealign-7b", "execution"),
        ("codellama/CodeLlama-7b-Python-hf", "execution"),

        # Preference-focused (2-3 models)
        ("codellama/CodeLlama-7b-Instruct-hf", "preference"),

        # Baseline (1-2 models)
        ("codellama/CodeLlama-7b-hf", "baseline"),
        ("bigcode/starcoder", "baseline"),
    ],
    "device_map": "auto",
    "torch_dtype": "float16",
    "trust_remote_code": True,
    "cache_dir": "./cache/models"
}

GENERATION_CONFIG = {
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "do_sample": True,
    "num_return_sequences": 1,
    "pad_token_id": 0  # Set to model-specific if needed
}
```

---

## A-4: Profiling Pipeline [Complexity: 16, Budget: 0 subtasks]

**Applied**: Standard profiling library defaults

### Configuration (Hardcoded Dict)

```python
# config.py - Profiling Configuration
PROFILING_CONFIG = {
    "num_samples_per_task": 64,
    "execution_timeout_sec": 3.0,
    "num_workers": 4,
    "random_seed": 42,

    # Correctness profiling (pass@k)
    "pass_k_values": [1, 10, 100],

    # Complexity profiling
    "complexity_metrics": ["cyclomatic", "ast_depth"],

    # Efficiency profiling
    "efficiency_metrics": ["runtime", "memory"],
    "profile_only_correct": True  # Only profile passing samples
}
```

---

## A-5: Clustering Analysis [Complexity: 13, Budget: 0 subtasks]

**Applied**: sklearn clustering pipeline pattern (StandardScaler → PCA → KMeans)

### Configuration (Hardcoded Dict)

```python
# config.py - Clustering Configuration
CLUSTERING_CONFIG = {
    "standardize": True,
    "pca_components": 3,
    "k_clusters": 3,
    "kmeans_init": "k-means++",
    "kmeans_n_init": 10,
    "random_state": 42,

    # Effect size computation
    "cohens_d_threshold": 1.5,  # Gate requirement
    "bootstrap_iterations": 1000
}
```

---

## A-6: Visualization [Complexity: 11, Budget: 0 subtasks]

**Applied**: Matplotlib publication defaults

### Configuration (Hardcoded Dict)

```python
# config.py - Visualization Configuration
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),

    # Color palette (color-blind friendly)
    "colors": {
        "execution": "#0173B2",  # Blue
        "preference": "#DE8F05",  # Orange
        "baseline": "#029E73"     # Green
    },

    # Figure types
    "figures": [
        "3d_scatter",
        "heatmap",
        "boxplots",
        "dendrogram",
        "effect_size",
        "gate_metrics"
    ]
}
```

---

## A-7: Experiment Orchestration [Complexity: 12, Budget: 0 subtasks]

**Applied**: Sequential execution pattern for GPU memory management

### Configuration (Hardcoded Dict)

```python
# config.py - Experiment Configuration
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "checkpoint_dir": "./checkpoints",
    "log_level": "INFO",

    # Sequential model processing
    "process_models_sequentially": True,
    "unload_model_after_use": True,

    # Results storage
    "save_signatures": True,
    "save_metrics": True,
    "save_raw_samples": False,  # Disk space optimization

    # Reproducibility
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42,
        "torch": 42
    }
}
```

---

## Complete Configuration Module

**File:** `code/config.py`

```python
"""
Configuration for H-E1 Alignment Method Clustering Analysis
LIGHT tier: Hardcoded constants for standalone execution
"""

# Environment Configuration
ENV_CONFIG = {
    "python_version": "3.9+",
    "cuda_version": "11.8+",
    "packages": [
        "evalplus",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "radon",
        "lizard",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "pandas",
        "numpy"
    ],
    "min_gpu_vram_gb": 14
}

# Data Configuration
DATA_CONFIG = {
    "dataset_name": "evalplus/humanevalplus",
    "num_problems": 164,
    "dataset_split": "test",
    "cache_dir": "./cache/datasets"
}

# Model Configuration
MODEL_CONFIG = {
    "models": [
        ("bigcode/selfcodealign-7b", "execution"),
        ("codellama/CodeLlama-7b-Python-hf", "execution"),
        ("codellama/CodeLlama-7b-Instruct-hf", "preference"),
        ("codellama/CodeLlama-7b-hf", "baseline"),
        ("bigcode/starcoder", "baseline"),
    ],
    "device_map": "auto",
    "torch_dtype": "float16",
    "trust_remote_code": True,
    "cache_dir": "./cache/models"
}

GENERATION_CONFIG = {
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "do_sample": True,
    "num_return_sequences": 1,
    "pad_token_id": 0
}

# Profiling Configuration
PROFILING_CONFIG = {
    "num_samples_per_task": 64,
    "execution_timeout_sec": 3.0,
    "num_workers": 4,
    "random_seed": 42,
    "pass_k_values": [1, 10, 100],
    "complexity_metrics": ["cyclomatic", "ast_depth"],
    "efficiency_metrics": ["runtime", "memory"],
    "profile_only_correct": True
}

# Clustering Configuration
CLUSTERING_CONFIG = {
    "standardize": True,
    "pca_components": 3,
    "k_clusters": 3,
    "kmeans_init": "k-means++",
    "kmeans_n_init": 10,
    "random_state": 42,
    "cohens_d_threshold": 1.5,
    "bootstrap_iterations": 1000
}

# Visualization Configuration
VIZ_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 8),
    "colors": {
        "execution": "#0173B2",
        "preference": "#DE8F05",
        "baseline": "#029E73"
    },
    "figures": [
        "3d_scatter",
        "heatmap",
        "boxplots",
        "dendrogram",
        "effect_size",
        "gate_metrics"
    ]
}

# Experiment Configuration
EXPERIMENT_CONFIG = {
    "output_dir": "./results",
    "checkpoint_dir": "./checkpoints",
    "log_level": "INFO",
    "process_models_sequentially": True,
    "unload_model_after_use": True,
    "save_signatures": True,
    "save_metrics": True,
    "save_raw_samples": False,
    "set_all_seeds": True,
    "seeds": {
        "random": 42,
        "numpy": 42,
        "torch": 42
    }
}

# Gate Evaluation
GATE_CONFIG = {
    "type": "MUST_WORK",
    "metric": "cohens_d",
    "threshold": 1.5,
    "comparison": "greater_than",
    "halt_on_failure": True
}
```

---

## Usage Pattern

Phase 4 Coder will import these configs directly:

```python
from config import (
    MODEL_CONFIG,
    GENERATION_CONFIG,
    PROFILING_CONFIG,
    CLUSTERING_CONFIG,
    VIZ_CONFIG,
    EXPERIMENT_CONFIG,
    GATE_CONFIG
)

# Example usage in modules
def load_models():
    for model_name, alignment_type in MODEL_CONFIG["models"]:
        # Use GENERATION_CONFIG for sampling
        pass

def run_clustering(signatures):
    # Use CLUSTERING_CONFIG parameters
    pass
```

---

## Non-Standard Value Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `temperature` | 0.8 | Higher than greedy (0.0) to generate diverse samples for statistical analysis |
| `num_samples_per_task` | 64 | Required for pass@k estimation (from PRD requirement) |
| `cohens_d_threshold` | 1.5 | MUST_WORK gate requirement from hypothesis specification |
| `execution_timeout_sec` | 3.0 | Function-level code should execute quickly; prevents infinite loops |

All other parameters use standard library defaults or research-backed values.

---

## Reproducibility Settings

All stochastic components use fixed seed=42:
- Random sampling (Python `random`)
- NumPy operations
- PyTorch tensor operations
- K-means clustering (`random_state=42`)

---

## GPU Configuration

User must set before execution:

```bash
# Check available GPUs
nvidia-smi

# Set single GPU (REQUIRED)
export CUDA_VISIBLE_DEVICES=0  # Use empty GPU
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] KB search logged (1 line)
- [x] Codebase Analysis section included
- [x] Rationale only for non-standard values
- [x] No subtask decomposition (0 budget)
- [x] Total length < 400 lines
- [x] Complete config module provided
- [x] Copy-paste ready Python code

---

**End of Configuration Document**

*Ready for Phase 4 Implementation (code/config.py)*
