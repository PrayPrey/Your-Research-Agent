## Related Work

**Related Papers**
1. **Title**: Fast ε-free Inference of Simulation Models with Bayesian Conditional Density Estimation
   - **Authors**: Papamakarios et al.
   - **Summary**: Introduced Sequential Neural Posterior Estimation (SNPE) with amortized inference using normalizing flows for simulation-based inference.
   - **Year**: 2016

2. **Title**: Automatic Posterior Transformation for Likelihood-Free Inference
   - **Authors**: Greenberg et al.
   - **Summary**: Developed SNPE-C with proposal-based sampling for improved efficiency in likelihood-free inference.
   - **Year**: 2019

3. **Title**: The frontier of simulation-based inference
   - **Authors**: Cranmer et al.
   - **Summary**: Comprehensive survey of SBI methods and applications in science, identifying sample efficiency as a major bottleneck for expensive simulators.
   - **Year**: 2020

4. **Title**: Active Sequential Posterior Estimation for Simulation-Based Inference
   - **Authors**: Griesemer et al.
   - **Summary**: Introduced active SBI using expected information gain acquisition, achieving 5-20× sample reduction compared to passive methods.
   - **Year**: 2024

5. **Title**: Effortless Bayesian Deep Learning through Transformers
   - **Authors**: Vetter et al.
   - **Summary**: Proposed tabular foundation models for SBI where transfer learning reduces sample count requirements.
   - **Year**: 2025

6. **Title**: Physics-Informed Neural Networks: A Deep Learning Framework for Solving Forward and Inverse Problems Involving Nonlinear PDEs
   - **Authors**: Raissi et al.
   - **Summary**: Developed PINNs framework that enforces PDE residuals as soft constraints in loss functions for solving forward and inverse PDE problems.
   - **Year**: 2019

7. **Title**: Understanding and Mitigating Gradient Flow Pathologies in Physics-Informed Neural Networks
   - **Authors**: Wang et al.
   - **Summary**: Identified PINN training challenges and proposed adaptive weighting strategies for physics constraint optimization.
   - **Year**: 2021

8. **Title**: Uncertainty Quantification for Forward and Inverse Problems of PDEs via Latent Global Evolution
   - **Authors**: Wu et al.
   - **Summary**: Introduced LE-PDE-UQ framework for physics-informed surrogates with uncertainty propagation using passive sampling.
   - **Year**: 2024

9. **Title**: Sequential Bayesian Experimental Design for Implicit Models via Mutual Information
   - **Authors**: Foster et al.
   - **Summary**: Developed mutual information acquisition methods for experimental design in high dimensions, achieving 10-100× reduction in experimental design.
   - **Year**: 2022

10. **Title**: Fourier Neural Operator for Parametric Partial Differential Equations
    - **Authors**: Li et al.
    - **Summary**: Introduced FNO for operator learning in Fourier space achieving <1% error on PDE benchmarks with mesh-independence properties.
    - **Year**: 2021

11. **Title**: Learning Generalizable Neural Operators for Inverse Problems (B2B⁻¹)
    - **Authors**: Thorpe et al.
    - **Summary**: Developed framework for ill-posed inverse PDEs with uncertainty quantification using neural operators.
    - **Year**: 2025

12. **Title**: Fast Stokes Flow Simulations for Geodynamic Inverse Problems via Reduced Order Modeling
    - **Authors**: Ortega-Gelabert et al.
    - **Summary**: Demonstrated that PDE constraints reduce geodynamic inverse problem search space through adaptive surrogate modeling for expensive Stokes flow simulations.
    - **Year**: 2020

13. **Title**: Multi-Fidelity Gaussian Process Regression for Computer Experiments
    - **Authors**: Kennedy & O'Hagan
    - **Summary**: Introduced methods to combine cheap low-fidelity and expensive high-fidelity models for computational efficiency.
    - **Year**: 2000

14. **Title**: Learning Coefficient Functions for Reaction-Diffusion Equations (LE-PDE-UQ reference)
    - **Authors**: Not specified
    - **Summary**: Physics-informed surrogate approach with uncertainty quantification for PDE parameter inference.
    - **Year**: 2024

15. **Title**: Active Learning for Bayesian Optimization (BALD)
    - **Authors**: Houlsby (referenced) and Gal
    - **Summary**: Uncertainty-based acquisition strategies using Monte Carlo estimation for active learning applications.
    - **Year**: 2011 (Houlsby), 2017 (Gal)

**Key Challenges**
1. **Sample Inefficiency for Expensive Simulators**: Standard SBI methods require 10⁴ simulations making them intractable for expensive PDE-governed simulators (CFD, FEM, plasma physics) that take minutes to hours per run.

2. **Physics Knowledge Underutilization**: Active SBI methods ignore domain-specific physics constraints, wasting samples exploring physically infeasible parameter regions.

3. **Passive Sampling Limitations**: Physics-informed surrogate methods use physics constraints but employ passive random sampling, still requiring many samples to adequately cover feasible parameter space.

4. **Integration Barrier**: SBI community focuses on general inference avoiding domain-specific physics, while PDE surrogate community focuses on forward solvers with less emphasis on inverse/SBI problems.

5. **Technical Complexity**: Encoding PDE constraints in likelihood-free inference requires differentiable physics residuals, which presents implementation challenges.

6. **Computational Cost Hierarchy**: Acquisition overhead must remain negligible compared to simulation cost, requiring careful balance between sample efficiency and computational overhead.

7. **Scalability with Dimensionality**: Methods suffer from curse of dimensionality as parameter dimension increases, with sample complexity scaling poorly for high-dimensional problems.

8. **Quality-Efficiency Trade-off**: Sample reduction methods often degrade posterior accuracy, requiring careful validation that efficiency gains don't sacrifice inference quality.

9. **Domain-Specific Engineering**: Each new simulator requires custom PDE residual implementation and surrogate architecture tuning, limiting accessibility to researchers without deep ML expertise.

10. **Surrogate Approximation Quality**: Neural surrogates must achieve sufficient accuracy during cold start phase to enable reliable acquisition decisions, requiring careful initialization protocols.
