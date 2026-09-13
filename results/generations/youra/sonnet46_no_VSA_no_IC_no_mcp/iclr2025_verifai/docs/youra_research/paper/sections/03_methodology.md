# Methodology

## Overview

Our key insight motivates the experimental design: if mypy output functions as
a general diagnostic context enricher rather than a type-targeted correction
signal, then the improvement should appear broadly across problem types, not
concentrated on type-error problems. To test this, we need not just an
existence check (does mypy help?) but a *mechanistic decomposition* — a causal
chain from signal existence through LLM consumption to overall effect to
type-specificity.

We operationalize this as a five-sub-hypothesis experiment (h-e1 through h-z1),
each testing one link in the causal chain. This structure lets us distinguish
between "mypy helps but through an unexpected mechanism" (our finding) and
"mypy doesn't help" (an equally possible outcome).

## Experimental Conditions

We define three experimental conditions:

- **Condition A (execution-only):** After each generation attempt, run the
  solution against EvalPlus test cases. Capture pass/fail status and, on
  failure, the exception trace or wrong-output message. Feed this as feedback
  to the LLM for the next repair attempt.

- **Condition B (execution+mypy):** Same as Condition A, but additionally run
  `mypy --ignore-missing-imports --no-strict-optional` on the generated code
  and append the mypy output (errors or "Success: no issues found") to the
  feedback prompt before calling the LLM.

- **Condition C (execution+mypy+Z3):** Same as Condition B, but for problems
  in the arithmetic subset where a valid Z3 specification was generated and a
  counterexample was found, additionally append the Z3 counterexample (input
  values, expected output) to the repair prompt.

Condition A is the Self-Debug baseline. Condition B is the treatment. Condition
C is the extension tested in h-z1.

**Rationale for the condition structure:** We hold everything constant between
Condition A and B except the presence of mypy output. This isolates the
marginal contribution of the static analysis feedback channel. The one-flag
difference (add/remove mypy call) ensures that observed pass@1 differences
are attributable to the mypy signal, not to other confounds.

## LLM Configuration

All experiments use GPT-4o-mini via the OpenAI API:

- **Initial generation:** temperature=0.8, max\_tokens=1024
- **Repair loop:** temperature=0.0, max\_tokens=2048
- **Seeds:** 42, 123, 456 (for h-m3 three-seed replication)

**Rationale for temperature=0.0 in repair:** Deterministic repair makes the
error elimination results (h-m1) interpretable — the LLM's repair policy is
a fixed function of the feedback, not a stochastic draw. Per-round mypy error
trajectories reflect the policy's deterministic behavior, not sampling variance.
Three seeds at temperature=0.8 for initial generation separate the initial
solution randomness from the repair-loop behavior.

**Rationale for GPT-4o-mini:** Cost-controlled experiment (~$10–15 for the
full HumanEval+ multi-seed comparison). The repair loop architecture is
model-agnostic; replication with stronger models is future work.

## Repair Loop Structure

The repair loop (Conditions A and B) follows Algorithm 1:

```
Algorithm 1: Execution+mypy Repair Loop (Condition B)

Input:  problem p, initial solution s_0, rounds k=5
Output: final solution s_k, pass@1 indicator

1. For round r = 0 to k-1:
   a. result_exec ← evaluate(s_r, p.tests)  // EvalPlus test harness
   b. If result_exec.passed: return s_r, PASS
   c. result_mypy ← run_mypy(s_r)           // mypy --ignore-missing-imports
   d. feedback ← format(result_exec, result_mypy)  // Condition B only
   e. s_{r+1} ← LLM.generate(repair_prompt(p, s_r, feedback), T=0.0)
2. Return s_k, evaluate(s_k, p.tests).passed

// Condition A: Step (c) omitted; feedback = format(result_exec) only
// Condition C: Step (c) extended with Z3 CE check for arithmetic subset
```

The mypy invocation uses `--ignore-missing-imports` and `--no-strict-optional`
flags to avoid false positives from missing library stubs, while preserving
detection of structurally significant errors (`name-defined`, `arg-type`,
`return-value`). Mypy timeout is set to 30 seconds per call.

**Rationale for k=5 rounds:** h-m1 establishes that mypy errors reach 0 by
round 2 (saturation). k=5 captures the full repair behavior and matches
Self-Debug's comparison conditions.

## Sub-Hypothesis Structure

The five sub-hypotheses form a causal chain:

| Sub-hypothesis | Question | Gate Type |
|----------------|----------|-----------|
| h-e1 | Does mypy signal exist? (≥10% error rate) | MUST\_WORK |
| h-m1 | Does the LLM consume mypy feedback? (monotonic error reduction, ρ<0) | MUST\_WORK |
| h-m2 | Is improvement type-specific? (delta\_type > delta\_non) | SHOULD\_WORK |
| h-m3 | Does execution+mypy outperform execution-only? (pass@1\_B > pass@1\_A) | MUST\_WORK |
| h-z1 | Does Z3 CE feedback further improve pass@1 on arithmetic subset? | SHOULD\_WORK |

**Rationale for the causal chain:** h-e1 is a necessary precondition — if mypy
produces no signal, testing h-m1 through h-m3 is premature. h-m1 tests whether
the LLM acts on the signal. h-m2 tests the type-specificity mechanism. h-m3
tests the overall outcome. This decomposition ensures that a null h-m3 result
can be attributed: either mypy produces no signal (h-e1 fail), or the LLM
doesn't use it (h-m1 fail), or it produces a non-type-specific benefit
(h-m2 fail + h-m3 pass — our actual finding).

## Benchmarks and Problem Selection

- **Primary benchmark:** HumanEval+ [Liu et al., 2023], 164 problems
- **Secondary benchmark:** MBPP+ [Liu et al., 2023], 378 problems (h-e1, h-m1
  characterization; h-m3 Condition A/B comparison incomplete)
- **Arithmetic subset:** 123 HumanEval+ problems with arithmetic content
  (curated by heuristic keyword matching), of which 112 have valid Z3
  specifications (91.1% spec validity rate)

**Rationale for HumanEval+ as primary:** h-e1 establishes that 70% of
HumanEval+ failing solutions have mypy-detectable errors, while MBPP+ shows
0%. HumanEval+ is the correct test bed for the mypy signal hypothesis;
MBPP+'s 0% error rate would test a null condition. We restrict the primary
pass@1 comparison to HumanEval+ and treat MBPP+ as a boundary condition
characterization.

## Z3 Specification Generation and Validation Pipeline

For the arithmetic subset (h-z1), we use a three-stage pipeline:

1. **Curation:** Identify arithmetic-heavy HumanEval+ problems by heuristic
   keyword matching (arithmetic operations, numeric return types, mathematical
   relationships). Yields 123 candidate problems.

2. **Spec generation:** Prompt GPT-4o-mini to generate a Z3 Python specification
   for each problem — a set of Z3 assertions encoding the expected input-output
   relationship. Timeout: 10 seconds per Z3 check.

3. **Spec validation:** Execute the generated Z3 specification against the
   EvalPlus ground-truth test cases. A spec is *valid* if it accepts all
   ground-truth passing solutions. Validity rate: 112/123 = 91.1%.

For valid specs, we attempt counterexample generation on each repair attempt.
A *counterexample* (CE) is an input assignment that satisfies the Z3 spec's
constraints but produces a value the LLM's current solution returns incorrectly.
CE rate on the arithmetic subset: 18/112 = 16.1%.

The pipeline is implemented in `h-z1/code/z3_utils.py` (functions:
`curate_arithmetic_subset`, `generate_z3_spec`, `validate_z3_spec`,
`find_counterexample`). The validation pipeline is reusable for future
formal-verification experiments on Python benchmarks.

## Evaluation Metrics

- **pass@1:** Fraction of problems passing all EvalPlus test cases after k=5
  repair rounds, estimated as the mean over 3 seeds (h-m3) or 1 seed (other
  sub-hypotheses).
- **Spearman ρ:** Rank correlation between repair round (1..5) and mean mypy
  error count, computed over problems with at least one initial mypy error
  (n=20 for HumanEval+ in h-m1).
- **Type-specificity differential:** delta\_type − delta\_non, where
  delta\_type = repair\_rate\_B(type-error problems) −
  repair\_rate\_A(type-error problems), and similarly for non-type-error
  problems (h-m2). A positive differential supports the type-specificity
  mechanism; zero or negative refutes it.
- **Z3 CE rate:** Fraction of valid-spec problems for which a Z3 counterexample
  was found on at least one repair round (h-z1).
