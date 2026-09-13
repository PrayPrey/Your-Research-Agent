# Logic Design: H-M1

**Hypothesis:** Task embeddings learned from clustered hidden states encode functional specialization patterns.
**Type:** MECHANISM | **Gate:** MUST_WORK (probe accuracy > 0.125)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No base_hypothesis code folder or existing src/ found for H-M1 in this project tree (only unrelated archived runs from a different topic). Designing new APIs from PRD/experiment brief.
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

**Input dependency (data, not code):** H-E1 cluster assignments consumed as a serialized array (e.g., `cluster_assignments.npy`), not via API call. No Serena verification required for this data-only dependency.

---

## A-1: TaskEmbeddingEncoder + Training [Complexity: 3, Budget: 3]

**Applied:** Standard PyTorch (nn.Linear projection + mean pooling), InfoNCE contrastive loss

### API Signatures

```python
import torch
from torch import Tensor
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class TaskEmbeddingEncoder(nn.Module):
    def __init__(self, hidden_dim: int, embedding_dim: int, num_tasks: int = 8):
        """Projects pooled hidden states into task embedding space."""
        super().__init__()
        self.projection = nn.Linear(hidden_dim, embedding_dim)

    def forward(self, hidden_states: Tensor, cluster_assignments: Optional[Tensor] = None) -> Tensor:
        """hidden_states: [B, seq, hidden_dim] -> pooled embeddings [B, embedding_dim].
        cluster_assignments unused in forward (reserved for label lookup in training loop)."""
        projected = self.projection(hidden_states)     # [B, seq, emb_dim]
        mask_pool = projected.mean(dim=1)               # [B, emb_dim]  (mean pooling over seq)
        return mask_pool


class LinearProbe(nn.Module):
    def __init__(self, embedding_dim: int, num_tasks: int):
        """Frozen-embedding linear classifier for probe evaluation (torch variant, optional)."""
        super().__init__()
        self.classifier = nn.Linear(embedding_dim, num_tasks)

    def forward(self, embeddings: Tensor) -> Tensor:
        """embeddings: [B, embedding_dim] -> logits [B, num_tasks]"""
        return self.classifier(embeddings)


def info_nce_loss(embeddings: Tensor, cluster_labels: Tensor, temperature: float = 0.1) -> Tensor:
    """embeddings: [B, emb_dim], cluster_labels: [B] (int64, values in [0, num_tasks)).
    Positives = same cluster label in batch. Returns scalar loss."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [B, seq, hidden_dim] | Mamba-370m last hidden layer |
| cluster_assignments | [B] | int64 labels from H-E1 (0..7) |
| embeddings | [B, embedding_dim] | embedding_dim in {16, 32, 64} |
| sim_matrix | [B, B] | cosine sim for InfoNCE |

### Pseudo-code (InfoNCE on cluster labels)

```
1. embeddings = encoder(hidden_states)                       # [B, D]
2. embeddings = F.normalize(embeddings, dim=-1)               # [B, D]
3. sim_matrix = embeddings @ embeddings.T / temperature        # [B, B]
4. sim_matrix.fill_diagonal_(-inf)                             # exclude self
5. pos_mask[i,j] = (cluster_labels[i] == cluster_labels[j]) and i != j   # [B, B] bool
6. edge case: if a sample has no positive in batch (mask row all False) -> skip that row from loss (mean over valid rows only)
7. log_prob = log_softmax(sim_matrix, dim=1)                   # [B, B]
8. loss_i = -(log_prob[i] * pos_mask[i]).sum() / pos_mask[i].sum().clamp(min=1)
9. loss = mean(loss_i over valid rows)
```

### Training Loop Pseudo-code

```python
def train_encoder(
    encoder: TaskEmbeddingEncoder,
    hidden_states: Tensor,          # [N, seq, hidden_dim] full dataset, precomputed
    cluster_labels: Tensor,         # [N] int64
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 1e-4,
) -> TaskEmbeddingEncoder:
    optimizer = torch.optim.AdamW(encoder.parameters(), lr=lr)
    n = hidden_states.shape[0]
    for epoch in range(epochs):
        perm = torch.randperm(n)
        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            batch_h, batch_labels = hidden_states[idx], cluster_labels[idx]
            if batch_h.shape[0] < 2:
                continue  # edge case: skip batches too small for contrastive pairs
            emb = encoder(batch_h)
            loss = info_nce_loss(emb, batch_labels)
            optimizer.zero_grad(); loss.backward(); optimizer.step()
    return encoder
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | TaskEmbeddingEncoder | Projection + mean pooling module |
| L-1-2 | info_nce_loss | Cluster-label contrastive loss with empty-positive-mask guard |
| L-1-3 | train_encoder | Minibatch training loop, AdamW, small-batch guard |

---

## A-2: Linear Probe Evaluation [Complexity: 2, Budget: 2]

**Applied:** sklearn LogisticRegression standard linear probe pattern

### API Signatures

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

def extract_embeddings(
    encoder: TaskEmbeddingEncoder,
    hidden_states: Tensor,   # [N, seq, hidden_dim]
) -> np.ndarray:
    """Frozen-encoder inference. Returns [N, embedding_dim] numpy array."""
    encoder.eval()
    with torch.no_grad():
        emb = encoder(hidden_states)   # [N, emb_dim]
    return emb.cpu().numpy()


def evaluate_linear_probe(
    train_embeddings: np.ndarray,   # [N_train, emb_dim]
    train_labels: np.ndarray,       # [N_train]
    test_embeddings: np.ndarray,    # [N_test, emb_dim]
    test_labels: np.ndarray,        # [N_test]
    num_tasks: int = 8,
    C: float = 1.0,
    max_iter: int = 1000,
    seed: int = 42,
) -> dict:
    """Returns {"accuracy": float, "per_task_accuracy": dict, "report": str}."""
    probe = LogisticRegression(C=C, max_iter=max_iter, random_state=seed)
    probe.fit(train_embeddings, train_labels)
    preds = probe.predict(test_embeddings)
    accuracy = accuracy_score(test_labels, preds)
    report = classification_report(test_labels, preds, output_dict=True, zero_division=0)
    per_task_accuracy = {
        str(cls): report[str(cls)]["recall"]
        for cls in np.unique(test_labels)
        if str(cls) in report
    }
    return {"accuracy": accuracy, "per_task_accuracy": per_task_accuracy, "report": report}


def random_baseline_embeddings(num_tasks: int, embedding_dim: int, seed: int = 42) -> np.ndarray:
    """Baseline: fixed random embedding per task, frozen. Returns [num_tasks, embedding_dim]."""
    g = torch.Generator().manual_seed(seed)
    return torch.randn(num_tasks, embedding_dim, generator=g).numpy()
```

### Edge Cases

- Class present in test but absent in train (e.g., WSC with only 104 samples split unevenly): `zero_division=0` prevents crash; missing class excluded from `per_task_accuracy`.
- `train_test_split` must be stratified by `cluster_labels` to avoid empty classes; use `sklearn.model_selection.train_test_split(..., stratify=labels)`.
- If a task has < 2 samples after split, drop from probe training and log warning (do not crash pipeline).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | extract_embeddings + evaluate_linear_probe | Frozen inference + sklearn probe fit/eval with class-imbalance guards |
| L-2-2 | random_baseline_embeddings | Fixed-seed random baseline for gate comparison |

---

## A-3: Ablation - Embedding Dimension Sweep [Complexity: 1, Budget: 1]

**Applied:** Standard PyTorch loop over hyperparameter grid

### API Signatures

```python
def run_dimension_ablation(
    hidden_states_train: Tensor,
    cluster_labels_train: Tensor,
    hidden_states_test: Tensor,
    cluster_labels_test: Tensor,
    hidden_dim: int,
    dims: list = [16, 32, 64],
) -> dict:
    """Returns {dim: {"accuracy": float, ...}} for each embedding_dim in dims."""
    results = {}
    for dim in dims:
        encoder = TaskEmbeddingEncoder(hidden_dim, dim)
        encoder = train_encoder(encoder, hidden_states_train, cluster_labels_train)
        train_emb = extract_embeddings(encoder, hidden_states_train)
        test_emb = extract_embeddings(encoder, hidden_states_test)
        results[dim] = evaluate_linear_probe(
            train_emb, cluster_labels_train.numpy(), test_emb, cluster_labels_test.numpy()
        )
    return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | run_dimension_ablation | Sweep embedding_dim in {16,32,64}, reuse train/eval APIs |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied lines only, no KB search logs
- [x] Docstrings <= 2 lines
- [x] Tensor shapes annotated in comments/tables
- [x] Subtask count within allocated budget (3+2+1=6)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included (green-field, skip justified)
