# Logic: H-M1
# Graph Representation as Cross-Architecture Generalization Mechanism

Applied: standard-DL-API-design (no weight-space patterns in Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 incremental extension)
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `EquiSSLEncoder.__init__(node_in_dim, edge_in_dim, hidden_dim, latent_dim, num_layers, symmetry, pool)`
- `EquiSSLEncoder.forward(data: Data) -> Tensor`  # returns L2-normalized (B, latent_dim)
- `EquiSSLObjective.__init__(encoder, decoder, temperature, lam)`
- `EquiSSLObjective.forward(graph_a: Data, graph_b: Data) -> tuple[Tensor, Tensor]`
- `checkpoint_to_graph(state_dict: dict) -> Data`  # node features: [mean, std, l2_norm, max_abs]
- `MultiZooGraphDataset.__init__(root, max_models, normalize, split, val_fraction, seed)`
- `MultiZooGraphDataset.get(idx) -> Data`  # Data.x shape (n_layers, 4), edge_attr (n_edges, 4)
- `ViTZooGraphDataset.__init__(root, max_models, normalize, return_labels, seed)`
- `ViTZooGraphDataset.get(idx) -> Data`  # Data.y = accuracy label tensor
- `load_encoder_from_checkpoint(ckpt_path: str, device: str) -> EquiSSLEncoder`
- `make_positive_pair(graph: Data, scale_alpha_range) -> tuple[Data, Data]`
- `perm_augment(graph: Data) -> Data`  # noise-based augmentation (not true permutation)
- `scale_augment(graph: Data, alpha, alpha_range) -> Data`

**Key API facts from actual code**:
- `Data.x`: node features `[n_nodes, 4]` (mean, std, l2_norm, max_abs per layer)
- `Data.edge_attr`: edge features `[n_edges, 4]`
- `Data.structure`: dict with `n_layers`, `layer_sizes`, `layers`, `offsets`
- `Data.y`: accuracy label `[1]` float tensor (ViTZooGraphDataset only)
- Checkpoint keys: `encoder_state_dict`, `decoder_state_dict`, `val_loss`, `lam`, `seed`, `epoch`
- `EquiSSLObjective.forward` calls `self.decoder(z_a, graph_a.structure)` — structure dict required

---

## External Dependencies API

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/models/equissl_encoder.py (ACTUAL CODE)
class EquiSSLEncoder(nn.Module):
    def __init__(
        self,
        node_in_dim: int = 4,
        edge_in_dim: int = 4,
        hidden_dim: int = 256,
        latent_dim: int = 128,
        num_layers: int = 4,
        symmetry: str = 'monomial',  # 'monomial'=scale+perm, 'permutation'=perm-only
        pool: str = 'mean',
    ): ...

    def forward(self, data: Data) -> Tensor:
        """data.x: [N, 4], data.edge_attr: [E, 4] -> [B, latent_dim] L2-normalized"""

# From: h-e1/code/models/equissl_objective.py (ACTUAL CODE)
class EquiSSLObjective(nn.Module):
    def __init__(
        self,
        encoder: nn.Module,
        decoder: nn.Module,
        temperature: float = 0.07,
        lam: float = 0.1,
    ): ...

    def forward(self, graph_a: Data, graph_b: Data) -> tuple[Tensor, Tensor]:
        """Returns (total_loss, z_a.detach()) — graph_a must have .structure dict"""

# From: h-e1/code/data/multizoo_graph_dataset.py (ACTUAL CODE)
def checkpoint_to_graph(state_dict: dict) -> Data:
    """state_dict -> Data(x=[n_layers,4], edge_index=[2,E], edge_attr=[E,4], structure=dict)"""

class MultiZooGraphDataset(Dataset):
    def __init__(
        self,
        root: str,
        max_models: int = None,
        normalize: bool = True,
        split: str = 'train',
        val_fraction: float = 0.1,
        seed: int = 0,
    ): ...
    def len(self) -> int: ...
    def get(self, idx: int) -> Data: ...  # Data.x [n_layers,4], no .y label

# From: h-e1/code/data/vitzoo_graph_dataset.py (ACTUAL CODE)
class ViTZooGraphDataset(Dataset):
    def __init__(
        self,
        root: str,
        max_models: int = None,
        normalize: bool = True,
        return_labels: bool = True,
        seed: int = 0,
    ): ...
    def len(self) -> int: ...
    def get(self, idx: int) -> Data: ...  # Data.y = [1] float accuracy label

# From: h-e1/code/data/augmentations.py (ACTUAL CODE)
def perm_augment(graph: Data) -> Data:
    """Gaussian noise augmentation (1% magnitude). NOTE: not true neuron permutation."""

def make_positive_pair(graph: Data, scale_alpha_range: tuple = (0.5, 2.0)) -> tuple[Data, Data]:
    """Returns two views: perm_augment(scale_augment(graph)) each."""

# From: h-e1/code/training/train_equissl.py (ACTUAL CODE)
def load_encoder_from_checkpoint(ckpt_path: str, device: str = 'cuda') -> EquiSSLEncoder:
    """Loads ckpt['encoder_state_dict'] into EquiSSLEncoder with config dims."""

def train_equissl(
    lam: float,
    seed: int,
    data_root: str,
    checkpoint_dir: str,
    device: str = 'cuda',
    epochs: int = None,
    n_train_models: int = None,
) -> str:
    """Train EquiSSL for one lambda/seed. Returns best checkpoint path."""
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, NOT spec!)

---

## A-2: RealViTZooDataset + vit_checkpoint_to_graph [Complexity: 16, Budget: 5]

Applied: extends ViTZooGraphDataset pattern from H-E1

### API Signatures

```python
# code/data/real_vit_zoo_dataset.py
import os, glob
import torch
import numpy as np
from torch_geometric.data import Dataset, Data
from typing import Optional

# Import from H-E1 (direct path import, not package)
# from h-e1 code: checkpoint_to_graph, _scale_normalize_state_dict


def vit_checkpoint_to_graph(state_dict: dict, model_name: str = "") -> Data:
    """Convert ViT state_dict to PyG Data per GMN paper (ICLR 2024).

    Handles attn.qkv (Q/K/V fused), attn.proj, mlp.fc1/fc2, norm layers.
    Node = layer/head-slice. Edge = weight flow between layers.
    head_id encoded as node feature (int, normalized).
    Falls back to checkpoint_to_graph for non-ViT layers.

    Returns Data with:
      x: [N, 5]          # mean, std, l2_norm, max_abs, head_id (0 if not attn)
      edge_index: [2, E]
      edge_attr: [E, 4]
      structure: dict
    """
    ...


class RealViTZooDataset(Dataset):
    """250 real ViT checkpoints with accuracy labels.

    Extends H-E1 ViTZooGraphDataset for ModelZoos/ViTModelZoo format.
    Falls back to ViTZooGraphDataset label discovery (filename parsing).
    """

    def __init__(
        self,
        root: str,
        normalize: bool = True,
        return_labels: bool = True,
        max_models: Optional[int] = None,
        seed: int = 0,
    ):
        # root: path to downloaded ViT Model Zoo directory
        # Discovers checkpoints + labels from metadata.json or filename
        ...
        super().__init__()

    def _discover_checkpoints_and_labels(self, root: str) -> tuple[list[str], list[float]]:
        """Find .ckpt/.pt files; load accuracy from metadata.json or filename."""
        ...

    def len(self) -> int: ...

    def get(self, idx: int) -> Data:
        """Returns Data with x=[N,5], edge_attr=[E,4], y=[1] accuracy label."""
        ...

    def get_labels(self) -> np.ndarray:
        """Returns all accuracy labels as numpy array. Shape: (n_models,)"""
        return np.array(self._labels, dtype=np.float32)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `data.x` | `[N, 5]` | N = number of layer-nodes; feat: mean, std, l2_norm, max_abs, head_id |
| `data.edge_attr` | `[E, 4]` | cross-layer weight statistics |
| `data.edge_index` | `[2, E]` | directed edges layer_i -> layer_j |
| `data.y` | `[1]` | accuracy label float |

**Note on node_in_dim**: H-E1 encoder uses `node_in_dim=4`. H-M1 `vit_checkpoint_to_graph` adds `head_id` as 5th feature. `EquiSSLPermEncoder` must set `node_in_dim=5`. Alternatively, set `head_id` in a separate field and project separately. **Recommended**: keep `node_in_dim=5` for the new encoder; H-E1 frozen encoders take `node_in_dim=4` (use `vit_checkpoint_to_graph` with `include_head_id=False` for those).

### Pseudo-code: vit_checkpoint_to_graph

```
node_feats = []
edge_index = []
edge_feats = []
node_idx = 0
prev_node = None

for key, tensor in sorted(state_dict.items()):
    if 'attn.qkv' or 'attn.in_proj':
        # Q/K/V fused: split into num_heads slices
        W = tensor  # shape [3*D, D] or [3*num_heads*head_dim, D]
        for h in range(num_heads):
            slice_feats = stats(W[h*head_dim:(h+1)*head_dim])  # mean, std, norm, max_abs
            node_feats.append([*slice_feats, h])  # head_id = h
            if prev_node is not None:
                add_edge(prev_node, node_idx, edge_stats(W))
            prev_node = node_idx; node_idx += 1
    elif 'attn.proj' or 'mlp' or 'fc':
        # Standard linear: one node, head_id = 0
        node_feats.append([*stats(tensor), 0])
        if prev_node is not None: add_edge(prev_node, node_idx, edge_stats(tensor))
        prev_node = node_idx; node_idx += 1
    elif 'norm' or 'ln':
        # LayerNorm: fold scale/bias into current node features (not new node)
        pass  # absorbed into nearest linear node's stats

return Data(x=stack(node_feats), edge_index=..., edge_attr=..., structure=...)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | `_discover_checkpoints_and_labels` | Parse ModelZoos dir; load metadata.json or filename accuracy |
| L-2-2 | `vit_checkpoint_to_graph` core | Detect ViT layer keys; dispatch to attn vs mlp vs norm handler |
| L-2-3 | Attention subgraph builder | Q/K/V head slicing, head_id node feature, edge construction |
| L-2-4 | `RealViTZooDataset.get` | Load ckpt, strip Lightning prefix, call vit_checkpoint_to_graph |
| L-2-5 | Unit test | Assert `get(0)` returns Data with correct shapes; `get_labels()` shape (250,) |

---

## A-3: EquiSSLPermEncoder [Complexity: 14, Budget: 4]

Applied: wraps H-E1 EquiSSLEncoder with symmetry='permutation', node_in_dim=5

### API Signatures

```python
# code/models/equi_perm_encoder.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'h-e1', 'code'))
from models.equissl_encoder import EquiSSLEncoder
import torch, torch.nn as nn
from torch_geometric.data import Data, Batch


class EquiSSLPermEncoder(nn.Module):
    """EquiSSLEncoder with symmetry='permutation' and node_in_dim=5 for ViT head_id.

    Permutation-only equivariance: LayerNorm input projection (handles scale at input)
    is still present, but no scale augmentation during training.
    """

    def __init__(
        self,
        node_in_dim: int = 5,    # 4 stats + head_id
        edge_in_dim: int = 4,
        hidden_dim: int = 256,
        latent_dim: int = 128,
        num_layers: int = 4,
    ):
        super().__init__()
        self.encoder = EquiSSLEncoder(
            node_in_dim=node_in_dim,
            edge_in_dim=edge_in_dim,
            hidden_dim=hidden_dim,
            latent_dim=latent_dim,
            num_layers=num_layers,
            symmetry='permutation',  # permutation-only (no scale component in augmentation)
        )

    def forward(self, data: Data) -> torch.Tensor:
        """data.x: [N, 5], data.edge_attr: [E, 4] -> [B, latent_dim] L2-normalized"""
        return self.encoder(data)

    def encode(self, data: Data) -> torch.Tensor:
        """Alias for forward; explicit name for extraction phase."""
        with torch.no_grad():
            return self.forward(data)
```

**Note**: `symmetry='permutation'` is stored on `EquiSSLEncoder` but does not change the forward pass in H-E1's implementation (the encoder uses mean pooling regardless). The flag is preserved for semantic correctness and future ScaleGMN integration. The behavioral difference is in **augmentation only**: EquiSSL-perm uses `perm_augment` only; EquiSSL uses `make_positive_pair` (scale + noise).

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | `EquiSSLPermEncoder.__init__` | Wrap EquiSSLEncoder; set node_in_dim=5, symmetry='permutation' |
| L-3-2 | `forward` + `encode` | Delegate to inner encoder; verify Data.x dim=5 |
| L-3-3 | Checkpoint save/load helpers | `save_equi_perm_ckpt`, `load_equi_perm_encoder` matching H-E1 ckpt format |
| L-3-4 | Shape smoke test | Assert forward on synthetic batch returns (B, 128) |

---

## A-4: train_equi_perm [Complexity: 15, Budget: 4]

Applied: mirrors train_equissl from H-E1 with perm_augment only (no scale_augment)

### API Signatures

```python
# code/training/train_equi_perm.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'h-e1', 'code'))
from data.multizoo_graph_dataset import MultiZooGraphDataset
from data.augmentations import perm_augment  # noise-only, no scale
from models.graph_decoder import GraphDecoder
from models.equissl_objective import EquiSSLObjective

from models.equi_perm_encoder import EquiSSLPermEncoder
import torch, torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from torch_geometric.data import Batch


def collate_perm_only(batch: list) -> tuple[Batch, Batch]:
    """Positive pairs via perm_augment only (no scale). Used as DataLoader collate_fn."""
    views_a = [perm_augment(g) for g in batch]
    views_b = [perm_augment(g) for g in batch]
    return Batch.from_data_list(views_a), Batch.from_data_list(views_b)


def train_equi_perm(
    seed: int,
    data_root: str,
    checkpoint_dir: str,
    lam: float = 0.1,
    epochs: int = 100,
    batch_size: int = 64,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: str = 'cuda',
    n_train_models: int = None,
) -> str:
    """Train EquiSSL-perm for one seed. Returns best checkpoint path.

    Identical to train_equissl except:
      - encoder: EquiSSLPermEncoder (node_in_dim=5, symmetry='permutation')
      - augmentation: perm_augment only (no scale_augment)
      - checkpoint key: 'equi_perm_seed{seed}'
    """
    ...


def train_all_seeds(
    data_root: str,
    checkpoint_dir: str,
    seeds: list[int] = None,
    **train_kwargs,
) -> list[str]:
    """Train EquiSSL-perm for all seeds. Returns list of checkpoint paths."""
    if seeds is None:
        seeds = [0, 1, 2, 3, 4]
    return [train_equi_perm(seed=s, data_root=data_root, checkpoint_dir=checkpoint_dir, **train_kwargs)
            for s in seeds]
```

### Pseudo-code: train_equi_perm

```
set seeds (torch, numpy, random)
encoder = EquiSSLPermEncoder(node_in_dim=5, ...).to(device)
decoder = GraphDecoder(latent_dim=128, hidden_dim=256).to(device)
objective = EquiSSLObjective(encoder, decoder, temperature=0.07, lam=lam).to(device)

train_dataset = MultiZooGraphDataset(root=data_root, normalize=True,
                                      split='train', seed=seed)
# NOTE: MultiZooGraphDataset.get() returns Data.x with shape [n_layers, 4]
# EquiSSLPermEncoder expects node_in_dim=5 → pad x with zeros for head_id column
# Add head_id=0 column: x = torch.cat([x, torch.zeros(x.shape[0],1)], dim=-1) in collate

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True,
                           collate_fn=collate_perm_only, drop_last=True)

optimizer = Adam(objective.parameters(), lr=lr, weight_decay=weight_decay)
scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

best_val_loss = inf
for epoch in 1..epochs:
    for batch_a, batch_b in train_loader:
        # batch_a.x shape: [total_nodes, 4] from MultiZoo (no head_id)
        # Pad to [total_nodes, 5] with zeros for head_id
        batch_a.x = cat([batch_a.x, zeros(N,1)], dim=-1)
        batch_b.x = cat([batch_b.x, zeros(N,1)], dim=-1)
        loss, _ = objective(batch_a, batch_b)
        loss.backward(); clip_grad_norm_; optimizer.step()
    scheduler.step()
    if val_loss < best_val_loss: save checkpoint

checkpoint = {
    'encoder_state_dict': encoder.state_dict(),
    'decoder_state_dict': decoder.state_dict(),
    'val_loss': val_loss, 'seed': seed, 'lam': lam, 'epoch': epoch
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | `collate_perm_only` | perm_augment both views; pad x to dim=5 with zeros for head_id |
| L-4-2 | `train_equi_perm` core loop | Mirrors train_equissl; perm-only augment; CSV log; best ckpt save |
| L-4-3 | `train_all_seeds` | Sequential training over 5 seeds; return paths list |
| L-4-4 | Integration smoke test | 2-epoch run on 10 models; assert checkpoint saved and loadable |

---

## A-5: Embedding Extraction [Complexity: 13, Budget: 3]

Applied: standard frozen-encoder embedding extraction pattern

### API Signatures

```python
# code/evaluation/extract_embeddings.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'h-e1', 'code'))
from training.train_equissl import load_encoder_from_checkpoint  # actual H-E1 function

import torch
import numpy as np
from torch.utils.data import DataLoader
from torch_geometric.data import Batch
from typing import Union


def _pad_x_to_dim5(batch: Batch) -> Batch:
    """Pad batch.x from [N,4] to [N,5] with zeros for head_id column (MultiZoo graphs)."""
    if batch.x.shape[-1] == 4:
        batch.x = torch.cat([batch.x, torch.zeros(batch.x.shape[0], 1, device=batch.x.device)], dim=-1)
    return batch


def extract_embeddings(
    encoder: torch.nn.Module,
    dataset,                        # RealViTZooDataset or ViTZooGraphDataset
    batch_size: int = 32,
    device: str = 'cuda',
    pad_to_dim5: bool = True,       # True for EquiSSL-perm encoder
) -> np.ndarray:
    """Frozen encoder forward on all dataset items.

    Returns: np.ndarray shape (n_models, latent_dim)
    """
    ...


def load_h1_encoder(
    model_name: str,                # 'sane' | 'equi'
    checkpoint_path: str,
    device: str = 'cuda',
) -> torch.nn.Module:
    """Load frozen H-E1 encoder from checkpoint.

    model_name='equi': uses load_encoder_from_checkpoint (node_in_dim=4)
    model_name='sane': loads SANE model (flat tokenizer — different extraction path)
    """
    ...


def extract_all_embeddings(
    vit_dataset,                    # RealViTZooDataset
    he1_checkpoint_dir: str,
    hm1_checkpoint_dir: str,
    seeds: list[int] = None,
    device: str = 'cuda',
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Extract embeddings for all 3 encoder types × 5 seeds.

    Returns:
      embeddings_dict: keys 'sane_seed{i}', 'equi_seed{i}', 'equi_perm_seed{i}'
                       values: np.ndarray shape (250, latent_dim)
      labels: np.ndarray shape (250,) — accuracy labels from vit_dataset
    """
    if seeds is None:
        seeds = [0, 1, 2, 3, 4]
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | `extract_embeddings` | DataLoader loop, encoder.eval(), torch.no_grad(), cat to numpy |
| L-5-2 | `load_h1_encoder` | load_encoder_from_checkpoint for 'equi'; SANE flat path for 'sane' |
| L-5-3 | `extract_all_embeddings` | Orchestrate all seeds × 3 encoders; return dict + labels |

---

## A-6: Linear Probe Evaluation [Complexity: 10, Budget: 2]

Applied: sklearn RidgeCV + scipy ttest_rel pattern from experiment brief

### API Signatures

```python
# code/evaluation/linear_probe.py
import numpy as np
from dataclasses import dataclass
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from scipy.stats import ttest_rel
from typing import Dict


@dataclass
class ProbeResult:
    r2_per_seed: list[float]
    r2_mean: float
    r2_std: float


@dataclass
class StatTestResult:
    t_stat: float
    p_value: float
    significant: bool   # p < 0.05


def linear_probe_r2(
    embeddings: np.ndarray,         # (n_models, latent_dim)
    labels: np.ndarray,             # (n_models,)
    n_seeds: int = 5,
    test_size: float = 0.2,
    alphas: list[float] = None,
) -> ProbeResult:
    """RidgeCV linear probe, n_seeds 80/20 splits, returns mean/std R²."""
    if alphas is None:
        alphas = [0.1, 1.0, 10.0, 100.0]
    r2_per_seed = []
    for seed in range(n_seeds):
        idx = np.arange(len(embeddings))
        tr, te = train_test_split(idx, test_size=test_size, random_state=seed)
        ridge = RidgeCV(alphas=alphas).fit(embeddings[tr], labels[tr])
        r2_per_seed.append(r2_score(labels[te], ridge.predict(embeddings[te])))
    return ProbeResult(r2_per_seed=r2_per_seed, r2_mean=float(np.mean(r2_per_seed)),
                       r2_std=float(np.std(r2_per_seed)))


def run_significance_tests(
    r2_sane: list[float],           # per-seed R² for SANE (5 values)
    r2_equi_perm: list[float],      # per-seed R² for EquiSSL-perm (5 values)
    r2_equi: list[float],           # per-seed R² for EquiSSL (5 values)
) -> Dict[str, StatTestResult]:
    """Paired t-tests: equi_perm vs sane, equi vs sane.

    Returns dict with keys 'equi_perm_vs_sane', 'equi_vs_sane'.
    """
    results = {}
    for name, r2_graph in [('equi_perm_vs_sane', r2_equi_perm), ('equi_vs_sane', r2_equi)]:
        t, p = ttest_rel(r2_graph, r2_sane)
        results[name] = StatTestResult(t_stat=float(t), p_value=float(p), significant=p < 0.05)
    return results


def evaluate_gate(stat_tests: Dict[str, StatTestResult]) -> str:
    """PASS: both significant. PARTIAL: one significant. FAIL: neither."""
    sigs = [v.significant for v in stat_tests.values()]
    if all(sigs):
        return 'PASS'
    elif any(sigs):
        return 'PARTIAL'
    return 'FAIL'
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | `linear_probe_r2` | RidgeCV 80/20 per seed; return ProbeResult dataclass |
| L-6-2 | `run_significance_tests` + `evaluate_gate` | ttest_rel over 5-seed R² lists; PASS/PARTIAL/FAIL |

---

## Summary: Subtask Budget

| Epic | Budget | Used | Subtask IDs |
|------|--------|------|-------------|
| A-2  | 5      | 5    | L-2-1 to L-2-5 |
| A-3  | 4      | 4    | L-3-1 to L-3-4 |
| A-4  | 4      | 4    | L-4-1 to L-4-4 |
| A-5  | 3      | 3    | L-5-1 to L-5-3 |
| A-6  | 2      | 2    | L-6-1, L-6-2  |
| **Total** | **18** | **18** | |

---

## Cross-Cutting Notes for Phase 4 Coder

1. **node_in_dim mismatch**: MultiZooGraphDataset produces `x=[N,4]`. EquiSSLPermEncoder expects `node_in_dim=5`. Pad with zeros in `collate_perm_only` and `extract_embeddings(pad_to_dim5=True)`. H-E1 frozen encoders (EquiSSL, SANE) use `node_in_dim=4` — do NOT pad for those.

2. **H-E1 import path**: All H-E1 modules imported via `sys.path.insert(0, '.../h-e1/code')`. No package install required.

3. **EquiSSLObjective requires `graph.structure`**: `EquiSSLObjective.forward` calls `self.decoder(z_a, graph_a.structure)`. Ensure all batched graphs retain `.structure` dict through `Batch.from_data_list`.

4. **perm_augment is noise-based**: H-E1's `perm_augment` adds 1% Gaussian noise, not true neuron permutation. This is the actual behavior — document as-is; do not re-implement as true permutation unless explicitly requested.

5. **Checkpoint format consistency**: Save EquiSSL-perm checkpoints with same keys as H-E1 (`encoder_state_dict`, `decoder_state_dict`, `val_loss`, `lam`, `seed`, `epoch`) so `load_encoder_from_checkpoint` can be reused.
