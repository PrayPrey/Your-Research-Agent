# Experiment Design: h-e1

**Date:** 2026-08-22
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Per-layer attention entropy in Llama-2-7B produces a stable layer ranking (Spearman ρ ≥ 0.8) across 3 independent 100-sequence calibration subsets from WikiText-103 validation split.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (h-e1 is the first hypothesis)
**Gate Status:** MUST_WORK — failure (ρ < 0.7) blocks h-e2, h-m1, h-m2, h-c1 and invalidates H-EntropySWA-v1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: Spearman ρ ≥ 0.8 for top-8 layer entropy rankings across all 3 pairwise comparisons of non-overlapping 100-sequence calibration subsets of WikiText-103 validation split.

Falsification threshold: ρ < 0.7 → entropy ranking is noise; entropy criterion invalid for H-EntropySWA-v1.

---

## Continuation Context

No previous hypothesis results — h-e1 is the entry point of the verification chain.

### Previous Hypothesis Results (if applicable)
None.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: attention entropy layer selection LLM**
- Archon KB returned diffusers/stable-diffusion content (similarity ~0.43). No directly relevant attention entropy / LLM layer selection cases in KB.
- Key insight from KB code results: PyTorch `scaled_dot_product_attention` with causal mask is standard; `output_attentions=True` in HuggingFace returns raw softmax weights per layer.

**Query 2: attention entropy stability calibration transformer**
- No high-similarity KB results (max similarity 0.39). KB does not contain LLM efficiency / entropy-based pruning cases.

**Query 3: WikiText-103 perplexity benchmark LLM**
- HuggingFace paper hf.co/papers/2305.14314 (similarity 0.51) + OpenReview LLM quantization paper (0.41) returned. Confirm WikiText-103 is standard LLM benchmark.

**Conclusion:** Archon KB lacks prior cases for this specific mechanism. All design decisions grounded in Exa GitHub findings below.

### Archon Code Examples

**Query: attention entropy PyTorch output_attentions**
- PyTorch `scaled_dot_product_attention` reference implementation (similarity 0.50) — shows standard attention weight computation pattern.
- Key pattern: `attn_weight = softmax(Q @ K.T * scale)` then `attn_weight @ V` — entropy computed from `attn_weight`.
- Llama-2-7B FLOPs calculation snippet confirmed `meta-llama/Llama-2-7b` as correct HuggingFace identifier.

**Query: Spearman rank correlation layer importance**
- No directly relevant results. Spearman ρ computation confirmed via scipy (standard; no special library).

### Exa GitHub Implementations

**Repository 1: GAIR-NLP/Entropy-ABF** (retrieve_attn.py)
- **URL:** https://github.com/GAIR-NLP/Entropy-ABF/blob/main/retrieve_attn.py
- **Relevance:** Direct implementation of per-layer attention entropy extraction from Llama using `output_attentions=True`
- **Key Code:**
  ```python
  output = model(**input, output_attentions=True)
  attentions = output.attentions  # tuple of (1, n_heads, seq_len, seq_len) per layer

  for layer in selected_layers:
      attn_scores = attentions[layer]  # shape: (1, head_size, seq_len, seq_len)
      attn_scores.squeeze_()          # shape: (head_size, seq_len, seq_len)
      # last token attention: shape (head_size, seq_len)
      last_token_attn = attn_scores[:, -1].softmax(dim=1)

  # Entropy computation
  def compute_entropy(attn_weights):
      entropy = 0
      for val in attn_weights:
          entropy -= val * math.log(val + 1e-9, math.e)
      return entropy
  ```
- **Training Config:** Inference-only (no training)
- **Dataset:** JSONL text files, sequences up to 4096 tokens
- **Used For:** Core mechanism pseudo-code; confirms `output_attentions=True` API

**Repository 2: mathispink/attention-saver**
- **URL:** https://github.com/mathispink/attention-saver
- **Relevance:** Production-grade attention entropy extraction for HuggingFace LLMs including Llama; handles flash-attention context
- **Key Code:**
  ```python
  with AttentionSaver(
      model=model,
      layer_ids=[4, 5, 6],
      row_wise_statistics=[
          lambda p: -np.sum(p * np.log2(p + 1e-9)),  # entropy
      ],
  ):
      model(**inputs)
  ```
- **Note:** Useful for long sequences; for h-e1 (100 seqs × 2048 tokens), standard `output_attentions=True` is sufficient

**Repository 3: HuggingFace transformers modeling_llama.py**
- **URL:** https://github.com/huggingface/transformers/blob/v4.46.0/src/transformers/models/llama/modeling_llama.py
- **Relevance:** Confirms `output_attentions` flag in Llama decoder layer; returns `self_attn_weights` in layer outputs
- **Key Code:**
  ```python
  # In LlamaDecoderLayer.forward():
  if output_attentions:
      outputs += (self_attn_weights,)
  # output.attentions is tuple of length 32, each (batch, n_heads, seq_len, seq_len)
  ```

**Repository 4: yuyijiong/sliding-window-attention-adaptation (SWAA)**
- **URL:** https://github.com/yuyijiong/sliding-window-attention-adaptation
- **Relevance:** Paper "Sliding Window Attention Adaptation" (arXiv 2512.10411) — directly related to H-EntropySWA-v1 hypothesis; confirms feasibility of post-hoc SWA adaptation
- **Note:** Used for downstream h-e2 context; h-e1 only requires entropy scoring

**Web sources on layer-level entropy in LLMs:**
- arxiv 2604.03589: Layer-wise entropy profiles across LLMs — confirms LLaMA has lower mean entropy (1.809) with higher cross-layer SD (0.600), indicating strong layer differentiation → supports stability of ranking
- arxiv 2502.16570 (Entropy-Lens): Per-layer entropy profiling on Llama3.2; same `output_attentions` approach confirmed
- arxiv 2604.24938 (Calibration Matters More Than Search): Spearman ρ used to measure correlation of layer rankings across calibration configurations — directly relevant methodology

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

This is not a paper reproduction experiment — it is an original measurement experiment. No single "author implementation" exists. Priority:

1. ⭐⭐⭐ HIGHEST: Custom implementation using HuggingFace `transformers` + `output_attentions=True`, modeled on GAIR-NLP/Entropy-ABF pattern
2. ⭐⭐ MEDIUM: `entropy-profiler` PyPI package (logit-lens entropy, not attention entropy — different measure, not applicable here)

**Recommended Implementation Path:**
- Primary: Custom script using `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")` + `output_attentions=True`, entropy computed per head then averaged per layer, Spearman ρ via `scipy.stats.spearmanr`
- Fallback: `mathispink/attention-saver` library for memory-efficient extraction if GPU OOM
- Justification: GAIR-NLP/Entropy-ABF demonstrates exact API pattern; standard HuggingFace approach with no custom kernels required

### Code Analysis (Serena MCP)

*Skipped* — Code from search results (GAIR-NLP/Entropy-ABF, HuggingFace modeling_llama.py) was sufficiently clear for pseudo-code generation.

---

## Experiment Specification

### Dataset

**Dataset:** WikiText-103
**Type:** standard
**Source:** HuggingFace Datasets — `Salesforce/wikitext`, config `wikitext-103-raw-v1`
**Split used:** `validation` split only (to avoid test contamination)
**Total validation tokens:** ~217K tokens (WikiText-103 validation = ~217K tokens across ~4,358 articles)

**Calibration Subset Construction:**
- Tokenize full validation split with Llama-2 tokenizer (seqlen = 2048)
- Sample 3 non-overlapping subsets of 100 contiguous sequences each (seeds 0, 1, 2)
- Total: 300 sequences × 2048 tokens = 614,400 tokens processed
- Subset assignment: indices [0:100], [100:200], [200:300] after tokenization and chunking

**Preprocessing:**
- Tokenizer: `AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")`
- Tokenize with `truncation=False`, then chunk into windows of `seqlen=2048`
- No padding (use full sequences); batch_size=1 for memory efficiency
- No augmentation (inference-only experiment)

**Path Specification:**
- Type: `standard`
- Path: `auto` (HuggingFace cache, auto-download)
- Code: `load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="validation")`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"Salesforce/wikitext"` / `"wikitext-103-raw-v1"` / split `"validation"`
- Code: `from datasets import load_dataset; ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="validation")`

### Models

#### Baseline Model

**Architecture:** Llama-2-7B
**Pretrained:** `meta-llama/Llama-2-7b-hf`
**Type:** Causal decoder transformer, 32 attention layers, 32 attention heads per layer, head_dim=128, hidden_size=4096
**Attention type:** Standard full self-attention (eager implementation, NOT sdpa/flash — required for `output_attentions=True`)
**Parameters:** 6.74B

**Configuration for h-e1:**
- `attn_implementation="eager"` (required to get attention weights; flash_attention_2 does not support `output_attentions=True`)
- `torch_dtype=torch.float16`
- `device_map="auto"`
- `output_attentions=True` during forward pass

**No modifications** to model weights or architecture — inference only.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", attn_implementation="eager", torch_dtype=torch.float16, device_map="auto")`

#### Proposed Model

**Architecture:** Not applicable — h-e1 measures entropy stability only; no model modification.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Layer Attention Entropy Scoring for Llama-2-7B
# Based on: GAIR-NLP/Entropy-ABF retrieve_attn.py + HuggingFace modeling_llama.py
# Purpose: Compute mean per-layer attention entropy over calibration sequences
#          to produce a stable layer ranking (Spearman ρ ≥ 0.8 across 3 subsets)

import torch
import numpy as np
from scipy.stats import spearmanr

def compute_layer_entropy(model, input_ids):
    """
    Args:
        model: LlamaForCausalLM with attn_implementation='eager'
        input_ids: (1, seq_len) token ids on device
    Returns:
        entropy_per_layer: (n_layers,) mean entropy across heads and tokens
    """
    with torch.no_grad():
        output = model(input_ids, output_attentions=True)
    # output.attentions: tuple of 32 tensors, each (1, n_heads, seq_len, seq_len)

    n_layers = len(output.attentions)
    entropy_per_layer = np.zeros(n_layers)

    for layer_idx, attn in enumerate(output.attentions):
        # attn: (1, 32, seq_len, seq_len) — softmax weights, already normalized
        attn_np = attn.squeeze(0).float().cpu().numpy()  # (32, seq_len, seq_len)
        # Shannon entropy: H = -sum(p * log(p + eps)) per query position per head
        eps = 1e-9
        H = -np.sum(attn_np * np.log(attn_np + eps), axis=-1)  # (32, seq_len)
        entropy_per_layer[layer_idx] = H.mean()  # scalar: mean over heads and positions

    return entropy_per_layer  # shape: (32,)


def score_calibration_subset(model, sequences):
    """
    sequences: list of (1, 2048) input_id tensors
    Returns: (32,) mean entropy per layer over all sequences
    """
    all_entropies = []
    for input_ids in sequences:
        layer_ent = compute_layer_entropy(model, input_ids)
        all_entropies.append(layer_ent)
    return np.mean(all_entropies, axis=0)  # (32,)


def rank_layers(mean_entropy_per_layer):
    """Return layer indices sorted by entropy descending (highest entropy first)."""
    return np.argsort(mean_entropy_per_layer)[::-1]  # descending

# Stability check across 3 subsets:
# entropy_subset_A = score_calibration_subset(model, subset_A_sequences)
# entropy_subset_B = score_calibration_subset(model, subset_B_sequences)
# rho_AB, _ = spearmanr(entropy_subset_A, entropy_subset_B)
# SUCCESS: min(rho_AB, rho_AC, rho_BC) >= 0.8
```

### Training Protocol

h-e1 is an inference-only measurement experiment. No training is performed.

**Computational Protocol:**

- **Hardware:** 1× GPU with ≥24GB VRAM (H100/A100/RTX 3090); CPU-feasible if GPU unavailable (slower)
- **Precision:** float16 for model weights; float32 for entropy computation
- **Batch size:** 1 (single sequence per forward pass due to attention weight memory)
- **Sequences per subset:** 100 (seqlen=2048)
- **Total forward passes:** 3 subsets × 100 sequences = 300 forward passes
- **Seeds:** Fixed — subset assignment uses deterministic index slicing (seeds 0/1/2 for reproducibility label only; actual split is non-overlapping indices)
- **Estimated runtime:** ~15 min on 1× H100; ~45 min on CPU

**No optimizer, no loss, no gradient computation.**

> ⚠️ **EXISTENCE (PoC):** No training loop. Single run. 1 seed.

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target |
|--------|-----------|--------|
| Spearman ρ (A,B) | Spearman rank correlation of per-layer mean entropy between subset A and subset B | ≥ 0.8 |
| Spearman ρ (A,C) | Same for subsets A and C | ≥ 0.8 |
| Spearman ρ (B,C) | Same for subsets B and C | ≥ 0.8 |
| min(ρ) | Minimum of the 3 pairwise ρ values | ≥ 0.8 (gate criterion) |

**Computation:**
```python
from scipy.stats import spearmanr
rho_AB, p_AB = spearmanr(entropy_A, entropy_B)  # entropy_A: (32,) mean per layer
rho_AC, p_AC = spearmanr(entropy_A, entropy_C)
rho_BC, p_BC = spearmanr(entropy_B, entropy_C)
gate_passes = min(rho_AB, rho_AC, rho_BC) >= 0.8
```

**Secondary diagnostic outputs:**
- Per-layer mean entropy values for each subset (32-dim vectors)
- Top-8 highest-entropy layer indices per subset
- Overlap in top-8 sets across subsets
- Per-layer entropy bar chart for each subset

**Success Criteria:**
- proposed_metric > baseline_metric: min(ρ_AB, ρ_AC, ρ_BC) ≥ 0.8

**Expected Performance (from literature):**
- arxiv 2604.03589: LLaMA exhibits cross-layer entropy SD of 0.600 with clear layer differentiation — supports stable ranking
- Calibration literature (GPTQ/AWQ): 100 calibration sequences routinely used; rankings stable across seeds at this scale

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Ranking stability (statistical correlation)
- Library: `scipy.stats.spearmanr` (stdlib-adjacent; in scipy which is standard)
- Code: `from scipy.stats import spearmanr; rho, pval = spearmanr(vec_a, vec_b)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart — min(ρ), mean(ρ) vs threshold (0.8); 3 pairwise ρ values side-by-side

#### Additional Figures (LLM Autonomous)
- Per-layer mean entropy heatmap/bar chart: 32 layers × 3 subsets overlay — shows visual stability
- Top-K layer ranking overlap Venn or table: which layers appear in top-8 across all 3 subsets
- Entropy rank correlation scatter plots: entropy_A vs entropy_B, entropy_A vs entropy_C, entropy_B vs entropy_C with ρ annotated

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `min(rho_AB, rho_AC, rho_BC) >= 0.8`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** PyTorch `scaled_dot_product_attention` documentation
- Query: "attention entropy PyTorch output_attentions"
- Key insight: Standard attention weight computation (`attn_weight = softmax(Q @ K.T * scale)`); entropy computed from these weights
- Used for: Confirming attention weight API

**Source A.2:** HuggingFace Transformers documentation (transformers index)
- Query: "attention entropy stability calibration transformer"
- Key insight: `output_attentions=True` returns all layer attention tensors
- Used for: Confirming HuggingFace API for attention extraction

**Source A.3:** hf.co/papers/2305.14314 + OpenReview LLM quantization paper
- Query: "WikiText-103 perplexity benchmark LLM"
- Key insight: WikiText-103 is standard benchmark; 100-sequence calibration is standard practice
- Used for: Dataset choice justification

### B. GitHub Implementations (Exa)

**Repository B.1:** GAIR-NLP/Entropy-ABF — retrieve_attn.py
- **URL:** https://github.com/GAIR-NLP/Entropy-ABF/blob/main/retrieve_attn.py
- **Query:** "per-layer attention entropy scoring Llama-2 PyTorch output_attentions sliding window layer selection"
- **Relevance:** Direct implementation of per-layer attention entropy extraction from Llama using `output_attentions=True` — highest relevance
- **Key Code (annotated):**
  ```python
  output = model(**input, output_attentions=True)
  attentions = output.attentions  # tuple[32], each (1, n_heads, seq_len, seq_len)
  # Used as basis for: core mechanism pseudo-code
  for layer in selected_layers:
      attn_scores = attentions[layer].squeeze_()  # (n_heads, seq_len, seq_len)
      entropy -= val * math.log(val + 1e-9, math.e)  # Shannon entropy
  ```
- **Configuration Extracted:** Inference-only, `load_in_4bit=True`, `device_map="auto"`, bfloat16
- **Used For:** Core mechanism pseudo-code (Section "Core Mechanism Implementation")

**Repository B.2:** mathispink/attention-saver
- **URL:** https://github.com/mathispink/attention-saver
- **Relevance:** Production library for attention entropy extraction; memory-efficient; supports all HuggingFace causal LLMs
- **Key Code:**
  ```python
  # row_wise_statistics callable list for entropy
  lambda p: -np.sum(p * np.log2(p + 1e-9))  # Shannon entropy per attention row
  ```
- **Used For:** Fallback implementation path; confirms entropy formula

**Repository B.3:** HuggingFace transformers modeling_llama.py (v4.46.0)
- **URL:** https://github.com/huggingface/transformers/blob/v4.46.0/src/transformers/models/llama/modeling_llama.py
- **Relevance:** Authoritative source for Llama-2 attention output API
- **Key Code:**
  ```python
  # output_attentions=True appends self_attn_weights to layer outputs
  if output_attentions:
      outputs += (self_attn_weights,)
  # output.attentions[i]: (batch, n_heads, seq_len, seq_len)
  ```
- **Used For:** Confirming `output_attentions` API; tensor shape verification

**Repository B.4:** yuyijiong/sliding-window-attention-adaptation (SWAA, arXiv 2512.10411)
- **URL:** https://github.com/yuyijiong/sliding-window-attention-adaptation
- **Relevance:** Directly related to H-EntropySWA-v1 main hypothesis; shows SWA adaptation is feasible
- **Used For:** Downstream h-e2 context only; not used in h-e1 design

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from GAIR-NLP/Entropy-ABF and HuggingFace modeling_llama.py was sufficiently clear.

### D. Previous Hypothesis Context

**Previous Context:** None — h-e1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: WikiText-103 | Archon KB (A.3) + Exa web | hf.co/papers/2305.14314; Salesforce/wikitext HF page |
| Dataset: 100-sequence calibration | Exa web | GPTQ/AWQ literature; 02b_verification_plan.md |
| Dataset: validation split | Phase 2B | 02b_verification_plan.md Section h-e1 |
| Model: Llama-2-7B | Phase 2B | 02b_verification_plan.md Controlled Variables |
| Model loading: `attn_implementation="eager"` | Exa GitHub | HuggingFace modeling_llama.py (B.3) |
| Entropy formula: H = -Σ p log(p+ε) | Exa GitHub | GAIR-NLP/Entropy-ABF (B.1), attention-saver (B.2) |
| Attention API: `output_attentions=True` | Exa GitHub | GAIR-NLP/Entropy-ABF (B.1), modeling_llama.py (B.3) |
| Entropy averaging: mean over heads and positions | Exa web | arxiv 2604.03589 (layer-level entropy methodology) |
| Success metric: Spearman ρ ≥ 0.8 | Phase 2B | 02b_verification_plan.md h-e1 success criterion |
| Spearman ρ computation: scipy | Exa (Calibration Matters) | arxiv 2604.24938 Figure 3 Spearman ρ methodology |
| Pseudo-code | Exa GitHub | GAIR-NLP/Entropy-ABF retrieve_attn.py (B.1) |
| Runtime estimate: ~15 min H100 | Phase 2B | 02b_verification_plan.md Timeline |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block below)
**Date:** 2026-08-22T00:00:00+00:00

### Workflow History for This Hypothesis
- 2026-08-22T02:45:35: h-e1 set to IN_PROGRESS (external loop)
- 2026-08-22: Phase 2C experiment design started (Step 1)
- 2026-08-22: Archon KB searched (Step 2) — no domain-specific results
- 2026-08-22: Exa GitHub searched (Step 3) — 4 repositories found
- 2026-08-22: Serena skipped (Step 4) — code sufficiently clear
- 2026-08-22: Dataset/baseline confirmed (Step 5)
- 2026-08-22: Experiment specification synthesized (Step 6)
- 2026-08-22: References documented (Step 7)
- 2026-08-22: Validation passed (Step 8) — experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code, 5 queries), Exa (GitHub + Web, 4 queries), Serena (skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
