# Related Work

We survey three areas relevant to SA-based code quality prediction: static analysis for LLM code, self-repair and iterative refinement, and code generation evaluation. Our positioning: prior work uses SA for feedback (correction) rather than prediction (correlation)—we fill this gap.

## Static Analysis for LLM-Generated Code

Recent studies integrate static analysis into LLM code generation pipelines, but as feedback rather than predictors. Blyth et al. [2025] demonstrate an iterative feedback loop where Bandit and Pylint errors are fed back to the LLM for self-correction. Their approach reduces security vulnerabilities from >40% to 13% and readability violations from >80% to 11% within 10 iterations on HumanEval/MBPP. However, they measure improvement magnitude, not predictive correlation—whether SA scores before correction predict which samples will pass tests.

AutoSafeCoder [Nunez et al., 2024] combines multi-agent SA with fuzz testing, achieving 13% reduction in code vulnerabilities. CodeQUEST [Liu et al., 2025] uses GPT-4o to iteratively improve code quality as measured by Pylint Score, Radon Maintainability, and Bandit logs, reporting 52.6% mean improvement and "meaningful correlation" between SA metrics and quality. Yet neither study quantifies this correlation—no r-values or regression coefficients appear.

STALL+ [Liu et al., 2024] integrates static analysis at the prompting phase for repository-level code completion, finding SA integration performs best when combined with RAG. Their focus is on improving generation quality through SA-informed prompts, not on using SA metrics as standalone predictors of correctness.

Our work differs fundamentally: we measure correlation directly (r=0.87 for pylint-correctness), enabling SA-based rejection sampling without any LLM feedback loop.

## Self-Repair and Iterative Refinement

The self-repair paradigm feeds execution feedback—including SA errors—back to LLMs for correction. Olausson et al. [2024] systematically study self-repair effectiveness, finding it improves pass rates but is not universally effective across models. Arimbur [2026] shows self-repair improves HumanEval pass rates by +4.9 to +17.1 percentage points, with most gains occurring in the first 2 iterations.

CodeCoR [Pan et al., 2025] achieves 77.13% average Pass@1 on HumanEval/MBPP using multi-agent pruning and test case generation. INTERVENOR [NEUIR, 2024] employs Code Teacher and Code Learner agents with compiler feedback. RePair [TnTWoW, 2024] uses process-based feedback with a reward model as critic.

These approaches share a common assumption: SA feedback is useful for correction. Our work tests a logically prior question: does SA signal predict correctness in the first place? If correlation is weak, iterative feedback may work through mechanisms other than SA signal (e.g., LLM exploration through regeneration). Our finding that r=0.87 validates the assumption underlying these approaches.

## Code Generation Evaluation

Benchmark infrastructure underpins code generation research. Chen et al. [2021] introduced HumanEval with 164 hand-crafted problems and the pass@k metric. Austin et al. [2021] created MBPP with 974 problems (427 sanitized). Liu et al. [2023] extended these with EvalPlus, adding 80× more test cases to HumanEval+ and revealing that 19-29% of previously "correct" code actually fails under rigorous testing.

Yetistiren et al. [2023] evaluate Copilot, CodeWhisperer, and ChatGPT on HumanEval across correctness, security, reliability, and maintainability dimensions, using Radon, Bandit, and Pylint as quality metrics. However, they report quality scores and correctness separately—no correlation analysis between the two.

We build on this evaluation infrastructure while filling the correlation gap: using HumanEval+MBPP as ground truth, we measure how well SA metrics predict pass@1 outcomes.

## Our Contribution

Table 1 summarizes the positioning. Prior work uses SA for improvement feedback; we use it for prediction. Prior work reports quality metrics and correctness separately; we correlate them. This enables a new capability: SA-based rejection sampling without additional LLM calls.

| Work | SA Usage | Correlation Measured | r-Value Reported |
|------|----------|---------------------|------------------|
| Blyth et al. [2025] | Feedback loop | No | — |
| CodeQUEST [2025] | Iterative improvement | "Meaningful" (qualitative) | — |
| AutoSafeCoder [2024] | Multi-agent feedback | No | — |
| Yetistiren et al. [2023] | Quality measurement | No | — |
| **Ours** | **Prediction** | **Yes** | **r=0.87** |

*Table 1: Comparison of SA usage in prior work. We are the first to quantify SA-correctness correlation.*
