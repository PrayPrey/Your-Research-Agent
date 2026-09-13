# Title: Multi-Scale Geometric Foundation Model for RNA Tertiary Structure Prediction

## Motivation
RNA tertiary structure prediction remains a critical bottleneck in understanding RNA function and designing RNA-based therapeutics. Unlike proteins, RNAs exhibit highly flexible, hierarchical folding with complex base-pairing patterns and non-canonical interactions. Current methods either focus on secondary structure or struggle with the multi-scale nature of RNA folding—from nucleotide-level interactions to global 3D architecture. A unified foundation model that captures these hierarchical geometric relationships could dramatically advance RNA structure prediction and enable rational RNA drug design.

## Main Idea
We propose **RNAGeom-FM**, a multi-scale geometric foundation model that jointly learns RNA representations across sequence, secondary structure, and tertiary structure levels. The approach uses:

1. **Hierarchical SE(3)-equivariant architecture**: A novel network that processes RNA at three scales—nucleotide graphs, secondary structure motifs (stems, loops), and coarse-grained 3D representations—with message passing between scales.

2. **Multi-task pre-training**: Self-supervised objectives including masked nucleotide prediction, secondary structure denoising, and 3D coordinate reconstruction from partial structures using available PDB data and cryo-EM densities.

3. **Physics-informed constraints**: Integration of base-pairing energetics and backbone geometry priors to ensure chemically valid predictions.

Expected outcomes include state-of-the-art RNA 3D structure prediction and transferable representations for downstream tasks like RNA-ligand binding prediction, directly impacting RNA therapeutic development.