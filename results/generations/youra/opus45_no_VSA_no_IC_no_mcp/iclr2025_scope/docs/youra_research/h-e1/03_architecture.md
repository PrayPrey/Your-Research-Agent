# H-E1 Architecture: Task-Correlated Structure in BERT Hidden States

**Type**: EXISTENCE (PoC) — analysis only, no training
**Applied**: KB pattern — embedding-extraction + clustering-eval PoC (encoder frozen, sklearn eval)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## Data Flow

```
SuperGLUE val split (HF datasets)
  -> tokenize (BertTokenizer)
  -> BERT-base-uncased forward pass (frozen)
  -> extract [CLS] hidden state, last layer  -> (N, 768) matrix + task labels
  -> KMeans(K=8) on (N, 768)                 -> cluster assignments (N,)
  -> metrics: purity, ARI, NMI (vs task labels)
  -> viz: bar chart (per-cluster task composition), t-SNE scatter (colored by task)
```

---

## Module Structure

- `h-e1/code/extract.py` — data load + BERT forward + [CLS] extraction
- `h-e1/code/cluster.py` — KMeans + metrics
- `h-e1/code/visualize.py` — bar chart + t-SNE
- `h-e1/code/config.py` — fixed constants
- `h-e1/code/run.py` — orchestration entrypoint

---

## Interfaces

### `config.py`

```python
MODEL_NAME: str = "bert-base-uncased"
SUPERGLUE_TASKS: list[str] = ["boolq", "cb", "copa", "wic", "wsc"]  # tasks with labeled val split
MAX_SAMPLES_PER_TASK: int = 200
MAX_SEQ_LEN: int = 128
N_CLUSTERS: int = 8
RANDOM_SEED: int = 42
OUTPUT_DIR: str = "h-e1/results/"
```

### `extract.py` (`h-e1/code/extract.py`)

**Dependencies**: transformers, datasets, torch, config

```python
def load_superglue_samples(task: str, max_samples: int) -> list[dict]: ...
def extract_cls_embeddings(texts: list[str], model, tokenizer, device) -> np.ndarray: ...
def build_dataset() -> tuple[np.ndarray, np.ndarray]:
    """Returns (embeddings [N,768], task_labels [N])"""
```

### `cluster.py` (`h-e1/code/cluster.py`)

**Dependencies**: sklearn, numpy

```python
def run_kmeans(embeddings: np.ndarray, k: int, seed: int) -> np.ndarray:
    """Returns cluster_ids [N]"""

def cluster_purity(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float: ...
def compute_ari(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float: ...
def compute_nmi(cluster_ids: np.ndarray, task_labels: np.ndarray) -> float: ...
def evaluate(cluster_ids: np.ndarray, task_labels: np.ndarray) -> dict:
    """Returns {"purity": float, "ari": float, "nmi": float}"""
```

### `visualize.py` (`h-e1/code/visualize.py`)

**Dependencies**: matplotlib, sklearn.manifold.TSNE

```python
def plot_cluster_task_bar(cluster_ids: np.ndarray, task_labels: np.ndarray, out_path: str) -> None: ...
def plot_tsne(embeddings: np.ndarray, task_labels: np.ndarray, out_path: str) -> None: ...
```

### `run.py` (`h-e1/code/run.py`)

**Dependencies**: extract, cluster, visualize, config

```python
def main() -> None:
    """build_dataset -> run_kmeans -> evaluate -> save metrics.json -> plot bar + tsne"""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config setup | Fixed constants (model, tasks, K, seed) | 4 | 1+1+1+1 |
| A-2 | SuperGLUE loader | Load val splits, sample per task, cap N | 8 | 2+2+2+2 |
| A-3 | BERT CLS extraction | Forward pass, extract last-layer [CLS] | 8 | 2+3+2+1 |
| A-4 | KMeans clustering | Fit K=8 on embeddings | 5 | 1+2+1+1 |
| A-5 | Cluster metrics | Purity, ARI, NMI vs task labels | 7 | 2+2+2+1 |
| A-6 | Bar chart viz | Per-cluster task composition plot | 5 | 1+1+2+1 |
| A-7 | t-SNE viz | 2D projection colored by task | 6 | 2+2+1+1 |
| A-8 | Run orchestration | Wire modules, save metrics.json + figures | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8]

---

## Dependencies

`transformers`, `datasets`, `torch`, `scikit-learn`, `matplotlib`, `numpy` — all standard, no new/exotic packages.

skipped: no train/eval split logic, no checkpointing, no config file format (YAML/JSON) — add if scaling beyond PoC.
