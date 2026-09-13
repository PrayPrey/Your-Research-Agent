# Logic: H-M1 (RLHF Reward Signal Conflation Analysis)

**Scope**: Medium-complexity modules only — M-3 (Confidence extraction), M-6 (Cross-model + per-dataset), M-9 (Main runner)

Applied: Length-normalized logprob confidence extraction (reused verbatim from H-E1 `inference.py`)
Applied: Histogram-intersection overlap (scipy/numpy standard pattern)
Applied: Point-biserial correlation for binary-cluster vs categorical-type association (scipy.stats)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified directly from actual H-E1 source (Serena MCP unavailable in this environment; used Read tool)
**Analyzed Path**: `h-e1/code/{data.py, inference.py, config.py, outputs/results.json}`
**Relevant Symbols**:
- `data.Task` (TypedDict: `task_id, source_dataset, question, correct_answer, incorrect_answers, category`)
- `data.load_all_tasks() -> List[Task]`
- `inference.load_model(model_id: str) -> Tuple[model, tokenizer]` — **1 positional arg only**, no `device_map`/`dtype` params (hardcoded fp16/auto internally)
- `inference.get_length_normalized_logprob(model, tokenizer, prompt: str, answer: str) -> float`
- `inference.run_inference_on_tasks(model, tokenizer, tasks, batch_size: int = 8) -> Dict[str, Dict]`
- `outputs/results.json` → `per_task[]` has `task_id` (str) and `cluster_label` (int, 0 or 1)

**Discrepancy vs 03_architecture.md**: none material. Architecture's cited signatures match actual code exactly.

---

## M-3: Confidence Extraction Wrapper [Complexity: 9, Budget: 8]

**Applied**: Reuse H-E1 `get_length_normalized_logprob` directly — no new logprob logic needed.

### API Signatures

```python
# confidence.py
from typing import Dict, List
from inference import load_model, get_length_normalized_logprob  # H-E1, same dir or sys.path
from data import Task

def extract_confidence_for_tasks(
    model, tokenizer, tasks: List[Task], batch_size: int = 16
) -> Dict[str, float]:
    """Per-task confidence = exp(length_normalized_logprob) on correct_answer only."""
    ...

def run_all_models_confidence(
    tasks: List[Task], model_ids: List[str]
) -> Dict[str, Dict[str, float]]:
    """Loads each model via H-E1 load_model, extracts confidence, unloads. {model_id: {task_id: confidence}}"""
    ...
```

### Tensor/Data Shapes

| Variable | Type | Note |
|----------|------|------|
| confidences | `dict[str, float]` | task_id -> confidence in (0, 1] |
| conf_by_model | `dict[str, dict[str, float]]` | 3 models x 2212 tasks |

### Pseudo-code

```
extract_confidence_for_tasks(model, tokenizer, tasks, batch_size):
    out = {}
    for task in tasks (tqdm, chunked by batch_size for progress only — H-E1 fn is per-sample):
        lp_norm = get_length_normalized_logprob(model, tokenizer, task.question, task.correct_answer)
        out[task.task_id] = exp(lp_norm)   # clip exp overflow: min(exp(lp_norm), 1.0)
    return out

run_all_models_confidence(tasks, model_ids):
    result = {}
    for model_id in model_ids:
        model, tok = load_model(model_id)          # H-E1 signature: 1 arg only
        result[model_id] = extract_confidence_for_tasks(model, tok, tasks)
        del model; torch.cuda.empty_cache()
    return result
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | extract_confidence_for_tasks | wrap get_length_normalized_logprob + exp, per-task loop |
| L-M3-2 | run_all_models_confidence | loop 3 models: load_model -> extract -> unload |
| L-M3-3 | Numeric safety | clip exp() overflow, handle logprob=0.0 sentinel from H-E1 error path |
| L-M3-4 | Progress/logging | tqdm wrapper, per-model timing log |

---

## M-6: Cross-Model + Per-Dataset Analysis (ABL-3) [Complexity: 8, Budget: 8]

**Applied**: Reuse `distribution_overlap` (M-4) per model/per dataset slice — no new stats algorithm.

### API Signatures

```python
# overlap_analysis.py (additions)
import numpy as np
from typing import Dict, List

def cross_model_overlap(
    conf_by_model: Dict[str, Dict[str, float]],
    task_types: Dict[str, str],
) -> Dict[str, float]:
    """Per model: distribution_overlap(conf[type==A], conf[type==B]). {model_id: overlap_score}"""
    ...

def per_dataset_overlap(
    tasks: List[dict],
    confidences: Dict[str, float],
    task_types: Dict[str, str],
) -> Dict[str, float]:
    """ABL-3: split tasks by source_dataset, compute overlap within each. {source_dataset: overlap_score}"""
    ...
```

### Tensor/Data Shapes

| Variable | Shape/Type | Note |
|----------|------|------|
| overlap_by_model | `dict[str, float]` | 3 entries, one per model_id |
| overlap_by_dataset | `dict[str, float]` | keys: "truthfulqa", "mmlu_moral", "anthropic_hh" |

### Pseudo-code

```
cross_model_overlap(conf_by_model, task_types):
    out = {}
    for model_id, conf in conf_by_model.items():
        dist_a = np.array([conf[tid] for tid in conf if task_types[tid] == "A"])
        dist_b = np.array([conf[tid] for tid in conf if task_types[tid] == "B"])
        out[model_id] = distribution_overlap(dist_a, dist_b)
    return out

per_dataset_overlap(tasks, confidences, task_types):
    out = {}
    for ds in {"truthfulqa", "mmlu_moral", "anthropic_hh"}:
        ids = [t["task_id"] for t in tasks if t["source_dataset"] == ds]
        dist_a = np.array([confidences[i] for i in ids if task_types[i] == "A"])
        dist_b = np.array([confidences[i] for i in ids if task_types[i] == "B"])
        out[ds] = distribution_overlap(dist_a, dist_b) if len(dist_a) and len(dist_b) else float("nan")
    return out
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M6-1 | cross_model_overlap | per-model dist split + overlap call |
| L-M6-2 | per_dataset_overlap | per-dataset dist split + overlap call, empty-slice guard |
| L-M6-3 | plot_cross_model_heatmap wiring | pass overlap_by_model dict to visualize.py |
| L-M6-4 | Edge cases | dataset/model with <2 samples of a type -> NaN, log warning |

---

## M-9: Main Runner + Results Output [Complexity: 9, Budget: 8]

**Applied**: Standard sequential orchestration; no parallelism (single GPU per NFR-1).

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """Full pipeline: classify -> confidence x3 models -> analyze -> visualize -> write results.json"""
    ...

def build_results_dict(
    task_types: Dict[str, str],
    conf_by_model: Dict[str, Dict[str, float]],
    conflation_result: dict,
    cross_model: Dict[str, float],
    dataset_overlap: Dict[str, float],
    cluster_corr: tuple,
) -> dict:
    ...
```

### Tensor/Data Shapes (output JSON schema)

| Key | Type | Note |
|-----|------|------|
| `aggregate.gate_pass` | bool | overlap>0.7 or mean_diff<0.1 |
| `aggregate.overlap` / `mean_diff` | float | primary model (index 0) |
| `aggregate.cross_model_overlap` | dict[str,float] | 3 models |
| `aggregate.per_dataset_overlap` | dict[str,float] | ABL-3 |
| `aggregate.cluster_correlation` | `{r: float, p: float}` | point-biserial |
| `per_task[]` | list[dict] | `{task_id, task_type, confidence_<model_short>}` per task |

### Pseudo-code

```
main():
    cfg = CONFIG  # h-m1/code/config.py
    tasks = load_all_tasks()                                   # H-E1 data.py, 2212 tasks
    task_types = classify_all_tasks(tasks, cfg.BIDIR_SCORE_THRESHOLD)

    he1 = json.load(open(cfg.HE1_RESULTS_PATH))
    cluster_labels_by_task = {t["task_id"]: t["cluster_label"] for t in he1["per_task"]}

    conf_by_model = run_all_models_confidence(tasks, cfg.MODELS)   # M-3
    primary_conf = conf_by_model[cfg.MODELS[cfg.PRIMARY_MODEL_INDEX]]

    conflation = analyze_conflation(primary_conf, task_types)       # M-4
    gate_pass = conflation["overlap"] > cfg.OVERLAP_GATE or conflation["diff"] < cfg.MEAN_DIFF_GATE

    cross_model = cross_model_overlap(conf_by_model, task_types)    # M-6
    dataset_overlap = per_dataset_overlap(tasks, primary_conf, task_types)  # M-6

    common_ids = [tid for tid in task_types if tid in cluster_labels_by_task]
    r, p = cluster_task_correlation(
        [cluster_labels_by_task[i] for i in common_ids],
        [task_types[i] for i in common_ids],
    )                                                              # M-5

    plot_gate_metrics(conflation["overlap"], conflation["diff"], "../figures/gate_metrics.png")
    plot_confidence_histograms(dist_a, dist_b, "../figures/confidence_histograms.png")
    plot_cross_model_heatmap(cross_model, "../figures/cross_model_heatmap.png")
    plot_cluster_correlation_scatter(cluster_labels, task_types_list, r, "../figures/cluster_scatter.png")

    results = build_results_dict(task_types, conf_by_model, conflation, cross_model, dataset_overlap, (r, p))
    json.dump(results, open("outputs/results.json", "w"), indent=2)
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M9-1 | Task loading + classification wiring | call load_all_tasks, classify_all_tasks |
| L-M9-2 | H-E1 results.json ingestion | read cluster_label per task_id, handle missing IDs |
| L-M9-3 | 3-model confidence orchestration | call run_all_models_confidence, sequential load/unload |
| L-M9-4 | Primary-model gate analysis | analyze_conflation + gate_pass/gate_fail logic (PRD sec 6) |
| L-M9-5 | Cross-model + per-dataset call wiring | invoke M-6 functions with correct args |
| L-M9-6 | Cluster correlation call wiring | align common task_ids, invoke cluster_task_correlation |
| L-M9-7 | Figure generation calls | invoke all 4 visualize.py functions with correct paths |
| L-M9-8 | build_results_dict + JSON write | assemble aggregate + per_task schema, write outputs/results.json |

---

## External Dependencies API (Base Hypothesis H-E1)

Verified from `h-e1/code/` (actual implementation, read directly — no MCP available).

```python
# From: h-e1/code/data.py (ACTUAL CODE)
class Task(TypedDict):
    task_id: str
    source_dataset: str          # "truthfulqa" | "mmlu_moral" | "anthropic_hh"
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    category: Optional[str]

def load_all_tasks() -> List[Task]: ...   # returns 2212 tasks

# From: h-e1/code/inference.py (ACTUAL CODE)
def load_model(model_id: str) -> Tuple:
    """Returns (model, tokenizer). fp16, device_map='auto' hardcoded internally — no extra kwargs."""
    ...

def get_length_normalized_logprob(model, tokenizer, prompt: str, answer: str) -> float:
    """Sum logprob of answer tokens / len(answer_tokens)."""
    ...

def run_inference_on_tasks(model, tokenizer, tasks: List[Task], batch_size: int = 8) -> Dict[str, Dict]: ...

# From: h-e1/code/outputs/results.json (ACTUAL DATA, schema)
# per_task[]: {task_id: str, correct_logprob_norm: float, max_wrong_logprob_norm: float,
#              inversion_score: float, is_inverted: bool, cluster_label: int}  # 0 or 1
```

**Import note**: `load_model` takes exactly 1 positional arg (`model_id`) — do NOT pass `device_map`/`dtype` kwargs (architecture doc omits these too, consistent). Phase 4 Coder: copy or `sys.path.append` `h-e1/code/` to import `data.py`/`inference.py` unmodified.
