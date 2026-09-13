# Phase 2C: Experiment Brief
## H-E1: Static→Execution Ordering Effect

**Generated**: 2026-08-09T19:58:00+09:00  
**Hypothesis ID**: h-e1  
**Archon Task**: `f674a5be-7f71-4fa7-9615-bacf5212e684`

---

## 1. Experiment Overview

**Objective**: Verify that static→execution feedback ordering achieves ≥15% relative pass@1 improvement over execution→static ordering with 95% CI lower bound >10%.

**Type**: EXISTENCE (MUST_WORK gate)

---

## 2. Dataset Specification

| Parameter | Value |
|-----------|-------|
| **Name** | HumanEval + MBPP |
| **Type** | standard |
| **Source** | `openai/human-eval` (HF) + `mbpp` (HF) |
| **Size** | 164 + 500 = 664 problems |
| **Split** | Full test set (no train/val needed) |
| **Cache** | `~/.cache/huggingface/datasets/` |

**Rationale**: Standard code generation benchmarks with established baselines. Full test sets ensure statistical power for detecting 15% effect.

---

## 3. Model Specification

| Parameter | Value |
|-----------|-------|
| **Model** | GPT-4o-mini |
| **Provider** | OpenAI API |
| **Temperature** | 0.0 (deterministic) |
| **Max Tokens** | 2048 (per response) |

---

## 4. Experimental Conditions

### Condition A: Static→Execution (CASCADE)
```
[Code] + [Static Analysis Feedback: 500 tokens] + [Execution Feedback: 500 tokens]
```

### Condition B: Execution→Static (REVERSE)
```
[Code] + [Execution Feedback: 500 tokens] + [Static Analysis Feedback: 500 tokens]
```

### Control Variables
- **Token Budget**: 1000 total feedback tokens (500 each type)
- **Truncation**: Deterministic, byte-identical across conditions
- **Iterations**: 3 repair iterations per problem
- **Randomization**: Problems shuffled; condition order counterbalanced

---

## 5. Feedback Generation

### Static Analysis (500 tokens)
- **Tool**: `pylint` + `mypy`
- **Content**: Type errors, undefined variables, unused imports, style violations
- **Truncation**: Priority order: errors > warnings > info

### Execution Feedback (500 tokens)
- **Source**: Unit test execution output
- **Content**: Test results, assertion errors, tracebacks
- **Truncation**: Failed tests first, then passed tests summary

---

## 6. Metrics

### Primary Metric
| Metric | Formula | Target |
|--------|---------|--------|
| **Relative Improvement** | (pass@1_A - pass@1_B) / pass@1_B × 100 | ≥15% |
| **95% CI Lower Bound** | Bootstrap CI | >10% |

### Secondary Metrics (for h-m1, h-m2)
- ΔPass₁₂: Pass rate change between iterations 1 and 2
- Regression Rate₁₂: Problems that passed iteration 1 but failed iteration 2

---

## 7. Statistical Analysis

- **Test**: Paired McNemar test (per-problem comparison)
- **Bootstrap**: 10,000 resamples for CI estimation
- **α**: 0.05
- **Power**: >0.90 at N=664 for detecting 15% relative effect

---

## 8. Implementation Requirements

### Core Pipeline
1. **Data Loader**: Load HumanEval/MBPP from HuggingFace
2. **Code Generator**: Initial code generation via GPT-4o-mini
3. **Static Analyzer**: pylint + mypy wrapper with token truncation
4. **Test Executor**: Sandboxed execution with timeout (10s)
5. **Repair Loop**: 3 iterations with feedback injection
6. **Metric Calculator**: pass@1 with bootstrap CI

### Output Artifacts
- `results/h-e1_raw.jsonl`: Per-problem results
- `results/h-e1_metrics.json`: Aggregate metrics
- `results/h-e1_iteration_logs.jsonl`: Per-iteration state (for h-m1, h-m2)

---

## 9. API Cost Estimate

| Component | Calls | Tokens/Call | Total Tokens | Cost |
|-----------|-------|-------------|--------------|------|
| Initial gen | 664 | ~1000 | 664K | ~$0.10 |
| Repair A | 664×3 | ~2000 | 3.98M | ~$0.60 |
| Repair B | 664×3 | ~2000 | 3.98M | ~$0.60 |
| **Total** | — | — | ~8.6M | **~$1.30** |

---

## 10. Timeline

| Step | Duration |
|------|----------|
| Data setup | 5 min |
| Initial generation | 30 min |
| Condition A (cascade) | 2 hr |
| Condition B (reverse) | 2 hr |
| Analysis | 15 min |
| **Total** | ~4.5 hr |

---

## 11. Success Criteria

| Criterion | Threshold | Action if Fail |
|-----------|-----------|----------------|
| Relative improvement | ≥15% | Gate fails, hypothesis rejected |
| 95% CI lower bound | >10% | Increase N or adjust threshold |
| API completion | 100% | Retry failed calls |

---

## 12. Related Work (From Research)

- **DynaFix (2025)**: Iterative APR with execution-level dynamic info — demonstrates value of multi-iteration repair
- **Tool-Guided RAG Repair (2026)**: Combines compilation + CodeQL + KLEE for iterative refinement
- **Static Analysis Feedback Loop (2026)**: 10 iterations with Bandit/Pylint reduced security issues from 40% to 13%

Key insight: Prior work uses static+execution feedback but does NOT systematically compare ordering effects.

---

## 13. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Exponential backoff, batch requests |
| Execution timeout | 10s limit per test, skip on timeout |
| Token truncation variance | Deterministic truncation algorithm |
| Test flakiness | 3 test runs, majority vote |

---

## 14. Archon References

- **Project**: `a6171cdd-c4e1-4b7b-b2c8-42b319d21e38`
- **Task h-e1**: `f674a5be-7f71-4fa7-9615-bacf5212e684`

---

## Next Steps

1. **Phase 3**: Implementation planning (PRD, Architecture, PRP)
2. **Phase 4**: Code generation and validation
3. **Phase 5**: Baseline comparison (DETERMINES_SUCCESS)
