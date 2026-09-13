# Product Requirements Document: H-E1

**Date:** 2026-08-28
**Hypothesis:** Execution-detailed feedback yields measurably higher pass@1 than random baseline after k=3 refinement iterations on HumanEval and MBPP.
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

---

## Executive Summary

This experiment validates whether execution-based feedback (error messages, line numbers, expected/actual values) improves iterative code refinement compared to random generic feedback. Success criterion: pass@1(execution) > pass@1(random) on standard code generation benchmarks.

---

## Problem Statement

Code generation models often fail on first attempt. Iterative refinement with feedback can improve success rates. The core question: does execution-specific feedback provide useful signal, or is any feedback sufficient?

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HumanEval (164 problems) via HuggingFace `openai_humaneval`
- Load MBPP test split (500 problems) via HuggingFace `mbpp`
- Store problem prompts, test cases, entry points

### FR-2: Model Integration
- **Primary**: CodeLlama-7B-Instruct via HuggingFace transformers
- **Secondary**: StarCoder-7B for generalization (optional)
- Inference config: temperature=0.2, max_tokens=512, top_p=0.95

### FR-3: Code Execution Sandbox
- Execute generated code with test cases
- Timeout: 10 seconds per execution
- Memory limit: 512MB
- Capture: stdout, stderr, error type, line number, expected/actual

### FR-4: Feedback Generation
- **Execution feedback**: Format error type, line number, expected vs actual
- **Random baseline**: Generic templates ("Try a different approach", "Check your logic")
- Ensure feedback strings are distinguishable

### FR-5: Iterative Refinement Loop
- Maximum k=3 iterations
- On each iteration: execute → format feedback → prompt model for refinement
- Stop early if tests pass

### FR-6: Evaluation Metrics
- **Primary**: pass@1 (single attempt success rate)
- **Secondary**: pass@1 after k iterations
- Track per-iteration success rates

### FR-7: Comparison Conditions
- **Condition A**: Execution feedback refinement
- **Condition B**: Random feedback refinement (baseline)
- Same model, same problems, only feedback differs

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=42
- Deterministic model outputs (temperature=0.2)
- Version-locked dependencies

### NFR-2: Resource Constraints
- Single GPU (A100/V100)
- ~2-4 hours total runtime for full benchmark

### NFR-3: Safety
- Sandboxed execution (subprocess isolation)
- No network access during code execution

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| pass@1(exec) > pass@1(random) | Any positive delta |
| Mechanism verification | Feedback strings differ |
| Refinement observable | At least 1 problem improved by iteration |

---

## Data Requirements

| Dataset | Source | Split | Size |
|---------|--------|-------|------|
| HumanEval | openai_humaneval | test | 164 |
| MBPP | mbpp | test | 500 |

---

## Dependencies

- transformers >= 4.35.0
- datasets >= 2.14.0
- torch >= 2.0.0
- accelerate >= 0.24.0

---

## Out of Scope

- Fine-tuning models
- Multi-turn conversation
- Advanced RL-based refinement
- Scaling beyond 7B parameters

---

*Generated from Phase 2C: 02c_experiment_brief.md*
