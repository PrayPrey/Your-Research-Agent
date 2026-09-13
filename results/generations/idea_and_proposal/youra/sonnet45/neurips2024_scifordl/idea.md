# Title
Universal Computational Motifs: Cross-Architecture Mechanistic Interpretability via Graph Neural Networks

# Motivation
Current mechanistic interpretability methods are architecture-specific, requiring manual re-engineering for each new model family (transformers, diffusion models, state space models). This creates a bottleneck: understanding one model takes weeks of expert effort and doesn't transfer to others. Existing automated tools like ACDC work only within single architectures, while cross-architecture methods like HAGD achieve only 67% similarity. We need automated discovery tools that recognize *functional* computational patterns across structurally different implementations—analogous to how neuroscience identifies conserved synaptic motifs across brain regions.

# Main Idea
We hypothesize that deep learning architectures share conserved **computational motifs** (information convergence, multiplicative gating, residual bypass) that manifest as recognizable graph patterns despite structural differences. Our approach: (1) construct a universal motif library from existing mechanistic analyses, (2) train graph neural networks to detect these motifs as functional graph patterns rather than architecture-specific circuits, (3) enable zero-shot transfer across architectures. 

A pilot study will first validate ≥70% motif conservation across GPT-2, DiT, and Mamba. If confirmed, GNN-based detection should achieve F1≥0.80 on-architecture (matching ACDC) and F1≥0.60 cross-architecture (exceeding HAGD's 67%), while reducing analysis time from 8 weeks to <1 hour per model. This shifts interpretability from circuit-tracing to motif-recognition, providing a unified framework for mechanistic discovery.