# Title
Hierarchical Foundation Model Planning with Learned Temporal Abstractions for Long-Horizon Decision Making

# Motivation
Foundation models excel at reasoning about high-level semantic concepts but struggle with long-horizon decision making due to compounding errors and computational constraints. Traditional hierarchical RL methods require task-specific reward engineering and fail to leverage the rich world knowledge in pretrained models. There is a critical need for methods that automatically decompose complex tasks into semantically meaningful subgoals while maintaining the generalization capabilities of foundation models.

# Main Idea
We propose a hierarchical framework where a vision-language foundation model learns to generate temporal abstractions (subgoals) for long-horizon tasks, while a lower-level policy trained with RL executes these subgoals. The key innovation is **automatic subgoal discovery** through analyzing foundation model representations across successful trajectories in diverse environments.

**Methodology:**
1. Use unsupervised clustering on foundation model embeddings to identify natural "semantic waypoints" in task demonstrations
2. Train a high-level planner (fine-tuned foundation model) to predict sequences of these waypoints given task descriptions
3. Train low-level policies via RL to achieve each waypoint, with foundation model providing shaped rewards

**Expected Outcomes:**
- Improved sample efficiency through knowledge transfer and skill reuse
- Better generalization to novel task compositions
- Interpretable intermediate representations for debugging

**Impact:** This bridges the gap between foundation models' semantic understanding and RL's sequential optimization, enabling practical deployment in robotics, autonomous systems, and interactive agents.