# Title: Hierarchical Contrastive Learning for Multi-Scale Biological Representations

## Motivation
Current biological foundation models typically operate at a single scale (e.g., molecular, cellular, or tissue level), missing crucial cross-scale dependencies that govern biological function. For instance, genetic variants affect protein structure, which influences cellular phenotype, ultimately manifesting as organism-level traits. Existing approaches struggle to capture these hierarchical relationships, limiting their utility for understanding complex biological processes and predicting perturbation effects across scales.

## Main Idea
I propose a hierarchical contrastive learning framework that explicitly models cross-scale biological relationships through scale-bridging representations. The method introduces:

1. **Scale-specific encoders** for each biological level (genomic sequences, protein structures, single-cell transcriptomics, cell morphology) trained with modality-appropriate architectures.

2. **Cross-scale contrastive objectives** that align representations between adjacent scales using known biological mappings (e.g., gene-to-protein, genotype-to-phenotype) as positive pairs, with hard negatives sampled from functionally distinct entities.

3. **Scale-conditioned prediction heads** that enable both upward (molecule→cell→tissue) and downward (phenotype→molecular mechanism) inference.

The framework will be evaluated on multi-scale perturbation prediction tasks using JUMP-CP data, assessing whether genetic perturbation effects can be predicted at the cellular imaging level. Expected outcomes include improved generalization on cross-scale tasks and interpretable representations that reveal mechanistic links between biological scales—a critical step toward virtual cell simulators.