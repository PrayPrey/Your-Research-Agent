## Related Work

**Related Papers**

1. **Title**: Atlas-based manifolds for geometric deep learning (Robinett 2025)
   - **Authors**: Robinett
   - **Summary**: Proposes atlas-based neural network architectures for learning manifold structures, providing the foundation for differentiable chart representations used in API-RNN.
   - **Year**: 2025

2. **Title**: Physics-Informed Neural Networks review (Plankovskyy 2025)
   - **Authors**: Plankovskyy
   - **Summary**: Comprehensive review of PINNs that identifies Gap 3 (physics-informed adaptive geometry discovery) as a fundamental limitation in current approaches.
   - **Year**: 2025

3. **Title**: Standard Physics-Informed Neural Networks baseline (Hamel 2022)
   - **Authors**: Hamel
   - **Summary**: Establishes the primary baseline PINN methodology used for comparison, with 38 citations, representing standard Euclidean PINN approaches.
   - **Year**: 2022

4. **Title**: Observable-augmented manifold learning for turbulent flow (Fukami & Taira 2025)
   - **Authors**: Fukami and Taira
   - **Summary**: Provides the turbulent flow benchmark dataset (2D cylinder wake flows at various Reynolds numbers) used for Tier 2 validation in API-RNN experiments.
   - **Year**: 2025

5. **Title**: Distance-Based Attention for Physics-Informed Neural Networks (DBA-PINN)
   - **Authors**: Not specified
   - **Summary**: Introduces hand-crafted geometric conditioning using distance-based attention mechanisms, serving as a strong baseline to test whether learned geometry beats engineered features.
   - **Year**: Not specified

6. **Title**: Geomstats: Riemannian geometry library
   - **Authors**: Not specified
   - **Summary**: Provides computational tools for Riemannian geometry operations including metric tensor computation, Riemann curvature tensor calculation, and geodesic computation used in API-RNN implementation.
   - **Year**: Not specified

7. **Title**: DeepXDE: Physics-informed neural network library
   - **Authors**: Not specified
   - **Summary**: Provides PINN baseline utilities and standard benchmark implementations for comparison with API-RNN, version 1.10.0 used in experiments.
   - **Year**: Not specified

**Key Challenges**

1. **Fixed Geometry Limitation**: Current PINNs require geometric structure to be specified a priori, preventing automatic discovery of physics-appropriate coordinate systems that could simplify physical laws.

2. **Generalization to Unseen Parameters**: Standard PINNs with Euclidean geometry show limited ability to generalize to unseen system parameters (e.g., different Reynolds numbers in turbulence), requiring retraining for new conditions.

3. **Bi-level Optimization Instability**: Jointly learning manifold geometry and physics-informed representations presents significant training stability challenges, with risks of manifold collapse to Euclidean space or optimization divergence.

4. **Computational Overhead**: Adaptive geometry discovery methods introduce significant computational costs (3-6× standard PINN) due to chart network computations, metric tensor calculations, and Riemannian derivative operations.

5. **Hyperparameter Sensitivity**: Geometry learning requires careful tuning of multiple loss weights (physics residual, boundary conditions, Jacobian regularization, curvature bounds) with high sensitivity to these hyperparameters.

6. **Validation of Learned Geometry**: Ensuring that discovered manifold structures are physically meaningful and not arbitrary latent representations requires rigorous geometric consistency metrics (Riemann curvature, chart transition smoothness, volume preservation).
