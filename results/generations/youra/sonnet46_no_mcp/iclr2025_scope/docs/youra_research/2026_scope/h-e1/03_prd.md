# PRD: H-E1 — Eviction-Aware LoRA Weight Divergence (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Phase:** 3 - Implementation Planning
**Type:** EXISTENCE (MUST_WORK gate)
**Generated:** 2026-05-04
**Tier:** LIGHT (max 15 tasks)

---

## 1. Executive Summary

H-E1 tests whether applying H2O eviction masks during the LoRA training forward pass
produces adapter weights that are statistically different from weights trained without
masking. This is the foundational existence check: if eviction-aware training does NOT
change the gradient signal (and therefore the adapter weights), then the entire
Eviction-Aware LoRA hypothesis chain (H-M1, H-M2, H-M3) is invalidated.

**Outcome:** Two trained LoRA adapters (baseline vs. eviction-aware) compared via
per-layer cosine similarity on lora_A and lora_B matrices. Gate passes if
`min(cosine_similarity) < 0.95` in at least one layer.

---

## 2. Problem Statement

Standard LoRA fine-tuning followed by H2O KV cache eviction at inference (sequential
baseline) may suffer from a training-inference distribution mismatch: the adapter was
trained on full attention, but evaluated on evicted attention. H-E1 tests whether
training WITH H2O eviction masks changes the LoRA adapter parameters at all — a
necessary precondition for any performance benefit from joint training.

**Research Question:** Does applying H2O-style attention masking during LoRA training
forward pass cause measurable divergence in adapter weight matrices compared to standard
LoRA training?

---

## 3. Scope

### In Scope
- Train two LoRA adapters on LLaMA-2-7B: baseline (no mask) vs. eviction-aware (H2O mask r=0.5)
- Train two LoRA adapters on Mistral-7B-v0.1: same condition
- Compute per-layer cosine similarity between baseline and eviction-aware lora_A, lora_B
- Compare mean cosine similarity and identify layers below 0.95 threshold
- Generate visualization: bar chart of per-layer cosine similarity with 0.95 threshold line

### Out of Scope
- Downstream accuracy evaluation (LongBench) — this is H-M3
- Multiple budget ratios (r=0.25, r=0.75) — only r=0.5 for H-E1
- Attention pattern analysis — this is H-M1

---

## 4. Data Specification

### 4.1 Fine-Tuning Dataset

| Field | Value |
|-------|-------|
| Name | LongAlpaca-12k |
| Source | `Yukang/LongAlpaca-12k` (HuggingFace Hub) |
| Split | train (full, ~12,000 samples) |
| Type | Long-context instruction-following pairs |
| Sequence length | 8k–32k tokens |
| Download method | Auto (HuggingFace datasets library) |
| Manual download required | ❌ No — auto-download via HuggingFace Hub |

```python
from datasets import load_dataset
dataset = load_dataset("Yukang/LongAlpaca-12k", split="train")
```

**Note:** No evaluation dataset needed for H-E1. The dependent variable is adapter
weight cosine similarity, not downstream task accuracy.

### 4.2 Data Preprocessing

- Tokenize with model-specific tokenizer (`AutoTokenizer.from_pretrained(...)`)
- Truncate/pad to `max_seq_length=32768`
- Use standard causal LM format (instruction + response)

---

## 5. Functional Requirements

### FR-1: Baseline LoRA Training (LLaMA-2-7B)
Train standard LoRA adapter on LLaMA-2-7B with LongAlpaca-12k. No eviction mask.
Save adapter weights to `outputs/h-e1/llama2-7b-baseline/`.

**Config:**
- LoRA rank=16, alpha=32, dropout=0.05, targets=[q_proj, v_proj]
- Optimizer: AdamW, lr=2e-4, cosine schedule, warmup_ratio=0.03
- Batch: 1 per GPU, gradient_accumulation=16 (effective batch=16)
- Epochs: 1, max_seq_length=32768, seed=42

### FR-2: Eviction-Aware LoRA Training (LLaMA-2-7B)
Train LoRA adapter on LLaMA-2-7B with H2O eviction mask (r=0.5) injected at attention
logit level during forward pass. Save adapter weights to
`outputs/h-e1/llama2-7b-eviction-aware/`.

**H2O Mask Injection:** Applied at attention score level (before softmax), using
cumulative attention score thresholding (top-50% tokens retained). Mask is deterministic
and applied during training forward pass only.

**All other config identical to FR-1.**

### FR-3: Baseline LoRA Training (Mistral-7B-v0.1)
Same as FR-1 but on Mistral-7B-v0.1. Save to `outputs/h-e1/mistral-7b-baseline/`.

### FR-4: Eviction-Aware LoRA Training (Mistral-7B-v0.1)
Same as FR-2 but on Mistral-7B-v0.1. Save to `outputs/h-e1/mistral-7b-eviction-aware/`.

### FR-5: Weight Divergence Analysis
Load both adapter pairs (baseline vs. eviction-aware) per model. Compute:
- Per-layer cosine similarity for lora_A matrices
- Per-layer cosine similarity for lora_B matrices
- Mean cosine similarity across all layers
- Count of layers with cosine similarity < 0.95

```python
import torch.nn.functional as F

def compute_layer_cosine_similarity(baseline_sd, proposed_sd):
    results = {}
    for key in baseline_sd:
        if 'lora_A' in key or 'lora_B' in key:
            b = baseline_sd[key].flatten()
            p = proposed_sd[key].flatten()
            results[key] = F.cosine_similarity(b.unsqueeze(0), p.unsqueeze(0)).item()
    return results
```

### FR-6: PoC Gate Evaluation
Evaluate MUST_WORK gate:
- **PASS:** `min(cosine_similarity_per_layer) < 0.95` for at least one model
- **FAIL:** All layers ≥ 0.95 for both models

Save gate result to `outputs/h-e1/gate_result.json`.

### FR-7: Visualization
Generate figures saved to `docs/youra_research/20260504_scope/h-e1/figures/`:
- **Required:** Bar chart of per-layer cosine similarity with 0.95 threshold line (both models)
- **Optional:** Heatmap (layers × matrix type: A, B), L2 norm difference line plot,
  cosine similarity histogram, LLaMA-2-7B vs Mistral-7B-v0.1 side-by-side comparison

---

## 6. Non-Functional Requirements

| Requirement | Specification |
|------------|---------------|
| Reproducibility | Fixed seed=42 for all training runs |
| GPU usage | Single GPU only (`CUDA_VISIBLE_DEVICES=<empty_gpu_id>`) |
| Precision | float16 for model loading; bfloat16 if available |
| Logging | WandB or CSV logging of training loss per step |
| Checkpointing | Save final adapter only (no intermediate checkpoints) |
| Runtime estimate | ~2–4h per training run on single A100/V100 |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
datasets>=2.16.0
accelerate>=0.25.0
bitsandbytes>=0.41.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference)

| Repository | URL | Purpose |
|------------|-----|---------|
| FMInference/H2O | github.com/FMInference/H2O | H2O eviction mask reference implementation |
| huggingface/peft | github.com/huggingface/peft | LoRA adapter library (install via pip) |
| dvlab-research/LongLoRA | github.com/dvlab-research/LongLoRA | Training config reference for LongAlpaca-12k |

---

## 8. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Code runs without error | Both training runs complete | MUST |
| Gate metric (primary) | `min(cosine_similarity) < 0.95` in ≥1 layer | MUST |
| Mean cosine similarity | `mean(cosine_similarity) < 0.99` | SHOULD |
| Dual-model validation | Result holds for ≥1 of 2 models | MUST |
| Figures generated | Bar chart with threshold line exists | MUST |

**MUST_WORK Gate:** If the primary gate criterion fails for BOTH models, the experiment
fails and H-M1, H-M2, H-M3 are blocked pending investigation of mask injection method.

---

## 9. Evaluation Protocol

1. Train baseline LLaMA-2-7B (FR-1) → save adapter
2. Train eviction-aware LLaMA-2-7B (FR-2) → save adapter
3. Train baseline Mistral-7B-v0.1 (FR-3) → save adapter
4. Train eviction-aware Mistral-7B-v0.1 (FR-4) → save adapter
5. Run weight divergence analysis (FR-5) → compute cosine similarities
6. Evaluate gate (FR-6) → record PASS/FAIL
7. Generate figures (FR-7) → save to figures/

**Sequential execution required** (each model pair before analysis).

---

## 10. File Output Structure

```
outputs/h-e1/
├── llama2-7b-baseline/          # FR-1 adapter weights
├── llama2-7b-eviction-aware/    # FR-2 adapter weights
├── mistral-7b-baseline/         # FR-3 adapter weights
├── mistral-7b-eviction-aware/   # FR-4 adapter weights
├── weight_analysis_llama2.json  # FR-5 per-layer cosine similarities
├── weight_analysis_mistral.json # FR-5 per-layer cosine similarities
└── gate_result.json             # FR-6 PASS/FAIL with metrics

docs/youra_research/20260504_scope/h-e1/figures/
├── cosine_similarity_bar_llama2.png
├── cosine_similarity_bar_mistral.png
└── (optional additional figures)
```

---

*Generated by Phase 3 Step 2 (inline PRD generation — BMAD PRD workflow.md not found in this environment)*
*Source: h-e1/02c_experiment_brief.md*
*Hypothesis: H-E1 | Type: EXISTENCE | Gate: MUST_WORK*
