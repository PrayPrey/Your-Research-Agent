# 1. Introduction

Large language models (LLMs) have transformed code generation, achieving remarkable performance on benchmarks like HumanEval and MBPP. Iterative repair loops—where models refine their output based on feedback—have emerged as a key technique for improving functional correctness. The dominant paradigm, exemplified by Self-Debug, relies on execution feedback: test results and stack traces guide the model toward working solutions.

Static analysis offers an alternative signal. Tools like pylint and mypy detect potential issues—undefined variables, type mismatches, unreachable code—before execution. Unlike execution traces that show *where* code fails, static warnings explain *why* the code is problematic. This mechanistic feedback could enable more targeted repairs.

**The gap.** Prior work has shown static analysis improves code *quality* metrics. Blyth et al. demonstrated reductions in security issues (40% → 13%) and readability problems (80% → 11%) when integrating static feedback into LLM pipelines. However, no study has measured the impact on *functional correctness*—the pass@k metrics that matter for code generation benchmarks.

**Our question.** Does integrating static analyzer feedback into iterative LLM code repair improve pass@k compared to execution-only feedback?

**This paper.** We present a methodology study that establishes the groundwork for answering this question. We develop a hypothesis validation framework with gate-based testing, implement a pylint analysis pipeline for HumanEval, and provide baseline measurements. Our existence gate—testing whether static analyzers produce actionable warnings on benchmark code—reveals a critical methodological insight: canonical solutions exhibit only 9.15% warning rates, making them invalid proxies for LLM-generated code.

**Contributions:**

1. First baseline measurement of static warning rates on HumanEval canonical solutions (9.15%, 23 warnings across 9 categories)
2. Validated pylint analysis pipeline for code generation research (reusable components)
3. Gate-based hypothesis validation methodology that correctly catches methodology limitations
4. Identification of proxy limitation: canonical solutions ≠ LLM output for static analysis evaluation

We frame this as a methodology contribution. The hypothesis that static analysis improves pass@k remains untested—but we provide the validated pipeline and baseline for future work with LLM API access.
