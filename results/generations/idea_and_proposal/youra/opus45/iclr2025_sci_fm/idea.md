# MetroFM-Bench: A Metrological Framework for Fair Cross-Domain Foundation Model Evaluation

## Motivation
Current foundation model (FM) benchmarks like HELM and lm-eval enable within-domain comparisons but fail to provide fair cross-domain evaluation. Raw accuracy rankings conflate model capability with domain-specific advantages, making it impossible to assess true generalization. This gap hinders open science efforts to transparently compare FMs across diverse applications (vision, language, medicine). We need principled methods—inspired by physical metrology—to establish traceable, comparable measurements across domains.

## Main Idea
We propose MetroFM-Bench, applying metrological principles to FM evaluation through two key innovations: (1) **Bridge Datasets**—domain-invariant reference datasets spanning domain boundaries that serve as "transfer standards," and (2) **Domain-Canonical Task Templates (DCTTs)**—abstract task specifications ensuring semantic equivalence across instantiations (validated via expert agreement κ>0.7).

The core mechanism introduces **Transfer Efficiency (T_eff)**: measuring performance ratio normalized by data requirements across domains. Our hypothesis predicts T_eff rankings will significantly diverge from raw accuracy rankings (Spearman ρ<0.7), with ≥30% of FM pairs showing rank reversals—revealing which models truly generalize versus those optimized for specific domains.

We will evaluate 10+ FMs across 4 domains using 3 bridge datasets per domain pair. Expected outcomes include actionable guidance for FM selection based on generalization capability rather than domain fit, advancing transparent, reproducible FM evaluation for the open science community.