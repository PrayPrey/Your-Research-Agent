## 1. Introduction

We trained the same code language model on four different practice problem sets and found that
practicing HumanEval-style algorithm completions made the model better at MBPP utility scripts
than practicing MBPP scripts directly — consistently across all three random seeds. This
counterintuitive result is not a fluke: it reveals a precise, embedding-measurable mechanism
governing what code SFT actually teaches.

Code LLMs are routinely fine-tuned on mixes of public datasets — HumanEval training problems,
MBPP utility scripts, LeetCode algorithmic challenges — but practitioners choose these sources
based on intuition rather than measurement. The prevailing assumption is that training on X
specializes a model for X: MBPP training should confer MBPP benchmark advantage; HumanEval
training should sharpen HumanEval performance. If this intuition were correct, source selection
would be straightforward. It is not correct.

The deeper problem is that no controlled study has isolated the causal effect of SFT source
identity on code benchmark pass@1 while holding model architecture, token budget, training
hyperparameters, and supervision format constant. Existing code SFT papers vary data quality,
quantity, and format simultaneously, making causal attribution impossible. Domain mixture
optimization literature [Xie et al., 2023; Zhang, 2026] addresses pretraining but has not
been applied as a source-identity ablation for code-specific SFT with execution-based
evaluation. The gap — a controlled 4-source × 2-benchmark transfer matrix with token-budget
equalization — does not exist in the literature.

We close this gap and discover that source selection is not a neutral engineering choice: it
is the dominant factor governing post-SFT benchmark performance. Under identical token budgets,
HumanEval-only training achieves 32.6% HumanEval+ pass@1 while LeetCode-only training achieves
3.0% — a 29.6 percentage point gap for the same model on the same compute budget. This effect
dwarfs most reported architectural improvements.

The key insight enabling our analysis: **code-embedding cosine similarity between the SFT
training source and the test benchmark perfectly predicts the pass@1 rank order across all four
conditions.** When we rank sources by CodeBERT embedding similarity to HumanEval+, the order
is HumanEval > MBPP > Equal-mix > LeetCode. This matches the observed pass@1 rank exactly
(Spearman ρ=1.0, permutation test p=0.042, n=10,000 shuffles). Embedding-space distributional
alignment is a measurable, pre-training predictor of SFT behavioral outcomes.

This insight also explains the counterintuitive finding: HumanEval-style algorithmic function
completion problems are embedding-closer to both HumanEval+ and MBPP+ than MBPP utility scripts
are. The training distribution that best aligns with the test distribution — regardless of
surface-level similarity — produces the best performance.

Building on this insight, we make the following contributions:

1. **First controlled source-identity ablation for code SFT**: We train DeepSeek-Coder-1.3B/7B-Base
   on four isolated conditions (HumanEval-only, MBPP-only, LeetCode-only, Equal-mix) with
   token-budget equalization, deduplication, and format normalization — enabling causal
   attribution of the 29.6pp source identity effect (ANOVA F=11.37, p=0.020).

2. **Distributional alignment predicts code SFT rank order**: CodeBERT embedding cosine
   similarity between training source and test benchmark perfectly predicts HumanEval+ pass@1
   rank across all four conditions (ρ=1.0, p=0.042, dual-encoder concordant), providing the
   first permutation-tested evidence that embedding-space alignment governs code SFT
   specialization.

3. **HumanEval SFT confers cross-benchmark coding advantage**: Contrary to symmetric
   specialization, HumanEval-only training achieves the highest pass@1 on both HumanEval+
   (35.9%) and MBPP+ (~52%), suggesting that algorithmic function-completion training develops
   more transferable Python programming competence than utility-script training.

4. **Methodological insight on scale comparison**: At 7B scale, within-condition seed variance
   collapses to near-deterministic (σ²=0.00043), inflating η² and motivating absolute
   condition spread as the primary scale-comparison metric.

We organize the paper as follows: Section 2 surveys related work on domain mixture optimization,
code SFT, and alignment prediction. Section 3 describes our experimental methodology. Section 4
presents the experimental setup. Section 5 reports results. Section 6 discusses findings and
limitations. Section 7 concludes.
