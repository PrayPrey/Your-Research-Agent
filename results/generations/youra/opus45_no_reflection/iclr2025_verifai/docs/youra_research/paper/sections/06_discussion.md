# Discussion

## Key Findings

Our existence test revealed a **boundary condition** rather than a framework failure. The Actionable Specificity decomposition (AS_loc, AS_state, AS_causal) remains conceptually valid—ordering is preserved, components are independent—but regex-based operationalization fails on assertion-dominated benchmarks.

The core insight: **the error types that most need actionable feedback are those that structurally cannot provide it.** Assertion errors (53% of failures, ~45% repair success) produce minimal diagnostic output, creating a fundamental mismatch between feedback need and feedback availability.

## Implications for Future Research

1. **Stratify by error type first:** Before operationalizing AS extraction, researchers should verify extraction feasibility per error category. Assertion-dominated benchmarks require different approaches than type-error-dominated ones.

2. **Alternative operationalizations needed:** LLM-based extraction (prompting the LLM to identify location/state/cause from free text), AST-based analysis, or `pytest --tb=long` for richer output may achieve higher extraction rates.

3. **Mechanism hypotheses blocked:** We could not test whether AS *predicts* repair success because extraction failed. The causal chain (signal → extraction → LLM use → repair) broke at the extraction step.

## Limitations

**Single operationalization tested.** We tested only regex extraction. More sophisticated methods (LLM-based parsing, semantic analysis) remain untested and may achieve higher coverage.

**Single benchmark family.** HumanEval and MBPP share characteristics (assertion-heavy, single-function). Results may differ on benchmarks with richer error types (e.g., multi-file projects with stack traces).

**Python-specific.** Trace mechanisms differ by language. Results may not transfer to languages with different error reporting conventions.

## Broader Impact

This negative result has methodological value: it documents a necessary verification step (extraction feasibility) that future feedback informativeness research should perform. The AS framework may still explain feedback effectiveness on traceback-rich error subsets or with alternative operationalizations.

The finding that assertion errors—the hardest to repair—are also the least extractable suggests a potential intervention point: improving assertion error diagnostics (e.g., including expected/actual values in structured format) could simultaneously improve extractability and repair success.
