# Title
Causal Mediation Analysis of Representational Alignment: Quantifying How Neural Network Representations Drive Value-Aligned Behaviors

# Motivation
Current alignment research shows strong correlations between representational similarity and behavioral outcomes (e.g., truthfulness, safety), but correlation doesn't prove causation. We cannot determine whether representational changes actually *cause* aligned behaviors or are merely epiphenomenal. This gap prevents principled intervention design—researchers use trial-and-error fine-tuning without knowing which representational features to target. We need a rigorous causal framework to quantify how much of alignment effects flow through representational pathways versus other mechanisms, enabling efficient, targeted interventions.

# Main Idea
We formalize representational features (geometric structure via CKA, attention patterns, sparse activations) as **causal mediators** between alignment interventions (RLHF, DPO) and value-aligned behaviors (truthfulness, fairness, safety). Using mediation analysis from epidemiology, we decompose total alignment effects into Natural Indirect Effects (NIE—flowing through representations) and Natural Direct Effects (NDE—bypassing representations). **Core hypothesis**: NIE/Total Effect ≥60%, proving representations causally mediate alignment.

**Methodology**: (1) Randomized experiments varying RLHF intensity; (2) LASSO-based mediator selection from high-dimensional activations; (3) Representation engineering validation—intervening *only* on representations to verify predicted behavioral changes; (4) Sensitivity analysis quantifying robustness to unmeasured confounders.

**Expected impact**: 2× intervention efficiency by targeting high-leverage mediators; transparent causal claims with assumption bounds; predictive modeling of behavioral outcomes from representational shifts before deployment.