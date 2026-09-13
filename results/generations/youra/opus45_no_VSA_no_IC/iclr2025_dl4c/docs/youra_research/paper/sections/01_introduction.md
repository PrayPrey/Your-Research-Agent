# Introduction

When all three LLM judges—from 7B to proprietary scale—unanimously agree that a code solution is correct, the verdict is wrong 64% of the time. This counterintuitive finding challenges the common assumption that model scale directly correlates with reliability and that ensemble agreement signals confidence.

LLM-as-judge has emerged as a practical alternative to execution-based evaluation for code correctness assessment. With execution requiring test infrastructure and compute resources, practitioners increasingly deploy language models to judge whether generated code will pass tests—without running them. Industry adoption is accelerating, with millions of daily LLM-based code evaluations across development pipelines, code review automation, and quality filtering systems.

Yet practitioners face a critical decision with little empirical guidance: which model scale to deploy? Common intuitions suggest that larger models provide higher accuracy and that combining multiple scales through ensemble voting should improve reliability. Neither assumption has been systematically tested for code correctness judgment.

Prior work establishes that LLM code judges exhibit biases (Moon et al., 2025), that even GPT-4 "frequently misjudges" correctness (Crupi et al., 2025), and that test-time scaling via MCTS can improve single-model accuracy from 41% to 80% (Wang et al., 2025). However, no prior work has conducted scale-controlled comparison with fixed evaluation settings to isolate the effect of model scale on error patterns.

We address this gap by investigating scale-dependent error patterns in LLM code judges. Our key insight is that **scale predicts error TYPE, not just error RATE**. Smaller models (7B) systematically over-accept—declaring incorrect code as correct (FPR=74.8%). Larger models (proprietary) systematically under-accept—rejecting correct code (FNR=29.3%). These asymmetric error profiles explain why ensemble voting fails: the over-accepting majority drowns the accurate minority signal.

We evaluate four predictions under standardized conditions (fixed zero-shot prompt, temperature=0, HumanEval+ ground truth):

1. **Scale ordering with diminishing returns** (P1): Judge-execution agreement increases with scale, but the 7B→70B gain is much larger than 70B→proprietary.

2. **Scale-dependent error patterns** (P2): Different scales exhibit statistically different FP/FN ratios, not random variation.

3. **Ensemble benefit** (P3): Scale-diverse majority voting outperforms the best single judge by ≥3%.

4. **Unanimous reliability** (P4): When all scales agree, accuracy is ≥10% higher than when they disagree.

Our results confirm P1 and P2 with strong statistical evidence (p=0.021 and p=3.27×10⁻⁸ respectively), but **falsify** P3 and P4. Ensemble voting degrades accuracy by 8.05% compared to the best single judge. Unanimous agreement correlates with *lower* accuracy than disagreement—the opposite of the hypothesized effect.

These findings make three contributions:

- **First scale-controlled characterization** of FP/FN error patterns in LLM code judges, showing that scale determines error type through a FPR-FNR tradeoff.

- **Falsification of the ensemble hypothesis** with statistical significance (McNemar p=1.45×10⁻⁶), demonstrating that scale diversity does not confer ensemble benefit when errors are asymmetric.

- **Practical guidance** for scale-cost tradeoffs: use 70B models for best cost-accuracy balance; select scale based on which error type is more costly to your application.

The remainder of this paper reviews related work on LLM evaluation metrics and code judges (§2), details our experimental methodology (§3), describes experimental setup and predictions (§4), presents results (§5), interprets findings with honest limitations (§6), and concludes with future directions (§7).
