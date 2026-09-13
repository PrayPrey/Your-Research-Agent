# Research Idea: Curriculum-Aware Intrinsic Motivation via Meta-Learned Difficulty Estimation

## Motivation
Current intrinsic motivation methods often struggle with premature specialization or inefficient exploration, spending excessive time on either too-easy or impossibly-hard tasks. Humans naturally seek challenges at the "edge of competence" – tasks that are neither trivially easy nor frustratingly difficult. This Goldilocks zone maximizes learning efficiency, yet most IM approaches lack explicit mechanisms to identify and maintain this sweet spot dynamically across diverse open-ended environments.

## Main Idea
We propose a meta-learning framework that learns to estimate task difficulty relative to the agent's current competence, enabling adaptive curriculum generation. The system consists of:

1. **Meta-learned difficulty predictor**: A neural network trained across multiple tasks to predict expected learning progress based on current policy parameters and task features
2. **Competence-calibrated intrinsic reward**: Rewards that peak for medium-difficulty tasks, incorporating uncertainty estimates about difficulty predictions
3. **Dynamic goal buffer**: Automatically archives and samples goals near the agent's expanding competence frontier

The difficulty predictor is meta-trained using episodes from various environments, learning to generalize difficulty assessment across domains. This enables rapid adaptation to new environments without costly online calibration. Expected outcomes include improved sample efficiency, better skill coverage, and enhanced generalization. This addresses IMOL's core challenge of autonomous, lifelong learning by ensuring agents consistently engage with optimally challenging experiences.