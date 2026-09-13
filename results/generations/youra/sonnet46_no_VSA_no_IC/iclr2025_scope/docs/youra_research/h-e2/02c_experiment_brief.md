# Experiment Design: h-e2

**Date:** 2026-08-22
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Entropy-guided k=4 SWA(w=512) conversion of Llama-2-7B zero-shot maintains WikiText-103 perplexity within 2.0 points of the full-attention baseline (Prediction P1).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 PASS (Gini mean=0.6829, top-10% share mean=0.7172, 100% examples pass)
**Gate Status:** MUST_WORK — prerequisite h-e1 satisfied ✅

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e2
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition
MUST_WORK: Δperplexity(entropy-k4 vs baseline) ≤ 2.0 on WikiText-103 test set. Failure routes to Phase 0 — zero-shot selective SWA fundamentally infeasible. Both positive and negative results are publishable (characterizes zero-shot SWA boundary).

---

## Continuation Context

**From h-e1 (VALIDATED):**
- Entropy criterion is stable (Spearman ρ ≥ 0.8 across seeds — confirmed)
- Gini coefficient mean=0.6829 (std=0.0117) across 200 examples — heavy-hitter concentration confirmed
- Top-10% token share mean=0.7172 — extreme attention concentration validated
- Head-mean pooling across heads is the correct entropy aggregation (head-max Gini drops to 0.466)
- Model: `meta-llama/Llama-2-7b-hf`, output_attentions=True
- Calibration set: 100 sequences from WikiText-103 validation split

**Key lesson for h-e2:** The entropy ranking from h-e1 identifies 4 layers with highest mean per-layer attention entropy. These are the 4 layers to replace with SWA(w=512). The depth positions of these layers should be recorded as a diagnostic output (relevant for h-m2 later).

### Previous Hypothesis Results (if applicable)
h-e1 validated existence and stability of the entropy criterion. h-e2 builds directly on the entropy ranking produced by h-e1 code to select conversion targets.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: sliding window attention SWA transformer experiment design**
- Results matched diffusion model attention (HuggingFace diffusers), not LLM SWA — no relevant findings for this hypothesis.
- Archon KB does not contain LLM-domain SWA experiment cases.

**Query 2: selective attention layer replacement LLM zero-shot perplexity**
- Results matched diffusion model community examples — no relevant findings.

**Query 3: sliding window attention mask PyTorch LLM (code examples)**
- One useful result: `torch.nn.functional.scaled_dot_product_attention` — confirms PyTorch SDPA accepts attn_mask with sliding window structure. Sliding window masking via upper-triangular boolean mask pattern is valid.

**Summary:** Archon KB is diffusion-model focused; no directly applicable LLM SWA cases. All grounding comes from Exa GitHub and web search.

### Archon Code Examples

**torch.nn.functional.scaled_dot_product_attention** (pytorch.org docs)
```python
# Sliding window mask can be passed as attn_mask to SDPA
# For window_size w, valid positions for query at i: [max(0, i-w), i]
# Mask: bool tensor where True = attend, False = block
def make_sliding_window_mask(seq_len, window_size, device):
    mask = torch.zeros(seq_len, seq_len, dtype=torch.bool, device=device)
    for i in range(seq_len):
        mask[i, max(0, i - window_size):i + 1] = True
    return mask  # (seq_len, seq_len)
```
**Used for:** SWA mask construction approach in pseudo-code.

### Exa GitHub Implementations

**Repository 1: yuyijiong/sliding-window-attention-adaptation** (SWAA paper)
- **URL:** https://github.com/yuyijiong/sliding-window-attention-adaptation
- **Relevance:** Exact paper for "Sliding Window Attention Adaptation" (arXiv 2512.10411) — supports Llama models, monkey-patches HF transformers, provides `non_sliding_layers` parameter to keep specific layers as full attention
- **Key Code:**
  ```python
  from swaa_patch import SWAAConfig, hack_hf_swaa
  hack_hf_swaa(training=False)
  model = AutoModelForCausalLM.from_pretrained(model_path, ...)
  swaa_config = SWAAConfig(
      sliding_window_size=2048,
      keep_first=100,
      non_sliding_layers=[1,3,5,7,9,11],  # layers kept as full attention
  )
  model.config.swaa_config = swaa_config
  ```
- **Key insight:** `non_sliding_layers` specifies indices of layers to KEEP as full attention. Entropy-selected high-entropy layers go to SWA; all others listed in `non_sliding_layers`.
- **Used for:** Primary implementation reference for SWA layer injection.

**Repository 2: HuggingFace Transformers (modeling_llama.py / AttentionMaskConverter)**
- **URL:** https://github.com/huggingface/transformers (issues #28915, #29777)
- **Relevance:** Confirms that SWA in HF Transformers works via `sliding_window` parameter in model config or via attention mask injection. `LLAMA_ATTENTION_CLASSES` registry supports custom attention implementations.
- **Key insight:** Zero-shot SWA drop-in WITHOUT fine-tuning causes severe quality degradation (user report in issue #28915: "doesn't even produce fluent text"). This is the key risk for h-e2 — but our approach converts only k=4 high-entropy layers, not all layers, which is the hypothesis differentiator.
- **Used for:** Understanding implementation risks and mask correctness.

**Repository 3: awslabs/hybrid-model-factory L2A**
- **URL:** https://github.com/awslabs/hybrid-model-factory/tree/main/examples/research/L2A
- **Relevance:** L2A replaces attention layers with Local (SWA) + conditional Global attention. Uses `sliding_window` config parameter. Shows layer-selective hybrid approach.
- **Used for:** Confirms selective per-layer SWA replacement pattern.

**Exa Web Search: WikiText-103 perplexity evaluation**
- HuggingFace `transformers` docs: stride-based perplexity for causal LMs with `max_length` constraint
- Dataset: `wikitext` in HuggingFace datasets (`wikitext-103-v1`, test split)
- Standard stride=512 for Llama-2-7B (context 4096) — use stride equal to window size for fair SWA comparison
- Llama-2-7B full-attention baseline WikiText-103 perplexity: ~5.47 (reported in literature)

**Serena Analysis Needed:** false — SWAA GitHub code and HF transformers issues are sufficiently clear for pseudo-code generation.

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT a paper reproduction — it is a novel zero-shot selective SWA experiment.**

**Recommended Implementation Path:**
- Primary: Direct HuggingFace Transformers monkey-patch approach inspired by SWAA (yuyijiong/sliding-window-attention-adaptation) — adapt `non_sliding_layers` logic for entropy-selected layers. No dependency on SWAA package directly.
- Fallback: Modify `model.config.sliding_window` and selectively override `model.model.layers[i].self_attn` forward method via monkey-patch per selected layer.
- Justification: SWAA shows the cleanest Llama-compatible implementation pattern. Direct HF override is simpler for 4 targeted layers.

**Recommended Implementation Path:**
- Primary: Monkey-patch 4 entropy-selected layers in Llama-2-7B with sliding window mask (w=512) using causal mask override
- Fallback: Fork `modeling_llama.py`, add `sliding_window_layers` config parameter
- Justification: Minimal code change, zero fine-tuning, directly tests the zero-shot feasibility claim

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The SWAA implementation pattern and HF transformers SWA mask construction are well-documented in GitHub issues and the SWAA repository README.

---

## Experiment Specification

### Dataset

**Name:** WikiText-103  
**Version:** wikitext-103-v1  
**Type:** standard (real dataset)  
**Source:** HuggingFace Datasets  
**Splits used:**
- Calibration: validation split, first 100 sequences (inherited from h-e1 — reuse exact same calibration indices)
- Evaluation: **full test split** (~245K tokens, ~60 articles)

**Preprocessing:**
- Tokenizer: `meta-llama/Llama-2-7b-hf` tokenizer (BPE, vocab=32000)
- Concatenate all test tokens into a single sequence, then chunk into `max_length=4096` with `stride=512`
- Stride choice: stride=512 matches SWA window size (w=512) — ensures fair comparison where SWA layers see a full window at every position
- No special tokens prepended (raw WikiText-103 tokens)
- Padding: none — trailing incomplete chunk discarded (consistent between baseline and SWA model)

**Statistics:**
- Train: ~103M tokens
- Validation: ~218K tokens  
- Test: ~245K tokens (~60 articles)
- Vocabulary: standard word-level (WikiText-103 original) but we use LLM tokenizer → ~200K BPE tokens on test

**Synthetic data check:** PASS — WikiText-103 is a standard real dataset (Merity et al., 2016).

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `"wikitext"`, config `"wikitext-103-v1"`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("wikitext", "wikitext-103-v1")
  test_text = "\n\n".join(dataset["test"]["text"])
  ```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (full attention, no modification)  
**Config:** 32 layers, 32 heads, hidden=4096, intermediate=11008, context=4096  
**Source:** `meta-llama/Llama-2-7b-hf` (HuggingFace Hub)  
**Fine-tuning:** None (zero-shot evaluation only)  
**Expected perplexity:** ~5.47 on WikiText-103 test (from literature; measure empirically)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.bfloat16,
      device_map="auto",
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  model.eval()
  ```

#### Proposed Model

**Architecture:** Llama-2-7B with k=4 layers replaced by SWA(w=512)

**Integration Point:**
- Select 4 layers with highest mean per-layer attention entropy (computed in h-e1, using 100-sequence calibration set, head-mean pooling)
- Replace those 4 layers' causal attention mask with a sliding window causal mask (window=512 tokens)
- All other 28 layers remain full attention

**Modification:** Monkey-patch `model.model.layers[i].self_attn.forward` for each entropy-selected layer index `i` to apply SWA mask instead of full causal mask. No weight changes.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Entropy-Guided SWA Layer Replacement
# Based on: SWAA (yuyijiong/sliding-window-attention-adaptation),
#           HF Transformers modeling_llama.py

def make_sliding_window_causal_mask(seq_len, window_size, dtype, device):
    """
    Returns additive mask: 0.0 for attended positions, -inf for blocked.
    Sliding window causal: position i attends to [max(0, i-window_size+1), i].
    """
    mask = torch.full((seq_len, seq_len), float("-inf"), dtype=dtype, device=device)
    for i in range(seq_len):
        start = max(0, i - window_size + 1)
        mask[i, start:i + 1] = 0.0
    return mask  # (seq_len, seq_len)

def patch_layer_with_swa(layer, window_size=512):
    """Monkey-patch a single LlamaDecoderLayer attention to use SWA mask."""
    original_forward = layer.self_attn.forward

    def swa_forward(hidden_states, attention_mask=None, position_ids=None, **kwargs):
        seq_len = hidden_states.shape[1]
        swa_mask = make_sliding_window_causal_mask(
            seq_len, window_size,
            dtype=hidden_states.dtype,
            device=hidden_states.device
        )
        # Override with SWA mask regardless of input mask
        return original_forward(
            hidden_states,
            attention_mask=swa_mask.unsqueeze(0).unsqueeze(0),
            position_ids=position_ids,
            **kwargs
        )
    layer.self_attn.forward = swa_forward

def apply_entropy_guided_swa(model, entropy_layer_ranking, k=4, window_size=512):
    """
    Args:
        entropy_layer_ranking: list of layer indices sorted by entropy descending (from h-e1)
        k: number of high-entropy layers to convert to SWA
    """
    target_layers = entropy_layer_ranking[:k]  # top-k highest entropy
    print(f"Converting layers {target_layers} to SWA(w={window_size})")
    for layer_idx in target_layers:
        patch_layer_with_swa(model.model.layers[layer_idx], window_size=window_size)
    return target_layers  # return for diagnostic logging (h-m2 depth analysis)
```

### Training Protocol

No training (zero-shot evaluation only). This is a pure inference experiment.

**Inference Configuration:**
- Batch size: 1 (sequential chunked evaluation)
- Max sequence length: 4096 (Llama-2 context window)
- Stride: 512 (matches SWA window size)
- Precision: bfloat16
- Device: 1× H100 GPU
- Seeds: 1 (fixed — EXISTENCE PoC, single run sufficient)
- torch.no_grad() throughout

**Mask validation (MANDATORY before evaluation):**
Before running perplexity evaluation, verify SWA mask is correct:
```python
# Check that position i only attends to [max(0,i-511), i]
def validate_swa_mask(mask, window_size=512):
    seq_len = mask.shape[-1]
    for i in range(min(seq_len, 10)):  # spot-check 10 positions
        attended = (mask[i] == 0.0).nonzero().squeeze()
        assert attended.min() >= max(0, i - window_size + 1)
        assert attended.max() == i
    print("SWA mask validation PASSED")
```

**Estimated runtime:** ~30 min on 1× H100

### Evaluation

**Primary Metric:** WikiText-103 perplexity (PPL) on full test set

**Perplexity computation:**
```python
import torch
from tqdm import tqdm

def compute_perplexity(model, tokenizer, text, max_length=4096, stride=512):
    encodings = tokenizer(text, return_tensors="pt")
    input_ids = encodings.input_ids.to(model.device)
    seq_len = input_ids.shape[1]
    nlls = []
    prev_end_loc = 0
    for begin_loc in range(0, seq_len, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        trg_len = end_loc - prev_end_loc
        input_chunk = input_ids[:, begin_loc:end_loc]
        target_ids = input_chunk.clone()
        target_ids[:, :-trg_len] = -100  # ignore non-target positions
        with torch.no_grad():
            outputs = model(input_chunk, labels=target_ids)
        nlls.append(outputs.loss * trg_len)
        prev_end_loc = end_loc
        if end_loc == seq_len:
            break
    ppl = torch.exp(torch.stack(nlls).sum() / seq_len)
    return ppl.item()
```

**Outputs to record:**
- `ppl_baseline`: Llama-2-7B full attention perplexity on WikiText-103 test
- `ppl_swa_k4`: Entropy-guided k=4 SWA perplexity on WikiText-103 test
- `delta_ppl`: `ppl_swa_k4 - ppl_baseline`
- `target_layers`: Indices of 4 entropy-selected layers (diagnostic, needed for h-m2)
- `depth_positions`: Depth statistics of converted layers (early/mid/late)

**Success Criteria (EXISTENCE PoC):**
- `delta_ppl ≤ 2.0` → GATE PASS → h-e2 VALIDATED
- `delta_ppl > 2.0` but `delta_ppl ≤ 5.0` → SWA feasible but h-e2 threshold not met → route to Phase 0 for threshold relaxation analysis
- `delta_ppl > 5.0` → Zero-shot selective SWA infeasible → route to Phase 0

**Expected baseline performance (from literature):**
- Llama-2-7B WikiText-103 PPL: ~5.47 (Touvron et al., 2023)
- Source: SWAA paper (arXiv 2512.10411) reports Llama-2 baselines in similar range

**PoC Pass Condition:**
1. Code runs without error
2. `ppl_swa_k4 - ppl_baseline ≤ 2.0`

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: language_modeling
- Library: computed inline (NLL from model `labels` argument)
- Code: `torch.exp(mean_nll)` — standard HF perplexity pattern

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing `ppl_baseline` vs `ppl_swa_k4`, with Δ=2.0 threshold line marked.

#### Additional Figures (LLM Autonomous)
- **Layer depth distribution**: Scatter plot of 32 Llama-2-7B layers with entropy score per layer (x=layer index, y=entropy), highlighting top-4 entropy-selected layers. Confirms depth position hypothesis (residual stream compensation mechanism).
- **Perplexity delta breakdown**: If per-chunk PPL is tracked, plot PPL delta vs. sequence position to show whether SWA degradation concentrates at long-range dependencies.

**Output Location:** `docs/youra_research/h-e2/figures/`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Llama-2-7B uses standard causal attention (not flash attention or sliding window natively) — SWA mask injection is architecturally possible | TRUE |
| Mechanism Isolatable | Monkey-patch can be applied/removed per layer — baseline run uses no patch, SWA run patches exactly k=4 layers | TRUE |
| Baseline Measurable | Llama-2-7B without patches runs standard perplexity eval — baseline fully independent | TRUE |

### Architecture Compatibility Check

**Llama-2-7B is fully compatible:**
- Standard multi-head causal attention with rotary position embeddings (RoPE)
- Grouped-query attention only in 70B model; 7B uses standard MHA
- `modeling_llama.py` forward accepts `attention_mask` parameter — SWA additive mask can be injected directly
- No flash attention dependency required (eager mode for mask injection)

**Required:** `attn_implementation="eager"` (not flash_attention_2) — flash attention handles masking internally and cannot accept external sliding window masks via monkey-patch.

**Incompatible configurations:**
- `attn_implementation="flash_attention_2"` — cannot inject custom masks
- `attn_implementation="sdpa"` — may partially handle but unreliable for custom sliding window mask shape

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Converting layers [i,j,k,l] to SWA(w=512)"` | `apply_entropy_guided_swa()` |
| Tensor Shape | attention_mask shape changes from `(1,1,seq,seq)` causal to `(1,1,seq,seq)` sliding window — non-zero positions per row = min(w, i+1) not i+1 | `patch_layer_with_swa()` → `swa_forward()` |
| Metric Delta | `ppl_swa_k4 ≠ ppl_baseline` (any difference confirms mechanism is active) | `compute_perplexity()` |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_swa_mechanism(model, target_layers, window_size=512, test_seq_len=600):
    """Verify SWA mask is correctly applied to target layers."""
    captured = {}
    hooks = []
    for idx in target_layers:
        def make_hook(layer_idx):
            def hook(module, args, kwargs):
                if "attention_mask" in kwargs and kwargs["attention_mask"] is not None:
                    mask = kwargs["attention_mask"]
                    # Count attended positions in row 599 (beyond window)
                    attended = (mask[0, 0, test_seq_len-1] == 0.0).sum().item()
                    captured[layer_idx] = attended
            return hook
        h = model.model.layers[idx].self_attn.register_forward_pre_hook(
            make_hook(idx), with_kwargs=True
        )
        hooks.append(h)
    # Run a dummy forward
    dummy = torch.zeros(1, test_seq_len, dtype=torch.long, device=model.device)
    with torch.no_grad():
        model(dummy)
    for h in hooks:
        h.remove()
    for layer_idx, attended in captured.items():
        expected = window_size
        assert attended == expected, (
            f"Layer {layer_idx}: expected {expected} attended positions, got {attended}. "
            "SWA mask not correctly applied!"
        )
    print(f"SWA mechanism VERIFIED: {len(target_layers)} layers correctly use w={window_size}")
    return captured
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No log message | `target_layers` list empty | FAIL: entropy ranking from h-e1 not loaded correctly |
| Mask unchanged | `attended == seq_len` (not window_size) in verification | FAIL: monkey-patch did not override mask |
| Zero delta | `ppl_swa_k4 == ppl_baseline` | FAIL: SWA not applied — check patch application |
| Architecture incompatible | `attn_implementation != "eager"` | FAIL EARLY: switch to eager mode |
| Position embedding conflict | PPL > 20 (catastrophic degradation) | FAIL: RoPE positions incompatible with SWA mask |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (log confirms target layers) | `apply_entropy_guided_swa()` return value |
| SWA Mask Correct | All target layers: attended=512 at pos≥512 | `verify_swa_mechanism()` |
| Effect Measurable | `ppl_swa_k4 ≠ ppl_baseline` | `delta_ppl != 0` |
| Hypothesis Supported | `delta_ppl ≤ 2.0` | `compute_perplexity()` on full test set |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `ppl_swa_k4 - ppl_baseline ≤ 2.0` (WikiText-103 test set)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: PyTorch `scaled_dot_product_attention` documentation
- **Type:** Code example (official docs)
- **Query:** "sliding window attention mask PyTorch LLM"
- **Relevance:** Confirms that custom `attn_mask` (additive float tensor) is accepted by SDPA backend
- **Key Insight:** Boolean mask or additive (-inf) mask both work; additive mask with 0.0/−inf is preferred for numerical stability
- **Used For:** SWA mask construction approach in pseudo-code

**Note:** Archon KB did not contain LLM-domain SWA experiment cases — all are diffusion model content.

### B. GitHub Implementations (Exa)

**Repository B.1**: yuyijiong/sliding-window-attention-adaptation
- **URL:** https://github.com/yuyijiong/sliding-window-attention-adaptation
- **Query:** "Llama-2 sliding window attention replacement zero-shot HuggingFace implementation GitHub"
- **Relevance:** Direct implementation of SWA adaptation for Llama models (paper arXiv 2512.10411 "Sliding Window Attention Adaptation")
- **Key Code (annotated):**
  ```python
  # SWAA approach: hack_hf_swaa patches transformers, SWAAConfig specifies which layers to keep as full attn
  swaa_config = SWAAConfig(
      sliding_window_size=2048,  # we use 512 for our hypothesis
      keep_first=100,             # sink tokens — we skip this for zero-shot PoC
      non_sliding_layers=[1,3,5,7,9,11],  # layers to KEEP as full attn
      # Our interpretation: non_sliding_layers = all layers EXCEPT entropy-selected top-4
  )
  ```
- **Used For:** Primary implementation pattern for selective SWA layer injection

**Repository B.2**: HuggingFace Transformers (issues #28915, #29777, Llama2 docs)
- **URL:** https://github.com/huggingface/transformers
- **Query:** "Llama-2 sliding window attention replacement zero-shot HuggingFace implementation GitHub"
- **Key finding:** Full-model SWA drop-in without fine-tuning produces gibberish ("doesn't even produce fluent text") — validates h-e2's selective approach as essential. Issue confirms `LLAMA_ATTENTION_CLASSES` hook for custom attention.
- **Key finding from #29777:** SWA mask in HF Transformers works via `_prepare_4d_causal_attention_mask` → `AttentionMaskConverter.to_causal_4d` with `sliding_window` parameter.
- **Used For:** Understanding failure modes of naive full-model SWA (motivates selective approach), mask implementation reference

**Repository B.3**: awslabs/hybrid-model-factory L2A
- **URL:** https://github.com/awslabs/hybrid-model-factory/tree/main/examples/research/L2A
- **Relevance:** Layer-selective hybrid (SWA + full attention) architecture on Llama/Qwen models
- **Used For:** Confirms per-layer selective SWA replacement is a valid and implementable pattern

**Repository B.4**: mit-han-lab/streaming-llm (StreamingLLM)
- **URL:** https://github.com/mit-han-lab/streaming-llm
- **Relevance:** Window attention + sink tokens for Llama-2, shows attention mask injection approach
- **Used For:** Background on windowed attention mask patterns

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results was sufficiently clear for pseudo-code generation.

### D. Previous Hypothesis Context

**Source:** h-e1 validation results (from injected state)
- **Reused:** Entropy layer ranking (top-4 indices by mean per-layer entropy on 100-sequence calibration set)
- **Reused:** Model loading config (`meta-llama/Llama-2-7b-hf`, bfloat16, device_map="auto")
- **Reused:** Calibration set (WikiText-103 validation split, first 100 sequences)
- **Why Reused:** h-e2 directly depends on h-e1 entropy ranking output; controlled experiment — only the SWA mask injection changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (WikiText-103 test) | Phase 2B plan + HF docs | 02b_verification_plan.md §Controlled Variables; Exa web search |
| Stride=512 for perplexity | HF transformers docs | Exa web search (huggingface.co/docs/transformers/perplexity) |
| Model loading (Llama-2-7B, eager mode) | GitHub B.2 | HF Transformers issues #28915, #29777 |
| SWA mask construction (additive float) | Archon A.1 + GitHub B.2 | PyTorch SDPA docs + HF Transformers |
| Monkey-patch approach | GitHub B.1 | SWAA repository (yuyijiong) |
| `apply_entropy_guided_swa` pseudo-code | GitHub B.1, B.2 | SWAA SWAAConfig pattern + HF Transformers |
| Top-4 entropy layer indices | h-e1 output | Previous hypothesis validation (injected state) |
| Success threshold (Δperplexity ≤ 2.0) | Phase 2B plan | 02b_verification_plan.md §h-e2 |
| Expected baseline PPL ~5.47 | Literature | Touvron et al. 2023 (Llama-2 paper); SWAA paper arXiv 2512.10411 |
| Verification code pattern | GitHub B.1 + Phase 2C template | SWAA + mechanism_verification_protocol.md |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate only)
**Date:** 2026-08-22

### Workflow History for This Hypothesis
- Phase 2C experiment design: COMPLETED (2026-08-22)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant LLM results), Exa (GitHub + web — primary grounding)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
