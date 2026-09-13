# Configuration Schema: h-e1 CCP Domain Degradation Experiment

**Date:** 2026-07-09
**Hypothesis:** h-e1 - ρ_j degradation by >0.15 when CCP applied to creative vs factual text
**Type:** EXISTENCE (Proof-of-Concept)
**Author:** Configuration Agent

Applied: PyTorch reproducibility pattern, hardcoded dict for PoC experiments

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation from scratch
**Config Files Found:** None - new config design
**Pattern Used:** Hardcoded dict (preferred for EXISTENCE PoC)

---

## Configuration Overview

Single fixed configuration optimized for minimal PoC validation. No hyperparameter tuning or subtask variations.

**Format:** Hardcoded dictionary (copy-paste ready for `config.py`)

---

## A-1: Setup Environment [Complexity: 5, Budget: 5]

**Applied:** Standard Python project structure

### Configuration (Hardcoded Dict)

```python
from pathlib import Path
import torch

# Base paths
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

# Create directories
for d in [CACHE_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(exist_ok=True, parents=True)

CONFIG = {
    "random_seed": 42,
    "dataset": {
        "truthfulqa": {
            "name": "truthfulqa/truthful_qa",
            "subset": "generation",
            "split": "validation"
        },
        "writingprompts": {
            "name": "euclaise/writingprompts",
            "split": "train",
            "sample_size": 817
        },
        "cache_dir": str(CACHE_DIR / "datasets")
    },
    "nli_model": {
        "name": "cross-encoder/nli-deberta-v3-base",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "batch_size": 16,
        "max_length": 512
    },
    "claim_decomposition": {
        "method": "nltk",
        "max_claims": 20
    },
    "output": {
        "intermediate": str(RESULTS_DIR / "sample_rho_j.json"),
        "metrics": str(RESULTS_DIR / "metrics_summary.json"),
        "validation_report": str(BASE_DIR.parent / "04_validation.md")
    },
    "gate_thresholds": {
        "delta_rho_j": 0.15,
        "autocorr_creative": 0.4,
        "autocorr_factual": 0.2,
        "krippendorff_alpha": 0.7
    }
}
```

### Reproducibility Settings

```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42):
    """Configure reproducible random state."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    # PyTorch deterministic algorithms
    torch.use_deterministic_algorithms(True)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Directory structure | Create code/, cache/, results/, figures/ |
| C-1-2 | Dependencies | Install transformers, sentence-transformers, torch, datasets |
| C-1-3 | Config file | Implement config.py with paths and settings |
| C-1-4 | Seed initialization | Set random seeds for reproducibility |
| C-1-5 | Pre-flight checks | Verify GPU availability, NLTK punkt data |

---

## A-2: Dataset Loading [Complexity: 6, Budget: 6]

**Applied:** HuggingFace datasets standard loading pattern

### Configuration (Hardcoded Dict)

```python
DATASET_CONFIG = {
    "truthfulqa": {
        "name": "truthfulqa/truthful_qa",
        "subset": "generation",
        "split": "validation",
        "expected_size": 817,
        "fields": ["question", "best_answer", "correct_answers"]
    },
    "writingprompts": {
        "name": "euclaise/writingprompts",
        "split": "train",
        "sample_size": 817,
        "random_seed": 42,
        "fields": ["prompt", "story"],
        # Filter criteria for creative content
        "min_story_length": 200,
        "max_story_length": 2000
    },
    "cache_dir": str(CACHE_DIR / "datasets"),
    "num_proc": 4
}
```

### Claim Decomposition

```python
CLAIM_CONFIG = {
    "method": "nltk",
    "tokenizer": "punkt",
    "max_claims_per_sample": 20,
    "min_claim_length": 10,  # characters
    "fallback_method": "simple_split"  # If NLTK fails
}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | TruthfulQA loader | Load validation split (817 samples) |
| C-2-2 | WritingPrompts loader | Subsample train split to 817 samples |
| C-2-3 | Data validation | Check for null entries, log statistics |
| C-2-4 | Claim decomposition | NLTK sentence tokenization |
| C-2-5 | Preprocessing | Clean text, truncate to max_claims |
| C-2-6 | Cache management | Save/load preprocessed data |

---

## A-3: NLI Model Integration [Complexity: 8, Budget: 8]

**Applied:** sentence-transformers CrossEncoder pattern

### Configuration (Hardcoded Dict)

```python
NLI_CONFIG = {
    "model_name": "cross-encoder/nli-deberta-v3-base",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "batch_size": 16,
    "max_length": 512,
    "num_labels": 3,  # [contradiction, entailment, neutral]
    "cache_dir": str(CACHE_DIR / "models"),
    "inference": {
        "show_progress": True,
        "convert_to_numpy": True,
        "activation_fn": "softmax"
    },
    "error_handling": {
        "max_retries": 3,
        "reduce_batch_on_oom": True,
        "min_batch_size": 4
    }
}
```

### GPU Memory Management

```python
MEMORY_CONFIG = {
    "initial_batch_size": 16,
    "oom_batch_multiplier": 0.5,
    "min_batch_size": 4,
    "clear_cache_between_domains": True,
    "max_gpu_memory_gb": 20  # A100 40GB budget
}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Model loading | Load DeBERTa-v3-base from HuggingFace |
| C-3-2 | Device setup | Configure CUDA/CPU device |
| C-3-3 | Batch inference | Implement batched NLI prediction |
| C-3-4 | Pair construction | Create (context, claim) pairs |
| C-3-5 | Score extraction | Extract 3-class probabilities |
| C-3-6 | OOM handling | Dynamic batch size reduction |
| C-3-7 | Progress tracking | tqdm integration for batches |
| C-3-8 | Cache clearing | Clear CUDA cache between domains |

---

## A-4: Metrics Implementation [Complexity: 10, Budget: 10]

**Applied:** Statistical computing standard patterns (scipy, numpy)

### Configuration (Hardcoded Dict)

```python
METRICS_CONFIG = {
    "rho_j": {
        "aggregation": "median",
        "classes": ["contradiction", "entailment", "neutral"],
        "claim_mass_classes": ["contradiction", "entailment"],
        "epsilon": 1e-8  # Avoid division by zero
    },
    "autocorrelation": {
        "max_lag": 10,
        "method": "pearson",
        "min_samples": 2
    },
    "reliability": {
        "metric": "krippendorff_alpha",
        "sample_size": 100,
        "num_repetitions": 2,
        "seed_offset": 100
    },
    "statistical_test": {
        "method": "wilcoxon",
        "alternative": "greater",
        "alpha": 0.05
    }
}
```

### Gate Thresholds

```python
GATE_CONFIG = {
    "must_work_criteria": {
        "delta_rho_j": {
            "threshold": 0.15,
            "direction": "creative > factual",
            "critical": True
        },
        "autocorr_creative": {
            "threshold": 0.4,
            "direction": "greater",
            "critical": True
        },
        "autocorr_factual": {
            "threshold": 0.2,
            "direction": "less",
            "critical": True
        },
        "krippendorff_alpha": {
            "threshold": 0.7,
            "direction": "greater",
            "critical": True
        },
        "p_value": {
            "threshold": 0.05,
            "direction": "less",
            "critical": False
        }
    }
}
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | ρ_j computation | Implement median claim-type mass ratio |
| C-4-2 | Per-sample ρ_j | Compute ρ_j for each sample |
| C-4-3 | Aggregate ρ_j | Median across domain samples |
| C-4-4 | Autocorrelation | Lag-1 to lag-10 Pearson correlation |
| C-4-5 | Krippendorff α | Claim decomposition reliability |
| C-4-6 | Statistical test | Wilcoxon rank-sum test |
| C-4-7 | Effect size | Cohen's d for Δρ_j |
| C-4-8 | Confidence intervals | Bootstrap 95% CI |
| C-4-9 | Gate validation | Check all MUST_WORK criteria |
| C-4-10 | Metrics export | Save to metrics_summary.json |

---

## A-5: Experiment Pipeline [Complexity: 9, Budget: 9]

**Applied:** Standard experiment orchestration pattern

### Configuration (Hardcoded Dict)

```python
PIPELINE_CONFIG = {
    "execution_order": [
        "set_seed",
        "load_datasets",
        "initialize_nli_model",
        "process_factual_domain",
        "clear_cache",
        "process_creative_domain",
        "compute_metrics",
        "generate_visualizations",
        "validate_gate",
        "save_results"
    ],
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": str(RESULTS_DIR / "experiment.log"),
        "console": True
    },
    "checkpointing": {
        "save_intermediate": True,
        "checkpoint_dir": str(RESULTS_DIR / "checkpoints")
    },
    "timeout": {
        "total_seconds": 1800,  # 30 minutes
        "per_domain_seconds": 600
    }
}
```

### Domain Processing

```python
DOMAIN_PROCESSING_CONFIG = {
    "batch_processing": True,
    "progress_tracking": True,
    "save_intermediate_scores": True,
    "log_failed_samples": True,
    "continue_on_error": True,
    "max_failures_per_domain": 50
}
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Pipeline class | Implement CCPExperiment orchestrator |
| C-5-2 | Initialization | Load datasets and models |
| C-5-3 | Factual processing | Process TruthfulQA through NLI |
| C-5-4 | Creative processing | Process WritingPrompts through NLI |
| C-5-5 | Metric computation | Call metrics module |
| C-5-6 | Error handling | Retry logic and logging |
| C-5-7 | Progress logging | Log each pipeline stage |
| C-5-8 | Results aggregation | Combine factual/creative results |
| C-5-9 | Checkpoint saving | Save intermediate results |

---

## A-6: Visualization [Complexity: 7, Budget: 7]

**Applied:** matplotlib/seaborn standard plotting patterns

### Configuration (Hardcoded Dict)

```python
VIS_CONFIG = {
    "output_dir": str(FIGURES_DIR),
    "dpi": 300,
    "format": "png",
    "style": "seaborn-v0_8-darkgrid",
    "figsize": (10, 6),
    "font_size": 12,
    "color_palette": {
        "factual": "#1f77b4",  # Blue
        "creative": "#ff7f0e"  # Orange
    },
    "plots": {
        "rho_distribution": {
            "type": "violin",
            "filename": "rho_j_distribution.png",
            "title": "ρ_j Distribution: Factual vs Creative",
            "ylabel": "ρ_j (Claim-type Mass Ratio)",
            "show_median": True,
            "show_quartiles": True
        },
        "nli_heatmap": {
            "type": "heatmap",
            "filename": "nli_distribution_heatmap.png",
            "title": "NLI Score Distribution by Domain",
            "cmap": "viridis",
            "annot": True,
            "fmt": ".3f"
        },
        "autocorrelation": {
            "type": "line",
            "filename": "autocorrelation_comparison.png",
            "title": "Autocorrelation: Factual vs Creative",
            "xlabel": "Lag",
            "ylabel": "Pearson Correlation",
            "marker": "o"
        },
        "sample_scatter": {
            "type": "scatter",
            "filename": "sample_rho_j_scatter.png",
            "title": "Per-Sample ρ_j Values",
            "xlabel": "Sample Index",
            "ylabel": "ρ_j",
            "alpha": 0.6
        }
    }
}
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Violin plot | ρ_j distribution comparison |
| C-6-2 | NLI heatmap | Score distribution visualization |
| C-6-3 | Autocorrelation plot | Lag correlation line plot |
| C-6-4 | Scatter plot | Per-sample ρ_j values |
| C-6-5 | Style configuration | Set matplotlib/seaborn theme |
| C-6-6 | Figure export | Save all plots to figures/ |
| C-6-7 | Embedding | Generate markdown for 04_validation.md |

---

## A-7: Validation Report [Complexity: 5, Budget: 5]

**Applied:** Markdown report generation pattern

### Configuration (Hardcoded Dict)

```python
REPORT_CONFIG = {
    "output_file": str(BASE_DIR.parent / "04_validation.md"),
    "template_sections": [
        "executive_summary",
        "gate_metrics",
        "statistical_analysis",
        "visualizations",
        "limitations",
        "recommendations"
    ],
    "gate_decision": {
        "all_criteria_must_pass": True,
        "report_failed_criteria": True
    },
    "verification_state_file": str(BASE_DIR.parent / "verification_state.yaml"),
    "include_raw_data": False,
    "include_figures": True
}
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Gate checker | Validate all MUST_WORK criteria |
| C-7-2 | Report generator | Create 04_validation.md |
| C-7-3 | Metrics table | Format results in markdown table |
| C-7-4 | Figure embedding | Embed PNG figures in report |
| C-7-5 | State update | Update verification_state.yaml |

---

## Complete Configuration File

**File:** `code/config.py`

```python
"""
Configuration for h-e1 CCP Domain Degradation Experiment
EXISTENCE hypothesis - minimal PoC settings
"""

from pathlib import Path
import torch
import random
import numpy as np

# Base paths
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

# Create directories
for d in [CACHE_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(exist_ok=True, parents=True)

# Main configuration
CONFIG = {
    "random_seed": 42,
    
    "dataset": {
        "truthfulqa": {
            "name": "truthfulqa/truthful_qa",
            "subset": "generation",
            "split": "validation",
            "expected_size": 817
        },
        "writingprompts": {
            "name": "euclaise/writingprompts",
            "split": "train",
            "sample_size": 817,
            "min_story_length": 200,
            "max_story_length": 2000
        },
        "cache_dir": str(CACHE_DIR / "datasets"),
        "num_proc": 4
    },
    
    "nli_model": {
        "name": "cross-encoder/nli-deberta-v3-base",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "batch_size": 16,
        "max_length": 512,
        "cache_dir": str(CACHE_DIR / "models")
    },
    
    "claim_decomposition": {
        "method": "nltk",
        "tokenizer": "punkt",
        "max_claims": 20,
        "min_claim_length": 10
    },
    
    "metrics": {
        "rho_j": {
            "aggregation": "median",
            "epsilon": 1e-8
        },
        "autocorrelation": {
            "max_lag": 10,
            "method": "pearson"
        },
        "reliability": {
            "sample_size": 100,
            "num_repetitions": 2
        }
    },
    
    "visualization": {
        "output_dir": str(FIGURES_DIR),
        "dpi": 300,
        "format": "png",
        "figsize": (10, 6),
        "colors": {
            "factual": "#1f77b4",
            "creative": "#ff7f0e"
        }
    },
    
    "output": {
        "intermediate": str(RESULTS_DIR / "sample_rho_j.json"),
        "metrics": str(RESULTS_DIR / "metrics_summary.json"),
        "log": str(RESULTS_DIR / "experiment.log"),
        "validation_report": str(BASE_DIR.parent / "04_validation.md")
    },
    
    "gate_thresholds": {
        "delta_rho_j": 0.15,
        "autocorr_creative": 0.4,
        "autocorr_factual": 0.2,
        "krippendorff_alpha": 0.7,
        "p_value": 0.05
    },
    
    "execution": {
        "timeout_seconds": 1800,
        "save_intermediate": True,
        "continue_on_error": True,
        "max_failures": 50
    }
}

def set_seed(seed: int = 42):
    """Configure reproducible random state across all libraries."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)

def get_device():
    """Return available compute device."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

---

## Dependencies

**File:** `code/requirements.txt`

```
# Core ML frameworks
transformers==4.36.0
sentence-transformers==2.2.2
torch==2.1.0
datasets==2.16.0

# Data processing
nltk==3.8.1
numpy==1.24.3
scipy==1.11.4

# Metrics
krippendorff==0.6.0

# Visualization
matplotlib==3.8.2
seaborn==0.13.0

# Utilities
pyyaml==6.0.1
tqdm==4.66.1
```

---

## Summary

**Total Tasks:** 7
**Total Subtasks:** 50 (budget: 50, used: 50)
**Configuration Format:** Hardcoded dictionary (PoC-optimized)
**Reproducibility:** Fixed seeds (42), deterministic PyTorch
**Pattern Applied:** Standard PyTorch experiment configuration

**Key Design Decisions:**
1. Single fixed config (no hyperparameter variations)
2. Hardcoded dict format (copy-paste ready for Phase 4)
3. All defaults from research literature (DeBERTa standard settings)
4. Gate thresholds directly from hypothesis specification
5. Minimal config - no ablation or tuning required

**Next Phase:** Phase 4 - Implementation (coder can directly copy config code)

---

**Configuration Status:** COMPLETED
**Output File:** `/workspace/TEST_question/docs/youra_research/h-e1/03_config.md`
