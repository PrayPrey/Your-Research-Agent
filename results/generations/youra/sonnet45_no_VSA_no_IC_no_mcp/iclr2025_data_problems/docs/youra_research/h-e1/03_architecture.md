# Architecture: h-e1 - Data Curation Filter Transfer Test

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-24
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: Clean slate experiment - no existing codebase patterns to follow

---

## System Overview

**Pipeline:** Raw Alpaca-52k → 3 Curation Variants → 3 Fine-Tuned Models → Evaluation → Gate Decision

**Execution Model:** Sequential batch processing (single A100 GPU)

**Components:**
- CurationPipeline (FR-1): Dataset filtering with configurable thresholds
- ThresholdTuner (FR-5): Grid search for stage-tuned parameters
- TrainingOrchestrator (FR-2): Fine-tuning loop wrapper
- EvaluationRunner (FR-3): MMLU/HellaSwag evaluation
- Visualizer (FR-4): Metrics plotting

**Data Flow:**
```
Alpaca-52k → [Curation] → 3 variants → [Training] → 3 checkpoints → [Eval] → Gate metrics
                ↓
         Threshold tuning (stage-tuned variant only)
```

---

## Module Interfaces

### CurationPipeline (`code/curation.py`)

**Dependencies:** datasketch, kenlm, datasets

```python
class CurationPipeline:
    def __init__(self, dedup_threshold: float = 0.8, perplexity_cutoff: float = 100.0):
        """Initialize MinHash LSH and KenLM language model."""
        ...
    
    def apply_deduplication(self, dataset: list[dict]) -> list[dict]:
        """MinHash LSH near-duplicate removal."""
        ...
    
    def apply_perplexity_filter(self, dataset: list[dict]) -> list[dict]:
        """KenLM-based quality filtering."""
        ...
    
    def run(self, dataset: list[dict]) -> tuple[list[dict], dict]:
        """Apply dedup → perplexity, return (filtered_data, stats)."""
        ...
```

### ThresholdTuner (`code/tuning.py`)

**Dependencies:** CurationPipeline, transformers

```python
class ThresholdTuner:
    def __init__(self, base_dataset: list[dict], val_split: float = 0.05):
        """Split dataset into tune/val for grid search."""
        ...
    
    def grid_search(self, dedup_range: list[float], ppl_range: list[float]) -> dict:
        """Evaluate all threshold combinations on validation perplexity."""
        ...
    
    def get_best_thresholds(self) -> tuple[float, float]:
        """Return (dedup_threshold, perplexity_cutoff) minimizing val loss."""
        ...
```

### TrainingOrchestrator (`code/train.py`)

**Dependencies:** transformers, torch

```python
class TrainingOrchestrator:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf", seed: int = 42):
        """Load base model and tokenizer."""
        ...
    
    def prepare_dataset(self, data: list[dict], tokenizer) -> Dataset:
        """Format instruction-response pairs with loss masking."""
        ...
    
    def train(self, train_data: Dataset, val_data: Dataset, output_dir: str) -> dict:
        """Fine-tune with AdamW, log validation perplexity."""
        ...
```

### EvaluationRunner (`code/evaluate.py`)

**Dependencies:** lm_eval, transformers

```python
class EvaluationRunner:
    def __init__(self, tasks: list[str] = ["mmlu", "hellaswag"]):
        """Initialize evaluation harness."""
        ...
    
    def run_evaluation(self, model_path: str, batch_size: int = 8) -> dict:
        """Run 0-shot evaluation, return accuracy metrics."""
        ...
    
    def compute_gate_metric(self, results: dict) -> dict:
        """Calculate |acc_transferred - acc_stage_tuned| for each task."""
        ...
```

### Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib

```python
class Visualizer:
    def plot_gate_metrics(self, results: dict, save_path: str):
        """Bar chart: MMLU/HellaSwag across 3 variants."""
        ...
    
    def plot_curation_stats(self, stats: dict, save_path: str):
        """Dataset size reduction per variant."""
        ...
    
    def plot_training_curves(self, logs: dict, save_path: str):
        """Validation perplexity over epochs."""
        ...
```

### Main Experiment (`code/run_experiment.py`)

**Dependencies:** All above modules

```python
def run_poc_experiment(config: dict) -> dict:
    """
    Execute full pipeline:
    1. Load Alpaca-52k
    2. Generate 3 variants (baseline, transferred, stage-tuned)
    3. Fine-tune LLaMA-2-7B on each
    4. Evaluate on MMLU/HellaSwag
    5. Compute gate metrics
    6. Generate visualizations
    """
    ...
```

---

## File Structure

```
h-e1/
├── code/
│   ├── run_experiment.py      # Main entry point
│   ├── curation.py            # CurationPipeline
│   ├── tuning.py              # ThresholdTuner
│   ├── train.py               # TrainingOrchestrator
│   ├── evaluate.py            # EvaluationRunner
│   ├── visualize.py           # Visualizer
│   └── config.py              # Fixed configuration
├── results/
│   ├── baseline/              # Checkpoints, logs
│   ├── transferred/
│   └── stage_tuned/
└── figures/                   # Generated plots
```

---

## Configuration Schema

### Fixed Parameters (`code/config.py`)

```python
CONFIG = {
    # Model
    "model_name": "meta-llama/Llama-2-7b-hf",
    "seed": 42,
    
    # Dataset
    "dataset_name": "tatsu-lab/alpaca",
    "val_split": 0.1,
    
    # Curation - Transferred (from C4)
    "transferred_dedup": 0.8,
    "transferred_ppl": 100.0,
    
    # Curation - Stage-Tuned (grid search)
    "dedup_range": [0.6, 0.7, 0.8, 0.9],
    "ppl_range": [50, 75, 100, 150, 200],
    "tune_val_split": 0.05,
    
    # Training
    "optimizer": "adamw",
    "lr": 2e-5,
    "batch_size": 128,
    "micro_batch_size": 4,
    "gradient_accumulation_steps": 32,
    "epochs": 3,
    "weight_decay": 0.01,
    
    # Evaluation
    "tasks": ["mmlu", "hellaswag"],
    "num_fewshot": 0,
    "eval_batch_size": 8,
    
    # Gate condition
    "max_delta": 0.01,  # 1% threshold
}
```

---

## Error Handling Strategy

### HuggingFace Download Failures
```python
try:
    model = AutoModelForCausalLM.from_pretrained(model_name)
except Exception as e:
    # Retry with exponential backoff (3 attempts)
    # Fall back to cached version if available
    raise RuntimeError(f"Model download failed after retries: {e}")
```

### GPU OOM
```python
try:
    trainer.train()
except torch.cuda.OutOfMemoryError:
    # Enable gradient checkpointing
    # Reduce micro_batch_size to 2
    # Retry training
```

### KenLM Language Model Missing
```python
if not Path("en.arpa.bin").exists():
    # Download from kenlm.org/models/
    # Verify checksum
    # Fallback URL: huggingface.co/edugp/kenlm/
```

---

## Resource Management

### GPU Memory Budget (A100 40GB)
- Model parameters (7B fp32): ~28GB
- Optimizer states (AdamW): ~8GB
- Activations (batch=4): ~3GB
- **Total:** ~39GB (within limit)

**Fallbacks:**
- Enable gradient checkpointing if OOM
- Reduce micro_batch_size to 2 (double accumulation steps)

### Disk Storage (~200GB)
- Base model cache: ~14GB
- Alpaca dataset: ~50MB
- 3 fine-tuned checkpoints: ~42GB (14GB each)
- Intermediate datasets: ~150MB
- Evaluation cache: ~2GB
- **Total:** ~58GB (well under limit)

### Execution Time Estimate
- Threshold tuning: 30 min (25 combinations × 1 min)
- Fine-tuning: 6 hours (3 variants × 2 hours)
- Evaluation: 1 hour (3 models × 20 min)
- **Total:** 7.5 hours (target: ≤8 hours)

---

## Reproducibility Guarantees

### Fixed Seeds
```python
import random, torch, numpy as np

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### Checkpoint Metadata
```json
{
  "model": "meta-llama/Llama-2-7b-hf",
  "dataset": "tatsu-lab/alpaca",
  "curation": {"dedup": 0.8, "perplexity": 100},
  "training": {"lr": 2e-5, "epochs": 3, "seed": 42},
  "dataset_hash": "sha256:...",
  "timestamp": "2026-08-24T12:00:00Z"
}
```

### Deterministic Operations
- `torch.use_deterministic_algorithms(True)`
- Fixed dataset shuffling (seed=42)
- No multi-GPU data parallel (introduces non-determinism)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Pipeline | Implement curation variants (baseline, transferred, stage-tuned) | 12 | Setup(3) + Dedup(3) + Perplexity(3) + Tuning(3) |
| E-2 | Training Loop | Fine-tune LLaMA-2-7B on 3 datasets with logging | 14 | Model loading(3) + Data prep(4) + Training(5) + Checkpointing(2) |
| E-3 | Evaluation | Run MMLU/HellaSwag, compute gate metrics | 10 | Integration(4) + Batch eval(3) + Metrics(3) |
| E-4 | Orchestration | Main pipeline + error handling + visualization | 9 | Workflow(4) + Error handling(3) + Plotting(2) |

**Total Complexity:** 45 (Distribution: VeryHigh(18-20): [], High(14-17): [E-2], Medium(9-13): [E-1, E-3, E-4])

---

## Gate Decision Logic

### Success Path
```python
results = {
    "baseline": {"mmlu": 0.42, "hellaswag": 0.76},
    "transferred": {"mmlu": 0.45, "hellaswag": 0.79},
    "stage_tuned": {"mmlu": 0.46, "hellaswag": 0.79}
}

delta_mmlu = abs(results["transferred"]["mmlu"] - results["stage_tuned"]["mmlu"])
delta_hellaswag = abs(results["transferred"]["hellaswag"] - results["stage_tuned"]["hellaswag"])

if delta_mmlu <= 0.01 and delta_hellaswag <= 0.01:
    print("GATE PASSED: Filter transfer validated")
else:
    print("GATE FAILED: PIVOT required")
```

---

## Dependencies

### Python Packages
```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
datasketch>=1.6.0
kenlm>=0.2.0
lm-evaluation-harness>=0.4.0
matplotlib>=3.7.0
numpy>=1.24.0
scipy>=1.10.0
```

### External Resources
- HuggingFace Hub token (for LLaMA-2 access)
- KenLM English language model (en.arpa.bin)
- A100 GPU with 40GB VRAM

---

## Validation Checklist

- [ ] 3 dataset variants generated with correct filtering logic
- [ ] Baseline: 52,000 samples (no reduction)
- [ ] Transferred: ≥40,000 samples (dedup + perplexity)
- [ ] Stage-tuned: Variable size based on optimized thresholds
- [ ] 3 fine-tuned models with decreasing validation perplexity
- [ ] MMLU/HellaSwag results obtained for all variants
- [ ] Gate condition computed: `|acc_transferred - acc_stage_tuned|`
- [ ] All figures saved to `h-e1/figures/`
- [ ] Execution time ≤8 hours

---

**Design Principle:** Minimal PoC architecture to test "does pre-training filter transfer work?" - no over-engineering, no ablation studies, single seed verification only.
