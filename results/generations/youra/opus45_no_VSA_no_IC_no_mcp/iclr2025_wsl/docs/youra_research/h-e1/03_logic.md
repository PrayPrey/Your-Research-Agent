# Logic: h-e1 (EXISTENCE PoC)

**Scope**: A-3 (DWS model), A-4 (NFT model) — 4 subtasks each per allocation.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: DWS Model [Complexity: 13, Budget: 4+2+4+3]

**Applied**: weight-space-classification-pipeline (equivariant per-layer processing + aggregation)

### API Signatures

```python
class DWSLayer(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int, int]], out_channels: int):
        """Per-layer linear projection, shared logic across SIREN layers."""
        ...

    def forward(self, weight_list: list[Tensor]) -> tuple[Tensor, list[Tensor]]:
        """weight_list[i]: [B, in_c_i, out_c_i] -> agg: [B, out_channels], feats: L x [B, out_channels]"""
        ...


class DWSModel(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int, int]], hidden: int = 128, num_classes: int = 10):
        ...

    def forward(self, weight_list: list[Tensor]) -> Tensor:
        """weight_list: L x [B, in_c, out_c] -> logits [B, num_classes]"""
        ...

    def get_layer_activations(self, weight_list: list[Tensor]) -> list[Tensor]:
        """Returns per-layer feats (no grad) for metrics.layer_activation_variance."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight_list[i] | [B, in_c_i, out_c_i] | per SIREN layer i, varies by shape |
| per_layer_feats[i] | [B, out_channels] | after DWSLayer per-layer linear + pool |
| agg | [B, out_channels] | mean-pooled across L layers |
| logits | [B, num_classes] | final classifier output |

### Pseudo-code

```
DWSLayer.forward(weight_list):
    feats = []
    for i, w in enumerate(weight_list):          # w: [B, in_c_i, out_c_i]
        flat = w.flatten(1)                       # [B, in_c_i*out_c_i]
        f = self.per_layer_linear[i](flat)         # [B, out_channels]
        feats.append(f)
    agg = stack(feats, dim=1).mean(dim=1)          # [B, out_channels]  <- cross-layer aggregation
    return agg, feats

DWSModel.forward(weight_list):
    agg, _ = self.dws_layer(weight_list)           # [B, out_channels]
    h = relu(self.fc1(agg))                        # [B, hidden]
    return self.fc2(h)                             # [B, num_classes]

DWSModel.get_layer_activations(weight_list):
    with no_grad(): _, feats = self.dws_layer(weight_list)
    return feats                                   # L x [B, out_channels]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | DWSLayer init | Per-layer nn.Linear list sized from weight_shapes |
| L-3-2 | DWSLayer forward | Flatten + project each layer, mean-pool aggregation |
| L-3-3 | DWSModel | fc1/fc2 classifier head on aggregated features |
| L-3-4 | get_layer_activations | No-grad hook returning per-layer feats list |

---

## A-4: NFT Model [Complexity: 13, Budget: 4+2+4+3]

**Applied**: weight-space-classification-pipeline (tokenization + TransformerEncoder attention comparison)

### API Signatures

```python
class WeightTokenizer(nn.Module):
    def __init__(self, weight_shapes: list[tuple[int, int]], d_model: int):
        """Per-layer linear projection to shared d_model token space."""
        ...

    def forward(self, weight_list: list[Tensor]) -> Tensor:
        """weight_list: L x [B, in_c, out_c] -> tokens [B, L, d_model]"""
        ...


class NFTModel(nn.Module):
    def __init__(
        self,
        weight_shapes: list[tuple[int, int]],
        d_model: int = 128,
        nhead: int = 4,
        num_layers: int = 2,
        num_classes: int = 10,
    ):
        ...

    def forward(self, weight_list: list[Tensor]) -> Tensor:
        """weight_list -> logits [B, num_classes]"""
        ...

    def get_attention_weights(self, weight_list: list[Tensor]) -> Tensor:
        """Returns last-layer self-attn weights [B, nhead, L, L] (no grad)."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tokens | [B, L, d_model] | L = num SIREN layers = num_tokens |
| encoder_out | [B, L, d_model] | TransformerEncoder output |
| pooled | [B, d_model] | mean pool over token (sequence) dim |
| attn_weights | [B, nhead, L, L] | need_weights=True on last encoder layer |
| logits | [B, num_classes] | classifier output |

### Pseudo-code

```
WeightTokenizer.forward(weight_list):
    tokens = []
    for i, w in enumerate(weight_list):           # w: [B, in_c_i, out_c_i]
        flat = w.flatten(1)                        # [B, in_c_i*out_c_i]
        t = self.per_layer_linear[i](flat)          # [B, d_model]
        tokens.append(t)
    return stack(tokens, dim=1)                     # [B, L, d_model]

NFTModel.forward(weight_list):
    tokens = self.tokenizer(weight_list)            # [B, L, d_model]
    enc = self.transformer_encoder(tokens)          # [B, L, d_model]
    pooled = enc.mean(dim=1)                        # [B, d_model]
    return self.classifier(pooled)                  # [B, num_classes]

NFTModel.get_attention_weights(weight_list):
    tokens = self.tokenizer(weight_list)
    with no_grad():
        # manually run last encoder layer's self_attn with need_weights=True
        _, attn = self.transformer_encoder.layers[-1].self_attn(
            tokens, tokens, tokens, need_weights=True, average_attn_weights=False
        )                                            # attn: [B, nhead, L, L]
    return attn
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | WeightTokenizer | Per-layer nn.Linear list projecting to d_model tokens |
| L-4-2 | NFTModel init | nn.TransformerEncoder(nhead, num_layers) + classifier head |
| L-4-3 | NFTModel forward | Tokenize -> encode -> mean-pool -> classify |
| L-4-4 | get_attention_weights | No-grad hook extracting last-layer self-attn [B,H,L,L] |

---

## verify_mechanism Pseudo-code (metrics.py, referenced by A-3/A-4 usage)

```python
def verify_mechanism(model: nn.Module, sample_input: list[Tensor], model_type: str) -> bool:
    """model_type: 'dws' | 'nft'. Returns True if expected inductive-bias signal present."""
    ...
```

```
verify_mechanism(model, sample_input, model_type):
    if model_type == "dws":
        feats = model.get_layer_activations(sample_input)   # L x [B, out_channels]
        score = layer_activation_variance(feats)
        return score < 1.0                                   # PRD: DWS locality score < 1.0
    elif model_type == "nft":
        attn = model.get_attention_weights(sample_input)     # [B, nhead, L, L]
        entropy = attention_entropy(attn)
        return entropy > 2.0                                 # PRD: NFT attention entropy > 2.0
    else:
        raise ValueError(f"unknown model_type: {model_type}")
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied: line per task
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments + tables
- [x] Subtask count within budget (4/4 each)
- [x] Codebase Analysis (Serena) section included (green-field)
