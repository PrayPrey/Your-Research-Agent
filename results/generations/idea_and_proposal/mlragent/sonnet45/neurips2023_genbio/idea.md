# Title
Multi-Scale Geometric Diffusion Models for RNA Structure-Function Co-Design

# Motivation
RNA therapeutics (mRNA vaccines, siRNA, aptamers) have shown immense promise, yet rational RNA design remains challenging due to the complex relationship between sequence, secondary/tertiary structure, and function. Unlike proteins where structure prediction has advanced dramatically, RNA design lacks robust generative models that simultaneously optimize sequence, structure, and functional properties across multiple scales. This gap limits our ability to design stable, functional RNA molecules for therapeutic applications.

# Main Idea
Develop a hierarchical geometric diffusion model that generates RNA molecules through multi-scale co-design:

1. **Architecture**: Implement a cascaded diffusion process operating on three levels: (a) secondary structure topology (base-pairing graph), (b) 3D geometric coordinates (backbone/base positions), and (c) sequence assignment, with cross-attention mechanisms enabling information flow between scales.

2. **Training**: Use existing RNA structures from PDB/RNA-puzzles, incorporating physics-based energy terms and experimental stability data as conditioning signals.

3. **Controllable generation**: Enable constraint specification including binding affinity targets, thermodynamic stability thresholds, immunogenicity profiles, and delivery requirements.

4. **Validation pipeline**: Integrate wet-lab-in-the-loop optimization using high-throughput screening data to iteratively refine model predictions.

**Expected Impact**: This approach would enable de novo design of functional RNAs with desired properties, accelerating development of RNA-based therapeutics and biosensors while advancing our understanding of RNA structure-function relationships.