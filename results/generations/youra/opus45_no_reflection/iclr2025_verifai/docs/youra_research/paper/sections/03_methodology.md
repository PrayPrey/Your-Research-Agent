# Methodology

## Actionable Specificity Framework

We propose that feedback effectiveness for LLM code repair depends on **Actionable Specificity (AS)**—the degree to which a verification signal provides information that enables targeted bug localization and fix inference. We decompose AS into three orthogonal dimensions:

**AS_loc (Localization):** Whether the signal identifies the failure location. Binary: 1 if file:line information present, 0 otherwise. Extraction pattern: `File "([^"]+)", line (\d+)`.

**AS_state (State Exposure):** How many variable values are visible at the failure point. Continuous: count of variable-value pairs. Extraction pattern: `(\w+)\s*=\s*(['""]?[\w\d\.\-\[\]{}]+['""]?)`.

**AS_causal (Causal Context):** Execution trace depth between variable assignment and failure. Continuous: count of traceback frames. Extraction pattern: `^\s+File "([^"]+)", line (\d+), in (\w+)`.

These components are designed to be **independently measurable** from signal text using regex extraction, enabling quantitative analysis across signal types.

## Signal Generation Conditions

We defined 6 signal generation conditions varying in expected AS level:

| Condition | Description | Expected AS Level |
|-----------|-------------|-------------------|
| C1 | Full runtime trace | High (all components) |
| C2 | Truncated trace (last 5 frames) | Medium-High |
| C3 | Value-masked trace | Medium (no AS_state) |
| C4 | Error message only | Low |
| C5 | Static analysis (mypy/pylint) | Variable |
| C6 | Syntax error baseline | Minimal |

The conditions are ordered such that C1 ≥ C2 ≥ C3 ≥ C4 in expected AS, enabling ordered hypothesis testing.

## Design Rationale

We chose the **simplest operationalization** (regex extraction) to establish feasibility bounds before investing in more sophisticated methods (AST analysis, LLM-based extraction). This follows the scientific principle of testing necessary conditions first: if AS components cannot be reliably extracted via simple patterns, the framework requires reformulation before testing predictive power.

The regex patterns target standard Python traceback format produced by the `traceback` module. This design decision creates a known limitation: non-standard error output (assertion messages, custom exceptions) may not match patterns.

## Existence Test Design (H-E1)

Before testing whether AS predicts repair success, we test whether AS is *measurable*. Our existence hypothesis:

> **H-E1:** Under standard verification signal generation, AS_loc, AS_state, and AS_causal can be independently computed for ≥95% of signals, and AS values show expected ordering across conditions (C1≥C2≥C3≥C4).

This is a **MUST_WORK gate**: failure indicates the operationalization needs revision before proceeding to mechanism hypotheses.

**Success Criteria:**
- Primary: Extraction rate ≥95% across all signals
- Secondary: AS ordering C1≥C2≥C3≥C4 preserved

**Gate Logic:** Both criteria must pass to proceed; ordering alone is insufficient if extraction fails.
