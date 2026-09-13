# Configuration: h-m-pareto

**Date:** 2026-08-20  
**Author:** yoon303b@gmail.com  
**Hypothesis:** Pareto frontier analysis for UQ methods  
**Phase:** 3 - Configuration Design

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Config patterns discovered from h-m1 and h-m3  
**Config Files Found:** experiments/h-m1/config.py, experiments/h-m3/config.py  
**Pattern Used:** Hardcoded dict (h-m1), Capitalized dict sections (h-m3)

**Applied:** Hardcoded dict pattern (minimal PoC for EXISTENCE hypothesis)

---

## Configuration

```python
# config.py - h-m-pareto Configuration

CONFIG = {
    "dataset": {
        "truthfulqa": {
            "source": "truthfulqa/truthful_qa",
            "config": "generation",
            "split": "validation",
            "total_samples": 817,
            "cache_dir": "~/.cache/huggingface/datasets/truthful_qa"
        },
        "halueval": {
            "source": "pminervini/HaluEval",
            "config": "qa_samples",
            "split": "train",
            "calibration_samples": 10000,
            "cache_dir": "~/.cache/huggingface/datasets/halueval"
        }
    },
    
    "model": {
        "name": "meta-llama/Llama-3.1-8B-Instruct",
        "precision": "bfloat16",
        "device_map": "auto",
        "token_env": "HF_TOKEN",
        "enable_dropout": True,
        "use_cache": False
    },
    
    "uq_methods": {
        "temperature_scaling": {
            "grid_range": [0.5, 5.0],
            "grid_step": 0.1,
            "cost_multiplier": 1.0
        },
        "conformal_prediction": {
            "alpha": 0.1,
            "coverage_target": 0.9,
            "cost_multiplier": 1.0
        },
        "mc_dropout": {
            "k_values": [1, 3, 5, 10],
            "dropout_rate": 0.1
        }
    },
    
    "experiment": {
        "seeds": [42, 123, 456],
        "batch_size": 8,
        "statistical_test_alpha": 0.05,
        "auroc_threshold": 0.55,
        "spearman_threshold": 0.2
    },
    
    "output": {
        "results_dir": "results/",
        "figures_dir": "figures/",
        "calibration_file": "results/calibration.json",
        "auroc_scores_file": "results/auroc_scores.json",
        "pareto_frontier_file": "results/pareto_frontier.json"
    }
}
```

---

## Configuration Rationale

### Dataset Configuration
- **TruthfulQA:** Standard validation split (817 samples), generation task for full text predictions
- **HaluEval:** 10k calibration samples for temperature/conformal hyperparameter tuning

### Model Configuration
- **Llama-3.1-8B-Instruct:** Instruction-tuned LLM for truthfulness task
- **bfloat16:** Default precision for Llama 3.1 (memory efficient)
- **enable_dropout=True, use_cache=False:** Required for MC dropout inference

### UQ Method Hyperparameters
- **Temperature grid [0.5, 5.0]:** Standard range from TS4CP paper (ICML)
- **Conformal α=0.1:** 90% coverage target (standard conformal prediction)
- **MC dropout k=[1,3,5,10]:** k=5 expected highest AUROC (H1), k=10 tests diminishing returns

### Experiment Configuration
- **Seeds [42, 123, 456]:** 3 seeds for AUROC variance estimation (conservative statistical power)
- **Batch size 8:** Memory constraint for 8B model inference
- **Statistical test α=0.05:** Standard significance level for paired t-test

---

## Inherited Configuration

**No base hypothesis** - This is a new analysis on h-m-integrated validation results.

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (temperature grid range, MC k values)
- [x] Codebase Analysis section included
- [x] Existing codebase patterns verified (h-m1/h-m3 use dict pattern)
- [x] Total length < 400 lines
