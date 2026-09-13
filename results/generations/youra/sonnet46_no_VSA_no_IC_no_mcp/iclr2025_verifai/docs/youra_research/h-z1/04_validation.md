# Phase 4 Validation Report: H-Z1

**Generated:** 2026-08-26T10:35:00+00:00  
**Execution Mode:** UNATTENDED  
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-z1 |
| **Statement** | On a curated subset of ~50 arithmetic-heavy HumanEval problems (after Z3 spec pre-validation), Condition C (execution+mypy+Z3) achieves higher pass@1 than Condition B (execution+mypy), because formal counterexamples from Z3 provide a distinct error signal that complements mypy type-error messages. |
| **Gate Type** | SHOULD_WORK |
| **Gate Condition** | pass_rate_C > pass_rate_B |
| **Prerequisites** | h-e1 (VALIDATED) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Problems Evaluated | 112 |
| Z3 Valid Specs Generated | 112/123 (91.1%) |
| Condition B Results | 112/112 |
| Condition C Results | 112/112 |
| Figures Generated | 4 |

### Generated Files

| File | Description |
|------|-------------|
| `code/run.py` | Main experiment runner with resume support |
| `code/repair_loop.py` | Condition B and C repair loop implementations |
| `code/pipeline.py` | EvalPlus integration (evaluate_solution, run_mypy) |
| `code/z3_utils.py` | Z3 spec generation, validation, CE extraction |
| `code/config.py` | Experiment configuration |
| `code/visualize.py` | Figure generation |
| `results/condition_b_results.jsonl` | 112 Condition B results |
| `results/condition_c_results.jsonl` | 112 Condition C results |
| `results/validated_subset.json` | 112 Z3-validated problem specs |
| `results/summary.json` | Final metrics |
| `experiment_results.json` | Canonical results for Phase 5/6 |

---

## Code Quality Checklist

- [✓] Experiment ran to completion (112/112 problems)
- [✓] Resume support functional (survived 3 process restarts)
- [✓] Z3 spec generation and validation pipeline operational
- [✓] Condition B repair loop (exec+mypy feedback)
- [✓] Condition C repair loop (exec+mypy+Z3 CE feedback)
- [✓] Z3 CE extraction integrated with repair prompts
- [✓] EvalPlus ground-truth evaluation via check_correctness
- [✓] Results saved incrementally (JSONL streaming)
- [⚠] 2 problems (HumanEval/39, HumanEval/163) timed out in evaluate_solution — injected as failed (conservative)

---

## Experiment Results

### Problem Curation Funnel

| Stage | Count | Rate |
|-------|-------|------|
| Total HumanEval+ problems | 164 | 100% |
| Arithmetic-heavy subset (curated) | 123 | 75.0% |
| Valid Z3 specs generated | 112 | 91.1% of curated |
| Problems evaluated (B+C) | 112 | 100% of valid |

### Primary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| pass@1 Condition B (exec+mypy) | 86.6% (97/112) | — | Baseline |
| pass@1 Condition C (exec+mypy+Z3) | 85.7% (96/112) | > B | **BELOW** |
| Delta (C − B) | **−0.9 pp** | > 0 pp | ❌ |
| Z3 spec validity rate | 91.1% | ≥30 valid | ✓ |
| Z3 CE found rate (among C repairs) | 16.1% (18/112) | — | Low |

### Z3 Counterexample Analysis

| Metric | Value |
|--------|-------|
| Problems where Z3 found CE | 18/112 (16.1%) |
| Problems where Z3 CE = 0 | 94/112 (83.9%) |
| Mean CEs per problem (C condition) | 0.65 |
| Max CEs per problem | 5 |

### Repair Round Distribution

| Rounds | Condition B | Condition C |
|--------|-------------|-------------|
| 1 (passed immediately) | ~72 | ~72 |
| 2–5 (repaired then passed) | ~25 | ~24 |
| 6 (exhausted, failed) | ~15 | ~16 |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Gate Condition** | pass_rate_C > pass_rate_B |
| **pass_rate_B** | 86.6% |
| **pass_rate_C** | 85.7% |
| **Delta** | −0.9 pp |
| **Result** | **FAIL** |
| **Satisfied** | false |

### Gate Interpretation

Gate type is **SHOULD_WORK** (not MUST_WORK). Failure means this hypothesis is **not supported** by the PoC experiment but does **not** block the pipeline. The result is recorded as a limitation.

---

## Analysis: Why Z3 CE Feedback Did Not Help

### Key Finding 1: Low CE Discovery Rate (16.1%)

Z3 counterexamples were found in only 16.1% of problems. For 83.9% of problems in Condition C, the Z3 CE signal was absent (identical to Condition B feedback). The mechanism cannot improve repair if it rarely triggers.

**Root cause:** HumanEval arithmetic problems tend to have:
- Simple input domains (integers, short lists) where the LLM generates mostly syntactically correct solutions
- Failures dominated by logical errors that Z3 specs as written don't capture (e.g., off-by-one, incorrect formula)
- Z3 specs that are too permissive (valid specs that accept the wrong implementation)

### Key Finding 2: CE Signal May Not Guide Repair

Even when Z3 CE was found (18 problems), Condition C did not outperform Condition B on those problems. The concrete counterexample inputs may not provide more actionable repair signal than the execution error message alone for GPT-4o-mini.

### Key Finding 3: High Base Pass Rate

GPT-4o-mini achieves 86.6% pass@1 with exec+mypy feedback alone on this arithmetic subset. The ceiling effect means there is limited room for Z3 CE to show benefit — most problems that are repairable are already repaired without Z3.

---

## Next Steps

| Condition | Action |
|-----------|--------|
| SHOULD_WORK FAIL | Record as LIMITATION_RECORDED; continue pipeline |
| Dependent hypotheses | None specified — h-z1 is terminal |
| Phase 5 | Baseline comparison deferred; gate failed |

**Recommended follow-up (not mandatory):**
1. Investigate why Z3 CE rate is 16% — improve spec generation quality
2. Test on harder problems where base pass@1 is lower (e.g., MBPP+)
3. Consider using Z3 CE to generate more targeted test cases rather than direct feedback

---

## Phase 2C Handoff

### Proven Components

| Component | File | Status | Evidence |
|-----------|------|--------|----------|
| Z3 spec generation (LLM-based) | `code/z3_utils.py` | ✓ PROVEN | 91.1% validity rate |
| Arithmetic problem curation | `code/z3_utils.py:curate_arithmetic_subset` | ✓ PROVEN | 123/164 problems accepted |
| EvalPlus evaluation pipeline | `code/pipeline.py:evaluate_solution` | ✓ PROVEN | 112 problems evaluated |
| Repair loop with mypy feedback | `code/repair_loop.py:repair_loop_b` | ✓ PROVEN | 86.6% pass@1 achieved |
| Z3 CE extraction | `code/z3_utils.py:extract_z3_counterexample` | ✓ PROVEN (low activation) | Finds CEs in 16.1% of cases |

### Configuration

```yaml
model: gpt-4o-mini
gen_temperature: 0.8
repair_temperature: 0.0
max_tokens: 2048
seed: 42
k_repair_rounds: 5
z3_timeout: 10  # seconds per Z3 check
benchmark: humaneval+
curated_subset_size: 112  # after Z3 validation
```

### Lessons Learned

**What Worked:**
- Z3 spec generation via LLM prompt achieves high validity (91.1%)
- Arithmetic problem curation heuristic is effective
- Resume-based experiment execution handles process interruptions
- exec+mypy feedback alone is strong (86.6% pass@1 on arithmetic subset)

**What Didn't Work:**
- Z3 CE signal rarely activates (16.1% CE rate)
- Z3 CE feedback does not improve repair rate when it does activate
- evaluate_solution (evalplus check_correctness) can hang on specific problems (HumanEval/39, /163) — add subprocess timeout at OS level

**Key Insight:**
The arithmetic curation + Z3 spec validation pipeline is sound and reusable, but the CE feedback mechanism for LLM repair has insufficient activation rate (16%) to show statistical benefit on HumanEval+. The h-e1 finding (41.2% type errors) suggests type feedback channels are more activated; Z3's logical counterexample channel is far less frequently activated in this domain.

### Recommendations for Dependent Hypotheses

No direct dependents of h-z1 specified. For future work exploring Z3 feedback:
- Use problems where pass@1 without Z3 is lower (< 70%) to have headroom
- Improve Z3 spec quality to increase CE discovery rate to > 40%
- Consider Z3 as a test-case generator rather than direct feedback signal

---

## Figures

| Figure | Description |
|--------|-------------|
| `figures/gate_metrics.png` | pass@1 comparison: Condition B vs Condition C |
| `figures/z3_funnel.png` | Problem curation and Z3 validation funnel |
| `figures/z3_ce_distribution.png` | Z3 CE found vs not found distribution |
| `figures/repair_rounds.png` | Repair round distribution by condition |

---

## Appendix

### Checkpoint State

```yaml
hypothesis_id: h-z1
phase: 4
status: COMPLETED
gate_result: FAIL
reflection_outcome: LIMITATION_RECORDED
gate_satisfied: false
gate_type: SHOULD_WORK
n_problems: 112
pass_rate_b: 0.866
pass_rate_c: 0.857
delta: -0.009
z3_ce_found_rate: 0.161
```

### Data Files

| File | Records |
|------|---------|
| `results/condition_b_results.jsonl` | 112 |
| `results/condition_c_results.jsonl` | 112 |
| `results/validated_subset.json` | 112 problems |
| `results/summary.json` | Final metrics |
| `experiment_results.json` | Canonical output |

### Execution Notes

- Experiment required 3 restarts due to evaluate_solution hangs on problems HumanEval/39 and HumanEval/163
- Both hanging problems injected as failed (conservative, does not change gate outcome)
- Total wall time: ~10 minutes for 90 new problems (resumed from 22 done)
- OpenAI API: gpt-4o-mini, ~1,200 API calls total
