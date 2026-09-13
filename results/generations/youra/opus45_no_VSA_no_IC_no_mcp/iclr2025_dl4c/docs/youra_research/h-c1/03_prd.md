# Product Requirements Document: H-C1

**Hypothesis:** The execution feedback advantage over AI-critic is larger on complex tasks (MBPP) compared to simple tasks (HumanEval), due to increased benefit of precise error localization on multi-step problems.

**Date:** 2026-08-28
**Type:** CONDITION
**Gate:** SHOULD_WORK

---

## Executive Summary

This experiment compares execution feedback vs AI-critic feedback across two benchmarks of different complexity (HumanEval=simple, MBPP=complex) to test whether execution feedback advantage scales with task complexity.

---

## Problem Statement

H-M1 established that execution feedback provides superior error localization. H-C1 tests whether this advantage is larger on complex multi-step tasks where precise localization matters more.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval (164 problems) via HuggingFace `openai_humaneval`
- Load MBPP-sanitized (427 problems) via HuggingFace `mbpp`
- Cache datasets locally

### FR-2: Code Generation
- Generate initial code solutions using CodeLlama-7B-Instruct
- Temperature=0.2 for consistency
- One solution per problem

### FR-3: Execution Feedback Mechanism
- Execute generated code against test cases
- Extract: error line, expected vs actual, traceback
- Format feedback for refinement prompt

### FR-4: AI-Critic Feedback Mechanism
- Generate critique using same LLM
- No execution information provided
- Critique based on code inspection only

### FR-5: Code Refinement
- Single refinement iteration per mechanism
- Same refinement prompt template for both mechanisms
- Only feedback source differs

### FR-6: Evaluation
- Compute pass@1 for each (mechanism, benchmark) pair
- Compute exec_advantage = pass@1(exec) - pass@1(critic)
- Compute complexity_effect = exec_advantage_MBPP - exec_advantage_HE

### FR-7: Visualization
- Bar chart: exec_advantage by benchmark
- Grouped bar: pass@1 for all 4 conditions
- Save to h-c1/figures/

---

## Non-Functional Requirements

### NFR-1: Resource Constraints
- GPU: 1x A100 (40GB) or 2x V100
- Time: 2-4 hours total
- Storage: ~20GB model weights

### NFR-2: Reproducibility
- Fixed random seed
- Deterministic code execution
- Logged all intermediate results

---

## Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| complexity_effect > 0 | MBPP advantage > HumanEval advantage | P0 |
| Both advantages positive | Execution beats AI-critic on both | P1 |
| Code runs without error | Completion | P0 |

---

## Dependencies

- **H-M1:** VALIDATED (prerequisite satisfied)
- **HuggingFace Datasets:** openai_humaneval, mbpp
- **HuggingFace Transformers:** CodeLlama-7B-Instruct

---

## Out of Scope

- Multi-iteration refinement
- Training/fine-tuning models
- Other benchmarks beyond HumanEval/MBPP
- Multiple model comparisons
