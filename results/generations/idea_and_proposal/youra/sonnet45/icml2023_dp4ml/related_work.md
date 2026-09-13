## Related Work

**Related Papers**

1. **Title**: Natural gradient works efficiently in learning (Amari, 1998)
   - **Authors**: Shun-ichi Amari
   - **Summary**: Proved Fisher information matrix is the unique Riemannian metric invariant to parameter reparameterization and showed natural gradient follows steepest descent in Riemannian geometry, demonstrating convergence advantages on simple examples (online learning, multi-layer perceptrons).
   - **Year**: 1998

2. **Title**: Information Geometry and Its Applications (Amari, 2016)
   - **Authors**: Shun-ichi Amari
   - **Summary**: Comprehensive treatment of dually-flat manifolds in information geometry, covering Legendre duality (primal potential ↔ dual potential), Bregman divergences as canonical distances on dually-flat spaces, and exponential families as archetypal dually-flat manifolds.
   - **Year**: 2016

3. **Title**: Optimizing neural networks with Kronecker-factored approximate curvature (Martens & Grosse, 2015)
   - **Authors**: James Martens, Roger Grosse
   - **Summary**: Introduced efficient Fisher matrix approximation via Kronecker products (F_l ≈ A_l ⊗ G_l), reducing complexity from O(p²) to O(p) for computing natural gradient. Achieved ~25% iteration reduction vs. SGD on ImageNet ResNet-50 by exploiting layer-wise independence and Kronecker structure.
   - **Year**: 2015

4. **Title**: On leave-one-out conditional mutual information for generalization (Rammal et al., 2022)
   - **Authors**: Myriam Rammal, Alessandro Achille, Aditya Golatkar, Suhas Diggavi, Stefano Soatto
   - **Summary**: Developed information-theoretic generalization bounds based on leave-one-out conditional mutual information (LOO-CMI), connecting information measures to loss-landscape geometry and showing empirically that LOO-CMI correlates with test performance.
   - **Year**: 2022

5. **Title**: ManifoldFormer: Geometric deep learning for neural dynamics on Riemannian manifolds (Fu et al., 2025)
   - **Authors**: Y. Fu, L. He, Q. Chen
   - **Summary**: Developed Riemannian VAE for embedding neural signal data (EEG) on manifolds with geodesic-aware attention mechanisms that respect manifold structure, demonstrating practical application of geometric methods to neural systems.
   - **Year**: 2025

6. **Title**: Shampoo: Preconditioned stochastic tensor optimization (Gupta et al., 2018)
   - **Authors**: Vineet Gupta, Tomer Koren, Yoram Singer
   - **Summary**: Introduced layer-wise preconditioning using Kronecker products (P_l = A_l^(-1/4) ⊗ G_l^(-1/4)), using 4th root for better conditioning. Differs from K-FAC by not explicitly targeting Fisher matrix, with comparable or better empirical results on some tasks.
   - **Year**: 2018

7. **Title**: Adam: A method for stochastic optimization (Kingma & Ba, 2015)
   - **Authors**: Diederik P. Kingma, Jimmy Ba
   - **Summary**: Introduced adaptive learning rates per parameter using first and second moments of gradients (momentum m_t and variance v_t), becoming the most widely used optimizer in deep learning with fast per-iteration computation but potentially requiring more iterations than second-order methods.
   - **Year**: 2015

8. **Title**: Computational optimal transport (Peyré & Cuturi, 2019)
   - **Authors**: Gabriel Peyré, Marco Cuturi
   - **Summary**: Comprehensive treatment of optimal transport theory and algorithms, covering Kantorovich duality (primal transport plan ↔ dual potentials), Bregman divergences in OT, and efficient algorithms via dual optimization (e.g., Sinkhorn algorithm for entropy-regularized OT).
   - **Year**: 2019

9. **Title**: Deep learning via Hessian-free optimization (Martens, 2016)
   - **Authors**: James Martens
   - **Summary**: Demonstrated that second-order methods (Hessian-based, Fisher-based) can scale to large networks with appropriate approximations (block-diagonal, Kronecker-factored structures), reducing O(p²) to O(p) complexity with empirical validation on networks with millions of parameters.
   - **Year**: 2016

10. **Title**: Natural policy gradient (Kakade, 2001)
    - **Authors**: Not specified
    - **Summary**: Applied natural gradient methods to reinforcement learning policy optimization, using F^(-1) for Fisher information over action distributions π(a|s,θ).
    - **Year**: 2001

**Key Challenges**

1. **No Explicit Dual Coordinate Representation**: Natural gradient literature uses F^(-1) as a preconditioner but doesn't frame this as operating in a dual coordinate system η, lacking geometric interpretation beyond "apply inverse Fisher."

2. **No Adaptive Coordinate System Selection**: Existing methods either use primal coordinates (SGD, Adam) or dual coordinates (K-FAC, natural gradient) but not both adaptively, missing the opportunity to combine efficiency of primal (cheap) with effectiveness of dual (curvature-aware).

3. **Limited Information Geometry in Deep Learning**: Information geometry is well-developed but mostly applied to simple models (exponential families, shallow networks) with no systematic application of dually-flat manifolds to modern deep networks.

4. **Incomplete Understanding of When Natural Gradients Help**: While empirical observations show natural gradients help in ill-conditioned problems, there is no formal characterization connecting local geometry (curvature) to natural gradient advantage.

5. **K-FAC Approximation Quality**: K-FAC assumes layer-wise independence and Kronecker factorization, which can be violated in architectures with strong inter-layer coupling (residual connections in ResNets/DenseNets) or tensor/graph operations.

6. **Computational Intractability of Exact Fisher**: Computing exact Fisher information matrix requires O(p²) operations, which is intractable for deep networks, necessitating approximations that may be too coarse for meaningful dual coordinates.

7. **Hyperparameter Sensitivity**: Adaptive switching methods require tuning threshold τ and mixing weight λ, with risk that poor tuning degrades performance and may not generalize across architectures/tasks.

8. **Memory Overhead**: Storing both primal θ and dual η representations increases memory by ~2x vs. SGD, potentially restricting applicability to models where memory is not a bottleneck.

9. **Incremental Benefit Uncertainty**: Methods may provide only modest improvement over K-FAC alone (5-20% iteration reduction), raising questions about effort-to-benefit ratio for practitioners.

10. **Gap Between Theory and Practice**: Exact dually-flat structure is guaranteed for exponential families with tractable partition functions but neural networks are not exact exponential families, requiring empirical validation of the local dually-flat assumption in deep learning settings.
