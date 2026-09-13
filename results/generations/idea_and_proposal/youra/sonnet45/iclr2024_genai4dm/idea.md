# Title
Narrative Coherence as Intrinsic Motivation: Using LLM Priors to Guide Exploration in Sparse-Reward Sequential Decision Making

# Motivation
Current reinforcement learning agents struggle with long-horizon sparse-reward tasks requiring causal reasoning, as traditional exploration methods (RND, ICM) prioritize state novelty over semantic meaningfulness. While pretrained generative models contain rich priors about causal relationships, their potential for guiding exploration remains underexplored. This research addresses the critical gap of leveraging large language models to improve sample efficiency in semantically-rich decision-making environments where discovering coherent causal sequences is essential for success.

# Main Idea
We propose Narrative Coherence Intrinsic Motivation (NCIM), which augments traditional exploration bonuses with LLM-evaluated narrative coherence scores. The core mechanism converts state trajectories to natural language, then uses frozen LLMs to assess coherence via two metrics: causal completeness (unresolved entity references) and prediction violation (semantic surprisal). The intrinsic reward combines these scores with RND: r_intrinsic = α×r_RND + (1-α)×r_narrative, directing agents toward resolving meaningful storylines rather than merely novel states.

We test this in NetHack, Crafter, and TextWorld environments, predicting 20-30% improvement in task success rates and 40-50% more unique causal sequence discovery within 10M steps. Falsification criteria include no significant improvement over baselines and computational overhead exceeding 20%. This bridges cognitive science's Information Gap Theory with computational exploration, offering a practical method for long-horizon sparse-reward tasks.