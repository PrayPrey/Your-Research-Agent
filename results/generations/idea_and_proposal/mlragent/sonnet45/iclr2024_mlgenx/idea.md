# Title
**Causal Perturbation Graphs: Learning Interpretable Gene Regulatory Networks through Multi-Modal Perturbation Integration**

# Motivation
Current perturbation biology approaches struggle to integrate diverse experimental readouts (RNA-seq, proteomics, imaging) into coherent causal models of gene regulation. This limits our ability to identify robust drug targets and predict off-target effects. Most existing methods either focus on single modalities or use black-box models that lack biological interpretability, hindering clinical translation and mechanistic understanding of disease pathways.

# Main Idea
We propose a framework combining graph neural networks with causal representation learning to construct interpretable gene regulatory networks from multi-modal perturbation data. The approach has three key components:

1. **Multi-modal encoder**: Learn joint representations from perturbation screens across RNA-seq, protein abundance, and cellular imaging using contrastive learning to align modality-specific features.

2. **Causal graph discovery**: Apply differentiable structure learning with sparsity constraints to infer directed regulatory relationships, incorporating known biological priors (pathway databases, protein-protein interactions) as soft constraints.

3. **Counterfactual validation**: Generate testable hypotheses through in-silico perturbation predictions, with uncertainty quantification to prioritize high-confidence edges for experimental validation.

Expected outcomes include: (1) more accurate target identification by revealing causal mechanisms, (2) reduced experimental costs through active learning-guided perturbation selection, and (3) interpretable models enabling mechanistic insights into disease biology. This bridges ML innovation with practical drug discovery needs.