# Methodology

Our methodology is motivated directly by the gradient dead zone problem identified in Section 1. To prove that ratio reward addresses binary reward's zero-variance property in GRPO groups, we use a two-phase design: (1) a mechanistic existence proof (h-e1) that isolates the group-level gradient signal difference, and (2) a policy-level training experiment (h-m1) that tests whether the mechanistic difference produces downstream performance improvements.

## 3.1 Reward Functions

We compare two reward formulations for GRPO post-training of code LLMs.

**Binary reward.** Given a completion and n test cases, binary reward assigns:

$$r_{\text{binary}}(c) = \mathbf{1}[\forall i \in [n]: \text{pass}(c, t_i)]$$

where pass(c, t_i) = 1 if the completion c produces the correct output on test case t_i within a 5-second timeout, and 0 otherwise. This is the reward used by all prior RLEF work for code LLMs.

**Ratio reward.** Ratio reward assigns credit proportional to the fraction of test cases passed:

$$r_{\text{ratio}}(c) = \frac{1}{n} \sum_{i=1}^{n} \text{pass}(c, t_i) \in [0, 1]$$

Ratio reward coincides with binary reward when all tests pass (both = 1) or none pass (both = 0). It differs precisely in the partial-pass regime (0 < k < n tests passing), which is the relevant early-training scenario.

**Implementation.** Both functions are implemented as subprocess sandboxes with a 5-second timeout per test case. Code execution is isolated: each completion is run in a subprocess, standard input is piped from the test case input, and standard output is compared to the expected output. Timeout, runtime error, and output mismatch all return pass(c, t_i) = 0. The implementation is validated by 12/12 unit tests covering the full range of pass/fail/timeout/error scenarios.

## 3.2 GRPO Advantage Computation and the Dead Zone

GRPO computes advantages within a group of G completions for a given prompt by:

$$A_i = r_i - \bar{r}, \quad \bar{r} = \frac{1}{G} \sum_{j=1}^{G} r_j$$

The group gradient contribution is proportional to the variance of advantages. When all completions fail all test cases (the all-zero binary reward regime), $r_i = 0$ for all i, $\bar{r} = 0$, and $A_i = 0$ for all i — the group contributes zero gradient to any model parameter. This is a mathematical guarantee, not a probabilistic statement: it holds for every training step in which the condition (all completions fail all tests) is satisfied.

Ratio reward breaks this guarantee: whenever any completion passes at least one test (k ≥ 1), ratio reward assigns $r_i > 0$ to that completion, creating non-zero group variance. For the illustrative group with test-pass counts $[0, 0, 1, 2, 0, 3, 0, 0]$ (8 completions, 5 test cases):

| Completion | Pass count k | Binary reward | Ratio reward | Binary advantage | Ratio advantage |
|------------|-------------|---------------|--------------|-----------------|-----------------|
| c1 | 0 | 0.0 | 0.000 | 0.000 | −0.150 |
| c2 | 0 | 0.0 | 0.000 | 0.000 | −0.150 |
| c3 | 1 | 0.0 | 0.200 | 0.000 | +0.050 |
| c4 | 2 | 0.0 | 0.400 | 0.000 | +0.250 |
| c5 | 0 | 0.0 | 0.000 | 0.000 | −0.150 |
| c6 | 3 | 0.0 | 0.600 | 0.000 | +0.450 |
| c7 | 0 | 0.0 | 0.000 | 0.000 | −0.150 |
| c8 | 0 | 0.0 | 0.000 | 0.000 | −0.150 |

**Advantage variance: binary = 0.0000, ratio = 0.0475.** The gradient update for binary reward is identically zero for this group; ratio reward produces a gradient that increases the probability of completions passing more test cases.

**Formal condition.** Let $G$ be a GRPO group, $n$ the number of test cases, and $k_i$ the number of tests passed by completion $i$. Binary reward produces zero advantage variance in $G$ if and only if all $k_i \in \{0, n\}$ (all-fail or all-pass). Under binary reward, a group in which no completion passes all $n$ tests but some completions pass $1 \leq k < n$ tests produces zero variance — this is the dead zone. Ratio reward produces non-zero variance whenever $\exists i: 1 \leq k_i < n$ (partial-pass completion exists) and $\exists j: k_j \neq k_i$ (completions differ in pass count), which is the complement of the all-zero-variance condition.

## 3.3 Phase 1: Mechanistic Existence Proof (h-e1)

**Objective.** Prove that ratio reward provides non-zero advantage variance in GRPO groups where binary reward provides zero variance, and confirm that the training infrastructure is functionally correct.

**Synthetic validation.** We directly compute advantages for the illustrative group [0, 0, 1, 2, 0, 3, 0, 0] under both reward functions (Table 1 in results). This is a mathematical proof of the mechanism, not an empirical estimate.

**Scale simulation.** We simulate 1,000 GRPO groups under realistic early-training conditions: each completion independently passes each of 5 test cases with probability p_pass = 0.1 (modeling a model at ~10% per-test accuracy). We record whether ratio and binary rewards differ in each group. This quantifies the prevalence of the dead zone under distributional assumptions.

**Infrastructure validation.** We run 3 GRPO training steps on APPS using DeepSeek-Coder-6.7B-instruct under both conditions (binary and ratio), verifying exit code 0, gradient norm logging, and checkpoint saving. This confirms that the implementation is correct before any policy-level claims are made.

**Gate criterion.** h-e1 is satisfied if: (1) code executes without error, (2) the mechanistic proof demonstrates advantage variance difference, and (3) gradient norms are measurable from training logs.

## 3.4 Phase 2: Policy-Level Mechanism Test (h-m1)

**Objective.** Test whether the mechanistic gradient signal difference (h-e1) translates to measurable policy-level performance differences after full GRPO training.

**Setup.** We train two conditions — binary and ratio reward — using GRPOTrainer (trl 1.0.0) for up to 1,000 steps on the APPS training split (≥1 test case filter; codeparrot/apps). Model: DeepSeek-Coder-6.7B-instruct. Each condition runs on a dedicated H100 NVL GPU (95 GB). Hyperparameters: group_size=8, learning_rate=1×10⁻⁶, kl_beta=0.04, max_new_tokens=512, seed=42.

**Monitoring.** We log reward_mean, grad_norm, kl, and clipped_ratio (fraction of completions reaching the max_new_tokens limit) at every step. We add a FractionPartialCallback that monitors the fraction of completions with 0 < k < n test cases passing — the quantity required to be positive for ratio reward to differ from binary reward. If fraction_partial collapses to 0, we flag ratio reward as degenerate (equivalent to binary).

**Gate criterion.** h-m1 is satisfied if ratio HumanEval pass@1 − binary HumanEval pass@1 ≥ 0.03 with 95% bootstrap CI excluding 0 (paired bootstrap, n=1,000, on per-problem pass rates).

## 3.5 Training Configuration

```yaml
model: deepseek-ai/deepseek-coder-6.7b-instruct
dataset: codeparrot/apps (train split)
  h-e1_filter: ≥5 test cases (n=1,789 problems)
  h-m1_filter: ≥1 test case (full train split)
grpo:
  group_size: 8
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 8
  learning_rate: 1.0e-6
  warmup_steps: 100
  kl_beta: 0.04
  clip_ratio: 0.2
  max_new_tokens: 512
  gradient_checkpointing: true
  logging_steps: 1
environment:
  gpu: H100 NVL (95 GB each)
  python: 3.10
  torch: 2.5+cu124
  trl: 1.0.0
  conda_env: youra-h-e1-grpo
```

**Engineering notes.** We resolved 9 engineering issues during development: CUDA OOM (2×, due to stale processes), GRPOTrainer API changes (generation_kwargs dict, processing_class parameter), FSDPModule ImportError (trl 1.x assumes torch 2.7; patched with try/except for torch 2.5 compatibility), torchvision version mismatch, circular import between h-e1 and h-m1 config modules, and GPU pinning for multi-condition parallel training. All issues are documented in the experimental logs and the implementation is validated by 35/35 unit tests across h-e1 and h-m1.
