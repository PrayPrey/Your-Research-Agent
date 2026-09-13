# Title
Hierarchical Grounding Framework: Bridging MFM High-Level Reasoning with Low-Level Embodied Control via Learned Action Primitives

# Motivation
Current Multi-modal Foundation Models (MFMs) excel at high-level reasoning and planning but struggle with fine-grained, low-level control required for embodied agents. The "reasoning-to-action gap" causes MFMs to generate abstract commands (e.g., "grasp the cup") that fail to translate into precise robot movements in dynamic environments. This disconnect limits practical deployment of MFM-powered embodied AI, as sophisticated reasoning cannot be grounded into executable, adaptive behaviors.

# Main Idea
We propose a hierarchical framework with three components:

1. **MFM Planner**: Generates high-level task plans and subgoals using vision-language models (e.g., GPT-4V)
2. **Action Primitive Library**: A learned repertoire of reusable, parameterized skills (e.g., "reach," "grasp," "place") trained via reinforcement learning in simulation and real-world data
3. **Grounding Module**: A lightweight vision-language-action (VLA) model that translates MFM outputs into action primitive sequences with appropriate parameters, conditioned on real-time sensory feedback

The grounding module is trained using paired data: MFM high-level descriptions and corresponding low-level action trajectories. We evaluate on manipulation and navigation benchmarks, measuring task success rates and execution efficiency.

**Expected Impact**: This framework enables scalable deployment of MFM-powered agents by decomposing complex tasks while maintaining adaptability, advancing practical embodied AI applications in robotics and autonomous systems.