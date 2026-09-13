## Related Work

**Related Papers**

1. **Title**: The General Problem of the Stability of Motion
   - **Authors**: Lyapunov, A. M.
   - **Summary**: Introduced Lyapunov functions V(x) satisfying V̇ < 0 as certificate for asymptotic stability of dynamical systems, providing the classical foundation for all Lyapunov-based control methods.
   - **Year**: 1892

2. **Title**: Stochastic Stability and Control
   - **Authors**: Kushner, H. J.
   - **Summary**: Extended Lyapunov theory to stochastic differential equations with probabilistic stability guarantees, justifying probabilistic formulation E[V̇] < -αE[V] for diffusion sampling.
   - **Year**: 1967

3. **Title**: Denoising Diffusion Probabilistic Models (DDPM)
   - **Authors**: Ho, J., Jain, A., Abbeel, P.
   - **Summary**: Established diffusion models as powerful generative framework via forward noise process and reverse denoising, providing foundation for score network architecture and training objectives.
   - **Year**: 2020

4. **Title**: Score-Based Generative Modeling through Stochastic Differential Equations
   - **Authors**: Song, Y., Sohl-Dickstein, J., Kingma, D. P., et al.
   - **Summary**: Unified diffusion models as continuous-time SDEs with score function s_θ(x,t) = ∇log p_t(x), providing SDE formulation enabling Lyapunov analysis.
   - **Year**: 2021

5. **Title**: Safe and Stable Control via Lyapunov-Guided Diffusion Models (S²Diff)
   - **Authors**: Cheng, X., Tang, X., Yang, Y.
   - **Summary**: Applies Lyapunov guidance at inference time by modifying score function, achieving ~80% Lyapunov satisfaction with iterative guidance requiring slower sampling than proposed training-time approach.
   - **Year**: 2025

6. **Title**: Contractive Diffusion Policies: Robust Action Diffusion via Contractive Score-Based Sampling
   - **Authors**: Abyaneh, A., Morissette, C., et al.
   - **Summary**: Uses contraction theory (alternative to Lyapunov) to ensure robustness against solver errors in diffusion sampling with exponential convergence guarantees.
   - **Year**: 2026

7. **Title**: Control Barrier Functions: Theory and Applications
   - **Authors**: Ames, A. D., Grizzle, J. W., Tabuada, P.
   - **Summary**: Introduced Control Barrier Functions (CBF) for safety, often used with Control Lyapunov Functions (CLF) for stability in RL using quadratic programming for control synthesis.
   - **Year**: 2014

8. **Title**: The Lyapunov Neural Network: Adaptive Stability Certification for Safe Learning
   - **Authors**: Richards, S. M., Berkenkamp, F., Krause, A.
   - **Summary**: Learn Lyapunov function V_θ(x) via neural network alongside policy for safe RL, providing architectural foundation for neural Lyapunov parameterization.
   - **Year**: 2018

9. **Title**: Planning with Diffusion for Flexible Behavior Synthesis (Diffuser)
   - **Authors**: Janner, M., Du, Y., Tenenbaum, J., Levine, S.
   - **Summary**: First application of diffusion models to trajectory planning in RL, generating full trajectories via denoising and validating diffusion-based control approach.
   - **Year**: 2022

10. **Title**: Score Matching Diffusion Based Feedback Control and Planning of Nonlinear Systems
    - **Authors**: Elamvazhuthi, K., Gadginmath, D., Pasqualetti, F.
    - **Summary**: Eliminates noise in reverse diffusion for deterministic feedback control laws by eliminating stochasticity in the diffusion process.
    - **Year**: 2025

11. **Title**: Dynamics-aware Diffusion Models for Planning and Control
    - **Authors**: Gadginmath, D., Pasqualetti, F.
    - **Summary**: Integrates system dynamics f(x,u) directly into diffusion denoising process via sequential prediction-projection, demonstrating feasibility of embedding dynamics constraints.
    - **Year**: 2025

12. **Title**: Curriculum Learning
    - **Authors**: Bengio, Y., Louradour, J., Collobert, R., Weston, J.
    - **Summary**: Introduced curriculum learning concept of gradually increasing task difficulty during training for better convergence, adapted in TLCD to multi-objective balancing.
    - **Year**: 2009

13. **Title**: Bayesian Physics-Informed Neural Networks for real-world nonlinear dynamical systems
    - **Authors**: Linka, K., Schäfer, A., Meng, X., et al.
    - **Summary**: Embed physics constraints (PDEs) into neural network loss functions for dynamics learning, providing precedent for constraint integration feasibility (146 citations).
    - **Year**: 2022

14. **Title**: Optimal Control and Reinforcement Learning: Theory, Algorithms, and Robotics Applications
    - **Authors**: Pasupuleti, M. K.
    - **Summary**: Comprehensive survey connecting optimal control theory (HJB equations, Lyapunov methods) with RL, providing theoretical bridge between control theory and learning.
    - **Year**: 2025

15. **Title**: Optimal Transport in Systems and Control
    - **Authors**: Chen, Y., Georgiou, T., Pavon, M.
    - **Summary**: Reviews optimal transport as geometric framework for stochastic control via Schrödinger bridge, establishing conceptual connection with diffusion models.
    - **Year**: 2021

16. **Title**: Stochastic Stability of Differential Equations
    - **Authors**: Khasminskii, R. Z.
    - **Summary**: Extended Lyapunov methods to stochastic systems with rigorous probability bounds, providing theoretical justification for probabilistic Lyapunov formulation.
    - **Year**: 1980

17. **Title**: GenerativeRL (opendilab/generativerl, GitHub, 171 stars)
    - **Authors**: Not specified
    - **Summary**: Production-ready library for diffusion-based RL with PyTorch implementation, serving as implementation foundation for extending with Lyapunov network module.
    - **Year**: Not specified

18. **Title**: ddpo (jannerm/ddpo, GitHub, 549 stars)
    - **Authors**: Not specified
    - **Summary**: Training diffusion models with reinforcement learning, implementing RL-diffusion integration as reference implementation for RL-diffusion training loop.
    - **Year**: Not specified

19. **Title**: MuJoCo Continuous Control Suite
    - **Authors**: Todorov, Erez, Tassa
    - **Summary**: Standard physics-based continuous control benchmark (HalfCheetah, Ant, Walker, Hopper) serving as primary evaluation benchmark for stability and performance experiments.
    - **Year**: 2012

20. **Title**: DeepMind Control Suite
    - **Authors**: Tassa et al.
    - **Summary**: Diverse continuous control tasks with standardized evaluation protocol for secondary benchmark for generalization assessment.
    - **Year**: 2018

21. **Title**: Embedding Active Force Control within the Compliant Hybrid Zero Dynamics to Achieve Stable, Fast Running on MABEL
    - **Authors**: Sreenath, K., Park, H. W., Poulakakis, I., Grizzle, J. W.
    - **Summary**: CLF methods successfully deployed in robotic locomotion, demonstrating empirical support for Lyapunov function learnability assumption.
    - **Year**: 2013

22. **Title**: A 'universal' construction of Artstein's theorem on nonlinear stabilization
    - **Authors**: Sontag, E. D.
    - **Summary**: Foundational CLF theory for nonlinear stabilization (identified as missing citation to be filled in Phase 2B).
    - **Year**: 1989

23. **Title**: Nonlinear Systems
    - **Authors**: Khalil, H. K.
    - **Summary**: Lyapunov stability textbook reference (identified as missing citation to be filled in Phase 2B).
    - **Year**: 2002

24. **Title**: Generative Modeling by Estimating Gradients of the Data Distribution
    - **Authors**: Song, Y., Ermon, S.
    - **Summary**: Score matching foundation for diffusion models (identified as missing citation to be filled in Phase 2B).
    - **Year**: 2019

25. **Title**: Diffusion Models Beat GANs on Image Synthesis
    - **Authors**: Dhariwal, P., Nichol, A.
    - **Summary**: Architectural improvements for diffusion models (identified as missing citation to be filled in Phase 2B).
    - **Year**: 2021

26. **Title**: Dynamic Programming and Optimal Control
    - **Authors**: Bertsekas, D. P.
    - **Summary**: Optimal control textbook (identified as missing citation to be filled in Phase 2B).
    - **Year**: 2005

27. **Title**: Stochastic Controls: Hamiltonian Systems and HJB Equations
    - **Authors**: Yong, J., Zhou, X. Y.
    - **Summary**: Stochastic optimal control theory (identified as missing citation to be filled in Phase 2B).
    - **Year**: 1999

**Key Challenges**

1. **Training-Time vs Inference-Time Stability Integration**: Existing methods like S²Diff apply Lyapunov guidance at inference time (post-hoc) requiring iterative guidance that slows sampling, whereas training-time integration could "bake in" stability to score functions for faster deployment.

2. **Joint Optimization Conflict**: Balancing score diversity (required for multimodal control solutions from diffusion objective) with stability enforcement (restrictive Lyapunov constraints) creates optimization tension that may cause mode collapse or unstable controllers.

3. **Probabilistic vs Deterministic Guarantees**: Stochastic diffusion sampling inherently prevents deterministic stability guarantees (V̇ < -αV almost surely), requiring probabilistic formulation (E[V̇] < -αE[V]) which may be insufficient for zero-failure-tolerance systems.

4. **Computational Overhead**: Computing Lyapunov decrease rate ∇V·f requires gradient computation and sampling that adds training overhead, with high-dimensional state spaces potentially requiring prohibitive computational costs.

5. **Region of Attraction Limitation**: Learned Lyapunov functions are only valid over training data distribution, leading to potential instability when encountering out-of-distribution (OOD) states far from training distribution.

6. **Lyapunov Function Expressiveness**: Neural network parameterization of Lyapunov functions must balance expressiveness (capturing complex stability certificates) with validity guarantees (ensuring V̇ < 0 condition is satisfied).

7. **Hyperparameter Sensitivity**: Performance depends on Lyapunov loss weight λ_max, stability margin α, and curriculum schedule, requiring extensive tuning that may vary across domains and limit initial deployment.

8. **Scalability to High-Dimensional Systems**: Methods must scale to complex continuous control tasks with hundreds of state dimensions while maintaining computational efficiency and stability guarantees.

9. **Lack of Comprehensive Theoretical Framework**: Gap exists in connecting diffusion sampling dynamics with classical control guarantees, requiring formal analysis of training-time Lyapunov integration with convergence theory and probabilistic guarantees.

10. **Real-World Deployment and Certification**: Translation of probabilistic stability guarantees (95% Lyapunov satisfaction) into regulatory approval pathways for safety-critical applications (medical devices, aerospace, autonomous vehicles) requires formalized evidence packages and certification protocols.
