# Architecture: H-E1 (Behavioral Information Exists Beyond Accuracy)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT

Applied: statistical-analysis-pipeline pattern (load -> compute -> baseline -> variance -> report)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze (foundation hypothesis, no base_hypothesis_folder, no existing src/)
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

## File Structure (EXISTENCE minimal)

- `data.py` - dataset + ground truth loading
- `analysis.py` - class-wise accuracy, stratified baseline, variance analysis
- `visualize.py` - required + optional figures
- `run.py` - orchestration, result reporting
- `config.py` - fixed constants (threshold, seed, paths)

## Modules

### config.py

```python
SEED = 42
N_CLASSES = 10
RESIDUAL_RATIO_THRESHOLD = 0.05
DATA_URL = "https://zenodo.org/records/6620869/files/dataset_cifar_small_hyp_rand.pt"
DATA_PATH = "./data/dataset_cifar_small_hyp_rand.pt"
CIFAR_ROOT = "./data"
FIGURES_DIR = "./figures"
RESULTS_PATH = "./results.json"
```

### data.py

**Dependencies**: config

```python
def download_zenodo_dataset(url: str, dest: str) -> str: ...
def load_model_zoo(path: str) -> dict:  # {"weights", "metrics", "predictions"}
    ...
def load_cifar10_ground_truth(root: str) -> np.ndarray:  # shape (10000,)
    ...
def get_model_predictions(model_zoo: dict) -> dict[str, np.ndarray]:
    # model_id -> predicted labels, shape (10000,)
    ...
```

### analysis.py

**Dependencies**: numpy, sklearn.metrics

```python
def compute_class_wise_accuracy(
    predictions: dict[str, np.ndarray], ground_truth: np.ndarray, n_classes: int
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    # returns class_wise_acc (N,10), overall_acc (N,), model_ids
    ...

def stratified_baseline(class_wise_acc: np.ndarray, overall_acc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # returns baseline_pred (N,10), class_difficulty (10,)
    ...

def variance_analysis(class_wise_acc: np.ndarray, baseline_pred: np.ndarray) -> dict:
    # returns total_variance, residual_variance, residual_ratio, r2_baseline
    ...

def per_class_variance(class_wise_acc: np.ndarray) -> np.ndarray:  # shape (10,)
    ...
```

### visualize.py

**Dependencies**: matplotlib, seaborn, sklearn.decomposition.PCA, analysis

```python
def plot_gate_metric(residual_ratio: float, threshold: float, out_path: str) -> str: ...
def plot_accuracy_heatmap(class_wise_acc: np.ndarray, out_path: str) -> str: ...
def plot_variance_decomposition(residual_variance: float, total_variance: float, out_path: str) -> str: ...
def plot_per_class_variance(per_class_var: np.ndarray, out_path: str) -> str: ...
def plot_model_clustering(class_wise_acc: np.ndarray, overall_acc: np.ndarray, out_path: str) -> str: ...
```

### run.py

**Dependencies**: config, data, analysis, visualize, json

```python
def main() -> None:
    # load -> compute class-wise acc -> baseline -> variance -> figures -> write results.json
    ...

def build_report(metrics: dict, figure_paths: list[str], threshold: float) -> dict:
    # {"pass": bool, "metrics": {...}, "figures": [...]}
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Download/load Zenodo model zoo + CIFAR-10 ground truth | 8 | 2+3+2+1 |
| A-2 | Extract predictions | Get per-model predicted labels from model zoo dataset | 6 | 2+2+2+0 |
| A-3 | Class-wise accuracy | Compute (N_models,10) accuracy matrix + overall_acc | 7 | 2+2+3+0 |
| A-4 | Stratified baseline | Implement baseline formula + class_difficulty | 5 | 1+1+3+0 |
| A-5 | Variance analysis | Total/residual variance, residual_ratio, R² | 6 | 1+2+3+0 |
| A-6 | Required visualization | Gate metrics bar chart (residual_ratio vs 0.05) | 4 | 1+1+1+1 |
| A-7 | Optional visualizations | Heatmap, pie chart, per-class variance, PCA scatter | 8 | 3+2+2+1 |
| A-8 | Result reporting + orchestration | run.py pipeline, JSON output, pass/fail gate | 6 | 2+3+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8]
