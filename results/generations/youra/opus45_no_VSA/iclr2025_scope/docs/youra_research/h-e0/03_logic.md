# Logic: h-e0

**Type:** EXISTENCE (PoC)

Applied: MiniLM+LogisticRegression linear-probe pattern (frozen encoder + sklearn linear classifier)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 9, Budget: 9]

**Applied**: pandas stratified split (standard sklearn `train_test_split(stratify=y)`)

### API Signatures

```python
import pandas as pd

def load_flan_metadata(csv_path: str) -> pd.DataFrame:
    """Load FLAN CSV with columns: instruction, task_family."""
    ...

def select_families(df: pd.DataFrame, min_samples: int = 500, min_families: int = 10) -> list[str]:
    """Return family names with >= min_samples rows, must have >= min_families."""
    ...

def extract_prefix(text: str, max_tokens: int = 128) -> str:
    """Whitespace-truncate text to max_tokens words."""
    ...

def build_dataset(df: pd.DataFrame, families: list[str]) -> tuple[list[str], list[str]]:
    """Filter df to families, apply extract_prefix. Returns (texts, labels)."""
    ...

def stratified_split(
    X: list[str], y: list[str], test_size: float = 0.2, seed: int = 42
) -> tuple[list[str], list[str], list[str], list[str]]:
    """sklearn train_test_split(stratify=y). Returns X_train, X_test, y_train, y_test."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | load+select | `load_flan_metadata` + `select_families` |
| L-A1-2 | extract | `extract_prefix` (word-split truncation) |
| L-A1-3 | build | `build_dataset` filter+map |
| L-A1-4 | split | `stratified_split` wrapping `train_test_split` |

---

## A-2/A-3: Baseline + Proposed Models [Complexity: 4+10, Budget: 14]

**Applied**: Frozen sentence-transformer embedding + `LogisticRegression(multi_class='multinomial', solver='lbfgs', class_weight='balanced')`

### API Signatures

```python
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer

class BaselineClassifier:
    def __init__(self, seed: int = 42):
        self.clf = DummyClassifier(strategy="stratified", random_state=seed)

    def fit(self, X_texts: list[str], y_labels: list[str]) -> "BaselineClassifier":
        self.clf.fit(X_texts, y_labels)  # DummyClassifier ignores X content
        return self

    def predict(self, X_texts: list[str]) -> np.ndarray:  # [N] str labels
        return self.clf.predict(X_texts)


class InstructionPrefixClassifier:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)  # frozen, no grad
        self.clf = LogisticRegression(
            multi_class="multinomial", solver="lbfgs",
            class_weight="balanced", max_iter=1000, random_state=42,
        )

    def encode(self, texts: list[str]) -> np.ndarray:
        # texts: N strings -> embeddings [N, 384]
        return self.encoder.encode(texts, convert_to_numpy=True)

    def fit(self, X_texts: list[str], y_labels: list[str]) -> "InstructionPrefixClassifier":
        emb = self.encode(X_texts)  # [N, 384]
        self.clf.fit(emb, y_labels)
        return self

    def predict(self, X_texts: list[str]) -> np.ndarray:  # [N] str labels
        emb = self.encode(X_texts)  # [N, 384]
        return self.clf.predict(emb)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| texts | [N] | list of instruction prefix strings |
| emb | [N, 384] | MiniLM sentence embeddings, frozen |
| y_labels | [N] | task family string labels |
| predict() output | [N] | predicted family labels |

### Subtasks [2/2 used - combined A-2+A-3 into budget]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | baseline | `BaselineClassifier` wrapping `DummyClassifier` |
| L-A3-1 | proposed | `InstructionPrefixClassifier` encode+fit+predict |

---

## A-4/A-5: Evaluation + Gate Check [Complexity: 8+4, Budget: 12]

**Applied**: sklearn `f1_score(average='macro')` + `classification_report(output_dict=True)`

### API Signatures

```python
from sklearn.metrics import f1_score, accuracy_score, classification_report

def compute_metrics(y_true: list[str], y_pred: list[str]) -> dict:
    """Returns {macro_f1: float, accuracy: float, report: dict}."""
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "accuracy": accuracy_score(y_true, y_pred),
        "report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }

def verify_mechanism(
    model: "InstructionPrefixClassifier", X_sample: list[str], y_sample: list[str]
) -> bool:
    """Assert emb.shape == (N,384), clf fitted (has classes_), preds in known labels."""
    emb = model.encode(X_sample)
    assert emb.shape == (len(X_sample), 384)
    assert hasattr(model.clf, "classes_")
    preds = model.predict(X_sample)
    assert set(preds).issubset(set(model.clf.classes_))
    return True

def gate_check(proposed_f1: float, baseline_f1: float, threshold: float = 0.75) -> dict:
    """Returns {pass: bool, proposed_f1, baseline_f1, threshold, reasons: list[str]}."""
    passed = proposed_f1 >= threshold and proposed_f1 > baseline_f1
    reasons = []
    if proposed_f1 < threshold:
        reasons.append(f"macro_f1 {proposed_f1:.3f} < threshold {threshold}")
    if proposed_f1 <= baseline_f1:
        reasons.append(f"proposed {proposed_f1:.3f} not > baseline {baseline_f1:.3f}")
    return {"pass": passed, "proposed_f1": proposed_f1, "baseline_f1": baseline_f1,
            "threshold": threshold, "reasons": reasons}
```

### Subtasks [2/2 used - combined A-4+A-5]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | metrics | `compute_metrics` macro-F1/accuracy/report |
| L-A5-1 | gate | `verify_mechanism` + `gate_check` |

---

## A-6/A-7: Visualization + Pipeline [Complexity: 8+7, Budget: 15 — deferred, boilerplate]

**Applied**: standard matplotlib bar/heatmap, sklearn TSNE

### API Signatures

```python
def plot_gate_metrics(baseline_f1: float, proposed_f1: float, threshold: float, out_dir: str) -> None: ...
def plot_confusion_matrix(y_true: list[str], y_pred: list[str], labels: list[str], out_dir: str) -> None: ...
def plot_tsne_embeddings(embeddings: np.ndarray, labels: list[str], out_dir: str) -> None:
    # embeddings: [N, 384] -> TSNE -> [N, 2] scatter
    ...
def plot_per_family_f1(report: dict, out_dir: str) -> None: ...

def main() -> None:
    """load -> split -> fit baseline+proposed -> evaluate -> verify -> visualize -> write 04_validation.md"""
    ...
```

No subtasks allocated (budget exhausted at A-1/A-2/A-3/A-4/A-5 = 3 allocated subtask groups; A-6/A-7 use signatures above directly in Phase 4 without further breakdown).

---

## Subtask Budget Summary [3/3 groups used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1 | Data pipeline | load/select/extract/build/split (A-1) |
| L-2 | Models | BaselineClassifier + InstructionPrefixClassifier (A-2, A-3) |
| L-3 | Eval + gate | compute_metrics, verify_mechanism, gate_check (A-4, A-5) |
