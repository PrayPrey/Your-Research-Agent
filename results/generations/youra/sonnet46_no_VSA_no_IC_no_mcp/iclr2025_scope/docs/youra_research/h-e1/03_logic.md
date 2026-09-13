# Logic Design: H-E1
## Query-Aware KV Eviction — API Signatures, Tensor Shapes, Pseudo-code

**Hypothesis:** H-E1  
**Date:** 2026-08-27  
**Budget:** 8 subtasks across A-5 (×4), A-6 (×2), A-3 (×2)

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase to analyze. `get_symbols_overview("src/")` returned no results (directory does not exist). All APIs designed from scratch based on SnapKV (arXiv:2404.14469), H2O (NeurIPS 2023), and HuggingFace transformers `past_key_values` API.

**Applied: SnapKV prefill-observation windowed attention pattern**
**Applied: HuggingFace past_key_values gather-based eviction pattern**
**Applied: Bootstrap CI resampling pattern for LLM evaluation**

---

## Notation

- `B` = batch size = 1 (PoC, single example at a time)
- `H` = attention heads = 32 (LLaMA-2-7B)
- `S` = full prefill sequence length (≤ 4096 after truncation)
- `K` = retained KV positions = `int(S × 0.5)` at 50% retention
- `D` = head dimension = 128 (hidden_dim 4096 / 32 heads)
- `L` = number of transformer layers = 32

---

## A-3: KV Eviction + Verification

### L-3-1: `apply_kv_eviction`

```python
def apply_kv_eviction(
    past_kv: tuple[tuple[torch.Tensor, torch.Tensor], ...],
    scores: list[torch.Tensor],
    retention_ratio: float = 0.5,
) -> tuple[tuple[torch.Tensor, torch.Tensor], ...]:
    """
    Evict bottom (1 - retention_ratio) KV positions per head per layer.

    Args:
        past_kv: Tuple of L tuples; each is (k, v) with shape (B, H, S, D)
        scores:  List of L tensors, each shape (B, H, S) — importance per position
        retention_ratio: Fraction of KV positions to keep (0.5 = keep top 50%)

    Returns:
        Evicted past_kv — same structure, shape (B, H, K, D) per layer
        where K = int(S * retention_ratio)
    """
```

**Tensor shape trace (per layer `l`):**
```
k_cache: (B=1, H=32, S, D=128)
v_cache: (B=1, H=32, S, D=128)
scores[l]: (B=1, H=32, S)

keep_n = int(S * 0.5)

# topk over last dim (position axis)
topk_indices: (B=1, H=32, K)           ← scores.topk(keep_n, dim=-1).indices
topk_sorted:  (B=1, H=32, K)           ← topk_indices.sort(dim=-1).values

# expand for gather
idx_k: (B=1, H=32, K, D=128)           ← topk_sorted.unsqueeze(-1).expand(-1,-1,-1,D)
k_retained: (B=1, H=32, K, D=128)      ← k_cache.gather(dim=2, index=idx_k)
v_retained: (B=1, H=32, K, D=128)      ← v_cache.gather(dim=2, index=idx_k)
```

**Pseudo-code:**
```python
evicted_kv = []
for l, (k, v) in enumerate(past_kv):
    S = k.shape[2]
    keep_n = int(S * retention_ratio)
    topk_idx = scores[l].topk(keep_n, dim=-1).indices          # (B, H, K)
    topk_idx = topk_idx.sort(dim=-1).values                    # sort preserves position order
    idx = topk_idx.unsqueeze(-1).expand(-1, -1, -1, k.shape[-1])  # (B, H, K, D)
    evicted_kv.append((k.gather(2, idx), v.gather(2, idx)))
return tuple(evicted_kv)
```

**Key pitfall:** `expand` not `repeat` — zero memory overhead. Sort after topk preserves causal order (important for positional embeddings).

---

### L-3-2: `verify_mechanism_activated`

```python
def verify_mechanism_activated(
    kv_before: tuple[tuple[torch.Tensor, torch.Tensor], ...],
    kv_after: tuple[tuple[torch.Tensor, torch.Tensor], ...],
    results_m1: dict,   # {"macro_f1": float, ...}
    results_m0: dict,   # {"macro_f1": float, ...}
    retention_ratio: float = 0.5,
) -> tuple[bool, dict[str, bool]]:
    """
    Verify KV eviction actually activated (shape reduced, F1 non-zero, M1 differs from M0).

    Returns:
        (all_pass: bool, indicators: dict of check_name -> bool)

    Raises:
        RuntimeError if any indicator fails
    """
```

**Indicators checked:**
```python
layer0_k_before = kv_before[0][0]   # (B, H, S_full, D)
layer0_k_after  = kv_after[0][0]    # (B, H, K, D)
expected_K = int(layer0_k_before.shape[2] * retention_ratio)

indicators = {
    "shape_changed":        layer0_k_after.shape[2] == expected_K,
    "shape_reduced":        layer0_k_after.shape[2] < layer0_k_before.shape[2],
    "m1_non_zero":          results_m1["macro_f1"] > 0,
    "m1_differs_from_m0":  abs(results_m1["macro_f1"] - results_m0["macro_f1"]) > 0.1,
}
```

**Log message on success:**
```
✅ Mechanism verified: KV reduced {S_full} → {K} per head per layer
```

---

## A-5: Experiment Runner

### L-5-1: `ExperimentRunner.run_all`

```python
class ExperimentRunner:
    def run_all(
        self,
        config: ExperimentConfig,
    ) -> dict:
        """
        Outer loop: load model once, iterate method × task × example.

        Returns:
            results: {
                "M0": {"narrativeqa": [f1, ...], "hotpotqa": [...], ...},
                "M1": {...},
                "M2": {...},
                "M6": {...},
            }
        """
```

**Pseudo-code:**
```python
model, tokenizer = load_model(config)   # single load, FP16
results = {m: {t: [] for t in config.tasks} for m in config.methods}

for method in config.methods:           # ["M0", "M1", "M2", "M6"]
    for task in config.tasks:           # ["narrativeqa", ...]
        examples = load_longbench(task, config.examples_per_task, config.seed)
        for ex in tqdm(examples):
            pred = run_single_example(ex["context"], ex["input"], method, model, tokenizer, config)
            f1 = compute_f1(pred, ex["answers"], task)
            results[method][task].append(f1)

return results
```

**Key constraint:** Model loaded once (not per method) — `past_key_values` is generated fresh per example via a new forward pass. No state persists between examples.

---

### L-5-2: `run_single_example`

```python
def run_single_example(
    context: str,
    question: str,
    method: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    config: ExperimentConfig,
) -> str:
    """
    Full pipeline for one example: tokenize → prefill → score → evict → generate → decode.

    Returns:
        prediction: str — decoded model output (answer)
    """
```

**Pipeline with tensor shapes:**
```
1. prompt = format_chat_template(context, question)   # str
2. input_ids: (1, S) ← tokenize + left-truncate to 4096

3. PREFILL:
   need_attn = (method != "M6")
   outputs = model.forward(
       input_ids,
       output_attentions=need_attn,   # False for M6 — saves memory
       use_cache=True,
   )
   past_kv: L × (B=1, H=32, S, D=128)
   attn_weights: L × (B=1, H=32, S, S)  # None if need_attn=False

4. SCORE:
   scores = dispatch_score_fn(method, attn_weights, past_kv, S, config)
   # scores: list of L tensors, each (B=1, H=32, S)
   # M0: no scores needed (retention_ratio=1.0, skip eviction)

5. EVICT (skip for M0):
   evicted_kv = apply_kv_eviction(past_kv, scores, config.retention_ratio)
   # evicted_kv: L × (B=1, H=32, K, D=128)  K = int(S*0.5)

6. GENERATE:
   # CRITICAL: input_ids for generate must be the LAST token only
   # (past_key_values already contains all prior context)
   continuation_id: (1, 1) ← input_ids[:, -1:]
   generated = model.generate(
       continuation_id,
       past_key_values=evicted_kv if method != "M0" else past_kv,
       max_new_tokens=config.max_new_tokens,   # 50
       do_sample=False,                         # greedy
   )
   # generated: (1, 1 + max_new_tokens)

7. DECODE:
   new_tokens = generated[0, 1:]   # skip the continuation seed token
   prediction = tokenizer.decode(new_tokens, skip_special_tokens=True)
```

**Key pitfall:** Pass `input_ids[:, -1:]` (shape `(1,1)`) to `generate()`, not full `input_ids` — the full context is already in `past_key_values`. Passing full prompt again duplicates it.

---

### L-5-3: `dispatch_score_fn`

```python
def dispatch_score_fn(
    method: str,
    attn_weights: list[torch.Tensor] | None,
    past_kv: tuple,
    seq_len: int,
    config: ExperimentConfig,
) -> list[torch.Tensor] | None:
    """
    Route to correct score function per method.

    Returns:
        scores: list of L tensors (B, H, S), or None for M0
    """
```

**Routing table:**
```python
if method == "M0":
    return None   # no eviction; run_single_example skips apply_kv_eviction

elif method == "M1":
    # attn_weights: list[L × (B, H, S, S)]
    return [compute_kv_scores_M1(attn_weights[l], config.observation_window)
            for l in range(len(attn_weights))]

elif method == "M2":
    return [compute_kv_scores_M2(attn_weights[l])
            for l in range(len(attn_weights))]

elif method == "M6":
    # StreamingLLM: positional selection — no attn_weights needed
    # attn_weights is None here (prefill called with output_attentions=False)
    return [compute_kv_scores_M6(seq_len, config.retention_ratio, config.streaming_sink_size)
            for _ in range(32)]   # same positional mask for all layers
```

**M6 score function (positional, no attention):**
```python
def compute_kv_scores_M6(seq_len, retention_ratio, sink_size=4):
    keep_n = int(seq_len * retention_ratio)
    # Scores: 1.0 for sinks + last (keep_n - sink_size) positions; 0.0 elsewhere
    scores = torch.zeros(1, 1, seq_len)   # (1, 1, S) — broadcast over H
    scores[:, :, :sink_size] = 1.0
    recent_start = max(sink_size, seq_len - (keep_n - sink_size))
    scores[:, :, recent_start:] = 1.0
    return scores.expand(1, 32, seq_len)   # (B=1, H=32, S)
```

---

### L-5-4: Attention Weight Extraction from Prefill

```python
# Inside run_single_example, after model.forward():
outputs = model.forward(input_ids, output_attentions=True, use_cache=True)

# outputs.attentions: tuple of L tensors
# Each: (B=1, H=32, S, S)  — full prefill attention matrix
# NOTE: LLaMA-2 uses causal mask; attn_weights[l][:, :, i, j]=0 for j>i
# For M1: only need attn_weights[:, :, -W:, :] — last W rows
# For M2: sum over dim=2 (query axis)

# Shape check (assert in debug mode):
assert outputs.attentions[0].shape == (1, 32, seq_len, seq_len), \
    f"Unexpected attn shape: {outputs.attentions[0].shape}"

attn_weights = list(outputs.attentions)   # list of L=32 tensors
past_kv = outputs.past_key_values         # tuple of L=32 (k, v) pairs
```

**Memory note:** `output_attentions=True` materializes L×(B×H×S×S) tensors. At S=4096, L=32, H=32: 32×1×32×4096×4096×2 bytes ≈ 32GB — **too large in FP32**. Use `.to(torch.float16)` or process immediately and free:
```python
# Free attn weights immediately after scoring to avoid OOM
scores = dispatch_score_fn(method, attn_weights, ...)
del attn_weights   # free before generate()
torch.cuda.empty_cache()
```

**Alternative (memory-safe):** Use hooks to capture attention per layer during forward, process and discard immediately.

---

## A-6: Results + Figures

### L-6-1: `ResultsAggregator.compute_gate_check`

```python
@dataclass
class GateResult:
    m1_macro_f1: float
    m2_macro_f1: float
    delta_f1: float                # M1 - M2
    bootstrap_ci_lower: float      # 2.5th percentile of delta distribution
    bootstrap_ci_upper: float      # 97.5th percentile
    gate_pass: bool                # delta >= 2.0 AND ci_lower > 0

def compute_gate_check(
    per_method_results: dict,      # {method: {task: [f1_per_example]}}
    n_bootstrap: int = 1000,
    seed: int = 42,
    gate_threshold: float = 2.0,
) -> GateResult:
```

**Bootstrap CI pseudo-code:**
```python
# Combine 400 examples (100/task × 4 tasks) into paired arrays
m1_f1s = np.array([f1 for task in tasks for f1 in per_method_results["M1"][task]])
m2_f1s = np.array([f1 for task in tasks for f1 in per_method_results["M2"][task]])
# m1_f1s, m2_f1s: shape (400,)

rng = np.random.default_rng(seed)
bootstrap_deltas = []
for _ in range(n_bootstrap):
    idx = rng.integers(0, 400, size=400)      # resample with replacement
    m1_boot = m1_f1s[idx].reshape(4, 100).mean(axis=1).mean()  # macro-avg
    m2_boot = m2_f1s[idx].reshape(4, 100).mean(axis=1).mean()
    bootstrap_deltas.append(m1_boot - m2_boot)

ci_lower = np.percentile(bootstrap_deltas, 2.5)
ci_upper = np.percentile(bootstrap_deltas, 97.5)
delta = m1_f1s.reshape(4,100).mean(axis=1).mean() - m2_f1s.reshape(4,100).mean(axis=1).mean()
gate_pass = (delta >= gate_threshold) and (ci_lower > 0)
```

---

### L-6-2: `FigureGenerator.generate_all`

```python
def generate_all(
    results: dict,                  # {method: {task: [f1_per_example]}}
    gate_result: GateResult,
    bootstrap_deltas: list[float],  # from compute_gate_check
    output_dir: str = "h-e1/figures",
) -> None:
    """Generate all 4 mandatory figures. Save as PNG to output_dir."""
```

**Figure specifications:**

| Fig | File | Type | X-axis | Y-axis | Notes |
|-----|------|------|--------|--------|-------|
| 1 | `fig1_macro_f1_comparison.png` | Bar chart | Method (M0,M1,M2,M6) | Macro-avg F1 | 95% CI error bars from bootstrap |
| 2 | `fig2_pertask_f1.png` | Grouped bar | Task (4 tasks) | F1 | Grouped by method (M0,M1,M2) |
| 3 | `fig3_bootstrap_delta.png` | Histogram | Delta F1 (M1−M2) | Count | Vertical lines at 0 and 2.0 |
| 4 | `fig4_score_heatmap.png` | Heatmap | Position (0..S) | Example (5 samples) | Side-by-side M1 vs M2 scores, layer 0 |

**Figure 4 data extraction:**
```python
# For 5 spot-check examples, during inference store:
# m1_scores_example[i]: shape (H=32, S) — mean over heads for visualization
# Heatmap shows mean-over-heads score per position
spot_check_m1 = scores_m1[0].mean(dim=1).cpu().numpy()  # (S,) for layer 0, mean over H
spot_check_m2 = scores_m2[0].mean(dim=1).cpu().numpy()  # (S,)
# Normalize per-example for visual clarity
```
