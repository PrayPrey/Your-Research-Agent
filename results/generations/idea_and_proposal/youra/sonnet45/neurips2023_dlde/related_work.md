## Related Work

**Related Papers**
1. **Title**: Characterizing possible failure modes in physics-informed neural networks (Krishnapriyan et al., 2021)
   - **Authors**: Krishnapriyan et al.
   - **Summary**: Established that PINN failures stem from ill-conditioned loss landscapes, not neural network expressivity. Proposed curriculum learning as a solution which requires problem-specific curriculum design.
   - **Year**: 2021

2. **Title**: Multi-level physics informed deep learning for solving partial differential equations (He et al., 2024)
   - **Authors**: He et al.
   - **Summary**: Demonstrated that multi-level decomposition showing separating physics terms improves training, interpreted as implicit conditioning balancing. Requires manual decomposition.
   - **Year**: 2024

3. **Title**: Stochastic Galerkin Method and Hierarchical Preconditioning for PDE-constrained Optimization (Li et al., 2025)
   - **Authors**: Li et al.
   - **Summary**: Core preconditioning theory demonstrating hierarchical preconditioners reduce condition numbers for PDE-constrained optimization, providing direct analogy to PINN loss balancing. Designed for fixed linear systems.
   - **Year**: 2025

4. **Title**: Optimal Preconditioning for Online Quadratic Cone Programming (Kamath et al., 2025)
   - **Authors**: Kamath et al.
   - **Summary**: Validates feasibility of online adaptive preconditioning without matrix refactorization, supporting real-time conditioning monitoring approach. Focuses on convex quadratic cone programming.
   - **Year**: 2025

5. **Title**: Synchronization of chaotic oscillator systems based on adaptive synergetic control theory (Saadi et al., 2024)
   - **Authors**: Saadi et al.
   - **Summary**: Lyapunov-stable adaptive gain laws for uncertain systems, adapted for gradient-based weight updates with stability guarantees in continuous dynamics.
   - **Year**: 2024

6. **Title**: A Data-Driven Model for Power Loss Estimation Based on Multi-Objective Optimization (Li et al., 2024)
   - **Authors**: Li et al.
   - **Summary**: Multi-objective perspective for balancing competing losses at different scales, framing PINN training as multi-objective problem. Uses Pareto-optimal hyperparameter selection offline.
   - **Year**: 2024

7. **Title**: GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multi-task Networks (Chen et al., 2018)
   - **Authors**: Chen et al.
   - **Summary**: Balances multi-task gradients by normalizing gradient magnitudes without conditioning analysis. Uses gradient norms as heuristic without theoretical convergence guarantees.
   - **Year**: 2018

8. **Title**: Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics (Kendall et al., 2018)
   - **Authors**: Kendall et al.
   - **Summary**: Learns task uncertainties to weight losses treating loss scales as learned parameters. Heuristic approach without conditioning theory grounding.
   - **Year**: 2018

9. **Title**: Curriculum regularization for PINNs (Krishnapriyan et al., 2021)
   - **Authors**: Krishnapriyan et al.
   - **Summary**: Sequential easy-to-hard training improves PINN convergence, achieving 1-2 orders of magnitude error reduction. Requires manual problem-specific curriculum design.
   - **Year**: 2021

10. **Title**: Residual-Based Attention PINNs (jdtoscano94 repo)
   - **Authors**: Not specified
   - **Summary**: Attention mechanism for dynamic loss reweighting based on residuals using empirical data-driven approach without theoretical grounding.
   - **Year**: Not specified

11. **Title**: Optimizing Neural Networks with Kronecker-factored Approximate Curvature (K-FAC) (Martens & Grosse, 2015)
   - **Authors**: Martens & Grosse
   - **Summary**: Uses approximate Hessian (Fisher information) for preconditioning neural network optimization to accelerate training by preconditioning entire loss.
   - **Year**: 2015

12. **Title**: AdaHessian: An Adaptive Second Order Optimizer for Machine Learning (Yao et al., 2020)
   - **Authors**: Yao et al.
   - **Summary**: Uses Hessian diagonal for adaptive learning rates in single-objective optimization as per-parameter adaptive learning rate method.
   - **Year**: 2020

13. **Title**: Shampoo: Preconditioned Stochastic Tensor Optimization (Gupta et al., 2018)
   - **Authors**: Gupta et al.
   - **Summary**: Block-wise preconditioning for large-scale tensor optimization focusing on parameter-space preconditioning for per-parameter optimization.
   - **Year**: 2018

14. **Title**: Fourier Neural Operator for Parametric Partial Differential Equations (Li et al., 2021)
   - **Authors**: Li et al.
   - **Summary**: Learns operator mapping instead of solving per-instance, avoiding PINN training difficulties by changing problem formulation. Requires large datasets of PDE solutions.
   - **Year**: 2021

15. **Title**: Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators (Lu et al., 2021)
   - **Authors**: Lu et al.
   - **Summary**: Learns operators via branch-trunk networks using data-driven approach requiring datasets, contrasting with physics-driven PINN methods.
   - **Year**: 2021

**Key Challenges**
1. **PINN Training Failures on Ill-Conditioned PDEs**: Physics-informed neural networks fail on convection-dominated and stiff PDEs due to ill-conditioned loss landscapes, not from lack of network expressivity.

2. **Manual Hyperparameter Tuning Burden**: Existing PINN methods require manual tuning of 3+ loss weights (often 10+ for complex PDEs), with 10-100 trials per PDE instance and expert domain knowledge.

3. **Lack of Theoretical Foundation for Loss Balancing**: Current multi-task learning approaches (GradNorm, uncertainty weighting) use heuristics without rigorous conditioning theory or stability guarantees.

4. **Non-Stationary Loss Landscapes**: PINN loss Hessians change as network weights update during training, making online conditioning estimation from stationary linear system preconditioning theory challenging.

5. **Gap Between Linear Preconditioning Theory and Nonlinear Optimization**: Classical preconditioning theory designed for fixed linear systems needs extension to nonlinear, non-stationary neural network optimization contexts.

6. **Computational Overhead of Second-Order Methods**: Hessian-based methods for neural networks can be computationally expensive, with memory constraints for very large networks (>10^7 parameters).

7. **Problem-Specific Curriculum Design**: Curriculum learning approaches for PINNs require manual easy-to-hard sequence design with domain knowledge, limiting automation and generalization.

8. **Lack of Convergence Guarantees**: Existing adaptive loss balancing methods lack formal convergence rate characterization and stability analysis for non-convex neural network optimization.
