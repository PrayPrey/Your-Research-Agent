# Product Requirements Document: H-M2

**Hypothesis:** Token masking excludes non-executed code from gradient updates
**Type:** MECHANISM
**Date:** 2026-08-10
**Author:** Anonymous

---

## Executive Summary

Validate FGO (Fine-Grained Optimization) token masking mechanism that excludes non-executed code tokens from gradient computation during PPO training. This builds on H-M1's validated trace collection to implement selective gradient updates.

---

## Problem Statement

Standard PPO training computes gradients for ALL generated tokens, including code that never executes (dead branches, unreachable code). This wastes compute and may degrade learning signal quality. FGO masks non-executed tokens so only executed code contributes to policy updates.

---

## Functional Requirements

### FR-1: FGO Token Masking Implementation
- Implement `compute_fgo_masked_loss()` that applies execution mask to PPO loss
- Mask tensor shape: `[batch, seq_len]` where 1=executed, 0=not-executed
- Non-executed tokens must receive exactly ZERO gradient

### FR-2: Baseline Model - Standard PPO (No Masking)
- CodeLlama-7B-Instruct with standard PPO
- All tokens contribute to loss computation
- Serves as comparison baseline

### FR-3: Ablation - Random Masking
- Mask random tokens (matched sparsity to trace-based)
- Controls for masking effect vs trace-specific effect

### FR-4: Ablation - Trace-Based Masking (FGO)
- Use H-M1 execution traces to build mask
- Only executed tokens contribute to loss
- Primary experimental condition

### FR-5: Gradient Verification
- Log gradient norms for masked vs unmasked positions
- Verify masked tokens have gradient_norm = 0
- Verify unmasked tokens have gradient_norm > 0

### FR-6: Dataset Preparation
- HumanEval: 164 test problems
- MBPP: 500 test problems
- Total: 664 evaluation samples

### FR-7: Evaluation Pipeline
- pass@1 metric computation
- Statistical comparison (paired t-test, p < 0.05)
- 3 seeds: 42, 123, 456

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- Training: 1000 steps per condition
- Batch size: 16
- Context length: 4096 tokens

### NFR-2: Reproducibility
- Fixed seeds across all conditions
- Deterministic operations where possible
- All hyperparameters documented

---

## Success Criteria

| Criterion | Target | Priority |
|-----------|--------|----------|
| Trace-based > Random pass@1 | p < 0.05 | MUST |
| Masked token gradient = 0 | Exact zero | MUST |
| Unmasked token gradient > 0 | Non-zero | MUST |
| Training completes | All 3 conditions | MUST |

---

## Data Requirements

### Input Data
- HumanEval dataset (OpenAI)
- MBPP dataset (Google)
- Pre-trained CodeLlama-7B-Instruct weights

### Output Data
- Trained model checkpoints (3 conditions × 3 seeds)
- Evaluation results JSON
- Gradient verification logs
- Visualization figures

---

## Dependencies

- H-M1 trace collection mechanism (CONDITIONAL_PASS)
- PyTorch, Transformers, TRL libraries
- GPU with 40GB+ VRAM (A100 recommended)

---

## Appendix: Training Configuration

| Parameter | Value |
|-----------|-------|
| Algorithm | PPO |
| Learning Rate | 1e-5 |
| LR Schedule | Cosine decay |
| Batch Size | 16 |
| PPO Epochs | 4 |
| Clip Epsilon | 0.2 |
| GAE Lambda | 0.95 |
| Training Steps | 1000 |
