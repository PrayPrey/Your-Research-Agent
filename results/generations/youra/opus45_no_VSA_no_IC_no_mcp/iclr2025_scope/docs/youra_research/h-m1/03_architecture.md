# Architecture: H-M1 (MECHANISM)

**Applied**: Linear probing pattern (frozen embeddings + LogisticRegression), InfoNCE contrastive loss on cluster labels

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base_hypothesis folder or existing src/ found

---

## Module Structure

- `h-m1/code/data/extract_hidden_states.py` - Mamba hidden state extraction
- `h-m1/code/data/dataset.py` - SuperGLUE loading + cluster label attach
- `h-m1/code/models/task_embedding.py` - TaskEmbeddingEncoder (proposed)
- `h-m1/code/models/baseline.py` - RandomEmbeddingBaseline
- `h-m1/code/losses/infonce.py` - InfoNCE contrastive loss
- `h-m1/code/train.py` - Embedding training loop
- `h-m1/code/probe.py` - Linear probe (LogisticRegression wrapper)
- `h-m1/code/evaluate.py` - Gate metric + secondary metrics
- `h-m1/code/config.py` - Config dataclass (embedding_dim ablation)
- `h-m1/code/visualize.py` - Figures (bar chart, t-SNE, ablation plot)
- `h-m1/code/main.py` - Orchestration entrypoint

---

## Module Interfaces

### HiddenStateExtractor (`data/extract_hidden_states.py`)

**Dependencies**: mamba-ssm, transformers

```python
class HiddenStateExtractor:
    def __init__(self, model_name: str = "state-spaces/mamba-370m"): ...
    def extract(self, texts: list[str]) -> Tensor: ...  # [N, seq, hidden_dim]
```

### SuperGLUEDataset (`data/dataset.py`)

**Dependencies**: datasets (HF), H-E1 cluster assignments (external artifact)

```python
TASKS = ["boolq", "cb", "copa", "rte", "wic", "wsc"]

def load_superglue_splits(tasks: list[str] = TASKS) -> dict: ...
def attach_cluster_labels(hidden_states: Tensor, cluster_path: str) -> Tensor: ...  # [N] int labels
def make_task_labels(dataset_meta: list[str]) -> Tensor: ...  # [N] task id for probe eval
```

### TaskEmbeddingEncoder (`models/task_embedding.py`)

**Dependencies**: torch.nn

```python
class TaskEmbeddingEncoder(nn.Module):
    def __init__(self, hidden_dim: int, embedding_dim: int, num_tasks: int = 8): ...
    def forward(self, hidden_states: Tensor) -> Tensor: ...  # [B, seq, H] -> [B, emb_dim]
```

### RandomEmbeddingBaseline (`models/baseline.py`)

**Dependencies**: torch

```python
class RandomEmbeddingBaseline(nn.Module):
    def __init__(self, embedding_dim: int, num_tasks: int = 8, seed: int = 42): ...
    def forward(self, hidden_states: Tensor) -> Tensor: ...  # ignores input, returns frozen random emb
```

### InfoNCELoss (`losses/infonce.py`)

**Dependencies**: torch

```python
class InfoNCELoss(nn.Module):
    def __init__(self, temperature: float = 0.1): ...
    def forward(self, embeddings: Tensor, cluster_labels: Tensor) -> Tensor: ...  # scalar loss
```

### Trainer (`train.py`)

**Dependencies**: TaskEmbeddingEncoder, InfoNCELoss, torch.optim.AdamW

```python
def train_embedding(
    model: TaskEmbeddingEncoder,
    hidden_states: Tensor,
    cluster_labels: Tensor,
    lr: float = 1e-4,
    batch_size: int = 32,
    epochs: int = 10,
) -> TaskEmbeddingEncoder: ...
```

### LinearProbe (`probe.py`)

**Dependencies**: sklearn.linear_model.LogisticRegression

```python
def fit_probe(train_emb: np.ndarray, train_labels: np.ndarray, C: float = 1.0) -> LogisticRegression: ...
def probe_accuracy(probe: LogisticRegression, test_emb: np.ndarray, test_labels: np.ndarray) -> float: ...
```

### Evaluator (`evaluate.py`)

**Dependencies**: LinearProbe, sklearn.metrics

```python
def run_gate_check(probe_acc: float, threshold: float = 0.125) -> bool: ...
def per_task_accuracy(probe, embeddings, labels, task_ids) -> dict: ...
def silhouette(embeddings: np.ndarray, labels: np.ndarray) -> float: ...
```

### Config (`config.py`)

```python
@dataclass
class Config:
    model_name: str = "state-spaces/mamba-370m"
    hidden_dim: int = 1024
    embedding_dim: int = 32  # ablation: {16, 32, 64}
    num_tasks: int = 8
    lr: float = 1e-4
    batch_size: int = 32
    epochs: int = 10
    seed: int = 42
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, sklearn.manifold.TSNE

```python
def plot_gate_comparison(proposed_acc: float, random_acc: float, out_path: str) -> None: ...
def plot_tsne(embeddings: np.ndarray, task_ids: np.ndarray, out_path: str) -> None: ...
def plot_ablation(dim_to_acc: dict[int, float], out_path: str) -> None: ...
```

---

## Data Flow

1. `extract_hidden_states.py` -> hidden states `[N, seq, hidden_dim]` per SuperGLUE sample
2. `dataset.py` attaches H-E1 cluster labels `[N]` + ground-truth task ids `[N]`
3. `train.py`: TaskEmbeddingEncoder + InfoNCELoss trained on (hidden_states, cluster_labels) -> frozen embeddings `[N, emb_dim]`
4. Baseline path: RandomEmbeddingBaseline produces frozen random embeddings (no training)
5. `probe.py`: LogisticRegression fit on frozen embeddings vs task ids (train/val split)
6. `evaluate.py`: gate check (probe_acc > 0.125), per-task acc, silhouette
7. `visualize.py`: gate bar chart (mandatory), t-SNE, per-task bars, ablation plot -> `h-m1/figures/`
8. Ablation loop: repeat steps 3-6 for embedding_dim in {16, 32, 64}

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | SuperGLUE load + hidden state extraction from mamba-370m | 12 | 3+3+3+3 |
| A-2 | Cluster label integration | Load H-E1 cluster assignments, align with hidden states | 8 | 2+2+2+2 |
| A-3 | TaskEmbeddingEncoder | Linear projection + mean pooling module | 6 | 2+1+2+1 |
| A-4 | Random baseline | Frozen random embedding module | 4 | 1+1+1+1 |
| A-5 | InfoNCE loss + training loop | Contrastive training, AdamW, 10 epochs | 13 | 3+3+4+3 |
| A-6 | Linear probe evaluation | LogisticRegression fit/eval, gate check | 8 | 2+2+2+2 |
| A-7 | Secondary metrics | Per-task accuracy, silhouette score | 6 | 2+1+2+1 |
| A-8 | Visualization | Gate chart, t-SNE, per-task bars, ablation plot | 9 | 2+2+3+2 |
| A-9 | Ablation orchestration | Run pipeline across embedding_dim {16,32,64} + random | 10 | 2+3+3+2 |
| A-10 | Main entrypoint + config | Wire pipeline end-to-end, reproducibility (seeds) | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-6, A-9], Low(4-8): [A-3, A-4, A-5(13 borderline-Medium), A-7, A-8, A-10]
