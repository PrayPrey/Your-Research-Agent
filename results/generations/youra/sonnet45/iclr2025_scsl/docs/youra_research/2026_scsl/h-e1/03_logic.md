# Logic Specification: h-e1 — Clusterability Diagnostic

**Date:** 2026-03-19
**Author:** Phase 3 Logic Design
**Hypothesis:** h-e1 (EXISTENCE)
**Applied:** PyTorch SSL training pattern, SimCLR architecture pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Archived implementation found with Waterbirds

Dataset infrastructure
**Analyzed Path:** `docs/youra_research/20260318_scsl/_archive/*/h-e1/`
**Findings:** Reusable data loader pattern confirmed. Previous implementation exists but different hypothesis scope.

---

## Module Logic - Essential APIs Only

### Data Module
```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform=None): ...
    def __getitem__(self, idx: int) -> Tuple[Tensor, int, int]: ...
    # Returns: (image[3,224,224], label, group)

def get_ssl_transforms() -> Tuple[Callable, Callable]: ...
def get_eval_transforms() -> Callable: ...
```

### SimCLR Model
```python
class SimCLR(nn.Module):
    def __init__(self, encoder_name='resnet50', projection_dim=128, pretrained=False): ...
    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]: ...
    # Returns: (h[B,2048], z[B,128])

def nt_xent_loss(z_i: Tensor, z_j: Tensor, temperature=0.5) -> Tensor: ...
```

### Linear Probe
```python
class LinearProbe(nn.Module):
    def __init__(self, input_dim=2048, num_classes=2): ...
    def forward(self, x: Tensor) -> Tensor: ...

def cluster_balanced_loss(logits, targets, cluster_ids, cluster_weights) -> Tensor: ...
def compute_cluster_weights(cluster_labels: Tensor, num_clusters=4) -> Tensor: ...
```

### Metrics
```python
def compute_ami(embeddings: ndarray, groups: ndarray) -> Tuple[float, ndarray]: ...
def compute_wga(preds, labels, groups) -> Tuple[float, Dict]: ...
def compute_linear_auroc(embeddings, groups) -> float: ...
```

---

## Tensor Shapes

| Operation | Input | Output |
|-----------|-------|--------|
| SimCLR.encoder | [B,3,224,224] | [B,2048] |
| SimCLR.projector | [B,2048] | [B,128] |
| nt_xent_loss | z_i[B,128], z_j[B,128] | scalar |
| KMeans | [N,2048] | [N] cluster_labels |
| LinearProbe | [B,2048] | [B,2] |

---

**Subtasks:** 6 (A-2: 4 subtasks, A-4: 2 subtasks)
**Status:** Complete
