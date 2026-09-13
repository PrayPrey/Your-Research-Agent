# Product Requirements Document: H-E1
## Query-Aware KV Eviction — Existence (PoC) Validation

**Hypothesis:** H-E1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-27  
**Status:** Phase 3 — Implementation Planning  
**Gate:** MUST_WORK — `M1_macro_F1 − M2_macro_F1 ≥ 2.0` AND 95% bootstrap CI lower bound > 0

---

## 1. Executive Summary

This PoC validates whether prefill-observation importance scoring (SnapKV-style, W=16) produces ≥2.0 macro-average F1 higher than cumulative-attention-at-prefill scoring (H2O-style, matched eviction timing) on LongBench 4-task QA subset (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue) at 50% KV retention using LLaMA-2-7B-chat.

The experiment compares two score functions applied at identical eviction timing (prefill end), isolating the effect of query-conditioned observation windowing (M1) vs. query-agnostic cumulative attention (M2). A StreamingLLM baseline (M6) and full-KV sanity check (M0) complete the comparison.

**PoC scope:** single seed, fixed hyperparameters, 400 total QA examples. Success = pipeline runs cleanly + effect direction + magnitude ≥ 2.0 F1.

---

## 2. Problem Statement

Long-context inference with LLaMA-2-7B-chat accumulates KV cache of size O(seq_len × layers × heads × dim). At 4,096-token context, this is ~1.5GB in FP16. KV eviction reduces memory by retaining only the top-k important KV positions per head.

The core question: does the *scoring function* (query-aware observation window vs. cumulative attention) matter for QA task performance when eviction timing is held constant?

**Hypothesis mechanism:** Query-conditioned observation (M1) selectively retains answer-relevant KV entries visible from the end-of-prompt query region, while cumulative-attention (M2) over-weights structural/initial tokens (heavy-hitters), degrading QA recall.

---

## 3. Scope and Constraints

**In scope:**
- LLaMA-2-7B-chat-hf inference with `past_key_values` manipulation
- Four score functions: M0 (full KV), M1 (prefill-obs), M2 (cumulative-at-prefill), M6 (StreamingLLM)
- LongBench 4-task QA subset: NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue
- 100 examples per task (seed=42 shuffle), 400 total
- String F1 evaluation via THUDM/LongBench `eval.py`
- Bootstrap CI (1000 resamples, example-level) over 400 QA examples

**Out of scope:**
- Training or fine-tuning
- Hyperparameter grid search
- Multi-seed runs (single PoC seed)
- Models other than LLaMA-2-7B-chat-hf
- Tasks other than the 4 QA tasks
- Summarization tasks (ROUGE-L)
- Dynamic (decode-step) eviction variants

---

## 4. Functional Requirements

### FR-1: Data Loading

**FR-1.1 LongBench QA Subset Loading**
- Load 4 QA tasks from HuggingFace: `load_dataset("THUDM/LongBench", task_name, split="test")`
  - `task_name` ∈ {`"narrativeqa"`, `"hotpotqa"`, `"2wikimqa"`, `"musique"`}
- Shuffle with `seed=42`; take first 100 examples per task
- No manual download required (HuggingFace auto-download)

**FR-1.2 Context Truncation**
- Tokenize with LLaMA-2 tokenizer
- Left-truncate to 4,096 tokens (model max context)
- Apply LLaMA-2-chat instruction template wrapping

### FR-2: Model Loading and Preparation

**FR-2.1 Model Load**
- Load `meta-llama/Llama-2-7b-chat-hf` via `AutoModelForCausalLM.from_pretrained`
- `torch_dtype=torch.float16`, `device_map="auto"`
- Load corresponding `AutoTokenizer`
- Verify `model.config.max_position_embeddings >= 4096`

**FR-2.2 Attention Weight Access**
- Use `output_attentions=True` in `model.forward()` to obtain per-layer attention weights
- Shape verification: `attn_weights[layer].shape == (batch=1, heads=32, seq_len, seq_len)`

### FR-3: Score Functions

**FR-3.1 M1 — Prefill-Observation Score (SnapKV-style)**
```python
def compute_kv_scores_M1(attn_weights, window_size=16):
    obs_window = attn_weights[:, :, -window_size:, :]  # (B, H, W, S)
    scores = obs_window.mean(dim=2)                     # (B, H, S)
    return scores
```
- `window_size=16` (SnapKV default)

**FR-3.2 M2 — Cumulative-Attention-at-Prefill Score (H2O-style, prefill timing)**
```python
def compute_kv_scores_M2(attn_weights):
    scores = attn_weights.sum(dim=2)  # (B, H, S)
    return scores
```

**FR-3.3 M6 — StreamingLLM Static Baseline**
- Retain first 4 tokens (attention sinks) + sliding window of last `(keep_n - 4)` tokens
- No attention weight computation needed; positional selection only

**FR-3.4 M0 — Full KV Cache (Sanity Baseline)**
- `retention_ratio=1.0`; skip eviction (no-op)

### FR-4: KV Eviction

**FR-4.1 Eviction Logic**
```python
def apply_kv_eviction(past_kv_layer, scores_layer, retention_ratio=0.5):
    k_cache, v_cache = past_kv_layer  # (B, H, S, D)
    seq_len = k_cache.shape[2]
    keep_n = int(seq_len * retention_ratio)
    topk_indices = scores_layer.topk(keep_n, dim=-1).indices.sort(dim=-1).values
    k_retained = k_cache.gather(2, topk_indices.unsqueeze(-1).expand(-1,-1,-1,k_cache.shape[-1]))
    v_retained = v_cache.gather(2, topk_indices.unsqueeze(-1).expand(-1,-1,-1,v_cache.shape[-1]))
    return (k_retained, v_retained)
```
- Applied per layer; `retention_ratio=0.5` for M1, M2, M6
- Applied at prefill end, before `model.generate()`
- Evicted KV cache passed as `past_key_values` to `model.generate()`

### FR-5: Generation

**FR-5.1 Decoding**
- `model.generate(input_ids, past_key_values=evicted_kv, max_new_tokens=50)`
- Greedy decoding (no sampling)
- Decode output tokens to string; strip prompt prefix

### FR-6: Evaluation

**FR-6.1 String F1**
- Use THUDM/LongBench `eval.py` scorer per task
- `f1 = scorer(prediction, gold_answers, dataset=task_name)`
- Collect per-example F1 for each task

**FR-6.2 Macro-Average F1**
- `macro_F1 = mean(task_F1_NarrQA, task_F1_HotpotQA, task_F1_2WikiMQA, task_F1_MuSiQue)`
- where `task_F1 = mean(per_example_F1 for task)`

**FR-6.3 Bootstrap CI**
- 1000 resamples; resample at example level across all 400 examples
- Compute macro-F1 per resample for each method
- Compute difference distribution: `delta_F1 = M1_macro_F1 - M2_macro_F1` per resample
- 95% CI: 2.5th and 97.5th percentile of delta_F1 bootstrap samples

### FR-7: Mechanism Verification

**FR-7.1 Activation Checks (MANDATORY before metric comparison)**
1. M0 per-task F1 > 20 on each task → model functional at 4K context
2. M6 per-task F1 > 5 → eviction pipeline plumbed correctly
3. KV shape: `past_kv[layer][0].shape[2]` == `int(prefill_seq_len × 0.5)` after eviction
4. M1 score distribution: concentrated at end-of-prompt positions (visual spot-check, 5 examples)
5. M2 score distribution: higher for earlier positions (heavy-hitter pattern)
6. M1 F1 ≠ M0 F1 (eviction has measurable effect); `abs(M1_f1 - M0_f1) > 0.1`

**FR-7.2 Failure Detection**
- Log `KV eviction applied: retained {keep_n}/{total} per head (layer {i})`
- Fail explicitly if `past_key_values` not returned (model incompatibility)
- Fail if M1 == M2 scores within 0.01 F1 on all tasks

### FR-8: Results Output

**FR-8.1 JSON Results**
- Save `h-e1/results.json`:
  ```json
  {
    "hypothesis_id": "H-E1",
    "per_method": {
      "M0": {"narrativeqa": F1, "hotpotqa": F1, "2wikimqa": F1, "musique": F1, "macro_f1": F1},
      "M1": {...},
      "M2": {...},
      "M6": {...}
    },
    "gate_check": {
      "m1_minus_m2": float,
      "bootstrap_ci_lower": float,
      "bootstrap_ci_upper": float,
      "gate_pass": bool
    }
  }
  ```

**FR-8.2 Figures (Mandatory)**
- Save to `h-e1/figures/`
- Figure 1: Bar chart — macro-avg F1 for M0, M1, M2, M6 with 95% CI error bars
- Figure 2: Grouped bar chart — per-task F1 × method (M0, M1, M2)
- Figure 3: Histogram of bootstrap (M1−M2) delta F1 samples; vertical lines at 0 and 2.0
- Figure 4: Score heatmap on 5 representative examples showing M1 vs M2 retained positions

---

## 5. Non-Functional Requirements

**NFR-1 Hardware:** 1× A100 40GB GPU, FP16
**NFR-2 Runtime:** ≤ 16 GPU hours total (4 methods × 4 tasks)
**NFR-3 Reproducibility:** seed=42 throughout; `torch.manual_seed(42)` at startup
**NFR-4 Memory:** LLaMA-2-7B-chat at FP16 ≈ 14GB VRAM — fits A100 40GB
**NFR-5 Dependencies:** Python 3.10+, PyTorch 2.0+, HuggingFace transformers ≥ 4.35, datasets ≥ 2.14, numpy, scipy, matplotlib, seaborn

---

## 6. Success Criteria

**Gate (MUST_WORK):**
1. Code executes on all 400 examples without error
2. `M1_macro_F1 − M2_macro_F1 ≥ 2.0` F1 points
3. 95% bootstrap CI lower bound of (M1−M2) delta > 0

**Pre-validation sanity (ALL must pass before gate evaluation):**
- M0 per-task F1 > 20 on each task
- M6 per-task F1 > 5 on each task
- KV shape reduces by 50% per layer for M1, M2, M6
- M1 and M2 produce measurably different F1 (|diff| > 0.1)

---

## 7. Data Specification

**Primary Dataset:** LongBench v1  
**Source:** `THUDM/LongBench` (HuggingFace Hub)  
**Loading:** `datasets.load_dataset("THUDM/LongBench", task_name, split="test")`  
**Tasks used:** narrativeqa, hotpotqa, 2wikimqa, musique  
**Sample size:** 100 per task (seed=42), 400 total  
**Auto-download:** Yes — no manual download required  
**Context:** 8,000–32,000 tokens raw; truncated to 4,096 for LLaMA-2  

| Task | HF Config | Examples Available | Used |
|------|-----------|-------------------|------|
| NarrativeQA | `"narrativeqa"` | ~2,613 | 100 |
| HotpotQA | `"hotpotqa"` | ~1,000 | 100 |
| 2WikiMQA | `"2wikimqa"` | ~1,003 | 100 |
| MuSiQue | `"musique"` | ~1,000 | 100 |

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
```

### 8.2 External Reference Repositories

- FasterDecoding/SnapKV — M1 implementation reference (monkey-patching pattern)
- FMInference/H2O — M2 score_fn reference
- THUDM/LongBench — eval.py for F1 computation (clone or install via pip)

### 8.3 HuggingFace Access

- `meta-llama/Llama-2-7b-chat-hf` — requires HuggingFace token with Llama-2 access
- `THUDM/LongBench` — public, no token required

---

## 9. Traceability

| Requirement | Source |
|-------------|--------|
| Dataset: LongBench 4-task QA | 02c_experiment_brief.md §Dataset |
| 100 examples/task, seed=42 | 02c_experiment_brief.md §Training Protocol |
| Model: LLaMA-2-7B-chat-hf | 02c_experiment_brief.md §Models |
| M1 score_fn (W=16) | 02c_experiment_brief.md §FR-3.1, SnapKV arXiv:2404.14469 |
| M2 score_fn (cumulative) | 02c_experiment_brief.md §FR-3.2, H2O NeurIPS 2023 |
| M6 StreamingLLM baseline | 02c_experiment_brief.md §Training Protocol |
| M0 full-KV sanity | 02c_experiment_brief.md §Pre-validation |
| KV retention: 50% | 02c_experiment_brief.md §Training Protocol |
| Gate: ≥2.0 F1, CI lower>0 | 02c_experiment_brief.md §PoC Pass Condition |
| Bootstrap CI 1000 resamples | 02c_experiment_brief.md §Evaluation |
| Figures: 4 required | 02c_experiment_brief.md §Visualization Requirements |
