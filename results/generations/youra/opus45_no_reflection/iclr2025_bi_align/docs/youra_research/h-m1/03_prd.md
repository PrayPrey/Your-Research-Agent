# Product Requirements Document: H-M1

**Date:** 2026-08-18
**Hypothesis:** L_agency integrates stably with DPO loss (training completes, loss decreases)
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This PRD defines requirements for validating BiDPO training stability. The experiment tests whether the agency-preservation loss (L_agency) can be combined with standard DPO loss without destabilizing optimization. Success is defined as training completion without NaN/Inf errors and monotonically decreasing total loss.

---

## Problem Statement

Standard DPO optimizes for human preference alignment but may inadvertently reduce user agency by training models to be overly directive. BiDPO proposes adding an auxiliary loss term (L_agency = 1 - collab_score) to preserve collaborative behavior. Before evaluating BiDPO's effectiveness, we must first verify that the multi-objective training remains stable.

**Prerequisite:** H-E1 demonstrated collab_score is orthogonal to preference labels (r=-0.026), validating it as a meaningful auxiliary signal.

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

| Requirement | Specification |
|-------------|---------------|
| Dataset | Anthropic HH-RLHF |
| Train Split | ~170K preference pairs |
| Test Split | ~8.5K preference pairs |
| Tokenizer | Mistral tokenizer, max_length=1024 |
| Preprocessing | Compute collab_score_v2 for all pairs |

### FR-2: Model Initialization

| Requirement | Specification |
|-------------|---------------|
| Base Model | mistralai/Mistral-7B-Instruct-v0.2 |
| Policy Model | Clone of base, trainable |
| Reference Model | Frozen copy for DPO |
| Precision | bfloat16 |
| Device | GPU with auto device_map |

### FR-3: BiDPO Loss Implementation

| Component | Formula |
|-----------|---------|
| L_DPO | -E[log σ(β(log π_θ(y+)/π_ref(y+) - log π_θ(y-)/π_ref(y-)))] |
| L_agency | (1 - collab_score_chosen) - 0.5*(1 - collab_score_rejected) |
| L_total | L_DPO + λ * L_agency |
| Beta | 0.1 |
| Lambda | 0.5 |

### FR-4: Training Loop

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning Rate | 5e-7 |
| LR Schedule | Cosine with 10% warmup |
| Batch Size | 4 (effective 16 with grad accum) |
| Gradient Accumulation | 4 |
| Epochs | 1 |
| Gradient Clipping | 1.0 |
| Logging Interval | Every 100 steps |

### FR-5: Stability Monitoring

| Check | Implementation |
|-------|----------------|
| NaN/Inf Detection | Check each loss component every step |
| Gradient Norm | Track via clip_grad_norm_ |
| Loss Components | Log dpo_loss, agency_loss, total_loss separately |
| Early Stop | If NaN detected, save debug info and exit |

### FR-6: Visualization Generation

| Figure | Description |
|--------|-------------|
| training_loss_curves.png | Line plot: dpo_loss, agency_loss, total_loss vs steps |
| gradient_norm.png | Gradient magnitude over training |
| lr_schedule.png | Learning rate visualization |

---

## Non-Functional Requirements

### NFR-1: Memory Efficiency
- Use bfloat16 precision
- Gradient checkpointing if needed
- Target: fit on single 80GB GPU

### NFR-2: Reproducibility
- Set random seeds (42)
- Log all hyperparameters
- Save training config YAML

### NFR-3: Checkpoint Management
- Save final checkpoint
- Save best checkpoint (lowest loss)

---

## Success Criteria

### Primary Gate Conditions

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Training Completion | No NaN/Inf | All loss values finite |
| Loss Decrease | total_loss_final < total_loss_initial | After warmup period |

### Secondary Metrics

| Metric | Target |
|--------|--------|
| DPO Loss Stability | No divergence |
| Agency Loss Range | Within [0, 2] |
| Gradient Norm | < 10.0 throughout |

---

## Dependencies

### From H-E1 (Prerequisite)
- `collab_score_v2()` function implementation
- Validated feature extraction pipeline

### External
- HuggingFace transformers
- HuggingFace datasets
- PyTorch
- wandb (logging)

---

## Out of Scope

- Model quality evaluation (H-M2)
- Benchmark performance (H-M3, H-M4)
- Lambda hyperparameter search
- Multi-GPU training

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Coverage |
|---------------|--------------|
| Dataset: HH-RLHF | FR-1 |
| Model: Mistral-7B | FR-2 |
| BiDPO Loss | FR-3 |
| Training Protocol | FR-4 |
| Stability Checks | FR-5 |
| Visualizations | FR-6 |

---

*Generated from Phase 2C experiment brief*
*Next: Architecture Document*
