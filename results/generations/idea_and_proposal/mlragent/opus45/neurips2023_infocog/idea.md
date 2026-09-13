# Title: Mutual Information Bottleneck for Emergent Communication in Human-AI Cooperative Tasks

## Motivation
A fundamental challenge in human-AI cooperation is developing artificial agents that communicate efficiently and interpretably with humans. Current emergent communication approaches often produce codes that are optimal for agent-agent interaction but opaque to humans. Information-theoretic principles, particularly the Information Bottleneck (IB), offer a principled framework for balancing compression and task-relevance, but existing applications ignore the asymmetric capacity constraints between human and artificial communicators. Understanding how to shape AI communication to align with human cognitive bandwidth limitations is crucial for effective collaboration.

## Main Idea
I propose a **Cognitive-Constrained Information Bottleneck (CCIB)** framework for training AI agents that communicate with humans in cooperative tasks. The key innovation is incorporating empirically-measured human channel capacity constraints directly into the IB objective. Specifically:

1. **Methodology**: Augment the standard IB objective with a human-inspired capacity penalty estimated from cognitive science literature (e.g., working memory limits, attention bandwidth). Train agents using variational bounds where the compression term is weighted by task-specific human processing costs.

2. **Validation**: Conduct human-subject experiments comparing CCIB-trained agents against standard emergent communication baselines on referential games and collaborative navigation tasks, measuring both task performance and human interpretability ratings.

3. **Expected Outcomes**: Agents that spontaneously develop human-aligned communication protocols—more compositional, less redundant, and matching human semantic categories.

This bridges information theory, cognitive constraints, and practical AI alignment.