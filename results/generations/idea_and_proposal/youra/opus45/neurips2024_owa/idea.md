# Research Idea

## Title
Adaptive Orthogonal Subspace Transformers for Compositional Generalization in Open-World Agents

## Motivation
Open-world AI agents must simultaneously reason (e.g., answering questions, dialogue) and make decisions (e.g., planning, control) across novel task combinations. Current unified transformer architectures suffer from representational interference—reasoning and decision-making compete for the same embedding space, causing catastrophic forgetting and poor compositional transfer. Neuroscience evidence shows the prefrontal cortex uses orthogonal neural codes to prevent memory interference, yet this principle remains unexploited in agent architectures. The key gap: how can we enable controlled separation of reasoning and decision representations while preserving their necessary interactions?

## Main Idea
We propose Adaptive Orthogonal Subspace Transformers (A-OST), which separate reasoning and decision representations into geometrically-orthogonal subspaces using SVD-based projection layers with tunable constraint strength (λ). The mechanism operates in three steps: (1) learned token classification assigns reasoning/decision roles, (2) orthogonal projection routes tokens to separate subspaces, and (3) gated cross-subspace attention enables controlled knowledge sharing without reintroducing interference. We predict A-OST will achieve >60% zero-shot accuracy on novel task combinations (vs. ~30% baseline), reduce representation interference (cosine similarity <0.3), and require 40% fewer adaptation samples. Validation uses Dynamic GameBench with mid-episode rule changes. This establishes geometric constraints as a principled approach for building compositionally generalizable open-world agents.