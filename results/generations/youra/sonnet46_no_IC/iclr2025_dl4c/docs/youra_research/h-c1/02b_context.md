---
hypothesis_id: "h-c1"
hypothesis_title: "Doctest Prevalence Feasibility Boundary Condition"
generated_from: "02b_verification_plan.md"
generated_at: "2026-08-04"
type: "CONDITION"
gate: "SHOULD_WORK"
status: "IN_PROGRESS"
---

# Per-Hypothesis Context: H-C1

## Hypothesis Statement

Under a scan of The Stack Python (bigcode/the-stack-dedup) Python subset, if a systematic pilot scan of 10,000 randomly sampled files is conducted, then the proportion of files containing at least one valid doctest (parseable and executable) is ≥3%, because Python ecosystem conventions (NumPy, SciPy, standard library) encourage doctest-style function documentation in library and educational code.

## Hypothesis Type & Gate

- **Type**: CONDITION (boundary feasibility check)
- **Gate**: SHOULD_WORK
- **Practical Execution Order**: Run FIRST (before H-E1) to determine whether compile+test condition is feasible
- **Logical Position in Chain**: H-C1 → H-E1 → H-M1 → H-M2 → H-M3 → H-M4

## Variables

- **Independent**: None (observational study)
- **Dependent**: Doctest prevalence rate (% of Python files containing ≥1 valid doctest)
- **Controlled**: The Stack Python version (bigcode/the-stack-dedup), Python version, random sampling method, file size filter

## Prerequisites

None — this is the first hypothesis to execute in practice.

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Stack Python (bigcode/the-stack-dedup) | Canonical open-source Python corpus; publicly available |
| **Scan Method** | HuggingFace streaming + AST docstring extraction + doctest execution | Same tooling as BigCode analysis (py_compile + ast modules) |
| **Pilot Size** | 10,000 randomly sampled Python files | Matches The Stack's own internal analysis methodology |

## Success Criteria

- **Primary**: ≥3% of sampled files contain ≥1 successfully executable doctest
- **Secondary**: Estimated token pool from doctest-passing files ≥500M tokens

## Failure Response

- IF prevalence 1-3%: SCOPE — reduce token budget N; compile+test condition may still be feasible at smaller N
- IF prevalence <1%: PIVOT — abandon compile+test; fall back to 2-condition design (unfiltered vs compile-only)

## Source References

- Phase 2A Assumption A1
- Phase 2B readiness: sh1_existence
- The Stack paper (Kocetkov et al., 2022) — used py_compile on 10k files for internal analysis
