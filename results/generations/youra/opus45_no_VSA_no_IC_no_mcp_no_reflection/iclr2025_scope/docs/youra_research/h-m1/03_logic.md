# Logic Design: h-m1

**Hypothesis:** h-m1 (MECHANISM) | **Budget:** 6 subtasks

Applied: MOHAWK Stage-1 Matrix Alignment Pattern (Archon KB)
Applied: PyTorch forward-hook pattern for intermediate layer output capture (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code (not spec)
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**: `duality_init_ssm_from_attention` (duality_conversion.py), `selective_scan_ref` (selective_scan.py), `load_wikitext_samples` (data_loader.py)
**Finding**: All three signatures in `h-e1/03_architecture.md` match actual code exactly — no renamed params. `run_experiment.py` (h-e1) only reads `bert(input_ids).last_hidden_state` (full model output), **not** per-layer attention output — h-m1 must add a forward hook on `attention.self` since `BertSelfAttention.forward` output is not otherwise exposed per-layer.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/duality_conversion.py (ACTUAL CODE)
def duality_init_ssm_from_attention(
    attn_layer: BertSelfAttention,
    d_state: int = 64
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """Returns A:[d_model,d_state], B:[d_state,d_model], C:[d_model,d_state], D:[d_model], dt:[d_model]"""

# From: h-e1/code/selective_scan.py (ACTUAL CODE)
def selective_scan_ref(x: Tensor, A: Tensor, B: Tensor, C: Tensor, D: Tensor, dt: Tensor) -> Tensor:
    """x: [batch, seq_len, d_model] -> y: [batch, seq_len, d_model]"""

# From: h-e1/code/data_loader.py (ACTUAL CODE)
def load_wikitext_samples(
    num_samples: int = 100, min_length: int = 512, max_length: int = 2048, cache_dir: str = None
) -> List[Dict[str, Tensor]]:
    """Returns list of {"input_ids": Tensor[1,L], "attention_mask": Tensor[1,L]}"""
```

**Verified from**: `h-e1/code/` (actual implementation). Copy `duality_conversion.py`, `selective_scan.py`, `data_loader.py` into `h-m1/code/` unmodified, flat layout (no package-relative imports, matches h-e1 style).

---

## M-1: Reuse Setup [Complexity: 5, Budget: 5]

**Applied**: Standard file copy, no new logic

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy + verify | Copy `duality_conversion.py`, `selective_scan.py`, `data_loader.py` from h-e1/code/ into h-m1/code/ unmodified; smoke-test imports |

---

## M-2: Random Init Baseline [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch init (Xavier/normal)

### API Signatures

```python
# h-m1/code/random_init.py
import torch
from torch import Tensor
from typing import Tuple

def random_init_ssm(
    d_model: int = 768,
    d_state: int = 64,
    seed: int = 42
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """Random SSM baseline, shape-matched to duality_init_ssm_from_attention."""
    ...
```

### Tensor Shapes

| Variable | Shape | Init |
|----------|-------|------|
| A | [d_model, d_state] | `randn / sqrt(d_state)` |
| B | [d_state, d_model] | Xavier uniform |
| C | [d_model, d_state] | Xavier uniform |
| D | [d_model] | zeros |
| dt | [d_model] | `ones * 0.1` |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | random_init_ssm | Implement with `torch.manual_seed(seed)`, `nn.init.xavier_uniform_` for B/C |

---

## M-3: Reconstruction Error Metric [Complexity: 8, Budget: 8]

**Applied**: MOHAWK Stage-1 alignment metric (Frobenius norm) + scipy paired t-test

### API Signatures

```python
# h-m1/code/reconstruction_error.py
from typing import List, Dict
import torch
from torch import Tensor
from scipy import stats

def compute_reconstruction_error(ssm_output: Tensor, attn_output: Tensor) -> float:
    """ssm_output, attn_output: [batch, seq_len, d_model] -> scalar Frobenius norm mean."""
    ...

def paired_stats(duality_errors: List[float], random_errors: List[float]) -> Dict[str, float]:
    """Paired t-test + Cohen's d. Returns:
    {mean_duality, mean_random, reduction_pct, p_value, cohens_d}
    """
    ...
```

### Pseudo-code

```
compute_reconstruction_error:
  diff = ssm_output - attn_output
  return torch.linalg.matrix_norm(diff, ord="fro").mean().item()

paired_stats:
  t_stat, p_value = stats.ttest_rel(random_errors, duality_errors)
  diff = [r - d for r, d in zip(random_errors, duality_errors)]
  cohens_d = mean(diff) / std(diff, ddof=1)
  reduction_pct = (mean_random - mean_duality) / mean_random * 100
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | error + stats | Both functions above in one file |

---

## M-4: Per-Layer Attention Reference [Complexity: 9, Budget: 8]

**Applied**: PyTorch forward hook (captures `BertSelfAttention.forward` output per-layer; `BertModel` only exposes `last_hidden_state`, not per-layer attention output)

### API Signatures

```python
# h-m1/code/attention_reference.py
from typing import List
import torch
from torch import Tensor
from transformers import BertModel

class AttentionOutputCapture:
    """Registers forward hooks on all 12 BertSelfAttention modules; captures outputs."""
    def __init__(self, bert: BertModel): ...
    def get_layer_output(self, layer_idx: int, input_ids: Tensor) -> Tensor:
        """Runs bert(input_ids) once, returns captured self-attn output for layer_idx.
        Output: [batch, seq_len, d_model]
        """
        ...
    def remove_hooks(self) -> None: ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| captured output | [batch, seq_len, 768] | raw `BertSelfAttention.forward()[0]`, pre-dense-projection |

### Pseudo-code

```
__init__:
  self._cache = {}
  for i, layer in enumerate(bert.encoder.layer):
      layer.attention.self.register_forward_hook(
          lambda mod, inp, out, i=i: self._cache.__setitem__(i, out[0])
      )

get_layer_output(layer_idx, input_ids):
  with torch.no_grad(): bert(input_ids)
  return self._cache[layer_idx]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | hook capture | Implement `AttentionOutputCapture` above |

---

## M-5: Comparative Evaluation Loop [Complexity: 15, Budget: 5]

**Applied**: Standard PyTorch eval loop, no_grad, per-layer/per-sample nesting

### API Signatures

```python
# h-m1/code/run_experiment.py (partial)
from typing import Dict, Any, List

def run_comparison(
    num_samples: int = 500,
    d_state: int = 64,
    device: str = "cuda"
) -> Dict[str, Any]:
    """Returns {"per_layer": {layer_idx: {"duality_errors": [...], "random_errors": [...]}}}"""
    ...
```

### Pseudo-code

```
run_comparison:
  bert = BertModel.from_pretrained("bert-base-uncased").eval().to(device)
  capture = AttentionOutputCapture(bert)
  samples = load_wikitext_samples(num_samples, min_length=64, max_length=512)
  per_layer = {i: {"duality_errors": [], "random_errors": []} for i in range(12)}

  for sample in samples:
    input_ids = sample["input_ids"].to(device)
    with torch.no_grad():
      embeddings = bert.embeddings(input_ids)
      _ = bert(input_ids)  # populates capture cache for all 12 layers
    for layer_idx in range(12):
      attn_out = capture.get_layer_output(layer_idx, input_ids)  # or read cache directly
      d_params = duality_init_ssm_from_attention(bert.encoder.layer[layer_idx].attention.self, d_state)
      r_params = random_init_ssm(768, d_state, seed=42)
      duality_out = selective_scan_ref(embeddings, *[p.to(device) for p in d_params])
      random_out  = selective_scan_ref(embeddings, *[p.to(device) for p in r_params])
      per_layer[layer_idx]["duality_errors"].append(compute_reconstruction_error(duality_out, attn_out))
      per_layer[layer_idx]["random_errors"].append(compute_reconstruction_error(random_out, attn_out))
  capture.remove_hooks()
  return {"per_layer": per_layer}
```

**Note**: single `bert(input_ids)` call per sample populates hook cache for all layers; avoid re-running BERT per-layer.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | comparison loop | Implement `run_comparison` per pseudo-code |

---

## M-6: Statistical Analysis Aggregation [Complexity: 10, Budget: 4]

**Applied**: Aggregation over `paired_stats` (M-3) across full flattened set + gate check

### API Signatures

```python
def aggregate_results(per_layer: Dict[int, Dict[str, List[float]]]) -> Dict[str, Any]:
    """Flattens all layers/samples, computes global + per-layer paired_stats, gate pass/fail."""
    ...
```

### Pseudo-code

```
aggregate_results:
  all_duality = flatten(per_layer[i]["duality_errors"] for i in per_layer)
  all_random  = flatten(per_layer[i]["random_errors"]  for i in per_layer)
  global_stats = paired_stats(all_duality, all_random)
  layer_stats = {i: paired_stats(v["duality_errors"], v["random_errors"]) for i, v in per_layer.items()}
  gate_pass = (global_stats["mean_duality"] < global_stats["mean_random"]) and (global_stats["reduction_pct"] > 0)
  return {**global_stats, "gate_pass": gate_pass, "per_layer_stats": layer_stats}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | aggregate | Implement `aggregate_results` above |

---

## M-7: Visualization Suite [Complexity: 8, Budget: 0 — folded into M-8]

No dedicated subtask budget; `generate_figures` implemented directly in run_experiment.py during M-8.

### API Signatures

```python
def generate_figures(results: Dict[str, Any], output_dir: str = "figures/") -> List[str]:
    """Bar chart (mean err), box plot (distributions), per-layer line/bar chart, histogram overlay.
    Returns list of saved file paths.
    """
    ...
```

---

## M-8: Full Pipeline Orchestration [Complexity: 11, Budget: 2]

**Applied**: Standard orchestration + JSON dump (matches h-e1 `main()` pattern)

### API Signatures

```python
def main() -> Dict[str, Any]:
    """run_comparison -> aggregate_results -> generate_figures -> save results/comparison_results.json"""
    ...
```

### Pseudo-code

```
main:
  raw = run_comparison(num_samples=500, d_state=64, device="cuda")
  results = aggregate_results(raw["per_layer"])
  figures = generate_figures(results, "figures/")
  json.dump(results excluding large arrays, "results/comparison_results.json")
  return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | generate_figures | Implement 4 required figures (bar, box, per-layer, histogram) |
| L-8-2 | main + orchestration | Wire run_comparison → aggregate_results → generate_figures → JSON save |

---

## Subtask Budget Summary

| Task | Subtasks Used |
|------|---------------|
| M-1 | 1 |
| M-2 | 1 |
| M-3 | 1 |
| M-4 | 1 |
| M-5 | 1 |
| M-6 | 1 |
| M-7 | 0 (folded into M-8) |
| M-8 | 2 (includes M-7 figures) |

**Total: 8 subtasks listed, but M-7 contributes 0 dedicated — actual distinct L-IDs = 8.**

**Correction to fit 6-subtask allocation budget**: Merge M-1+M-2 (setup+baseline, both trivial file writes) and M-6 into M-5's subtask, yielding:

| ID | Merged Scope |
|----|--------------|
| L-1-1 | Copy h-e1 files + implement `random_init_ssm` |
| L-3-1 | `compute_reconstruction_error` + `paired_stats` |
| L-4-1 | `AttentionOutputCapture` hook |
| L-5-1 | `run_comparison` loop |
| L-6-1 | `aggregate_results` |
| L-8-1 | `generate_figures` + `main` orchestration + JSON save |

**Final: 6 subtasks, matches allocated budget.**
