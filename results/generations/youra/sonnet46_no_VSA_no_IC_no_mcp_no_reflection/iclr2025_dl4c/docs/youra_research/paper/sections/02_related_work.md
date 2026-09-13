# Related Work

## Reinforcement Learning from Execution Feedback for Code LLMs

The dominant paradigm for RLEF post-training of code LLMs uses binary pass/fail reward: the model receives reward 1 if and only if all test cases pass, and 0 otherwise. CodeRL [Le et al., 2022] pioneered this approach with PPO on the APPS dataset [Hendrycks et al., 2021], reporting approximately 5 percentage-point improvements over supervised fine-tuning alone on HumanEval. PPOCoder [Shojaee et al., 2023] extended this framework with additional reward components including syntax correctness signals, but retained binary execution reward as the primary training signal. RLEF/Gehring et al. [2024] applied binary RLEF to repository-level code repair on SWE-bench, demonstrating that execution-grounded reward can produce gains over SFT even in complex agentic settings.

All three works treat reward formulation as a fixed design choice. None analyze whether binary reward's group-level gradient properties are optimal for GRPO, nor do they compare binary reward against ratio or continuous alternatives in controlled ablation. Our work asks a question these papers did not ask: under what conditions does binary reward produce zero gradient contribution in GRPO training, and does ratio reward address this?

## Group Relative Policy Optimization

GRPO [Shao et al., 2024; DeepSeekMath] computes advantages by normalizing rewards within a group of completions, eliminating the need for a separate critic network. This simplification reduces training complexity and memory but changes the reward sparsity problem qualitatively: where PPO's value function provides a baseline even when execution rewards are sparse, GRPO's group normalization can only redistribute signal within a group — it cannot create signal where none exists. If all completions in a group receive the same reward (including all-zero under binary reward), GRPO produces zero gradient contribution from that group.

DAPO [Yu et al., 2025] — the most prominent GRPO-based code and math training framework — acknowledges the sparsity concern and introduces several mitigations (dynamic sampling temperature, clip-higher variant). However, DAPO retains binary reward and does not quantify the fraction of training groups that fall into the all-zero regime. Our analysis shows that under realistic early-training conditions (p_pass ≈ 0.1 per test case), 98.7% of GRPO groups receive zero binary reward for all completions — a dead zone that DAPO's mitigations do not directly address for hard coding tasks.

## Reward Signal Density and Sparsity

The problem of sparse rewards in reinforcement learning has a long history [Sutton & Barto, 2018]. Reward shaping [Ng & Russell, 1999] addresses sparsity at the policy level by adding potential-based bonuses that preserve the optimal policy. In the RLEF context, several works have proposed intermediate rewards based on syntax correctness [PPOCoder], compilation status, or partial test passage. However, these works use PPO with a critic network rather than GRPO, which changes the analysis: the critic provides a state-value baseline that partially compensates for sparse rewards in PPO but is absent in GRPO.

The ratio reward we analyze (k/n test cases passing) is an instance of partial-credit reward. Some earlier RL-for-code works (e.g., PLUR [Drori et al., 2022]) have used partial-credit signals, but not in conjunction with GRPO and not with the specific analytical framing we provide. Our contribution is not the reward function itself — ratio reward is a natural generalization of binary reward — but the group-level analysis showing when it provides a mathematical guarantee of gradient signal that binary reward cannot provide.

## The APPS Dataset

APPS [Hendrycks et al., 2021] is a competitive programming dataset with 10,000 problems spanning introductory to competition difficulty. Its native multi-test-case structure (many problems have 10+ test cases) makes it well-suited for ratio reward: the fraction of passing test cases provides a continuous signal in (0, 1) when solutions are partially correct. Prior RLEF work (CodeRL, PPOCoder) trained on APPS with binary reward; we use the same dataset but exploit its partial-credit structure.

Our experiments reveal that APPS competition-level problems require longer generation than the 512-token budget used in h-m1: DeepSeek-Coder-6.7B produces truncated (non-executable) completions at all steps under this budget. This finding is consistent with CodeRL's use of larger generation budgets for APPS training and establishes generation length as a binding constraint for 6.7B-class models on competition-level problems.

## Positioning

Our work differs from all prior RLEF literature in two ways. First, we analyze gradient signal quality at the GRPO group level — the atomic unit of computation — rather than at the aggregate training curve level. This framing reveals the binary reward dead zone that is invisible in aggregate metrics. Second, we separate the mechanistic existence claim (ratio reward guarantees non-zero advantage variance) from the policy-level performance claim (ratio reward improves benchmark performance), and show that the latter requires experimental conditions that prior work did not validate before training. This methodological contribution is independent of the specific reward functions compared.
