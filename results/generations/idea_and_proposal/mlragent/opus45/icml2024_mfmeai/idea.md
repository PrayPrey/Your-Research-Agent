# Research Idea

## Title
Hierarchical Skill Abstraction Framework for Bridging Multi-modal Foundation Models with Low-level Robot Control

## Motivation
Current Multi-modal Foundation Models (MFMs) excel at high-level reasoning and planning but struggle to translate abstract decisions into precise, real-time motor commands required for embodied agents. This semantic-to-motor gap leads to brittle robot behaviors, especially in dynamic environments requiring reactive adjustments. Existing approaches either fine-tune entire MFMs (computationally expensive) or use simple action primitives (limiting expressiveness). A principled framework that bridges MFM's cognitive capabilities with low-level control remains an open challenge critical for practical deployment.

## Main Idea
We propose **SkillBridge**, a hierarchical framework featuring learnable "skill tokens" that serve as an intermediate representation between MFM outputs and low-level controllers. The approach involves:

1. **Skill Token Library**: A learned embedding space where each token encodes a parameterized motor skill (e.g., "grasp-fragile," "push-heavy")
2. **MFM Skill Decoder**: Lightweight adapter layers that map MFM's multimodal reasoning to skill token sequences with continuous parameters
3. **Diffusion-based Skill Executor**: A diffusion policy conditioned on skill tokens that generates smooth, reactive trajectories

Training uses a combination of simulated demonstrations and real-world teleoperation data with contrastive learning to align MFM semantics with skill tokens. We expect significant improvements in task success rates for manipulation tasks requiring both semantic understanding and precise control, enabling more practical MFM-powered robots.