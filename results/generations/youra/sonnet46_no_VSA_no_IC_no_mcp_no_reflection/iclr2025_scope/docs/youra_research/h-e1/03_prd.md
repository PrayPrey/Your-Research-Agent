---
title: "PRD: h-e1 — Mamba-130m LoRA GLUE Fine-tuning (EXISTENCE PoC)"
hypothesis_id: h-e1
type: EXISTENCE
stepsCompleted: [prd]
date: "2026-08-31"
author: yoon303@ust.ac.kr
---

# Product Requirements Document: h-e1

## 1. Executive Summary

This PRD specifies the implementation requirements for **h-e1**, an EXISTENCE (Proof-of-Concept) experiment that validates whether standard HuggingFace PEFT LoRA can be applied to a Mamba-130m State Space Model (SSM) for GLUE benchmark fine-tuning, achieving >70% accuracy on SST-2 (the primary gate metric).

**Gate Condition**: `sst2_accuracy_lora > 0.70` (MUST_WORK).  
**If fails**: H-M1, H-M2, H-M3 are blocked.

---

## 2. Problem Statement

Standard transformer-based LLMs use self-attention layers as LoRA targets (`q_proj`, `v_proj`). Mamba SSMs replace attention with selective state-space mechanisms, exposing different linear projection layers (`in_proj`, `out_proj`, `x_proj`). It is unconfirmed in this pipeline whether HuggingFace PEFT LoRA (without custom patching) successfully transfers to Mamba's projection layers for downstream classification tasks. This PoC answers: **does projection-only LoRA work on Mamba-130m for GLUE?**

---

## 3. Hypothesis & Success Criteria

### 3.1 Hypothesis
Under fine-tuning of Mamba-130m on GLUE (SST-2, MNLI, QNLI, QQP) with projection-only LoRA (Condition A: `in_proj`, `out_proj`, `x_proj`, r=8), GLUE average accuracy exceeds 70% on SST-2 and is non-trivially above zero-shot baseline, confirming that standard LoRA PEFT transfers to Mamba SSMs.

### 3.2 Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| SST-2 LoRA accuracy | > 70% | PRIMARY (gate) |
| GLUE avg LoRA > zero-shot GLUE avg | directional | SECONDARY |
| Code runs without error | TRUE | BLOCKER |
| LoRA weights in state_dict (nonzero) | TRUE | BLOCKER |

### 3.3 Expected Performance

| Task | Zero-shot (baseline) | LoRA r=8 (expected) |
|------|---------------------|---------------------|
| SST-2 | ~55–62% | ~90–92% |
| MNLI | ~35–40% | ~82–85% |
| QNLI | ~50–55% | ~88–90% |
| QQP (F1) | ~60–65% | ~87–89% |
| **GLUE avg** | **~50–56%** | **~87–89%** |

---

## 4. Data Specification

### 4.1 Primary Dataset: GLUE Benchmark

| Task | Train | Validation | Metric |
|------|-------|------------|--------|
| SST-2 | 67,349 | 872 | Accuracy |
| MNLI | 392,702 | 9,815 (matched) | Accuracy |
| QNLI | 104,743 | 5,463 | Accuracy |
| QQP | 363,846 | 40,430 | F1 |

- **Source**: HuggingFace `datasets` library (`load_dataset("glue", "<task>")`)
- **Download**: Auto-download (no manual step required)
- **Evaluation**: Validation split (GLUE test labels are private)

### 4.2 Preprocessing

| Parameter | Value |
|-----------|-------|
| Tokenizer | `AutoTokenizer.from_pretrained("state-spaces/mamba-130m-hf")` |
| Max length | 128 tokens |
| Truncation | Right-side |
| Padding | Dynamic (pad_right or no padding for causal LM) |
| Augmentation | None |

### 4.3 Static Baselines (Zero-shot Evaluation)

Zero-shot baseline: Mamba-130m evaluated on GLUE validation sets **without LoRA or task-specific fine-tuning**. Uses the same classification head (randomly initialized) — or majority-class prediction — as a lower bound reference. Results stored for gate comparison.

---

## 5. Functional Requirements

### FR-01: Environment Setup
- Install: `torch`, `transformers`, `peft`, `datasets`, `evaluate`, `accelerate`, `scipy`
- Python ≥ 3.10, CUDA optional (CPU fallback acceptable for debug)

### FR-02: Model Loading — Mamba-130m Base
- Load `state-spaces/mamba-130m-hf` via `AutoModelForCausalLM.from_pretrained()`
- Wrap with custom `MambaForSequenceClassification` head (last-token pooling + linear classifier)
- Verify `conv1d` is NOT in `target_modules` (raises TypeError if included)

### FR-03: LoRA Configuration (Condition A)
- Apply HuggingFace PEFT `LoraConfig`:
  - `target_modules = ["in_proj", "out_proj", "x_proj"]`
  - `r = 8`, `lora_alpha = 16`, `lora_dropout = 0.05`, `bias = "none"`
- Call `get_peft_model(base_model, lora_cfg)`
- Print trainable parameters: expected ~0.5–1% of total

### FR-04: Per-task Fine-tuning
- Fine-tune independently on each of 4 GLUE tasks (SST-2, MNLI, QNLI, QQP)
- Optimizer: AdamW, lr=3e-4, weight_decay=0.01, betas=(0.9, 0.999)
- Schedule: Linear warmup (6% steps) + linear decay
- Batch size: 32, Epochs: 3, Seed: 42

### FR-05: Zero-shot Baseline Evaluation
- Evaluate Mamba-130m WITHOUT LoRA on all 4 GLUE tasks
- Record zero-shot accuracies/F1 for gate comparison

### FR-06: LoRA Fine-tuned Evaluation
- Evaluate fine-tuned model on GLUE validation sets
- Compute: SST-2 acc, MNLI acc, QNLI acc, QQP F1, GLUE avg
- Use `evaluate.load("glue", "<task>").compute()`

### FR-07: Mechanism Verification
- Verify LoRA weight keys exist in `state_dict` (`lora_A`, `lora_B` patterns)
- Verify LoRA weights are nonzero post-training
- Verify accuracy improved over zero-shot on SST-2

### FR-08: Results Logging
- Save per-task results to `h-e1/results/results.json`
- Log: zero-shot metrics, LoRA metrics, GLUE avg, gate outcome, mechanism indicators
- Format: JSON with structured keys

### FR-09: Visualization
- **Required**: Bar chart comparing SST-2 zero-shot vs LoRA accuracy with 70% gate line marked
- Additional (autonomous): training loss curves (4 subplots), GLUE avg grouped bar, LoRA weight magnitude heatmap
- Save figures to `h-e1/figures/`

### FR-10: Gate Evaluation
- Auto-evaluate: `sst2_lora_acc > 0.70` → PASS/FAIL
- Print gate result to stdout
- Record in `results.json`: `{"gate_passed": true/false, "gate_metric": sst2_lora_acc}`

---

## 6. Non-Functional Requirements

### NFR-01: Reproducibility
- Fixed seed: 42 throughout (torch, numpy, random, transformers)
- Single-seed sufficient (EXISTENCE PoC — directional check only)

### NFR-02: Performance
- Training time: ≤ 2 hours total for 4 GLUE tasks on single GPU
- VRAM: ≤ 8GB (Mamba-130m + LoRA at batch 32)

### NFR-03: Code Quality
- Single entrypoint script (`train_eval.py`) per task, or unified script with `--task` arg
- No hardcoded paths — all paths parameterized

### NFR-04: Failure Handling
- If `conv1d` detected in target_modules → explicit error + fix message
- If GLUE dataset download fails → retry with timeout
- If GPU unavailable → fallback to CPU with warning

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.38.0
peft>=0.9.0
datasets>=2.18.0
evaluate>=0.4.0
accelerate>=0.27.0
scipy>=1.12.0
matplotlib>=3.8.0
seaborn>=0.13.0
numpy>=1.26.0
```

### 7.2 External Models / Data
- HF Hub: `state-spaces/mamba-130m-hf` (auto-download)
- HF Hub: GLUE dataset via `datasets` library (auto-download)
- No proprietary data required

### 7.3 Hardware
- Single GPU (A100/V100 preferred; ~4–8 GB VRAM)
- CPU fallback for debugging (slow but functional)

---

## 8. Out of Scope

- Multi-seed runs / statistical significance testing (MECHANISM phase)
- LoRA rank ablation (`r` = 4, 16, 32) — deferred to H-M1/M2
- `dt_proj` as LoRA target (Condition B) — deferred to H-M1
- Multi-task training (each task fine-tuned independently)
- Production deployment
- GLUE test-set submission (labels private)

---

## 9. Acceptance Criteria

Phase 3 → Phase 4 handoff is complete when:

1. `03_architecture.md`, `03_logic.md`, `03_config.md` generated ✓
2. `03_tasks.yaml` generated with ≤15 tasks ✓
3. Phase 4 Coder can implement from specs without ambiguity ✓

Phase 4 experiment is complete when:

1. `h-e1/results/results.json` exists with all 8 metrics (4 zero-shot + 4 LoRA)
2. `gate_passed` field present and evaluated
3. All required figures in `h-e1/figures/`
4. `verify_lora_activated()` returns True
