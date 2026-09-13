## Related Work

**Related Papers**
1. **Title**: Score-Based Generative Modeling through Stochastic Differential Equations (arXiv:2011.13456)
   - **Authors**: Song, Sohl-Dickstein, Kingma, Kumar, Ermon, Poole
   - **Summary**: Established a unified SDE framework for diffusion models with predictor-corrector sampling, providing the foundational score-based approach for generative modeling.
   - **Year**: 2020

2. **Title**: Variational Diffusion Models (arXiv:2107.00630)
   - **Authors**: Kingma, Salimans, Poole, Ho
   - **Summary**: Demonstrated that the variational lower bound simplifies to signal-to-noise ratio and proved the equivalence between score matching and ELBO maximization.
   - **Year**: 2021

3. **Title**: Adjoint Matching: Fine-tuning Flow and Diffusion with Memoryless SOC (arXiv:2409.08861)
   - **Authors**: Domingo-Enrich, Drozdzal, Karrer, Chen
   - **Summary**: Proved that specific noise schedules are required for stochastic optimal control formulation, establishing precedent for control-theoretic approaches to diffusion models.
   - **Year**: 2024

4. **Title**: Standard Denoising Score Matching (DSM)
   - **Authors**: Not specified
   - **Summary**: Serves as the baseline training objective for diffusion model experiments, against which HJB-derived objectives can be compared.
   - **Year**: Not specified

5. **Title**: ELBO Training (Variational Perspective)
   - **Authors**: Not specified
   - **Summary**: Provides an alternative probabilistic training objective for diffusion models, expected to emerge as a special case within the HJB framework.
   - **Year**: Not specified

6. **Title**: HuggingFace Diffusers Library
   - **Authors**: Not specified
   - **Summary**: Standard implementation library for diffusion models that uses empirically-tuned objectives without control-theoretic derivation.
   - **Year**: Not specified

7. **Title**: Diffuser (Planning)
   - **Authors**: Not specified
   - **Summary**: Applies diffusion models for trajectory planning but does not establish connections to HJB training objective derivation.
   - **Year**: Not specified

**Key Challenges**
1. **Lack of Control-Theoretic Foundation**: Standard diffusion model implementations rely on empirically-tuned objectives without rigorous derivation from control theory principles such as the Hamilton-Jacobi-Bellman equation.

2. **Disconnect Between Planning and Training**: Existing work using diffusion for trajectory planning (e.g., Diffuser) does not connect the planning formulation back to principled training objective derivation.

3. **Fragmented Theoretical Perspectives**: While score matching and variational (ELBO) perspectives exist separately, a unified framework that derives both as special cases from a common control-theoretic foundation is missing.

4. **Noise Schedule Constraints**: Recent work demonstrates that specific noise schedules are required for stochastic optimal control formulations, indicating constraints that need to be addressed in control-theoretic approaches.
