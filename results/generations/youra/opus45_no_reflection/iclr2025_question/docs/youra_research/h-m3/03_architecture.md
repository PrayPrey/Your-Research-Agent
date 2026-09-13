# Architecture: H-M3 (Linear Correctness Probe)

Applied: sklearn LogisticRegression probe pattern (concept-probes / SEP style)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: h-m2 folder contains no `code/` subfolder (docs only); H-M3 consumes H-M2's *data artifacts* (`hidden_states_l15.pt`, `correctness_labels.pt`) at runtime, not its code. No prior implementation to reuse patterns from.

---

## File Organization

- `code/data.py` - load hidden states/labels, split, scale
- `code/probe.py` - LinearCorrectnessProbe, RandomBaseline, MLP fallback
- `code/evaluate.py` - AUROC/accuracy/mechanism verification
- `code/visualize.py` - gate bar chart + ROC curve
- `code/train.py` - orchestration entrypoint
- `config.py` - hyperparameters

---

## Modules

### DataModule (`code/data.py`)

**Dependencies**: torch, sklearn.preprocessing.StandardScaler

```python
def load_hidden_states(h_m2_folder: str) -> tuple[np.ndarray, np.ndarray]: ...
def split_train_val(X: np.ndarray, y: np.ndarray, n_train: int = 9500) -> tuple: ...
def scale_features(X_train: np.ndarray, X_val: np.ndarray) -> tuple[np.ndarray, np.ndarray, StandardScaler]: ...
```

### RandomBaseline (`code/probe.py`)

**Dependencies**: numpy

```python
class RandomBaseline:
    def __init__(self, d_model: int = 4096, seed: int = 42): ...
    def score(self, X: np.ndarray) -> np.ndarray: ...  # X @ random_direction
```

### LinearCorrectnessProbe (`code/probe.py`)

**Dependencies**: sklearn.linear_model.LogisticRegression, StandardScaler

```python
class LinearCorrectnessProbe:
    def __init__(self, C: float = 1e-3, max_iter: int = 2000): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "LinearCorrectnessProbe": ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...
    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> float: ...  # returns AUROC
```

### MLPFallbackProbe (`code/probe.py`)

**Dependencies**: sklearn.neural_network.MLPClassifier

```python
class MLPFallbackProbe:
    def __init__(self, hidden_layer_sizes: tuple = (256,), max_iter: int = 500): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "MLPFallbackProbe": ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...
```

### Evaluator (`code/evaluate.py`)

**Dependencies**: sklearn.metrics, LinearCorrectnessProbe

```python
def compute_metrics(y_val: np.ndarray, probs: np.ndarray) -> dict: ...  # auroc, accuracy
def verify_mechanism(probe, X_val: np.ndarray, y_val: np.ndarray) -> dict: ...  # weight_norm, pred_std, auroc
def compare_to_baseline(probe_auroc: float, baseline_auroc: float) -> dict: ...
```

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, sklearn.metrics.roc_curve

```python
def plot_gate_comparison(achieved_auroc: float, threshold: float, out_path: str) -> None: ...
def plot_roc_curve(y_val: np.ndarray, probs: np.ndarray, auroc: float, out_path: str) -> None: ...
```

### Train Orchestrator (`code/train.py`)

**Dependencies**: DataModule, RandomBaseline, LinearCorrectnessProbe, MLPFallbackProbe, Evaluator, Visualizer

```python
def main(h_m2_folder: str, hypothesis_folder: str) -> dict: ...  # returns final results dict, handles fallback logic
```

### Config (`config.py`)

```python
SEED = 42
D_MODEL = 4096
N_TRAIN = 9500
LAYER = "l15"
PROBE_C = 1e-3
PROBE_MAX_ITER = 2000
MLP_HIDDEN = (256,)
MLP_MAX_ITER = 500
AUROC_GATE = 0.70
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load H-M2 .pt hidden states/labels, verify shapes | 6 | 2+2+1+1 |
| A-2 | Train/val split + scaling | Fixed split (9500/1700), StandardScaler fit/transform | 5 | 1+2+1+1 |
| A-3 | Random baseline | Implement random-direction scoring, 5-seed CI | 6 | 2+1+2+1 |
| A-4 | Linear probe implementation | LinearCorrectnessProbe class per spec | 7 | 2+2+2+1 |
| A-5 | Probe training run | Fit on train split, track convergence/n_iter | 6 | 1+2+2+1 |
| A-6 | Evaluation metrics | AUROC, accuracy, baseline comparison | 6 | 2+2+1+1 |
| A-7 | Mechanism verification | weight_norm, pred_std, AUROC>0.55 assertions | 5 | 1+1+2+1 |
| A-8 | Fallback MLP protocol | Conditional MLP training if AUROC<0.70 | 7 | 2+2+2+1 |
| A-9 | Visualization | Gate comparison bar chart + ROC curve figures | 6 | 2+1+1+2 |
| A-10 | End-to-end orchestration | Wire train.py, produce results JSON | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-2,A-3,A-4,A-5,A-6,A-7,A-8,A-9,A-10]

---

## External Data Dependencies (H-M2 Artifacts, not code)

| Artifact | Path | Shape |
|----------|------|-------|
| Hidden states | `{{hypothesis_folder}}/../h-m2/hidden_states_l15.pt` | (11200, 4096) |
| Labels | `{{hypothesis_folder}}/../h-m2/correctness_labels.pt` | (11200,) |

No code import paths apply — H-M2 produced only data tensors, no reusable probe/model code.
