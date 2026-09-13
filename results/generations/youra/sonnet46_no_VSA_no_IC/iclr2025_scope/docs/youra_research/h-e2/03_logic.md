# Logic Design: h-e2
# Entropy-Guided Selective SWA Conversion of Llama-2-7B

---
hypothesis_id: h-e2
tier: LIGHT
date: 2026-08-22
author: yoon303@etri.re.kr
---

Applied: functional decomposition with pure-function tensor ops (stateless mask builders)
Applied: hook-based introspection pattern for attention mechanism verification

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — Serena returned no active project for h-e2/code/
**Findings**: All logic derived from 02c_experiment_brief.md pseudo-code and 03_architecture.md API signatures.

---

## Subtask L-E3-1: `make_sliding_window_causal_mask`

**Parent Epic**: E-3 (SWA Mask + Monkey-Patch)

**API Signature:**
```python
def make_sliding_window_causal_mask(
    seq_len: int,
    window_size: int,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    """
    Build additive causal sliding-window attention mask.

    Returns:
        mask: shape (seq_len, seq_len), dtype=dtype
              mask[i, j] = 0.0   if j in [max(0, i-window_size+1), i]
              mask[i, j] = -inf  otherwise
    """
```

**Tensor Shapes:**
- Input: scalars `seq_len`, `window_size`
- Output: `(seq_len, seq_len)` float tensor

**Pseudo-code:**
```python
def make_sliding_window_causal_mask(seq_len, window_size, dtype, device):
    mask = torch.full((seq_len, seq_len), float("-inf"), dtype=dtype, device=device)
    for i in range(seq_len):
        start = max(0, i - window_size + 1)
        mask[i, start : i + 1] = 0.0
    return mask
```

**Vectorized alternative (faster for large seq_len):**
```python
def make_sliding_window_causal_mask(seq_len, window_size, dtype, device):
    idx = torch.arange(seq_len, device=device)
    row = idx.unsqueeze(1)   # (seq_len, 1)
    col = idx.unsqueeze(0)   # (1, seq_len)
    # causal: col <= row; window: col >= row - window_size + 1
    attend = (col <= row) & (col >= row - window_size + 1)
    mask = torch.where(attend, torch.zeros(1, dtype=dtype, device=device),
                       torch.full((1,), float("-inf"), dtype=dtype, device=device))
    return mask  # (seq_len, seq_len)
```

**Edge cases:**
- `i < window_size`: start=0, attends all positions up to i (no clipping issue)
- `seq_len=1`: mask is `[[0.0]]`
- `window_size >= seq_len`: equivalent to full causal mask

---

## Subtask L-E3-2: `patch_layer_with_swa` and `apply_entropy_guided_swa`

**Parent Epic**: E-3 (SWA Mask + Monkey-Patch)

**API Signatures:**
```python
def patch_layer_with_swa(layer: LlamaDecoderLayer, window_size: int = 512) -> None:
    """
    Monkey-patches layer.self_attn.forward IN-PLACE with SWA mask injection.
    Original forward is captured via closure.
    No return value — modifies layer in place.
    """

def apply_entropy_guided_swa(
    model: LlamaForCausalLM,
    entropy_layer_ranking: list[int],
    k: int = 4,
    window_size: int = 512,
) -> list[int]:
    """
    Patches top-k entropy layers with SWA mask.
    Args:
        entropy_layer_ranking: layer indices sorted by entropy descending (from h-e1)
        k: number of layers to convert
    Returns:
        target_layers: list of k patched layer indices (for diagnostic logging + h-m2)
    """
```

**Pseudo-code:**
```python
def patch_layer_with_swa(layer, window_size=512):
    original_forward = layer.self_attn.forward  # capture in closure

    def swa_forward(hidden_states, attention_mask=None, position_ids=None, **kwargs):
        seq_len = hidden_states.shape[1]
        swa_mask = make_sliding_window_causal_mask(
            seq_len=seq_len,
            window_size=window_size,
            dtype=hidden_states.dtype,
            device=hidden_states.device,
        )
        # Shape: (1, 1, seq_len, seq_len) — broadcast over batch and heads
        return original_forward(
            hidden_states,
            attention_mask=swa_mask.unsqueeze(0).unsqueeze(0),
            position_ids=position_ids,
            **kwargs,
        )

    layer.self_attn.forward = swa_forward


def apply_entropy_guided_swa(model, entropy_layer_ranking, k=4, window_size=512):
    target_layers = entropy_layer_ranking[:k]  # top-k highest entropy indices
    print(f"Converting layers {target_layers} to SWA(w={window_size})")
    for layer_idx in target_layers:
        patch_layer_with_swa(model.model.layers[layer_idx], window_size=window_size)
    return target_layers
```

**Tensor Shapes:**
- `hidden_states`: `(batch=1, seq_len, hidden=4096)`
- `swa_mask` injected: `(1, 1, seq_len, seq_len)`
- Llama-2-7B eager attention expects additive mask of shape `(batch, 1, tgt_len, src_len)`

**Edge cases:**
- `k > len(entropy_layer_ranking)`: clip to available length (add assert)
- Model in eval mode: patches persist across forward calls (intended)
- Multiple calls: second patch wraps first — add guard `if hasattr(layer.self_attn, '_swa_patched')`

---

## Subtask L-E2-1: `compute_entropy_layer_ranking` — calibration forward pass

**Parent Epic**: E-2 (Entropy Layer Ranking)

**API Signature:**
```python
def compute_entropy_layer_ranking(
    model: LlamaForCausalLM,
    tokenizer: AutoTokenizer,
    calib_dataset,          # HuggingFace Dataset, validation split
    n_sequences: int = 100,
    max_seq_len: int = 512,
    device: str = "cuda",
) -> list[int]:
    """
    Returns 32 layer indices sorted by mean per-layer attention entropy descending.
    Uses head-MEAN pooling (not head-max — h-e1 lesson).
    Requires model loaded WITHOUT output_attentions in config;
    passes output_attentions=True at call time.
    """
```

**Tensor Shapes (Llama-2-7B):**
- `attentions` tuple: 32 elements, each `(batch=1, n_heads=32, seq_len, seq_len)`
- After head-mean pool per layer: `(seq_len, seq_len)`
- Entropy per row: scalar — `H[i] = -sum(p * log(p + eps))` where `p = softmax(attn_row)`
- Layer entropy: mean over all rows and all sequences → scalar

**Pseudo-code:**
```python
def compute_entropy_layer_ranking(model, tokenizer, calib_dataset, n_sequences=100,
                                   max_seq_len=512, device="cuda"):
    model.eval()
    num_layers = model.config.num_hidden_layers  # 32 for Llama-2-7B
    layer_entropy_sums = torch.zeros(num_layers, device=device)
    count = 0

    for i, sample in enumerate(calib_dataset):
        if i >= n_sequences:
            break
        text = sample["text"]
        if not text.strip():
            continue
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                           max_length=max_seq_len).to(device)
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # outputs.attentions: tuple of (1, 32, seq, seq) per layer
        for layer_idx, attn in enumerate(outputs.attentions):
            # attn: (1, n_heads, seq_len, seq_len)
            attn_mean = attn[0].mean(dim=0)  # head-mean → (seq_len, seq_len)
            # already softmaxed; compute entropy per row
            eps = 1e-9
            H = -(attn_mean * torch.log(attn_mean + eps)).sum(dim=-1)  # (seq_len,)
            layer_entropy_sums[layer_idx] += H.mean().item()
        count += 1

    layer_entropy_mean = layer_entropy_sums / count  # (num_layers,)
    ranking = torch.argsort(layer_entropy_mean, descending=True).tolist()
    return ranking  # list[int], len=32
```

---

## Subtask L-E2-2: entropy diagnostic output

**Parent Epic**: E-2 (Entropy Layer Ranking)

**Purpose:** Record per-layer mean entropy scores for visualization and h-m2 downstream use.

**API Signature:**
```python
def compute_entropy_layer_ranking_with_scores(
    model, tokenizer, calib_dataset,
    n_sequences: int = 100,
    max_seq_len: int = 512,
    device: str = "cuda",
) -> tuple[list[int], list[float]]:
    """
    Returns:
        ranking: list[int] — layer indices sorted entropy descending
        entropy_scores: list[float] — mean entropy per layer (index=layer_idx)
    """
```

**Extension of L-E2-1:** same loop, additionally return `layer_entropy_mean.tolist()` alongside ranking.

```python
    # After computing layer_entropy_mean:
    ranking = torch.argsort(layer_entropy_mean, descending=True).tolist()
    entropy_scores = layer_entropy_mean.tolist()  # len=32, index=layer_idx
    return ranking, entropy_scores
```

**Used by:** `run_experiment.py` to populate `results["entropy_scores"]` and `visualization.plot_entropy_scatter`.

---

## Subtask L-E5-1: `validate_swa_mask`

**Parent Epic**: E-5 (Mask Validation + Mechanism Verification)

**API Signature:**
```python
def validate_swa_mask(mask: torch.Tensor, window_size: int = 512) -> None:
    """
    Spot-checks 10 positions in mask for correct sliding-window causal structure.
    Args:
        mask: (seq_len, seq_len) additive float mask (0.0 / -inf)
    Raises:
        AssertionError if any position violates expected pattern
    """
```

**Pseudo-code:**
```python
def validate_swa_mask(mask, window_size=512):
    seq_len = mask.shape[0]
    check_positions = list(range(min(seq_len, 10)))

    for i in check_positions:
        attended = (mask[i] == 0.0).nonzero(as_tuple=True)[0]
        assert len(attended) > 0, f"Row {i}: no attended positions"
        assert attended.min().item() >= max(0, i - window_size + 1), \
            f"Row {i}: attended too far back (min={attended.min()}, expected>={max(0,i-window_size+1)})"
        assert attended.max().item() == i, \
            f"Row {i}: max attended position {attended.max()} != {i} (causal violation)"

    print(f"SWA mask validation PASSED (checked {len(check_positions)} positions)")
```

---

## Subtask L-E5-2: `verify_swa_mechanism`

**Parent Epic**: E-5 (Mask Validation + Mechanism Verification)

**API Signature:**
```python
def verify_swa_mechanism(
    model: LlamaForCausalLM,
    target_layers: list[int],
    window_size: int = 512,
    test_seq_len: int = 600,
) -> dict[int, int]:
    """
    Uses forward pre-hooks to verify SWA mask is correctly applied to target layers.
    Args:
        test_seq_len: must be > window_size to verify windowing at position test_seq_len-1
    Returns:
        {layer_idx: attended_count} — attended_count should == window_size for all target layers
    Raises:
        AssertionError if any layer has wrong attended count
    """
```

**Pseudo-code:**
```python
def verify_swa_mechanism(model, target_layers, window_size=512, test_seq_len=600):
    captured = {}
    hooks = []

    for idx in target_layers:
        def make_hook(layer_idx):
            def hook(module, args, kwargs):
                if "attention_mask" in kwargs and kwargs["attention_mask"] is not None:
                    mask = kwargs["attention_mask"]
                    # mask shape: (1, 1, seq_len, seq_len)
                    row = mask[0, 0, test_seq_len - 1]  # (seq_len,)
                    attended = (row == 0.0).sum().item()
                    captured[layer_idx] = attended
            return hook
        h = model.model.layers[idx].self_attn.register_forward_pre_hook(
            make_hook(idx), with_kwargs=True
        )
        hooks.append(h)

    dummy = torch.zeros(1, test_seq_len, dtype=torch.long,
                        device=next(model.parameters()).device)
    with torch.no_grad():
        model(dummy)

    for h in hooks:
        h.remove()

    for layer_idx, attended in captured.items():
        assert attended == window_size, (
            f"Layer {layer_idx}: expected {window_size} attended positions, "
            f"got {attended}. SWA mask not correctly applied!"
        )

    print(f"SWA mechanism VERIFIED: {len(target_layers)} layers correctly use w={window_size}")
    return captured
```

**Edge cases:**
- `test_seq_len <= window_size`: hook check would pass trivially (all positions attend) — assert `test_seq_len > window_size` at entry
- Hook may not fire if forward is a compiled function — ensure model is NOT `torch.compile`d

---

## Subtask L-E4-1: `compute_perplexity`

**Parent Epic**: E-4 (Perplexity Evaluation)

**API Signature:**
```python
def compute_perplexity(
    model: LlamaForCausalLM,
    tokenizer: AutoTokenizer,
    text: str,
    max_length: int = 4096,
    stride: int = 512,
) -> float:
    """
    Stride-chunked NLL perplexity (HuggingFace standard pattern).
    Discards trailing incomplete chunk.
    Uses torch.no_grad() throughout.
    Returns perplexity as float.
    """
```

**Tensor Shapes:**
- `input_ids`: `(1, seq_len)` where `seq_len` = total tokenized test length (~200K tokens)
- Per chunk: `(1, max_length)` = `(1, 4096)`
- `target_ids`: same shape, with `-100` masking non-target positions
- `nlls`: list of scalars (loss * trg_len per chunk)

**Pseudo-code:**
```python
def compute_perplexity(model, tokenizer, text, max_length=4096, stride=512):
    encodings = tokenizer(text, return_tensors="pt")
    input_ids = encodings.input_ids.to(model.device)
    seq_len = input_ids.shape[1]

    nlls = []
    prev_end_loc = 0

    for begin_loc in range(0, seq_len, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        trg_len = end_loc - prev_end_loc  # tokens newly entering the target window
        input_chunk = input_ids[:, begin_loc:end_loc]
        target_ids = input_chunk.clone()
        target_ids[:, :-trg_len] = -100  # mask context (non-new) tokens

        with torch.no_grad():
            outputs = model(input_chunk, labels=target_ids)
            # outputs.loss = mean NLL over non-masked positions

        nlls.append(outputs.loss * trg_len)
        prev_end_loc = end_loc
        if end_loc == seq_len:
            break

    total_nll = torch.stack(nlls).sum()
    ppl = torch.exp(total_nll / seq_len)
    return ppl.item()
```

**Notes:**
- `stride=512` matches `window_size=512` — fair comparison (SWA layers always see full window)
- Baseline and SWA evaluation MUST use identical call (same text, max_length, stride)
- `seq_len` is total token count, used as normalization denominator

---

## Summary

| Subtask ID | Parent | Function | Lines (est.) |
|-----------|--------|----------|-------------|
| L-E3-1 | E-3 | `make_sliding_window_causal_mask` | ~15 |
| L-E3-2 | E-3 | `patch_layer_with_swa`, `apply_entropy_guided_swa` | ~30 |
| L-E2-1 | E-2 | `compute_entropy_layer_ranking` | ~35 |
| L-E2-2 | E-2 | entropy scores diagnostic extension | ~10 |
| L-E5-1 | E-5 | `validate_swa_mask` | ~20 |
| L-E5-2 | E-5 | `verify_swa_mechanism` | ~35 |
| L-E4-1 | E-4 | `compute_perplexity` | ~25 |

Total: 7 subtasks ✓ (within logic budget)
