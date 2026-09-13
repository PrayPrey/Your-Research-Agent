# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Linear probe on frozen MiniLM embeddings predicts oracle adapter (Top-1 ≥70% OR Top-3 ≥85%)

Applied: MiniLM + LogisticRegression linear-probe pattern (sentence-transformers/all-MiniLM-L6-v2 → sklearn LogisticRegression, canonical probing pipeline)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base_hypothesis_folder referenced (H-E0 provides conceptual continuity only, no reusable code artifact).

---

## File Organization

```
h-e1/code/
  config.py       # fixed experiment config
  data.py         # dataset load, oracle labeling, split
  model.py        # AdapterSelectionProbe (encoder + LogisticRegression)
  evaluate.py      # baselines, metrics, figures
  train.py         # orchestration entrypoint
```

## Module Interfaces

### config.py

```python
@dataclass
class Config:
    dataset_name: str = "Open-Orca/FLAN"
    encoder_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    base_model_name: str = "meta-llama/Llama-2-7b-hf"
    adapter_ids: list[str] = field(default_factory=lambda: [...])  # 9 FLAN-family LoRAs
    n_samples: int = 3000          # 2K-5K range
    prefix_chars: int = 256
    train_val_test_split: tuple = (0.70, 0.15, 0.15)
    random_state: int = 42
    max_iter: int = 2000
    solver: str = "lbfgs"
    top_k: int = 3
```

### data.py

**Dependencies**: config.py

```python
def stream_instructions(cfg: Config) -> list[dict]: ...
def extract_prefix(text: str, max_chars: int) -> str: ...
def compute_oracle_labels(samples: list[dict], base_model, adapters: dict, cfg: Config) -> list[int]: ...
def stratified_split(samples: list[dict], labels: list[int], cfg: Config) -> dict: ...  # {train,val,test}
```

### model.py

**Dependencies**: config.py, sentence-transformers, sklearn

```python
class AdapterSelectionProbe:
    def __init__(self, encoder_name: str, num_adapters: int, max_iter: int, solver: str, random_state: int): ...
    def encode(self, texts: list[str]) -> np.ndarray: ...          # (N, 384)
    def fit(self, texts: list[str], adapter_labels: list[int]) -> None: ...
    def predict_proba(self, texts: list[str]) -> np.ndarray: ...   # (N, k)
    def evaluate(self, texts: list[str], adapter_labels: list[int]) -> dict: ...  # top1/top3 acc
```

### evaluate.py

**Dependencies**: model.py, sklearn.metrics, matplotlib

```python
def random_baseline(labels: list[int], num_adapters: int, random_state: int) -> float: ...
def majority_baseline(train_labels: list[int], test_labels: list[int]) -> float: ...
def oracle_task_family_agreement(oracle_labels: list[int], task_family_labels: list[int]) -> float: ...
def plot_gate_metrics(top1: float, top3: float, out_path: str) -> None: ...
def plot_confusion_matrix(y_true, y_pred, out_path: str) -> None: ...
def plot_per_adapter_accuracy(y_true, y_pred, out_path: str) -> None: ...
def plot_embedding_tsne(embeddings: np.ndarray, labels: list[int], out_path: str) -> None: ...
```

### train.py

**Dependencies**: config.py, data.py, model.py, evaluate.py

```python
def main() -> None: ...  # load data -> label oracle -> split -> fit probe -> baselines -> evaluate -> figures -> gate check
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Stream Open-Orca/FLAN, sample 2K-5K, extract prefixes | 8 | 2+2+2+2 |
| A-2 | Oracle labeling | Load 9 LoRA adapters, compute per-sample argmin loss | 12 | 3+4+3+2 |
| A-3 | Stratified split | 70/15/15 split by oracle adapter label | 5 | 1+1+1+2 |
| A-4 | Linear probe model | MiniLM encode + LogisticRegression fit/predict | 6 | 2+2+1+1 |
| A-5 | Baselines | Random selection + majority class baselines | 4 | 1+1+1+1 |
| A-6 | Evaluation metrics | Top-1/Top-3 accuracy, confusion matrix, oracle-vs-family agreement | 7 | 2+2+2+1 |
| A-7 | Visualization | Gate bar chart, per-adapter breakdown, t-SNE plot | 6 | 2+1+1+2 |
| A-8 | Orchestration + gate check | train.py wiring, PASS/FAIL gate report | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2], Low(4-8): [A-3, A-4, A-5, A-6, A-7, A-8]
