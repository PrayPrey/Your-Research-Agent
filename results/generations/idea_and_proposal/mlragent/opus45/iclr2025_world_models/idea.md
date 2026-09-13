# Research Idea

## Title
Causal State-Space Models for Compositional World Understanding

## Motivation
Current world models excel at pattern recognition but struggle with compositional generalization—understanding novel combinations of known concepts (e.g., predicting how a never-seen object behaves under familiar physics). This limitation stems from entangling causal mechanisms with spurious correlations during training. While state-space models (SSMs) offer efficient long-range temporal modeling, they lack explicit causal structure, leading to brittle predictions in out-of-distribution scenarios. Enabling world models to discover and leverage modular causal mechanisms would dramatically improve their ability to generalize across diverse environments and support robust planning.

## Main Idea
We propose **Causal SSM (C-SSM)**, which augments state-space models with a learned causal graph over latent state dimensions. The key innovation is a two-phase training approach: (1) **Causal Discovery Phase**: Using interventional data from environment interactions, we learn a sparse directed acyclic graph (DAG) that captures causal dependencies between state variables via a differentiable structure learning objective. (2) **Modular Dynamics Phase**: The SSM's state transition matrices are factorized according to the discovered DAG, enabling independent mechanism updates.

We evaluate on compositional generalization benchmarks (e.g., PHYRE, CausalWorld) measuring prediction accuracy on novel object-property combinations. Expected outcomes include improved zero-shot transfer and interpretable state representations. This approach bridges causality research with scalable sequence modeling, offering a principled path toward world models that truly "understand" rather than merely memorize environment dynamics.