# Teaching Large Language Models to Self-Debug

## Key Metadata
- **Authors:** Chen et al.
- **Year:** 2023
- **Venue:** arXiv (2304.05128)
- **Core Contribution:** Rubber Duck Debugging + execution trace feedback increases MBPP pass@1 by 12%; establishes execution trace as informative feedback signal; 10x sample efficiency over best-of-N on MBPP.

## Section Summaries

### Abstract
Self-Debugging teaches LLMs to debug their own code using two signals: (1) rubber duck debugging (explaining code line-by-line to detect logical errors), and (2) execution trace feedback (running the code and observing step-by-step variable values). Combining these signals improves MBPP performance by 12% and achieves 10x sample efficiency over best-of-N sampling.

### Introduction & Motivation
LLMs generate incorrect code that cannot be self-corrected with plain language feedback alone. Execution traces provide structured, objective information about what the code actually does vs. what it should do. The research question: can execution trace information — without human feedback — enable LLMs to self-repair code?

### Methodology
Two-stage Self-Debug: (1) Code Explanation (rubber duck): LLM generates line-by-line explanation, may detect own errors; (2) Execution Trace Feedback: code is executed in a sandbox, trace (variable values at each step) is formatted and added to prompt for repair. No external training signal. Multiple repair rounds allowed. Key models: Codex, GPT-3.5. Benchmarks: MBPP, Spider (text-to-SQL), TransCoder (code translation).

Metric: pass@1 with fixed generation budget. Comparison: best-of-N sampling at equivalent total generation count.

### Experiments & Results
| Method | pass@1 | Benchmark |
|---|---|---|
| Baseline (no feedback) | ~38% | MBPP |
| Self-Debug (execution trace) | ~50% (+12%) | MBPP |
| Best-of-N (same budget) | ~45% | MBPP |
Self-Debug outperforms best-of-N at equal generation budget on MBPP. No comparison to static analysis or type-constrained decoding.

### Discussion & Conclusion
Execution trace provides richer signal than simple pass/fail: the model can observe where logic diverges from expectation. Limitation: execution traces require sandboxed code execution; infinite loops and unsafe code need special handling. Static analysis as an alternative (non-execution) feedback signal was not investigated.

## Key Contributions
- Rubber Duck Debugging + execution trace feedback framework
- +12% MBPP pass@1 improvement
- 10x sample efficiency over best-of-N on MBPP
- Established execution trace as actionable structured feedback

## Potential Relevance
Establishes execution-based feedback as the incumbent strong baseline for Gap 3. The +12% MBPP improvement and 10x sample efficiency are key reference points. For Gap 3, this paper defines what execution feedback achieves; Gap 3 tests whether pylint/mypy and type-constrained decoding can match or exceed this on the same benchmarks. [Chen et al., 2023] format for citations.
