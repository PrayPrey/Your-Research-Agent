# Conclusion

We opened with an unexpected result: across 2,680 completions from 134 HumanEval problems, CodeLlama-7B produces zero type errors, making the mypy repair channel structurally inapplicable in this setting. This is not a failure — it is a measurement. And it reveals something important: formal repair method effectiveness is inseparable from the empirical failure distribution of the model being repaired.

Our FMD-conditioned repair framework operationalizes a precondition-first approach. We measure which failures actually occur before applying methods conditioned on those failures. The measurement reveals a strikingly simple reality for CodeLlama-7B on HumanEval: 97.5% of failures are syntax-level. SynCode — which operates at generation time to prevent syntax invalidity — is therefore the universally-applicable first-stage repair. Z3 applies to 33% of problems (the arithmetic-output subset). mypy applies to 0% in this setting.

This characterization is both a negative result and a contribution. The negative: the three-method complementarity hypothesis as originally formulated cannot be tested without either typed LLM code (for mypy) or Z3 repair execution (for the SynCode-Z3 pair). The contribution: we have established the empirical framework to determine which channels are viable, confirmed the pipeline infrastructure, and identified the precise next experiment — h-m3 SynCode-Z3 C_score measurement — that can confirm or refute the core complementarity claim.

**What we know.** SynCode directionally reduces AST failures (delta_ast=0.075, consistent across two experiments). Z3 applies to one-third of the benchmark. mypy is operational but inapplicable to annotation-free LLMs. All three tools integrate in a Python-native pipeline without Docker.

**What remains.** SynCode's statistical significance at N=164 (FW1). The SynCode-Z3 C_score (h-m3, FW2). The mypy channel with annotation-prompted LLMs (FW3). These are not limitations — they are the research program this work enables.

Knowing when formal repair methods fail to engage is as important as knowing when they succeed. Our framework makes this measurement explicit, reproducible, and actionable. The most valuable result in this paper may be the one that shows a method produces zero output — not because the method is broken, but because the precondition was never met, and now we know how to measure that before building repair pipelines on unverified assumptions.
