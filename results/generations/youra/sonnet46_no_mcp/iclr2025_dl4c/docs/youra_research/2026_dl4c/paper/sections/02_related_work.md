# 2. Related Work

## 2.1 Execution-Feedback Reinforcement Learning for Code

Reinforcement learning with execution feedback has emerged as a powerful paradigm for training code-generating models. **CodeRL** [Le et al., 2022] was among the first to train a code generation model using RL directly on APPS execution outcomes, demonstrating measurable pass@1 improvements over supervised fine-tuning. However, CodeRL uses uniform random sampling from the APPS dataset and does not analyze how difficulty composition affects training effectiveness. The possibility that reward sparsity on harder problems degrades RL training is not addressed.

**RLEF** [Gehring et al., 2024] extends execution-feedback RL to function-level benchmarks (HumanEval, MBPP, APPS) and demonstrates that iterative refinement with execution-grounded reward outperforms both SFT and standard RLHF approaches. While RLEF provides important evidence for execution-feedback RL's general effectiveness, it does not report per-step training diagnostics such as advantage variance or reward density, and training data composition is not a research variable.

**DeepSeek-R1** [DeepSeek-AI, 2025] applies GRPO at scale with competitive programming data, achieving strong reasoning performance. The paper demonstrates that group-relative advantage normalization enables effective policy optimization on reasoning tasks. However, DeepSeek-R1 operates at model scales (>30B parameters) where non-zero solve rates are common, and the paper does not characterize what happens when the initializing policy cannot solve the training problems — the regime our work targets.

None of these prior works measure GRPO advantage variance as a function of task difficulty or execution reward sparsity. Our work fills this diagnostic gap by directly quantifying the advantage collapse that occurs when execution feedback is too sparse to produce informative group-relative gradients.

## 2.2 Curriculum Learning

The theoretical foundation for easy-to-hard curriculum ordering in machine learning was established by **Bengio et al.** [2009], who showed that training on easier examples first can accelerate convergence and improve generalization for a wide range of learning tasks. The key intuition is that easy examples provide stable, consistent gradient signal early in training, when the model is most sensitive to the direction of the update.

Subsequent work has extended curriculum learning to neural machine translation [Platanios et al., 2019], question answering [Sachan and Xing, 2016], and more recently to language model fine-tuning [Xu et al., 2020]. However, curriculum learning has not been systematically instantiated in execution-feedback GRPO training. Our work establishes the mechanistic precondition for curriculum GRPO: that a reward density gradient across difficulty levels must exist for the curriculum effect to activate.

**Self-paced learning** [Kumar et al., 2010] extends curriculum learning by adapting difficulty selection to the model's current performance rather than following a pre-defined schedule. This direction is complementary to our fixed-split curriculum approach and represents an avenue for future work once the static curriculum's viability is established.

## 2.3 GRPO and Group-Relative Policy Optimization

GRPO [Shao et al., 2024] replaces the learned value baseline of PPO [Schulman et al., 2017] with a group-relative normalization scheme: for each prompt, $G$ completions are sampled and advantages are computed relative to the group's mean and standard deviation. This eliminates the need for a separate critic model but introduces a structural dependency: meaningful gradients require reward variance *within each group*. When all completions receive identical reward, the advantage is zero and the gradient contribution vanishes.

**AlphaCode** [Li et al., 2022] demonstrates that performance on competitive programming degrades sharply with difficulty tier, confirming that the solve rate distribution is highly skewed toward hard problems for most models. Our work quantifies how this skew translates into advantage variance collapse in GRPO.

## 2.4 Positioning

Our work differs from prior execution-feedback RL papers in two key respects. First, we measure *training diagnostics* (advantage variance, reward density) rather than only benchmark outcomes, making the failure mode visible rather than inferring it from marginal performance gains. Second, we provide a controlled cross-granularity comparison that isolates the effect of reward sparsity from other confounders (model scale, training duration, dataset size). This diagnostic contribution is a prerequisite for the principled design of curriculum approaches to execution-feedback GRPO.
