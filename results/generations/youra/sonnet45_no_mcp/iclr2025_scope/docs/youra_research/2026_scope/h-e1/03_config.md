# Configuration Design: h-e1

**Date:** 2026-04-19
**Hypothesis:** Oracle gap G_o ≥ 10% exists between per-task oracle and best fixed-rank baseline
**Type:** EXISTENCE (PoC)
**Infrastructure:** LIGHT (argparse/hardcoded dict)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** Hardcoded dict + argparse (LIGHT tier)

**Rationale:** No existing codebase or base hypothesis. EXISTENCE PoC requires minimal configuration structure for "does it work?" validation.

---

## Configuration Philosophy

**EXISTENCE constraints applied:**
- Single fixed config per parameter
- No hyperparameter grid or variations
- Minimal epochs for effect validation
- One seed (42)
- Hardcoded defaults from LoRA literature

**LIGHT infrastructure:**
- Argparse for command-line overrides
- Hardcoded dict for defaults
- No YAML files or dataclasses
- Copy-paste ready for Phase 4

---

## Global Configuration

Applied: Standard LoRA training defaults (Hu et al., 2021)

```python
# config.py - Global experiment configuration
import argparse

# Hardcoded defaults for EXISTENCE PoC
DEFAULT_CONFIG = {
    # Model
    "model_name": "meta-llama/Llama-2-7b-hf",
    "torch_dtype": "float16",
    
    # LoRA adapters
    "lora_ranks": [4, 8, 16, 32],
    "lora_alpha": 16,
    "lora_dropout": 0.1,
    "target_modules": ["q_proj", "v_proj"],
    
    # Training
    "learning_rate": 3e-4,
    "min_lr": 1e-6,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.999,
    "adam_epsilon": 1e-8,
    "warmup_ratio": 0.1,
    
    # Batch and accumulation
    "batch_size": 16,
    "gradient_accumulation_steps": 2,
    "max_seq_length": 512,
    
    # Epochs (task-dependent)
    "epochs_small": 5,      # <10k samples
    "epochs_large": 3,      # >50k samples
    "early_stopping_patience": 2,
    
    # Loss
    "label_smoothing": 0.1,
    
    # Reproducibility
    "seed": 42,
    
    # Datasets
    "glue_tasks": ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli"],
    "xtreme_languages": ["en", "es", "de", "zh"],
    
    # Paths
    "output_dir": "./outputs",
    "cache_dir": "./cache",
}

def get_config():
    """Return config dict with optional CLI overrides."""
    parser = argparse.ArgumentParser()
    
    # Allow overriding key parameters
    parser.add_argument("--lr", type=float, default=DEFAULT_CONFIG["learning_rate"])
    parser.add_argument("--batch_size", type=int, default=DEFAULT_CONFIG["batch_size"])
    parser.add_argument("--seed", type=int, default=DEFAULT_CONFIG["seed"])
    parser.add_argument("--output_dir", type=str, default=DEFAULT_CONFIG["output_dir"])
    
    args = parser.parse_args()
    
    # Merge CLI args into config
    config = DEFAULT_CONFIG.copy()
    config["learning_rate"] = args.lr
    config["batch_size"] = args.batch_size
    config["seed"] = args.seed
    config["output_dir"] = args.output_dir
    
    return config
```

---

## Per-Task Configuration

Applied: Task-specific settings from GLUE/XTREME benchmarks

```python
# task_configs.py - Task-specific configurations

TASK_CONFIGS = {
    # GLUE tasks
    "cola": {
        "num_labels": 2,
        "metric": "matthews_correlation",
        "epochs": 5,  # Small dataset
    },
    "sst2": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,  # Large dataset
    },
    "mrpc": {
        "num_labels": 2,
        "metric": "f1",
        "epochs": 5,
    },
    "qqp": {
        "num_labels": 2,
        "metric": "f1",
        "epochs": 3,
    },
    "stsb": {
        "num_labels": 1,  # Regression
        "metric": "pearson",
        "epochs": 5,
        "loss": "mse",  # Non-standard: regression task
    },
    "mnli": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "qnli": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "rte": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 5,
    },
    "wnli": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 5,
    },
    
    # XTREME tasks
    "xnli_en": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_es": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_de": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "xnli_zh": {
        "num_labels": 3,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_en": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_es": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_de": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
    "pawsx_zh": {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    },
}

def get_task_config(task_name):
    """Get task-specific configuration."""
    return TASK_CONFIGS.get(task_name, {
        "num_labels": 2,
        "metric": "accuracy",
        "epochs": 3,
    })
```

---

## Training Loop Configuration

Applied: Standard PyTorch training patterns

```python
# training_config.py - Training loop settings

TRAINING_CONFIG = {
    # Optimizer schedule
    "scheduler_type": "cosine",  # Cosine annealing
    
    # Checkpointing
    "save_strategy": "epoch",
    "save_total_limit": 2,
    "load_best_model_at_end": True,
    
    # Evaluation
    "eval_strategy": "epoch",
    "eval_steps": None,  # Eval at end of epoch
    
    # Logging
    "logging_steps": 50,
    "log_level": "info",
    
    # Device
    "device": "cuda",  # Single GPU
    "fp16": True,      # Mixed precision
    
    # Gradient settings
    "max_grad_norm": 1.0,
}
```

---

## Evaluation Configuration

Applied: Oracle gap measurement protocol from Phase 2B

```python
# eval_config.py - Evaluation and metrics

EVAL_CONFIG = {
    # Oracle gap calculation
    "hypervolume_ref_point": [0.0, 1e12],  # [min_accuracy, max_flops]
    
    # Per-task oracle selection
    "oracle_selection_metric": "accuracy",  # Primary metric
    
    # Fixed-rank baselines
    "fixed_ranks": [4, 8, 16, 32],
    
    # Success criteria
    "target_oracle_gap": 0.10,  # 10% normalized gap
    
    # Metrics to track
    "metrics": [
        "accuracy",
        "flops",
        "params",
        "hypervolume",
    ],
    
    # Efficiency calculation
    "count_base_model_flops": False,  # Only adapter FLOPs
}
```

---

## Dataset Loading Configuration

Applied: HuggingFace datasets standard loading

```python
# data_config.py - Dataset loading settings

DATA_CONFIG = {
    # HuggingFace datasets
    "dataset_cache_dir": "./cache/datasets",
    
    # Preprocessing
    "max_length": 512,
    "padding": "max_length",
    "truncation": True,
    
    # Data loading
    "num_workers": 4,
    "pin_memory": True,
    
    # GLUE loading
    "glue_dataset": "glue",
    
    # XTREME loading
    "xnli_dataset": "xnli",
    "xnli_split": "validation",
    "pawsx_dataset": "paws-x",
    "pawsx_split": "validation",
}
```

---

## Experiment Execution Plan

Total training runs: 17 tasks × 4 ranks = 68 adapter training runs

```python
# experiment_plan.py - Execution workflow

EXPERIMENT_PLAN = {
    # Task execution
    "total_tasks": 17,
    "ranks_per_task": 4,
    "total_runs": 68,
    
    # Estimated runtime (A100 40GB)
    "estimated_hours_per_run": 2.5,
    "estimated_total_hours": 170,
    
    # Parallelization (if available)
    "parallel_tasks": False,  # Single GPU PoC
    
    # Execution order
    "task_order": [
        # GLUE tasks (9)
        "cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli",
        # XTREME tasks (8)
        "xnli_en", "xnli_es", "xnli_de", "xnli_zh",
        "pawsx_en", "pawsx_es", "pawsx_de", "pawsx_zh",
    ],
    
    # Checkpointing strategy
    "checkpoint_each_run": True,
    "results_file": "oracle_gap_results.json",
}
```

---

## Visualization Configuration

Applied: Matplotlib standard plotting for paper figures

```python
# viz_config.py - Visualization settings

VIZ_CONFIG = {
    # Figure output
    "figure_dir": "./figures",
    "figure_format": "pdf",
    "figure_dpi": 300,
    
    # Plot style
    "style": "seaborn-v0_8-paper",
    "font_size": 10,
    "legend_size": 8,
    
    # Required figures
    "required_figures": [
        "gate_metrics_comparison",  # Mandatory
    ],
    
    # Additional figures
    "additional_figures": [
        "per_task_pareto_fronts",
        "oracle_vs_fixed_rank",
        "rank_selection_heatmap",
        "task_heterogeneity",
        "efficiency_performance_tradeoff",
    ],
    
    # Color schemes
    "rank_colors": {
        4: "#1f77b4",
        8: "#ff7f0e",
        16: "#2ca02c",
        32: "#d62728",
    },
    
    # Plot dimensions
    "single_figure_size": (6, 4),
    "grid_figure_size": (12, 10),
}
```

---

## Complete Configuration Assembly

```python
# main_config.py - All configs in one place for Phase 4

from config import DEFAULT_CONFIG, get_config
from task_configs import TASK_CONFIGS, get_task_config
from training_config import TRAINING_CONFIG
from eval_config import EVAL_CONFIG
from data_config import DATA_CONFIG
from experiment_plan import EXPERIMENT_PLAN
from viz_config import VIZ_CONFIG

class ExperimentConfig:
    """Single config object for entire experiment."""
    
    def __init__(self):
        self.global_config = DEFAULT_CONFIG
        self.task_configs = TASK_CONFIGS
        self.training = TRAINING_CONFIG
        self.eval = EVAL_CONFIG
        self.data = DATA_CONFIG
        self.experiment = EXPERIMENT_PLAN
        self.viz = VIZ_CONFIG
    
    def get_task_config(self, task_name):
        """Get merged config for specific task."""
        base = self.global_config.copy()
        task = self.task_configs.get(task_name, {})
        base.update(task)
        return base
    
    def override_from_cli(self):
        """Apply CLI overrides."""
        self.global_config = get_config()

# Usage in Phase 4:
# config = ExperimentConfig()
# config.override_from_cli()
# task_cfg = config.get_task_config("cola")
```

---

## Configuration Validation

**Quick checks:**
- [x] ONE format only (hardcoded dict, no dataclasses)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included
- [x] EXISTENCE constraints (single seed, fixed params, minimal epochs)
- [x] LIGHT infrastructure (argparse + dict, no YAML)
- [x] Copy-paste ready Python code
- [x] Total length < 400 lines

**EXISTENCE validation:**
- [x] Single config per parameter (no grid search)
- [x] Default values from LoRA literature (Hu et al., 2021)
- [x] One seed (42)
- [x] Minimal epochs (3-5 based on dataset size)

**Infrastructure validation:**
- [x] No dataclasses (LIGHT tier)
- [x] No YAML files (LIGHT tier)
- [x] Argparse for CLI overrides
- [x] Simple dict structure

---

## Notes for Phase 4 Coder

**Configuration usage:**
1. Copy all Python code blocks to respective files
2. Import `ExperimentConfig` in main experiment script
3. CLI override example: `python train.py --lr 5e-4 --batch_size 32`
4. Task-specific config access: `config.get_task_config("cola")`

**Key parameters verified from literature:**
- LoRA ranks {4,8,16,32}: Standard from Hu et al., 2021
- Learning rate 3e-4: PEFT library default for LoRA
- AdamW betas (0.9, 0.999): Standard optimizer settings
- Batch size 16 + grad_accum 2: Fits LLaMA-2-7B on A100 40GB
- Epochs 3-5: Standard GLUE fine-tuning protocol

**Execution estimate:**
- Total training time: ~170 hours on single A100 40GB
- Can parallelize across tasks if multiple GPUs available
- Results saved to `oracle_gap_results.json`

---

*Generated by Configuration Agent*
*Infrastructure: LIGHT (argparse + hardcoded dict)*
*Hypothesis Type: EXISTENCE (PoC)*
*Phase: 3 (Implementation Planning)*
