# Title
**Effort-Aware Preference Learning: Modeling Cognitive Cost in Human Feedback for AI Alignment**

## Motivation
Current AI alignment methods assume humans provide feedback with consistent effort and rationality, ignoring that real human feedback quality varies dramatically based on cognitive load, task complexity, and fatigue. When humans are asked to rank AI outputs or provide demonstrations, they often satisfice rather than optimize, especially for difficult comparisons. This leads to noisy, inconsistent feedback that misleads alignment algorithms. Understanding and modeling the *effort* humans invest in providing feedback is crucial for building robust alignment systems that can distinguish between carefully considered preferences and low-effort responses.

## Main Idea
We propose a framework that jointly models human preferences and the cognitive effort invested in expressing them. The key innovation is treating effort as a latent variable that influences feedback reliability. We develop:

1. **Effort-conditional reward models** that weight feedback by estimated cognitive cost (response time, choice difficulty, attention patterns)
2. **Active querying strategies** that optimize the effort-information tradeoff, asking simpler questions when detecting low engagement
3. **Hierarchical Bayesian models** that learn both individual effort patterns and task-specific difficulty

We'll validate this on RLHF for LLMs and preference-based robotics tasks, showing improved alignment with true human values while reducing annotation burden. Expected outcomes include more sample-efficient learning and better handling of feedback heterogeneity across users and contexts.