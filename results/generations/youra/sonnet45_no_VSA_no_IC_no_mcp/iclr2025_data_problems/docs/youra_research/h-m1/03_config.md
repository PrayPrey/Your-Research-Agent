# Configuration Schema: h-m1

**Date:** 2026-08-24
**Hypothesis ID:** h-m1 (MECHANISM - PoC)
**Author:** Phase 3 Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-e1)
**Status:** Config verified from h-e1 actual code
**Config Files Found:** h-e1/code/run_experiment.py, h-e1/03_config.md
**Pattern Used:** Hardcoded dict (PoC simplicity)

---

## Configuration Overview

Fixed configuration for threshold transfer robustness testing. Reuses h-e1 training protocol (controlled experiment - only threshold sweep changes).

---

## Threshold Sweep Configuration

**Applied:** DataComp curation patterns (0.7-0.9 dedup, 500-1500 perplexity)

```python
THRESHOLD_CONFIG = {
    # Deduplication thresholds (exact-match hash for PoC)
    "dedup_thresholds": [0.7, 0.8, 0.9],
    
    # Perplexity cutoffs (KenLM scoring)
    "perplexity_thresholds": [500, 1000, 1500],
    
    # Total combinations: 3 × 3 = 9 threshold pairs
    # Pre-training optimal: determined by grid search on C4
    # Fine-tuning optimal: determined by grid search on Dolly-15k
}
```

---

## Training Configuration

**Applied:** h-e1 training protocol (reused for controlled comparison)

```python
TRAINING_CONFIG = {
    # Optimizer (from h-e1/code/run_experiment.py)
    "optimizer": "adamw",
    "learning_rate": 2e-5,
    "weight_decay": 0.01,
    "betas": (0.9, 0.999),
    
    # Batch settings (from h-e1)
    "batch_size": 16,
    "micro_batch_size": 4,
    "gradient_accumulation_steps": 4,
    
    # Duration (from h-e1)
    "epochs": 3,
    
    # Reproducibility
    "seed": 1,
    "deterministic": True,
}
```

---

## Dataset Configuration

**Applied:** C4 + Dolly-15k standard splits

```python
DATASET_CONFIG = {
    # Pre-training stage dataset
    "pretrain": {
        "name": "allenai/c4",
        "split": "train",
        "streaming": True,
        "num_samples": 52002,  # From h-e1
    },
    
    # Fine-tuning stage dataset
    "finetune": {
        "name": "databricks/databricks-dolly-15k",
        "split": "train",
        "num_samples": 15000,
    },
    
    # Preprocessing
    "max_length": 512,
    "min_words": 5,
    
    # Cache paths
    "cache_dir": "~/.cache/huggingface/",
    "curated_data_dir": "data/h-m1/curated",
}
```

---

## Model Configuration

**Applied:** Llama-2-7B (from h-e1)

```python
MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-2-7b-hf",
    "tokenizer_name": "meta-llama/Llama-2-7b-hf",
    
    # Fine-tuning strategy (from h-e1)
    "full_finetuning": True,
    
    # Memory optimization
    "gradient_checkpointing": False,
    "bf16": True,
    "fp16": False,
    
    # Checkpoint paths
    "checkpoint_dir": "data/h-m1/checkpoints",
}
```

---

## Evaluation Configuration

**Applied:** lm-evaluation-harness standard (from h-e1)

```python
EVALUATION_CONFIG = {
    # Tasks (from h-e1)
    "tasks": ["mmlu", "hellaswag"],
    "num_fewshot": 0,
    "eval_batch_size": 8,
    
    # Gate condition (h-m1 MUST_WORK)
    "gate_type": "MUST_WORK",
    "max_delta": 0.10,  # <10% performance degradation when thresholds mismatched
    
    # PoC mode
    "mock_evaluation": True,  # Skip actual lm-eval for PoC
}
```

---

## Visualization Configuration

**Applied:** Standard matplotlib settings

```python
VISUALIZATION_CONFIG = {
    # Output directory
    "figures_dir": "docs/youra_research/h-m1/figures",
    
    # Figure formats
    "format": "png",
    "dpi": 300,
    
    # Required figures (from PRD FR4)
    "required_figures": [
        "gate_metrics_comparison.png",
        "threshold_sensitivity_heatmap.png",
        "transfer_delta_barchart.png",
        "curation_impact_chart.png",
    ],
}
```

---

## Perplexity Computation Configuration

**Applied:** KenLM reference model (from h-e1 patterns)

```python
PERPLEXITY_CONFIG = {
    # Reference language model
    "model_type": "kenlm",
    "model_path": "data/h-m1/en.arpa.bin",  # Download from KenLM
    
    # Scoring settings
    "batch_size": 1000,
    "cache_scores": True,
    "score_cache_path": "data/h-m1/perplexity_cache.json",
}
```

---

## Deduplication Configuration

**Applied:** Exact-match hash (PoC simplicity over LSH)

```python
DEDUPLICATION_CONFIG = {
    # Method: exact-match for PoC (LSH in production)
    "method": "exact_hash",
    
    # Hash function (deterministic)
    "hash_function": "sha256",
    
    # Output
    "log_duplicates": True,
    "duplicate_log_path": "data/h-m1/duplicates.json",
}
```

---

## Resource Configuration

**Applied:** Single GPU setup (from h-e1)

```python
RESOURCE_CONFIG = {
    "device": "cuda",
    "gpu_device": 0,
    "num_workers": 4,
    "pin_memory": True,
}
```

---

## Path Configuration

**Applied:** h-m1 hypothesis folder structure

```python
from pathlib import Path

PATH_CONFIG = {
    # Base directories
    "hypothesis_dir": Path("docs/youra_research/h-m1"),
    "data_dir": Path("data/h-m1"),
    
    # Data paths
    "cache_dir": Path("~/.cache/huggingface/"),
    "curated_data_dir": Path("data/h-m1/curated"),
    
    # Output paths
    "output_dir": Path("docs/youra_research/h-m1/results"),
    "checkpoint_dir": Path("data/h-m1/checkpoints"),
    "figures_dir": Path("docs/youra_research/h-m1/figures"),
    
    # Logs
    "log_file": Path("docs/youra_research/h-m1/experiment.log"),
}
```

---

## Master Configuration

```python
CONFIG = {
    "hypothesis_id": "h-m1",
    "experiment_name": "threshold_transfer_robustness",
    "tier": "PoC",
    
    "thresholds": THRESHOLD_CONFIG,
    "training": TRAINING_CONFIG,
    "dataset": DATASET_CONFIG,
    "model": MODEL_CONFIG,
    "evaluation": EVALUATION_CONFIG,
    "visualization": VISUALIZATION_CONFIG,
    "perplexity": PERPLEXITY_CONFIG,
    "deduplication": DEDUPLICATION_CONFIG,
    "resources": RESOURCE_CONFIG,
    "paths": PATH_CONFIG,
}
```

---

## Usage

```python
# Load config
from config import CONFIG

# Run threshold sweep on pre-training data
pretrain_optimal = tune_thresholds(
    data=load_dataset(**CONFIG["dataset"]["pretrain"]),
    dedup_grid=CONFIG["thresholds"]["dedup_thresholds"],
    ppl_grid=CONFIG["thresholds"]["perplexity_thresholds"],
)

# Run threshold sweep on fine-tuning data
finetune_optimal = tune_thresholds(
    data=load_dataset(**CONFIG["dataset"]["finetune"]),
    dedup_grid=CONFIG["thresholds"]["dedup_thresholds"],
    ppl_grid=CONFIG["thresholds"]["perplexity_thresholds"],
)

# Cross-apply thresholds
pretrain_data_with_finetune_thresholds = curate(
    data=load_dataset(**CONFIG["dataset"]["pretrain"]),
    dedup_threshold=finetune_optimal["dedup"],
    ppl_threshold=finetune_optimal["perplexity"],
)

# Measure transfer delta
delta = measure_performance_delta(
    optimal_data=pretrain_data_with_pretrain_thresholds,
    transferred_data=pretrain_data_with_finetune_thresholds,
)
```

---

## Experiment Variants

### Pre-training Stage Tuning

```python
pretrain_config = CONFIG.copy()
pretrain_config["stage"] = "pretrain"
pretrain_config["dataset"]["active"] = CONFIG["dataset"]["pretrain"]
```

### Fine-tuning Stage Tuning

```python
finetune_config = CONFIG.copy()
finetune_config["stage"] = "finetune"
finetune_config["dataset"]["active"] = CONFIG["dataset"]["finetune"]
```

### Cross-Stage Transfer (Mismatch)

```python
transfer_config = CONFIG.copy()
transfer_config["stage"] = "transfer"
transfer_config["pretrain_thresholds_on_finetune"] = True
transfer_config["finetune_thresholds_on_pretrain"] = True
```

---

## PRD Traceability

| Requirement | Config Section |
|-------------|----------------|
| FR1 (Threshold sweep) | THRESHOLD_CONFIG |
| FR2 (Cross-stage transfer) | Experiment variants |
| FR3 (Performance measurement) | EVALUATION_CONFIG |
| FR4 (Visualization) | VISUALIZATION_CONFIG |
| NFR1 (Reproducibility) | TRAINING_CONFIG.seed, DEDUPLICATION_CONFIG.hash_function |
| NFR2 (Efficiency) | PERPLEXITY_CONFIG.cache_scores, DEDUPLICATION_CONFIG.method |

---

## Inherited from h-e1

**Training hyperparameters verified from h-e1/code/run_experiment.py:**
- learning_rate=2e-5 (line 193)
- batch_size=4 (line 194, micro_batch_size)
- epochs=1 (PoC mode, line 54)
- seed=42 (h-e1 actual), changed to seed=1 (h-m1 spec)

**Dataset paths verified from h-e1:**
- cache_dir pattern (line 48-49)
- Alpaca loading pattern (lines 72-73)

**Evaluation setup verified from h-e1/code/evaluate.py:**
- tasks=["mmlu", "hellaswag"] (line 118)
- num_fewshot=0 (line 119)
- batch_size=8 (line 120)

---

## PoC Simplifications

**EXISTENCE tier constraints:**
- Single seed (seed=1, no multi-run)
- Fixed learning rate (no scheduling)
- Exact-match dedup (not LSH)
- Mock evaluation acceptable (lm-eval optional)
- Coarse threshold grid (9 combinations)

**Phase 4 Usage:**
Copy CONFIG dict to h-m1/code/config.py and import. Fixed values - no command-line overrides needed for PoC.
