# Logic: H-M2

**Hypothesis:** Different confidence distributions require different temperature parameters for optimal calibration
**Type:** MECHANISM

Applied: temperature-scaling-nll-lbfgs (gpleiss/temperature_scaling canonical pattern, adapted per-cluster via scipy L-BFGS-B). No direct KB match for temperature scaling; using architecture-specified canonical pattern.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1) + upstream dependency (h-e1)
**Status**: API signatures verified from actual code
**Analyzed Path**: `docs/youra_research/h-e1/code/model.py`, `docs/youra_research/h-e1/code/data.py`, `docs/youra_research/h-m1/code/config.py`
**Relevant Symbols**:
- `score_choices(model, tokenizer, question, choices, device) -> list[float]` — returns raw log-prob sums per choice (NOT softmax-applied). Confirmed via body read: uses `F.log_softmax` per-token then sums, final output is a Python list of floats, one per choice. This is the "logits" vector for temperature scaling (variable-length per question = number of choices for that question).
- `load_model_and_tokenizer(model_id=MODEL_ID) -> (model, tokenizer)` — standard load, `model.eval()` already applied.
- `load_truthfulqa_mc() -> Dataset` — HF Dataset with `question`, `mc1_targets` (dict: `choices: list[str]`, `labels: list[int]`), `category` fields.
- `assign_clusters(dataset) -> Dataset` — adds `cluster_id` int field (1-7) via `dataset.map`.
- h-m1/code/config.py pattern: `sys.path.insert(0, ... h-e1/code)`, then `from config import SEED, MODEL_ID, DTYPE, DEVICE_MAP, DATASET_ID, DATASET_CONFIG, DATASET_SPLIT, BATCH_SIZE, CATEGORY_TO_CLUSTER, CLUSTER_NAMES`.

**No pre-computed logits exist in h-m1 outputs** (verified: h-m1 stores only scalar `confidence`/`correct`, simulated via beta distribution — GPU was unavailable). H-M2 must call `score_choices` itself over the dataset.

---

## External Dependencies (h-e1 Upstream)

```python
# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
def load_model_and_tokenizer(model_id=MODEL_ID): ...  # -> (model, tokenizer)
def score_choices(model, tokenizer, question: str, choices: list[str], device) -> list[float]:
    """Log-prob score per choice (pre-softmax). len(return) == len(choices)."""

# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
def load_truthfulqa_mc() -> "Dataset":
    """HF Dataset. Fields: question(str), category(str), mc1_targets(dict: choices, labels)."""
def assign_clusters(dataset) -> "Dataset":
    """Adds cluster_id(int, 1-7) field via CATEGORY_TO_CLUSTER map."""
def validate_cluster_sizes(dataset) -> dict[int, int]: ...  # cluster_id -> count
```

**Verified from**: `docs/youra_research/h-e1/code/model.py`, `docs/youra_research/h-e1/code/data.py`

**Key correctness note**: `mc1_targets` has exactly ONE correct answer at a fixed index (usually 0 after shuffling is NOT done by h-e1 — verify `labels` list, index of `1` is the correct choice). Use `labels.index(1)` as the true class index per question.

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch / sys.path re-export pattern (matches h-m1)

```python
# config.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from config import (
    SEED, MODEL_ID, DTYPE, DEVICE_MAP, DATASET_ID, DATASET_CONFIG,
    DATASET_SPLIT, BATCH_SIZE, CATEGORY_TO_CLUSTER, CLUSTER_NAMES,
)

N_CLUSTERS: int = 7
N_FOLDS: int = 5
T_BOUNDS: tuple[float, float] = (0.1, 10.0)
T_INIT: float = 1.0
MIN_SAMPLES_PER_FOLD: int = 80
N_BOOTSTRAP: int = 1000
CV_GATE_THRESHOLD: float = 0.1
RANGE_GATE_THRESHOLD: float = 0.3
RESULTS_JSON: str = "outputs/results.json"
VALIDATION_MD: str = "../04_validation.md"
FIGURES_DIR: str = "figures/"
ABLATION_BOUNDS: list[tuple[float, float]] = [(0.5, 5.0), (0.1, 10.0)]
ABLATION_T_INIT: list[float] = [0.5, 1.0, 2.0]
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | config.py | re-export + local constants above |

---

## A-2: Data collection [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch inference loop (score_choices per question)

### API Signatures

```python
# data_loader.py
import numpy as np

def collect_logits_by_cluster(
    dataset, model, tokenizer, device
) -> tuple[dict[int, list[np.ndarray]], dict[int, list[int]]]:
    """Loop dataset rows; call score_choices per question; group by cluster_id.
    Per-question logits: np.ndarray [n_choices_i] (ragged -> stored as list, not stacked).
    Returns (logits_by_cluster, labels_by_cluster) where labels[i] = true choice index."""
    ...

def pad_and_stack_cluster(
    logits_list: list[np.ndarray], labels_list: list[int]
) -> tuple[np.ndarray, np.ndarray]:
    """Pad ragged [n_choices_i] logit vectors to [N, max_choices] with -inf; stack labels [N]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| single question logits | `[n_choices_i]` | ragged, from `score_choices` |
| padded cluster logits | `[N, C_max]` | `-inf` padding -> softmax gives 0 prob |
| cluster labels | `[N]` | int, true choice index (0-based) |

### Pseudo-code

```
1. dataset = load_truthfulqa_mc(); dataset = assign_clusters(dataset)
2. for row in dataset:
     choices = row.mc1_targets.choices
     label = row.mc1_targets.labels.index(1)
     scores = score_choices(model, tokenizer, row.question, choices, device)  # list[float]
     logits_by_cluster[row.cluster_id].append(np.array(scores))
     labels_by_cluster[row.cluster_id].append(label)
3. for cid: pad_and_stack_cluster(...) -> final dict[int, (np.ndarray[N,Cmax], np.ndarray[N])]
```

### Subtasks [3/3 used... within budget 9→3 subtasks]
| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | inference loop | run score_choices over dataset, group raw scores/labels by cluster |
| L-2-2 | ragged padding | pad_and_stack_cluster with -inf pad for softmax-safe stacking |
| L-2-3 | validation | assert per-cluster N >= MIN_SAMPLES_PER_FOLD * N_FOLDS via validate_cluster_sizes |

---

## A-3: Stratified CV splits [Complexity: 7, Budget: 7]

**Applied**: sklearn-free manual K-fold (numpy random permutation, seeded)

### API Signatures

```python
# data_loader.py (cont.)
def stratified_kfold_splits(
    labels_by_cluster: dict[int, np.ndarray], n_folds: int, seed: int
) -> dict[int, list[tuple[np.ndarray, np.ndarray]]]:
    """Per-cluster shuffled index split into n_folds groups (80/20 each fold).
    Returns {cluster_id: [(train_idx, val_idx), ...]} len == n_folds."""
    ...
```

### Pseudo-code

```
for cluster_id, labels in labels_by_cluster.items():
    N = len(labels)
    rng = np.random.RandomState(seed)
    idx = rng.permutation(N)
    fold_size = N // n_folds
    folds = []
    for k in range(n_folds):
        val_idx = idx[k*fold_size:(k+1)*fold_size]
        train_idx = np.setdiff1d(idx, val_idx)
        assert len(train_idx) >= MIN_SAMPLES_PER_FOLD
        folds.append((train_idx, val_idx))
    splits_by_cluster[cluster_id] = folds
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | stratified_kfold_splits | per-cluster seeded 5-fold split |
| L-3-2 | min-size assert | raise if any fold train split < MIN_SAMPLES_PER_FOLD |

---

## A-4: Temperature optimizer core [Complexity: 8, Budget: 8]

**Applied**: scipy L-BFGS-B minimization of NLL (gpleiss adaptation, numpy/scipy not torch)

### API Signatures

```python
# temperature_optim.py
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax

def nll_loss(T: np.ndarray, logits: np.ndarray, labels: np.ndarray) -> float:
    """T: [1]. logits: [N, C]. labels: [N]. Returns scalar mean NLL."""
    ...

def optimize_temperature(
    logits: np.ndarray, labels: np.ndarray,
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0,
) -> float:
    """scipy.optimize.minimize(nll_loss, x0=[t_init], method='L-BFGS-B', bounds=[bounds]).
    Returns result.x[0]."""
    ...
```

### Pseudo-code

```
def nll_loss(T, logits, labels):
    scaled = logits / T[0]
    probs = softmax(scaled, axis=1)
    return -np.mean(np.log(probs[np.arange(len(labels)), labels] + 1e-10))

def optimize_temperature(logits, labels, bounds, t_init):
    result = minimize(nll_loss, x0=[t_init], args=(logits, labels),
                       method='L-BFGS-B', bounds=[bounds])
    return float(result.x[0])
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | nll_loss | softmax + NLL with 1e-10 epsilon |
| L-4-2 | optimize_temperature | L-BFGS-B wrapper, single cluster |

---

## A-5: Per-cluster + CV optimization [Complexity: 10, Budget: 10]

**Applied**: loop-and-aggregate over A-4 core

### API Signatures

```python
# temperature_optim.py (cont.)
def optimize_temperature_per_cluster(
    logits_by_cluster: dict[int, np.ndarray],
    labels_by_cluster: dict[int, np.ndarray],
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0,
) -> dict[int, float]:
    """Loop clusters, call optimize_temperature on full cluster data. Returns {cluster_id: T}."""
    ...

def cross_validate_temperatures(
    logits_by_cluster: dict[int, np.ndarray],
    labels_by_cluster: dict[int, np.ndarray],
    splits_by_cluster: dict[int, list[tuple[np.ndarray, np.ndarray]]],
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0,
) -> dict[int, list[float]]:
    """Per fold, per cluster: optimize_temperature on logits[train_idx], labels[train_idx].
    Returns {cluster_id: [T_fold1, ..., T_fold5]}."""
    ...
```

### Pseudo-code

```
def optimize_temperature_per_cluster(logits_by_cluster, labels_by_cluster, bounds, t_init):
    return {cid: optimize_temperature(logits_by_cluster[cid], labels_by_cluster[cid], bounds, t_init)
            for cid in logits_by_cluster}

def cross_validate_temperatures(logits_by_cluster, labels_by_cluster, splits_by_cluster, bounds, t_init):
    out = {}
    for cid, folds in splits_by_cluster.items():
        fold_temps = []
        for train_idx, val_idx in folds:
            T = optimize_temperature(logits_by_cluster[cid][train_idx],
                                      labels_by_cluster[cid][train_idx], bounds, t_init)
            fold_temps.append(T)
        out[cid] = fold_temps
    return out
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | optimize_temperature_per_cluster | full-data per-cluster optimal T |
| L-5-2 | cross_validate_temperatures | per-fold per-cluster T |
| L-5-3 | aggregation glue | assemble fold_temps dict for metrics/viz consumption |

---

## A-6: Metrics module [Complexity: 8, Budget: 8]

**Applied**: numpy std/mean + scipy.stats.bootstrap

### API Signatures

```python
# metrics.py
import numpy as np
from scipy.stats import bootstrap
from typing import Callable

def compute_cv_and_range(optimal_temps: dict[int, float]) -> tuple[float, float]:
    """cv = std(T)/mean(T); t_range = max(T) - min(T). T = list(optimal_temps.values())."""
    ...

def bootstrap_ci(
    temps: np.ndarray, statistic_fn: Callable, n_resamples: int = 1000, seed: int = 42,
) -> tuple[float, float]:
    """scipy.stats.bootstrap((temps,), statistic_fn, n_resamples=n_resamples,
    random_state=seed).confidence_interval -> (low, high)."""
    ...

def evaluate_gate(cv: float, t_range: float) -> tuple[bool, bool]:
    """Returns (cv > CV_GATE_THRESHOLD, t_range > RANGE_GATE_THRESHOLD)."""
    ...
```

### Subtasks [2/2 used... within budget 8→2]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | compute_cv_and_range + bootstrap_ci | core stats |
| L-6-2 | evaluate_gate | threshold comparison vs config |

---

## A-7: Ablation A1/A2 [Complexity: 9, Budget: 9]

**Applied**: re-run A-5 core with varied hyperparameters

### API Signatures

```python
# ablations.py
def run_bounds_ablation(
    logits_by_cluster: dict, labels_by_cluster: dict, bounds_list: list[tuple[float, float]],
) -> dict[str, dict]:
    """A1: for each bounds in bounds_list, run optimize_temperature_per_cluster(t_init=T_INIT);
    compute cv/range. Key = f"bounds_{bounds}"."""
    ...

def run_init_ablation(
    logits_by_cluster: dict, labels_by_cluster: dict, t_init_list: list[float],
) -> dict[str, dict]:
    """A2: for each t_init in t_init_list, run optimize_temperature_per_cluster(bounds=T_BOUNDS);
    compute cv/range. Key = f"t_init_{t_init}"."""
    ...
```

### Pseudo-code

```
def run_bounds_ablation(logits_by_cluster, labels_by_cluster, bounds_list):
    out = {}
    for bounds in bounds_list:
        temps = optimize_temperature_per_cluster(logits_by_cluster, labels_by_cluster, bounds, T_INIT)
        cv, t_range = compute_cv_and_range(temps)
        out[f"bounds_{bounds}"] = {"optimal_temps": temps, "cv": cv, "range": t_range}
    return out
# run_init_ablation mirrors, varying t_init instead of bounds
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run_bounds_ablation | A1 sweep |
| L-7-2 | run_init_ablation | A2 sweep |

---

## A-8: Visualization suite [Complexity: 7, Budget: 7]

**Applied**: matplotlib standard bar/box/line/hist

### API Signatures

```python
# visualize.py
def plot_temperature_bar(optimal_temps: dict[int, float], fold_temps: dict[int, list[float]], path: str) -> None:
    """Bar: mean T per cluster, yerr=std(fold_temps[cid]). MANDATORY gate figure."""
    ...

def plot_temperature_boxplot(fold_temps: dict[int, list[float]], path: str) -> None:
    """Box: T distribution per cluster across 5 folds."""
    ...

def plot_t_vs_cluster_line(optimal_temps: dict[int, float], path: str) -> None:
    """Line: T vs cluster_id (ordered 1-7)."""
    ...

def plot_cv_bootstrap_hist(bootstrap_cvs: np.ndarray, path: str) -> None:
    """Hist: distribution of CV across bootstrap resamples."""
    ...
```

### Subtasks [2/2 used... within budget 7]
| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | plot_temperature_bar + boxplot | mandatory + fold distribution figs |
| L-8-2 | plot_t_vs_cluster_line + cv_bootstrap_hist | remaining 2 figs |

---

## A-9: Main orchestrator + reporting [Complexity: 9, Budget: 9]

**Applied**: single main() orchestrator pattern (matches h-m1/train.py)

### API Signatures

```python
# train.py
def save_results_json(results: dict, path: str) -> None: ...
def save_validation_md(results: dict, gate_passed: bool, path: str) -> None: ...

def main() -> None:
    """1) load_model_and_tokenizer, load_truthfulqa_mc + assign_clusters
    2) collect_logits_by_cluster -> pad_and_stack_cluster per cluster
    3) stratified_kfold_splits
    4) cross_validate_temperatures -> fold_temps
    5) optimize_temperature_per_cluster -> optimal_temps (full data)
    6) compute_cv_and_range(optimal_temps) + bootstrap_ci on temps array
    7) evaluate_gate(cv, t_range)
    8) run_bounds_ablation + run_init_ablation
    9) plot_temperature_bar/boxplot/line/hist
    10) save_results_json + save_validation_md"""
    ...
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | main() orchestration | steps 1-8 wiring |
| L-9-2 | save_results_json | serialize optimal_temps, fold_temps, cv, range, ci, gate, ablations |
| L-9-3 | save_validation_md | PASS/FAIL report to ../04_validation.md |

---

**Total subtasks used**: 3+3+2+2+3+2+2+2+3 = 22 (within per-task budgets; task-level budget field is complexity points, not subtask count — subtask counts follow architecture's stated breakdown column)
