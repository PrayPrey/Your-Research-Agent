# Configuration Schema: H-E1

**Hypothesis:** Mamba-130M checkpoint validation  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr

Applied: DL minimal inference pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing config to analyze  
**Config Files Found**: None - new config  
**Pattern Used**: hardcoded dict (EXISTENCE simplicity)

---

## Configuration Format

Single hardcoded dict in `code/config.py` - no dataclass needed for PoC with fixed values.

---

## E1-1: Setup Infrastructure [Complexity: 5, Budget: 2]

### Configuration (Python Dict)

```python
# code/config.py

# Model checkpoint
CHECKPOINT_NAME = "state-spaces/mamba-130m-hf"

# GLUE tasks for validation
GLUE_TASKS = ["mnli", "qqp", "sst2"]

# Inference settings
BATCH_SIZE = 16
MAX_LENGTH = 512
DEVICE = "cuda"
DTYPE = "float16"

# Memory and reproducibility
MEMORY_LIMIT_GB = 16.0
RANDOM_SEED = 42

# Output paths (set at runtime by train.py)
OUTPUT_DIR = None  # Set to hypothesis folder path
FIGURES_DIR = None  # Set to hypothesis_folder/figures/
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C1-1 | Install dependencies | Create requirements.txt with transformers, datasets, torch, numpy, matplotlib |
| C1-2 | Verify environment | Check CUDA availability, create output directories |

---

## E1-2: Implement Checkpoint Loading [Complexity: 8, Budget: 2]

Uses same config from E1-1. No additional parameters needed.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C2-1 | CheckpointLoader class | Implement model/tokenizer loading with device_map="auto" |
| C2-2 | Memory tracking | Add get_memory_stats() using torch.cuda.max_memory_allocated() |

---

## E1-3: Implement Data Loading [Complexity: 7, Budget: 2]

Uses GLUE_TASKS from config. No additional parameters.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C3-1 | GLUELoader class | Implement load_task() for datasets.load_dataset("glue", task) |
| C3-2 | Task metadata | Add get_task_info() returning sample counts and label mappings |

---

## E1-4: Implement Zero-Shot Evaluator [Complexity: 10, Budget: 2]

Uses BATCH_SIZE, MAX_LENGTH, DEVICE from config.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C4-1 | Log-prob classifier | Implement classify() computing choice log probabilities |
| C4-2 | Batch evaluator | Implement evaluate_task() batching and accuracy computation |

---

## E1-5: Run Experiments [Complexity: 9, Budget: 2]

Uses all config values. Orchestrates full pipeline.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C5-1 | Experiment runner | Implement run_experiment() executing full eval pipeline |
| C5-2 | Gate validation | Check all MUST_WORK gates, save results.json and figures |

---

## Config Usage Map

| Config Key | Used By | Purpose |
|------------|---------|---------|
| CHECKPOINT_NAME | E1-2 (CheckpointLoader) | Model download identifier |
| GLUE_TASKS | E1-3 (GLUELoader), E1-5 (runner) | Tasks to evaluate |
| BATCH_SIZE | E1-4 (ZeroShotEvaluator) | Inference batch size |
| MAX_LENGTH | E1-4 (ZeroShotEvaluator) | Tokenizer truncation |
| DEVICE | E1-2, E1-4 | GPU/CPU placement |
| DTYPE | E1-2 | Model precision (FP16) |
| MEMORY_LIMIT_GB | E1-5 (validate_memory) | Gate threshold |
| RANDOM_SEED | E1-5 (run_experiment) | Reproducibility |
| OUTPUT_DIR | E1-5 (save_results) | Results path |
| FIGURES_DIR | E1-5 (visualize) | Plot save path |

---

## EXISTENCE Simplifications

This PoC uses fixed values with no tuning:
- Single seed (42)
- Fixed batch size (16)
- No hyperparameter grid
- No ablation variants
- Values from HuggingFace Transformers defaults

Add hyperparameter search only if baseline fails gates.
