# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** DeBERTa-v3-large-mnli P(contradiction) as hallucination signal on HaluEval
**Type:** EXISTENCE PoC
**Generated:** 2026-03-16

Applied: HuggingFace load_dataset standard pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis. Pure inference experiment — no training loop.

---

## Overview

Minimal 5-file PoC. No training. Frozen model inference + AUROC evaluation across 3 HaluEval subsets.

**File Structure:**
- `code/config.py` — single fixed config
- `code/data.py` — HaluEval loading for all 3 subsets
- `code/model.py` — CrossEncoder wrapper (NLI inference)
- `code/evaluate.py` — AUROC, DeLong, Cohen's d, structural ceiling, figures
- `code/run_experiment.py` — main entry point

**Output directories:**
- `results/` — h-e1_results.json, h-e1_summary.json
- `figures/` — gate_metrics_comparison.png, roc_curves.png, score_distributions.png, structural_ceiling.png

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    model_name: str = "cross-encoder/nli-deberta-v3-large"
    batch_size: int = 32
    max_length: int = 512
    seed: int = 42
    label_audit_n: int = 200
    auroc_threshold: float = 0.55
    tasks: tuple = ("dialogue", "qa", "summarization")
    results_dir: str = "results"
    figures_dir: str = "figures"

def get_config() -> ExperimentConfig: ...
```

---

### Data (`code/data.py`)

**Dependencies**: Config

```python
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class TaskData:
    task_name: str
    premises: List[str]
    hypotheses: List[str]
    labels: np.ndarray  # binary: 1=hallucinated, 0=non-hallucinated

def load_halueval_dialogue() -> TaskData: ...
def load_halueval_qa() -> TaskData: ...
def load_halueval_summarization() -> TaskData: ...
def load_all_tasks() -> List[TaskData]: ...
def encode_labels(raw_labels: List[str]) -> np.ndarray: ...
    # "yes" -> 1, "no" -> 0
```

---

### Model (`code/model.py`)

**Dependencies**: Config

```python
import numpy as np
from typing import List, Tuple

class NLIInferenceModel:
    def __init__(self, config): ...
    def load(self) -> None: ...
        # loads cross-encoder/nli-deberta-v3-large via sentence_transformers.CrossEncoder
        # verifies model.config.id2label for contradiction index
    def get_contradiction_index(self) -> int: ...
        # returns verified index of 'contradiction' class
    def predict(self, premises: List[str], hypotheses: List[str]) -> np.ndarray: ...
        # returns (N, 3) softmax probabilities [P(contradiction), P(entailment), P(neutral)]
        # uses torch.inference_mode(), batch_size from config, apply_softmax=True
        # logs progress every 1000 examples
    def verify_label_map(self) -> dict: ...
        # returns id2label dict; logs actual mapping
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, TaskData, NLIInferenceModel outputs

```python
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class TaskResult:
    task_name: str
    auroc: float
    delong_pvalue: float
    cohen_d: float
    auroc_max: float          # structural ceiling
    p_contradictory: float    # fraction of category A in label audit
    score_inverted: bool      # True if 1-P(contradiction) was used
    n_examples: int
    label_distribution: dict  # {0: count, 1: count}

def compute_auroc(y_true: np.ndarray, y_score: np.ndarray) -> float: ...
def delong_test(y_true: np.ndarray, y_score: np.ndarray) -> float: ...
    # returns p-value vs. AUROC=0.5 baseline
def cohen_d(scores: np.ndarray, labels: np.ndarray) -> float: ...
def check_inversion(auroc: float, y_true: np.ndarray, y_score: np.ndarray) -> Tuple[float, bool]: ...
    # if auroc < 0.5, tries 1-y_score; returns (final_auroc, inverted_flag)
def verify_mechanism_activated(scores: np.ndarray, labels: np.ndarray, task_name: str) -> Tuple[bool, dict]: ...
    # checks shape==3, std>0.05, auroc>0.5, both label classes present
def label_audit(premises: List[str], hypotheses: List[str], labels: np.ndarray,
                scores: np.ndarray, seed: int = 42, n: int = 200) -> dict: ...
    # stratified sample 200 hallucinated examples
    # returns {p_contradictory, auroc_max, category_counts}
def evaluate_task(task_name: str, scores: np.ndarray, labels: np.ndarray,
                  premises: List[str], hypotheses: List[str],
                  contradiction_idx: int, config) -> TaskResult: ...
def check_gate_condition(results: List[TaskResult], config) -> Tuple[bool, str]: ...
    # PASS: auroc>0.55 AND delong_p<0.05 on >=2/3 tasks
def plot_gate_metrics(results: List[TaskResult], output_path: str) -> None: ...
def plot_roc_curves(task_results_with_arrays: list, output_path: str) -> None: ...
def plot_score_distributions(task_results_with_arrays: list, output_path: str) -> None: ...
def plot_structural_ceiling(results: List[TaskResult], output_path: str) -> None: ...
def save_results(results: List[TaskResult], scores_dict: dict, config) -> None: ...
    # saves h-e1_results.json (per-example) and h-e1_summary.json
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: Config, Data, Model, Evaluate

```python
def setup_gpu() -> None: ...
    # detects lowest-memory GPU, sets CUDA_VISIBLE_DEVICES
def main() -> None: ...
    # 1. setup_gpu()
    # 2. config = get_config()
    # 3. tasks = load_all_tasks()
    # 4. model = NLIInferenceModel(config); model.load()
    # 5. for each task: scores = model.predict(premises, hypotheses)
    # 6. for each task: result = evaluate_task(...)
    # 7. check_gate_condition(results)
    # 8. generate all 4 figures
    # 9. save_results(results, scores_dict, config)
    # 10. print final gate PASS/FAIL

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py, requirements.txt, GPU setup utility | 5 | 1+1+1+2 |
| A-2 | Data Loading | data.py: load all 3 HaluEval subsets, field mapping, label encoding, verify distributions | 8 | 2+2+2+2 |
| A-3 | NLI Inference | model.py: CrossEncoder load, label map verification, batch predict with progress logging, inversion check | 11 | 3+2+4+2 |
| A-4 | Evaluation & Stats | evaluate.py: AUROC, DeLong test, Cohen's d, mechanism activation check, structural ceiling / label audit | 14 | 3+3+4+4 |
| A-5 | Visualization | evaluate.py figure functions: gate metrics bar, ROC curves, score distributions, structural ceiling | 9 | 2+2+3+2 |
| A-6 | Integration & Run | run_experiment.py: wire all modules, gate condition reporting, JSON output, end-to-end test | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-5, A-6], Low(4-8): [A-1, A-2]

---

## Data Flow

- `run_experiment.py` calls `data.py` → `TaskData` objects
- `run_experiment.py` calls `model.py` → `np.ndarray (N, 3)` scores per task
- `run_experiment.py` calls `evaluate.py` → `TaskResult` per task + figures + JSON output
- All intermediate scores stored in `results/h-e1_results.json` for H-M series reuse

---

## Key Interface Contracts

- `model.predict()` returns `(N, 3)` softmax array; caller uses `get_contradiction_index()` to extract score column
- `evaluate_task()` handles inversion check internally; sets `TaskResult.score_inverted=True` if applied
- `save_results()` stores full `(N, 3)` score matrix per task for downstream H-M series
- Gate: PASS requires `auroc > 0.55` AND `delong_pvalue < 0.05` on `>= 2` of 3 tasks
