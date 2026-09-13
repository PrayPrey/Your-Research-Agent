# Title
Adaptive Preference Elicitation under Strategic Behavior: Learning Human Utilities from Inconsistent Feedback

## Motivation
Current algorithmic decision-making systems assume user preferences remain stable and honestly reported. However, users often exhibit strategic behavior—gaming recommendation systems, misreporting preferences to explore alternatives, or behaving inconsistently due to bounded rationality. This creates a fundamental challenge: algorithms trained on strategic feedback learn distorted preference models, leading to suboptimal personalization and potential manipulation vulnerabilities. Understanding and modeling this strategic human-algorithm interaction is crucial for building robust decision-making systems that converge to socially beneficial outcomes despite non-truthful behavior.

## Main Idea
We propose a framework that jointly models strategic user behavior and learns true underlying preferences through repeated interactions. The key innovation is treating preference elicitation as a dynamic game where:

1. **User Model**: We model users as boundedly rational agents with true latent utilities but who strategically report preferences based on their belief about the algorithm's behavior and exploration incentives.

2. **Algorithm Design**: Develop a meta-learning approach that maintains beliefs over both true preferences and strategic behavioral patterns, using inverse reinforcement learning to disentangle genuine preferences from strategic distortions.

3. **Convergence Analysis**: Prove conditions under which the algorithm-user interaction converges to truthful preference revelation, leveraging mechanism design principles.

**Expected outcomes**: Algorithms robust to strategic manipulation, theoretical guarantees on convergence to true preferences, and empirical validation on recommendation systems showing improved long-term user satisfaction and reduced gaming behavior.