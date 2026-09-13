---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: "yoon303@ust.ac.kr"
---

# Logic: H-E1 — CNN Weight-Space Encoder for Generalization Gap

## Summary

6 subtasks across E3 (equivariant encoders) and E4 (training loop). All encoders share
`forward(weights) → Tensor[B]` interface and are trained with MSE loss on `gap = train_acc - test_acc`.

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase. Serena MCP skipped per protocol.
Architecture sourced from official repos: DWSNets, neural-graphs, nfn, cnns_weight_prediction.

---

Applied: Encoder-Agnostic-Train-Loop — train_encoder() takes nn.Module; works for all 4 encoders
Applied: Spearman-Val-Selection — select best trial by val Spearman, not val loss
Applied: Early-Stop-On-Best-Checkpoint — deepcopy state_dict at best val Spearman

---

## E3: Equivariant Encoders [4 subtasks]

### L-E3-1: EquivariantLayer (DWSNet building block)

**Parent**: E3 — DWSNet encoder
**Applied**: Standard PyTorch

```python
class EquivariantLayer(nn.Module):
    def __init__(self, fan_in: int, fan_out: int, hidden_dim: int):
        """Row + col linear transforms for a single weight matrix."""
        ...

    def forward(self, w: Tensor) -> Tensor:
        """w: [B, fan_in, fan_out] -> [B, hidden_dim]"""
        ...
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| w | [B, fan_in, fan_out] | single layer weight matrix |
| row_feat | [B, fan_out, hidden_dim] | row-wise linear |
| col_feat | [B, fan_in, hidden_dim] | col-wise linear |
| out | [B, hidden_dim] | mean of row+col features |

Pseudo-code:

```
row_feat = linear_row(w)          # [B, fan_out, hidden_dim] via Linear on last dim
col_feat = linear_col(w.T)        # [B, fan_in, hidden_dim]
combined = row_feat.mean(1) + col_feat.mean(1)  # [B, hidden_dim]
out = activation(combined + bias)  # [B, hidden_dim]
return out
```

Subtasks: [1/1 used]

---

### L-E3-2: DWSNet forward assembly

**Parent**: E3 — DWSNet encoder
**Applied**: Standard PyTorch

```python
class DWSNet(nn.Module):
    def __init__(
        self,
        weight_shapes: list[tuple[int, int]],  # [(fan_in_0, fan_out_0), ...]
        hidden_dim: int = 256,
        n_heads: int = 4,
    ):
        """One EquivariantLayer per weight shape; MLP scalar head."""
        ...

    def forward(self, weights: list[Tensor]) -> Tensor:
        """weights: L x [B, fan_in_i, fan_out_i] -> [B]"""
        ...
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| weights[i] | [B, fan_in_i, fan_out_i] | per-layer weight matrix |
| layer_feats | [L, B, hidden_dim] | equivariant encoding per layer |
| pooled | [B, hidden_dim] | mean across L layers |
| out | [B] | scalar prediction |

Pseudo-code:

```
layer_feats = [eq_layers[i](weights[i]) for i in range(L)]  # L x [B, H]
pooled = stack(layer_feats).mean(0)                          # [B, H]
out = mlp_head(pooled).squeeze(-1)                           # [B]
return out
```

Subtasks: [1/1 used]

---

### L-E3-3: NFT forward (cross-layer attention)

**Parent**: E3 — NFT encoder
**Applied**: Standard PyTorch transformer

```python
class NFT(nn.Module):
    def __init__(
        self,
        weight_shapes: list[tuple[int, int]],  # [(fan_in_0, fan_out_0), ...]
        d_model: int = 256,
        n_heads: int = 4,
        n_layers: int = 4,
    ):
        """Weight rows/cols as tokens; CLS token; transformer; scalar head."""
        ...

    def forward(self, weights: list[Tensor]) -> Tensor:
        """weights: L x [B, fan_in_i, fan_out_i] -> [B]
        NOTE: batch_size=32 required (memory constraint)."""
        ...
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| weights[i] | [B, fan_in_i, fan_out_i] | per-layer weight matrix |
| tokens | [B, T, d_model] | T = sum(fan_in_i + fan_out_i) across all layers + 1 CLS |
| cls_out | [B, d_model] | CLS token after transformer |
| out | [B] | scalar prediction |

Pseudo-code:

```
# Tokenize: flatten rows and cols of each layer weight matrix
row_tokens = [proj(w[i])  for w in weights]   # rows as tokens: [B, fan_in_i, d_model]
col_tokens = [proj(w[i].T) for w in weights]  # cols as tokens: [B, fan_out_i, d_model]
cls = repeat(cls_token, B)                    # [B, 1, d_model]
tokens = cat([cls, *row_tokens, *col_tokens], dim=1)  # [B, T, d_model]
for layer in transformer_layers:
    tokens = layer(tokens)  # cross-layer attention
cls_out = tokens[:, 0, :]   # [B, d_model]
out = linear_head(cls_out).squeeze(-1)  # [B]
return out
```

Subtasks: [1/1 used]

---

### L-E3-4: GNN forward (bipartite graph)

**Parent**: E3 — GNN encoder
**Applied**: PyG MessagePassing pattern

```python
class GNN(nn.Module):
    def __init__(
        self,
        node_dim: int,
        edge_dim: int,
        hidden_dim: int = 256,
        n_layers: int = 4,
    ):
        """Bipartite neuron graph; message passing; global pool; scalar head."""
        ...

    def forward(self, weights: list[Tensor]) -> Tensor:
        """weights: L x [B, fan_in_i, fan_out_i] -> [B]
        Requires torch_geometric. Builds bipartite graph per batch item."""
        ...
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| weights[i] | [B, fan_in_i, fan_out_i] | per-layer weight matrix |
| node_feat | [B*N_nodes, node_dim] | neuron features (bias init) |
| edge_attr | [B*N_edges, edge_dim] | weight values as edge attrs |
| edge_index | [2, B*N_edges] | bipartite connectivity |
| graph_emb | [B, hidden_dim] | global mean pool over nodes |
| out | [B] | scalar prediction |

Pseudo-code:

```
# Build batched bipartite graph from weight matrices
node_feat, edge_index, edge_attr, batch_vec = build_bipartite_graph(weights)
for mp_layer in mp_layers:
    node_feat = mp_layer(node_feat, edge_index, edge_attr)  # message passing
graph_emb = global_mean_pool(node_feat, batch_vec)          # [B, hidden_dim]
out = linear_head(graph_emb).squeeze(-1)                    # [B]
return out
```

Subtasks: [1/1 used]

---

## E4: Training Loop [2 subtasks]

### L-E4-1: train_encoder() with checkpoint

**Parent**: E4 — Training loop
**Applied**: Encoder-Agnostic-Train-Loop, Spearman-Val-Selection, Early-Stop-On-Best-Checkpoint

```python
import copy
from scipy.stats import spearmanr
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

def train_encoder(
    encoder: nn.Module,
    zoo: "ZooData",
    lr: float,
    batch_size: int,
    epochs: int,
    seed: int = 42,
    lr_schedule: str = "none",  # "none" | "cosine"
) -> tuple[nn.Module, float, list[float]]:
    """Train encoder with MSE on gap; select by val Spearman.
    Returns (best_model, best_val_spearman, val_spearman_curve)."""
    ...
```

Pseudo-code:

```
torch.manual_seed(seed)
train_loader = make_loader(zoo, "train", batch_size, shuffle=True)
val_loader   = make_loader(zoo, "val",   batch_size, shuffle=False)
optimizer = Adam(encoder.parameters(), lr=lr)
scheduler = CosineAnnealingLR(optimizer, epochs) if lr_schedule == "cosine" else None
best_r, best_state, curve = -inf, None, []
for epoch in range(epochs):
    encoder.train()
    for weights, gap in train_loader:
        loss = F.mse_loss(encoder(weights), gap)
        optimizer.zero_grad(); loss.backward(); optimizer.step()
    if scheduler: scheduler.step()
    encoder.eval()
    val_r = spearmanr(predict_all(encoder, val_loader), get_targets(val_loader)).correlation
    curve.append(val_r)
    if val_r > best_r:
        best_r = val_r
        best_state = copy.deepcopy(encoder.state_dict())
encoder.load_state_dict(best_state)
return encoder, best_r, curve
```

Subtasks: [1/1 used]

---

### L-E4-2: random_search() 50-trial protocol

**Parent**: E4 — Training loop
**Applied**: Spearman-Val-Selection

```python
from typing import Type

def random_search(
    encoder_cls: Type[nn.Module],
    arch_kwargs: dict,
    zoo: "ZooData",
    lr_candidates: list[float],
    batch_size: int,
    epochs: int,
    n_trials: int = 50,
) -> tuple[nn.Module, dict, list[float]]:
    """Random search over lr_candidates; select by best val Spearman.
    Returns (best_model, best_config, best_val_curve)."""
    ...
```

Pseudo-code:

```
best_r, best_model, best_cfg, best_curve = -inf, None, None, None
rng = random.Random(42)
for trial in range(n_trials):
    lr = rng.choice(lr_candidates)
    encoder = encoder_cls(**arch_kwargs)
    model, val_r, curve = train_encoder(encoder, zoo, lr, batch_size, epochs, seed=42)
    if val_r > best_r:
        best_r, best_model, best_cfg, best_curve = val_r, model, {"lr": lr}, curve
return best_model, best_cfg, best_curve
```

Subtasks: [1/1 used]

---

## Integration Notes

- L-E3-1 is used exclusively by L-E3-2 (EquivariantLayer is internal to DWSNet).
- L-E3-2, L-E3-3, L-E3-4 all conform to the `forward(weights: list[Tensor]) -> Tensor[B]` interface from E3; FlatMLP (E2) uses `forward(weights_flat: Tensor[B, D]) -> Tensor[B]` (loader handles flattening).
- L-E4-2 calls L-E4-1 internally; called once per encoder in `run_experiment.py`.
- `make_loader()` (E1) handles weight formatting per encoder type before L-E4-1 receives batches.
- `eval_spearman()` (E5) is called on the best model returned from L-E4-2 to produce test results.
- GNN encoder (L-E3-4) requires `torch_geometric`; `build_bipartite_graph()` is a helper inside `gnn.py`.

---

## Subtask Budget

| ID | Subtask | Epic | Complexity |
|----|---------|------|------------|
| L-E3-1 | EquivariantLayer | E3 | 1/4 |
| L-E3-2 | DWSNet forward | E3 | 2/4 |
| L-E3-3 | NFT forward | E3 | 3/4 |
| L-E3-4 | GNN forward | E3 | 4/4 |
| L-E4-1 | train_encoder | E4 | 1/2 |
| L-E4-2 | random_search | E4 | 2/2 |

**Total**: 6/6 subtasks used.
