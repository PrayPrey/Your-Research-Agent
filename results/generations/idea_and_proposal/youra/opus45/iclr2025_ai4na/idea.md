# Research Idea

## Title
HiMamba-CL: Hierarchical Bidirectional Mamba with Contrastive Learning for Unified RNA Representation

## Motivation
Current RNA foundation models struggle to capture the multi-scale nature of RNA biology—from local sequence motifs (3-10nt) to secondary structure domains (50-200nt) to full transcript context. Existing approaches either use flat architectures that miss hierarchical patterns or focus on single modalities, limiting cross-task generalization. This gap hinders progress in RNA therapeutics, structure prediction, and functional annotation.

## Main Idea
We propose HiMamba-CL, combining hierarchical bidirectional Mamba layers with contrastive cross-modal alignment for RNA representation learning. The core mechanism operates through four causal steps: (1) stacked Mamba layers with 2x receptive field expansion capture progressively larger RNA patterns, (2) enabling multi-scale representations spanning motifs to global context, (3) contrastive learning with biological augmentations (orthologs, splice isoforms) aligns sequence and structure modalities, (4) producing modality-invariant embeddings that generalize across tasks.

We will train on >1M sequence-structure pairs from RNAcentral/Rfam, testing three architecture depths (2/4/6 layers) and modality configurations. Key predictions: ≥10% improvement in structure prediction (TM-score >0.72 vs. 0.65 baseline) and ≥15% better transfer efficiency. Falsification occurs if hierarchical processing shows ≤5% gain over flat Mamba. Success would establish a new paradigm for multimodal RNA foundation models with direct therapeutic applications.