# Introduction

A single static analysis metric predicts LLM code correctness better than any ensemble—pylint score correlates r=0.87 with pass@1, challenging assumptions about metric combination. This finding suggests that decades of expert knowledge encoded in static analysis rules transfers directly to LLM-generated code, enabling cheap quality filtering without expensive test execution.

The deployment economics of LLM code generation present a practical dilemma. Running test suites on k candidate completions costs k× compute, yet accepting unchecked code risks deploying incorrect implementations. Static analysis tools—pylint, mypy, radon—are free, fast, and deterministic, but the field has assumed they detect style issues rather than logic bugs. If SA metrics could predict functional correctness, practitioners could filter LLM outputs at ~0.01× the cost of test execution.

The research landscape reveals a surprising gap. Recent work demonstrates that iterative SA feedback improves code quality: Blyth et al. [2025] show Bandit+Pylint feedback reduces security issues from 40% to 13% on HumanEval/MBPP. CodeQUEST [Liu et al., 2025] reports "meaningful correlation" between SA metrics and LLM code quality. Yet no study quantifies the predictive correlation—no r-values, no R², no statistical framework enabling rejection sampling. Studies use SA for correction but not prediction.

We address this gap directly. Our key insight is that static analysis quality metrics—originally designed for human code—are strongly predictive of LLM-generated code correctness. Pylint score achieves r=0.87 correlation with pass@1 on HumanEval/MBPP after controlling for code length, far exceeding the r≥0.35 threshold that would indicate moderate predictive power. This correlation persists because pylint rules encode expert knowledge about defect-prone patterns, and these same patterns appear in incorrect LLM code.

Building on this insight, we make the following contributions:

**Empirical:** We present the first quantified correlation study between SA metrics and functional correctness for LLM-generated code, establishing r=0.87 as the baseline for the pylint-correctness relationship on standard benchmarks.

**Methodological:** We demonstrate a partial correlation framework controlling for code length as a confounding variable. The minimal change between raw (r=0.868) and partial (r=0.873) correlations validates that the SA signal is genuine, not an artifact of code brevity.

**Practical:** We show that pylint alone is sufficient—weighted ensemble combination (pylint+radon) achieves r=0.86, actually degrading performance. This "less is more" finding simplifies deployment: practitioners need only a single metric for effective quality filtering.

We organize the paper as follows. Section 2 surveys related work on SA for code generation, highlighting the correlation gap. Section 3 describes our methodology for measuring SA-correctness correlation. Section 4 presents experimental setup across four sub-hypotheses. Section 5 reports results, including the unexpected ensemble degradation finding. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
