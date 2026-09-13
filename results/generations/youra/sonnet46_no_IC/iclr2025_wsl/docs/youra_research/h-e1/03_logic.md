# Logic: H-E1 — EquiSSL Distribution Shift PoC

**Applied**: Standard PyTorch Module API pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation. Interface design follows PyG `Data` conventions and SimCLR-style contrastive loss patterns. All API signatures are designed to be consistent across E-1 and E-2 modules, with `Data` objects as the graph currency.

---

## E-1: Graph Data Pipeline [Complexity: 14/20, Budget: 4 subtasks]

### L-E1-1: `checkpoint_to_graph` [Subtask 1/4]

**File**: `data/multizoo_graph_dataset.py`

#### API Signature

```python
def checkpoint_to_graph(state_dict: dict[str, torch.Tensor]) -> Data:
    """Convert a PyTorch state_dict to a PyG Data object.
    Nodes = bias vectors, edges = flattened weight matrices."""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| node x | (N_nodes, 1) | bias scalars; one node per neuron |
| edge_attr | (N_edges, d_flat) | flattened weight matrix per layer transition; d_flat = in_dim * out_dim |
| edge_index | (2, N_edges) | directed src→dst; N_edges = number of layer-to-layer connections |

#### Algorithm

```
# state_dict has keys like: 'layers.0.weight', 'layers.0.bias', 'layers.1.weight', ...

1. Parse keys → ordered list of (weight, bias) pairs per layer
2. Build node list: for each layer i, append bias_i as row in x  # each bias row → [n_neurons_i, 1]
3. Cumulative neuron offsets: offset[i] = sum(n_neurons_0..i-1)
4. For each weight matrix W between layer i and i+1:
   a. src_nodes = arange(n_i) + offset[i]    # all neurons in layer i
   b. dst_nodes = arange(n_{i+1}) + offset[i+1]  # all neurons in layer i+1
   c. edge_index cols = cartesian product (src, dst)  # shape (2, n_i * n_{i+1})
   d. edge_attr rows = W.flatten() repeated per edge, OR store W as one edge per weight row
      # CHOICE: one edge per (src_neuron, dst_neuron), edge_attr = scalar weight → (N_edges, 1)
      # OR: one edge per layer, edge_attr = W.flatten() → (N_layers-1, d_flat)
      # USE: per-neuron-pair edges (N_edges = sum of n_i * n_{i+1}), edge_attr = (N_edges, 1)
5. structure = {layer_idx: (in_dim, out_dim)} for decoder reconstruction
6. return Data(x=x, edge_index=edge_index, edge_attr=edge_attr, structure=structure)
```

**Key invariant**: `structure` dict is the sole record of original weight shapes; required by GraphDecoder.

**Note on edge_attr design**: Per-neuron-pair edges (each edge = one scalar weight) keeps d_flat=1 uniform across architectures. Alternatively, per-layer edges with flattened weight vectors have variable d_flat. The architecture doc specifies `edge_attr=[n_edges, d_flat]` with variable d_flat — use **per-layer edges** (one edge per layer transition) with d_flat=in_dim*out_dim, and `edge_index` encodes layer connectivity (one src node = layer-level virtual node, or use neuron-pair). Implement as per-layer with `PyG` padding or use **per-neuron-pair scalar** for uniform shape. Since ScaleGMN operates on graph structure, prefer per-neuron-pair scalar (d_flat=1) for architectural uniformity.

---

### L-E1-2: `scale_augment` [Subtask 2/4]

**File**: `data/augmentations.py`

#### API Signature

```python
def scale_augment(
    graph: Data,
    alpha: torch.Tensor | None = None,
    alpha_range: tuple[float, float] = (0.5, 2.0)
) -> Data:
    """Scale-equivariant augmentation: scale layer i by alpha_i, layer i+1 by alpha_i^{-1}.
    Preserves network function. alpha: (n_hidden_layers,) or None for random."""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| alpha | (n_hidden_layers,) | per-layer scale factor; sampled log-uniform if None |
| graph.x (out) | (N_nodes, 1) | biases scaled: b_i *= alpha_i |
| graph.edge_attr (out) | (N_edges, 1) | weights scaled: W_{i→i+1} *= alpha_i, W_{i+1→i+2} *= alpha_i^{-1} |

#### Algorithm

```
1. If alpha is None: alpha = torch.exp(torch.FloatTensor(n_hidden).uniform_(log(alpha_range[0]), log(alpha_range[1])))
2. Clone graph (deep copy edge_attr, x)
3. For each hidden layer i in range(n_hidden_layers):
   a. node_mask_i = nodes belonging to layer i  # use structure dict
   b. x[node_mask_i] *= alpha[i]
   c. edge_mask_in = edges incoming to layer i  # layer i-1 → layer i
   d. edge_mask_out = edges outgoing from layer i  # layer i → layer i+1
   e. edge_attr[edge_mask_out] *= alpha[i]
   f. edge_attr[edge_mask_in] *= (1.0 / alpha[i])  # compensate previous layer
   # Net effect: W_{i→i+1} → alpha_i * W_{i→i+1}, b_i → alpha_i * b_i (preserves f(x))
4. return augmented Data
```

**Key invariant**: Scale equivariance preserved — the augmented network computes the same function as original. ScaleGMN is invariant to these scales, so augmented pairs map to same latent region.

---

### L-E1-3: `perm_augment` [Subtask 3/4]

**File**: `data/augmentations.py`

#### API Signature

```python
def perm_augment(graph: Data) -> Data:
    """Randomly permute hidden neuron ordering within each layer.
    Preserves network function (permutation symmetry of hidden layers)."""
```

#### Algorithm

```
1. Clone graph
2. For each hidden layer i:
   a. perm_i = torch.randperm(n_neurons_i)  # random permutation of hidden units
   b. node_mask_i = nodes of layer i
   c. x[node_mask_i] = x[node_mask_i][perm_i]  # permute bias values
   d. For edges incoming to layer i (src → layer_i_dst):
      remap dst node indices: edge_index[1, incoming_mask] = perm_i[edge_index[1, incoming_mask] - offset_i] + offset_i
   e. For edges outgoing from layer i (layer_i_src → dst):
      remap src node indices: edge_index[0, outgoing_mask] = perm_i[edge_index[0, outgoing_mask] - offset_i] + offset_i
3. return permuted Data
```

**Key invariant**: Graph structure (edge_index) updated to match new neuron ordering — ScaleGMN permutation invariance maps both views to same latent.

---

### L-E1-4: `make_positive_pair` [Subtask 4/4]

**File**: `data/augmentations.py`

#### API Signature

```python
def make_positive_pair(
    graph: Data,
    scale_alpha_range: tuple[float, float] = (0.5, 2.0)
) -> tuple[Data, Data]:
    """Return two independently augmented views of the same graph.
    Each view: scale_augment then perm_augment with independent random draws."""
```

#### Algorithm

```
1. view_a = perm_augment(scale_augment(graph, alpha=None, alpha_range=scale_alpha_range))
2. view_b = perm_augment(scale_augment(graph, alpha=None, alpha_range=scale_alpha_range))
   # independent alpha samples for each view
3. return (view_a, view_b)
```

**Key invariant**: Both views are semantically equivalent networks; EquiSSL encoder must map them to nearby latents.

---

## E-2: EquiSSL Encoder Wrapper [Complexity: 15/20, Budget: 4 subtasks]

### L-E2-1: `EquiSSLEncoder.__init__` [Subtask 1/4]

**File**: `models/equissl_encoder.py`

#### API Signature

```python
import sys
import os
import torch.nn as nn
from torch_geometric.data import Data

class EquiSSLEncoder(nn.Module):
    def __init__(
        self,
        scalegmn_path: str,          # absolute path to jkalogero/scalegmn repo root
        node_in_dim: int = 1,        # bias scalar features
        edge_in_dim: int = 1,        # weight scalar features (per-edge)
        hidden_dim: int = 256,
        latent_dim: int = 128,
        num_layers: int = 4,
        symmetry: str = 'monomial',  # 'monomial'=scale+perm, 'permutation'=ablation
        pool: str = 'mean',          # global pooling: 'mean' | 'sum'
    ) -> None:
        """Wrap ScaleGMN with monomial symmetry for scale+perm invariant graph encoding."""
```

#### Algorithm

```
1. super().__init__()
2. sys.path.insert(0, scalegmn_path)
3. from scalegmn.models import ScaleGMN  # or whatever ScaleGMN's actual import path is
4. self.backbone = ScaleGMN(
       node_in_dim=node_in_dim,
       edge_in_dim=edge_in_dim,
       hidden_dim=hidden_dim,
       num_layers=num_layers,
       symmetry=symmetry,
       pool=pool,
   )
   # ScaleGMN output dim: hidden_dim (after pooling); project to latent_dim
5. self.proj = nn.Sequential(
       nn.Linear(hidden_dim, hidden_dim),
       nn.ReLU(),
       nn.Linear(hidden_dim, latent_dim),
   )
   # ponytail: proj head kept simple; use BN+larger head if SSL underfits
```

**Note**: Actual ScaleGMN constructor arg names must be verified against `jkalogero/scalegmn` source at integration time. The arg names above are representative — Phase 4 Coder must inspect `scalegmn/models/__init__.py` or equivalent.

---

### L-E2-2: `EquiSSLEncoder.forward` [Subtask 2/4]

**File**: `models/equissl_encoder.py`

#### API Signature

```python
    def forward(self, data: Data) -> torch.Tensor:
        """Encode a batch of graphs to scale+perm invariant latent vectors.
        Returns z of shape (B, latent_dim), L2-normalized."""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| data.x | (sum_N_nodes_in_batch, 1) | batched node features |
| data.edge_attr | (sum_N_edges_in_batch, 1) | batched edge features |
| data.edge_index | (2, sum_N_edges_in_batch) | global node indices |
| data.batch | (sum_N_nodes_in_batch,) | batch assignment per node |
| h | (B, hidden_dim) | pooled graph representation from ScaleGMN; B=64 |
| z | (B, latent_dim) | projected latent; (B=64, 128) |
| z_norm | (B, latent_dim) | L2-normalized; (B=64, 128) |

#### Algorithm

```
1. h = self.backbone(data.x, data.edge_index, data.edge_attr, data.batch)
   # ScaleGMN does message passing + global pool → (B, hidden_dim)
2. z = self.proj(h)       # (B, latent_dim)
3. z_norm = F.normalize(z, dim=-1)  # (B, latent_dim), unit sphere
4. return z_norm
```

**Key invariant**: L2 normalization on unit sphere is required for NT-Xent cosine similarity formulation.

---

### L-E2-3: `nt_xent_loss` [Subtask 3/4]

**File**: `models/equissl_objective.py`

#### API Signature

```python
def nt_xent_loss(
    z_a: torch.Tensor,      # (B, latent_dim), L2-normalized
    z_b: torch.Tensor,      # (B, latent_dim), L2-normalized
    temperature: float = 0.07,
) -> torch.Tensor:
    """SimCLR NT-Xent contrastive loss on 2B samples.
    Returns scalar loss."""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| z_a, z_b | (B, D) | B=64, D=128 |
| z | (2B, D) | concatenated views; (128, 128) |
| sim | (2B, 2B) | cosine similarity matrix / temperature |
| labels | (2B,) | positive pair index for each sample |
| loss | () | scalar cross-entropy |

#### Algorithm

```
1. z = torch.cat([z_a, z_b], dim=0)             # (2B, D)
2. sim = z @ z.T / temperature                   # (2B, 2B) — already L2-norm so this is cosine/τ
3. # Mask out self-similarity diagonal
   mask = torch.eye(2*B, dtype=bool, device=z.device)
   sim = sim.masked_fill(mask, -1e9)
4. # Positive pairs: (i, i+B) and (i+B, i)
   labels = torch.cat([torch.arange(B, 2*B), torch.arange(B)]).to(z.device)  # (2B,)
5. loss = F.cross_entropy(sim, labels)
6. return loss
```

**Key invariant**: NT-Xent pulls positive pairs (same graph, different augmentation) together; pushes all 2(B-1) negatives apart.

---

### L-E2-4: `EquiSSLObjective.forward` [Subtask 4/4]

**File**: `models/equissl_objective.py`

#### API Signature

```python
class EquiSSLObjective(nn.Module):
    def __init__(
        self,
        encoder: nn.Module,         # EquiSSLEncoder instance
        decoder: nn.Module,         # GraphDecoder instance
        temperature: float = 0.07,
        lam: float = 0.1,           # reconstruction loss weight
    ) -> None:
        """Combined SSL objective: NT-Xent + lambda * MSE reconstruction."""

    def forward(
        self,
        graph_a: Data,              # augmented view A, batched PyG Data
        graph_b: Data,              # augmented view B, batched PyG Data
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns (total_loss, z_a).
        total_loss = nt_xent + lam * mse_recon  — scalar
        z_a = (B, latent_dim) — for downstream MMD eval"""
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| z_a, z_b | (B, 128) | L2-normalized latents from encoder |
| recon_edge_attr | (sum_N_edges, 1) | reconstructed edge features from decoder |
| mse_recon | () | MSE vs graph_a.edge_attr |
| total_loss | () | scalar, backward-ready |

#### Algorithm

```
1. z_a = self.encoder(graph_a)               # (B, latent_dim)
2. z_b = self.encoder(graph_b)               # (B, latent_dim)
3. contrastive = nt_xent_loss(z_a, z_b, self.temperature)  # scalar
4. recon = self.decoder(z_a, graph_a.structure)  # (sum_N_edges, 1) or (B, max_edges)
5. mse_recon = F.mse_loss(recon, graph_a.edge_attr)         # scalar
6. total_loss = contrastive + self.lam * mse_recon
7. return (total_loss, z_a.detach())
```

**Key invariant**: `z_a.detach()` returned to avoid holding computation graph in eval/MMD collection; `total_loss` is not detached (used for `.backward()`).

---

## Subtask Summary

| ID | Subtask | File | Budget |
|----|---------|------|--------|
| L-E1-1 | `checkpoint_to_graph` | `data/multizoo_graph_dataset.py` | 1/8 |
| L-E1-2 | `scale_augment` | `data/augmentations.py` | 2/8 |
| L-E1-3 | `perm_augment` | `data/augmentations.py` | 3/8 |
| L-E1-4 | `make_positive_pair` | `data/augmentations.py` | 4/8 |
| L-E2-1 | `EquiSSLEncoder.__init__` | `models/equissl_encoder.py` | 5/8 |
| L-E2-2 | `EquiSSLEncoder.forward` | `models/equissl_encoder.py` | 6/8 |
| L-E2-3 | `nt_xent_loss` | `models/equissl_objective.py` | 7/8 |
| L-E2-4 | `EquiSSLObjective.forward` | `models/equissl_objective.py` | 8/8 |
