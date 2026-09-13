# Architecture: h-e0

**Type:** EXISTENCE (PoC) | **Gate:** MUST_WORK | **Date:** 2026-08-09

Applied: MiniLM+LogisticRegression linear-probe pattern (belrem/llm-prompt-intent-classifier via experiment brief research)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New standalone implementation from scratch (per experiment brief: "no local codebase to analyze")

---

## File Structure (EXISTENCE minimal)

```
h-e0/code/
  data.py       # load + filter + split FLAN instruction data
  model.py      # baseline (Dummy) + proposed (MiniLM+LogReg) classifiers
  evaluate.py   # metrics, mechanism verification, gate check
  visualize.py  # required + optional figures
  train.py      # entrypoint: run pipeline end-to-end
  config.py     # fixed constants (paths, seed, thresholds)
```

---

## Modules

### config.py

```python
SEED = 42
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MIN_SAMPLES_PER_FAMILY = 500
MIN_FAMILIES = 10
MAX_TOKENS = 128
TEST_SIZE = 0.2
GATE_MACRO_F1 = 0.75
FIGURES_DIR = "h-e0/figures/"
```

### data.py (`h-e0/code/data.py`)

**Dependencies**: pandas, sklearn.model_selection, config

```python
def load_flan_metadata(csv_path: str) -> pd.DataFrame: ...
def select_families(df: pd.DataFrame, min_samples: int, min_families: int) -> list[str]: ...
def extract_prefix(text: str, max_tokens: int) -> str: ...
def build_dataset(df: pd.DataFrame, families: list[str]) -> tuple[list[str], list[str]]: ...  # (texts, labels)
def stratified_split(X: list[str], y: list[str], test_size: float, seed: int) -> tuple: ...  # X_train, X_test, y_train, y_test
```

### model.py (`h-e0/code/model.py`)

**Dependencies**: sentence_transformers, sklearn.linear_model, sklearn.dummy, sklearn.preprocessing, config

```python
class BaselineClassifier:
    def __init__(self, seed: int = SEED): ...
    def fit(self, X_texts: list[str], y_labels: list[str]) -> "BaselineClassifier": ...
    def predict(self, X_texts: list[str]) -> np.ndarray: ...

class InstructionPrefixClassifier:
    def __init__(self, model_name: str = MODEL_NAME): ...
    def encode(self, texts: list[str]) -> np.ndarray: ...          # (N, 384)
    def fit(self, X_texts: list[str], y_labels: list[str]) -> "InstructionPrefixClassifier": ...
    def predict(self, X_texts: list[str]) -> np.ndarray: ...
```

### evaluate.py (`h-e0/code/evaluate.py`)

**Dependencies**: sklearn.metrics, model

```python
def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict: ...  # macro_f1, accuracy, report
def verify_mechanism(model: InstructionPrefixClassifier, X_sample: list[str], y_sample: list[str]) -> bool: ...
def gate_check(proposed_f1: float, baseline_f1: float, threshold: float) -> dict: ...  # pass/fail + reasons
```

### visualize.py (`h-e0/code/visualize.py`)

**Dependencies**: matplotlib, sklearn.manifold (TSNE), evaluate

```python
def plot_gate_metrics(baseline_f1: float, proposed_f1: float, threshold: float, out_dir: str) -> None: ...
def plot_confusion_matrix(y_true, y_pred, labels: list[str], out_dir: str) -> None: ...
def plot_tsne_embeddings(embeddings: np.ndarray, labels: list[str], out_dir: str) -> None: ...
def plot_per_family_f1(report: dict, out_dir: str) -> None: ...
```

### train.py (`h-e0/code/train.py`)

**Dependencies**: data, model, evaluate, visualize, config

```python
def main() -> None: ...  # load -> split -> fit baseline+proposed -> evaluate -> verify -> visualize -> write 04_validation.md gate result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load FLAN metadata, filter families, extract/truncate prefixes, stratified split | 9 | 3+2+3+1 |
| A-2 | Baseline model | DummyClassifier wrapper, fit/predict | 4 | 1+1+1+1 |
| A-3 | Proposed model | MiniLM encoder + LogisticRegression wrapper (encode/fit/predict) | 10 | 3+3+3+1 |
| A-4 | Evaluation + mechanism verification | macro-F1, accuracy, classification report, shape/fit/prediction asserts | 8 | 2+2+2+2 |
| A-5 | Gate check | Compare proposed vs baseline vs 0.75 threshold, produce pass/fail | 4 | 1+1+1+1 |
| A-6 | Visualization | Gate bar chart, confusion matrix, t-SNE, per-family F1 | 8 | 2+2+2+2 |
| A-7 | Pipeline integration | train.py orchestration, write 04_validation.md | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3], Low(4-8): [A-2, A-4, A-5, A-6, A-7]

---

## Dependency Order

A-1 -> A-2, A-3 -> A-4 -> A-5 -> A-6 -> A-7
