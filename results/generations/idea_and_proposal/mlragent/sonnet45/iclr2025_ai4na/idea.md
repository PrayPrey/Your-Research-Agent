# Title
**Multimodal Foundation Models for RNA Structure-Function Prediction via Contrastive Learning**

## Motivation
Current RNA structure prediction models treat sequence, secondary structure, and tertiary structure as separate problems, failing to capture the intrinsic relationships between RNA structural hierarchies and their biological functions. A unified multimodal foundation model could learn rich representations that bridge the gap between RNA sequence, structure at multiple scales, and functional annotations, enabling more accurate predictions and novel RNA design capabilities for therapeutic applications.

## Main Idea
We propose developing a multimodal foundation model that jointly learns from:
1) RNA sequences
2) Secondary structure representations (dot-bracket notation, base-pairing matrices)
3) 3D tertiary structures (geometric graphs)
4) Functional annotations (binding sites, catalytic activity, cellular localization)

The methodology employs:
- **Contrastive pre-training** to align representations across modalities (e.g., matching sequence embeddings with their corresponding structural and functional embeddings)
- **Hierarchical encoders** that capture dependencies from sequence → secondary → tertiary structure
- **Cross-modal attention mechanisms** to enable structure-informed sequence understanding and vice versa

Expected outcomes include improved RNA tertiary structure prediction, zero-shot function prediction for novel RNAs, and a unified embedding space for rational RNA therapeutic design. This approach would enable researchers to query RNAs by structure to find similar functions, or design sequences with desired structural and functional properties simultaneously.