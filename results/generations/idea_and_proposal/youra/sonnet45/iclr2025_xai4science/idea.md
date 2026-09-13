# Title
SynthEx: Synthetic Oracle Verification Framework for Ante-Hoc Explainable AI in Scientific Discovery

# Motivation
Machine learning models increasingly support scientific discovery in climate, healthcare, and materials science, but their explanations often lack verified faithfulness—we cannot confirm they reflect true causal reasoning. Current verification relies on expensive expert validation or unvalidated post-hoc comparisons. This creates a critical barrier: scientists cannot trust model explanations for knowledge discovery. We need scalable, objective methods to verify that ante-hoc interpretable models generate faithful explanations before deployment in high-stakes scientific applications.

# Main Idea
We propose SynthEx, a two-stage verification framework that tests explanation faithfulness using synthetic tasks with constructible ground-truth "explanation oracles." **Core hypothesis**: Ante-hoc models achieving high alignment with synthetic oracles (composite score ≥0.80 across structural, semantic, and causal metrics) will demonstrate significantly higher expert-validated faithfulness on real tasks (≥0.70 vs. ~0.50 baseline). 

**Methodology**: Stage 1 screens models against 60-90 domain-informed synthetic tasks embedding known causal mechanisms. Stage 2 validates that synthetic scores predict real-world faithfulness across climate attribution, materials prediction, and healthcare diagnostics.

**Innovation**: First adaptation of systems engineering test oracles to XAI, enabling automated, quantitative faithfulness measurement while reducing expert annotation burden by ~70%. Success requires demonstrating synthetic-real transfer correlation (r≥0.6) across all domains, establishing a scalable pathway for trustworthy scientific AI.