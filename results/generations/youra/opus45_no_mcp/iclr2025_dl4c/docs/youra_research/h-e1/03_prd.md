# Product Requirements Document: h-e1

**Hypothesis:** Error-Type Gating Improves Sample Efficiency
**Date:** 2026-08-19
**Type:** EXISTENCE (PoC)
**Phase:** Implementation Planning

---

## Executive Summary

Validate that error-type-gated fine-grained feedback improves RL training sample efficiency for code generation. Compare RLTF baseline (fine_always) against proposed method (fine_gated: apply fine-grained penalties only to U_line errors) on APPS dataset using CodeT5-large.

**Success Criterion:** fine_gated reaches 30% pass@1 >10% faster than fine_always.

---

## Problem Statement

RLTF applies fine-grained feedback uniformly to all error types. However, U_ignore errors (RuntimeError, RecursionError) have unreliable traceback localization, potentially introducing gradient noise. Gating fine-grained feedback to U_line errors only may improve training efficiency.

---

## Functional Requirements

### FR-1: Dataset Preparation
- Load APPS dataset (5,000 train, 5,000 test)
- Tokenize with CodeT5 tokenizer (max 512 input, 256 output)
- Create execution sandbox for pass@1 evaluation

### FR-2: Baseline Model (fine_always)
- Load CodeT5-large (Salesforce/codet5-large)
- Implement RLTF reward: fine-grained penalties on ALL errors
- PPO training with multi-granularity feedback
- Log training steps and pass@1 at checkpoints

### FR-3: Proposed Model (fine_gated)
- Same as FR-2 with gating modification
- Classify errors: U_line vs U_ignore
- Apply fine-grained penalties ONLY to U_line errors
- U_ignore errors receive coarse penalty only
- Log gating activation rate

### FR-4: Error Classification Module
- Parse Python tracebacks to extract error type
- U_LINE: SyntaxError, IndentationError, NameError, TypeError, AttributeError, KeyError, IndexError
- U_IGNORE: RuntimeError, RecursionError, MemoryError, TimeoutError, AssertionError
- Return category string for reward calculation

### FR-5: Evaluation Pipeline
- Compute pass@1 on full test set (5,000 problems)
- Record training steps when pass@1 crosses 30% threshold
- Calculate efficiency ratio: (steps_baseline - steps_proposed) / steps_baseline

### FR-6: Visualization
- Training curves: pass@1 vs steps for both conditions
- Error distribution: pie chart of U_line vs U_ignore
- Gate metrics comparison: bar chart of steps-to-30%

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42
- Log all hyperparameters
- Save checkpoints at 1K step intervals

### NFR-2: Execution Safety
- Sandboxed code execution (Docker or subprocess timeout)
- 30-second timeout per test case
- Memory limit: 512MB per execution

### NFR-3: Compute Budget
- Single GPU (A100 40GB recommended)
- ~6 GPU hours per condition
- Total: ~12 GPU hours for full experiment

---

## Success Criteria

| Metric | Condition | Threshold |
|--------|-----------|-----------|
| Primary | steps_fine_gated < steps_fine_always | >10% improvement |
| Activation | gating_rate | 10-15% of failing samples |
| Code | Experiment runs without error | Pass |

---

## Dependencies

| Dependency | Source | Version |
|------------|--------|---------|
| CodeT5-large | HuggingFace | Salesforce/codet5-large |
| APPS Dataset | HuggingFace | codeparrot/apps |
| PyTorch | pip | >=2.0 |
| Transformers | pip | >=4.30 |

---

## Data Specifications

### Input
- APPS problem prompts (text)
- APPS test cases (input/output pairs)

### Output
- Generated code solutions
- Execution results (PASS/FAIL/ERROR)
- Training metrics (loss, reward, pass@1)

---

## Out of Scope

- Multi-seed statistical validation (Phase 5)
- Comparison with other RL methods
- Hyperparameter optimization
- Production deployment

---

## References

1. Liu et al., "RLTF: Reinforcement Learning from Unit Test Feedback" (NeurIPS 2023)
2. Wang et al., "CodeT5: Identifier-aware Unified Pre-trained Encoder-Decoder" (EMNLP 2021)
3. Hendrycks et al., "Measuring Coding Challenge Competence With APPS" (NeurIPS 2021)
