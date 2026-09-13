# Logic: h-m3 (MECHANISM)

**Applied**: Standard PyTorch logit-lens projection (h @ unembedding.T), consecutive-layer argmax diff for flip detection.

## Codebase Analysis (Serena)

**Project Type**: green-field (base hypothesis h-e1/code/ does not exist on disk)
**Status**: Green-field project - designing new APIs, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## M-5: RCI Flip Detector [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch logit-lens projection

### API Signatures

```python
class RCIFlipDetector:
    def __init__(self, unembedding_weight: Tensor, layer_range: tuple[int, int] = (24, 32)):
        """unembedding_weight: [vocab_size, hidden_dim] (lm_head.weight)."""
        self.W = unembedding_weight  # [V, 4096]
        self.layer_range = layer_range  # (24, 32) inclusive -> 9 layers

    def extract_layer_predictions(self, hidden_states: tuple[Tensor, ...], position: int = -1) -> Tensor:
        """hidden_states: 33-tuple of [B, seq, 4096] -> logits [9, B, V]."""
        ...

    def detect_flip_pattern(self, layer_logits: Tensor) -> tuple[Tensor, Tensor]:
        """layer_logits: [9, B, V] -> (num_flips [B], flip_positions [B, 8] bool)."""
        ...

    def compute_sample(self, hidden_states: tuple[Tensor, ...]) -> dict:
        """-> {"num_flips": int, "has_flip": bool, "flip_positions": list[int]}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | 33-tuple of [B, seq, 4096] | HF output_hidden_states, index 24-32 selected |
| layer_logits | [9, B, V] | 9 = layer_range span (24..32 inclusive) |
| top_tokens | [9, B] | argmax(layer_logits, dim=-1) |
| flip_positions | [B, 8] bool | True where top_tokens[i] != top_tokens[i+1] |
| num_flips | [B] int | flip_positions.sum(dim=-1) |

### Pseudo-code (flip detection)

```
1. selected = hidden_states[layer_range[0] : layer_range[1]+1]   # 9 tensors [B, seq, 4096]
2. h_last = stack([s[:, position, :] for s in selected])          # [9, B, 4096]
3. layer_logits = h_last @ W.T                                    # [9, B, V]
4. top_tokens = argmax(layer_logits, dim=-1)                      # [9, B]
5. flips = top_tokens[1:] != top_tokens[:-1]                      # [8, B]
6. num_flips = flips.sum(dim=0)                                   # [B]
7. has_flip = num_flips > 0
8. flip_positions = nonzero indices along layer axis (per sample, offset by layer_range[0])
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M5-1 | extract_layer_predictions + detect_flip_pattern | Logit-lens projection (steps 1-3) and flip detection (steps 4-6), unit-testable on synthetic hidden_states |
| L-M5-2 | compute_sample | Wraps detector for single-sample dict output; batch_size=1 assumed (position=-1 default), converts tensors to python types |

---

## External Dependencies

None — green-field, no base hypothesis code to import.
