# Logic: H-M1

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional) and decoder (causal)

Applied: HuggingFace `output_attentions=True` unified extraction (BertViz-style)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code, no base hypothesis dependency
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-3: Attention Extraction [Complexity: 9, Budget: 9]

**Applied:** HuggingFace `output_attentions=True` unified extraction pattern

### API Signatures

```python
def extract_attentions(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    texts: list[str],
    max_length: int = 128,
    device: str = "cpu",
) -> list[tuple[Tensor, ...]]:
    """Forward pass per sample (batch=1). Returns list of len(texts);
    each item is tuple of len num_layers, each tensor [1, H, S, S]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, S] | batch=1, S<=max_length |
| attentions[i] | [1, H, S, S] | per-layer attn, H=12 |
| return | list[tuple(12 x [1,H,S,S])] | len == len(texts) |

### Pseudo-code

```
1. for text in texts:
2.     enc = tokenizer(text, truncation=True, max_length=max_length,
                        padding=False, return_tensors="pt").to(device)
3.     with torch.no_grad(): out = model(**enc)
4.     results.append(out.attentions)  # tuple[Tensor[1,H,S,S]] len=12
5. return results
```

### Subtasks [3/9 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Single-sample forward | Tokenize + model(**enc, output_attentions=True) |
| L-3-2 | Batch loop | Iterate texts, no_grad, append out.attentions |
| L-3-3 | Device handling | .to(device) for model + inputs, CPU fallback |

---

## A-4: Sparsity Metrics Core [Complexity: 8, Budget: 8]

**Applied:** Boolean-mask upper-triangle extraction via `torch.triu`

### API Signatures

```python
def upper_triangle_sparsity(attn_matrix: Tensor, threshold: float = 1e-6) -> float:
    """attn_matrix: [..., S, S] -> scalar fraction of upper-tri entries < threshold."""
    ...

def compute_attention_sparsity(
    attention_weights: list[tuple[Tensor, ...]],
) -> dict:
    """attention_weights: list of per-sample tuples (12 x [1,H,S,S]).
    Returns {overall_sparsity: float, upper_sparsity: float, is_causal: bool}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attn_matrix | [..., S, S] | last 2 dims = query, key |
| mask | [S, S] bool | `torch.triu(ones(S,S), diagonal=1)` |
| upper_values | [num_upper_elems] | `attn_matrix[..., mask]` |

### Pseudo-code

```
upper_triangle_sparsity(attn_matrix, threshold):
    S = attn_matrix.shape[-1]
    mask = torch.triu(torch.ones(S, S), diagonal=1).bool()
    upper_values = attn_matrix[..., mask]
    return (upper_values < threshold).float().mean().item()

compute_attention_sparsity(attention_weights):
    upper_scores, overall_scores = [], []
    for sample in attention_weights:
        for layer_attn in sample:  # [1,H,S,S]
            upper_scores.append(upper_triangle_sparsity(layer_attn))
            overall_scores.append((layer_attn.abs() < 1e-6).float().mean().item())
    upper_mean = mean(upper_scores)
    return {
        "overall_sparsity": mean(overall_scores),
        "upper_sparsity": upper_mean,
        "is_causal": upper_mean > 0.99,
    }
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | upper_triangle_sparsity | triu mask + threshold compare |
| L-4-2 | compute_attention_sparsity | aggregate over samples/layers, is_causal flag |

---

## A-7: Gate Verification [Complexity: 4, Budget: 4]

### API Signatures

```python
def verify_attention_structure(bert_metrics: dict, gpt2_metrics: dict) -> dict:
    """Compare upper_sparsity vs thresholds. Returns
    {sparsity_difference, bert_is_causal, bert_pass, gpt2_is_causal, gpt2_pass, gate_pass}."""
    ...
```

### Pseudo-code

```
1. bert_pass = bert_metrics["upper_sparsity"] < 0.10
2. gpt2_pass = gpt2_metrics["upper_sparsity"] > 0.99
3. diff = gpt2_metrics["upper_sparsity"] - bert_metrics["upper_sparsity"]
4. gate_pass = bert_pass and gpt2_pass
5. return dict(sparsity_difference=diff, bert_is_causal=bert_metrics["is_causal"],
               bert_pass=bert_pass, gpt2_is_causal=gpt2_metrics["is_causal"],
               gpt2_pass=gpt2_pass, gate_pass=gate_pass)
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | verify_attention_structure | threshold compare + gate dict |
