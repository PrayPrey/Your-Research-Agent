# Product Requirements Document: H-E1

**Hypothesis:** Higher bandwidth reward signals (categorical + continuous) provide more bits of information per gradient update than binary signals
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-29
**Author:** Anonymous

---

## Executive Summary

This experiment validates whether multi-signal reward functions (combining categorical error types + continuous test pass ratios) accelerate PPO training convergence compared to binary pass/fail rewards for code generation tasks.

**Core Question:** Does higher information bandwidth in reward signals enable faster learning?

---

## Problem Statement

Binary reward signals (pass=1, fail=0) provide minimal gradient information per training step. When code fails tests, the model receives no indication of *how close* it was or *why* it failed. This information bottleneck may slow convergence.

**Proposed Solution:** Multi-signal rewards encoding:
1. Error category (syntax/runtime/assertion/pass) - 2 bits
2. Test pass ratio (continuous) - continuous signal
3. Partial credit for numeric closeness - continuous signal

---

## Functional Requirements

### FR-1: Dataset Pipeline
- Load MBPP dataset (374 train, 90 val, 500 test problems)
- Load HumanEval (164 problems) for generalization evaluation
- Parse test cases from MBPP test_list field
- Format prompts for CodeLlama instruction format

### FR-2: Model Setup
- Load CodeLlama-7B-Instruct from Hugging Face
- Configure for PPO training via TRL library
- Support bfloat16 precision for memory efficiency

### FR-3: Reward Function Implementation
Implement 3 reward computation modes:

| Condition | Reward Computation |
|-----------|-------------------|
| Binary | 1.0 if all tests pass, else 0.0 |
| Categorical | Error type score: passed=1.0, assertion=0.5, runtime=0.25, syntax=0.0 |
| High-Bandwidth | 0.5*categorical + 0.3*pass_ratio + 0.2*partial_credit |

### FR-4: Code Execution Sandbox
- Safe execution of generated Python code
- Capture error types (syntax, runtime, assertion)
- Extract expected/actual values for partial credit computation
- Timeout handling (5s per test case)

### FR-5: PPO Training Loop
- TRL PPOTrainer integration
- Configurable reward function selection
- Logging of rewards, KL divergence, loss metrics
- Checkpoint saving per epoch

### FR-6: Evaluation Pipeline
- pass@1 computation on MBPP test split
- pass@1 computation on HumanEval
- Samples-to-threshold tracking (pass@1 > 0.3)

### FR-7: Visualization
- Learning curves: pass@1 vs training samples (all conditions)
- Convergence speed bar chart
- Reward distribution histograms

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (5 seeds per condition)
- Deterministic data loading order
- Version pinning for transformers, TRL, datasets

### NFR-2: Compute Constraints
- Single GPU training (A100 40GB or equivalent)
- Batch size 4 per device
- 3 epochs per condition

### NFR-3: Memory Efficiency
- bfloat16 model weights
- Gradient checkpointing if needed

---

## Success Criteria

### Gate Condition (MUST_WORK)
High-bandwidth condition reaches pass@1 > 0.3 in fewer training samples than binary condition.

**Measurement:**
- samples_to_threshold(high_bandwidth) < samples_to_threshold(binary)
- OR if threshold not reached: pass@1(high_bandwidth) > pass@1(binary) at fixed sample count

### Statistical Requirements
- 5 random seeds per condition
- Report mean ± std for all metrics
- p < 0.05 for condition comparison

---

## Data Specifications

### Input Data
| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| MBPP | google-research-datasets/mbpp | 374 train, 500 test | Training + primary eval |
| HumanEval | openai_humaneval | 164 test | Generalization eval |

### Output Data
| Artifact | Format | Location |
|----------|--------|----------|
| Checkpoints | PyTorch | checkpoints/{condition}_{seed}/ |
| Metrics | JSON | results/metrics.json |
| Figures | PNG | figures/*.png |

---

## Dependencies

### Python Packages
- transformers >= 4.40.0
- trl >= 0.8.0
- datasets >= 2.18.0
- torch >= 2.2.0
- evaluate >= 0.4.0

### Hardware
- GPU: NVIDIA A100 40GB (or equivalent)
- RAM: 64GB recommended

---

## Out of Scope

- Token-level reward attribution (future work)
- Other base models beyond CodeLlama-7B
- Other RL algorithms beyond PPO
- Multi-GPU distributed training

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Location |
|---------------|--------------|
| MBPP dataset | FR-1, Data Specifications |
| HumanEval eval | FR-1, FR-6 |
| CodeLlama-7B-Instruct | FR-2 |
| 3 reward conditions | FR-3 |
| pass@1 metric | FR-6, Success Criteria |
| 5 seeds, 3 epochs | NFR-1, NFR-2 |
| Visualization | FR-7 |
