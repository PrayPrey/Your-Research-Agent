# Experiment Design: H-E1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under LLaMA-3.1-8B fine-tuned with LoRA (r=16) on MNLI, the Spearman rank correlation between LoRA-modified attention weights and Locret retaining head scores (trained on LM loss) is systematically below 0.7 for task-discriminative tokens across 100 MNLI validation examples, indicating that task-adapted attention patterns are misaligned with LM-loss-trained eviction heuristics.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — pending evaluation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — if H-E1 fails (mean Spearman ρ ≥ 0.7), the entire hypothesis chain (H-M1 through H-M4) is blocked. Failure response: revisit assumption A1, run gradient attribution experiment before abandoning.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous context applies.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the root hypothesis with no predecessors.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "LoRA attention weights KV cache eviction correlation analysis"**
- Matched pages: HuggingFace PEFT docs (LoRA adapter conceptual guide), HuggingFace PEFT GitHub
- **Similarity scores:** 0.44–0.41 (low; no direct past cases for LoRA-KV correlation experiments)
- **Key insight:** Archon KB confirms LoRA as established method but does not contain past cases on correlation between LoRA attention and KV eviction scores — this is a novel diagnostic experiment.
- **Relevant code pattern:** `F.scaled_dot_product_attention` for GQA on LLaMA-3 (PyTorch docs, similarity 0.44), which confirms LLaMA-3.1-8B uses grouped-query attention (GQA) with separate num_key_value_heads — important for per-head correlation extraction.

**Query 2: "Spearman correlation attention scores PEFT fine-tuning LLM"**
- Matched pages: HuggingFace PEFT GitHub (chunk_matches=2), PEFT paper (2305.14314), LoRA conceptual guide
- **Key insight:** No past experiment cases for Spearman ρ between LoRA attention and Locret scores. PEFT library (v0.x+) supports `output_attentions=True` in model forward pass for attention weight extraction.

**Query 3: "Locret KV cache retaining head token eviction LLM"**
- Matched pages: flash-attention (0.38), PEFT paper (0.36) — low relevance
- **Key insight:** Archon KB does not contain Locret-specific content; Locret information sourced from Exa search (next section).

**Code Query: "attention weight extraction hook LLaMA PyTorch"**
- **Best match:** `F.scaled_dot_product_attention` implementation (similarity 0.44) — confirms attention weight tensor shape `(B, num_heads, seq_len, seq_len)` for LLaMA-3.1-8B in eager mode.
- **Key code pattern from Archon:**
  ```python
  # PyTorch scaled dot-product attention (eager mode returns attention weights)
  attn_weight = query @ key.transpose(-2, -1) * scale_factor
  attn_weight = torch.softmax(attn_weight, dim=-1)  # (B, H, L, S) attention matrix
  ```
- **Used for:** Confirming that `output_attentions=True` with `attn_implementation="eager"` is required to extract attention weights from LLaMA-3.1-8B.

### Archon Code Examples

**Code Source 1:** PyTorch `scaled_dot_product_attention` (pytorch.org docs)
- **Pattern:** Returns attention weights `(B, H, L, S)` in eager mode
- **Insight:** LLaMA-3.1-8B GQA: queries shape `(B, 32, L, 64)`, keys/values shape `(B, 8, L, 64)` — need to handle GQA head expansion when comparing per-token attention to Locret CIS scores.

**Code Source 2:** NVIDIA kvpress `ScorerPress` / `ObservedAttentionPress`
- **URL:** github.com/NVIDIA/kvpress
- **Pattern:** `scores = attentions.sum(2)` — aggregates attention weights over query axis to get per-token KV importance score `(B, num_kv_heads, seq_len)`
- **Insight:** This is the standard way to convert attention weights to per-token scores, directly comparable to Locret's CIS scores.

### Exa GitHub Implementations

**Query 1: Locret official implementation**

**Repository 1:** huangyuxiang03/Locret (⭐ main repo)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Relevance:** HIGHEST — official author implementation of Locret retaining heads for LLaMA-3.1-8B
- **Architecture:** Retaining head is a small MLP injected into each attention layer, computing CIS (Causal Importance Score):
  ```python
  # Locret retaining head (from paper Section 3.3)
  # S_tilde = R([Q, K, V]) = sigma([Q, K, V] @ W1) @ W2
  # W1 in R^{(dm + 2*dkv) x dR}, W2 in R^{dR x (h/g)}
  # Output: CIS S_tilde shape (batch, seq_len, num_heads_per_group)
  ```
- **Official checkpoint:** `hyx21/Locret-llama-3.1-8B-instruct` on HuggingFace
- **Training:** Retaining heads trained on frozen LLaMA-3.1-8B using LM distillation loss
- **Loading:** `python example.py --model_dir <model_dir>` or `--retaining_head_path <*.bin>` for separate head loading
- **Key observation:** Locret CIS is computed from concatenated [Q, K, V] — it is NOT simply attention weights but a learned MLP over KV representations.

**Repository 2:** NVIDIA/kvpress (⭐1025)
- **URL:** github.com/NVIDIA/kvpress
- **Relevance:** HIGH — provides `ObservedAttentionPress` as reference for attention-based KV scoring
- **Key code:**
  ```python
  # ObservedAttentionPress: attention-based KV importance score
  scores = attentions.sum(2)  # (B, num_heads, seq_len) — sum over query axis
  scores = scores / n_tokens_in_sum  # normalize
  scores = scores.view(bsz, num_kv_heads, -1, n_tokens).mean(2)
  ```
- **Insight:** This is the "attention weight as proxy for KV importance" baseline — the H-E1 hypothesis tests whether this proxy is misaligned with task-specific LoRA attention patterns.

**Repository 3:** ngocbh/trimkv
- **URL:** github.com/ngocbh/trimkv
- **Relevance:** MEDIUM — includes LocRet as baseline in comparison study; confirms Locret checkpoint compatibility with standard PEFT workflows.

**Serena Analysis Needed:** false — code is clear from Exa snippets.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is a diagnostic experiment using TWO existing pre-trained models — no new training required. Implementation priority:

1. **Locret official checkpoint:** `hyx21/Locret-llama-3.1-8B-instruct` (author's official release on HuggingFace) — **HIGHEST PRIORITY** for CIS score extraction
2. **HuggingFace PEFT LoRA checkpoint:** `yophis/DRM-Llama-3.1-8B-mnli` (LLaMA-3.1-8B with LoRA on MNLI, task_type=SEQ_CLS) — available on HuggingFace; alternatively train LoRA r=16 on MNLI if no direct checkpoint is compatible
3. **NVIDIA kvpress:** Reference for attention weight aggregation patterns

**Recommended Implementation Path:**
- Primary: Load `hyx21/Locret-llama-3.1-8B-instruct` for CIS extraction + `yophis/DRM-Llama-3.1-8B-mnli` (or train LoRA r=16 on MNLI) for attention weight extraction
- Fallback: Train LoRA r=16 fine-tune on MNLI from `meta-llama/Meta-Llama-3.1-8B` (3 epochs, standard PEFT config) if no compatible checkpoint found
- Justification: H-E1 is inference-only (no new training needed for Locret); LoRA MNLI fine-tune can be done in ~2h on single GPU if checkpoint unavailable.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Locret retaining head architecture is fully documented in paper (CIS = sigma([Q,K,V]@W1)@W2) and official GitHub. No complex custom codebase to analyze in this diagnostic experiment.

---

## Experiment Specification

### Dataset

**Name:** GLUE MNLI validation set
**Type:** standard
**Source:** HuggingFace datasets (`nyu-mll/glue`, config `mnli`)
**Split used:** `validation_matched` (first 500 examples, primary test on 100)
**Size:** 9,815 examples in validation_matched (use fixed first 100, extend to 500 if borderline ρ ∈ [0.65, 0.75])
**Labels:** 3-class (entailment=0, neutral=1, contradiction=2)
**Hypothesis Fit:** MNLI sentence pairs have well-defined hypothesis/premise structure with discriminatively relevant tokens (hypothesis markers, contrast words) that differ from LM-predicted high-frequency tokens — ideal for testing task-attention vs. LM-eviction misalignment.
**Dataset type check:** `standard` ✅ (NOT synthetic — real benchmark dataset)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"nyu-mll/glue"`, config `"mnli"`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("nyu-mll/glue", "mnli")
  val_data = dataset["validation_matched"].select(range(500))  # 500 examples; use 100 for primary
  ```

### Models

#### Baseline Model

**Architecture:** LLaMA-3.1-8B with LoRA (r=16) fine-tuned on MNLI (task classification)
**Type:** Decoder-only transformer, 8B params, GQA (32 query heads / 8 KV heads per layer, 32 layers)
**LoRA config:** rank=16, alpha=32, target_modules=[q_proj, k_proj, v_proj], task_type=SEQ_CLS
**Source:** `meta-llama/Meta-Llama-3.1-8B` base + `yophis/DRM-Llama-3.1-8B-mnli` LoRA adapter (HuggingFace)
**Note:** If `yophis/DRM-Llama-3.1-8B-mnli` is incompatible (different LoRA rank), fall back to fine-tuning LoRA r=16 on MNLI for 3 epochs using HuggingFace PEFT. This takes ~2h on single A100.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace PEFT
- Identifier: `"yophis/DRM-Llama-3.1-8B-mnli"` (primary); `"meta-llama/Meta-Llama-3.1-8B"` (fallback base)
- Code:
  ```python
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  from peft import PeftModel
  base_model = AutoModelForSequenceClassification.from_pretrained(
      "meta-llama/Meta-Llama-3.1-8B",
      num_labels=3,
      attn_implementation="eager",  # REQUIRED for attention weight extraction
      torch_dtype=torch.float16,
      device_map="auto"
  )
  model = PeftModel.from_pretrained(base_model, "yophis/DRM-Llama-3.1-8B-mnli")
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
  ```

#### Proposed Model

**Architecture:** LLaMA-3.1-8B with Locret retaining heads (LM-distillation-trained, frozen backbone)

**Core Mechanism Implementation:**

```python
# H-E1: Spearman Correlation Diagnostic
# Measures misalignment between LoRA-adapted attention weights
# and Locret retaining head CIS scores
# Based on: Locret (huangyuxiang03/Locret) + NVIDIA kvpress ObservedAttentionPress
# No training required — inference-only diagnostic

import torch
import numpy as np
from scipy.stats import spearmanr
from transformers import AutoModelForCausalLM
from peft import PeftModel

def extract_lora_attention_scores(model, input_ids, attention_mask, layer_idx):
    """
    Extract per-token attention weights from LoRA-adapted model.
    Returns: attn_scores shape (num_heads, seq_len) — sum over query axis
    Requires: attn_implementation="eager" in model config
    """
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask,
                        output_attentions=True)
    # attentions: list of (B, num_heads, L, L) per layer
    attn = outputs.attentions[layer_idx]  # (1, 32, L, L)
    # Aggregate over query axis → per-token importance (B, num_heads, L)
    per_token_attn = attn.sum(dim=2).squeeze(0)  # (32, L)
    return per_token_attn

def extract_locret_cis_scores(locret_model, input_ids, attention_mask, layer_idx):
    """
    Extract CIS (Causal Importance Score) from Locret retaining heads.
    CIS = sigma([Q,K,V] @ W1) @ W2  per Locret paper Section 3.3
    Returns: cis_scores shape (num_kv_heads, seq_len)
    """
    with torch.no_grad():
        outputs = locret_model(input_ids, attention_mask=attention_mask,
                               output_retaining_scores=True)
    # Locret outputs retaining scores per layer
    cis = outputs.retaining_scores[layer_idx]  # (1, num_kv_heads, L)
    return cis.squeeze(0)  # (8, L) for GQA

def compute_spearman_rho(lora_scores, cis_scores):
    """
    Compute mean Spearman rho between LoRA attention and Locret CIS.
    Handles GQA: expand KV heads to match query heads.
    Returns: mean_rho (scalar), per_head_rho (array)
    """
    # Expand CIS from 8 KV heads to 32 query heads (GQA)
    cis_expanded = cis_scores.repeat_interleave(4, dim=0)  # (32, L)
    rhos = []
    for h in range(lora_scores.shape[0]):
        rho, _ = spearmanr(
            lora_scores[h].cpu().float().numpy(),
            cis_expanded[h].cpu().float().numpy()
        )
        rhos.append(rho)
    return np.mean(rhos), np.array(rhos)

# Main loop: 100 MNLI validation examples, seed=42
# Target layer: average over all 32 layers (or use middle layers 14-18)
# Success: mean_rho < 0.7 → misalignment confirmed
```

### Training Protocol

**No training required for H-E1.** This is an inference-only diagnostic experiment.

**Inference Configuration:**
- **Seed:** 42 (fixed for reproducibility)
- **Examples:** First 100 from MNLI `validation_matched` (fixed indices, seed=42 shuffle)
- **Batch size:** 1 (sequential processing for attention extraction; flash attention disabled)
- **Precision:** float16
- **Device:** Single GPU (CUDA_VISIBLE_DEVICES set to lowest-usage GPU)
- **attn_implementation:** `"eager"` (REQUIRED — disables FlashAttention to enable `output_attentions=True`)
- **Max sequence length:** 512 tokens (standard MNLI premise+hypothesis length)

**Fallback (if LoRA checkpoint unavailable):**
- Fine-tune LoRA r=16 on MNLI for 3 epochs using HuggingFace PEFT + Trainer
- Optimizer: AdamW, LR=1e-4, batch_size=16, warmup_ratio=0.06
- Estimated time: ~2h on single A100 80GB

**Seeds:** 1 (seed=42 only — EXISTENCE PoC, single run sufficient)

### Evaluation

**Primary Metric:** Mean Spearman ρ across 100 MNLI validation examples, all attention heads

**Computation:**
- For each example: compute per-head Spearman ρ between LoRA attention scores and Locret CIS scores
- Average across all heads and all 100 examples → `mean_rho` ± std

**Success Criteria:**
- `mean_rho < 0.7` → misalignment confirmed → H-E1 PASSES (MUST_WORK gate satisfied)
- `mean_rho ≥ 0.7` → misalignment absent → H-E1 FAILS → revisit assumption A1

**Borderline case:** If `mean_rho ∈ [0.65, 0.75]`, extend to 500 examples and check SST-2, QNLI datasets.

**Expected range based on research:** Prior work (arXiv 2604.21335, Locret paper) shows routing/eviction signals differ from attention patterns in task-adapted models. Expected ρ ≈ 0.3–0.6.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation measurement (not classification accuracy)
- Library: `scipy.stats.spearmanr`
- Code:
  ```python
  from scipy.stats import spearmanr
  rho, pvalue = spearmanr(lora_attn_scores, locret_cis_scores)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing mean Spearman ρ vs. threshold 0.7 (target vs. actual)

#### Additional Figures (LLM Autonomous)
- **Per-layer ρ heatmap:** Spearman ρ by layer (x-axis) and head (y-axis) — shows which layers/heads have highest misalignment
- **Token-level scatter plot:** For 5 representative examples — scatter plot of LoRA attention score vs. Locret CIS score per token, colored by token type (hypothesis marker / contrast word / other)
- **Distribution histogram:** Distribution of per-example mean ρ values across 100 examples

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (attention extraction + CIS extraction + Spearman computation)
2. `mean_spearman_rho < 0.7`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace PEFT LoRA Conceptual Guide
- **URL:** huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query used:** "LoRA attention weights KV cache eviction correlation analysis"
- **Relevance:** Confirms LoRA architecture (A·B injection into Q/K/V); confirms PEFT library support for `output_attentions=True`
- **Used for:** Model loading code, LoRA config specification

**Source A.2:** PyTorch `scaled_dot_product_attention` docs
- **URL:** pytorch.org/docs/master/generated/torch.nn.functional.scaled_dot_product_attention
- **Query used:** "attention weight extraction hook LLaMA PyTorch"
- **Key insight:** LLaMA-3.1-8B GQA shapes: query `(B, 32, L, 64)`, key/value `(B, 8, L, 64)`
- **Used for:** GQA head expansion in correlation computation

**Source A.3:** NVIDIA kvpress `ObservedAttentionPress`
- **URL:** github.com/NVIDIA/kvpress/blob/main/kvpress/presses/observed_attention_press.py
- **Pattern:** `scores = attentions.sum(2)` for per-token KV importance
- **Used for:** Attention weight aggregation pattern in pseudo-code

### B. GitHub Implementations (Exa)

**Repository B.1:** huangyuxiang03/Locret (⭐ official)
- **URL:** https://github.com/huangyuxiang03/Locret
- **Query used:** "Locret KV cache retaining head eviction LLaMA official implementation GitHub"
- **Key findings:**
  - Official Locret checkpoint for LLaMA-3.1-8B: `hyx21/Locret-llama-3.1-8B-instruct`
  - CIS formula: `S_tilde = sigma([Q,K,V]@W1)@W2` — MLP over concatenated QKV
  - Loading: `python example.py --model_dir <model_dir> --retaining_head_path <*.bin>`
  - Training used LM distillation loss on frozen backbone
- **Used for:** Locret CIS extraction, model loading code, understanding CIS formula

**Repository B.2:** NVIDIA/kvpress (⭐1025)
- **URL:** https://github.com/NVIDIA/kvpress
- **Query used:** "LoRA attention weights extraction Spearman correlation KV eviction score PyTorch LLM"
- **Key code:** `ScorerPress.compress()` — shows standard pattern for attention-based KV scoring
- **Used for:** Attention score aggregation pattern, understanding compression_ratio mechanics

**Repository B.3:** ngocbh/trimkv
- **URL:** https://github.com/ngocbh/trimkv
- **Relevance:** Confirms Locret is standard baseline in KV eviction comparison studies
- **Used for:** Verification that Locret checkpoint is standard-compatible

**Repository B.4:** yophis/DRM-Llama-3.1-8B-mnli (HuggingFace)
- **URL:** huggingface.co/yophis/DRM-Llama-3.1-8B-mnli
- **Key info:** LLaMA-3.1-8B with PEFT LoRA, task_type=SEQ_CLS, base_model=meta-llama/Meta-Llama-3.1-8B, trained on nyu-mll/glue
- **Used for:** Primary LoRA-MNLI checkpoint recommendation

### C. Code Analysis (Serena)

Serena analysis not performed — code from search results was sufficiently clear for this inference-only diagnostic experiment.

### D. Previous Hypothesis Context

None — H-E1 is the root hypothesis with no predecessors.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: GLUE MNLI | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Dataset loading code | Exa web search | HuggingFace datasets docs |
| Model: LLaMA-3.1-8B base | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Model: LoRA MNLI checkpoint | Exa web search | yophis/DRM-Llama-3.1-8B-mnli |
| Model: Locret checkpoint | Exa search | huangyuxiang03/Locret (B.1) |
| Locret CIS formula | Exa search | Locret paper arXiv:2410.01805 via B.1 |
| Attention extraction pattern | Archon KB | PyTorch SDPA docs (A.2) |
| Attention aggregation | Archon KB + Exa | A.3 (NVIDIA kvpress) |
| GQA head handling | Archon KB | PyTorch SDPA docs (A.2) |
| Spearman ρ computation | Standard library | scipy.stats.spearmanr |
| Success threshold ρ < 0.7 | Phase 2B | 02b_verification_plan.md H-E1 spec |
| Sample size: 100 examples | Phase 2B | 02b_verification_plan.md H-E1 spec |
| Extend to 500 if borderline | Phase 2B | 02b_verification_plan.md H-E1 spec |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T00:00:00

### Workflow History for This Hypothesis
- 2026-05-20T00:00:00: Phase 2B completed, H-E1 created with status IN_PROGRESS
- 2026-05-20: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
