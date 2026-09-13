# Experimental Setup

## 4.1 Experimental Design

Our experiments answer two questions that follow directly from the gradient dead zone analysis in Section 3.

**Question 1 (h-e1).** Does ratio reward produce detectably different GRPO advantage variance than binary reward in groups representative of early-training conditions?

**Question 2 (h-m1).** Does the gradient signal difference (Q1) translate to measurable policy-level performance improvements (HumanEval pass@1 and APPS all-pass rate) after 1,000 GRPO training steps?

The two questions correspond to two phases of the causal chain: gradient signal differentiation (Step 1) and policy target shift (Step 2). We test them sequentially because Step 2 is only observable if Step 1 holds and the experimental setup satisfies the partial-pass prerequisite.

## 4.2 Dataset

**APPS** [Hendrycks et al., 2021] (codeparrot/apps, train split) is a competitive programming dataset with problems spanning introductory to competition difficulty. Its native multi-test-case structure (many problems have 10+ test cases per problem) makes it the natural setting for ratio reward: k/n is well-defined and informative when n ≥ 2.

For h-e1 (mechanistic proof), we filter to problems with ≥5 test cases (n = 1,789 problems), ensuring ratio reward has meaningful resolution (at least 5 distinct values in [0, 0.2, 0.4, 0.6, 0.8, 1.0]).

For h-m1 (policy-level training), we use the full train split filtered to ≥1 test case, maximizing training diversity.

## 4.3 Model

**DeepSeek-Coder-6.7B-instruct** [Guo et al., 2024] (deepseek-ai/deepseek-coder-6.7b-instruct) is a 6.7B-parameter decoder-only transformer specialized for code generation, with strong HumanEval (~52% pass@1) and MBPP (~65% pass@1) baselines. It is a representative 7B-class open-weight code LLM with publicly available weights and an instruct variant suitable for GRPO fine-tuning.

## 4.4 Baseline

The primary comparison is **binary vs. ratio reward** under identical GRPO training conditions. Binary reward is the control condition (universal baseline in prior RLEF work). Ratio reward is the treatment condition. All other variables are held constant: same model, same dataset, same GRPO hyperparameters, same number of training steps, separate dedicated GPUs to prevent interference.

## 4.5 Evaluation Metrics

**Advantage variance (h-e1).** Directly measures the group-level gradient signal: Var({r_i − mean(r)}_{i=1}^G). This is the mechanistic quantity; binary must produce 0.0 and ratio must produce > 0 in the dead zone.

**Gradient norm trajectory (h-e1, h-m1).** Per-step L2 norm of model gradients, logged by GradNormCallback at every step. A 95% bootstrap CI (paired, n=1,000 bootstrap samples) on (ratio_grad_norm − binary_grad_norm) over steps 100–500 tests whether the conditions produce detectably different training dynamics.

**FractionPartialCallback (h-m1).** Fraction of completions per batch with 0 < k < n test cases passing. This diagnostic monitors whether the partial-pass prerequisite is satisfied during training. If fraction_partial = 0 throughout, both rewards are equivalent (both = 0 or both = 1 for all completions).

**Clipped ratio (h-m1).** Fraction of completions reaching the max_new_tokens limit. If clipped_ratio → 1.0, all completions are truncated and no test cases are executed, making both rewards = 0.

**HumanEval pass@1 (h-m1).** Greedy-decode pass@1 on 164 HumanEval problems [Chen et al., 2021], evaluated at training checkpoints (steps 200, 400, 600, 800, 1,000). The gate criterion is ratio − binary ≥ 0.03 (3 percentage points) with 95% bootstrap CI excluding 0.

## 4.6 h-e1: Mechanistic Existence Proof

The h-e1 experiment has three components:

**Synthetic group computation.** We directly compute binary and ratio rewards, group means, advantages, and advantage variance for the illustrative group with test-pass counts [0, 0, 1, 2, 0, 3, 0, 0] (8 completions, 5 test cases). This produces the Table 1 values in Section 5.

**Scale simulation.** We simulate 1,000 GRPO groups. Each group contains G = 8 completions; each completion independently passes each of n = 5 test cases with probability p_pass = 0.1 (modeling early-training conditions). For each group, we compute binary and ratio rewards and record whether the two differ (i.e., whether at least one completion has partial credit). This produces the 98.7% coverage figure.

**Smoke test.** We run 3 actual GRPO training steps (binary condition, GPU 0) and verify: exit code 0, gradient norm logged, no errors. This validates the code infrastructure independently of the mechanistic proof.

## 4.7 h-m1: Policy-Level Training

The h-m1 experiment runs full GRPO training for 1,000 steps under both conditions simultaneously on separate GPUs (binary: GPU 3; ratio: GPU 4). Training is launched at the same wall-clock time to ensure step-aligned comparison. Checkpoints are saved at steps 200, 400, 600, 800, and 1,000; HumanEval is evaluated at all checkpoints; MBPP and APPS all-pass rate are evaluated at step 1,000.

The FractionPartialCallback fires at every logging step (every step, since logging_steps=1), reporting the fraction of the current batch's completions that achieve 0 < k < n test cases passing. This diagnostic is the primary early-stopping criterion: if fraction_partial = 0 consistently (ratio reward degenerate), the experiment is terminated and routed to Phase 0 redesign.
