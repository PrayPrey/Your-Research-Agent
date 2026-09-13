# Product Requirements Document: H-E1
## Feedback Ordering Effect in LLM Code Repair

**Generated**: 2026-08-09  
**Hypothesis**: h-e1  
**Type**: EXISTENCE (MUST_WORK gate)

---

## 1. Executive Summary

Implement an experiment to verify that presenting static analysis feedback before execution feedback (static→execution order) achieves ≥15% relative pass@1 improvement over execution→static ordering in LLM-based code repair.

---

## 2. Problem Statement

LLM code repair pipelines combine static analysis and execution feedback, but the optimal ordering is unknown. This experiment tests whether static-first ordering scaffolds repair toward surface fixes before semantic issues.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load HumanEval (164 problems) from `openai/human-eval` HuggingFace
- Load MBPP (500 problems) from `mbpp` HuggingFace
- Total: 664 problems (full test sets)

### FR-2: Initial Code Generation
- Generate initial code using GPT-4o-mini (temperature 0.0)
- Max tokens per response: 2048

### FR-3: Static Analysis Feedback
- Run `pylint` + `mypy` on generated code
- Truncate to 500 tokens (priority: errors > warnings > info)
- Deterministic truncation algorithm

### FR-4: Execution Feedback
- Execute code against unit tests in sandbox
- 10-second timeout per test
- Truncate to 500 tokens (failed tests first)

### FR-5: Feedback Ordering Conditions
- **Condition A (Static→Execution)**: [Code] + [Static: 500 tok] + [Execution: 500 tok]
- **Condition B (Execution→Static)**: [Code] + [Execution: 500 tok] + [Static: 500 tok]

### FR-6: Repair Loop
- 3 iterations per problem per condition
- Same token budget (1000 total) for both conditions

### FR-7: Metric Calculation
- Compute pass@1 for each condition
- Relative improvement: (pass@1_A - pass@1_B) / pass@1_B × 100
- Bootstrap CI with 10,000 resamples

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Deterministic truncation (byte-identical across conditions)
- Temperature 0.0 for deterministic generation
- Fixed random seed for problem shuffling

### NFR-2: API Reliability
- Exponential backoff on rate limits
- Retry failed API calls (max 3 retries)

### NFR-3: Execution Safety
- Sandboxed test execution
- 10s timeout per test
- 3 test runs with majority vote for flaky tests

---

## 5. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Relative improvement (A over B) | ≥15% |
| 95% CI lower bound | >10% |
| Statistical test | McNemar p < 0.05 |

---

## 6. Output Artifacts

| File | Description |
|------|-------------|
| `results/h-e1_raw.jsonl` | Per-problem results |
| `results/h-e1_metrics.json` | Aggregate metrics |
| `results/h-e1_iteration_logs.jsonl` | Per-iteration state (for h-m1, h-m2) |

---

## 7. Dependencies

- OpenAI API (GPT-4o-mini)
- HuggingFace Datasets
- pylint, mypy
- Python sandbox environment

---

## 8. Estimated Cost

~$1.30 total API cost (~8.6M tokens)

---

## 9. Timeline

~4.5 hours total execution time
