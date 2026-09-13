# Logic: H-E1 — Spurious Direction Recovery via K-Means Clustering

**Hypothesis**: H-E1 (EXISTENCE / PoC)
**Phase**: 3 — API Design

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-2: Model + ERM Training [Complexity: 12, Budget: 2]

**Applied**: Standard PyTorch Model API

### API Signatures

```python
# models/resnet.py
import torch
import torch.nn as nn
from torch import Tensor
import torchvision.models as tv_models

class ERMModel(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        """ResNet-50 wrapper with penultimate-layer access."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """x: (B, 3, 224, 224) -> logits: (B, num_classes)"""
        ...

    def get_feature_extractor(self) -> nn.Sequential:
        """Returns Sequential(*list(self.backbone.children())[:-1]).
        Output: (B, 2048, 1, 1) -> caller must squeeze to (B, 2048)."""
        ...


def get_model(num_classes: int, pretrained: bool = True) -> ERMModel:
    """Instantiate ERMModel."""
    ...


def save_checkpoint(model: ERMModel, optimizer: "Optimizer",
                    epoch: int, path: str) -> None:
    """Save state_dict + optimizer state + epoch to path."""
    ...


def load_checkpoint(model: ERMModel, path: str,
                    device: torch.device) -> int:
    """Load checkpoint from path into model. Returns epoch number."""
    ...
```

```python
# train.py
from typing import Dict
import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from models.resnet import ERMModel

def train_epoch(
    model: ERMModel,
    optimizer: Optimizer,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Dict[str, float]:
    """Train one epoch. Returns {"loss": float, "acc": float}."""
    ...


def save_checkpoint(model: ERMModel, optimizer: Optimizer,
                    epoch: int, path: str) -> None:
    """Persist model + optimizer state."""
    ...


def load_checkpoint(model: ERMModel, path: str,
                    device: torch.device) -> int:
    """Load checkpoint. Returns epoch number."""
    ...


def train(
    config_path: str,
    dataset_name: str,
    output_dir: str,
    stop_after_epoch: int = 5
) -> str:
    """Run ERM training. Returns path to epoch-5 checkpoint."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (input) | (B, 3, 224, 224) | float32, ImageNet-normalized |
| backbone output | (B, 2048, 1, 1) | after AdaptiveAvgPool2d |
| logits | (B, num_classes) | float32 |

### Pseudo-code

```
train():
  model = ERMModel(num_classes, pretrained=True)
  optimizer = SGD(model.parameters(), lr=1e-3, momentum=0.9, weight_decay=wd)
  for epoch in 1..stop_after_epoch:
    loss, acc = train_epoch(model, optimizer, loader, CrossEntropy, device)
    save_checkpoint(model, optimizer, epoch, f"{output_dir}/epoch_{epoch}.pt")
    print(f"Epoch {epoch}: loss={loss:.4f}, acc={acc:.4f}")
  return f"{output_dir}/epoch_{stop_after_epoch}.pt"

train_epoch():
  model.train()
  for x, y, g in dataloader:
    logits = model(x.to(device))
    loss = criterion(logits, y.to(device))
    optimizer.zero_grad(); loss.backward(); optimizer.step()
  return {"loss": avg_loss, "acc": avg_acc}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ERMModel class | `__init__`, `forward`, `get_feature_extractor` in models/resnet.py |
| L-2-2 | Training loop | `train_epoch`, `train`, `save/load_checkpoint` with epoch-5 early-stop |

---

## A-3: Embedding Extraction [Complexity: 9, Budget: 1]

**Applied**: Standard PyTorch Model API

### API Signatures

```python
# extract.py
import numpy as np
import torch
from torch.utils.data import DataLoader
from typing import Tuple, Dict
from models.resnet import ERMModel

def extract_embeddings(
    model: ERMModel,
    dataloader: DataLoader,
    device: torch.device
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Batch inference on penultimate layer.
    Returns: embeddings (N, 2048) float32,
             labels (N,) int64,
             group_ids (N,) int64.
    Asserts embeddings.shape[1] == 2048."""
    ...


def run_extraction(
    ckpt_path: str,
    dataset_name: str,
    data_dir: str,
    output_dir: str,
    batch_size: int = 256
) -> Dict[str, str]:
    """Load checkpoint, extract embeddings, save .npy files.
    Returns: {"embeddings": path, "labels": path, "group_ids": path}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | (B, 3, 224, 224) | float32 |
| feat (per batch) | (B, 2048) | after squeeze(-1).squeeze(-1) |
| embeddings | (N, 2048) | float32 np.ndarray, asserted |
| labels | (N,) | int64 np.ndarray |
| group_ids | (N,) | int64 np.ndarray, values in {0,1,2,3} |

### Pseudo-code

```
extract_embeddings(model, dataloader, device):
  feature_extractor = model.get_feature_extractor()
  feature_extractor.eval()
  embs, labs, grps = [], [], []
  with torch.no_grad():
    for x, y, g in dataloader:
      feat = feature_extractor(x.to(device))  # (B, 2048, 1, 1)
      feat = feat.squeeze(-1).squeeze(-1)       # (B, 2048)
      embs.append(feat.cpu().numpy())
      labs.append(y.numpy()); grps.append(g.numpy())
  embeddings = np.concatenate(embs)             # (N, 2048)
  assert embeddings.shape[1] == 2048, f"Wrong dim: {embeddings.shape[1]}"
  return embeddings, np.concatenate(labs), np.concatenate(grps)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | extract_embeddings | Batched penultimate-layer extraction + .npy save |

---

## A-4: K-Means Clustering Probe [Complexity: 11, Budget: 2]

**Applied**: Standard PyTorch Model API

### API Signatures

```python
# cluster.py
import numpy as np
from typing import Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score

def run_kmeans_probe(
    embeddings: np.ndarray,   # (N, 2048) float32
    group_ids: np.ndarray,    # (N,) int64 — 4-class group labels {0,1,2,3}
    k: int = 2,
    n_init: int = 10,
    seed: int = 42
) -> Tuple[float, float, np.ndarray]:
    """Run k-means, compute AMI and worst-cluster purity.
    Returns: (ami: float, worst_purity: float, cluster_assignments: (N,) int32)."""
    ...


def worst_cluster_purity(
    group_ids: np.ndarray,          # (N,) int64
    cluster_assignments: np.ndarray, # (N,) int32
    k: int
) -> float:
    """Min purity across all clusters. Returns scalar in [0, 1]."""
    ...


def compute_random_baseline(
    group_ids: np.ndarray,  # (N,) int64
    k: int,
    seed: int = 0
) -> Tuple[float, float]:
    """Random cluster assignment baseline.
    Returns: (ami_random: float, purity_random: float)."""
    ...


def verify_mechanism_activated(
    embeddings: np.ndarray,          # (N, 2048) float32
    cluster_assignments: np.ndarray,  # (N,) int32
    group_ids: np.ndarray,           # (N,) int64
    k: int = 2
) -> Tuple[bool, Dict[str, bool]]:
    """Check mechanism activation indicators.
    Returns: (all_passed: bool, indicators: dict).
    indicators keys: embedding_shape_correct, clusters_non_trivial,
                     ami_above_chance, ami_passes_threshold."""
    ...


def probe(
    embeddings_path: str,
    group_ids_path: str,
    k: int = 2
) -> Dict[str, float]:
    """Integration entry point for evaluate.py.
    Returns: {"ami": float, "worst_purity": float,
              "ami_random": float, "purity_random": float,
              "mechanism_ok": bool}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | (N, 2048) | float32 np.ndarray |
| cluster_assignments | (N,) | int32 np.ndarray, values in {0,..,k-1} |
| group_ids | (N,) | int64 np.ndarray, values in {0,1,2,3} |
| ami | scalar | float in [-1, 1], expected >= 0.5 |
| worst_purity | scalar | float in [0, 1], expected >= 0.75 |

### Pseudo-code

```
run_kmeans_probe(embeddings, group_ids, k, n_init, seed):
  kmeans = KMeans(n_clusters=k, n_init=n_init, random_state=seed)
  cluster_assignments = kmeans.fit_predict(embeddings)      # (N,)
  ami = adjusted_mutual_info_score(group_ids, cluster_assignments)
  wp = worst_cluster_purity(group_ids, cluster_assignments, k)
  return ami, wp, cluster_assignments

worst_cluster_purity(group_ids, cluster_assignments, k):
  purities = []
  for c in range(k):
    mask = cluster_assignments == c
    if mask.sum() == 0: continue
    counts = np.bincount(group_ids[mask])
    purities.append(counts.max() / mask.sum())
  return min(purities)

verify_mechanism_activated(embeddings, cluster_assignments, group_ids, k):
  ami_actual = adjusted_mutual_info_score(group_ids, cluster_assignments)
  ami_random = adjusted_mutual_info_score(
      group_ids, np.random.randint(0, k, size=len(group_ids)))
  indicators = {
    "embedding_shape_correct": embeddings.shape[1] == 2048,
    "clusters_non_trivial": all((cluster_assignments==c).sum()>10 for c in range(k)),
    "ami_above_chance": ami_actual > ami_random + 0.1,
    "ami_passes_threshold": ami_actual >= 0.5,
  }
  return all(indicators.values()), indicators
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_kmeans_probe + worst_cluster_purity + compute_random_baseline | Core AMI/purity computation |
| L-4-2 | verify_mechanism_activated + probe | Gate check assertions + integration entry point |

---

## Summary: All Subtasks [5/5 used]

| ID | Task | Subtask | File |
|----|------|---------|------|
| L-2-1 | A-2 | ERMModel class + get_feature_extractor | models/resnet.py |
| L-2-2 | A-2 | train_epoch + train + checkpoint funcs | train.py |
| L-3-1 | A-3 | extract_embeddings + run_extraction | extract.py |
| L-4-1 | A-4 | run_kmeans_probe + worst_cluster_purity + random_baseline | cluster.py |
| L-4-2 | A-4 | verify_mechanism_activated + probe | cluster.py |
