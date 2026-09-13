# Architecture Specification: h-m3
## Supervised AI Feedback Training System

**Date:** 2026-08-25  
**Author:** PrayPrey  
**Phase:** 3 (Implementation Planning)

---

## Codebase Analysis

**Project Type:** green-field (new supervised training pipeline)  
**Base Reference:** h-e1 (data loading patterns only)  
**Status:** New implementation - reuses h-e1 data cache, new training code  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1/code/`  
**Findings:** Reuse data loader pattern from h-e1, new HuggingFace Trainer-based training pipeline

---

## Architecture Overview

Single-script supervised learning pipeline:
- Load HumanEval/MBPP from h-e1 cache
- Add synthetic human annotations (0-10 scores)
- Fine-tune CodeBERT on (code, score) pairs
- Evaluate correlation vs baseline
- Generate 4 required figures

**Design Pattern:** HuggingFace Trainer workflow (standard supervised learning)

---

## File Structure

```
h-m3/code/
├── run_experiment.py          # Main entry point (single script)
├── data_utils.py              # Dataset loading + annotation
├── model_utils.py             # Model setup + training
├── eval_utils.py              # Correlation metrics + gate check
├── viz_utils.py               # Figure generation
└── outputs/
    ├── model_checkpoint/      # Best model weights
    └── results.json           # Metrics output
```

---

## Module Specifications

### 1. DataUtils (`data_utils.py`)

**Dependencies:** datasets, numpy

```python
from typing import List, Dict, Tuple
from datasets import Dataset
import numpy as np

class AnnotatedDataset:
    def __init__(self, cache_dir: str):
        """Load HumanEval/MBPP from h-e1 cache."""
        ...
    
    def add_synthetic_annotations(self, seed: int = 42) -> None:
        """Add synthetic human scores (0-10) based on execution results."""
        ...
    
    def get_splits(self) -> Tuple[Dataset, Dataset, Dataset]:
        """Return (train 70%, val 15%, test 15%) stratified by score."""
        ...
    
    def get_stats(self) -> Dict[str, int]:
        """Return dataset statistics."""
        ...
```

### 2. ModelUtils (`model_utils.py`)

**Dependencies:** transformers, torch

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from typing import Dict

class CodeFeedbackModel:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """Load pretrained model + regression head."""
        ...
    
    def train(self, train_dataset: Dataset, val_dataset: Dataset, output_dir: str) -> Trainer:
        """Fine-tune with MSE loss, early stopping on val loss."""
        ...
    
    def predict(self, test_dataset: Dataset) -> np.ndarray:
        """Generate predictions on test set."""
        ...
```

### 3. EvalUtils (`eval_utils.py`)

**Dependencies:** scipy, sklearn

```python
from typing import Dict, Tuple
import numpy as np

def compute_correlations(human: np.ndarray, ai: np.ndarray) -> Dict[str, float]:
    """Return {spearman_rho, spearman_p, pearson_r, mae}."""
    ...

def check_gate(spearman_rho: float, p_value: float, threshold: float = 0.7) -> Tuple[bool, str]:
    """Return (pass, message) based on >0.7 and p<0.05."""
    ...

def compare_baselines(h_e1: float, h_m1: float, h_m3: float) -> Dict[str, float]:
    """Return improvement deltas."""
    ...
```

### 4. VizUtils (`viz_utils.py`)

**Dependencies:** matplotlib

```python
from pathlib import Path
import numpy as np

def plot_baseline_comparison(h_e1: float, h_m1: float, h_m3: float, save_path: Path) -> None:
    """Bar chart with 0.7 threshold line."""
    ...

def plot_scatter(human: np.ndarray, ai: np.ndarray, save_path: Path) -> None:
    """Scatter plot with diagonal reference line."""
    ...

def plot_learning_curve(val_corrs: List[float], save_path: Path) -> None:
    """Validation correlation vs epoch."""
    ...

def plot_error_distribution(human: np.ndarray, ai: np.ndarray, save_path: Path) -> None:
    """Histogram of |human - ai| residuals."""
    ...
```

### 5. Main Script (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    """Single-command experiment execution."""
    # 1. Load data + annotations
    # 2. Train model
    # 3. Evaluate on test set
    # 4. Generate figures
    # 5. Save results
    # 6. Print gate status
    ...

if __name__ == "__main__":
    exit(main())
```

---

## Data Flow

1. **Load** h-e1 cached datasets → Parse problems + code
2. **Annotate** with synthetic human scores (execution-based)
3. **Split** stratified 70/15/15 by score distribution
4. **Tokenize** code with CodeBERT tokenizer (max_len=512)
5. **Train** 5 epochs with early stopping on val loss
6. **Predict** on test set
7. **Correlate** AI predictions vs human scores
8. **Visualize** 4 required figures

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.30.0 | Model training |
| datasets | >=2.14.0 | Data loading |
| torch | >=2.0.0 | Deep learning |
| scipy | >=1.11.0 | Statistics |
| matplotlib | >=3.7.0 | Visualization |
| scikit-learn | >=1.3.0 | Metrics |
| numpy | >=1.24.0 | Arrays |

---

## External Dependencies (h-e1 Data Cache)

**Data Source:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets`

**Import Pattern (from h-e1):**
```python
from datasets import load_dataset
import os

os.environ['HF_DATASETS_CACHE'] = '/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets'

humaneval = load_dataset("openai_humaneval", split="test")
mbpp = load_dataset("mbpp", split="test")
```

**Note:** Human annotations not in h-e1 cache → Generate synthetic scores based on execution pass/fail + random noise

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load h-e1 cache, add synthetic annotations, stratified split | 9 | 2(load)+3(annotate)+2(split)+2(validate) |
| A-2 | Model Setup | Load CodeBERT, add regression head, setup Trainer | 8 | 3(model)+2(head)+3(trainer config) |
| A-3 | Training Loop | Fine-tune with early stopping, checkpoint management | 10 | 4(training)+3(stopping)+3(checkpointing) |
| A-4 | Evaluation | Correlation metrics, statistical tests, baseline comparison | 11 | 3(correlation)+3(stats)+2(baseline)+3(gate) |
| A-5 | Visualization | Generate 4 required figures (bar, scatter, learning, error) | 9 | 2+2+3+2 (4 plots) |
| A-6 | Integration | Single-script execution, logging, reproducibility | 7 | 3(script)+2(logging)+2(seed) |

**Total:** 54 complexity points  
**Distribution:** High(10-11): [A-3, A-4], Medium(8-9): [A-1, A-2, A-5], Low(7): [A-6]

---

## Configuration Parameters

```python
# Data
CACHE_DIR = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets"
N_SAMPLES = None  # Use all available (164 HumanEval + 974 MBPP)
SPLIT_RATIOS = (0.7, 0.15, 0.15)
RANDOM_SEED = 42

# Model
MODEL_NAME = "microsoft/codebert-base"
MAX_LENGTH = 512
NUM_LABELS = 1  # Regression

# Training
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
NUM_EPOCHS = 5
EARLY_STOPPING_PATIENCE = 2
WARMUP_RATIO = 0.1

# Evaluation
GATE_THRESHOLD = 0.7
SIGNIFICANCE_LEVEL = 0.05
BASELINE_H_E1 = 0.485  # Average of 0.45-0.52 range
BASELINE_H_M1 = 0.65
```

---

## Success Metrics

### Primary Gate (MUST_WORK)
- Spearman ρ > 0.7 on test set (170 samples)
- p-value < 0.05
- Test correlation > h-m1 baseline (0.65)

### Secondary Validation
- All 4 figures generated without errors
- Training completes <30 min on GPU
- Results saved to `outputs/results.json`

---

## Implementation Notes

### Synthetic Annotation Strategy
Since h-e1 cache lacks human annotations:
```python
def generate_synthetic_scores(execution_result: bool, seed: int) -> float:
    """
    High-quality code (exec pass) → score 7-10
    Low-quality code (exec fail) → score 0-3
    Add noise for variance
    """
    np.random.seed(seed)
    if execution_result:
        return np.random.uniform(7, 10)
    else:
        return np.random.uniform(0, 3)
```

### Minimal HuggingFace Trainer Setup
```python
training_args = TrainingArguments(
    output_dir="./outputs/model_checkpoint",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    seed=42
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)
```

---

## File Paths Reference

| Component | Path |
|-----------|------|
| Main script | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m3/code/run_experiment.py` |
| Data cache | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets` |
| Output dir | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m3/code/outputs` |
| Figures dir | `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m3/figures` |

---

## Validation Checklist

- [ ] h-e1 data cache accessible at specified path
- [ ] CodeBERT model downloads successfully
- [ ] Training completes without OOM errors
- [ ] Test set has ≥170 samples
- [ ] Spearman correlation calculated correctly
- [ ] p-value < 0.05 (statistical significance)
- [ ] All 4 figures saved to figures/
- [ ] Gate pass/fail logged to 04_validation.md

---

**Next Phase:** Phase 4 - Implementation (Coder agent)
