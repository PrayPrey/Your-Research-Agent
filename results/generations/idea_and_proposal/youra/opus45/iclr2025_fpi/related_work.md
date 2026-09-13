## Related Work

**Related Papers**
1. **Title**: Scalable Equilibrium Sampling with Sequential Boltzmann Generators (Semantic Scholar ID: 3be60571c2befc478b37f2a0d902a8a277023423)
   - **Authors**: Tan, Bose, Lin, Klein, Bronstein, Tong
   - **Summary**: Demonstrates that combining Sequential Monte Carlo (SMC) with Langevin dynamics achieves state-of-the-art performance on peptide sampling tasks, serving as the primary comparison baseline for Boltzmann generator methods.
   - **Year**: 2025

2. **Title**: Transferable Boltzmann Generators (Semantic Scholar ID: e023272ec3eabf4473f42b17f76d961b81e3e6f0)
   - **Authors**: Klein, Noé
   - **Summary**: Shows that flow matching enables zero-shot transfer capabilities in Boltzmann generators, validating the effectiveness of flow-based approaches for molecular sampling.
   - **Year**: 2024

3. **Title**: Wavelet Conditional Renormalization Group (Semantic Scholar ID: baf4c8f51a362ea11909700beb6c8746d6b51283)
   - **Authors**: Marchand, Ozawa, Biroli, Mallat
   - **Summary**: Introduces hierarchical factorization techniques that avoid critical slowing down in sampling, providing theoretical inspiration for multiscale approaches.
   - **Year**: 2022

4. **Title**: Iterative Multiscale Molecular Dynamics (Semantic Scholar ID: a828ba27fc264bbc84d183cde43563dacf7eff03)
   - **Authors**: Do, Gnanakaran
   - **Summary**: Demonstrates that iterating between coarse-grained and all-atom representations can capture protein folding dynamics, validating hierarchical approaches for molecular simulation.
   - **Year**: 2025

**Key Challenges**
1. **Limited System Size**: Current Boltzmann generators are limited to systems with fewer than 100 atoms, restricting their applicability to larger biomolecular systems.
2. **Lack of Hierarchical-Flow Integration**: No existing method combines hierarchical factorization with flow matching for molecular sampling, leaving a methodological gap.
3. **Computational Prohibitiveness**: Protein conformational sampling remains computationally prohibitive for practical drug discovery applications, limiting the translational impact of current methods.
