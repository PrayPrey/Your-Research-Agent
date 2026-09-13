## Related Work

**Related Papers**
1. **Title**: Neural Posterior Estimation with Differentiable Simulators (arXiv:2207.05636)
   - **Authors**: Zeghal, Lanusse, Boucaud, Remy, Aubourg
   - **Summary**: Demonstrates that gradient information from differentiable simulators improves Neural Posterior Estimation sample efficiency by 2x when using fewer than 100 simulations.
   - **Year**: 2022

2. **Title**: Predictive Coding Networks and Inference Learning: Tutorial and Survey (arXiv:2407.04117)
   - **Authors**: van Zwol, Jefferson, van den Broek
   - **Summary**: Establishes that Predictive Coding Networks are mathematically equivalent to variational inference and provides a comprehensive framework for understanding PCN-based approaches.
   - **Year**: 2024

3. **Title**: Divide-and-Conquer Predictive Coding: a structured Bayesian inference algorithm
   - **Authors**: Sennesh, Wu, Salvatori
   - **Summary**: Provides mathematical foundations for structured inference in Predictive Coding Networks through the DCPC algorithm.
   - **Year**: 2024

4. **Title**: JPC: Flexible Inference for Predictive Coding Networks in JAX (arXiv:2412.03676)
   - **Authors**: Innocenti et al.
   - **Summary**: Demonstrates that 2nd-order ODE solvers achieve faster PCN settling dynamics and provides a practical JAX implementation for PCN inference.
   - **Year**: 2024

5. **Title**: Active SNPE
   - **Authors**: Griesemer
   - **Summary**: Improves sample efficiency in simulation-based inference through active learning strategies, though without utilizing simulator gradients.
   - **Year**: 2024

6. **Title**: sbi toolkit (Standard NPE)
   - **Authors**: Not specified
   - **Summary**: Provides a black-box baseline implementation for Neural Posterior Estimation in simulation-based inference.
   - **Year**: Not specified

**Key Challenges**
1. **SBI-Differentiable Simulator Gap**: Existing approaches to improving sample efficiency in simulation-based inference, such as Active SNPE, do not leverage gradient information from differentiable simulators despite its demonstrated benefits.

2. **PCN-External Gradient Integration Gap**: No prior work has combined Predictive Coding Networks with external simulator gradients for inference, leaving unexplored the potential synergy between PCN dynamics and gradient-informed learning.
