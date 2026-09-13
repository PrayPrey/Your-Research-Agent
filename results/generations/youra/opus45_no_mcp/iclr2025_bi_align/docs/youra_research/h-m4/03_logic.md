# Logic: H-M4 (Bidirectional Tasks Show Miscalibrated Confidence)

**Type:** MECHANISM (FULL) | **Applied:** point-biserial + Cohen's d + regression-residualized partial correlation (scipy/sklearn pattern)

Analysis-only pipeline extending H-E1 outputs. No training/GPU.

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** API signatures verified from actual H-E1 code (not PRD spec, which was wrong).
**Analyzed Path:** `docs/youra_research/h-e1/code/data.py`, `docs/youra_research/h-e1/code/outputs/results.json`
**Relevant Symbols:**
- `data.py`: `Task` (TypedDict), `load_truthfulqa()`, `load_mmlu_moral()`, `load_anthropic_hh()`, `load_all_tasks() -> List[Task]`
- `results.json`: `aggregate` (silhouette, cluster_centers, n_tasks_per_cluster, models_evaluated), `per_task[]` (task_id, correct_logprob_norm, max_wrong_logprob_norm, inversion_score, is_inverted, cluster_label). **No `task_metadata` key** — PRD/brief's `h_e1_results["task_metadata"]` reference is invalid; must rejoin task text via `load_all_tasks()` on `task_id`.

**Correction vs PRD:** datasets are `truthfulqa` / `mmlu_moral` / `anthropic_hh` (not ETHICS/HHH).

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/data.py (ACTUAL CODE)
class Task(TypedDict):
    task_id: str
    source_dataset: str       # "truthfulqa" | "mmlu_moral" | "anthropic_hh"
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    category: Optional[str]

def load_all_tasks() -> List[Task]: ...
```

```python
# h-e1/code/outputs/results.json schema (ACTUAL)
{
  "aggregate": {"n_tasks_per_cluster": [1519, 693], "cluster_centers": [[..],[..]], ...},
  "per_task": [
    {"task_id": str, "correct_logprob_norm": float, "max_wrong_logprob_norm": float,
     "inversion_score": float, "is_inverted": bool, "cluster_label": 0 | 1}
  ]
}
```
Cluster 1 = higher `inversion_score` = "inverted" cluster (verify via `cluster_centers`).

---

## A-1: Data Loading [Complexity: 10]

**Applied:** dict-join on task_id (stdlib, no pandas dependency needed unless already used elsewhere in project)

### API Signatures

```python
# code/data_loader.py
import sys, json
sys.path.insert(0, "../../h-e1/code")
from data import load_all_tasks, Task

def load_e1_results(path: str = "../h-e1/code/outputs/results.json") -> dict:
    """Load H-E1 results.json."""
    ...

def load_task_texts() -> dict[str, Task]:
    """task_id -> Task dict, via h-e1 load_all_tasks()."""
    ...

def build_dataset(e1_results: dict, task_texts: dict[str, Task]) -> list[dict]:
    """Join per_task with task text on task_id.
    Returns list of records: {task_id, question, source_dataset,
    cluster_label, inversion_score, is_inverted, correct_logprob_norm,
    max_wrong_logprob_norm}. Skips task_ids with no text match.
    """
    ...
```

### Pseudo-code

```
1. e1 = load_e1_results()
2. texts = {t["task_id"]: t for t in load_all_tasks()}
3. records = []
4. for row in e1["per_task"]:
5.     t = texts.get(row["task_id"])
6.     if t is None: continue  # log skipped count
7.     records.append({**row, "question": t["question"],
8.                      "source_dataset": t["source_dataset"]})
9. assert len(records) > 0.9 * len(e1["per_task"])  # sanity: most tasks joined
10. return records
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_e1_results | Read + parse results.json |
| L-1-2 | load_task_texts | Call h-e1 load_all_tasks, index by task_id |
| L-1-3 | build_dataset | Join, skip unmatched, log counts |
| L-1-4 | sanity check | Assert join coverage, print stats |

---

## A-2: Bidirectional Feature Scoring [Complexity: 6]

**Applied:** keyword-matching binary feature scoring (standard string pattern)

### API Signatures

```python
# code/features.py
def score_bidirectional_features(task_text: str) -> dict:
    """Score 0-3 bidirectional features. Returns
    {"user_belief_reference": 0|1, "context_dependent": 0|1,
     "hedged_answer": 0|1, "total": 0-3}."""
    ...

def score_all(records: list[dict]) -> list[dict]:
    """Adds feature keys + 'bidirectional_score' (=total) to each record."""
    ...
```

### Pseudo-code

```
BELIEF_MARKERS  = ["you think","you believe","your view","your opinion","you feel","you assume","you expect"]
CONTEXT_MARKERS = ["in this context","given that","assuming","depending on","it depends","situation"]
HEDGE_MARKERS   = ["might be","could be","possibly","sometimes","it varies","not always","generally"]

def score_bidirectional_features(task_text):
    t = task_text.lower()
    f = {
      "user_belief_reference": int(any(m in t for m in BELIEF_MARKERS)),
      "context_dependent": int(any(m in t for m in CONTEXT_MARKERS)),
      "hedged_answer": int(any(m in t for m in HEDGE_MARKERS)),
    }
    f["total"] = sum(f[k] for k in ("user_belief_reference","context_dependent","hedged_answer"))
    return f
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | belief feature | keyword list + match |
| L-2-2 | context feature | keyword list + match |
| L-2-3 | hedge feature | keyword list + match |
| L-2-4 | score_all | apply per record, attach total |

---

## A-3: Confound Extraction [Complexity: 9]

**Applied:** sklearn OneHotEncoder for categorical confounds

### API Signatures

```python
# code/confounds.py
import numpy as np
from sklearn.preprocessing import OneHotEncoder

def extract_length(texts: list[str]) -> np.ndarray:  # [N,] char counts
    ...

def extract_topic_onehot(source_dataset: list[str]) -> np.ndarray:  # [N, 3]
    ...

def extract_format_onehot(texts: list[str]) -> np.ndarray:
    """Heuristic MC-vs-open: presence of 'A)'/'B)' or '\n(a)' patterns. [N, 2]"""
    ...

def extract_difficulty(records: list[dict]) -> np.ndarray:
    """abs(correct_logprob_norm - max_wrong_logprob_norm) as difficulty proxy. [N,]"""
    ...

def build_confound_matrix(records: list[dict]) -> np.ndarray:
    """Concat [length, difficulty, topic_onehot, format_onehot] -> [N, F]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| length | [N,] | char count |
| difficulty | [N,] | logprob gap |
| topic_onehot | [N, 3] | truthfulqa/mmlu_moral/anthropic_hh |
| format_onehot | [N, 2] | mc/open |
| confound_matrix | [N, 7] | concatenated, standardized before regression |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | extract_length | char count array |
| L-3-2 | extract_topic_onehot | OneHotEncoder on source_dataset |
| L-3-3 | extract_format_onehot | regex heuristic MC detection |
| L-3-4 | build_confound_matrix | concat + z-score normalize |

---

## A-4: Correlation Analysis [Complexity: 11]

**Applied:** point-biserial correlation + Cohen's d + regression-residualization partial correlation (scipy/sklearn pattern)

### API Signatures

```python
# code/correlation.py
import numpy as np
from scipy.stats import pointbiserialr, pearsonr
from sklearn.linear_model import LinearRegression

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Pooled-std standardized mean difference. group1/group2: [n1,], [n2,]"""
    ...

def compute_partial_correlation(x: np.ndarray, y: np.ndarray, confounds: np.ndarray) -> tuple[float, float]:
    """Residualize x,y on confounds via linear regression, pearsonr on residuals.
    x,y: [N,], confounds: [N, F] -> (r, p)"""
    ...

def compute_correlations(cluster_labels: np.ndarray, scores: np.ndarray, confounds: np.ndarray) -> dict:
    """cluster_labels: [N,] in {0,1}; scores: [N,] bidirectional_score 0-3;
    confounds: [N, F]. Returns
    {point_biserial_r, point_biserial_p, cohens_d, partial_r, partial_p}."""
    ...

def check_gate(metrics: dict) -> bool:
    """(r>0.4) or (d>0.3 and partial_r>0.3)"""
    ...
```

### Pseudo-code

```
def compute_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    pooled_std = sqrt(((n1-1)*std(group1,ddof=1)**2 + (n2-1)*std(group2,ddof=1)**2) / (n1+n2-2))
    return (mean(group1) - mean(group2)) / pooled_std

def compute_partial_correlation(x, y, confounds):
    x_resid = x - LinearRegression().fit(confounds, x).predict(confounds)
    y_resid = y - LinearRegression().fit(confounds, y).predict(confounds)
    return pearsonr(x_resid, y_resid)  # (r, p)

def compute_correlations(cluster_labels, scores, confounds):
    r_pb, p_pb = pointbiserialr(cluster_labels, scores)
    scores_inv = scores[cluster_labels == 1]
    scores_norm = scores[cluster_labels == 0]
    d = compute_cohens_d(scores_inv, scores_norm)
    partial_r, partial_p = compute_partial_correlation(cluster_labels.astype(float), scores, confounds)
    return {"point_biserial_r": r_pb, "point_biserial_p": p_pb,
            "cohens_d": d, "partial_r": partial_r, "partial_p": partial_p}

def check_gate(metrics):
    return (metrics["point_biserial_r"] > 0.4) or \
           (metrics["cohens_d"] > 0.3 and metrics["partial_r"] > 0.3)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | pointbiserialr | cluster vs score correlation |
| L-4-2 | compute_cohens_d | pooled-std effect size |
| L-4-3 | compute_partial_correlation | residualize + pearsonr |
| L-4-4 | compute_correlations + check_gate | assemble metrics dict, gate logic |

---

## A-5: Gate Check [Complexity: 4]

### API Signatures

```python
# code/correlation.py (continued) or h_m4_experiment.py
def save_gate_result(metrics: dict, gate_passed: bool, out_path: str) -> None: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | apply check_gate | call on metrics dict |
| L-5-2 | attach thresholds | store thresholds used (0.4/0.3/0.3) in output |
| L-5-3 | log result | print PASS/FAIL |
| L-5-4 | save | write to results.json |

---

## A-6: Cross-Model Consistency [Complexity: 8]

**Applied:** best-effort aggregate reporting (no per-model cluster_label in results.json)

### API Signatures

```python
# code/cross_model.py
def per_model_consistency(records: list[dict], models: list[str]) -> dict:
    """No per-model cluster_label exists in H-E1 outputs (single cluster_label
    used across all models_evaluated). Returns note + the single-model metrics
    duplicated as best-effort, e.g.:
    {"note": "per-model cluster labels unavailable in h-e1 results.json;
              reporting aggregate metrics only", "models_evaluated": models,
     "aggregate_metrics": <same as compute_correlations output>}"""
    ...
```

### Pseudo-code

```
def per_model_consistency(records, models):
    # h-e1 results.json has single cluster_label (not per-model) -> cannot
    # recompute correlation per model without re-running inference (out of scope).
    return {"note": "aggregate-only: per-model cluster labels unavailable",
            "models_evaluated": models}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | check per-model fields | confirm absence in results.json |
| L-6-2 | build note dict | document limitation |
| L-6-3 | attach to results | include in outputs/results.json |

---

## A-7: Required Visualization [Complexity: 5]

### API Signatures

```python
# code/visualize.py
import matplotlib.pyplot as plt

def plot_gate_metrics(metrics: dict, out_path: str = "../figures/gate_metrics.png") -> None:
    """Bar chart: point_biserial_r, cohens_d, partial_r vs thresholds (0.4,0.3,0.3)."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | bar chart | 3 metrics + threshold lines |
| L-7-2 | save figure | write to figures/gate_metrics.png |

---

## A-8: Optional Visualizations [Complexity: 7]

### API Signatures

```python
# code/visualize.py (continued)
def plot_score_by_cluster(records: list[dict], out_path: str) -> None:
    """Violin/histogram of bidirectional_score split by cluster_label."""
    ...

def plot_feature_breakdown(records: list[dict], out_path: str) -> None:
    """Stacked bar: prevalence of each of 3 features per cluster."""
    ...

def plot_scatter(records: list[dict], out_path: str) -> None:
    """Scatter: bidirectional_score vs inversion_score, colored by cluster_label."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | violin plot | score by cluster |
| L-8-2 | feature breakdown | stacked bar per feature |
| L-8-3 | scatter plot | score vs inversion_score, cluster color |

---

## A-9: Results Serialization [Complexity: 5]

### API Signatures

```python
# code/h_m4_experiment.py
import random, numpy as np

def set_seed(seed: int = 42) -> None: ...

def main() -> None:
    """load -> score features -> build confounds -> compute_correlations
    -> gate check -> cross_model consistency -> save outputs/results.json
    -> generate figures."""
    ...
```

### Pseudo-code

```
def main():
    set_seed(42)
    records = build_dataset(load_e1_results(), load_task_texts())
    records = score_all(records)
    confounds = build_confound_matrix(records)
    cluster_labels = np.array([r["cluster_label"] for r in records])
    scores = np.array([r["bidirectional_score"] for r in records])
    metrics = compute_correlations(cluster_labels, scores, confounds)
    gate_passed = check_gate(metrics)
    cross_model = per_model_consistency(records, e1["aggregate"]["models_evaluated"])
    save_json({"metrics": metrics, "gate_passed": gate_passed,
               "cross_model": cross_model, "n_tasks": len(records)},
              "outputs/results.json")
    plot_gate_metrics(metrics, "../figures/gate_metrics.png")
    # optional: plot_score_by_cluster, plot_feature_breakdown, plot_scatter
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | set_seed | seed=42 numpy/random |
| L-9-2 | assemble results dict | metrics + gate + cross_model + n_tasks |
| L-9-3 | write results.json | outputs/ dir |
| L-9-4 | orchestrate main() | call all modules in order |
