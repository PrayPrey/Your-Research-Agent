# Product Requirements Document: H-M2
## JointLoRA-KV — Joint End-to-End Training Stability and LongBench-QA Accuracy

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis ID:** H-M2
**Hypothesis Type:** MECHANISM (INCREMENTAL — depends on H-E1)
**Phase:** 3 — Implementation Planning
**Date:** 2026-05-20
**Author:** Anonymous
**Gate:** MUST_WORK — Joint training converges stably (no NaN/divergence across 3 seeds) AND JointLoRA-KV LongBench-QA F1 ≥ B3 F1 at 50% KV budget

---

## 1. Executive Summary

H-M2 tests the technical feasibility of jointly training LoRA adapter parameters and Locret retaining head parameters in a single backward pass via task classification cross-entropy loss. The hypothesis asserts that since LoRA A/B matrices and Locret retaining head weights (W1, W2) are architecturally disjoint parameter sets with independent gradient paths, joint optimization converges stably and achieves accuracy no worse than B3 (sequential LoRA→Locret fine-tune) on LongBench-QA at 50% KV budget.

**Success Condition (MUST_WORK gate):**
1. **Stability:** Zero NaN events, no loss spike >2× moving average across all 3 seeds (42, 123, 456)
2. **Accuracy:** JointLoRA-KV mean LongBench-QA F1 ≥ B3 mean LongBench-QA F1 at budget_ratio=0.5

---

## 2. Problem Statement

H-E1 confirmed that LM-loss-trained Locret eviction heads are systematically misaligned with task-specific LoRA attention patterns (mean ρ=0.3662 < 0.7 threshold). H-M2 addresses the next question: can LoRA adapters and Locret retaining heads be jointly trained in a single end-to-end pass without gradient interference, preserving or improving accuracy compared to the sequential baseline B3?

The key mechanism: LoRA A/B matrices (injected into Q/K/V projections via PEFT) and Locret retaining head MLPs (W1/W2 appended per attention layer) are disjoint parameter sets. A shared AdamW optimizer with separate parameter groups and independent learning rates (LoRA: lr=1e-4, Locret: lr=5e-4) enables joint optimization without interference.

---

## 3. Functional Requirements

### FR-1: JointLoRA-KV Model Implementation
- **FR-1.1:** Load `meta-llama/Meta-Llama-3.1-8B` with `attn_implementation="eager"` and `torch_dtype=torch.bfloat16`
- **FR-1.2:** Wrap model with PEFT LoRA: r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj"], lora_dropout=0.05, bias="none"
- **FR-1.3:** Load Locret retaining heads (from `hyx21/Locret-llama-3.1-8B-instruct` or train from scratch) as warm initialization for Locret W1/W2
- **FR-1.4:** Both LoRA A/B matrices AND Locret W1/W2 weights must have `requires_grad=True` during joint training
- **FR-1.5:** CIS score formula: S̃ = σ([Q,K,V] @ W1) @ W2 (W1 ∈ R^{(d_model+2*d_kv)×1024}, W2 ∈ R^{1024×8})
- **FR-1.6:** Soft budget masking during training (differentiable top-k approximation), hard top-k eviction at inference
- **FR-1.7:** GQA compatibility: expand 8 KV heads to 32 query heads via `repeat_interleave(4)` for CIS score computation
- **FR-1.8:** KV budget ratio: 0.5 (50% retention) applied during both training (soft) and inference (hard)

### FR-2: Baseline B3 — Sequential LoRA → Locret Fine-tune (Primary Baseline)
- **FR-2.1:** Stage 1: LoRA fine-tune on GLUE (MNLI/SST-2/QNLI) task CE loss with same config as JointLoRA-KV (r=16, lora_alpha=32)
- **FR-2.2:** Stage 2: Freeze all LoRA parameters (`param.requires_grad = False`), train only Locret retaining heads using LM distillation loss (original Locret objective)
- **FR-2.3:** Source: `huangyuxiang03/Locret` official training script adapted for GLUE
- **FR-2.4:** Evaluate at budget_ratio=0.5 on LongBench-QA test sets
- **FR-2.5:** B3 serves as primary comparison baseline for MUST_WORK gate

### FR-3: Training Protocol — JointLoRA-KV
- **FR-3.1:** Optimizer: Single AdamW with two parameter groups:
  - Group 1 (LoRA): `lora_params = [p for n,p in model.named_parameters() if "lora_" in n and p.requires_grad]`, lr=1e-4
  - Group 2 (Locret): `locret_params = [p for n,p in model.named_parameters() if "retaining_head" in n and p.requires_grad]`, lr=5e-4
- **FR-3.2:** weight_decay=0.01, betas=(0.9, 0.999), eps=1e-8
- **FR-3.3:** LR schedule: linear warmup (10% of total steps) + cosine decay
- **FR-3.4:** Batch size: 8 per device, gradient accumulation steps=4 (effective batch=32)
- **FR-3.5:** Epochs: 3 on GLUE training splits (MNLI: 392,702 / SST-2: 67,349 / QNLI: 104,743 train examples)
- **FR-3.6:** Seeds: 42, 123, 456 (3 independent runs, each complete training)
- **FR-3.7:** Gradient clipping: max_norm=1.0
- **FR-3.8:** Precision: bfloat16 for model; float32 for loss computation
- **FR-3.9:** GPU: single GPU, `CUDA_VISIBLE_DEVICES=<empty_gpu>`

### FR-4: Stability Monitoring (CRITICAL for MUST_WORK gate)
- **FR-4.1:** Log training loss every step for all 3 seeds
- **FR-4.2:** NaN detection: check `torch.isnan(loss)` every step; log and halt if detected
- **FR-4.3:** Divergence detection: flag if `loss.item() > 2 * moving_average_loss` (window=100 steps)
- **FR-4.4:** Log gradient norms per parameter group: LoRA grad norm and Locret grad norm every 50 steps
- **FR-4.5:** Store stability report: `{seed}/stability_log.json` with NaN events, divergence events, final loss
- **FR-4.6:** Gate check: stability_passed = (nan_events == 0 AND divergence_events == 0) for ALL 3 seeds

### FR-5: LongBench-QA Evaluation (Primary Accuracy Metric)
- **FR-5.1:** Evaluate JointLoRA-KV and B3 on LongBench test sets at budget_ratio=0.5 (hard eviction at inference)
- **FR-5.2:** NarrativeQA: 200 test examples, QA F1 score via `qa_f1_score` from THUDM/LongBench metrics.py
- **FR-5.3:** Qasper: 200 test examples, QA F1 score
- **FR-5.4:** MultiFieldQA-en: 150 test examples, QA F1 score
- **FR-5.5:** Mean LongBench-QA F1 = average across 3 tasks (primary gate metric)
- **FR-5.6:** Load via `load_dataset("THUDM/LongBench", task_name, split="test")`
- **FR-5.7:** Report mean ± std across 3 seeds

### FR-6: GLUE Evaluation (Secondary/Monitoring Metric)
- **FR-6.1:** Evaluate JointLoRA-KV on GLUE validation sets (monitoring training quality)
- **FR-6.2:** MNLI: accuracy on `validation_matched` (9,815 examples)
- **FR-6.3:** SST-2: accuracy on `validation` (872 examples)
- **FR-6.4:** QNLI: accuracy on `validation` (5,463 examples)
- **FR-6.5:** Use `evaluate.load("glue", task_name)` for metric computation
- **FR-6.6:** Load via `load_dataset("nyu-mll/glue", task_name)`

### FR-7: Visualization Requirements
- **FR-7.1 (MANDATORY):** Bar chart — JointLoRA-KV vs B3 LongBench-QA F1 (per task + mean), saved to `h-m2/figures/longbench_comparison.png`
- **FR-7.2:** Training loss curves for all 3 seeds per-step, saved to `h-m2/figures/training_loss_curves.png`
- **FR-7.3:** Loss distribution box plot at epoch end per seed, saved to `h-m2/figures/loss_distribution.png`
- **FR-7.4:** Per-task F1 breakdown for JointLoRA-KV vs B3, saved to `h-m2/figures/per_task_f1.png`
- **FR-7.5:** Gradient norm plot (LoRA group vs Locret group over training), saved to `h-m2/figures/gradient_norms.png`

---

## 4. Data Specification

### Dataset 1: GLUE Benchmark (Training)
- **Source:** HuggingFace Hub `nyu-mll/glue`
- **Subtasks:** MNLI, SST-2, QNLI
- **Splits used:** train (joint training), validation (GLUE eval)
- **Loading:** `load_dataset("nyu-mll/glue", "mnli")`, `"sst2"`, `"qnli"` — AUTO-DOWNLOAD via HuggingFace datasets
- **Preprocessing:** Tokenize with LLaMA tokenizer, max_length=512 (GLUE short-context tasks)
- **No manual download required**

### Dataset 2: LongBench-QA (Evaluation)
- **Source:** HuggingFace Hub `THUDM/LongBench`
- **Subtasks:** narrativeqa, qasper, multifieldqa_en
- **Splits used:** test only
- **Loading:** `load_dataset("THUDM/LongBench", "narrativeqa", split="test")` etc. — AUTO-DOWNLOAD
- **Preprocessing:** Use THUDM/LongBench eval scripts (`eval.py`, `metrics.py`)
- **No manual download required**

---

## 5. Non-Functional Requirements

- **NFR-1:** Reproducibility — 3 seeds produce consistent results (loss std across seeds ≤ 0.1 at epoch 1 end)
- **NFR-2:** Memory efficiency — single GPU (H100 NVL or equivalent) with bfloat16 precision
- **NFR-3:** Training time — each seed run completes within 4 hours on single GPU
- **NFR-4:** Code organization — modular: trainer, model wrapper, evaluator, stability monitor as separate modules
- **NFR-5:** Checkpoint saving — save best checkpoint per seed, load for evaluation

---

## 6. Success Criteria

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| Stability: NaN events | = 0 across all 3 seeds | MUST_WORK (required) |
| Stability: Divergence events | = 0 (no loss spike >2×) across all 3 seeds | MUST_WORK (required) |
| Accuracy: JointLoRA-KV mean LongBench-QA F1 | ≥ B3 mean LongBench-QA F1 at budget_ratio=0.5 | MUST_WORK (required) |
| Accuracy: JointLoRA-KV GLUE mean accuracy | ≥ B3 GLUE mean accuracy (secondary) | Informational |

**Gate Logic:**
- If stability AND accuracy criteria both met → MUST_WORK gate SATISFIED → H-M3 proceeds
- If NaN or divergence in ANY seed → gate FAILS → H-M3 blocked, route to Phase 0
- If stability passes but accuracy < B3 → gate FAILS → H-M3 blocked

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.1.0
transformers>=4.40.0
peft>=0.10.0
datasets>=2.18.0
evaluate>=0.4.0
accelerate>=0.28.0
bitsandbytes>=0.43.0
scikit-learn>=1.4.0
matplotlib>=3.8.0
numpy>=1.26.0
PyYAML>=6.0
tqdm>=4.66.0
```

### 7.2 External Repositories
- **huangyuxiang03/Locret** (PRIMARY): Official Locret implementation for LLaMA-3.1-8B; retaining head architecture reference and B3 baseline training script
- **THUDM/LongBench**: LongBench evaluation framework (`eval.py`, `metrics.py`, `qa_f1_score`)
- **awslabs/keys_values**: Reference for joint LoRA+KV single-backward-pass training pattern

### 7.3 Model Checkpoints
- **meta-llama/Meta-Llama-3.1-8B**: Base model (HuggingFace Hub, requires access token)
- **hyx21/Locret-llama-3.1-8B-instruct** (optional): Pre-trained Locret heads for warm initialization

### 7.4 Prerequisite Hypothesis
- **H-E1** (COMPLETED): Confirmed misalignment (mean ρ=0.3662 < 0.7); validates motivation for joint training; confirms LoRA and Locret parameters are architecturally disjoint

---

## 8. Out of Scope

- Comparison with H2O, SnapKV, StreamingLLM (H-M3 scope)
- Full GLUE benchmark beyond MNLI/SST-2/QNLI
- LongBench tasks beyond NarrativeQA/Qasper/MultiFieldQA-en
- Quantization (INT4/INT8) experiments
- Multi-GPU distributed training
- Hyperparameter search (fixed by Phase 2B controlled variables)

---

*Generated by Phase 3 PRD Workflow (UNATTENDED)*
*Input: h-m2/02c_experiment_brief.md*
*Next: Phase 3 Architecture Agent*
