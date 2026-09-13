# Logic Design: H-E1 AUROC Discriminative Degradation Analysis

**Applied**: HuggingFace transformers logit extraction pattern
**Applied**: sklearn AUROC binary classification pattern
**Applied**: NumPy bootstrap resampling pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase to analyze
**Findings**: New implementation from scratch; designing APIs based on PRD and Architecture specifications.

---

## API Specifications

### 1. Data Module (`data.py`)

```python
from datasets import Dataset
from typing import Iterator

def load_mmlu_test() -> Dataset:
    """
    Load MMLU test split from HuggingFace.
    Returns: Dataset with columns: question, subject, choices, answer (int 0-3)
    """
    pass

def format_prompt(sample: dict) -> str:
    """Format MMLU sample into MCQ prompt string ending with 'Answer:'"""
    pass

def get_dataloader(dataset: Dataset, start_idx: int = 0) -> Iterator[dict]:
    """Create resumable iterator over dataset samples."""
    pass
```

### 2. Inference Module (`inference.py`)

```python
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset

def load_model(model_id: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load model with torch_dtype=float16, device_map='cuda'."""
    pass

def unload_model(model: AutoModelForCausalLM) -> None:
    """Unload model, call torch.cuda.empty_cache() and gc.collect()."""
    pass

def get_choice_token_ids(tokenizer: AutoTokenizer) -> list[int]:
    """Get token IDs for ' A', ' B', ' C', ' D'."""
    pass

def extract_choice_logits(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    choice_ids: list[int]
) -> np.ndarray:
    """
    Extract logits for answer choices at last token position.
    Returns: np.ndarray of shape (4,)
    
    Tensor Flow:
        input_ids: (1, seq_len) -> outputs.logits: (1, seq_len, vocab_size)
        -> last_token_logits: (vocab_size,) -> choice_logits: (4,)
    """
    pass

def compute_margin(logits: np.ndarray) -> float:
    """Compute margin = logit_top1 - logit_top2."""
    pass

def run_model_inference(
    model_id: str,
    dataset: Dataset,
    cache_path: str,
    start_idx: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run full inference with checkpointing every 1000 samples.
    Returns: (margins, correctness) arrays of shape (N,)
    """
    pass
```

### 3. Metrics Module (`metrics.py`)

```python
import numpy as np

def compute_auroc_with_ci(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> dict[str, float]:
    """
    Compute AUROC with bootstrap 95% CI.
    Returns: {"auroc": float, "ci_lower": float, "ci_upper": float}
    """
    pass

def compute_conditional_margins(
    margins: np.ndarray,
    correctness: np.ndarray
) -> dict[str, float]:
    """Returns: {"mean_correct": float, "mean_incorrect": float}"""
    pass

def compute_i2_statistic(
    deltas: list[float],
    ci_lowers: list[float],
    ci_uppers: list[float]
) -> float:
    """Compute I² heterogeneity statistic for meta-analysis."""
    pass

def evaluate_gate_criteria(results: dict) -> dict[str, bool]:
    """
    Evaluate MUST_WORK gate: AUROC_base > AUROC_instruct AND CI_lower(delta) > 0
    Returns: {"qwen": bool, "llama": bool, "mistral": bool, "all_pass": bool}
    """
    pass
```

### 4. Visualization Module (`visualize.py`)

```python
def plot_auroc_comparison(results: dict, save_path: str) -> None:
    """Grouped bar chart: 3 families, base vs instruct, with CI error bars."""
    pass

def plot_margin_distributions(margins_by_model: dict, correctness: np.ndarray, save_path: str) -> None:
    """KDE plots: correct vs incorrect per model."""
    pass

def plot_forest(results: dict, save_path: str) -> None:
    """Forest plot: AUROC delta per family + pooled estimate."""
    pass

def save_all_figures(results: dict, margins_by_model: dict, figures_dir: str) -> None:
    """Generate and save all figures."""
    pass
```

### 5. Orchestrator (`run_experiment.py`)

```python
def load_or_run_inference(family: str, variant: str, model_id: str, dataset) -> tuple:
    """Load cached results or run inference."""
    pass

def run_family(family: str, dataset) -> dict:
    """Run evaluation for one model family with memory management."""
    pass

def save_results(all_results: dict, results_dir: str) -> None:
    """Save results to auroc_results.yaml."""
    pass

def generate_validation_report(all_results: dict, gate: dict, output_path: str) -> None:
    """Generate 04_validation.md report."""
    pass

def main() -> None:
    """Main orchestrator: load data, run families, save results."""
    pass
```

---

## Tensor Shape Summary

| Location | Variable | Shape | Type |
|----------|----------|-------|------|
| extract_choice_logits | input_ids | (1, seq_len) | torch.LongTensor |
| extract_choice_logits | outputs.logits | (1, seq_len, vocab_size) | torch.FloatTensor |
| extract_choice_logits | choice_logits | (4,) | np.ndarray |
| run_model_inference | margins | (N,) | np.ndarray |
| run_model_inference | correctness | (N,) | np.ndarray |

---

## Subtasks (6 allocated)

### E3: Inference Engine (4 subtasks)
| ID | Subtask | Description |
|----|---------|-------------|
| E3.1 | Model Loading | load_model() with fp16, CUDA, pad token |
| E3.2 | Token Mapping | get_choice_token_ids() |
| E3.3 | Logit Extraction | extract_choice_logits() |
| E3.4 | Checkpoint System | run_model_inference() with .npy caching |

### E4: Metrics (2 subtasks)
| ID | Subtask | Description |
|----|---------|-------------|
| E4.1 | AUROC + Bootstrap | compute_auroc_with_ci() |
| E4.2 | Gate Evaluation | evaluate_gate_criteria() |

---

*Generated by Phase 3 Logic Agent*
