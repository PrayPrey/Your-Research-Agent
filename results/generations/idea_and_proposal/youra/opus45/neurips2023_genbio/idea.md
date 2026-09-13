# Research Idea

## Title
UniGenBench: A Hierarchical Three-Tier Benchmark Framework for Cross-Modal Evaluation of Generative Biomolecule Models

## Motivation
Generative AI has enabled breakthrough designs of proteins, small molecules, and antibodies, yet evaluating these models remains fragmented. Current benchmarks (ProteinBench, MolGenBench) operate in isolation with inconsistent metrics, making cross-modal comparison unreliable and hindering systematic progress. Researchers cannot determine whether a protein generator outperforms a molecule generator on comparable quality dimensions, nor can they reproduce rankings across labs. This fragmentation wastes resources and obscures genuine advances.

## Main Idea
We propose UniGenBench, a hierarchical benchmark separating evaluation into three tiers: (1) structural validity (modality-specific rules), (2) quality metrics (normalized cross-modal scores), and (3) functional verification (experimental correlation). The core hypothesis is that this hierarchical separation, combined with bootstrap uncertainty quantification, will achieve cross-modal ranking consistency (Kendall's tau > 0.7) and inter-lab reproducibility (CV < 10%)—significantly outperforming flat evaluation approaches.

The methodology involves benchmarking 30+ generative models across proteins (PDB), molecules (ChEMBL), and antibodies (SAbDab) using standardized metric implementations. Ablation studies will isolate each tier's contribution to consistency. Key predictions include improved failure mode diagnosis (>90% precision) and identification of ranking instabilities through uncertainty estimation. Success would establish the first unified evaluation standard for generative biology, accelerating reliable model development across modalities.