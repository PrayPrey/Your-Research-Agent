## Related Work

**Related Papers**
1. **Title**: Shaping manifolds in equivariant recurrent neural networks (arXiv:2511.04802)
   - **Authors**: Di Bernardo et al.
   - **Summary**: Demonstrates that group Fourier transform reduces equivariant RNNs to analyzable low-rank form, enabling complete characterization of attractor manifolds.
   - **Year**: 2025

2. **Title**: Toroidal topology of population activity in grid cells (DOI: 10.1038/s41586-021-04268-7)
   - **Authors**: Gardner et al.
   - **Summary**: Uses topological data analysis to reveal toroidal manifold structure in grid cell population activity, showing this structure is invariant across environments and brain states.
   - **Year**: 2021

3. **Title**: Geometric deep learning and equivariant neural networks (DOI: 10.1007/s10462-023-10502-7)
   - **Authors**: Gerken et al.
   - **Summary**: Establishes how Wigner matrices, spherical harmonics, and Clebsch-Gordan coefficients enable SO(3) equivariant neural network analysis.
   - **Year**: 2021

4. **Title**: A Spectral Theory of Neural Prediction and Alignment (arXiv:2309.12821)
   - **Authors**: Canatar et al.
   - **Summary**: Develops spectral decomposition methods that reveal geometrical interpretation of neural prediction error.
   - **Year**: 2023

5. **Title**: Latent Functional Maps: a spectral framework for representation alignment (NeurIPS 2024)
   - **Authors**: Fumero et al.
   - **Summary**: Proposes using spectral geometry to enable representation alignment via functional maps based on general Laplacian eigenfunctions.
   - **Year**: 2024

6. **Title**: The intrinsic attractor manifold and population dynamics
   - **Authors**: Chaudhuri et al.
   - **Summary**: Demonstrates that ring attractor dynamics are preserved across waking and sleep states in head direction circuits, providing biological validation for SO(2) symmetry.
   - **Year**: 2019

7. **Title**: e3nn library
   - **Authors**: Not specified
   - **Summary**: Software library providing implementation for E(3)-equivariant operations and group Fourier transform.
   - **Year**: Not specified

8. **Title**: Giotto-TDA library
   - **Authors**: Not specified
   - **Summary**: Software library providing implementation for persistent homology and topological data analysis methods.
   - **Year**: Not specified

**Key Challenges**
1. **Symmetry-Adaptive Comparison**: Existing spectral methods for neural prediction and alignment are not symmetry-adaptive, limiting their ability to leverage known or discovered symmetry structures in neural representations.

2. **General vs. Symmetry-Specific Spectral Methods**: Current approaches like Latent Functional Maps focus on general Laplacian eigenfunctions rather than symmetry group-specific decompositions, potentially missing structure that could be captured through group-theoretic analysis.

3. **Bridging Theory and Biological Validation**: While theoretical frameworks exist for equivariant neural networks and biological evidence supports specific symmetry structures (e.g., toroidal manifolds in grid cells, ring attractors in head direction circuits), methods for systematically discovering and validating symmetries across neural systems remain underdeveloped.
