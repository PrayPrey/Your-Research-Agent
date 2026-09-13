---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-12
author: Anonymous
status: Phase 3 - Implementation Planning
derived_from: 02c_experiment_brief.md
---

# Product Requirements Document: h-e1 LoRA-MoE Coordination

## Executive Summary

**Hypothesis:** Under intermediate task heterogeneity (mean pairwise KL divergence 0.3-1.5), joint LoRA-MoE training with performance-weighted alignment achieves super-additive efficiency gains exceeding the additive baseline by ≥2% absolute accuracy.

**Goal:** Validate the existence of super-additive coordination benefits through a proof-of-concept implementation.

**Success Criteria:** 
- Primary: proposed_accuracy > baseline_accuracy (direction check)
- Secondary: Super-additive gain > 0% (any positive coordination benefit)
- Tertiary: Alignment loss decreases during training (coordination learning)

## Problem Statement

Current multi-task learning approaches achieve only additive gains when combining LoRA adapters and MoE experts. We hypothesize that performance-weighted alignment between adapter routing and expert utilization can produce super-additive gains (≥2% above additive baseline) in intermediate heterogeneity regimes.

## Functional Requirements

### FR-1: Dataset Management
**Priority:** HIGH  
**Description:** Load and preprocess GLUE + SuperGLUE multi-task benchmark suite (17 tasks)

**Requirements:**
- Load GLUE tasks: CoLA, SST-2, MRPC, QQP, MNLI, QNLI, RTE, WNLI, STS-B
- Load SuperGLUE tasks: BoolQ, CB, COPA, MultiRC, ReCoRD, RTE, WiC, WSC
- Tokenization: max_length=512, dynamic padding per batch
- Task-specific label encoding
- Batch size: 32 (effective with gradient accumulation=4)

### FR-2: Baseline Model Implementation
**Priority:** HIGH  
**Description:** Implement Mixtral-8x7B baseline with standard inference

**Requirements:**
- Load pretrained Mixtral-8x7B-v0.1 from HuggingFace
- Top-2 expert routing (native MoE behavior)
- BFloat16 mixed precision
- Device mapping: auto (multi-GPU if available)
- Freeze base model weights during training

### FR-3: Proposed Model - LoRA-MoE Coordination
**Priority:** CRITICAL  
**Description:** Implement performance-weighted LoRA-MoE coordination mechanism

**Requirements:**
- **LoRA Configuration:**
  - Rank: 8-16
  - Alpha: 16-32 (2×rank)
  - Dropout: 0.05
  - Target modules: q_proj, k_proj, v_proj, o_proj (attention only)
  - Number of LoRA experts: 8

- **Router Implementation:**
  - Linear projection: hidden_dim → num_lora_experts
  - Top-K gating: K=2
  - Softmax activation

- **Coordination Loss:**
  - Performance-weighted KL divergence alignment
  - Loss weight λ=0.01
  - Task performance weights updated per epoch

### FR-4: Training Pipeline
**Priority:** HIGH  
**Description:** Implement multi-task training with coordination

**Requirements:**
- Optimizer: AdamW (lr=3e-4, betas=(0.9, 0.999), weight_decay=0.01)
- Learning rate schedule: Cosine annealing with 500-step warmup
- Training: 5 epochs per task (~12K total steps)
- Loss: Task loss + λ × Coordination loss + Auxiliary loss (0.01)
- Gradient accumulation: 4 steps
- Single seed: 42 (EXISTENCE PoC)

### FR-5: Evaluation System
**Priority:** HIGH  
**Description:** Task-specific metrics and aggregate performance

**Requirements:**
- **Metrics:**
  - Average accuracy across 17 tasks
  - Per-task accuracy
  - Super-additive gain: coordinated - (LoRA-only + MoE-only)
  - Expert utilization balance (entropy)
  - Routing alignment correlation

- **Baselines:**
  - Baseline: Frozen Mixtral-8x7B
  - LoRA-only: LoRA without coordination
  - MoE-only: Native MoE without LoRA
  - Proposed: LoRA-MoE with coordination

- **Gate Check:**
  - Direction: proposed > baseline
  - Magnitude: super-additive gain > 0%

### FR-6: Visualization
**Priority:** MEDIUM  
**Description:** Generate required figures for validation

**Requirements:**
- Gate metrics comparison (mandatory)
- Training curves (loss, coordination loss)
- Expert utilization heatmap
- Per-task performance comparison
- Save to: {hypothesis_folder}/figures/

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (CUDA_VISIBLE_DEVICES management)
- Training time: <24 hours on single A100/H100
- Memory: Within 80GB VRAM (with BFloat16 + quantization if needed)

### NFR-2: Reproducibility
- Fixed seed: 42
- Deterministic algorithms where possible
- Save all hyperparameters to config
- Log experiment configuration

### NFR-3: Code Quality
- Modular architecture (separate modules for model, data, training, eval)
- Clear separation: baseline vs proposed
- Documented configuration parameters
- Error handling for dataset loading failures

### NFR-4: Output Requirements
- Checkpoint saving: best model by validation accuracy
- Metrics logging: per-epoch and per-task
- Figure generation: automatic at training end
- Validation report: 04_validation.md with gate results

## Dependencies

### External Libraries
- torch >= 2.0
- transformers >= 4.44.0
- peft >= 0.11.1
- datasets (HuggingFace)
- accelerate (for device mapping)
- matplotlib, seaborn (visualization)

### Datasets
- GLUE: HuggingFace datasets ("glue" with task configs)
- SuperGLUE: HuggingFace datasets ("aps/super_glue")

### Models
- Mixtral-8x7B-v0.1: HuggingFace transformers
- Requires: ~100GB download, BFloat16 precision

### Implementation References
- MixLoRA (TUDB-Labs/MixLoRA): Router architecture, auxiliary loss
- Align-LoRA (arXiv 2508.05078): KL divergence alignment
- LiME (Kowsher/LiME): Parameter-efficient patterns

## Data Specifications

### Input Format
- Text pairs (premise, hypothesis) for NLI tasks
- Single sentences for classification
- Context-question pairs for QA tasks
- Task-specific tokenization with padding

### Output Format
- Metrics JSON: {task_name: {accuracy, f1, ...}}
- Figures: PNG files in figures/ directory
- Checkpoint: .pt file with model state dict
- Validation report: 04_validation.md (markdown)

## Success Criteria

### Primary Success (Gate Pass)
1. Code executes without errors
2. proposed_accuracy > baseline_accuracy (direction check)
3. Super-additive gain > 0% (coordination benefit exists)

### Secondary Success
- Alignment loss decreases during training
- Expert utilization balanced (entropy > threshold)
- All 17 tasks complete evaluation

### Failure Conditions
- Runtime errors (dataset load, model OOM)
- proposed_accuracy ≤ baseline_accuracy
- Super-additive gain ≤ 0% (no coordination benefit)

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OOM during training | HIGH | 4-bit quantization, gradient checkpointing |
| Dataset download failure | MEDIUM | Retry logic, local caching |
| Alignment loss divergence | HIGH | Loss weight tuning (λ), gradient clipping |
| Expert collapse | MEDIUM | Auxiliary loss (0.01), load balancing |

## Implementation Priority

1. **CRITICAL (Must Have):**
   - FR-3: Proposed model implementation
   - FR-4: Training pipeline
   - FR-5: Evaluation system

2. **HIGH (Should Have):**
   - FR-1: Dataset management
   - FR-2: Baseline model

3. **MEDIUM (Nice to Have):**
   - FR-6: Visualization
   - NFR-2: Reproducibility enhancements

## Constraints

- **Budget:** LIGHT tier (≤15 tasks total)
- **Scope:** EXISTENCE PoC (single seed, minimal ablations)
- **Time:** Single experiment run
- **Resources:** Single GPU

## Acceptance Criteria

**Phase 3 Complete When:**
- [ ] All 5 documents generated (PRD, Architecture, Logic, Config, Tasks)
- [ ] Architecture has 4-8 Epic tasks
- [ ] Total task count ≤ 15
- [ ] Archon project created with 5 documents

**Phase 4 Complete When:**
- [ ] Code executes without errors
- [ ] Gate check passes (proposed > baseline)
- [ ] 04_validation.md generated
- [ ] Figures saved to figures/

## References

- Phase 2C Experiment Brief: 02c_experiment_brief.md
- MixLoRA: https://github.com/TUDB-Labs/MixLoRA
- Align-LoRA: arXiv 2508.05078
- GLUE Benchmark: https://gluebenchmark.com/
- SuperGLUE: https://super.gluebenchmark.com/

---

*Generated from Phase 2C experiment design for Phase 3 implementation planning*
