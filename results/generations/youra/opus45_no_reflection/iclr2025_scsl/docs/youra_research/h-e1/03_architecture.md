# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** CV of probe accuracy trajectories distinguishes spurious from core features (AUC >= 0.75)
**Type:** EXISTENCE — minimal architecture, 4-8 Epic tasks

Applied: feature-cache-then-probe pattern (extract once, reuse for repeated probing sweeps)
Applied: sklearn-linear-probe pattern (LogisticRegression sweep over C as training-trajectory proxy)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis or existing codebase to reuse.

---

## Module Structure

### data.py (`code/data.py`)

**Dependencies**: pandas, PIL, torch

```python
def download_waterbirds(data_dir: str) -> str: ...
def load_metadata(data_dir: str) -> "pd.DataFrame": ...

class WaterbirdsDataset:
    def __init__(self, data_dir: str, split: str, preprocess): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple: ...  # (image, y, place)
```

### features.py (`code/features.py`)

**Dependencies**: clip, torch, data.py

```python
def load_clip_model(device: str) -> tuple: ...  # (model, preprocess)

def extract_features(
    dataset: "WaterbirdsDataset", model, device: str, batch_size: int = 100
) -> tuple: ...  # (features: np.ndarray [N,512], y: np.ndarray, place: np.ndarray)

def cache_features(path: str, features, y, place) -> None: ...
def load_cached_features(path: str) -> tuple: ...
```

### cv_probe.py (`code/cv_probe.py`)

**Dependencies**: sklearn, numpy

```python
def compute_cv_for_feature(
    features: "np.ndarray", labels: "np.ndarray",
    n_subsets: int = 5, subset_frac: float = 0.2, n_epochs: int = 10, seed: int = 42
) -> float: ...

def run_cv_analysis(features, y_labels, place_labels) -> dict: ...
    # returns {"background_cv": float, "bird_type_cv": float, "trajectories": dict}
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: sklearn.metrics, numpy

```python
def compute_metrics(cv_values: list, ground_truth_spurious: list) -> dict: ...
    # returns {"auc": float, "best_f1": float}

def check_gate(metrics: dict, threshold: float = 0.75) -> bool: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_gate_comparison(auc: float, threshold: float, out_path: str) -> None: ...
def plot_cv_distribution(cv_values: dict, out_path: str) -> None: ...
def plot_roc_curve(cv_values: list, ground_truth: list, out_path: str) -> None: ...
def plot_trajectories(trajectories: dict, out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main(config_path: str = "config.yaml") -> None: ...
    # 1. download + load data
    # 2. extract/cache CLIP features
    # 3. run_cv_analysis on background + bird_type
    # 4. compute_metrics, check_gate
    # 5. generate all figures
    # 6. write results.yaml
```

### config.yaml (`code/config.yaml`)

Single fixed config: data_dir, seed=42, n_subsets=5, subset_frac=0.2, n_epochs=10, C_range=[1e-3,1e2], auc_threshold=0.75, batch_size=100.

---

## File Organization

```
code/
  config.yaml
  data.py
  features.py
  cv_probe.py
  evaluate.py
  visualize.py
  run_experiment.py
  requirements.txt
figures/
  gate_comparison.png
  cv_distribution.png
  roc_curve.png
  trajectories.png
results.yaml
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Download Waterbirds, parse metadata, build Dataset with CLIP preprocessing | 8 | 2+2+2+2 |
| A-2 | CLIP feature extraction | Load CLIP ViT-B/16, extract+L2-normalize features, cache to disk | 7 | 2+3+1+1 |
| A-3 | CV probe computation | Implement compute_cv_for_feature: subset sampling, C-sweep logistic regression, improvement-rate CV | 9 | 3+2+3+1 |
| A-4 | AUC evaluation | ROC-AUC + F1 computation, gate check against 0.75 threshold | 5 | 1+2+1+1 |
| A-5 | Visualization suite | 4 required/optional figures (gate bar, CV histogram, ROC, trajectories) | 6 | 2+1+1+2 |
| A-6 | Pipeline integration | run_experiment.py orchestration, config loading, results.yaml output | 6 | 1+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-3], Low(4-8): [A-4, A-5, A-6]
