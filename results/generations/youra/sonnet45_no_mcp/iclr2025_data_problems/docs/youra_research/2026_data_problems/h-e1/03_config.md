# Configuration Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-04-15  
**Version:** 1.0  

Applied: **Minimal Config Pattern** - Hardcoded settings for PoC validation (LIGHT tier)

---

## Configuration Overview

For EXISTENCE hypothesis (LIGHT tier), we use **minimal infrastructure**:
- Configuration: Hardcoded defaults + argparse for key parameters
- No complex YAML/dataclass management
- Focus: Quick iteration for "does it work?" validation

---

## Experiment Configuration

### Domain Diversity Scores (Hardcoded)
```python
DIVERSITY_SCORES = {
    "Pile-CC": 0.92,           # High: web text, broad vocabulary
    "StackExchange": 0.88,     # High: technical Q&A
    "Wikipedia": 0.75,         # Medium-high: encyclopedic
    "ArXiv": 0.58,             # Medium: scientific papers
    "Github": 0.42,            # Medium-low: code
    "PubMed": 0.35             # Low: biomedical papers
}
```

### Experimental Conditions
```python
CONDITIONS = {
    "static": "Uniform 16.67% per domain throughout training",
    "diversity_ranked": "High→Low diversity Gaussian scheduling",
    "reversed": "Low→High diversity Gaussian scheduling",
    "shuffled": "Random domain order with Gaussian scheduling"
}
```

### Model Scales
```python
MODEL_CONFIGS = {
    "1B": {
        "n_layer": 24,
        "n_head": 16,
        "n_embd": 1536,
        "n_positions": 2048,
        "dropout": 0.1
    },
    "7B": {
        "n_layer": 32,
        "n_head": 32,
        "n_embd": 4096,
        "n_positions": 2048,
        "dropout": 0.1
    }
}
```

---

## Training Configuration

### Optimizer Settings
```python
OPTIMIZER_CONFIG = {
    "1B": {
        "optimizer": "AdamW",
        "lr": 3e-4,
        "betas": (0.9, 0.95),
        "weight_decay": 0.1,
        "warmup_steps": 2000,
        "total_steps": 100000,
        "lr_schedule": "cosine",
        "min_lr_ratio": 0.1  # Decay to 10% of peak
    },
    "7B": {
        "optimizer": "AdamW",
        "lr": 1.5e-4,
        "betas": (0.9, 0.95),
        "weight_decay": 0.1,
        "warmup_steps": 2000,
        "total_steps": 150000,
        "lr_schedule": "cosine",
        "min_lr_ratio": 0.1
    }
}
```

### Batch Configuration
```python
BATCH_CONFIG = {
    "1B": {
        "batch_size": 512,  # Sequences per batch
        "sequence_length": 2048,
        "gradient_accumulation_steps": 4,
        "num_gpus": 8  # A100
    },
    "7B": {
        "batch_size": 1024,
        "sequence_length": 2048,
        "gradient_accumulation_steps": 2,
        "num_gpus": 16  # A100
    }
}
```

### Curriculum Scheduling Parameters
```python
CURRICULUM_CONFIG = {
    "gaussian_width": 0.3,      # Transition smoothness
    "min_domain_weight": 0.05,  # Minimum 5% per domain
    "normalize_weights": True   # Sum to 1.0
}
```

---

## Data Configuration

### Dataset Settings
```python
DATA_CONFIG = {
    "dataset_name": "EleutherAI/pile-uncopyrighted",
    "target_domains": [
        "Pile-CC",
        "StackExchange", 
        "Wikipedia (en)",
        "ArXiv",
        "Github",
        "PubMed Central"
    ],
    "tokens_per_domain": 16.7e9,  # 16.7B tokens each
    "total_tokens": {
        "1B": 105e9,   # ~105B tokens
        "7B": 315e9    # ~315B tokens
    },
    "train_split": 0.95,
    "val_split": 0.05,
    "tokenizer": "gpt2",
    "vocab_size": 50257
}
```

### Checkpoint Settings
```python
CHECKPOINT_CONFIG = {
    "save_at_progress": [0.10, 0.25, 0.50, 0.75, 1.00],
    "save_optimizer_state": True,
    "checkpoint_dir": "checkpoints/{condition}_{scale}_seed{seed}",
    "max_checkpoints_keep": 5
}
```

---

## Evaluation Configuration

### Benchmark Settings
```python
EVAL_CONFIG = {
    "benchmarks": [
        "mmlu",           # 57 tasks
        "bigbench_hard",  # 23 tasks
        "hellaswag",
        "winogrande",
        "humaneval",      # Code
        "mbpp",           # Code
        "scienceqa"       # Scientific
    ],
    "num_fewshot": 5,
    "eval_at_checkpoints": [0.10, 0.25, 0.50, 0.75, 1.00],
    "eval_batch_size": 16
}
```

### Gradient Geometry Settings
```python
GEOMETRY_CONFIG = {
    "probe_dataset_size": 10000,  # Tokens per domain
    "compute_at_checkpoints": [0.10, 0.25, 0.50, 0.75, 1.00],
    "metrics": ["participation_ratio", "cka_similarity"],
    "cka_reference_checkpoint": 0.25  # Compare 25% vs 100%
}
```

### Statistical Validation
```python
STATS_CONFIG = {
    "seeds": [42, 43, 44, 45, 46],  # 5 independent runs
    "alpha": 0.05,
    "bonferroni_correction": True,
    "num_comparisons": 4,  # 4 conditions
    "gate_thresholds": {
        "1B": 2.0,  # ≥2.0% absolute improvement
        "7B": 0.5   # ≥0.5% absolute improvement
    }
}
```

---

## System Configuration

### Hardware
```python
HARDWARE_CONFIG = {
    "1B": {
        "gpu_type": "A100",
        "num_gpus": 8,
        "memory_per_gpu": "40GB",
        "precision": "bfloat16"
    },
    "7B": {
        "gpu_type": "A100",
        "num_gpus": 16,
        "memory_per_gpu": "80GB",
        "precision": "bfloat16",
        "use_gradient_checkpointing": True
    }
}
```

### Logging (Minimal - LIGHT tier)
```python
LOGGING_CONFIG = {
    "log_every_n_steps": 100,
    "validation_every_n_steps": 1000,
    "metrics_to_log": ["loss", "ppl", "lr", "tokens_per_sec"],
    "save_format": "csv",  # Simple CSV logging
    "wandb": False  # Not used for LIGHT tier
}
```

---

## Experiment Orchestration

### Total Runs
```python
ORCHESTRATION = {
    "total_runs": 40,  # 4 conditions × 2 scales × 5 seeds
    "conditions": 4,
    "scales": 2,
    "seeds_per_condition": 5,
    "estimated_duration": {
        "1B_per_run": "3 days",
        "7B_per_run": "10 days"
    }
}
```

### Execution Order
```python
# Sequential execution (no parallel optimization for PoC)
EXECUTION_ORDER = [
    # 1B scale first (faster validation)
    ("static", "1B", [42, 43, 44, 45, 46]),
    ("diversity_ranked", "1B", [42, 43, 44, 45, 46]),
    ("reversed", "1B", [42, 43, 44, 45, 46]),
    ("shuffled", "1B", [42, 43, 44, 45, 46]),
    
    # 7B scale second
    ("static", "7B", [42, 43, 44, 45, 46]),
    ("diversity_ranked", "7B", [42, 43, 44, 45, 46]),
    ("reversed", "7B", [42, 43, 44, 45, 46]),
    ("shuffled", "7B", [42, 43, 44, 45, 46])
]
```

---

## Visualization Configuration

### Figure Generation
```python
VISUALIZATION_CONFIG = {
    "output_dir": "figures/",
    "formats": ["png", "pdf"],
    "dpi": 300,
    "figures": {
        "fig1_gate_metrics": {
            "type": "bar_chart",
            "data": "composite_performance × 4 conditions × 2 scales",
            "error_bars": "±1 SEM (n=5)",
            "required": True  # MANDATORY
        },
        "fig2_domain_schedule": {
            "type": "line_plot",
            "data": "domain weights vs training progress",
            "conditions": ["diversity_ranked"]
        },
        "fig3_val_curves": {
            "type": "line_plot",
            "data": "validation perplexity vs steps"
        },
        "fig4_pr_evolution": {
            "type": "line_plot",
            "data": "Participation Ratio at checkpoints"
        },
        "fig5_cka_heatmap": {
            "type": "heatmap",
            "data": "Layer-wise CKA (25% vs 100%)"
        },
        "fig6_task_breakdown": {
            "type": "heatmap",
            "data": "Per-task performance (MMLU/Big-Bench)"
        }
    }
}
```

---

## Subtask Breakdown

### E-2: Curriculum Loader (3 subtasks)
1. **Domain Diversity Computation** - Implement diversity score calculation from corpus statistics
2. **Gaussian Weight Scheduler** - Time-dependent domain weight computation
3. **Weighted Sampling** - Integrate with PyTorch DataLoader for dynamic batching

---

## Command-Line Interface (Argparse - Minimal)

```python
# Minimal CLI for experiment launch
python train.py \
    --condition diversity_ranked \
    --scale 1B \
    --seed 42 \
    --output_dir ./checkpoints/diversity_ranked_1B_seed42
```

**Key Arguments:**
- `--condition`: {static, diversity_ranked, reversed, shuffled}
- `--scale`: {1B, 7B}
- `--seed`: Random seed (42-46)
- `--output_dir`: Checkpoint save location

All other settings hardcoded in config constants above.

---

**Total Subtasks:** 3 (within budget of 3)

**Infrastructure Level:** LIGHT (minimal - hardcoded configs, CSV logging, argparse CLI)
