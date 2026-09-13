# Research Idea: Hierarchical Memory-Augmented Reasoning for Adaptive Decision-Making in Open Worlds

## Title
Continual Abstraction Learning: A Hierarchical Memory Framework for Unified Reasoning and Decision-Making in Open-World Environments

## Motivation
Current AI agents struggle to transfer reasoning capabilities to novel decision-making contexts in open worlds. The key bottleneck is that reasoning (language-based inference) and decision-making (action selection) remain disconnected, preventing agents from building reusable abstractions. Humans excel by maintaining a hierarchical memory of task-agnostic concepts that bridge these modalities. We need unified architectures that can simultaneously abstract over linguistic patterns and behavioral strategies while continuously adapting to new scenarios with minimal supervision.

## Main Idea
We propose a **Hierarchical Abstraction Memory (HAM)** framework where agents maintain three interconnected memory tiers:
1. **Episodic layer**: Stores raw experience from reasoning (QA dialogues) and decision-making (action trajectories)
2. **Procedural layer**: Extracts cross-modal skills (e.g., "information gathering before acting") via self-supervised contrastive learning between language reasoning chains and action sequences
3. **Semantic layer**: Distills abstract principles applicable to both modalities

A meta-controller learns when to retrieve, compose, or refine abstractions based on environmental novelty signals. The system uses intrinsic motivation to identify knowledge gaps, triggering targeted exploration. We evaluate on benchmarks requiring joint reasoning-planning (e.g., interactive household tasks, strategic games) measuring zero-shot transfer to unseen scenarios, sample efficiency, and abstraction reusability across domains.