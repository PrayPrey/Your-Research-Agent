# Related Work

## Execution Feedback for Iterative Code Repair

Iterative self-repair using execution feedback — generate code, execute it, use error output as context, re-generate — is a well-established approach. Chen et al. [2023] showed that execution trace feedback enables LLMs to self-debug, improving MBPP by 12% and achieving 10× sample efficiency compared to best-of-N sampling. Shinn et al. [2023] demonstrated that verbal reinforcement via execution results reaches 91% HumanEval pass@1 in Reflexion. Gehring et al. [2024] showed that RL-grounded execution feedback (RLEF) further improves over prompting-only repair, reducing required samples by 10×. Most recently, Arimbur [2026] showed that modern 8B instruction-tuned models — including Llama 3.1 8B — achieve meaningful self-repair (+4.9 to +17.1pp HumanEval) with execution feedback alone, without fine-tuning, and that most gains occur in repair rounds 1–2.

These works collectively establish that execution feedback *works*. However, none compare execution feedback against pylint/mypy static analysis on the same benchmarks under compute-controlled conditions. Our work fills this gap.

## Static Analysis Feedback for LLM Code Quality

Pylint, mypy, and related static analysis tools have been integrated into LLM code generation pipelines primarily for quality metrics beyond functional correctness. Blyth et al. [2025] demonstrated that iterative pylint/bandit feedback reduces security issues in LLM-generated code from 40% to 13% over 10 iterations on PythonSecurityEval. This result establishes that pylint *can* provide useful feedback — but on a benchmark where pylint's Error and Warning categories (security violations) are the dominant failure mode. HumanEval and MBPP failures are dominated by logic and runtime errors, not security issues, making this result difficult to generalize.

FeedbackEval [Dai et al., 2025] provides the most systematic comparison of feedback types, covering compiler feedback, test feedback, minimal feedback, and LLM-expert feedback across HumanEval, CoderEval, and SWE-bench. However, FeedbackEval excludes semantic static analysis (pylint/mypy) — it uses compiler output (syntax errors) rather than pylint-style warnings — and does not compare against execution test feedback with compute normalization. Our study directly addresses this gap: we add pylint/mypy as a treatment condition and hold token budget constant across all conditions.

## Type-Constrained Decoding

Mündler et al. [2025] showed that type-constrained decoding — enforcing type correctness via vocabulary-filtered generation — reduces compilation errors by over 50% on HumanEval and MBPP. This approach is fundamentally different from repair-mode feedback: it prevents certain errors at generation time rather than correcting them after. As a *prevention* strategy, it is not directly comparable to iterative repair but establishes that type constraints can improve functional correctness benchmarks. Our experimental design treats type-constrained decoding as a distinct secondary study (not executed in this pipeline run due to resource constraints) and focuses on the repair-mode comparison.

## Positioning Our Work

Our study differs from prior work in three ways:

1. **Head-to-head pylint/mypy vs. execution:** Prior work studies these approaches in isolation on different benchmarks. We compare them directly on the same benchmark set (HumanEval + MBPP) in the same experimental framework.

2. **Iso-compute control:** We fix total output tokens at B=1000 per problem across all conditions, preventing feedback quality from being confounded with compute quantity. Prior comparisons typically fix repair rounds (not compute).

3. **Mechanism analysis:** We decompose pylint coverage by flag category (E/W/C/R/I) to distinguish *functional* coverage from *style* coverage — a measurement not reported in any prior work on pylint feedback for code generation.
