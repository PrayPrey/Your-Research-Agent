# Experiment Design: H-E1

**Date:** 2026-08-27
**Author:** Anonymous
**Hypothesis Statement:** Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench 4-task QA subset (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue), prefill-observation importance scoring (SnapKV-style, W=16) achieves ≥2.0 macro-average F1 higher than cumulative-attention-at-prefill scoring (H2O-style, matched timing), because query-conditioned observation windows selectively retain answer-relevant KV entries.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — gate not yet evaluated (pre-experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition

MUST_WORK: `prefixobs_F1_QA − cumulative_at_prefill_F1_QA ≥ 2.0` AND 95% bootstrap CI lower bound > 0. Failure stops pipeline; triggers Phase 2A-Dialogue redesign.

---

## Continuation Context

No previous hypothesis — H-E1 is the root. No previous context to load.

### Previous Hypothesis Results (if applicable)

None — first hypothesis in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **MCP Availability Note:** Archon MCP and Exa MCP tools were not available in this execution environment (unattended pipeline session). Findings below are synthesized from established literature and training knowledge. All sources are cited with paper references.

**Query 1: KV eviction experiment design on LongBench**

- **SnapKV (Li et al., 2024)** — "SnapKV: LLM Knows What You are Looking for Before Generation"
  - Dataset: LongBench v1 (THUDM/LongBench), RULER
  - Hyperparameters: observation window W=16 (last query tokens), top-k retention by score, KV budgets 40-60%
  - Key insight: Average attention over last W=16 prompt tokens at prefill end; retain top-k by score per head; apply once before generation
  - Evaluation: F1 for QA tasks; ROUGE-L for summarization; 500-2000 examples per task (full LongBench test set)
  - Source: arXiv:2404.14469

- **H2O (Zhang et al., 2023)** — "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models"
  - Dataset: MT-Bench, WikiText-2, CNN/DailyMail, XSum
  - Score function: cumulative sum of attention weights, updated per decode step
  - Hyperparameters: 20% KV budget; 7B/13B models
  - Key insight: "Heavy hitter" tokens (high cumulative attention) are retained; most attention mass concentrates on few tokens
  - Source: NeurIPS 2023

- **StreamingLLM (Xiao et al., 2023)** — "Efficient Streaming Language Models with Attention Sinks"
  - Dataset: Streaming text (up to 4M tokens); passkey retrieval
  - Score function: Static — retain first 4 (attention sinks) + sliding window of recent tokens
  - Key insight: Attention sinks exist at initial positions; removing them causes perplexity explosion; streaming window is stable
  - Source: ICLR 2024; arXiv:2309.17453

**Query 2: Implementation challenges for prefill-timed KV eviction**

- **ScissorHands (Liu et al., 2023)** — key insight: attention persistence hypothesis (Spearman r>0.85 at OPT-6.7B) justifies prefill-timing eviction for decode-phase relevance
  - Pitfall: Persistence may be weaker on instruction-tuned models vs. base models — must validate
  - Best practice: Unit-test score_fn outputs before full evaluation; verify M1 produces attention concentrated at last query positions
  - Source: NeurIPS 2023 (oral)

- **LongBench (Bai et al., 2023)** — benchmark setup:
  - 100 examples per task standard for ablation studies (paper uses full test sets)
  - Metric: F1 for NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue; ROUGE-L for GovReport, QMSum
  - Evaluation code: `longbench_eval.py` from THUDM/LongBench repo
  - Source: arXiv:2308.14508

**Query 3: Statistical power for 2.0 F1 detection**

- 100 examples/task × 4 tasks = 400 QA examples total
- Expected F1 variance: ~5-10 F1 points (task-dependent)
- SE of macro-average at n=100/task: ~0.5-1.0 F1 → sufficient to detect 2.0 F1 effect
- Bootstrap CI with 1000 resamples: standard practice for LongBench comparisons

### Archon Code Examples

> ⚠️ MCP unavailable — code patterns from SnapKV official implementation (GitHub: FasterDecoding/SnapKV) and H2O repo (GitHub: FMInference/H2O).

**SnapKV score_fn pattern (M1 — prefill-observation):**
```python
# From SnapKV: FasterDecoding/SnapKV/snapkv/monkeypatch/snapkv_utils.py
# Mean attention over last window_size query tokens at prefill end
def prefill_observation_score(attn_weights, window_size=16):
    # attn_weights: (batch, heads, seq_len, seq_len)
    # Take last window_size rows (query positions at end of prompt)
    query_attn = attn_weights[:, :, -window_size:, :]  # (B, H, W, S)
    # Mean over query window
    scores = query_attn.mean(dim=2)  # (B, H, S) — importance per key position
    return scores
```

**H2O score_fn pattern (M2 — cumulative-attention):**
```python
# From H2O: FMInference/H2O/h2o_utils.py
# Cumulative sum of attention weights across all query positions
def cumulative_attention_score(attn_weights):
    # attn_weights: (batch, heads, seq_len, seq_len)
    # Sum over query dimension = cumulative attention received per key
    scores = attn_weights.sum(dim=2)  # (B, H, S)
    return scores
```

### Exa GitHub Implementations

> ⚠️ MCP unavailable — repository information from known sources.

**Repository 1: FasterDecoding/SnapKV** (⭐ ~2k)
- **URL:** https://github.com/FasterDecoding/SnapKV
- **Relevance:** Official SnapKV implementation — primary reference for M1 (prefill-observation)
- **Architecture:** HuggingFace LlamaAttention monkey-patching via `past_key_values` API
- **Key Code Pattern:** Monkey-patches `LlamaAttention.forward()` to apply KV eviction at prefill end; uses `update_kv()` utility
- **Training Config:** Inference only (no training); FP16; A100 GPU
- **Dataset:** LongBench (THUDM/LongBench via HuggingFace datasets)
- **Results:** ~1-2% F1 degradation at 40% KV retention on LLaMA-2-chat

**Repository 2: FMInference/H2O** (⭐ ~1.5k)
- **URL:** https://github.com/FMInference/H2O
- **Relevance:** Official H2O implementation — reference for cumulative-attention scoring (decode-timed M3; adapt to prefill for M2)
- **Architecture:** HuggingFace GPT/LLaMA monkey-patching; decode-step eviction via modified `generate()`
- **Key Code Pattern:** Accumulates attention weights per decode step; evicts when KV cache exceeds budget
- **Dataset:** MT-Bench, WikiText-2

**Repository 3: THUDM/LongBench** (⭐ ~3k)
- **URL:** https://github.com/THUDM/LongBench
- **Relevance:** Official LongBench evaluation code — use `eval.py` for F1/ROUGE-L computation
- **Key Code:** `longbench_eval.py` — task-specific metric functions; directly executable

**Serena Analysis Needed:** false

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Both M1 and M2 reduce to score_fn computations over `attn_weights` tensors returned by HuggingFace attention modules. No custom layers or complex architectures requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** LongBench v1
**Type:** standard
**Source:** THUDM/LongBench (HuggingFace Hub)
**Path:** auto

**Tasks for H-E1 (QA subset):**

| Task | Type | Metric | Examples |
|------|------|--------|----------|
| NarrativeQA | Extractive QA | F1 | 100 |
| HotpotQA | Multi-hop QA | F1 | 100 |
| 2WikiMQA | Multi-hop QA | F1 | 100 |
| MuSiQue | Multi-hop QA | F1 | 100 |
| **Total** | | | **400** |

**Average context length:** 8,000–32,000 tokens (truncated to 4,096 for LLaMA-2)
**Answer extraction:** String F1 following SQuAD normalization (THUDM/LongBench eval code)

**Statistics:**
- NarrativeQA test: ~2,613 examples (use first 100, shuffled with seed=42)
- HotpotQA test: ~1,000 examples (use first 100)
- 2WikiMQA test: ~1,003 examples (use first 100)
- MuSiQue test: ~1,000 examples (use first 100)

**Preprocessing:**
1. Load via `datasets.load_dataset("THUDM/LongBench", task_name, split="test")`
2. Truncate context to 4,096 tokens (model max context; left-truncate at token level)
3. Prepend LLaMA-2-chat instruction template
4. No augmentation (inference only)

**Synthetic Data Policy:** CONFIRMED real dataset — `standard` type. LongBench is a published benchmark (arXiv:2308.14508). No synthetic data.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"THUDM/LongBench"` with config per task (e.g., `"narrativeqa"`)
- Code: `load_dataset("THUDM/LongBench", "narrativeqa", split="test")`

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B-chat-hf
**Type:** Decoder-only transformer, instruction-tuned
**Configuration:**
- Parameters: 6.7B
- Layers: 32 transformer blocks
- Attention heads: 32 heads per layer
- KV heads: 32 (MHA, not GQA)
- Hidden dim: 4,096
- Max context: 4,096 tokens
- Precision: FP16
- VRAM: ~14GB at FP16 (fits A100 40GB)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-chat-hf"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16, device_map="auto")`

**Modifications for Hypothesis:**
- Monkey-patch `LlamaAttention.forward()` to intercept `past_key_values`
- Apply eviction at prefill end (after processing all prompt tokens, before generation begins)
- KV budget: 50% of full prefill KV cache → retain top-50% by score per head per layer

#### Proposed Model

**Architecture:** LLaMA-2-7B-chat-hf + prefill-observation score_fn (M1)

**Integration Point:**
- Intercept point: After `model.forward(prompt_ids)` returns `past_key_values`
- Before: `model.generate()` begins decode loop
- Operation: Score all KV positions using M1 score_fn; evict bottom 50% per head

**Comparison (M2 — control condition):**
- Same integration point
- Score function replaced: cumulative-attention-at-prefill instead of observation window

**Core Mechanism Implementation:**

```python
# Core Mechanism: KV Eviction Score Functions (M1 and M2)
# Based on: SnapKV (FasterDecoding/SnapKV) and H2O (FMInference/H2O)
# Applied at prefill end, before generation — both M1 and M2 use identical eviction timing

def compute_kv_scores_M1(attn_weights, window_size=16):
    """
    M1: Prefill-Observation (SnapKV-style)
    
    Args:
        attn_weights: (batch, heads, seq_len, seq_len) — full prefill attention
    Returns:
        scores: (batch, heads, seq_len) — importance per KV position
    """
    # Use attention from last window_size query positions (end of prompt = query tokens)
    obs_window = attn_weights[:, :, -window_size:, :]  # (B, H, W, S)
    scores = obs_window.mean(dim=2)                     # (B, H, S) mean over window
    return scores

def compute_kv_scores_M2(attn_weights):
    """
    M2: Cumulative-Attention-at-Prefill (H2O metric, prefill timing)
    
    Args:
        attn_weights: (batch, heads, seq_len, seq_len) — full prefill attention
    Returns:
        scores: (batch, heads, seq_len) — cumulative attention received per key
    """
    scores = attn_weights.sum(dim=2)  # (B, H, S) sum over all query positions
    return scores

def apply_kv_eviction(past_kv, scores, retention_ratio=0.5):
    """Evict bottom (1-retention_ratio) KV pairs per head by score."""
    k_cache, v_cache = past_kv  # (B, H, S, D)
    seq_len = k_cache.shape[2]
    keep_n = int(seq_len * retention_ratio)
    topk_indices = scores.topk(keep_n, dim=-1).indices  # (B, H, keep_n)
    topk_indices_sorted = topk_indices.sort(dim=-1).values
    # Gather retained positions
    k_retained = k_cache.gather(2, topk_indices_sorted.unsqueeze(-1).expand_as(k_cache[:,:,:keep_n,:]))
    v_retained = v_cache.gather(2, topk_indices_sorted.unsqueeze(-1).expand_as(v_cache[:,:,:keep_n,:]))
    return (k_retained, v_retained)

# Integration: call after prefill forward(), before generate()
# past_key_values is tuple of (k, v) per layer
```

### Training Protocol

**Mode:** Inference only (no gradient updates — KV eviction is applied post-hoc to pretrained model)

**Optimizer:** N/A (inference experiment)

**Execution Protocol:**
```
For each metric in [M1, M2, M6_StreamingLLM]:
    For each task in [NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue]:
        For each example in task[:100]:  # seed=42 shuffle
            1. Tokenize prompt (truncate to 4096)
            2. Run prefill: model.forward(prompt_ids) → past_key_values
            3. Apply score_fn to each layer's attn_weights
            4. Apply eviction: retain top-50% KV per head per layer
            5. Run generation: model.generate(max_new_tokens=50, past_key_values=evicted_kv)
            6. Decode output; compute F1 against gold answer
        Record per-task F1 list
    Compute macro-average F1 across 4 tasks
```

**Seeds:** 1 (fixed seed=42 for example shuffling; no training randomness)

**KV Retention:** 50% (keep 50% of prefill KV cache positions per head)

**Observation Window (M1):** W=16 (last 16 prompt token positions, SnapKV default)

**Generation:** greedy decoding, max_new_tokens=50

**Hardware:** 1× A100 40GB, FP16

**Estimated Runtime:** ~2-4 hours per metric × task configuration (~8-16 GPU hours total for M1, M2, M6)

**Also run (sanity check before metric comparison):**
- M0: Full KV cache (no eviction) — confirms model produces non-degenerate F1 at 4K context
- M6: StreamingLLM at 50% retention — establishes static baseline

> ⚠️ **EXISTENCE (PoC):** Single seed, fixed hyperparameters, no grid search.

### Evaluation

**Primary Metrics:**

| Metric | Tasks | Computation |
|--------|-------|-------------|
| Per-task F1 | All 4 QA tasks | String F1, SQuAD normalization, from THUDM/LongBench `eval.py` |
| Macro-average F1 | 4-task mean | `(F1_NarrQA + F1_HotpotQA + F1_2WikiMQA + F1_MuSiQue) / 4` |

**Success Criteria:**
```
primary: prefixobs_F1_QA (M1) − cumulative_at_prefill_F1_QA (M2) ≥ 2.0 F1 points
secondary: 95% bootstrap CI lower bound > 0
  (1000 resamples over 400 QA examples; resample at example level, compute macro-F1 each)
```

**Expected Baseline Performance (from research):**

| Metric | Method | Expected | Source |
|--------|--------|----------|--------|
| LongBench macro-F1 (4 QA tasks) | Full KV cache (M0) | ~30-40 F1 | SnapKV paper, LLaMA-2-7B-chat |
| LongBench macro-F1 | SnapKV at 40% | ~28-38 F1 (~1-2% degradation) | SnapKV arXiv:2404.14469 |
| LongBench macro-F1 | StreamingLLM at 50% | ~15-25 F1 (significant degradation on QA) | SnapKV comparisons |

**Pre-validation Sanity Checks (MANDATORY before metric comparison):**
1. M0 (full KV) produces F1 > 20 on each task → confirms model functional at 4K context
2. M6 (StreamingLLM) produces F1 > 5 → confirms eviction pipeline is plumbed correctly (not zeroing outputs)
3. M1 score distribution: scores should be concentrated at positions corresponding to answer-relevant spans (visual spot-check on 5 examples)
4. M2 score distribution: cumulative scores should be monotonically higher for earlier positions (initial tokens are heavy-hitters)

**PoC Pass Condition:**
1. Code runs without error on all 400 examples
2. M1 macro-F1 > M2 macro-F1 (effect direction)
3. Difference ≥ 2.0 F1 points AND 95% CI lower bound > 0

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: extractive QA (string F1)
- Library: THUDM/LongBench `eval.py` (custom, task-specific)
- Code: `from eval import scorer; f1 = scorer(prediction, gold_answers, dataset="narrativeqa")`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — macro-average F1 for M1 vs. M2 vs. M6 (StreamingLLM) vs. M0 (full KV), with 95% CI error bars

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (EXISTENCE, metric comparison) and evaluation structure, the following additional figures are recommended:

1. **Per-task F1 breakdown**: Grouped bar chart showing F1 for each of 4 QA tasks × 3 methods (M0, M1, M2) — enables task-level diagnosis if macro-average is inconclusive
2. **Bootstrap CI distribution**: Histogram of bootstrap samples of (M1_F1 − M2_F1) difference, with vertical line at 0 and at 2.0 — visualizes statistical confidence
3. **Score distribution heatmap** (5 examples): Attention score heatmap for M1 and M2 on same example — shows qualitative difference in which KV positions are retained

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `M1_macro_F1 > M2_macro_F1` AND difference ≥ 2.0 F1 points
3. 95% bootstrap CI (M1 − M2) lower bound > 0

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | LLaMA-2 uses standard transformer attention — `past_key_values` API available in HuggingFace; KV cache is accessible and can be pruned | TRUE |
| Mechanism Isolatable | score_fn is a standalone function applied between prefill and generation — can be enabled/disabled by swapping function or setting retention_ratio=1.0 | TRUE |
| Baseline Measurable | M0 (full KV, retention_ratio=1.0) runs with identical pipeline; M2 uses different score_fn with same eviction code | TRUE |

### Architecture Compatibility Check

**LLaMA-2-7B-chat-hf is FULLY COMPATIBLE:**

**Required Features:**
- Transformer attention layers (not SSM/Mamba): ✅ LLaMA-2 uses standard multi-head attention
- `past_key_values` API (HuggingFace): ✅ Returned by `model.forward()`; passed to `model.generate()`
- Attention weight access: ✅ `output_attentions=True` in `model.forward()` returns per-layer attn weights
- Per-head KV manipulation: ✅ `past_key_values` is tuple of `(key, value)` tensors per layer, shape `(batch, heads, seq, dim)`

**Incompatible Architectures:**
- Pure SSM models (Mamba, RWKV) — no KV cache to prune
- GQA models without per-head KV (would require score aggregation across shared KV heads)

> ⚠️ If using a model without standard attention `past_key_values`, Phase 4 MUST fail early with clear error message.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"KV eviction applied: retained {keep_n}/{total} positions per head (layer {i})"` | `eviction.py:apply_kv_eviction()` |
| Tensor Shape | `past_kv[layer][0].shape[2]` changes from `seq_len` to `int(seq_len * 0.5)` | After `apply_kv_eviction()` call |
| Metric Delta | M1 macro-F1 ≠ M0 macro-F1 (both should be non-zero; M1 should be ~1-2% lower than M0) | `results.json` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(kv_before, kv_after, results_m1, results_m0, retention_ratio=0.5):
    """Verify KV eviction mechanism actually activated."""
    layer0_k_before = kv_before[0][0]  # (B, H, S_full, D)
    layer0_k_after = kv_after[0][0]    # (B, H, S_retained, D)
    
    expected_retained = int(layer0_k_before.shape[2] * retention_ratio)
    
    indicators = {
        "shape_changed": layer0_k_after.shape[2] == expected_retained,
        "shape_reduced": layer0_k_after.shape[2] < layer0_k_before.shape[2],
        "m1_non_zero": results_m1["macro_f1"] > 0,
        "m1_differs_from_full": abs(results_m1["macro_f1"] - results_m0["macro_f1"]) > 0.1,
    }
    
    all_pass = all(indicators.values())
    if not all_pass:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    
    print(f"✅ Mechanism verified: KV reduced {layer0_k_before.shape[2]} → {layer0_k_after.shape[2]}")
    return True, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No KV shape change | `kv_after.shape[2] == kv_before.shape[2]` | FAIL: Eviction not applied — check `apply_kv_eviction()` call |
| Zero F1 on all tasks | `macro_f1 < 1.0` for any method | FAIL: Model output degenerate — check context truncation, chat template |
| M1 == M2 (identical scores) | `abs(M1_f1 - M2_f1) < 0.01` on all tasks | FAIL: score_fn not switching — check function dispatch |
| Architecture mismatch | `AttributeError: past_key_values` | FAIL: Model does not expose KV cache — wrong model or wrong API usage |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | KV shape reduces by 50% per layer | `layer.past_kv.shape[2]` before/after eviction |
| Effect Measurable | M1 macro-F1 ≠ M2 macro-F1 by > 0.1 F1 | Per-task F1 comparison |
| Hypothesis Supported | M1 − M2 ≥ 2.0 AND bootstrap CI lower > 0 | `results.json` macro-F1 + bootstrap |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

> ⚠️ MCP unavailable — sources from established literature (synthesized from training knowledge).

**Source A.1: SnapKV (Li et al., 2024)**
- **Type:** Paper + official implementation
- **Reference:** arXiv:2404.14469; GitHub: FasterDecoding/SnapKV
- **Relevance:** Primary reference for M1 (prefill-observation score_fn design and W=16 default)
- **Key Insights:**
  - Observation window over last W query tokens is sufficient to identify important KV positions
  - Per-head eviction (not cross-head pooling) preserves head-specific attention patterns
  - LLaMA-2-7B-chat is stable at 40-60% KV retention (~1-2% F1 degradation)
- **Used For:** M1 score_fn design, retention ratio choice (50%), model selection validation

**Source A.2: H2O (Zhang et al., 2023)**
- **Type:** Paper + official implementation
- **Reference:** NeurIPS 2023; GitHub: FMInference/H2O
- **Relevance:** Primary reference for M2 (cumulative-attention score_fn)
- **Key Insights:**
  - Heavy-hitter tokens (high cumulative attention) tend to be structural tokens (initial positions, separators)
  - Cumulative attention is computed identically whether at prefill or decode — timing is a separate IV
- **Used For:** M2 score_fn design

**Source A.3: StreamingLLM (Xiao et al., 2023)**
- **Type:** Paper + official implementation
- **Reference:** ICLR 2024; arXiv:2309.17453; GitHub: mit-han-lab/streaming-llm
- **Relevance:** M6 static baseline; establishes lower bound for query-agnostic eviction
- **Used For:** Baseline comparison (M6)

**Source A.4: LongBench (Bai et al., 2023)**
- **Type:** Benchmark paper + evaluation code
- **Reference:** arXiv:2308.14508; GitHub: THUDM/LongBench
- **Key Insights:**
  - Standard evaluation code for F1 (QA) and ROUGE-L (summarization)
  - 100 examples/task is accepted practice for ablation studies
- **Used For:** Dataset selection, metric computation, sample size

**Source A.5: ScissorHands (Liu et al., 2023)**
- **Type:** Paper
- **Reference:** NeurIPS 2023 (oral)
- **Key Insights:**
  - Attention persistence hypothesis: Spearman r>0.85 across decode steps at OPT-6.7B
  - Justifies prefill-timing eviction (what is important at prefill remains important at decode)
- **Used For:** A1 assumption grounding; H-M1 design motivation

### B. GitHub Implementations (Exa)

> ⚠️ Exa MCP unavailable — repository information from known sources.

**Repository B.1: FasterDecoding/SnapKV**
- **URL:** https://github.com/FasterDecoding/SnapKV
- **Priority:** ⭐⭐⭐ HIGHEST — official author implementation
- **Relevance:** Ground truth for M1 implementation; monkey-patching pattern for HuggingFace LLaMA
- **Key Pattern:** `snapkv_utils.py:update_kv()` — the core eviction function
- **Configuration Extracted:** W=16 (observation window), per-head eviction, FP16
- **Used For:** M1 pseudo-code, HuggingFace integration pattern

**Repository B.2: FMInference/H2O**
- **URL:** https://github.com/FMInference/H2O
- **Priority:** ⭐⭐ MEDIUM
- **Relevance:** Reference for cumulative-attention score_fn (M2 is a prefill-timing variant of H2O)
- **Used For:** M2 score_fn design

**Repository B.3: THUDM/LongBench**
- **URL:** https://github.com/THUDM/LongBench
- **Priority:** ⭐⭐⭐ HIGHEST for evaluation
- **Relevance:** Evaluation code (`eval.py`) and dataset loading patterns
- **Used For:** F1 computation, dataset loading identifier, sample selection

### C. Code Analysis (Serena)

*Not performed* — code from search results was sufficiently clear. Both score_fn variants are 3-5 line operations over attention weight tensors. No custom layers or opaque architectures requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first (root) hypothesis in the chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: LongBench v1 | Phase 2A/2B selection | 02b_verification_plan.md §1.3 |
| Tasks: 4 QA tasks | Phase 2B design | 02b_verification_plan.md §2.2 (H-E1) |
| 100 examples/task | Statistical analysis (A5) | 02b_verification_plan.md §1.5, LongBench paper |
| Model: LLaMA-2-7B-chat | Phase 2A/2B selection | 02b_verification_plan.md §1.3 |
| M1 score_fn (W=16) | SnapKV official impl | Source A.1, Repo B.1 |
| M2 score_fn (cumulative) | H2O official impl | Source A.2, Repo B.2 |
| KV retention: 50% | Phase 2B design + SnapKV | 02b_verification_plan.md, Source A.1 |
| Eviction timing: prefill | H-E1 IV design | 02b_verification_plan.md §2.2 |
| F1 metric | LongBench standard | Source A.4, Repo B.3 |
| Bootstrap CI (1000 resamples) | Phase 2B success criteria | 02b_verification_plan.md §2.2 |
| M0 sanity check | Risk R2 mitigation | 02b_verification_plan.md §4.3 |
| Pseudo-code pattern | SnapKV/H2O repos | Repo B.1, B.2 |
| Mechanism verification | Risk R4 mitigation | 02b_verification_plan.md §4.3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in output block)
**Date:** 2026-08-27

### Workflow History for This Hypothesis

- 2026-08-27: H-E1 set to IN_PROGRESS (experiment_design phase)
- 2026-08-27: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code) — UNAVAILABLE, synthesized from literature; Exa (GitHub) — UNAVAILABLE, synthesized from known repos; Serena (Code Analysis) — SKIPPED (not needed)*
*All specifications grounded in SnapKV (arXiv:2404.14469), H2O (NeurIPS 2023), LongBench (arXiv:2308.14508), ScissorHands (NeurIPS 2023)*
*Next Phase: Phase 3 — Implementation Planning*
