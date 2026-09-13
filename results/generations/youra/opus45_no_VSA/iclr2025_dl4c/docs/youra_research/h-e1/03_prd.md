# Product Requirements Document: H-E1

**Hypothesis:** Training×Refinement interaction > 0 on logit(pass@1), p<0.05, OR≥1.2
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-08
**Author:** Anonymous

---

## Executive Summary

Validate whether RL training with execution feedback creates synergy with test-time self-refinement for code generation. 2×2 factorial design: Training (CE vs RL) × Inference (Single vs Refine). Success = positive interaction effect on pass@1.

---

## Problem Statement

Standard cross-entropy training may not prepare models for iterative refinement. RL with execution feedback might induce feedback-conditioned edit policies that amplify refinement gains.

---

## Functional Requirements

### FR-1: Dataset Loading
- **FR-1.1**: Load HumanEval+ (164 problems) via `evalplus.data.get_human_eval_plus()`
- **FR-1.2**: Load MBPP+ (378 problems) via `evalplus.data.get_mbpp_plus()`
- **FR-1.3**: Cache datasets locally for reproducibility

### FR-2: Model Setup
- **FR-2.1**: Load CodeT5+-220M from `Salesforce/codet5p-220m`
- **FR-2.2**: Initialize 4 model variants for experimental conditions
- **FR-2.3**: Support LoRA fine-tuning (rank=16, target_modules=["q_proj", "k_proj", "v_proj"])

### FR-3: Training Pipeline
- **FR-3.1**: Cross-Entropy training (CE conditions)
  - AdamW optimizer, lr=2e-5, weight_decay=0.05
  - 10 epochs, batch_size=8
  - Warmup steps=200
- **FR-3.2**: RL training with execution feedback (RL conditions)
  - REINFORCE with test pass rate reward
  - 5 epochs after CE warmup
  - Log "RL reward: X.XX" each step

### FR-4: Inference Modes
- **FR-4.1**: Single-shot generation (temperature=0, greedy)
- **FR-4.2**: Self-Refine protocol (K=3 iterations)
  - Execute code, get feedback
  - Construct refine prompt with error message
  - Re-generate until pass or K exhausted

### FR-5: Evaluation
- **FR-5.1**: Compute pass@1 using evalplus framework
- **FR-5.2**: Evaluate all 4 conditions on HumanEval+
- **FR-5.3**: Secondary evaluation on MBPP+
- **FR-5.4**: Compute interaction effect: `(RL-Refine - RL-Single) - (CE-Refine - CE-Single)`

### FR-6: Visualization
- **FR-6.1**: 2×2 factorial bar chart (pass@1 per condition)
- **FR-6.2**: Interaction plot (Training × Refinement)
- **FR-6.3**: Save figures to `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Single seed (seed=42) for PoC
- Log all hyperparameters to config file
- Save model checkpoints per condition

### NFR-2: Compute Efficiency
- LoRA fine-tuning to reduce memory
- Single GPU training (RTX 3090 / A100 compatible)
- Target: <4 hours total training time

### NFR-3: Code Quality
- Modular trainer class (RLCodeTrainer)
- Separate scripts for train/evaluate/visualize
- Type hints on public APIs

---

## Success Criteria

### Gate Condition (MUST_WORK)
```
Interaction Effect > 0
(RL_Refine - RL_Single) > (CE_Refine - CE_Single)
```

### PoC Pass Conditions
1. All 4 conditions train without error
2. All 4 conditions evaluate on HumanEval+
3. Interaction effect is positive (direction only, no stat test)

---

## Dependencies

### External Libraries
- transformers>=4.30.0
- evalplus>=0.2.0
- peft>=0.4.0 (LoRA)
- torch>=2.0.0

### Models
- Salesforce/codet5p-220m (HuggingFace)

### Datasets
- evalplus/humanevalplus
- evalplus/mbppplus

---

## Out of Scope

- Multi-seed statistical analysis (deferred to H-M hypotheses)
- Larger models (>1B parameters)
- Alternative RL algorithms (PPO, DPO)
- Critic model training
