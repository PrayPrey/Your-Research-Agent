# Experiment Brief: H-M2 (Targeted Edit Behavior)

**Date:** 2026-08-28
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Prerequisites:** h-e1 (VALIDATED)

---

## 1. Hypothesis Statement

Execution-detailed feedback yields higher pass@1 than execution-binary (pass/fail only) because detailed error traces enable targeted code edits rather than global rewrites.

---

## 2. Variables

| Variable | Type | Values |
|----------|------|--------|
| Feedback granularity | Independent | `detailed` (full trace), `binary` (pass/fail only) |
| Edit scope | Dependent | Lines changed, AST edit distance, edit concentration |
| Base model | Controlled | CodeLlama-7B-Instruct |
| Benchmark | Controlled | HumanEval (164) + MBPP (500) |
| Iterations | Controlled | k=3 |
| Temperature | Controlled | 0.0 (deterministic) |

---

## 3. Experimental Conditions

### Condition A: Execution-Detailed Feedback
- Full error trace with line numbers, error type, expected vs actual values
- Format: Structured error message preserving localization info

### Condition B: Execution-Binary Feedback  
- Pass/fail signal only
- Format: "PASS" or "FAIL" (no additional information)

---

## 4. Dataset

| Dataset | Size | Type | Source |
|---------|------|------|--------|
| HumanEval | 164 problems | standard | https://github.com/openai/human-eval |
| MBPP | 500 problems | standard | https://github.com/google-research/mbpp |

**Sample Size:** 664 total problems (full test sets)
**Rationale:** Full benchmark coverage for statistical validity

---

## 5. Metrics

### Primary Metrics
1. **Lines Changed** — Count of modified lines per refinement iteration
2. **AST Edit Distance** — Tree edit distance between original and refined code
3. **Edit Concentration** — Ratio of changes at error location vs elsewhere

### Secondary Metrics
4. **Pass@1 Improvement** — Delta from iteration 0 to iteration k
5. **Fix Success Rate** — Proportion of failing tests fixed per iteration
6. **Regression Rate** — New failures introduced per edit

### Operationalization
- Lines changed: `difflib.unified_diff` line count
- AST distance: `zss` tree edit distance on Python AST
- Edit concentration: (changes within ±3 lines of error) / (total changes)

---

## 6. Analysis Plan

### Primary Comparison
- **Null H0:** Mean edit scope (lines changed) is equal between detailed and binary conditions
- **Test:** Paired t-test (same problem, different conditions)
- **Significance:** α = 0.05
- **Effect Size:** Cohen's d ≥ 0.3 (small-medium)

### Success Criteria (PoC)
1. Detailed feedback produces smaller diffs than binary (p < 0.05)
2. Edit concentration higher with detailed feedback (>60% at error location)
3. Effect consistent across both models

### Failure Response
- IF fails: EXPLORE if models ignore localization information
- Document which feedback components models attend to

---

## 7. Execution Protocol

### Phase 1: Data Preparation
1. Load HumanEval and MBPP test sets
2. Generate initial code for all problems (zero-shot)
3. Execute and collect failing samples

### Phase 2: Refinement Loop
```
for problem in failing_samples:
    for condition in [detailed, binary]:
        code = initial_code[problem]
        for iter in range(3):
            result = execute(code)
            if result.passed:
                break
            feedback = format_feedback(result, condition)
            code = model.refine(code, feedback)
            record_diff(code, problem, condition, iter)
```

### Phase 3: Metric Extraction
1. Compute line-level diffs per iteration
2. Parse ASTs and compute edit distance
3. Annotate error locations from execution traces
4. Calculate edit concentration scores

### Phase 4: Analysis
1. Aggregate metrics by condition
2. Run paired statistical tests
3. Compute effect sizes
4. Generate visualization (box plots, scatter)

---

## 8. Resource Requirements

| Resource | Estimate |
|----------|----------|
| Model inference | ~4K calls (664 problems × 2 conditions × 3 iters) |
| Execution sandbox | ~8K runs (before/after per iteration) |
| GPU time | ~8 hours (A100 equivalent) |
| Storage | ~500MB (diffs, ASTs, metrics) |

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| R3 (Format confounding) | Both conditions use same template structure, only content differs |
| R4 (Model capability) | Use two model families as sanity check |
| Null result | Document which feedback components affect edit behavior |

---

## 10. Implementation Tasks

| Task | Priority | Estimate |
|------|----------|----------|
| Feedback formatter (detailed vs binary) | P0 | 2h |
| Diff metrics module | P0 | 3h |
| AST edit distance computation | P1 | 2h |
| Edit concentration analyzer | P1 | 2h |
| Execution sandbox setup | P0 | 4h |
| Statistical analysis script | P2 | 2h |

**Total:** ~15 hours implementation

---

## 11. Expected Outcomes

### If Hypothesis Supported
- Detailed feedback produces 40-60% smaller diffs
- Edit concentration >70% at error location with detailed feedback
- Clear mechanism: localization → targeting → efficiency

### If Hypothesis Refuted
- No significant diff size difference
- Models ignore localization info regardless of feedback type
- Alternative explanation: models have fixed edit strategy

---

## 12. Connection to Verification Plan

**Predecessor:** H-E1 (VALIDATED) — Execution feedback provides unique signal
**This Step:** H-M2 — Counterfactual information enables targeted edits
**Successor:** H-M3 — Targeted edits have higher fix probability

**Chain Logic:** If detailed feedback enables smaller, targeted edits (H-M2), and targeted edits have higher fix rates (H-M3), then detailed feedback improves outcomes via the targeting mechanism.

---

## Appendix: Feedback Format Templates

### Detailed Format
```
ERROR at line {line_num}: {error_type}
Expected: {expected_value}
Actual: {actual_value}
Traceback:
{truncated_traceback}
```

### Binary Format
```
FAIL
```
