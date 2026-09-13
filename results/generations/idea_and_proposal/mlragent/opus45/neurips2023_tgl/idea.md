# Title: Causal Discovery in Temporal Graphs via Interventional Contrastive Learning

## Motivation
Current temporal graph learning methods excel at capturing correlations but struggle to distinguish causal relationships from spurious associations that evolve over time. This limitation is critical in applications like disease modeling, fraud detection, and financial forecasting, where understanding *why* events occur—not just predicting them—is essential for intervention design. Existing causal discovery methods for static graphs fail to account for time-varying confounders and delayed causal effects, while temporal graph neural networks lack mechanisms to identify causal edges from observational data alone.

## Main Idea
We propose **Temporal Causal Graph Networks (TCGN)**, a framework that integrates interventional reasoning into temporal graph representation learning. The key innovation is a *temporal interventional contrastive learning* objective that simulates soft interventions on node features and edge formations across time steps, then contrasts representations to identify invariant causal structures versus spurious temporal correlations.

Specifically, we: (1) design a temporal intervention module that generates counterfactual graph sequences by perturbing potential cause nodes while preserving causal mechanisms; (2) develop a time-aware causal attention mechanism that assigns higher weights to edges exhibiting consistent causal influence across multiple time windows; (3) introduce a causal consistency regularizer enforcing that learned representations remain stable under distribution shifts.

Expected outcomes include improved interpretability, robustness to temporal distribution shift, and actionable insights for downstream intervention tasks in healthcare and finance applications.