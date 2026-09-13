# Paper Summary: LiveCodeBench (P4)

**Title:** LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code  
**Authors:** Jain et al.  
**arXiv:** 2403.07974 (2024)  
**Status:** [INFERRED] — MCP unavailable; summary from training knowledge

---

## Abstract
LiveCodeBench is a continuously updated benchmark using newly published competitive programming problems to provide contamination-resistant evaluation of code LLMs over time.

---

## Key Contributions
- Continuously updated: new problems added as competitive programming contests publish
- Contamination resistant: post-training-cutoff problems cannot be in model's training data
- Holistic evaluation: code generation, self-repair, test output prediction, code execution
- Tracks model performance over time (temporal leaderboard)
- Pass@1 as primary metric; uses execution-based evaluation (exact test case match)

---

## Methodology
- Problem source: Codeforces, LeetCode, AtCoder (post-publication, time-stamped)
- Evaluation: execution-based, all-or-nothing pass/fail per problem
- Time-window slicing: evaluate only on problems published after a model's training cutoff
- No partial credit in final metrics (pass@1 is binary at problem level)
- Multi-task: code generation + self-repair + code execution + test output prediction

---

## Experiments & Results
- Benchmark shows significant performance variance between models that score similarly on HumanEval/MBPP
- Reveals contamination: models with high HumanEval scores do not always rank as highly on LiveCodeBench
- Temporal trend: model performance on LiveCodeBench grows slower than HumanEval performance (suggests HumanEval contamination in newer models)
- Self-repair capability: less correlated with code generation performance than expected

---

## Limitations & Gaps
- Competitive programming distribution: harder and more algorithmic than real-world code tasks
- Does not evaluate repository-level reasoning (unlike SWE-bench)
- Limited to Python/C++/Java (contest languages)

---

## Relevance to Research Gap
**Key generalization benchmark.** The primary test for Gap 2 (overfitting vs. generalization). If models trained with partial-credit reward on APPS overfit to APPS test suite structure, LiveCodeBench (with novel, unseen problems from post-training contests) will reveal this degradation. Its contamination resistance makes it the ideal OOD test — performance gains on HumanEval that don't transfer to LiveCodeBench signal reward hacking rather than genuine learning.
