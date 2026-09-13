# Title
**Hierarchical Perturbation Encoders: Learning Scale-Bridging Representations from Multi-Level Biological Interventions**

## Motivation
Current foundation models treat biological perturbations at single scales (gene knockouts OR drug treatments OR environmental changes) in isolation, missing critical cross-scale causality. A drug affects molecular pathways, which alter cellular states, which manifest as tissue-level phenotypes. Existing representations fail to capture these cascading effects, limiting our ability to predict organism-level outcomes from molecular interventions or reverse-engineer molecular targets from phenotypic observations—crucial for drug discovery and precision medicine.

## Main Idea
We propose learning hierarchical perturbation representations by training encoders on paired multi-scale intervention data. The methodology involves:

1. **Multi-scale perturbation graphs**: Construct knowledge graphs linking genetic, chemical, and environmental perturbations to their effects across molecular (transcriptomics, proteomics), cellular (morphology, single-cell states), and phenotypic (disease outcomes) scales.

2. **Hierarchical contrastive learning**: Train encoders to align perturbations causing similar effects at ANY scale while maintaining scale-specific structure through hierarchical triplet losses.

3. **Cross-scale transfer tasks**: Evaluate via novel benchmarks: predicting cellular responses from gene edits, inferring molecular mechanisms from phenotypes, and designing multi-target interventions.

**Expected outcomes**: Representations enabling zero-shot prediction of untested perturbations across scales, interpretable attention maps revealing causal pathways, and practical tools for rational drug design targeting multiple biological levels simultaneously.