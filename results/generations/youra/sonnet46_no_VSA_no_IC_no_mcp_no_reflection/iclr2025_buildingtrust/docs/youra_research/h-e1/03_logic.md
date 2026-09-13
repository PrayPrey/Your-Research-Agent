---
title: "Logic: H-E1 — DPO/SFT Alignment Fingerprint Detection"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
phase: Phase 3
---

# Logic: H-E1

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Model Pair Curation [Complexity: 7, Budget: Low]

Applied: Standard Python

### API Signatures

```python
REQUIRED_FIELDS = ["sft_model_id", "dpo_model_id", "base_model_id",
                   "sft_dataset", "dpo_dataset", "source"]

def curate_pairs() -> list[dict]:
    """Return hardcoded primary pair + community pairs."""
    ...

def validate_pairs(pairs: list[dict]) -> None:
    """Assert len >= 6, required fields present, no duplicate model IDs."""
    assert len(pairs) >= 6
    seen = set()
    for p in pairs:
        for f in REQUIRED_FIELDS:
            assert f in p, f"Missing field {f}"
        for key in ("sft_model_id", "dpo_model_id"):
            assert p[key] not in seen, f"Duplicate model_id: {p[key]}"
            seen.add(p[key])

def write_pairs(pairs: list[dict], output_path: str = "model_pairs.json") -> None:
    """Write validated pairs to JSON."""
    ...

def main() -> None:
    """curate_pairs() -> validate_pairs() -> write_pairs()"""
    ...
```

### Subtasks [0/0 used]

No subtasks allocated (Low complexity).

---

## A-2: Benchmark Evaluation [Complexity: 9, Budget: Medium — 2 subtasks]

Applied: Standard subprocess + bash

### API Signatures

```python
# run_evaluations_wrapper.py — Python wrapper around run_evaluations.sh

def safe_model_id(model_id: str) -> str:
    """Replace '/' with '--' for filesystem paths."""
    return model_id.replace("/", "--")

def verify_tasks_available(tasks: list[str], lm_eval_version: str) -> dict[str, bool]:
    """Check lm-eval registry contains all required tasks before running.
    tasks: list of task names, e.g. ["truthfulqa_mc2", "bbq", ...]
    returns: {task_name: bool} availability map
    """
    ...

def handle_bbq_fallback(
    result_json: dict,
    model_id: str,
    sub_log_path: str = "results/substitutions.txt"
) -> tuple[dict, bool]:
    """Detect BBQ task failure and substitute winogrande scores.
    result_json: parsed lm-eval results dict for one model
    returns: (updated_result_json, substitution_was_made: bool)
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Task Availability Verification | subprocess call to lm_eval --tasks, parse output |
| L-2-2 | BBQ Fallback Handler | detect missing bbq key, substitute winogrande, log |

---

## L-2-1: Task Availability Verification

Applied: Standard subprocess

### API

```python
def verify_tasks_available(tasks: list[str], lm_eval_version: str) -> dict[str, bool]:
    """Subprocess lm_eval --tasks to get registry; return availability map."""
    ...
```

### Pseudo-code

```
1. result = subprocess.run(["lm_eval", "--tasks", "list"], capture_output=True, text=True)
2. if result.returncode != 0: raise RuntimeError("lm_eval not callable")
3. available_tasks = set(line.strip() for line in result.stdout.splitlines() if line.strip())
4. return {task: task in available_tasks for task in tasks}
```

---

## L-2-2: BBQ Fallback Handler

Applied: Standard dict inspection

### API

```python
def handle_bbq_fallback(
    result_json: dict,
    model_id: str,
    sub_log_path: str = "results/substitutions.txt"
) -> tuple[dict, bool]:
    """If bbq key missing from results, copy winogrande score as bbq proxy.
    result_json: {"results": {"bbq": {...}, "winogrande": {...}, ...}}
    returns: (result_json_with_bbq_filled, substituted: bool)
    """
    ...
```

### Pseudo-code

```
1. results = result_json["results"]
2. if "bbq" not in results or "acc,none" not in results.get("bbq", {}):
   a. if "winogrande" not in results: raise RuntimeError("neither bbq nor winogrande available")
   b. results["bbq"] = {"acc,none": results["winogrande"]["acc,none"]}  # proxy
   c. append to sub_log_path: f"{model_id}: bbq -> winogrande (substituted)\n"
   d. return result_json, True
3. return result_json, False
```

---

## A-3: Score Matrix Builder [Complexity: 6, Budget: Low]

Applied: Standard numpy

### API Signatures

```python
TASK_KEYS = {
    "truthfulqa_mc2": "acc,none",
    "bbq":            "acc,none",
    "winogrande":     "acc,none",
    "winograd_wsc":   "acc,none",
}

def safe_model_id(model_id: str) -> str:
    """Replace '/' with '--'."""
    return model_id.replace("/", "--")

def load_result(results_dir: str, model_id: str) -> dict[str, float]:
    """Load results/<safe_model_id>/results.json, extract 4 scores.
    returns: {"truthfulqa_mc2": float, "bbq": float, ...}  all in [0.0, 1.0]
    """
    ...

def build_matrix(
    pairs_path: str, results_dir: str
) -> tuple[np.ndarray, np.ndarray]:
    """Build X and y from all model results.
    X: np.ndarray shape=(2n, 4), dtype=float64, values in [0.0, 1.0]
    y: np.ndarray shape=(2n,),  dtype=int64,   values in {0=SFT, 1=DPO}
    """
    ...

def main() -> tuple[np.ndarray, np.ndarray]:
    """Entry point. Returns (X, y)."""
    ...
```

---

## A-4: Classification Pipeline [Complexity: 8, Budget: Low]

Applied: sklearn-permutation-test-pattern

### API Signatures

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, permutation_test_score

def run_loo_knn(X: np.ndarray, y: np.ndarray, k: int = 1) -> float:
    """LOO cross-validation with k-NN (Euclidean).
    X: [2n, 4], y: [2n,] -> mean LOO accuracy: float
    """
    ...

def run_permutation_test(
    X: np.ndarray,
    y: np.ndarray,
    k: int = 1,
    n_permutations: int = 1000,
    random_state: int = 42,
) -> tuple[float, float, np.ndarray]:
    """permutation_test_score with LOO CV.
    returns: (loo_accuracy, p_value, perm_scores: [1000,])
    """
    ...

def run_sensitivity(X: np.ndarray, y: np.ndarray) -> dict[int, float]:
    """LOO accuracy for k in {1, 3, 5}.
    returns: {1: float, 3: float, 5: float}
    """
    return {k: run_loo_knn(X, y, k=k) for k in [1, 3, 5]}

def main(X: np.ndarray, y: np.ndarray) -> dict:
    """Returns dict: {loo_accuracy, p_value, perm_scores, sensitivity}"""
    ...
```

### Tensor Shapes

| Variable | Shape | dtype |
|----------|-------|-------|
| X | (2n, 4) | float64 |
| y | (2n,) | int64 |
| perm_scores | (1000,) | float64 |

---

## A-5: Visualization [Complexity: 7, Budget: Low]

Applied: Standard matplotlib/seaborn

### API Signatures

```python
FIGURES_DIR = "../../figures"

def plot_gate_metrics(loo_accuracy: float, p_value: float, out_dir: str) -> None:
    """Bar chart: LOO acc vs 0.67 threshold vs 0.50 chance; p annotated."""
    ...

def plot_pca_scatter(X: np.ndarray, y: np.ndarray, out_dir: str) -> None:
    """PCA 2D projection. X: [2n, 4], y: [2n,] -> saved figure."""
    ...

def plot_benchmark_boxplots(X: np.ndarray, y: np.ndarray, out_dir: str) -> None:
    """4 boxplots side-by-side, DPO vs SFT per benchmark. X: [2n, 4]."""
    ...

def plot_permutation_histogram(
    perm_scores: np.ndarray, loo_accuracy: float, p_value: float, out_dir: str
) -> None:
    """Histogram of perm_scores [1000,] vs observed loo_accuracy."""
    ...

def plot_model_heatmap(
    X: np.ndarray, y: np.ndarray, model_ids: list[str], out_dir: str
) -> None:
    """Heatmap rows=models [2n], cols=4 benchmarks, color=alignment."""
    ...

def main(
    X: np.ndarray, y: np.ndarray, results: dict, model_ids: list[str]
) -> None:
    """Call all 5 plot functions; save to out_dir=FIGURES_DIR."""
    ...
```

---

## A-6: Reporting + Integration [Complexity: 8, Budget: Low]

Applied: Standard Python

### API Signatures

```python
PASS_THRESHOLD_ACC = 0.67
PASS_THRESHOLD_P   = 0.05
FAIL_THRESHOLD_ACC = 0.50

def determine_outcome(loo_accuracy: float, p_value: float) -> str:
    """Returns 'PASS' | 'FAIL' | 'INCONCLUSIVE'."""
    if loo_accuracy >= PASS_THRESHOLD_ACC and p_value <= PASS_THRESHOLD_P:
        return "PASS"
    if loo_accuracy < FAIL_THRESHOLD_ACC:
        return "FAIL"
    return "INCONCLUSIVE"

def print_report(results: dict, outcome: str) -> None:
    """Print LOO accuracy, p-value, permutation stats, sensitivity, outcome."""
    ...

def save_summary(
    results: dict, outcome: str, output_path: str = "results/summary.json"
) -> None:
    """Write summary.json: all metrics + outcome."""
    ...

def main(results: dict) -> str:
    """Returns outcome string."""
    ...
```

### Orchestrator (`main.py`)

```python
def main() -> None:
    """End-to-end pipeline."""
    # 1. curate_pairs.main()                     -> writes model_pairs.json
    # 2. verify_tasks_available(TASKS, "0.4.3")  -> abort if any False
    # 3. subprocess: bash run_evaluations.sh     -> writes results/<model>/results.json
    # 4. X, y = build_score_matrix.main()        -> X: [2n,4], y: [2n,]
    # 5. results = classify.main(X, y)           -> dict with metrics
    # 6. model_ids = load_model_ids("model_pairs.json")
    # 7. visualize.main(X, y, results, model_ids)
    # 8. outcome = report.main(results)
    # 9. sys.exit(0 if outcome == "PASS" else 1)
```
