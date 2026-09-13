# Title: LLM-Guided Automatic Hyperparameter Scheduling for Reinforcement Learning

## Motivation
Reinforcement learning algorithms are notoriously sensitive to hyperparameter choices, and optimal settings often change throughout training (e.g., learning rate, exploration rate, entropy coefficients). Current approaches either use fixed schedules designed by experts or rely on expensive population-based training. Meanwhile, LLMs possess extensive knowledge about RL algorithms from training corpora but this knowledge remains untapped for dynamic hyperparameter adaptation. Bridging LLMs' reasoning capabilities with online RL training could democratize effective hyperparameter tuning without extensive computational overhead.

## Main Idea
We propose **LLM-as-Scheduler**, a framework where an LLM acts as an intelligent hyperparameter scheduler during RL training. The system periodically summarizes training metrics (returns, loss curves, gradient statistics, exploration metrics) into natural language descriptions and queries an LLM to recommend hyperparameter adjustments. The LLM leverages its encoded knowledge of RL dynamics—such as "high policy entropy early aids exploration" or "reduce learning rate when returns plateau"—to provide contextual scheduling decisions.

**Methodology**: (1) Design compact, informative training state representations as prompts; (2) Fine-tune or prompt-engineer LLMs to output structured hyperparameter modifications; (3) Incorporate a lightweight verification mechanism to filter harmful suggestions.

**Expected Outcomes**: Competitive performance with population-based training at a fraction of the compute cost, improved generalization across diverse environments, and interpretable scheduling decisions via LLM explanations.

**Impact**: This bridges AutoML and LLM communities while making robust RL more accessible to practitioners.