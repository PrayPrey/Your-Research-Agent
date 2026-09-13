# Logic: H-E1 (Behavioral Information Exists Beyond Accuracy)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT

Applied: statistical-analysis-pipeline pattern (load -> compute -> baseline -> variance -> report)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Loading [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch/numpy I/O

### API Signatures

```python
def download_zenodo_dataset(url: str, dest: str) -> str:
    """Download file if not present. Returns dest path."""
    ...

def load_model_zoo(path: str) -> dict:
    """Load .pt file. Returns {"weights": ..., "metrics": ..., "predictions": ...}"""
    ...

def load_cifar10_ground_truth(root: str) -> np.ndarray:
    """Load CIFAR-10 test labels. Returns shape (10000,) int array."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | download_zenodo_dataset | requests/urllib streamed download with exist-check |
| L-1-2 | load_model_zoo | torch.load(path, map_location="cpu") |
| L-1-3 | load_cifar10_ground_truth | torchvision.datasets.CIFAR10(train=False), np.array(.targets) |
| L-1-4 | error handling | raise FileNotFoundError / validate keys present |

---

## A-2: Extract Predictions [Complexity: 6, Budget: 6]

**Applied**: Standard dict/array extraction

### API Signatures

```python
def get_model_predictions(model_zoo: dict) -> dict[str, np.ndarray]:
    """Extract per-model predicted labels. Returns {model_id: preds}, preds shape (10000,)"""
    ...
```

### Pseudo-code

```
1. for model_id, entry in model_zoo["predictions"].items():
2.     preds = entry.argmax(axis=-1) if entry.ndim == 2 else entry  # (10000,10) logits -> (10000,)
3.     result[model_id] = preds.astype(int)
4. return result
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | key discovery | inspect model_zoo structure, locate predictions field |
| L-2-2 | argmax conversion | handle logits (N,10) vs stored labels (N,) |
| L-2-3 | id mapping | build model_id -> preds dict, skip models w/ missing/malformed preds |

---

## A-3: Class-wise Accuracy [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch (numpy vectorized)

### API Signatures

```python
def compute_class_wise_accuracy(
    predictions: dict[str, np.ndarray],
    ground_truth: np.ndarray,
    n_classes: int,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    predictions: {model_id: (10000,)}, ground_truth: (10000,)
    Returns class_wise_acc (N,10), overall_acc (N,), model_ids (list len N)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| ground_truth | (10000,) | CIFAR-10 int labels |
| preds[model_id] | (10000,) | per-model predicted labels |
| class_wise_acc | (N, 10) | N = num models |
| overall_acc | (N,) | mean over all classes |

### Pseudo-code

```
1. for i, (model_id, pred) in enumerate(predictions.items()):
2.     for c in range(n_classes):
3.         mask = ground_truth == c
4.         class_wise_acc[i, c] = (pred[mask] == c).mean()
5.     overall_acc[i] = (pred == ground_truth).mean()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | per-class mask loop | vectorized via sklearn.metrics or boolean indexing |
| L-3-2 | overall_acc | accuracy_score(ground_truth, pred) |
| L-3-3 | model_ids alignment | preserve order matching rows of class_wise_acc |

---

## A-4: Stratified Baseline [Complexity: 5, Budget: 5]

**Applied**: Closed-form statistical formula (FR-4)

### API Signatures

```python
def stratified_baseline(
    class_wise_acc: np.ndarray, overall_acc: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Returns baseline_pred (N,10), class_difficulty (10,)"""
    ...
```

### Pseudo-code

```
1. class_difficulty = class_wise_acc.mean(axis=0)          # (10,)
2. baseline_pred = overall_acc[:, None] * class_difficulty[None, :] / class_difficulty.mean()
   # baseline_pred[i,c] = overall_acc[i] * class_difficulty[c] / mean(class_difficulty)
3. return baseline_pred, class_difficulty
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | class_difficulty | column-wise mean of class_wise_acc |
| L-4-2 | baseline formula | broadcast outer product per FR-4 |
| L-4-3 | shape validation | assert baseline_pred.shape == class_wise_acc.shape |

---

## A-5: Variance Analysis [Complexity: 6, Budget: 6]

**Applied**: Standard variance decomposition + sklearn r2_score

### API Signatures

```python
def variance_analysis(
    class_wise_acc: np.ndarray, baseline_pred: np.ndarray
) -> dict:
    """Returns {"total_variance": float, "residual_variance": float,
    "residual_ratio": float, "r2_baseline": float}"""
    ...

def per_class_variance(class_wise_acc: np.ndarray) -> np.ndarray:
    """Returns shape (10,) - variance per class across models"""
    ...
```

### Pseudo-code

```
1. residual = class_wise_acc - baseline_pred                 # (N,10)
2. total_variance = class_wise_acc.var()
3. residual_variance = residual.var()
4. residual_ratio = residual_variance / total_variance
5. r2_baseline = sklearn.metrics.r2_score(class_wise_acc.ravel(), baseline_pred.ravel())
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | variance_analysis | compute all 4 metrics per pseudo-code |
| L-5-2 | per_class_variance | class_wise_acc.var(axis=0) |
| L-5-3 | edge case | guard divide-by-zero if total_variance == 0 |

---

## A-6: Required Visualization [Complexity: 4, Budget: 4]

**Applied**: Standard matplotlib bar chart

### API Signatures

```python
def plot_gate_metric(residual_ratio: float, threshold: float, out_path: str) -> str:
    """Bar chart: residual_ratio vs threshold line. Saves PNG 300dpi. Returns out_path."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | bar plot | single bar for residual_ratio |
| L-6-2 | threshold line | axhline at threshold, red dashed |
| L-6-3 | labels | pass/fail annotation, title, ylabel |
| L-6-4 | save | savefig(out_path, dpi=300), plt.close() |

---

## A-7: Optional Visualizations [Complexity: 8, Budget: 8]

**Applied**: Standard seaborn/matplotlib + sklearn.decomposition.PCA

### API Signatures

```python
def plot_accuracy_heatmap(class_wise_acc: np.ndarray, out_path: str) -> str:
    """seaborn.heatmap of (N,10) class_wise_acc"""
    ...

def plot_variance_decomposition(residual_variance: float, total_variance: float, out_path: str) -> str:
    """Pie chart: explained vs residual variance"""
    ...

def plot_per_class_variance(per_class_var: np.ndarray, out_path: str) -> str:
    """Bar chart, shape (10,) input"""
    ...

def plot_model_clustering(class_wise_acc: np.ndarray, overall_acc: np.ndarray, out_path: str) -> str:
    """PCA(n_components=2).fit_transform(class_wise_acc) -> scatter colored by overall_acc"""
    ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | heatmap | sns.heatmap(class_wise_acc), 3 pts |
| L-7-2 | pie chart | explained = total-residual, residual, 2 pts |
| L-7-3 | per-class bar | sorted or class-index order bar, 2 pts |
| L-7-4 | PCA scatter | fit PCA, scatter c=overall_acc, colorbar, 1 pt |

---

## A-8: Result Reporting + Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard pipeline orchestration + json.dump

### API Signatures

```python
def main() -> None:
    """load -> compute class-wise acc -> baseline -> variance -> figures -> write results.json"""
    ...

def build_report(metrics: dict, figure_paths: list[str], threshold: float) -> dict:
    """Returns {"pass": bool, "metrics": {...}, "figures": [...]}"""
    ...
```

### Pseudo-code

```
1. model_zoo = load_model_zoo(DATA_PATH)
2. gt = load_cifar10_ground_truth(CIFAR_ROOT)
3. preds = get_model_predictions(model_zoo)
4. class_wise_acc, overall_acc, model_ids = compute_class_wise_accuracy(preds, gt, N_CLASSES)
5. baseline_pred, class_difficulty = stratified_baseline(class_wise_acc, overall_acc)
6. metrics = variance_analysis(class_wise_acc, baseline_pred)
7. per_class_var = per_class_variance(class_wise_acc)
8. figure_paths = [plot_gate_metric(...), plot_accuracy_heatmap(...), ...]
9. report = build_report(metrics, figure_paths, RESIDUAL_RATIO_THRESHOLD)
10. json.dump(report, open(RESULTS_PATH, "w"), indent=2)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | main pipeline | wire all module calls per pseudo-code, seed everything with SEED |
| L-8-2 | build_report | pass = residual_ratio > threshold |
| L-8-3 | json output | write RESULTS_PATH, ensure serializable (float() casts) |
