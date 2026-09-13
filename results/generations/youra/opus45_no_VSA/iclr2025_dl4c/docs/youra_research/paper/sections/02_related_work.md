# Related Work

Our work bridges two largely separate research streams---RL training with execution feedback and test-time refinement---that have rarely been combined systematically.

## RL Training for Code Generation

Reinforcement learning from execution feedback has emerged as a powerful paradigm for code generation. CodeRL [Le et al., 2022] treats the code-generating language model as an actor and introduces a critic network to estimate functional correctness, using program execution results as reward signals. This approach achieves state-of-the-art results on APPS and HumanEval by optimizing for test-case pass rates rather than token-level likelihood. PPOCoder [Shojaee et al., 2023] extends this framework with proximal policy optimization, demonstrating improved stability during RL fine-tuning. B-Coder [Yu et al., 2023] introduces value-based RL as an alternative to policy-based methods, leveraging off-policy programs to improve sample efficiency.

**Limitation:** These works evaluate RL-trained models in single-shot mode only. Whether RL training improves the model's ability to iteratively refine code based on execution feedback remains untested.

## Test-Time Refinement

A parallel line of work focuses on improving code generation at inference time without additional training. Self-Refine [Madaan et al., 2023] demonstrates that large language models can iteratively refine their outputs using self-generated feedback, achieving ~20% improvement across diverse tasks including code generation. S* [Li et al., 2025] presents a hybrid test-time scaling framework that enables 3B models to match or exceed GPT-4o-mini on HumanEval through execution-guided search. Recent work on test-time compute scaling [Ma et al., 2025] shows that 32B models can achieve 46% on SWE-bench Verified, outperforming DeepSeek R1 671B through strategic test-time allocation.

**Limitation:** These methods apply refinement to pretrained or instruction-tuned models. Whether RL training provides a better starting point for refinement is not explored.

## Hybrid Approaches

Some recent work has begun exploring hybrid training-inference combinations. RLEF [2025] shows that RL training can improve iterative code refinement on competitive programming tasks, but does not measure the interaction term formally. Rethinking Fine-Tuning [Chen et al., 2025] provides theoretical analysis of how fine-tuning affects test-time compute scaling, but focuses on general LLM capabilities rather than code-specific execution feedback.

**Gap:** No prior work measures the Training×Refinement interaction using factorial designs or operationalizes the mechanism via mutual information metrics.

## Our Position

Unlike prior work that studies RL training or test-time refinement in isolation, we provide the first factorial experimental framework to measure their interaction. We do not claim to improve upon CodeRL or Self-Refine individually; rather, we ask whether combining them produces superadditive gains. Our I(F;E) metric provides a mechanistic probe beyond aggregate accuracy, enabling analysis of *why* interaction effects occur (or fail to occur).
