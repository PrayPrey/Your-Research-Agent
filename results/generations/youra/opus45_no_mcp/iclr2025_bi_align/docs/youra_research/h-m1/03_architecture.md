# Architecture: H-M1 (RLHF Reward Signal Conflation Analysis)

**Type:** MECHANISM | **Tier:** FULL | **Date:** 2026-08-19

Applied: Sequence-logprob confidence extraction pattern (length-normalized, reused from H-E1)
Applied: Histogram-intersection distribution overlap pattern (scipy/numpy standard)
Applied: Feature-based text classification pattern (keyword-marker scoring)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Actual H-E1 code read directly (Serena MCP unavailable; used Read tool on source files)
**Analyzed Path**: `h-e1/code/{config.py, data.py, inference.py, outputs/results.json}`
**Findings**: H-E1 `data.py` loads TruthfulQA (`truthfulqa/truthful_qa`, mc), MMLU moral_scenarios (`cais/mmlu`), Anthropic HH-RLHF (`Anthropic/hh-rlhf` test[:500]) — identical to H-M1's dataset spec (2212 tasks total). H-E1 `inference.py` provides `load_model`, `get_length_normalized_logprob`, `run_inference_on_tasks` — directly reusable, no modification needed. H-E1 `outputs/results.json` contains `per_task[].cluster_label` (0/1) needed for FR-3 correlation analysis. All 3 models match H-M1 spec exactly.

---

## File Structure

```
h-m1/code/
  config.py           # experiment config (extends H-E1 config: classification thresholds)
  task_classifier.py  # FR-1: Type A/B classification via bidirectional features
  confidence.py       # FR-2: wraps H-E1 inference.py for answer-confidence extraction
  overlap_analysis.py # FR-3/FR-4: distribution overlap, mean diff, cluster correlation
  visualize.py         # FR-5: 4 figures
  run_experiment.py    # main orchestrator
h-m1/figures/
h-m1/code/outputs/results.json
```

---

## External Dependencies (Base Hypothesis H-E1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Task (TypedDict) | `from h_e1_code.data import Task, load_all_tasks` | `h-e1/code/data.py` |
| load_model | `from h_e1_code.inference import load_model` | `h-e1/code/inference.py` |
| get_length_normalized_logprob | `from h_e1_code.inference import get_length_normalized_logprob` | `h-e1/code/inference.py` |
| ExperimentConfig (models list) | `from h_e1_code.config import CONFIG` | `h-e1/code/config.py` |
| H-E1 cluster labels | read JSON directly | `h-e1/code/outputs/results.json` → `per_task[].{task_id, cluster_label}` |

**Verified from**: `h-e1/code/` (actual implementation, read directly)

**Note**: Phase 4 Coder should either add `h-e1/code/` to `sys.path` or copy `data.py`/`inference.py` into `h-m1/code/` — H-E1 datasets/models are identical, so direct reuse (not reimplementation) is correct.

---

## Modules

### config.py (`h-m1/code/config.py`)

**Dependencies**: none

```python
DATASETS = ["truthfulqa", "mmlu_moral", "anthropic_hh"]  # same as H-E1
MODELS = [
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.2",
]
PRIMARY_MODEL_INDEX: int = 0
BATCH_SIZE: int = 16
SEED: int = 42
OVERLAP_GATE: float = 0.7
MEAN_DIFF_GATE: float = 0.1
BIDIR_SCORE_THRESHOLD: int = 1   # >=1 feature -> Type B (ABL-1 varies this: 1,2,3)
HE1_RESULTS_PATH: str = "../../h-e1/code/outputs/results.json"
```

### task_classifier.py (`h-m1/code/task_classifier.py`)

**Dependencies**: config

```python
USER_BELIEF_MARKERS = ["you think", "your opinion", "do you believe"]
CONTEXT_MARKERS = ["given that", "considering", "in this situation"]
HEDGE_MARKERS = ["might", "could", "possibly", "it depends"]

def compute_bidir_features(task_text: str) -> dict:
    ...  # {"user_belief_reference": bool, "context_dependent": bool, "hedged_answer": bool}

def classify_task_type(task_text: str, threshold: int = 1) -> str:
    ...  # "A" or "B", sum(features) >= threshold -> "B"

def classify_all_tasks(tasks: list, threshold: int = 1) -> dict[str, str]:
    ...  # {task_id: "A"|"B"}
```

### confidence.py (`h-m1/code/confidence.py`)

**Dependencies**: config, h-e1 inference.py (external)

```python
def extract_confidence_for_tasks(
    model, tokenizer, tasks: list, batch_size: int = 16
) -> dict[str, float]:
    ...  # {task_id: length_normalized_confidence}, wraps get_length_normalized_logprob
         # confidence = exp(logprob_norm) on correct_answer only

def run_all_models_confidence(tasks: list, model_ids: list[str]) -> dict[str, dict[str, float]]:
    ...  # {model_id: {task_id: confidence}}
```

### overlap_analysis.py (`h-m1/code/overlap_analysis.py`)

**Dependencies**: scipy, numpy, config

```python
def distribution_overlap(dist_a: np.ndarray, dist_b: np.ndarray, bins: int = 50) -> float: ...

def mean_confidence_diff(dist_a: np.ndarray, dist_b: np.ndarray) -> float: ...

def cluster_task_correlation(
    cluster_labels: list[int], task_types: list[str]
) -> tuple[float, float]:
    ...  # (r, p) via scipy.stats.pointbiserialr

def analyze_conflation(
    confidences: dict[str, float], task_types: dict[str, str]
) -> dict:
    ...  # {mean_a, mean_b, diff, overlap, gate_pass, gate_fail}

def cross_model_overlap(
    conf_by_model: dict[str, dict[str, float]], task_types: dict[str, str]
) -> dict[str, float]:
    ...  # {model_id: overlap_score}

def per_dataset_overlap(
    tasks: list, confidences: dict, task_types: dict
) -> dict[str, float]:
    ...  # ABL-3: {source_dataset: overlap_score}
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, config

```python
def plot_gate_metrics(overlap: float, mean_diff: float, out_path: str) -> None: ...
def plot_confidence_histograms(dist_a: np.ndarray, dist_b: np.ndarray, out_path: str) -> None: ...
def plot_cross_model_heatmap(overlap_by_model: dict[str, float], out_path: str) -> None: ...
def plot_cluster_correlation_scatter(
    cluster_labels: list[int], task_types: list[str], r: float, out_path: str
) -> None: ...
```

### run_experiment.py (`h-m1/code/run_experiment.py`)

**Dependencies**: all modules above + h-e1/code (external)

```python
def main() -> None: ...
    # 1. load_all_tasks() [from h-e1 data.py]
    # 2. classify_all_tasks() -> task_types
    # 3. load H-E1 results.json -> cluster_labels per task_id
    # 4. for each of 3 models: load_model, extract_confidence_for_tasks
    # 5. analyze_conflation() on primary model -> gate check
    # 6. cross_model_overlap() across all 3 models
    # 7. cluster_task_correlation()
    # 8. per_dataset_overlap() [ABL-3]
    # 9. generate 4 figures
    # 10. write outputs/results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + H-E1 integration | config.py; load/reuse H-E1 data.py, inference.py, results.json | 8 | 2+3+1+2 |
| M-2 | Task classifier | bidirectional feature extraction + Type A/B classification | 6 | 1+1+2+2 |
| M-3 | Confidence extraction wrapper | wrap H-E1 inference for per-task confidence, 3 models | 9 | 2+3+2+2 |
| M-4 | Overlap + gate analysis | histogram overlap, mean diff, gate logic | 7 | 2+1+3+1 |
| M-5 | Cluster correlation analysis | point-biserial correlation with H-E1 cluster labels | 5 | 1+2+2+0 |
| M-6 | Cross-model + per-dataset analysis | overlap across 3 models, per-dataset breakdown (ABL-3) | 8 | 2+2+2+2 |
| M-7 | Classification threshold ablation | ABL-1 (threshold 1/2/3), ABL-2 (single-feature) | 7 | 1+2+3+1 |
| M-8 | Visualization suite | 4 required figures | 6 | 2+1+1+2 |
| M-9 | Main runner + results output | orchestrate full pipeline, results.json | 9 | 2+3+1+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-6, M-9], Low(4-8): [M-1, M-2, M-4, M-5, M-7, M-8]

---

## Notes

- No model training — pure analysis experiment reusing H-E1's trained-model inference infrastructure.
- H-E1 datasets/models are identical to H-M1 spec; Phase 4 Coder should import/copy `h-e1/code/data.py` and `inference.py` rather than reimplement.
- Gate check uses primary model (Llama-2-7B-Chat); 13B and Mistral used for cross-model consistency heatmap only.
- ABL-1/ABL-2/ABL-3 are lightweight parameter sweeps on the same pipeline, not separate architectures.
