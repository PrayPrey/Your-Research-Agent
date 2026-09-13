# Product Requirements Document: H-M3

**Date:** 2026-08-28
**Hypothesis:** H-M3 - Task-Conditioned SSM Training Integration
**Phase:** 3 - Implementation Planning

---

## 1. Problem Statement

Validate that TC-SSM preserves adaptation capability when task conditioning is integrated during training. Standard SSM conversion loses transformer's few-shot adaptation quality. H-M3 tests whether joint training with task conditioning preserves this capability.

## 2. Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| Primary | Few-shot accuracy gap | Within 5% of transformer baseline |
| Secondary | Adaptation speed | <100 gradient steps |
| Tertiary | TC-SSM > Standard Mamba | Must be true |

## 3. Scope

### In Scope
- TC-SSM module integration into Mamba-130M
- Conversion training pipeline (transformer → TC-SSM)
- Few-shot adaptation protocol (8-shot, 16-shot)
- SuperGLUE evaluation (BoolQ, CB, COPA, RTE, WiC)
- Comparison: TC-SSM vs Transformer vs Standard Mamba

### Out of Scope
- Larger model variants (>130M)
- Pre-training from scratch
- Non-SuperGLUE benchmarks
- Production deployment

## 4. Dependencies

### Prerequisites (Completed)
- H-M1: Task embedding mechanism (PASS)
- H-M2: Low-rank SSM modulation (PASS, rank=32)

### External
- state-spaces/mamba (official implementation)
- huggingface/peft (LoRA baseline)
- HuggingFace datasets (SuperGLUE)

## 5. Technical Requirements

### 5.1 Core Components

| Component | Requirement |
|-----------|-------------|
| TaskConditionedSSMBlock | Modulate Δ, B, C via low-rank task projections |
| ConversionTrainer | KL + MSE + adaptation regularizer loss |
| FewShotEvaluator | SuperGLUE tasks, k={8,16} |
| BaselineRunner | Standard Mamba + LoRA comparison |

### 5.2 Data Requirements

- SuperGLUE full validation sets for evaluation
- 8 and 16 stratified samples per task for few-shot
- 3 random seeds for statistical validity

### 5.3 Compute Requirements

- GPU: 1x A100 (40GB) or equivalent
- Time estimate: 4-6 hours total
- Checkpointing: Every 25 steps

## 6. Deliverables

1. `tc_ssm.py` - TaskConditionedSSMBlock implementation
2. `conversion_trainer.py` - Conversion training pipeline
3. `few_shot_eval.py` - Few-shot evaluation protocol
4. `run_experiment.py` - Main experiment script
5. `h-m3/figures/` - Visualization outputs
6. `04_validation.md` - Validation report

## 7. Risk Assessment

| Risk | Mitigation |
|------|------------|
| Conversion training diverges | Gradient clipping, lower LR |
| Few-shot variance high | 3 seeds, confidence intervals |
| OOM on A100 | Gradient checkpointing enabled |

## 8. Verification Protocol

Per 02c_experiment_brief.md:
- Mechanism activation check (different task_ids → different outputs)
- Modulation magnitude check (>1e-3)
- Gate metrics comparison visualization

---

*Generated: 2026-08-28*
*Source: 02c_experiment_brief.md*
