# Research Idea

## Title
Modular Adapter Composition for Continual Compositional Learning: Bridging Modularity and Temporal Generalization

## Motivation
While modular approaches like adapters show promise for compositional learning, their behavior in continual learning settings remains poorly understood. Current methods face catastrophic forgetting when adapting to evolving distributions, and it's unclear whether modular structures that enable compositional generalization in static settings maintain this property over time. This gap is critical for deploying foundation models in real-world scenarios where data distributions shift continuously.

## Main Idea
We propose **Compositional Adapter Banks (CAB)**, a framework that maintains a dynamically growing library of lightweight adapters, each capturing atomic skills or concepts. The key innovations are:

1. **Skill Decomposition**: Automatically decompose new tasks into combinations of existing adapters plus minimal new modules, using gradient-based attribution to identify reusable components.

2. **Composition Routing**: Train a meta-router that learns to compose adapter subsets for novel task combinations, enabling zero-shot generalization to unseen compositions.

3. **Selective Consolidation**: Periodically merge highly co-activated adapters to prevent memory explosion while preserving compositional boundaries through structured pruning.

We will evaluate on continual visual reasoning benchmarks (CLEVR variants with distribution shifts) and text-based semantic parsing with evolving schemas. Expected outcomes include improved forward transfer through composition and reduced backward interference compared to monolithic fine-tuning, providing empirical evidence on whether structural modularity translates to temporal compositional generalization.