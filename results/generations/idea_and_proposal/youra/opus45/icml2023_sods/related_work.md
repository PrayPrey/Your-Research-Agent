## Related Work

**Related Papers**
1. **Title**: Categorical Reparameterization with Gumbel-Softmax (arXiv:1611.01144)
   - **Authors**: Jang, Gu, Poole
   - **Summary**: Introduces Gumbel-Softmax as a differentiable approximation to categorical sampling, demonstrating convergence properties as temperature τ→0.
   - **Year**: 2016

2. **Title**: Flow Network based Generative Models for Non-Iterative Diverse Candidate Generation (arXiv:2106.04399)
   - **Authors**: Bengio et al.
   - **Summary**: Proposes GFlowNet, which enables proportional sampling via flow matching and serves as a foundational approach for diverse discrete generation.
   - **Year**: 2021

3. **Title**: Stein Variational Gradient Descent (NeurIPS 2016)
   - **Authors**: Liu & Wang
   - **Summary**: Introduces a particle-based variational inference method using the Stein operator, enabling gradient-based sampling for probabilistic inference.
   - **Year**: 2016

4. **Title**: Discrete Langevin Sampler via Wasserstein Gradient Flow
   - **Authors**: Sun et al.
   - **Summary**: Provides a principled extension of Langevin dynamics to discrete spaces through Wasserstein gradient flow formulation.
   - **Year**: 2022

5. **Title**: DIMES
   - **Authors**: Qiu et al.
   - **Summary**: A meta-solver approach for combinatorial optimization problems.
   - **Year**: 2022

6. **Title**: Generalized Gumbel-Softmax Gradient Estimator
   - **Authors**: Joo et al.
   - **Summary**: Demonstrates that Gumbel-Softmax can be extended beyond categorical distributions to generic discrete distributions.
   - **Year**: 2023

7. **Title**: Improving Discrete Optimisation Via Decoupled ST-GS
   - **Authors**: Not specified
   - **Summary**: Demonstrates gradient fidelity improvements in discrete optimization through temperature decoupling techniques.
   - **Year**: 2025 (ICLR)

8. **Title**: MetaBBO Survey
   - **Authors**: Not specified
   - **Summary**: Shows that adaptive method selection improves black-box optimization performance across diverse problem types.
   - **Year**: 2024

**Key Challenges**
1. **Limited Generalization of Gumbel-Softmax**: Standard Gumbel-Softmax is restricted to categorical distributions, requiring extensions to handle generic discrete distributions.
2. **Gradient Fidelity in Discrete Optimization**: Temperature coupling in straight-through Gumbel-Softmax estimators leads to gradient fidelity issues that require decoupling approaches.
3. **Adaptive Method Selection**: No single discrete optimization method dominates across all problem types, necessitating adaptive or meta-learning approaches for method selection.
4. **Discrete Space Sampling**: Extending continuous sampling methods like Langevin dynamics to discrete spaces requires principled theoretical frameworks.
