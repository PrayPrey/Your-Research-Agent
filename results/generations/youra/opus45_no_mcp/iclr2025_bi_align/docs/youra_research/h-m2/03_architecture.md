# H-M2 Architecture: Annotator Conflation Analysis

**Applied**: Statistical comparison pipeline pattern (load → threshold sweep → group compare → visualize)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: H-M1 code and results found; inspected directly (Serena MCP unavailable in this environment, used direct file read as fallback)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: `results.json` has `per_task: [{task_id, task_type: "A"|"B", confidence_Llama_2_7b_chat, confidence_Llama_2_13b_cha, confidence_Mistral_7B_Inst}]`. Bidir features (`user_belief_reference`, `context_dependent`, `hedged_answer`) computed in `task_classifier.py` but NOT stored per-task in results.json — must recompute from raw task text for feature breakdown (A-4), or reuse `he1_results_path` data. `config.py::M1Config` gives dataset/model lists and paths.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| compute_bidir_features | `from h_m1.task_classifier import compute_bidir_features` | `docs/youra_research/h-m1/code/task_classifier.py` |
| M1Config | `from h_m1.config import CONFIG` | `docs/youra_research/h-m1/code/config.py` |
| H-M1 results | N/A (JSON) | `docs/youra_research/h-m1/code/outputs/results.json` |
| H-E1 raw tasks | N/A (JSON, referenced by `CONFIG.he1_results_path`) | `docs/youra_research/h-e1/code/outputs/results.json` |

**Verified from**: `h-m1/code/` (actual implementation), not `03_architecture.md` spec.

---

## Scope (LIGHT — analysis only, no training)

Gate: SHOULD_WORK if `|high_conf_rate(A) - high_conf_rate(B)| < 0.15` at threshold 0.7.

Models (3, from `per_task` confidence fields): `confidence_Llama_2_7b_chat`, `confidence_Llama_2_13b_cha`, `confidence_Mistral_7B_Inst`.

## File Structure

```
h-m2/code/
  loader.py            # load + validate H-M1 results.json
  threshold_sweep.py   # high-conf rate @ multiple thresholds, per model
  group_compare.py     # Type A vs Type B stats + gate check
  feature_breakdown.py # recompute bidir features, rate per feature
  model_consistency.py # cross-model rate agreement
  plots.py
  run_analysis.py      # orchestrator
  outputs/
    metrics.json
  figures/
```

## Module Interfaces

### loader.py (`h-m2/code/loader.py`)

**Dependencies**: none

```python
MODEL_FIELDS = ["confidence_Llama_2_7b_chat", "confidence_Llama_2_13b_cha", "confidence_Mistral_7B_Inst"]

def load_results(path: str = "../h-m1/code/outputs/results.json") -> list[dict]: ...
    # returns per_task list; raises if task_id/task_type/MODEL_FIELDS missing
```

### threshold_sweep.py (`h-m2/code/threshold_sweep.py`)

**Dependencies**: loader

```python
def high_conf_rate(records: list[dict], task_type: str, threshold: float, field: str = None) -> float: ...
    # field=None -> average confidence across MODEL_FIELDS per task, else use single model field
def sweep_thresholds(records: list[dict], thresholds: list[float] = [0.5,0.6,0.7,0.8,0.9]) -> dict: ...
    # {threshold: {"A": rate, "B": rate, "diff": float}}
```

### group_compare.py (`h-m2/code/group_compare.py`)

**Dependencies**: threshold_sweep

```python
def compare_groups(records: list[dict], threshold: float = 0.7) -> dict: ...
    # {"rate_A": float, "rate_B": float, "diff": float, "gate_pass": bool, "chi2_p": float}
```

### feature_breakdown.py (`h-m2/code/feature_breakdown.py`)

**Dependencies**: loader, `h_m1.task_classifier.compute_bidir_features` (requires raw text from H-E1 results — task_id join)

```python
def join_task_text(records: list[dict], he1_results_path: str) -> list[dict]: ...
    # adds "text" field via task_id lookup in H-E1 results
def breakdown_by_feature(records_with_text: list[dict], threshold: float = 0.7) -> dict: ...
    # {feature_name: {"A": rate, "B": rate}} for user_belief_reference, context_dependent, hedged_answer
```

### model_consistency.py (`h-m2/code/model_consistency.py`)

**Dependencies**: threshold_sweep

```python
def per_model_rates(records: list[dict], threshold: float = 0.7) -> dict: ...
    # {model_field: {"A": rate, "B": rate, "diff": float}} for each of MODEL_FIELDS
def consistency_score(per_model: dict) -> float:  # std dev of diffs across 3 models
    ...
```

### plots.py (`h-m2/code/plots.py`)

**Dependencies**: matplotlib

```python
def plot_threshold_sweep(sweep_result: dict, out_path: str) -> None: ...
def plot_feature_breakdown(breakdown: dict, out_path: str) -> None: ...
def plot_model_consistency(per_model: dict, out_path: str) -> None: ...
```

### run_analysis.py (`h-m2/code/run_analysis.py`)

**Dependencies**: all modules above

```python
def main(results_path: str = "../h-m1/code/outputs/results.json",
          he1_results_path: str = "../h-e1/code/outputs/results.json",
          out_dir: str = "outputs") -> None: ...
    # runs full pipeline, writes outputs/metrics.json + figures/*.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Loader + schema validation | Load H-M1 `per_task`, validate task_type/confidence fields | 4 | 1+1+1+1 |
| A-2 | Threshold sweep | High-conf rate per type across thresholds 0.5-0.9 (avg + per-model) | 6 | 2+1+2+1 |
| A-3 | Group comparison + gate check | Type A vs B diff at 0.7, chi-square test, gate pass/fail | 6 | 2+1+2+1 |
| A-4 | Feature breakdown | Join H-E1 text, recompute bidir features, rate per feature per type | 7 | 2+2+2+1 |
| A-5 | Cross-model consistency | Per-model rates for 3 models, consistency score | 5 | 2+1+1+1 |
| A-6 | Visualizations | Sweep curve, feature bar chart, model consistency chart | 5 | 2+1+1+1 |
| A-7 | Orchestrator + metrics.json | Wire pipeline, write metrics.json with gate result | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7]
