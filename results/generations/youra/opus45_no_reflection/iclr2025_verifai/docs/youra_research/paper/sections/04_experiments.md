# Experimental Setup

## Research Questions

**RQ1 (Existence):** Can AS components (AS_loc, AS_state, AS_causal) be reliably extracted from standard verification signals?

**RQ2 (Ordering):** Does the expected AS ordering (C1≥C2≥C3≥C4) hold across signal conditions?

**RQ3 (Independence):** Are AS components sufficiently independent to warrant separate analysis?

## Dataset

We use HumanEval (164 problems) \citep{humaneval2021} and MBPP (500 problems) \citep{mbpp2021}, totaling 664 Python programming problems. These are standard benchmarks for code generation with executable test suites enabling automated pass/fail evaluation.

**Bug Injection:** For each problem, we generate an initial (buggy) solution using GPT-4 (temperature=0), then execute against the test suite to collect failure signals. This produces realistic failure scenarios rather than synthetic mutations.

**Sampling:** From 639 failures (96.2% failure rate), we stratified-sample 100 failures across error types to ensure coverage of assertion, type, runtime, and other error categories.

## Signal Generation Protocol

For each sampled failure, we generate 6 signal variants (C1–C6) by controlling trace output:

- **C1 (Full Trace):** Complete Python traceback with all frames
- **C2 (Truncated):** Last 5 traceback frames only
- **C3 (Value-Masked):** Full trace with variable values redacted
- **C4 (Error Message):** Exception type and message only
- **C5 (Static Analysis):** mypy/pylint output
- **C6 (Syntax Baseline):** Syntax error simulation

Total: 600 signals (100 failures × 6 conditions)

## Extraction Protocol

For each signal, we apply regex patterns to extract:
- AS_loc: Binary presence of file:line match
- AS_state: Count of variable-value pair matches
- AS_causal: Count of traceback frame matches

**Extraction Success:** A signal has successful extraction if AS_loc = 1 (at minimum, location must be identifiable).

## Evaluation Metrics

**Primary Metric:** Overall extraction rate = (signals with AS_loc=1) / (total signals)

**Component Rates:** Per-component extraction rates (AS_loc, AS_state, AS_causal separately)

**Ordering Verification:** Mean AS values per condition, verify C1≥C2≥C3≥C4

**Independence Check:** Pearson correlation between components; threshold r < 0.5 for independence
