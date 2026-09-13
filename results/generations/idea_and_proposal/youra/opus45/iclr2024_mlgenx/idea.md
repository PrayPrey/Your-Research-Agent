# Research Idea

## Title
HierarchicalGenomeFM: Bidirectional Cross-Scale Attention for Multi-Omics Foundation Models

## Motivation
Current genomic foundation models operate at single scales (DNA sequence, gene expression, or spatial transcriptomics), missing critical cross-scale biological dependencies. While DNA regulatory elements control gene expression, which determines spatial tissue organization, existing approaches combine these modalities through simple late fusion, failing to capture bidirectional information flow. This limits drug target identification and understanding of disease mechanisms—key bottlenecks in therapeutic development.

## Main Idea
We propose a 3-level hierarchical foundation model with sparse bidirectional cross-scale attention, inspired by visual cortex processing. Level 1 (Mamba/Hyena) processes DNA sequences at 100kb-1Mb resolution; Level 2 (Transformer) handles gene-level expression; Level 3 (ViT) captures spatial transcriptomics. The key innovation is sparse top-k attention (k=500) enabling both bottom-up feature extraction and top-down contextual modulation across scales.

**Methodology:** Train on Human Cell Atlas matched multi-scale data (~100M parameters) with multi-task objectives (sequence→expression, expression→spatial) plus hierarchical contrastive loss. Compare against ensemble baselines combining single-scale models.

**Expected Outcomes:** 15-25% improvement in cross-scale prediction accuracy (Spearman ρ), validated through ablation studies showing bidirectional attention contributes 5-15% of gains. This enables unified genomic representations for improved disease mechanism discovery and therapeutic target identification.