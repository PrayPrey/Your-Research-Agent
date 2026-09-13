## Related Work

**Related Papers**
1. **Title**: Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges
   - **Authors**: M. Bronstein, J. Bruna, T. Cohen, P. Veličković
   - **Summary**: Provides a unified geometric framework demonstrating how symmetries constrain neural network architectures through weight sharing patterns.
   - **Year**: 2021

2. **Title**: The principles behind equivariant neural networks for physics and chemistry
   - **Authors**: R. Kondor
   - **Summary**: Explains why the Clebsch-Gordan transform appears in equivariant architectures and defines the algebraic structure that can be exploited for theoretical analysis.
   - **Year**: 2025

3. **Title**: Training Certifiably Robust Neural Networks with Efficient Local Lipschitz Bounds
   - **Authors**: Y. Huang, H. Zhang, Y. Shi, J.Z. Kolter, A. Anandkumar
   - **Summary**: Demonstrates that local Lipschitz bounds provide tighter robustness certificates than global bounds by considering activation patterns in local neighborhoods.
   - **Year**: 2021

4. **Title**: Compositional Estimation of Lipschitz Constants for Deep Neural Networks (arXiv:2404.04375)
   - **Authors**: Y. Xu, S. Sivaranjani
   - **Summary**: Introduces a decomposition approach that reduces the computational complexity of Lipschitz constant estimation, providing foundations for block-diagonal exploitation.
   - **Year**: 2024

5. **Title**: Training Graph Neural Networks Subject to a Tight Lipschitz Constraint
   - **Authors**: S. Juvină, A. Neacsu, et al.
   - **Summary**: Develops methods to enforce Lipschitz constraints during training of graph neural networks, rather than deriving bounds from architectural structure.
   - **Year**: 2024

6. **Title**: Mathematical Foundations of GDL
   - **Authors**: Not specified
   - **Summary**: Formalizes concepts in geometric deep learning but does not derive robustness certificates from the formalized framework.
   - **Year**: 2025

**Key Challenges**
1. **No framework connecting equivariance to robustness bounds**: Existing certified robustness methods treat neural network architectures as black boxes and do not exploit equivariance structure to derive tighter bounds.

2. **Lack of formal guarantees in geometric deep learning**: While foundational frameworks like Bronstein et al. (2021) provide unified perspectives on geometric deep learning, they do not include formal robustness proofs or certificates.

3. **Loose generic spectral norm bounds**: Standard approaches using products of layer spectral norms do not exploit equivariance structure, resulting in bounds that are significantly looser than what structured analysis could provide.

4. **Gap between constraint enforcement and bound derivation**: Current work on Lipschitz-constrained networks focuses on enforcing constraints during training rather than deriving inherent bounds from architectural symmetries.
