# Architecture: H-M2

**Hypothesis:** Different confidence distributions require different temperature parameters for optimal calibration
**Type:** MECHANISM
**Gate:** SHOULD_WORK - CV(optimal T) > 0.1, Range(optimal T) > 0.3

Applied: temperature-scaling-nll-lbfgs (gpleiss/temperature_scaling canonical pattern, adapted per-cluster via scipy L-BFGS-B)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1) + upstream dependency (h-e1)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Findings**:
- h-m1 does NOT persist raw per-choice logits (only `confidence`/`correct` per `model.predict`) — `outputs/results.json` uses a simulated beta-distribution fallback (GPU unavailable). H-M2 **cannot** load pre-computed logits from H-M1 as PRD assumes; must regenerate scores itself.
- h-e1/code/model.py `score_choices(model, tokenizer, question, choices, device)` returns raw log-prob score list per choice (pre-softmax) — this is the "logit" vector needed for temperature scaling.
- h-e1/code/data.py `load_truthfulqa_mc()` + `assign_clusters(dataset)` give question/choices/cluster_id; `CATEGORY_TO_CLUSTER` maps into `config.CLUSTER_NAMES` (7 clusters, ids 1-7).
- h-m1/code/config.py pattern: sys.path insert of h-e1/code, re-export needed constants (`SEED`, `MODEL_ID`, `CLUSTER_NAMES`), local constants for own experiment.
- h-m1/code/train.py pattern: single `main()` orchestrator, `run_inference` loop, `plot_*` functions, `save_results_json`, `save_validation_md`.

---

## External Dependencies (Base Hypothesis / Upstream)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_truthfulqa_mc, assign_clusters, validate_cluster_sizes | `from data import load_truthfulqa_mc, assign_clusters, validate_cluster_sizes` (path-inserted) | `docs/youra_research/h-e1/code/data.py` |
| load_model_and_tokenizer, score_choices | `from model import load_model_and_tokenizer, score_choices` (path-inserted) | `docs/youra_research/h-e1/code/model.py` |
| SEED, MODEL_ID, CLUSTER_NAMES, CATEGORY_TO_CLUSTER | `import config as he1_config` | `docs/youra_research/h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, confirmed via h-m1's own import pattern in `train.py`/`config.py`)

Note: PRD's "pre-computed logits from H-M1 output" is not available in practice — H-M2 regenerates scores directly via `score_choices`, same as H-M1 did for confidences. This is the fallback path noted in `02c_experiment_brief.md` risk section.

---

## Module Structure

### config.py (`docs/youra_research/h-m2/code/config.py`)

**Dependencies**: h-e1 config

```python
# re-exported: SEED, MODEL_ID, CLUSTER_NAMES (from he1_config)
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
# Ablation configs
ABLATION_BOUNDS: list[tuple[float, float]] = [(0.5, 5.0), (0.1, 10.0)]
ABLATION_T_INIT: list[float] = [0.5, 1.0, 2.0]
```

### data_loader.py (`docs/youra_research/h-m2/code/data_loader.py`)

**Dependencies**: h-e1 data.py, h-e1 model.py

```python
def collect_logits_by_cluster(
    model, tokenizer, device
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    """Run score_choices over full dataset; group raw scores+labels by cluster_id.
    Returns (logits_by_cluster, labels_by_cluster)."""
    ...

def stratified_kfold_splits(
    labels_by_cluster: dict[int, np.ndarray], n_folds: int, seed: int
) -> dict[int, list[tuple[np.ndarray, np.ndarray]]]:
    """Per-cluster 80/20 index splits x n_folds. Returns {cluster_id: [(train_idx, val_idx), ...]}."""
    ...
```

### temperature_optim.py (`docs/youra_research/h-m2/code/temperature_optim.py`)

**Dependencies**: scipy.optimize, numpy

```python
def nll_loss(T: np.ndarray, logits: np.ndarray, labels: np.ndarray) -> float: ...

def optimize_temperature(
    logits: np.ndarray, labels: np.ndarray,
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0
) -> float:
    """scipy.optimize.minimize(method='L-BFGS-B'). Returns optimal T scalar."""
    ...

def optimize_temperature_per_cluster(
    logits_by_cluster: dict[int, np.ndarray],
    labels_by_cluster: dict[int, np.ndarray],
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0
) -> dict[int, float]:
    """Loop clusters, call optimize_temperature. Returns {cluster_id: T}."""
    ...

def cross_validate_temperatures(
    logits_by_cluster: dict[int, np.ndarray],
    labels_by_cluster: dict[int, np.ndarray],
    splits_by_cluster: dict[int, list[tuple[np.ndarray, np.ndarray]]],
    bounds: tuple[float, float] = (0.1, 10.0), t_init: float = 1.0
) -> dict[int, list[float]]:
    """Per fold, per cluster: optimize T on train split. Returns {cluster_id: [T_fold1, ..., T_fold5]}."""
    ...
```

### metrics.py (`docs/youra_research/h-m2/code/metrics.py`)

**Dependencies**: numpy, scipy.stats

```python
def compute_cv_and_range(optimal_temps: dict[int, float]) -> tuple[float, float]:
    """cv = std(T)/mean(T); t_range = max(T) - min(T)."""
    ...

def bootstrap_ci(
    temps: np.ndarray, statistic_fn: Callable, n_resamples: int = 1000, seed: int = 42
) -> tuple[float, float]:
    """scipy.stats.bootstrap 95% CI. Returns (low, high)."""
    ...

def evaluate_gate(cv: float, t_range: float) -> tuple[bool, bool]:
    """Returns (primary_pass, secondary_pass) vs config thresholds."""
    ...
```

### ablations.py (`docs/youra_research/h-m2/code/ablations.py`)

**Dependencies**: temperature_optim.py, metrics.py

```python
def run_bounds_ablation(
    logits_by_cluster: dict, labels_by_cluster: dict, bounds_list: list[tuple[float, float]]
) -> dict[str, dict]:
    """A1: re-run optimize_temperature_per_cluster per bounds setting; compute cv/range each."""
    ...

def run_init_ablation(
    logits_by_cluster: dict, labels_by_cluster: dict, t_init_list: list[float]
) -> dict[str, dict]:
    """A2: re-run per t_init; compute cv/range each."""
    ...
```

### visualize.py (`docs/youra_research/h-m2/code/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_temperature_bar(optimal_temps: dict[int, float], fold_temps: dict[int, list[float]], path: str) -> None:
    """Bar chart: mean T per cluster with std error bars (mandatory gate figure)."""
    ...

def plot_temperature_boxplot(fold_temps: dict[int, list[float]], path: str) -> None:
    """Box plot: T distribution across 5 CV folds per cluster."""
    ...

def plot_t_vs_cluster_line(optimal_temps: dict[int, float], path: str) -> None:
    """Line plot: T across ordered clusters."""
    ...

def plot_cv_bootstrap_hist(bootstrap_cvs: np.ndarray, path: str) -> None:
    """Histogram of CV across bootstrap resamples."""
    ...
```

### train.py (`docs/youra_research/h-m2/code/train.py`)

**Dependencies**: all above modules + h-e1 imports (path-insert pattern from h-m1/train.py)

```python
def save_results_json(results: dict, path: str) -> None: ...
def save_validation_md(results: dict, gate_passed: bool, path: str) -> None: ...
def main() -> None:
    """1) load model+data (h-e1), 2) collect_logits_by_cluster, 3) stratified_kfold_splits,
    4) cross_validate_temperatures, 5) optimize_temperature_per_cluster (full-data optimal T),
    6) compute_cv_and_range + bootstrap_ci, 7) evaluate_gate, 8) run_bounds_ablation + run_init_ablation,
    9) plot_* x4, 10) save_results_json + save_validation_md."""
    ...
```

---

## File Organization

- `docs/youra_research/h-m2/code/config.py`
- `docs/youra_research/h-m2/code/data_loader.py`
- `docs/youra_research/h-m2/code/temperature_optim.py`
- `docs/youra_research/h-m2/code/metrics.py`
- `docs/youra_research/h-m2/code/ablations.py`
- `docs/youra_research/h-m2/code/visualize.py`
- `docs/youra_research/h-m2/code/train.py`
- `docs/youra_research/h-m2/code/outputs/results.json`
- `docs/youra_research/h-m2/code/figures/*.png`
- `docs/youra_research/h-m2/04_validation.md` (generated)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | config.py re-exporting h-e1 constants + H-M2 params | 4 | 1+2+1+0 |
| A-2 | Data collection | data_loader.py: run score_choices over dataset, group by cluster | 9 | 3+3+2+1 |
| A-3 | Stratified CV splits | 5-fold 80/20 per-cluster split with min-size validation | 7 | 2+2+2+1 |
| A-4 | Temperature optimizer core | nll_loss + optimize_temperature (single cluster L-BFGS-B) | 8 | 2+1+4+1 |
| A-5 | Per-cluster + CV optimization | optimize_temperature_per_cluster + cross_validate_temperatures | 10 | 3+3+3+1 |
| A-6 | Metrics module | CV, range, bootstrap CI, gate evaluation | 8 | 2+2+3+1 |
| A-7 | Ablation A1/A2 | bounds sensitivity + init sensitivity re-runs | 9 | 3+3+2+1 |
| A-8 | Visualization suite | 4 plots (bar, boxplot, line, histogram) | 7 | 3+1+1+2 |
| A-9 | Main orchestrator + reporting | train.py main(), results.json, validation.md | 9 | 3+4+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5, A-6, A-7, A-9], Low(4-8): [A-1, A-3, A-4, A-8]
