## Related Work

**Related Papers**
1. **Title**: Adaptive Operator Selection for Meta-Heuristics: A Survey (2025)
   - **Authors**: Jiyuan Pei, Yi Mei, Jialin Liu, Mengjie Zhang, Xinghu Yao
   - **Summary**: Demonstrates that state-based operator selection (matching operators to optimization stages) improves meta-heuristic performance over fixed strategies by 15-30%, providing core technique for adaptive sampler selection.
   - **Year**: 2025

2. **Title**: Steady State and Switching Loss Improvements in Hybrid AC-DC Microgrids Using Adaptive Predictive Learning (2024)
   - **Authors**: Putchakayala Yanna Reddy, L. Saikia
   - **Summary**: Combines Model Predictive Control (MPC) with Deep Reinforcement Learning (DRL) to reduce switching losses in hybrid systems by predicting future behavior and adapting to dynamics, providing architectural inspiration for performance predictor and Thompson sampling.
   - **Year**: 2024

3. **Title**: Gradient-adjusted underdamped Langevin dynamics for sampling (GAUL, 2024)
   - **Authors**: Xinzhe Zuo, Stanley Osher, Wuchen Li
   - **Summary**: Combines Hessian information (curvature) with Langevin dynamics to achieve faster convergence, representing a static hybrid approach that uses fixed combination rather than dynamic selection.
   - **Year**: 2024

4. **Title**: Federated Averaging Langevin Dynamics (VR-FALD, 2022)
   - **Authors**: Vincent Plassier, A. Durmus, É. Moulines
   - **Summary**: Implements static hybrid approach using fixed variance reduction for federated sampling, contrasting with adaptive switching approaches.
   - **Year**: 2022

5. **Title**: SiT: Exploring Flow and Diffusion-based Generative Models with Scalable Interpolant Transformers (2024)
   - **Authors**: Nanye Ma, Mark Goldstein, M. S. Albergo, et al.
   - **Summary**: Develops scalable flow-based generative models using interpolant transformers, representing a fixed flow-based approach without adaptive selection between flows and MCMC.
   - **Year**: 2024

6. **Title**: Flow-based generative models as iterative algorithms in probability space (2025)
   - **Authors**: Yao Xie, Xiuyuan Cheng
   - **Summary**: Provides theoretical framework for flow-based samplers but does not address "when to use flows vs MCMC" question, highlighting need for principled selection guidelines.
   - **Year**: 2025

7. **Title**: Bayesian Data Analysis
   - **Authors**: Gelman et al.
   - **Summary**: Foundational text on Bayesian methods and MCMC diagnostics, providing standard approaches for Effective Sample Size (ESS) estimation via autocorrelation computation.
   - **Year**: Not specified

8. **Title**: Thompson Sampling for Multi-Armed Bandits
   - **Authors**: Not specified
   - **Summary**: Foundational work on Thompson sampling proving it balances exploration-exploitation in multi-armed bandit problems, with over 1000 citations supporting its use in uncertainty-aware selection.
   - **Year**: Not specified

9. **Title**: OpenReview Adaptive Methods Paper (2024)
   - **Authors**: Not specified
   - **Summary**: Demonstrates common failure patterns in adaptive methods when state features are uninformative or switching overhead dominates, validating need for explicit assumption validation.
   - **Year**: 2024

10. **Title**: hybrid-sampling (GitHub Repository)
    - **Authors**: arijitthegame
    - **Summary**: Implementation of hybrid sampling methods limited to specific domain (softmax sampling), demonstrating feasibility but highlighting lack of general framework for adaptive sampler selection.
    - **Year**: Not specified

**Key Challenges**
1. **Unified Framework for Hybrid Samplers**: Existing approaches use static combinations (GAUL's algorithmic combination of Hessian and Langevin, VR-FALD's fixed variance reduction) rather than dynamic selection based on problem state. No prior work addresses the "when to use which sampler" question for combining learning-based and classical methods.

2. **State Feature Informativeness**: Adaptive selection methods can fail when state features are uninformative or do not correlate with sampler performance, requiring careful validation that problem characteristics (ESS, convergence rate, dimension, curvature) meaningfully predict efficiency.

3. **Switching Overhead Dominance**: Hybrid systems risk performance degradation when the cost of switching between samplers exceeds the benefits of adaptive selection, particularly if warm-starting between different sampler types (flow→MCMC, MCMC→flow) is inefficient.

4. **Generalization from Synthetic Benchmarks**: Performance predictors trained on synthetic problems (Gaussian mixtures, funnel distributions) may not generalize to complex real-world distributions without prohibitive fine-tuning costs.

5. **Theoretical Selection Guidelines**: While theoretical frameworks exist for individual sampler types (flows, diffusion, Langevin MCMC), principled guidelines for selecting among them based on problem dynamics are lacking in the literature.

6. **Exploration-Exploitation Balance**: Early-stage sampling involves high uncertainty in state estimates (ESS, convergence rate), requiring robust selection strategies that balance exploring different samplers with exploiting predictor recommendations.

7. **Domain-Specific Adaptation**: Existing hybrid sampling implementations are often limited to specific application domains (e.g., softmax sampling, federated learning) rather than providing general frameworks applicable across diverse probabilistic inference problems.
