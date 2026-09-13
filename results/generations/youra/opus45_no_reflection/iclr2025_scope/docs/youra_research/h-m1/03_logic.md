# Logic: H-M1 (Attention Entropy Analysis)

**Applied**: Standard PyTorch (no specific KB pattern matched; searched "attention entropy computation" and "attention analysis" — only unrelated diffusers/flash-attention/SDPA results found)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code, no base_hypothesis_folder provided
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4/A-5: Metrics Module (`code/metrics.py`) [Complexity: 6+5=11, Budget: split into 2 tasks below]

### API Signatures

```python
import torch
from torch import Tensor

def compute_entropy(attention_weights: Tensor, clamp_min: float = 1e-10) -> Tensor:
    """Shannon entropy per query position. attn: [B, H, S, S] -> [B, H, S]"""
    ...

def compute_sparsity(attention_weights: Tensor, top_k: int = 32) -> Tensor:
    """Top-k mass fraction per query position. attn: [B, H, S, S] -> [B, H, S]"""
    ...

def aggregate_stats(values: List[float]) -> dict:
    """Returns {"mean": float, "std": float, "ci95_lo": float, "ci95_hi": float, "n": int}"""
    ...

def entropy_change_pct(entropy_a: float, entropy_b: float) -> float:
    """(entropy_b - entropy_a) / entropy_a"""
    ...

def find_inflection_point(lengths: List[int], entropies: List[float]) -> int:
    """Second derivative of entropy vs log(length). Returns index into `lengths`."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attention_weights | [B, H, S, S] | B=1 (single doc), H=32 (Phi-1.5 heads), S=seq_len |
| entropy out | [B, H, S] | per-position entropy |
| sparsity out | [B, H, S] | per-position top-k mass fraction |

### Pseudo-code

```
compute_entropy(attn, clamp_min):
    p = attn.clamp(min=clamp_min)              # [B,H,S,S]
    H = -(p * p.log()).sum(dim=-1)              # [B,H,S]
    return H

compute_sparsity(attn, top_k):
    topk_vals, _ = attn.topk(k=top_k, dim=-1)   # [B,H,S,top_k]
    return topk_vals.sum(dim=-1)                # [B,H,S], fraction since attn rows sum to 1

find_inflection_point(lengths, entropies):
    log_len = log(lengths)                      # [5]
    d1 = gradient(entropies, log_len)            # first derivative (np.gradient)
    d2 = gradient(d1, log_len)                   # second derivative
    return argmax(abs(d2))
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | compute_entropy | Clamp + `-sum(p*log p)` over last dim, [B,H,S,S]->[B,H,S] |
| L-4-2 | compute_sparsity | `topk(dim=-1).sum(dim=-1)`, [B,H,S,S]->[B,H,S] |
| L-4-3 | aggregate_stats + entropy_change_pct | mean/std/95% CI (1.96*std/sqrt(n)); pct change helper |
| L-4-4 | find_inflection_point | `np.gradient` twice over log-length axis, argmax abs(d2) |

---

## A-2: Model Loading + Attention Extraction (`code/model.py`) [Complexity: 9, Budget: 4]

### API Signatures

```python
from typing import Dict, Tuple
from torch import nn, Tensor

def load_model_and_tokenizer(config: "AnalysisConfig") -> Tuple[nn.Module, "PreTrainedTokenizer"]:
    """AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=fp16, device_map="auto",
    trust_remote_code=True, output_attentions=True). Returns (model.eval(), tokenizer)."""
    ...

def extract_attentions(model: nn.Module, tokens: dict, middle_layers: List[int]) -> Dict[int, Tensor]:
    """Forward pass with output_attentions=True under no_grad. Returns {layer_idx: attn}
    where attn: [1, H, S, S], one entry per layer in middle_layers."""
    ...

def verify_attention_valid(attn: Tensor) -> None:
    """Asserts torch.isfinite(attn).all(), (attn >= 0).all(),
    attn.sum(dim=-1) allclose to 1.0 (atol=1e-5). Raises AssertionError on failure."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tokens["input_ids"] | [1, S] | single doc, batch=1 |
| model(...).attentions | tuple of 24 x [1, H, S, S] | one per transformer layer |
| extract_attentions out[layer_idx] | [1, H, S, S] | selected middle layers only (8,12,16) |

### Pseudo-code

```
extract_attentions(model, tokens, middle_layers):
    with torch.no_grad():
        out = model(**tokens, output_attentions=True)
    return {i: out.attentions[i] for i in middle_layers}   # each [1,H,S,S]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_model_and_tokenizer | fp16, device_map=auto, trust_remote_code, output_attentions=True |
| L-2-2 | extract_attentions | no_grad forward, select layers 8/12/16 from `out.attentions` tuple |
| L-2-3 | verify_attention_valid | finite/non-negative/row-sum==1 asserts |
| L-2-4 | 32K memory handling | del intermediate attentions after use, `torch.cuda.empty_cache()` between docs |

---

## A-7/A-8: Analysis Pipeline + Gate Metrics (`code/analysis.py`) [Complexity: 12+6, Budget: split below]

### API Signatures

```python
def run_analysis(config: "AnalysisConfig") -> dict:
    """Loop target_lengths x documents x middle_layers.
    results[length][layer] = {"entropy": {mean,std,ci95_lo,ci95_hi,n},
                               "sparsity": {mean,std,ci95_lo,ci95_hi,n}}"""
    ...

def compute_gate_metrics(results: dict) -> dict:
    """entropy_change_pct(results[2048][layer].entropy.mean, results[16384][layer].entropy.mean)
    per layer + overall; pass = change > 0.20. Returns {"pass": bool, "per_layer": {...}, "overall_pct": float}"""
    ...

def save_results(results: dict, gate_metrics: dict, config: "AnalysisConfig") -> None:
    """json.dump({"results":..., "gate":...}, open(f"{output_dir}/results.json","w"))"""
    ...
```

### Pseudo-code (pipeline orchestration — complex nested loop)

```
run_analysis(config):
    model, tok = load_model_and_tokenizer(config)
    docs = get_long_documents(config, tok)                      # List[str], len=500
    acc = defaultdict(lambda: defaultdict(lambda: {"entropy": [], "sparsity": []}))

    for length in config.target_lengths:
        for doc in docs:
            tokens = truncate_to_length(doc, tok, length)         # [1, length]
            attns = extract_attentions(model, tokens, config.middle_layers)
            for layer, attn in attns.items():                     # attn: [1,H,length,length]
                verify_attention_valid(attn)
                H = compute_entropy(attn, config.entropy_clamp_min).mean(dim=(0,1))  # [length] -> scalar mean
                S = compute_sparsity(attn, config.top_k).mean(dim=(0,1))
                acc[length][layer]["entropy"].append(H.mean().item())
                acc[length][layer]["sparsity"].append(S.mean().item())
            del attns; torch.cuda.empty_cache()

    results = {length: {layer: {"entropy": aggregate_stats(acc[length][layer]["entropy"]),
                                 "sparsity": aggregate_stats(acc[length][layer]["sparsity"])}
                         for layer in config.middle_layers}
               for length in config.target_lengths}
    return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run_analysis outer loop | length x doc loop, truncate + extract_attentions per doc |
| L-7-2 | run_analysis inner accumulation | per-layer entropy/sparsity mean, memory cleanup per doc |
| L-7-3 | run_analysis aggregation | aggregate_stats per (length, layer), assemble results dict |
| L-7-4 | compute_gate_metrics + save_results | per-layer + overall entropy_change_pct, >20% pass check, JSON dump |

---

## Total Subtasks: 16/16 (4 tasks x 4 subtasks, within 4-subtask-per-task budget)
