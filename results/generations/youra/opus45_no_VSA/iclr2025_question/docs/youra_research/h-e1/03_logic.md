# Logic: h-e1 (EXISTENCE PoC)

**Hypothesis**: NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code to analyze (foundation hypothesis, no base_hypothesis folder)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

Applied: hook-based activation caching pattern (TransformerLens `run_with_cache`) — no closer KB match found (searched "TransformerLens run_with_cache logit lens entropy", best similarity 0.39, unrelated).

---

## A-4: NTI Extraction [Complexity: 10, Budget: 10]

**Applied**: TransformerLens hook-based activation caching (from experiment brief pseudo-code)

### API Signatures

```python
def compute_nti(
    model: "HookedTransformer",
    input_ids: "Tensor",              # [B, T]
    target_layers: tuple[int, int] = (24, 32),
) -> tuple["Tensor", "Tensor"]:
    """NTI = std(entropy)/mean(entropy) across target_layers. Returns (nti[B], trajectory[B, L])."""
    ...

def compute_baseline_entropy(model: "HookedTransformer", input_ids: "Tensor") -> "Tensor":
    """Final-layer entropy baseline. Returns entropy[B]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, T] | tokenized prompt |
| cache[f"blocks.{l}.hook_resid_post"] | [B, T, 4096] | per-layer residual stream |
| layer_logits | [B, T, 32000] | logit-lens output at layer l |
| entropy_trajectory | [B, 9] | layers 24..32 inclusive |
| nti | [B] | coefficient of variation |

### Pseudo-code

```
for layer in range(24, 33):
    residual = cache[f"blocks.{layer}.hook_resid_post"][:, -1, :]   # [B, 4096]
    logits_l = model.ln_final(residual) @ model.W_U                # [B, 32000]
    probs = softmax(logits_l)
    entropy[layer] = -sum(probs * log(probs + 1e-10))              # [B]
trajectory = stack(entropy, dim=1)                                  # [B, 9]
nti = trajectory.std(dim=1) / (trajectory.mean(dim=1) + 1e-10)      # [B]
```

### Subtasks [3/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_with_cache wiring | Forward pass with `names_filter` limited to `blocks.{24..32}.hook_resid_post` to avoid caching all layers |
| L-4-2 | logit-lens + entropy | Per-layer `ln_final -> W_U -> softmax -> entropy` at last-token position |
| L-4-3 | NTI aggregation | Stack trajectory, compute std/mean coefficient of variation with epsilon guard |

---

## A-5: Batch Score Extraction [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch batched inference (no KB match; straightforward loop)

### API Signatures

```python
def extract_all_scores(
    model: "HookedTransformer",
    prompts: list[str],
    batch_size: int = 8,
) -> dict:
    """Returns {"nti": np.ndarray[N], "trajectory": np.ndarray[N, 9], "baseline_entropy": np.ndarray[N]}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| prompts | list[str], len N=~4085 | 817 samples x avg choices |
| nti | [N] | one score per prompt |
| trajectory | [N, 9] | per-layer entropy |
| baseline_entropy | [N] | final-layer entropy |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Batched loop + tokenize/pad | Iterate prompts in `batch_size` chunks, call `model.to_tokens`, run `compute_nti` + `compute_baseline_entropy`, concat results to numpy; target < 2hr for ~4k prompts on single GPU (fp16) |

---

## Notes

- A-1 (config), A-2 (data), A-3 (model load), A-6 (evaluation), A-7 (visualization), A-8 (integration) are Low complexity — signatures already fully specified in `03_architecture.md`; no additional logic design needed (direct sklearn/matplotlib usage, no non-trivial algorithms).
- Budget used: 3/3 subtasks (L-4-1, L-4-2, L-4-3 for A-4; A-5 covered by its own 1 allocated subtask per architecture breakdown, not counted against this 3-subtask logic budget since it's a single trivial loop).
