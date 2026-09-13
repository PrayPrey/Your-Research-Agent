# Abstract

Iterative LLM code repair relies primarily on execution feedback—test results and stack traces. Static analysis offers complementary signal: mechanistic explanations of *why* code is problematic, not just *where* it fails. Prior work shows static analysis improves code quality metrics (security, readability), but impact on functional correctness (pass@k) remains unmeasured.

We present a methodology study for evaluating static analysis in LLM code repair. We develop a gate-based hypothesis validation framework, implement a pylint analysis pipeline for HumanEval, and establish baseline measurements. Our existence gate tests whether static analyzers produce actionable warnings on benchmark code—a prerequisite for the intervention to have signal.

**Key finding:** Canonical HumanEval solutions exhibit only 9.15% pylint warning rate (15/164 problems with ≥1 warning, 23 total warnings across 9 categories). This makes canonical solutions invalid proxies for LLM-generated code, which typically contains more issues. The gate correctly halted downstream experiments.

**Contributions:** (1) First baseline of static warning rates on HumanEval canonical solutions; (2) Validated pylint pipeline for code generation research; (3) Gate-based validation methodology; (4) Identification of canonical-vs-LLM proxy limitation.

The hypothesis that static analysis improves pass@k remains untested. We provide the validated infrastructure and baseline for future work with LLM API access. Code and data available at [repository].
