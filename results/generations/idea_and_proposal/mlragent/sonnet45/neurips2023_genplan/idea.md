# Title
Compositional Policy Synthesis via Learned Symbolic Abstractions for Few-Shot Transfer in Sequential Decision-Making

# Motivation
Current deep RL methods struggle with sample efficiency and transferability across problem variants, while classical planning requires hand-crafted symbolic representations. The gap between low-level sensorimotor control and high-level symbolic reasoning prevents agents from efficiently generalizing like humans do—learning abstract patterns from few examples and composing them for novel tasks. We need methods that automatically discover reusable symbolic abstractions from raw experience while maintaining the expressiveness needed for complex control.

# Main Idea
We propose a neuro-symbolic framework that learns compositional symbolic abstractions from demonstrations or limited interactions. The approach has three components:

1. **Abstraction Learning Module**: Uses neural networks to automatically discover latent predicates and operators from state-action trajectories, clustering experiences into symbolic abstractions via contrastive learning and information bottleneck principles.

2. **Compositional Policy Synthesis**: Represents policies as compositions of learned symbolic operators (analogous to STRIPS-like actions), enabling systematic generalization through symbolic planning over the learned abstraction space.

3. **Few-Shot Adaptation**: Given a new problem variant, the agent quickly identifies which learned abstractions apply and synthesizes novel policy compositions without retraining low-level controllers.

**Expected outcomes**: Demonstrate 10-100× improved sample efficiency on procedurally generated domains (e.g., craft-like environments, robot manipulation variants) compared to end-to-end deep RL, with provable compositional generalization guarantees under mild assumptions about environment structure.