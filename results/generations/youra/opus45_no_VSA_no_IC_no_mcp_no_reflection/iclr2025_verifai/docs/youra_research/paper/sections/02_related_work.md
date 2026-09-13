# 2. Related Work

## 2.1 Iterative Code Repair

Self-Debug introduced execution-feedback loops for LLM code generation, using test results and stack traces to guide iterative refinement. Self-Refine generalized this to broader refinement tasks using LLM self-feedback. These methods establish execution feedback as the baseline for repair loops.

LDB (LLM Debugger) extended this paradigm with block-by-block verification, improving localization of errors. However, all these approaches rely on execution traces—they know *where* code fails but not *why*.

## 2.2 Static Analysis for LLMs

Blyth et al. (arXiv:2508.14419) represent the closest prior work. They integrated static analysis feedback (pylint, bandit) into LLM pipelines and demonstrated improvements in code quality:
- Security issues: 40% → 13%
- Readability problems: 80% → 11%

Critically, they did not measure functional correctness (pass@k). Their contribution establishes that LLMs can interpret static warnings—but whether this improves benchmark performance remains unknown.

Helping LLMs Improve Code Generation (arXiv:2412.14841) combined testing with static analysis in a framework, but again focused on quality metrics rather than pass@k.

## 2.3 The Gap We Address

| Prior Work | Feedback Type | Metric | Pass@k? |
|------------|---------------|--------|---------|
| Self-Debug | Execution | Functional correctness | ✓ |
| Self-Refine | LLM self-feedback | Task completion | ✓ |
| Blyth et al. | Static analysis | Quality (security, readability) | ✗ |
| **This work** | Static + Execution | Methodology baseline | Pending |

The research gap is clear: no study measures static analysis impact on pass@k. We provide the methodology and baseline to enable this evaluation.

## 2.4 Benchmarks

HumanEval (164 problems) and MBPP (974 problems) are standard benchmarks for code generation. Pass@k metrics measure functional correctness—the fraction of problems solved within k attempts. We focus on HumanEval as the more widely-used benchmark, with MBPP extension as future work.
