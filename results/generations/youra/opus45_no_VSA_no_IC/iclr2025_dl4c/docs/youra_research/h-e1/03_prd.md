# Product Requirements Document: H-E1

**Hypothesis:** Different model scales (7B/70B/proprietary) exhibit statistically different FP/FN error ratios when judging code correctness

**Type:** EXISTENCE (PoC)
**Date:** 2026-08-24
**Author:** PrayPrey

---

## Executive Summary

This experiment validates whether LLM judge models at different scales (7B, 70B, proprietary) produce statistically distinguishable error patterns when evaluating code correctness. Using HumanEval+ as ground truth, we compare False Positive and False Negative rates across three model tiers.

---

## Problem Statement

LLM-as-judge systems are increasingly used for code evaluation, but scale-dependent biases remain poorly characterized. Understanding whether smaller models systematically produce different error profiles than larger models informs judge selection and ensemble strategies.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval+ (164 problems) via evalplus package
- Extract problem prompts and canonical solutions
- Support programmatic access to test cases

### FR-2: Code Solution Generation
- Generate code solutions for each problem using target models
- Alternatively, use pre-existing solution sets from EvalPlus benchmarks
- Store solutions with problem IDs

### FR-3: Ground Truth Execution
- Execute solutions against HumanEval+ test suite
- Record pass/fail per (problem, solution) pair
- Use Docker sandboxing for safe execution

### FR-4: Judge Model Inference
- **7B tier:** DeepSeek-Coder-7B-Instruct via vllm
- **70B tier:** CodeLlama-70B-Instruct via vllm (tensor_parallel=4)
- **Proprietary tier:** GPT-4 via OpenAI API
- Temperature=0 for deterministic outputs
- Zero-shot prompt for correctness judgment

### FR-5: Error Classification
- Classify each judgment as TP/TN/FP/FN against execution ground truth
- Aggregate counts per scale

### FR-6: Statistical Analysis
- Build contingency table: scale × error_type
- Compute chi-square test for independence
- Report p-value, chi-square statistic, degrees of freedom

### FR-7: Visualization
- Stacked bar chart: error distribution per scale
- Gate metric visualization: p-value vs 0.05 threshold

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed where applicable
- Deterministic inference (temperature=0)
- Version-pinned dependencies

### NFR-2: Scalability
- Support 1000+ judge verdicts total
- Efficient batch inference via vllm

### NFR-3: Safety
- Docker sandbox for code execution
- No network access during execution

---

## Success Criteria

| Metric | Threshold | Gate |
|--------|-----------|------|
| Chi-square p-value | < 0.05 | MUST_WORK |
| Code execution | Completes without error | MUST_WORK |
| Sample size | ≥500 verdicts | MUST_WORK |

---

## Data Requirements

### Input Data
- **HumanEval+**: 164 problems via `evalplus/humanevalplus`
- **Pre-generated solutions**: Optional, from EvalPlus leaderboard

### Output Data
- `results.csv`: (problem_id, solution_id, scale, verdict, ground_truth, error_type)
- `contingency.csv`: scale × error_type counts
- `figures/`: visualization outputs

---

## Dependencies

### Python Packages
- evalplus>=0.2.0
- vllm
- openai
- scipy
- pandas
- matplotlib/seaborn

### Hardware
- GPU: 4x A100 80GB (for 70B model)
- Alternative: API-only mode (7B+proprietary only)

### External Services
- OpenAI API (GPT-4 access)

---

## Out of Scope

- Training or fine-tuning models
- Multi-turn judge conversations
- Prompt engineering optimization
- Cost optimization

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| 70B model OOM | Fallback to API-based 70B alternative |
| Insufficient sample size | Use full HumanEval+ (164 problems × solutions) |
| OpenAI rate limits | Implement retry with backoff |

---

*Generated from Phase 2C: 02c_experiment_brief.md*
