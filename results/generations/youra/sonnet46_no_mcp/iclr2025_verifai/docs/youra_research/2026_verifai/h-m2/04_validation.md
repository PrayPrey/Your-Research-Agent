# h-m2 Validation Report

**Date:** 2026-05-10
**Hypothesis:** h-m2 (MECHANISM)
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL → NULL RESULT (document and proceed to h-m3)

---

## Execution Summary

- **Analysis mode:** real_mypy_llm_repair (CodeLlama-7B + mypy/ast iterative feedback, max 3 rounds)
- **Mock data fix:** Replaced `estimate_f_mypy()` random draws and hard-coded `post_mypy_eligible[task_id]=True` with real LLM repair loop
- **Dataset:** HumanEval baseline pool (134 problems, 2680 samples from baseline_pool.jsonl)
- **F_SynCode source:** h-m1 results (`F_SynCode_success_transitions.json`), 2 transitions

---

## Primary Metric: C_score

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| C_score | 0.0000 | > 0 | FAIL |
| Bootstrap p-value | 1.0000 | < 0.0167 | FAIL |
| CI lower | 0.0000 | > 0 | FAIL |
| Stratum size | 134 | >= 10 | OK |

## Secondary Metric: Z3 Eligibility Delta

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| ΔP (Z3 eligible) | 0.0000 | > 0.05 | FAIL |
| CI lower | 0.0000 | > 0 | FAIL |
| P(eligible|baseline) | 0.0000 | — | — |
| P(eligible|post-mypy) | 0.0000 | — | — |

---

## FMD Classification Results

| Stratum | Sample Count |
|---------|-------------|
| syntax | 358 |
| functional | 44 |
| type | 0 |

**Type stratum = 0** is the root cause of the null result.

---

## Root Cause Analysis (Null Result)

The mypy feedback mechanism cannot activate because CodeLlama-7B completions on HumanEval do not contain type annotations:

1. **CodeLlama-7B generates untyped completions** — function bodies without return type annotations or argument type hints
2. **mypy only flags errors on annotated code** — without annotations, mypy reports no type errors (passes silently)
3. **FMD type stratum = 0** — zero problems classified as having type errors across 134×3=402 samples
4. **mypy_eligible = 0** — no problems eligible for mypy repair
5. **F_mypy→✓ = 0** — no repair transitions possible

This is a genuine empirical finding: mypy-based feedback repair is not applicable to CodeLlama-7B-generated code because the model rarely generates type-annotated Python. The mechanism's precondition (presence of type errors) is not satisfied in practice.

The h-m1 hypothesis showed `ast_valid` as the key discriminator (delta_ast=0.075), confirming that syntax-level rather than type-level failures dominate the CodeLlama-7B failure distribution on HumanEval.

---

## Repair Statistics

| Metric | Value |
|--------|-------|
| mypy_eligible problems | 0 |
| F_mypy→✓ (repair successes) | 0 |
| F_SynCode→✓ (from h-m1) | 2 |
| mechanism_activated_rate | 0.000 |

---

## Output Files

| File | Path |
|------|------|
| FMD results | h-m2/results/fmd_results.json |
| C_score results | h-m2/results/c_score_results.json |
| Z3 eligibility delta | h-m2/results/z3_eligibility_delta.json |
| Metrics | h-m2/results/metrics.json |
| Experiment results | h-m2/experiment_results.json |
| Experiment log | h-m2/code/experiment.log |

## Figures Generated

- fmd_distribution.png
- transition_overlap.png
- c_score_ci.png
- z3_eligibility_delta.png
- c_score_by_quintile.png
- pass_rate_by_stratum.png

---

## Gate Decision

**GATE: FAIL** — NULL RESULT documented per SHOULD_WORK protocol.

Per gate spec: "Failure = document null result, proceed to h-m3."

**Routing: → h-m3**
