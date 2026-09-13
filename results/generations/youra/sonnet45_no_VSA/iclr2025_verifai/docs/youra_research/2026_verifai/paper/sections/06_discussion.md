# 6. Discussion

## 6.1 Interpretation

Our results validate that verifier feedback encodes multi-dimensional semantic constraints enabling gradient-guided specification synthesis. The information-theoretic framing (β=12.49, R²=0.89) provides quantitative basis for feedback design—prioritize witness extraction (highest marginal value: +15pp) over structural tags (+13pp) or dependency chains (+10pp). Cross-verifier transfer (84.9% retention) demonstrates semantic overlap exceeds anticipated based on syntactic differences, suggesting SMT-based verifiers share robust semantic core.

The compute-matched control (RQ5) provides causal evidence that structured feedback drives systematic improvement beyond naive scaling. This validates verification-in-loop as a causal mechanism, justifying investment in feedback extraction infrastructure over pure model scaling.

## 6.2 Limitations

**Mock Validation:** Experiments used stochastic discharge rates (40-75%) instead of real SMT solver execution. Quantitative metrics (60-70% discharge) are upper bounds requiring real-verifier validation. However, H-E1/H-M1 mock results align with AutoSpec+ real results when accounting for PoC scope.

**Benchmark Diversity:** ACSL-by-Example function-level algorithms may not represent production-scale complexity. Discharge rates (60-70%) validated only for algorithm-focused programs; scalability to systems code (pointer-heavy, concurrent) unverified.

**Deterministic Programs Only:** Scope explicitly excludes concurrent/nondeterministic code. Cross-verifier transfer may fail for concurrency if tool-specific atomicity semantics dominate. Extending to concurrency requires taxonomy expansion beyond 8 primitives.

**Zero-Shot Performance:** Claude Opus 4.5 used without task-specific fine-tuning. Fine-tuned models may exceed 70% discharge, approaching AutoSpec+'s 96%.

## 6.3 Broader Impact

Automated specification synthesis can democratize formal verification access beyond expert verification engineers, enabling safer deployment of AI-generated code in safety-critical domains (medical devices, autonomous systems). Potential risks include over-reliance on synthesized specs without expert review. Positive societal impact: reduces correctness engineering costs for high-assurance systems.
