# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Title:** AS Components Are Measurable
**Gate:** MUST_WORK

## Hypothesis Statement

Under standard verification signal generation, if we apply AS decomposition rules (file:line extraction, variable counting, trace depth measurement), then AS_loc, AS_state, and AS_causal can be independently computed for each signal type.

## Success Criteria

- **Primary:** AS components extractable from ≥95% of signals
- **Secondary:** AS values show expected ordering across signal types

## Failure Response

PIVOT to categorical signal comparison only (abandon AS decomposition)

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP | Standard code generation benchmarks with test oracles |
| **Model** | GPT-4 / Claude 3.5 Sonnet | State-of-the-art models with code repair capability |

**Dataset Details:**
- HumanEval: 164 problems
- MBPP: 500 problems
- Total: 664 problems

## Verification Protocol

1. Generate 100 failing test cases across HumanEval/MBPP
2. For each failure, generate all 6 signal variants (C1-C6)
3. Apply AS extraction rules: regex for file:line, count exposed variables, count trace depth
4. Verify inter-rater reliability (automated extraction matches manual annotation)
5. Confirm AS values vary systematically across signal types

## Variables

- **Independent:** Verification signal text (6 conditions: C1-C6)
- **Dependent:** AS_loc (binary), AS_state (count), AS_causal (count)
- **Controlled:** Signal generation method (pytest, Python trace module)

## Dependencies

None (root hypothesis)

## Gate Condition

This is a MUST_WORK gate. If H-E1 fails, the entire AS framework is invalid and verification stops.
