# 3. Methodology

Our experimental framework is designed to isolate the effect of token importance metric type on KV eviction performance. The core design principle is a unified codebase with a pluggable score_fn interface, so that all metric conditions share identical model loading, tokenization, eviction pipeline, generation, and evaluation code — with only the importance scoring function varying. This section describes the framework, the score function implementations, the eviction pipeline, and the DynamicCache incompatibility we discovered during implementation.

## 3.1 Experimental Framework

We implement all metric conditions within a single HuggingFace-based codebase using the following components:

- **Config:** `ExperimentConfig` dataclass specifying model, dataset, tasks, retention ratio, seed, and method identifier.
- **Runner:** `run_all()` iterates over methods and tasks; `run_single_example()` handles per-example inference, eviction, and F1 computation.
- **Score functions:** `score_M1()`, `score_M2()`, `score_M6()` — pluggable functions accepting attention weight tensors and returning per-token importance scores.
- **Eviction:** `apply_kv_eviction()` applies top-k selection and gather per attention head per layer; `verify_mechanism_activated()` checks shape reduction.
- **Data loader:** `load_task()` fetches LongBench examples from HuggingFace Hub.
- **Metrics:** `compute_f1()` implements SQuAD-style normalization, matching LongBench standard.
- **Aggregator:** `build_results_json()` produces a structured results.json with per-task and macro-average metrics.

The full KV (M0) condition serves as the baseline: it runs the identical pipeline with eviction disabled, verifying that the model, tokenizer, and F1 computation are correct before any eviction condition runs.

## 3.2 Score Function Implementations

We implement three metric conditions relevant to the h-e1 hypothesis:

**M1 — Prefill-Observation (SnapKV-style):**

At the end of the prefill phase, we capture the attention weight matrix for each layer and head. The importance score for KV position i is:

```
score_M1(i) = mean_{t in [T-W, T]} attn_weight(t, i)
```

where T is the last prefill token position, W=16 is the observation window size (SnapKV default), and attn_weight(t, i) is the attention weight from query token t to key position i. This computes the mean attention that the last W query tokens direct toward each KV position — identifying positions that are query-relevant at prefill end.

**M2 — Cumulative-Attention-at-Prefill (H2O-at-prefill):**

At the end of the prefill phase, importance scores are computed as:

```
score_M2(i) = sum_{t=0}^{T} attn_weight(t, i)
```

the cumulative sum of attention weights that all prefill query tokens have directed to position i. This is the H2O cumulative attention metric, applied at prefill timing rather than per decode step — isolating metric type from eviction timing.

**M6 — StreamingLLM (Static Baseline):**

Retains the first 4 attention sink tokens and the most recent tokens within a sliding window. No importance scoring; purely positional. This is the lower-bound baseline.

Both M1 and M2 are implemented as pure functions over attention weight tensors. Code review confirmed that the formulas match the pseudocode in the experiment brief, which in turn matches the SnapKV (M1) and H2O (M2) reference implementations.

## 3.3 KV Eviction Pipeline

The eviction pipeline applies to M1 and M2 after the prefill phase:

1. **Prefill forward pass:** Run the model on the full input with `output_attentions=True` to capture per-layer attention weights.
2. **Score computation:** Apply the chosen score_fn to obtain per-position importance scores for each attention head and layer.
3. **Top-k selection:** For each head h and layer l, select the top-k positions by importance score, where k = floor(retention_ratio × seq_len). At 50% retention with seq_len=4096, k=2048.
4. **Gather:** Collect the retained KV tensors using the top-k indices, producing tensors of shape [batch, heads, 2048, head_dim] for keys and values.
5. **Cache reconstruction:** Assemble the evicted KV tensors into a cache object for use during generation.
6. **Generation:** Run `model.generate()` with the evicted cache as `past_key_values`.

Steps 1-4 are mechanically correct. The shape verification log confirms that step 4 produces tensors of the correct dimension (2048/4096 per head per layer) for all 32 LLaMA-2 transformer layers. Step 5 is where the failure occurs.

## 3.4 Implementation Failure: DynamicCache Reconstruction

**The Problem:**

Our implementation of step 5 used the transformers DynamicCache constructor:

```python
evicted_cache = DynamicCache(ddp_cache_data=evicted_kv_tensors)
```

This constructor creates a DynamicCache object with the specified tensor data. However, transformers 5.x DynamicCache stores internal state beyond the raw (key, value) tuples — including sequence length bookkeeping and attention mask metadata that the generation loop depends on. Constructing DynamicCache from raw tensors populates the tensor content but leaves internal state in an inconsistent condition: the cache "knows" 0 tokens are cached (from initialization) while the tensor content corresponds to 2048 positions.

When `model.generate()` uses this cache as `past_key_values`, the attention mechanism references wrong positions. Position IDs and attention masks computed for the evicted cache reference the full 4096-position sequence, but the actual tensors contain only 2048 positions. The result is degenerate generation: the model produces empty strings or repetitive single-token outputs, yielding F1=0.00 regardless of actual answer content.

**Evidence of the Failure:**

The shape log from our experiment confirms:
```
Layer 0:  past_kv[0].shape = [1, 32, 2048, 128]  ✓ (reduced from 4096)
Layer 1:  past_kv[1].shape = [1, 32, 2048, 128]  ✓
...
Layer 31: past_kv[31].shape = [1, 32, 2048, 128] ✓
```

All shapes are correct. Yet M1 produces F1=0.00 on narrativeqa (M0 F1=0.09), hotpotqa (M0 F1=0.09), and 2wikimqa (M0 F1=0.11). The M0 condition, running the identical pipeline with eviction disabled (and therefore no DynamicCache reconstruction), produces coherent outputs at the expected F1 range. The DynamicCache reconstruction step is the only difference.

**Why This Was Not Caught Earlier:**

All prior KV eviction implementations avoid this failure by integrating eviction into the attention forward pass. SnapKV's `update_kv()` function, called inside LlamaAttention.forward(), modifies the key and value tensors before they are appended to the DynamicCache. The cache object is built incrementally through the standard `update()` method, which maintains internal consistency. Post-hoc reconstruction from external tensors is not the intended usage pattern and is not validated by the library.

## 3.5 Corrected Protocol: Forward-Pass Integration

The correct implementation approach, used by SnapKV's reference codebase [github.com/FasterDecoding/SnapKV] but **not yet validated in this pipeline** (experiment terminated before the fix could be tested), is:

1. **Override `LlamaAttention.forward()`:** Monkey-patch the attention module to intercept the key and value tensors after they are computed but before they are appended to past_key_values.
2. **Apply eviction within the forward pass:** Compute importance scores and apply top-k selection inside the overridden forward method, so the evicted tensors are appended to past_key_values through the standard `update()` path.
3. **Maintain cache consistency:** Because eviction happens through the standard update path, all internal DynamicCache bookkeeping is maintained automatically.

This approach requires replacing approximately 50 lines of the eviction.py module with a LlamaAttention override, leaving all other pipeline components unchanged. The score_fn implementations (M1, M2) can be reused without modification.

A pre-validation protocol should precede any full evaluation run: run 5 examples from one task, verify that F1 > 0.00 for all 5 before proceeding. This check would have identified the DynamicCache failure in approximately 3 minutes, avoiding a 30-minute degenerate run across 300 examples.
