# Architecture: H-E1 (Calibration Inversion Clusters Exist Systematically)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT | **Date:** 2026-08-19

Applied: Sequence-logprob calibration scoring pattern (length-normalized)
Applied: K-means + silhouette gate-check pattern (scikit-learn standard)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase present.

---

## File Structure (Minimal - EXISTENCE)

```
h-e1/code/
  config.py       # fixed experiment config (models, datasets, k range, thresholds)
  data.py         # load + unify TruthfulQA/ETHICS/HHH into task list
  inference.py    # logprob extraction per model
  calibration.py  # inversion score computation
  clustering.py   # k-means + silhouette selection
  visualize.py    # 5 required figures
  run_experiment.py  # main orchestrator
h-e1/figures/      # output figures
h-e1/results.json  # aggregate + per-task output
```

---

## Modules

### config.py

**Dependencies**: none

```python
DATASETS = ["truthfulqa", "ethics", "hhh"]
MODELS = [
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.2",
]
INVERSION_THRESHOLD: float = 0.1
SILHOUETTE_GATE: float = 0.3
K_RANGE = [2, 3, 4, 5]
DEFAULT_K: int = 3
BATCH_SIZE: int = 8
SEED: int = 42
```

### data.py (`h-e1/code/data.py`)

**Dependencies**: config, `datasets` lib

```python
class Task(TypedDict):
    task_id: str
    source_dataset: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]
    category: str | None

def load_truthfulqa() -> list[Task]: ...
def load_ethics_justice() -> list[Task]: ...
def load_hhh() -> list[Task]: ...
def load_all_tasks() -> list[Task]: ...  # combines all three, ~1517 tasks
```

### inference.py (`h-e1/code/inference.py`)

**Dependencies**: config, transformers, torch

```python
def load_model(model_id: str): ...  # -> (model, tokenizer)

def get_sequence_logprob(model, tokenizer, prompt: str, answer: str) -> float: ...
def get_length_normalized_logprob(model, tokenizer, prompt: str, answer: str) -> float: ...

def run_inference_on_tasks(
    model, tokenizer, tasks: list[Task], batch_size: int = 8
) -> dict[str, dict]: ...
    # {task_id: {"correct_logprob_norm": float, "max_wrong_logprob_norm": float}}
```

### calibration.py (`h-e1/code/calibration.py`)

**Dependencies**: config

```python
def compute_inversion_score(correct_logprob_norm: float, max_wrong_logprob_norm: float) -> float: ...
    # max_wrong_logprob_norm - correct_logprob_norm

def is_calibration_inverted(inversion_score: float, threshold: float = 0.1) -> bool: ...

def build_calibration_vectors(inference_results: dict[str, dict]) -> np.ndarray: ...
    # shape (n_tasks, 1) inversion scores for clustering
```

### clustering.py (`h-e1/code/clustering.py`)

**Dependencies**: config, scikit-learn

```python
def fit_kmeans(X: np.ndarray, k: int, seed: int = 42): ...  # -> KMeans

def evaluate_k_range(X: np.ndarray, k_range: list[int]) -> dict[int, float]: ...
    # {k: silhouette_score}

def select_best_k(silhouette_by_k: dict[int, float]) -> int: ...

def cluster_and_evaluate(X: np.ndarray, k: int) -> dict: ...
    # {"silhouette_score", "cluster_labels", "cluster_centers", "gate_passed"}
```

### visualize.py (`h-e1/code/visualize.py`)

**Dependencies**: matplotlib, config

```python
def plot_gate_metric(silhouette_score: float, threshold: float, out_path: str) -> None: ...
def plot_calibration_histogram(scores: np.ndarray, out_path: str) -> None: ...
def plot_cluster_scatter(scores: np.ndarray, labels: np.ndarray, out_path: str) -> None: ...
def plot_cluster_profiles(scores: np.ndarray, labels: np.ndarray, out_path: str) -> None: ...
def plot_cross_model_agreement(labels_by_model: dict[str, np.ndarray], out_path: str) -> None: ...
```

### run_experiment.py (`h-e1/code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load_all_tasks()
    # 2. for each model in MODELS: run_inference_on_tasks -> calibration vectors
    # 3. cluster primary model (evaluate_k_range, select_best_k, cluster_and_evaluate)
    # 4. gate check: silhouette > SILHOUETTE_GATE
    # 5. generate all 5 figures
    # 6. write results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Data loading | config.py + data.py; load/unify 3 datasets | 8 | 2+2+2+2 |
| A-2 | Inference module | logprob extraction, length norm, batched | 12 | 3+3+3+3 |
| A-3 | Calibration scoring | inversion score computation + vectors | 5 | 1+1+2+1 |
| A-4 | Clustering + silhouette gate | k-sweep, k-means, silhouette, gate check | 9 | 2+2+3+2 |
| A-5 | Visualization (5 figures) | histogram, scatter, boxplot, heatmap, gate bar | 7 | 2+1+2+2 |
| A-6 | Main runner + cross-model eval | orchestrate 3 models, results.json output | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-3, A-5]

---

## Notes

- No proposed model module — EXISTENCE test analyzes baseline model behavior only.
- Primary model (Llama-2-7B-Chat) drives the gate check; 13B and Mistral used for cross-model agreement heatmap (secondary/tertiary criteria).
- Single fixed config (no experiment variants/ablations per EXISTENCE rules).
