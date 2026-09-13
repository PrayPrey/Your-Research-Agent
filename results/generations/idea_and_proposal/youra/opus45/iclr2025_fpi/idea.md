# Research Idea

## Title
Hierarchical Flow Matching for Scalable Boltzmann Sampling of Large Proteins

## Motivation
Sampling from Boltzmann distributions is fundamental for understanding protein thermodynamics, yet current methods face critical scalability barriers. State-of-the-art approaches like Sequential Boltzmann Generators achieve reasonable efficiency only on small peptides (~100 atoms), while proteins of biological interest contain thousands of atoms. This scalability gap prevents accurate free energy estimation and conformational sampling for therapeutically relevant proteins. The core challenge is that sampling complexity grows prohibitively with system dimensionality, causing existing single-scale methods to fail on large biomolecules.

## Main Idea
We propose a hierarchical factorization approach that decomposes Boltzmann sampling into P(backbone) × P(all-atom|backbone), trained via SE(3)-equivariant flow matching with importance reweighting for exactness correction. The key insight is that backbone coordinates capture slow collective motions while side-chain distributions conditioned on backbone are simpler—reducing effective dimensionality without sacrificing thermodynamic accuracy.

**Methodology:** Train two-stage flows on MD trajectories, measuring Effective Sample Size (ESS) per GPU-hour across protein sizes (1,000-10,000 atoms) against Sequential BG baselines.

**Expected Outcomes:** Achieve >5% ESS/GPU-hour for 5,000-atom systems where baselines fail (<1%), with free energy accuracy within 1 kT. This would enable practical Boltzmann sampling for drug discovery and protein engineering applications previously computationally intractable.