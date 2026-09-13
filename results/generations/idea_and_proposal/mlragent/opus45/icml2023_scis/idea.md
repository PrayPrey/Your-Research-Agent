# Title: Adaptive Spurious Correlation Discovery via Gradient-Based Feature Attribution Disagreement

## Motivation
A critical challenge in addressing spurious correlations is that we often don't know they exist until models fail in deployment. Current discovery methods typically require prior knowledge of potential spurious features or access to group labels, which are rarely available in practice. We need automated methods that can proactively surface hidden spurious correlations before deployment failures occur, enabling researchers and practitioners to diagnose vulnerabilities without extensive domain expertise or labeled subgroups.

## Main Idea
We propose a self-supervised framework for discovering spurious correlations by analyzing disagreements in feature attributions across differently-initialized model ensembles. The key insight is that spurious features, being statistically predictive but causally irrelevant, exhibit higher attribution variance across models compared to robust features.

Our method: (1) trains an ensemble of models with diverse initializations and augmentation strategies on the same dataset; (2) computes gradient-based attributions (e.g., Integrated Gradients) for each model; (3) identifies features with high cross-model attribution variance as candidate spurious correlations; (4) clusters these features to generate interpretable "spurious hypotheses" for human verification.

Expected outcomes include an automated diagnostic tool that flags potential shortcuts without group annotations, validated on standard benchmarks (Waterbirds, CelebA, MultiNLI) and real medical imaging datasets. This bridges discovery and mitigation, enabling targeted data collection or robust training interventions before deployment failures occur.