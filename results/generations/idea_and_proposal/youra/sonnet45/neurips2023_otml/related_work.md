## Related Work

**Related Papers**

1. **Title**: An Optimal Transport Approach to Causal Inference (Di Marino & Gerolin 2019)
   - **Authors**: Di Marino, Gerolin
   - **Summary**: Provides foundational theory on Sinkhorn convergence for entropic regularized optimal transport, establishing convergence guarantees that underpin the computational feasibility of regularized OT methods.
   - **Year**: 2019

2. **Title**: Unbalanced Optimal Transport Complexity Analysis (Pham et al. 2020)
   - **Authors**: Pham et al.
   - **Summary**: Analyzes computational complexity of unbalanced Sinkhorn algorithm, demonstrating O(n²/ε) convergence rate with KL-divergence marginal relaxation without degradation from balanced case.
   - **Year**: 2020

3. **Title**: Entropic Multi-Marginal Optimal Transport (Beier et al. 2021)
   - **Authors**: Beier et al.
   - **Summary**: Extends unbalanced formulation to multi-marginal optimal transport setting, proving additivity of KL penalties and providing the baseline unconstrained Sinkhorn method for K-marginal problems.
   - **Year**: 2021

4. **Title**: Fourier-based Acceleration for Multi-Marginal Optimal Transport (Ba & Quellmalz 2022)
   - **Authors**: Ba, Quellmalz
   - **Summary**: Introduces FFT-based acceleration achieving O(KN) complexity for multi-marginal OT with special structure, providing inspiration for decomposition strategies in structured settings.
   - **Year**: 2022

5. **Title**: Hierarchical Decomposition for Multi-Marginal Optimal Transport (von Lindheim 2022)
   - **Authors**: von Lindheim
   - **Summary**: Validates decomposition approaches for multi-marginal OT problems, particularly focusing on tree-structured topologies and hierarchical solution methods.
   - **Year**: 2022

6. **Title**: Approximation Bounds for Constrained Optimal Transport with Entropic Regularization (Tang et al. 2024)
   - **Authors**: Tang et al.
   - **Summary**: Establishes critical theoretical result showing exponential error decay for constrained OT with convex constraints and entropic regularization, providing quality guarantees for topology-constrained formulations.
   - **Year**: 2024

7. **Title**: Progressive Optimal Transport (ProgOT) (Kassraie et al. 2024)
   - **Authors**: Kassraie et al.
   - **Summary**: Proposes progressive continuation methods achieving O(N) complexity through curriculum-based optimization, offering potential future acceleration strategy for the TAUMOT framework.
   - **Year**: 2024

8. **Title**: Sequential Martingale Optimal Transport in Finance (Engström et al. 2024)
   - **Authors**: Engström et al.
   - **Summary**: Applies sequential topology multi-marginal OT to financial modeling with martingale constraints, demonstrating that structured OT maintains quality comparable to unconstrained methods in real applications.
   - **Year**: 2024

9. **Title**: Star Topology Multi-Marginal OT for Robotic Task Assignment (Le Ny 2024)
   - **Authors**: Le Ny
   - **Summary**: Validates star topology multi-marginal optimal transport for robotics applications, showing practical scalability and near-optimal task assignment performance.
   - **Year**: 2024

10. **Title**: Graph-Structured Optimal Transport for Multi-Object Tracking (Wärnsäter et al. 2025)
    - **Authors**: Wärnsäter et al.
    - **Summary**: Applies graph-structured OT to tracking problems, maintaining tracking accuracy comparable to unconstrained methods while leveraging problem structure for efficiency.
    - **Year**: 2025

11. **Title**: Multi-Source Domain Adaptation with Optimal Transport (Montesuma 2024)
    - **Authors**: Montesuma
    - **Summary**: Applies multi-marginal OT to multi-source domain adaptation, demonstrating practical need for scalable K>10 methods in transfer learning applications.
    - **Year**: 2024

12. **Title**: Single-Cell Genomics with Optimal Transport (Bunne 2024)
    - **Authors**: Bunne
    - **Summary**: Uses multi-marginal OT for single-cell genomics trajectory inference across K>5 time points, highlighting computational bottlenecks with current methods.
    - **Year**: 2024

13. **Title**: POT: Python Optimal Transport Library
    - **Authors**: Not specified
    - **Summary**: Open-source Python library for optimal transport with 2,700+ GitHub stars, providing separate modules for unbalanced and multi-marginal OT but lacking combined implementation.
    - **Year**: Not specified

14. **Title**: LightUOT: Lightweight Unbalanced Optimal Transport (NeurIPS 2024)
    - **Authors**: Not specified
    - **Summary**: Recent practical implementation for large-scale unbalanced OT, validating real-world need for handling mass imbalances in optimal transport problems.
    - **Year**: 2024

15. **Title**: FUGW: Fused Unbalanced Gromov-Wasserstein
    - **Authors**: Not specified
    - **Summary**: GPU-accelerated implementation combining unbalanced formulation with Gromov-Wasserstein for structure-aware costs, particularly applied to brain imaging data.
    - **Year**: Not specified

**Key Challenges**

1. **Computational Complexity Explosion**: Multi-marginal OT suffers from exponential coupling space growth O(N^K), making problems with K>10 distributions and N>10,000 samples computationally intractable with unconstrained methods.

2. **Lack of Combined Unbalanced + Multi-Marginal Methods**: Existing methods treat unbalanced formulation and multi-marginal extensions separately, with no scalable implementation combining both properties for K>10 distributions.

3. **Topology-Awareness Gap**: Current multi-marginal OT methods ignore application-specific coupling topologies (star, tree, hierarchical) that could enable complexity reduction through structured decomposition.

4. **Approximation Quality Uncertainty**: While entropic regularization enables tractable computation, practical approximation error bounds for topology-constrained formulations were lacking prior to Tang et al. 2024.

5. **Scalability to Real Applications**: Multi-source domain adaptation (K>10 sources), single-cell genomics (K>5 time points), and federated learning (K>20 clients) require both unbalanced formulation (for imbalanced data) and computational efficiency not achieved by existing methods.

6. **Implementation Availability**: No open-source GPU-optimized implementation exists that combines topology-awareness, unbalanced formulation, and multi-marginal capabilities in a unified framework.
