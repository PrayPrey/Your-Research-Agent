# Research Idea

## Title
Bidirectional Predictive Gradients: Shared Dynamics Encoders for Faster Model-Based Reinforcement Learning Adaptation

## Motivation
Model-based reinforcement learning suffers from a fundamental inefficiency: world models and policies are typically trained separately, leading to representation mismatch and slow adaptation to new tasks. Recent work identifies this objective mismatch as a root cause of performance degradation. Inspired by neuroscience findings that motor and sensory cortices share predictive representations, we hypothesize that unifying world model and policy learning through a shared encoder can dramatically accelerate online adaptation—a critical capability for deploying RL in data-constrained real-world settings.

## Main Idea
We propose Bidirectional Predictive Gradients (BPG), a shared dynamics encoder architecture where both world model prediction loss and policy optimization gradients flow through a common latent space. The key mechanism is threefold: (1) a transformer-based encoder produces unified representations for both components, (2) bidirectional gradient flow creates aligned optimization signals, and (3) PCGrad-style projection prevents gradient conflicts during joint training.

We will evaluate BPG against DreamerV3 and TD-MPC2 across 15+ continuous control tasks (DMC, Meta-World, CARLA), measuring interactions to reach 90% optimal performance. We predict 3-5x faster adaptation with 50% lower policy-world mismatch (KL divergence), while maintaining ≥95% final performance. Falsification occurs if speedup falls below 2x. Success would establish shared latent dynamics as a principled approach for sample-efficient decision making with generative world models.