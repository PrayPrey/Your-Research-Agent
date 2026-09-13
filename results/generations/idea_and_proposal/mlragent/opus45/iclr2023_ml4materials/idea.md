# Title: Periodic Equivariant Diffusion Models for Crystal Structure Generation with Compositional Constraints

## Motivation
Generating novel crystal structures remains a fundamental challenge in materials discovery. Unlike molecules, crystals require periodic boundary conditions and must satisfy complex compositional constraints (e.g., charge neutrality, stoichiometry). Existing generative models often produce physically implausible structures or fail to respect periodicity properly. Current diffusion models for crystals either treat lattice parameters and atomic positions separately or ignore critical domain constraints, leading to unstable or unsynthesizable predictions. A unified framework that inherently respects crystallographic symmetry and chemical feasibility would dramatically accelerate the discovery of functional materials.

## Main Idea
We propose **CrystalFlow**, a periodic SE(3)-equivariant diffusion model that jointly generates lattice parameters, atomic positions, and species while enforcing compositional constraints. The key innovations are:

1. **Fractional coordinate diffusion**: Perform diffusion in fractional coordinates with a wrapped Gaussian process that naturally respects periodic boundaries, eliminating boundary artifacts.

2. **Constraint-guided sampling**: Incorporate a differentiable constraint module during reverse diffusion that enforces charge balance and target stoichiometry without post-hoc rejection.

3. **Hierarchical lattice-atom coupling**: Learn correlated noise schedules between lattice deformation and atomic positions to maintain physical density throughout generation.

We will train on the Materials Project dataset and evaluate on metrics including validity rate, uniqueness, formation energy distribution, and synthesizability scores. Expected outcomes include >90% valid structures and discovery of novel stable compositions for energy storage applications.