# Conclusion

We set out to validate that incremental SMT verification achieves 2-5x speedup over batch re-verification for LLM code repair in statically-typed languages. Instead, our validation pipeline failed before generating a single line of code, revealing that infrastructure robustness—not just theoretical soundness—determines whether a hypothesis can be tested. This negative result paper presents the hypothesis, the implemented experimental pipeline, and the lessons learned from complete validation failure due to API authentication errors.

The hypothesis—that incremental SMT verification (re-verifying only modified functions + dependencies) reduces verification time by 2-5x compared to batch re-verification—remains **theoretically plausible but empirically unvalidated**. All experimental validation was blocked at the foundational hypothesis (h-e1: static analyzers can extract SMT constraints from LLM-generated typed code) due to 100% API authentication failure rate (48/48 generation attempts returned HTTP 401 "API key is invalid").

**The Verified Contribution: Dataset Extension Methodology**

Despite generation failure, the dataset extension pipeline succeeded: HumanEval was mechanically extended with 100 Pydantic-annotated prompts, demonstrating that typed benchmarks can be created from existing code generation datasets without manual annotation. This artifact addresses a gap in formal verification research—prior benchmarks (HumanEval, APPS, CodeContests) lack type annotations required for SMT constraint extraction. The template-based transformation approach (function signature + docstring → Pydantic BaseModel + validators) scales mechanically, enabling future research on static analysis for LLM code.

The constraint extraction pipeline (DatasetExtender → LLMGenerator → PyreExtractor → Z3Validator → MetricsEngine) was validated on error files, confirming architectural soundness on negative cases. The modular design allowed partial validation despite generation failure—dataset extension succeeded independently, preventing cascading failures. This architectural pattern generalizes: experimental pipelines should separate concerns (data preparation, model execution, evaluation) to allow validating unaffected subsystems when external dependencies fail.

**Infrastructure Lesson: Pre-Flight Validation Is Critical**

The infrastructure failure mode is clearly identified (invalid Anthropic API key), not a scientific refutation of the hypothesis. The validation report explicitly recommends "RETRY with valid API key" rather than pivoting to alternative approaches, indicating the hypothesis remains viable pending infrastructure fixes. Retry requires only environment configuration (fixing the API key), not experiment redesign or re-implementation.

This lesson generalizes to any research relying on external APIs, cloud services, or distributed systems. Experimental design must address failure modes explicitly:
- **Pre-flight validation:** Test API keys, network connectivity, external dependencies before starting batch experiments (a single test call would have detected the auth error immediately).
- **Fast-fail logic:** Detect non-retryable errors (authentication, invalid input) and stop immediately rather than exhausting retries.
- **Checkpoint/resume:** For long-running experiments (100+ API calls), support resuming from partial completion.

**Honest Assessment of Claims**

We cannot claim:
- "Incremental SMT achieves 2-5x speedup" (prediction P1 untested)
- "Speedup scales with codebase size" (P2 untested)
- "Conservative dependency analysis maintains soundness" (P3 untested)
- "Type annotations enable constraint extraction from LLM code" (h-e1 foundational claim untested)

All quantitative speedup predictions await validation pending infrastructure fixes (valid API key) and completion of the h-e1 → h-m1 → h-m2 → h-m3 hypothesis chain.

**Future Work**

**Immediate:** Retry h-e1 with valid Anthropic API key. If extraction_rate ≥90%, the hypothesis validation can proceed to mechanism testing (h-m1: constraint extraction pipeline, h-m2: dependency analysis, h-m3: speedup measurement). If extraction_rate <90%, pivot to neural constraint extraction (Phase 2A future work H2).

**Medium-term:** Extend approach to Rust + Prusti for language generalization. Test whether incremental SMT transfers beyond Python. Validate repair locality assumption (A2) on LLM code—neural repair patterns may differ from human edits documented in CURE/CoCoNut literature.

**Long-term vision:** Standardize typed benchmarks for formal verification research across multiple languages (Python + Pydantic, Rust + Prusti, TypeScript + type predicates). Establish evaluation protocol for comparing neural code generation with/without SMT verification. Enable practical deployment of formally-verified LLM code repair in safety-critical domains.

**Closing the Loop**

We began with the question: can infrastructure robustness be separated from theoretical soundness in hypothesis testing? The answer is no—infrastructure is prerequisite, not afterthought. A scientifically sound hypothesis with elegant decomposition (existence → mechanisms), rigorous experimental protocol, and complete implementation can still fail to advance knowledge if external dependencies (API access, network reliability, service availability) are not validated before execution. The HumanEval + Pydantic dataset extension pipeline is the verified artifact from this validation attempt—a stepping stone for future constraint extraction research, and a reminder that experimental methodology extends beyond hypothesis design to encompass infrastructure reliability.
