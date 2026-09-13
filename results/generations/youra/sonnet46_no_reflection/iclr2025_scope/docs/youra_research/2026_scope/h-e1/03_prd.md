# Product Requirements Document: H-E1
# LoRA-KV Misalignment Diagnostic Experiment

---
## Frontmatter

```yaml
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-05-20
phase: Phase 3
stepsCompleted:
  - Phase 2B verification plan
  - Phase 2C experiment design
source: 02c_experiment_brief.md
```

---

## 1. Executive Summary

H-E1 is an inference-only diagnostic experiment that measures the Spearman rank correlation between LoRA-adapted attention weights and Locret retaining head CIS (Causal Importance Score) scores on LLaMA-3.1-8B. The hypothesis asserts that these scores are systematically misaligned (mean Spearman ρ < 0.7) for task-discriminative tokens in MNLI, establishing the motivating premise for joint training (H-M1 through H-M4).

**No training is required.** The experiment loads two pre-trained models and computes correlation statistics across 100 MNLI validation examples.

---

## 2. Problem Statement

Task-specific fine-tuning via LoRA modifies attention weight distributions to focus on task-discriminative tokens (e.g., hypothesis markers, contrast words in MNLI). However, Locret's retaining heads are trained via LM distillation loss, which rewards high-frequency next-token-predictive tokens rather than task-discriminative tokens. If these two scoring mechanisms are misaligned (low Spearman ρ), then:

1. KV eviction under Locret will discard tokens that LoRA attention has learned to be task-relevant
2. Sequential LoRA→Locret fine-tuning (Baseline B3) cannot resolve this misalignment
3. Joint training (JointLoRA-KV) is needed to align eviction priorities with task-specific attention

H-E1 provides the empirical foundation (existence proof) for this misalignment.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- **Requirement:** Load GLUE MNLI `validation_matched` split using HuggingFace datasets
- **Dataset ID:** `nyu-mll/glue`, config `mnli`
- **Sample size:** First 500 examples (fixed, deterministic); primary evaluation on first 100
- **Labels:** 3-class (entailment=0, neutral=1, contradiction=2)
- **Tokenization:** Max sequence length 512 tokens
- **Code:**
  ```python
  from datasets import load_dataset
  dataset = load_dataset("nyu-mll/glue", "mnli")
  val_data = dataset["validation_matched"].select(range(500))
  ```

### FR-2: LoRA-Adapted Model Loading
- **Requirement:** Load LLaMA-3.1-8B with LoRA fine-tuned on MNLI (task classification)
- **Primary checkpoint:** `yophis/DRM-Llama-3.1-8B-mnli` (PeftModel, task_type=SEQ_CLS)
- **Base model:** `meta-llama/Meta-Llama-3.1-8B`
- **LoRA config:** rank=16, alpha=32, target_modules=[q_proj, k_proj, v_proj]
- **Critical:** `attn_implementation="eager"` REQUIRED to enable `output_attentions=True`
- **Fallback:** If primary checkpoint incompatible, fine-tune LoRA r=16 on MNLI for 3 epochs (AdamW, LR=1e-4, batch_size=16)
- **Code:**
  ```python
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  from peft import PeftModel
  import torch
  base_model = AutoModelForSequenceClassification.from_pretrained(
      "meta-llama/Meta-Llama-3.1-8B",
      num_labels=3,
      attn_implementation="eager",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  model = PeftModel.from_pretrained(base_model, "yophis/DRM-Llama-3.1-8B-mnli")
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
  ```

### FR-3: Locret Model Loading
- **Requirement:** Load LLaMA-3.1-8B with Locret retaining heads (LM-distillation-trained)
- **Checkpoint:** `hyx21/Locret-llama-3.1-8B-instruct`
- **Retaining head architecture:** MLP over concatenated [Q, K, V]: `CIS = sigma([Q,K,V]@W1)@W2`
- **Output:** CIS scores shape `(batch, seq_len, num_kv_heads)` per layer
- **Loading:** Use official Locret loading code from `huangyuxiang03/Locret` repository

### FR-4: LoRA Attention Score Extraction
- **Requirement:** Extract per-token attention weights from LoRA-adapted model
- **Method:** `output_attentions=True` in model forward pass (requires eager mode)
- **Shape:** `(B, num_heads, L, L)` → aggregate over query axis → `(num_heads, L)`
- **GQA structure:** 32 query heads / 8 KV heads per layer, 32 layers total
- **Code:**
  ```python
  outputs = model(input_ids, attention_mask=attention_mask, output_attentions=True)
  attn = outputs.attentions[layer_idx]  # (1, 32, L, L)
  per_token_attn = attn.sum(dim=2).squeeze(0)  # (32, L) — sum over query axis
  ```

### FR-5: Locret CIS Score Extraction
- **Requirement:** Extract CIS scores from Locret retaining heads per layer
- **Output shape:** `(num_kv_heads, seq_len)` = `(8, L)` for GQA
- **Method:** `output_retaining_scores=True` in Locret model forward pass

### FR-6: Spearman Correlation Computation
- **Requirement:** Compute mean Spearman ρ between LoRA attention scores and Locret CIS scores
- **GQA handling:** Expand KV heads (8) to match query heads (32) via `repeat_interleave(4, dim=0)`
- **Per-example:** Compute per-head Spearman ρ, average across all 32 heads
- **Final metric:** Average across all 100 examples → `mean_rho ± std`
- **Library:** `scipy.stats.spearmanr`
- **Code:**
  ```python
  from scipy.stats import spearmanr
  import numpy as np
  cis_expanded = cis_scores.repeat_interleave(4, dim=0)  # (32, L)
  rhos = []
  for h in range(32):
      rho, _ = spearmanr(lora_scores[h].cpu().float().numpy(),
                         cis_expanded[h].cpu().float().numpy())
      rhos.append(rho)
  mean_rho_example = np.mean(rhos)
  ```

### FR-7: Borderline Extension
- **Requirement:** If `mean_rho ∈ [0.65, 0.75]`, extend evaluation to 500 examples and SST-2, QNLI datasets
- **SST-2:** `nyu-mll/glue`, config `sst2`
- **QNLI:** `nyu-mll/glue`, config `qnli`

### FR-8: Visualization
- **Required figure:** Bar chart — mean Spearman ρ vs. threshold 0.7
- **Additional figures:**
  - Per-layer ρ heatmap (layer × head)
  - Token-level scatter plot (5 representative examples)
  - Distribution histogram of per-example mean ρ
- **Output path:** `h-e1/figures/`

---

## 4. Data Specification

| Dataset | Source | Split | Size | Access |
|---------|--------|-------|------|--------|
| GLUE MNLI | `nyu-mll/glue` (HuggingFace) | `validation_matched` | 9,815 total; use first 500 (primary: 100) | Auto-download via HuggingFace datasets |
| GLUE SST-2 (borderline only) | `nyu-mll/glue` | `validation` | 872 | Auto-download |
| GLUE QNLI (borderline only) | `nyu-mll/glue` | `validation` | 5,463 | Auto-download |

**Note:** All datasets auto-download via HuggingFace. No manual download required.

---

## 5. Evaluation Metrics

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| `mean_spearman_rho` | Mean Spearman ρ across 100 examples × all heads | < 0.7 → PASS |
| `std_spearman_rho` | Standard deviation of per-example ρ | Report only |
| `per_head_rho` | Per-head Spearman ρ distribution | Report only |
| `per_layer_rho` | Per-layer Spearman ρ heatmap | Report only |

**Gate:** MUST_WORK — `mean_rho < 0.7` required to unblock H-M1 through H-M4.

---

## 6. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Hardware | Single GPU (lowest-memory-usage GPU via `nvidia-smi`) |
| Memory | ~16GB VRAM (float16, LLaMA-3.1-8B) |
| Precision | float16 |
| Seed | Fixed seed=42 |
| Batch size | 1 (sequential processing for attention extraction) |
| Max seq length | 512 tokens |
| Reproducibility | Fixed indices (first N examples, seed=42 shuffle) |
| Flash Attention | DISABLED — must use `attn_implementation="eager"` |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
peft>=0.10.0
datasets>=2.14.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
accelerate>=0.27.0
huggingface_hub>=0.20.0
```

### 7.2 External Models/Repositories

| Resource | Identifier | Usage |
|----------|-----------|-------|
| LLaMA-3.1-8B base | `meta-llama/Meta-Llama-3.1-8B` | Base model |
| LoRA-MNLI checkpoint | `yophis/DRM-Llama-3.1-8B-mnli` | Task-adapted attention extraction |
| Locret checkpoint | `hyx21/Locret-llama-3.1-8B-instruct` | CIS score extraction |
| Locret code | `huangyuxiang03/Locret` (GitHub) | Model loading reference |
| NVIDIA kvpress | `NVIDIA/kvpress` (GitHub) | Attention aggregation patterns |

---

## 8. Success Criteria

| Criterion | Requirement |
|-----------|-------------|
| Code runs without error | Attention extraction + CIS extraction + Spearman computation |
| `mean_spearman_rho < 0.7` | H-E1 PASSES (MUST_WORK gate satisfied) |
| Results saved to file | `h-e1/results/spearman_correlation_results.json` |
| Figures generated | At least bar chart + heatmap |

**Borderline handling:** If `mean_rho ∈ [0.65, 0.75]`, extend to 500 examples. Final decision based on extended results.

**Failure response:** If `mean_rho ≥ 0.7`, revisit assumption A1 (task-attention vs. LM-eviction misalignment). Run gradient attribution experiment before abandoning hypothesis chain.

---

## 9. Out of Scope

- Joint training of LoRA + Locret (covered in H-M1, H-M2)
- Evaluation on LongBench (covered in H-M3)
- Linear probing on KV representations (covered in H-M4)
- Comparison against Baseline B3 (covered in H-M3)
- Multiple seeds (single seed=42 sufficient for EXISTENCE PoC)

---

## 10. Implementation Notes

1. **Two-model inference:** Both models must be loaded (possibly on different GPUs or sequentially to manage memory)
2. **Eager attention mode:** Flash Attention must be explicitly disabled; `attn_implementation="eager"` is non-negotiable
3. **GQA head expansion:** LLaMA-3.1-8B uses 32 query heads and 8 KV heads; CIS scores must be expanded before correlation computation
4. **Layer selection:** Average over all 32 layers; optionally highlight middle layers (14–18)
5. **Token filtering:** Focus correlation on non-padding tokens only (use attention_mask)
