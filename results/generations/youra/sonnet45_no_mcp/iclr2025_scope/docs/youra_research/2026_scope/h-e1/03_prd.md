# Product Requirements Document: h-e1

**Date:** 2026-04-19
**Author:** Anonymous
**Hypothesis:** EXISTENCE - Oracle gap G_o ≥ 10% between per-task oracle and best fixed-rank baseline
**Type:** PoC Validation (LIGHT infrastructure)
**Version:** 1.0

---

## Executive Summary

This PRD defines requirements for implementing a multi-rank LoRA adapter experiment to validate the existence of an oracle gap in heterogeneous task environments. The system will train 4 LoRA adapters (ranks: 4, 8, 16, 32) across 17 tasks from GLUE and XTREME benchmarks, measure performance-efficiency trade-offs, and compute the oracle gap between per-task optimal configurations and the best fixed-rank baseline.

**Success Criterion:** Oracle gap G_o ≥ 10% (normalized hypervolume difference)

---

## Problem Statement

### Research Question
Do different tasks in multi-domain settings exhibit heterogeneous optimal adapter configurations such that a measurable oracle gap exists?

### Hypothesis
Under multi-domain benchmark evaluation, if tasks exhibit heterogeneous optimal adapter configurations, then oracle gap G_o ≥ 10% exists between per-task oracle and best fixed-rank baseline, because different tasks have fundamentally different performance-efficiency trade-offs.

### Gate Condition
**MUST_WORK:** Oracle gap G_o ≥ 10% with directional validation (no statistical test required for PoC)

---

## Functional Requirements

### FR-1: Multi-Domain Dataset Loading
**Priority:** P0 (Critical)
**Description:** Load and preprocess 17 tasks from GLUE and XTREME benchmarks

**Datasets:**
- GLUE: 9 tasks (CoLA, SST-2, MRPC, QQP, STS-B, MNLI, QNLI, RTE, WNLI)
- XTREME: 8 tasks (XNLI: 4 languages, PAWS-X: 4 languages)

**Requirements:**
- HuggingFace datasets library integration
- LLaMA-2 tokenizer with max_length=512
- Dynamic padding per batch
- Return DataLoader per task with train/validation splits

**Acceptance Criteria:**
- All 17 tasks load without error
- Tokenization produces correct tensor shapes [batch, seq_len]
- DataLoaders iterate correctly

---

### FR-2: Multi-Rank LoRA Adapter Factory
**Priority:** P0 (Critical)
**Description:** Create LoRA adapters with configurable ranks using PEFT library

**Configuration:**
- Base model: LLaMA-2-7B (`meta-llama/Llama-2-7b-hf`)
- Ranks: [4, 8, 16, 32]
- Target modules: q_proj, v_proj (attention layers)
- LoRA alpha: 16
- LoRA dropout: 0.1

**Requirements:**
- Use HuggingFace PEFT library (LoraConfig, get_peft_model)
- Support multiple num_labels per task (2 for binary, 3 for MNLI, etc.)
- Return trainable PeftModel instance

**Acceptance Criteria:**
- Adapters instantiate for all 4 ranks
- Parameter count matches O(d·r) scaling
- Adapters attach to LLaMA-2-7B correctly

---

### FR-3: Multi-Task Training Orchestration
**Priority:** P0 (Critical)
**Description:** Train 68 configurations (17 tasks × 4 ranks) with independent training runs

**Training Protocol:**
- Optimizer: AdamW (lr=3e-4, betas=(0.9, 0.999), weight_decay=0.01)
- Scheduler: Cosine annealing with 10% warmup
- Batch size: 16, gradient accumulation: 2 (effective batch: 32)
- Epochs: 3-5 (task-dependent on dataset size)
- Early stopping: patience=2 on validation loss
- Seed: 42 (fixed for PoC)

**Requirements:**
- Independent training run per (task, rank) pair
- Save checkpoint per configuration
- Log metrics: accuracy, loss, epoch time
- CSV logging (LIGHT tier - no WandB)

**Acceptance Criteria:**
- All 68 configurations train without error
- Checkpoints saved to `{output_dir}/{task}_{rank}/adapter_model.bin`
- Training metrics logged to CSV

---

### FR-4: Efficiency Metrics Collection
**Priority:** P0 (Critical)
**Description:** Measure parameter count and FLOPs for each adapter configuration

**Metrics:**
- **Parameter count:** Sum of trainable parameters (2 × d × r for LoRA)
- **FLOPs:** Floating-point operations per forward pass using fvcore library

**Requirements:**
- Use fvcore.nn.FlopCountAnalysis for FLOPs counting
- Count only adapter parameters (not base model)
- Measure on standardized input: [1, 512] sequence

**Acceptance Criteria:**
- FLOPs scale as O(d·r)
- Parameter count matches 2 × 4096 × r for LLaMA-2-7B
- Metrics stored per (task, rank) configuration

---

### FR-5: Task-Specific Performance Evaluation
**Priority:** P0 (Critical)
**Description:** Evaluate trained adapters using task-appropriate metrics

**Metrics:**
- Accuracy: Most GLUE tasks, XNLI, PAWS-X
- F1 score: QQP, MRPC (imbalanced)
- Pearson correlation: STS-B (regression)

**Requirements:**
- Use HuggingFace evaluate library
- Evaluate on full test sets (500-10k samples per task)
- Store per-task, per-rank results

**Acceptance Criteria:**
- All 68 configurations evaluated
- Results stored in structured format: `{task: {rank: {accuracy, f1, pearson}}}`

---

### FR-6: Hypervolume Computation
**Priority:** P0 (Critical)
**Description:** Compute hypervolume indicator on (accuracy, -FLOPs) Pareto space

**Method:**
- Library: pymoo (HV indicator)
- Objectives: Maximize accuracy, Minimize FLOPs
- Reference point: (0.0 accuracy, max_FLOPs across all ranks)

**Requirements:**
- Compute HV for each task's 4 configurations
- Aggregate across all 17 tasks
- Return scalar hypervolume value

**Acceptance Criteria:**
- Hypervolume computed for Oracle selection
- Hypervolume computed for each fixed-rank baseline
- Values are non-negative and bounded

---

### FR-7: Oracle Gap Calculation
**Priority:** P0 (Critical)
**Description:** Compute oracle gap between per-task oracle and best fixed-rank baseline

**Algorithm:**
```
For each task i in 17 tasks:
  - Select oracle rank r*_i = argmax_r accuracy_i_r (or best Pareto point)
  
HV_oracle = hypervolume(17 oracle selections)
HV_fixed_r = hypervolume(all tasks using rank r) for r in {4,8,16,32}
HV_best_fixed = max(HV_fixed_4, HV_fixed_8, HV_fixed_16, HV_fixed_32)

Oracle_gap = HV_oracle - HV_best_fixed
Oracle_gap_normalized = (Oracle_gap / HV_best_fixed) × 100%
```

**Requirements:**
- Select oracle per task (best rank by accuracy or Pareto dominance)
- Compute HV for oracle configuration
- Compute HV for each fixed-rank baseline
- Return normalized oracle gap percentage

**Acceptance Criteria:**
- Oracle gap G_o ≥ 10% → PoC PASS
- Oracle gap G_o < 10% → PoC FAIL
- Results logged with breakdown by task

---

### FR-8: Visualization Pipeline
**Priority:** P1 (Required for paper)
**Description:** Generate 5 figures for experiment analysis

**Required Figures:**
1. **Gate Metrics Comparison** (Mandatory)
   - Bar chart: Target (10%) vs Actual oracle gap
   - Single panel

2. **Per-Task Pareto Fronts**
   - 4×4 grid of 17 subplots
   - X-axis: FLOPs (log scale), Y-axis: Accuracy
   - 4 points per task (color-coded by rank)

3. **Oracle vs Fixed-Rank Comparison**
   - Bar chart: HV(oracle) vs HV(rank-4/8/16/32)
   - Annotation: Oracle gap percentage

4. **Rank Selection Heatmap**
   - Rows: 17 tasks, Columns: 4 ranks
   - Color: Accuracy value
   - Marker: Oracle selection per task

5. **Efficiency-Performance Trade-off**
   - 2D scatter: All 68 (task, rank) configurations
   - Pareto frontier highlighted
   - Oracle points marked with stars

**Requirements:**
- Use matplotlib for all figures
- Save to `{hypothesis_folder}/figures/*.png`
- Include in experiment code (not post-processing)

**Acceptance Criteria:**
- All 5 figures generated automatically
- Figures saved to correct directory
- Gate metrics chart always included

---

## Non-Functional Requirements

### NFR-1: Execution Time
**Priority:** P2
**Requirement:** Single GPU execution completes within reasonable time
**Target:** ~2-3 hours per adapter × 68 configurations = 140-200 hours
**Note:** Can parallelize across tasks with multiple GPUs

---

### NFR-2: Memory Efficiency
**Priority:** P1
**Requirement:** Fit on single A100 40GB GPU
**Configuration:**
- Model: LLaMA-2-7B in fp16
- Batch size: 16 with gradient accumulation
- LoRA adapters: ~2MB per rank (minimal overhead)

---

### NFR-3: Reproducibility
**Priority:** P1
**Requirement:** Fixed seed ensures deterministic results
**Configuration:**
- Random seed: 42
- Torch backends: cudnn.deterministic=True

---

### NFR-4: Logging (LIGHT Tier)
**Priority:** P1
**Requirement:** Minimal logging infrastructure
**Configuration:**
- Print to stdout for progress
- CSV files for metrics (no WandB, no MLflow)
- Checkpoint saving per configuration

---

## Data Specifications

### Input Data
- **GLUE:** HuggingFace datasets `glue` (9 task configs)
- **XTREME:** HuggingFace datasets `xnli`, `paws-x` (4 languages each)
- **Format:** Pre-tokenized text → LLaMA-2 tokenizer → [batch, seq_len] tensors

### Output Data
- **Checkpoints:** `{output_dir}/{task}_{rank}/adapter_model.bin`
- **Metrics:** `{output_dir}/results.csv` (68 rows)
- **Oracle Gap:** `{output_dir}/oracle_gap.json`
- **Figures:** `{hypothesis_folder}/figures/*.png`

---

## Success Criteria

### Gate Condition (MUST_WORK)
✅ **Oracle gap G_o ≥ 10%** (normalized hypervolume difference)

### PoC Pass Criteria
1. Code runs without error for all 68 configurations
2. Oracle gap computed successfully
3. `oracle_gap >= 0.10` (10% threshold)
4. All 5 figures generated

### PoC Fail Criteria
- Any configuration fails to train
- Oracle gap < 10%
- Missing required outputs

---

## Dependencies

### External Libraries
- **PyTorch:** 2.0+
- **HuggingFace:** transformers, peft, datasets, evaluate
- **Metrics:** pymoo (hypervolume), fvcore (FLOPs)
- **Visualization:** matplotlib, seaborn

### Model Weights
- **LLaMA-2-7B:** `meta-llama/Llama-2-7b-hf` from HuggingFace Hub
- **Tokenizer:** `meta-llama/Llama-2-7b-hf` tokenizer

### Compute Resources
- **GPU:** 1× A100 40GB (or equivalent)
- **Storage:** ~50GB (model weights + checkpoints + datasets)
- **Time:** 140-200 GPU hours (can parallelize)

---

## Out of Scope

### Not Included in EXISTENCE (PoC)
- ❌ Statistical significance testing (95% CI)
- ❌ Multiple seeds (only seed=42)
- ❌ Hyperparameter tuning
- ❌ Production infrastructure (YAML configs, dataclasses, unit tests)
- ❌ Advanced logging (WandB, MLflow)
- ❌ Model compression or optimization

---

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Training instability for some tasks | Medium | High | Use gradient clipping, early stopping |
| Memory overflow on 40GB GPU | Low | High | Use fp16, batch_size=16, gradient accumulation |
| HuggingFace Hub rate limiting | Low | Medium | Cache datasets locally |
| Oracle gap < 10% (hypothesis fails) | Medium | Critical | Accept null result, document findings |

---

## Glossary

- **Oracle Gap (G_o):** Difference in hypervolume between per-task optimal configurations and best fixed-rank baseline
- **Hypervolume (HV):** Volume under Pareto front on multi-objective space
- **LoRA Rank:** Dimension of low-rank matrices in adapter (controls capacity)
- **PEFT:** Parameter-Efficient Fine-Tuning library from HuggingFace
- **LIGHT Tier:** Minimal infrastructure (hardcoded config, print+CSV logging, smoke tests)

---

## Approval

**Status:** Approved for Phase 4 Implementation
**Next Phase:** Phase 4 - Coding & PoC Validation
**Tasks File:** 03_tasks.yaml (generated in Phase 3 Step 9)

---

*Generated by Phase 3 Implementation Planning*
*Based on: 02c_experiment_brief.md (Phase 2C output)*
*Infrastructure: LIGHT tier (EXISTENCE PoC validation)*
