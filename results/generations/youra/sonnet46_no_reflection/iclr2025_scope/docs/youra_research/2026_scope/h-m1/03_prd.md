# Product Requirements Document: H-M1
## JointLoRA-KV — Task CE Loss Joint Training of LoRA Adapters and Locret Retaining Heads

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis ID:** H-M1
**Hypothesis Type:** MECHANISM (INCREMENTAL — depends on H-E1)
**Phase:** 3 — Implementation Planning
**Date:** 2026-05-20
**Author:** Anonymous
**Gate:** MUST_WORK — JointLoRA-KV GLUE accuracy ≥ B1 + 2.0 pp at budget_ratio=0.5

---

## 1. Executive Summary

H-M1 tests whether replacing the original Locret LM-distillation training loss with a task classification cross-entropy (CE) loss — while jointly training LoRA adapters — produces eviction policies that better preserve task-discriminative tokens. The hypothesis is that task CE gradients direct Locret retaining heads to score tokens by label-discriminativeness rather than next-token predictability, closing the misalignment gap confirmed in H-E1 (mean ρ=0.3662).

**Success Condition:** JointLoRA-KV achieves mean GLUE accuracy (MNLI/SST-2/QNLI, 3 seeds) ≥ B1 (frozen Locret baseline) + 2.0 percentage points at 50% KV budget.

---

## 2. Problem Statement

H-E1 demonstrated that LM-loss-trained Locret retaining heads are systematically misaligned with task-specific LoRA attention patterns (mean Spearman ρ=0.3662, well below 0.7 threshold). This misalignment means LM-trained eviction preserves tokens useful for language modeling but not for classification — causing accuracy drops when KV cache is compressed.

**H-M1 directly addresses this:** by training Locret retaining heads with task CE loss (and jointly updating LoRA adapters), the eviction policy learns to preserve tokens that maximize task classification performance.

---

## 3. Functional Requirements

### FR-1: JointLoRA-KV Model Implementation
- **FR-1.1:** Load LLaMA-3.1-8B-Instruct with `attn_implementation="eager"` and `torch_dtype=torch.float16`
- **FR-1.2:** Wrap model with PEFT LoRA (r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj"])
- **FR-1.3:** Load Locret retaining heads from `hyx21/Locret-llama-3.1-8B-instruct` as warm initialization
- **FR-1.4:** Both LoRA A/B matrices AND Locret W1/W2 head weights must receive gradient updates during training
- **FR-1.5:** Implement CIS score formula: S̃ = σ([Q,K,V] @ W1) @ W2 (W1 ∈ R^{(dm+2dkv)×1024}, W2 ∈ R^{1024×8})
- **FR-1.6:** Implement soft budget masking during training (gradient-differentiable); hard top-k eviction at inference
- **FR-1.7:** GQA compatibility: expand 8 KV heads to 32 query heads via `repeat_interleave(4)`

### FR-2: Baseline B1 — LoRA + Frozen Locret
- **FR-2.1:** Same LoRA configuration as JointLoRA-KV (r=16, lora_alpha=32)
- **FR-2.2:** Locret heads loaded from `hyx21/Locret-llama-3.1-8B-instruct` with ALL parameters frozen (`param.requires_grad = False`)
- **FR-2.3:** Train only LoRA parameters with task CE loss; Locret heads NOT updated
- **FR-2.4:** Evaluate at 50% KV budget (hard eviction using frozen Locret CIS scores)

### FR-3: Baseline B2 — LoRA + kvpress Heuristic Eviction
- **FR-3.1:** Same LoRA configuration as B1
- **FR-3.2:** Apply kvpress StreamingLLM/H2O heuristic eviction at inference only (no eviction training)
- **FR-3.3:** Evaluate at 50% KV budget using heuristic eviction scores

### FR-4: Training Protocol
- **FR-4.1:** Optimizer: AdamW with two parameter groups — LoRA params (lr=1e-4), Locret params (lr=5e-4)
- **FR-4.2:** weight_decay=0.01, betas=(0.9, 0.999), eps=1e-8
- **FR-4.3:** LR schedule: linear warmup (6% of total steps) + linear decay
- **FR-4.4:** Batch size: 8 per device, gradient accumulation steps=4 (effective batch=32)
- **FR-4.5:** Epochs: 3 for MNLI, 5 for SST-2 and QNLI
- **FR-4.6:** Seeds: 42, 123, 456 (3 independent runs)
- **FR-4.7:** Gradient clipping: max_norm=1.0
- **FR-4.8:** Precision: float16 for model loading, float32 for loss computation
- **FR-4.9:** GPU: single H100 NVL, `CUDA_VISIBLE_DEVICES=0`

### FR-5: GLUE Evaluation (Primary Metrics)
- **FR-5.1:** Evaluate JointLoRA-KV, B1, B2 on GLUE validation sets at budget_ratio=0.5
- **FR-5.2:** MNLI: accuracy on `validation_matched` (9,815 examples)
- **FR-5.3:** SST-2: accuracy on `validation` (872 examples)
- **FR-5.4:** QNLI: accuracy on `validation` (5,463 examples)
- **FR-5.5:** Report mean GLUE accuracy ± std across 3 seeds
- **FR-5.6:** Use `evaluate.load("glue", task_name)` for metric computation

### FR-6: LongBench-QA Evaluation (Secondary Metrics)
- **FR-6.1:** Evaluate at budget_ratio=0.5 on full test sets
- **FR-6.2:** NarrativeQA: ~200 test examples, QA F1 score
- **FR-6.3:** Qasper: ~200 test examples, QA F1 score
- **FR-6.4:** MultiFieldQA-en: ~150+ test examples, QA F1 score
- **FR-6.5:** Use `qa_f1_score` from THUDM/LongBench `metrics.py`
- **FR-6.6:** Load via `load_dataset("THUDM/LongBench", task_name, split="test")`

### FR-7: Mechanism Activation Verification
- **FR-7.1:** Log Locret gradient norm every training step: `"locret_grad_norm={norm:.4f}"`
- **FR-7.2:** Verify CIS output shape is (B, L, 8) per layer with values in (0, 1)
- **FR-7.3:** Verify tokens_retained_ratio < 0.55 (eviction is active)
- **FR-7.4:** Implement `verify_mechanism_activated()` function per experiment brief spec
- **FR-7.5:** Gate check: JointLoRA-KV mean GLUE ≥ B1 mean GLUE + 2.0 pp

### FR-8: Visualization
- **FR-8.1 (Mandatory):** Gate Metrics Comparison bar chart — JointLoRA-KV vs B1 vs B2 mean GLUE accuracy with ± std error bars
- **FR-8.2:** Training loss curves per epoch for all 3 seeds (convergence verification)
- **FR-8.3:** Per-task GLUE breakdown bars (MNLI/SST-2/QNLI separately)
- **FR-8.4:** Budget sensitivity curve — accuracy vs budget_ratio (0.3, 0.5, 0.7)
- **FR-8.5:** LongBench-QA F1 comparison bar chart
- **FR-8.6:** All figures saved to `h-m1/figures/`

---

## 4. Data Specification

### 4.1 Primary Dataset: GLUE Benchmark

| Task | Train | Validation | Classes | Load Code |
|------|-------|------------|---------|-----------|
| MNLI | 392,702 | 9,815 (matched) | 3 | `load_dataset("glue", "mnli")` |
| SST-2 | 67,349 | 872 | 2 | `load_dataset("glue", "sst2")` |
| QNLI | 104,743 | 5,463 | 2 | `load_dataset("glue", "qnli")` |

- **Preprocessing:** LlamaTokenizer, max_length=512, pad_to_max_length=True
- **Source:** HuggingFace datasets (auto-download) — NO manual download required
- **Split used:** train (fine-tuning), validation (evaluation)

### 4.2 Secondary Dataset: LongBench-QA

| Task | Test Examples | Metric | Load Code |
|------|---------------|--------|-----------|
| NarrativeQA | ~200 | QA F1 | `load_dataset("THUDM/LongBench", "narrativeqa", split="test")` |
| Qasper | ~200 | QA F1 | `load_dataset("THUDM/LongBench", "qasper", split="test")` |
| MultiFieldQA-en | ~150+ | QA F1 | `load_dataset("THUDM/LongBench", "multifieldqa_en", split="test")` |

- **Context length:** 5k–15k tokens (KV eviction meaningfully activated)
- **Source:** THUDM/LongBench (HuggingFace, auto-download) — NO manual download required
- **Eval script:** `qa_f1_score` from `LongBench/metrics.py`

### 4.3 Models

| Model | Source | Load Method |
|-------|--------|-------------|
| LLaMA-3.1-8B-Instruct | `meta-llama/Meta-Llama-3.1-8B-Instruct` | `AutoModelForCausalLM.from_pretrained(..., torch_dtype=torch.float16, attn_implementation="eager")` |
| Locret retaining heads | `hyx21/Locret-llama-3.1-8B-instruct` | Load .bin checkpoint, extract fc1/fc2 per layer |

- **Download method:** HuggingFace Hub (`from_pretrained`)
- **VRAM:** Sequential loading required (H100 budget); LoRA first, then Locret heads
- **Disk:** ~16GB (LLaMA-3.1-8B float16) + ~200MB (Locret heads)

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Training must complete within 24h wall time per GLUE task per seed on H100 NVL
- Inference must not cause OOM at batch_size=1 with 15k-token context (LongBench)

### NFR-2: Reproducibility
- All experiments use fixed seeds (42, 123, 456) with `torch.manual_seed`, `numpy.random.seed`, `random.seed`
- All hyperparameters captured in config files

### NFR-3: Code Quality
- Type hints on all public functions
- Tensor shapes documented in docstrings
- Mechanism activation checks must log to file (not just stdout)

### NFR-4: GPU Usage
- `CUDA_VISIBLE_DEVICES=0` (single GPU, H100 NVL)
- float16 inference, float32 loss computation

---

## 6. Success Criteria

### Primary (MUST_WORK Gate)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Code executes without error | Training loop completes all 3 seeds | No exception/NaN |
| JointLoRA-KV GLUE ≥ B1 + 2.0 pp | Mean across MNLI/SST-2/QNLI, 3 seeds | `mean_glue_acc(joint) - mean_glue_acc(b1) >= 2.0` |

### Secondary
| Criterion | Threshold |
|-----------|-----------|
| JointLoRA-KV GLUE ≥ B2 | Any margin positive |
| Locret grad_norm > 0 | Throughout training |
| Eviction active | tokens_retained_ratio < 0.55 |
| LongBench-QA improvement | JointLoRA-KV F1 ≥ B1 F1 |

### Expected Performance
- Vanilla LoRA MNLI (no compression): ~87-89%
- B1 (frozen Locret at 50%): ~84-87%
- JointLoRA-KV (task CE eviction): ~87-90%

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.40.0
peft>=0.10.0
datasets>=2.18.0
evaluate>=0.4.0
accelerate>=0.28.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories
- **Locret:** `huangyuxiang03/Locret` (for CIS formula reference and training patterns)
- **LongBench eval:** `THUDM/LongBench` (for `qa_f1_score` metric function)
- **kvpress:** For B2 baseline heuristic eviction at inference

### 7.3 Hardware
- GPU: NVIDIA H100 NVL (80GB HBM3)
- `CUDA_VISIBLE_DEVICES=0`
- Minimum VRAM: 40GB (float16 LLaMA-3.1-8B + LoRA + Locret heads)

### 7.4 Prerequisite Results (from H-E1)
- Confirmed: LM-loss-trained Locret misaligned with task LoRA (mean ρ=0.3662 < 0.7)
- Proven: `meta-llama/Meta-Llama-3.1-8B-Instruct` loadable on H100 in float16
- Proven: `hyx21/Locret-llama-3.1-8B-instruct` accessible and correctly loadable
- Proven: GLUE MNLI loading via `load_dataset("glue", "mnli")` working
- Proven: GQA expansion `repeat_interleave(4)` correct for 8→32 head expansion

---

## 8. Constraints and Assumptions

- **Fixed KV budget:** budget_ratio=0.5 (50% retention) throughout all experiments
- **LoRA config fixed:** r=16, lora_alpha=32, target_modules=["q_proj","k_proj","v_proj"] (from H-E1)
- **Locret architecture unchanged:** Only training loss changes (CE vs LM distillation); W1/W2 dimensions preserved
- **Warm init required:** Locret heads initialized from `hyx21/Locret-llama-3.1-8B-instruct` (not random)
- **eager attention:** `attn_implementation="eager"` required for KV tensor access (flash-attn blocks this)
- **Single GPU:** No multi-GPU/DDP — sequential model loading for VRAM management

---

## 9. Out of Scope

- Multi-GPU distributed training
- Quantization (QLoRA, GPTQ)
- Models other than LLaMA-3.1-8B-Instruct
- KV budget ratios other than 0.5 for primary evaluation (budget sensitivity is secondary)
- New Locret architecture variants (only training loss change)
- GLUE tasks beyond MNLI/SST-2/QNLI

---

## 10. Traceability

| Requirement | Source |
|-------------|--------|
| GLUE datasets | 02b_verification_plan.md §1.3, 02c_experiment_brief.md §Dataset |
| LongBench datasets | 02b_verification_plan.md §1.3, 02c_experiment_brief.md §Dataset |
| LLaMA-3.1-8B model | verification_state.yaml controlled_variables |
| JointLoRA-KV architecture | 02c_experiment_brief.md §Proposed Model |
| B1/B2 baselines | 02c_experiment_brief.md §Baseline Model |
| AdamW config | Archon KB (HuggingFace PEFT examples) |
| LR schedule (linear warmup) | Archon KB (PEFT GLUE notebook) |
| Separate LR (LoRA/Locret) | Exa (Locret paper training config) |
| Budget_ratio=0.5 | verification_state.yaml controlled_variables |
| Seeds 42/123/456 | verification_state.yaml controlled_variables |
| Success threshold +2pp | 02b_verification_plan.md H-M1 success criteria |
| CIS formula | 02c_experiment_brief.md §Architecture, Locret paper Eq. 1 |
