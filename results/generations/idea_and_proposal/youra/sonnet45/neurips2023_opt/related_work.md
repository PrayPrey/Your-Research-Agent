## Related Work

**Related Papers**
1. **Title**: Optimization Hyper-parameter Laws for Large Language Models (dbdda156a9de5d8ba73a12d9b50c6eed097da055)
   - **Authors**: Xingyu Xie, Kuang-Yu Ding, Shuicheng Yan, Kim-Chuan Toh, Tianwen Wei
   - **Summary**: Demonstrates that learning rate schedules follow predictable stochastic differential equations (SDEs) across scales, providing direct evidence for β-function existence in hyperparameter evolution.
   - **Year**: 2024

2. **Title**: Scaling with Collapse: Efficient and Predictable Training of LLM Families (8b91aedddfe1d27d7f1a837c252e3e7c61d1d1c1)
   - **Authors**: Shane Bergsma, Bin Claire Zhang, Nolan Dey, et al.
   - **Summary**: Shows that loss curves collapse onto a universal trajectory when hyperparameters are optimally set, providing an empirical signature of renormalization group fixed points.
   - **Year**: 2025

3. **Title**: Renormalization group for deep neural networks: Universality of learning and scaling laws (3b467780515433e7bbac1679f0e86764e6795d95)
   - **Authors**: Peraza Coppola et al.
   - **Summary**: Validates that the renormalization group framework works for finite neural networks using "scaling intervals" framework, enabling application of RG concepts to practical finite systems.
   - **Year**: 2025

4. **Title**: Information-Theoretic Foundations for Neural Scaling Laws (71589222ecf9700a519dd430ac00177b3b467fda)
   - **Authors**: Hong Jun Jeon, Benjamin Van Roy
   - **Summary**: Establishes that optimal data-model size relation is linear through information-theoretic bounds, providing conservation laws relevant to RG framework.
   - **Year**: 2024

5. **Title**: Non-convergence of Adam and other adaptive stochastic gradient descent optimization methods (4baabe81670772edb9952d6c15381a814af8d2a8)
   - **Authors**: Steffen Dereich, Robin Graeber, Arnulf Jentzen
   - **Summary**: Proves that adaptive optimization methods require learning rate decay for convergence, providing relevant perturbation analysis for renormalization group flow dynamics.
   - **Year**: 2024

6. **Title**: Tune As You Scale: Hyperparameter Optimization For Compute Efficient Training (196e48016d66617fe21f3d2fdde9657b9bb52ca3)
   - **Authors**: Abraham J. Fetterman, Ellie Kitanidis, Joshua Albrecht, et al.
   - **Summary**: Proposes CARBS method that learns scaling relationships via Bayesian optimization, representing an empirical learning approach to hyperparameter scaling.
   - **Year**: 2023

7. **Title**: Predictable Scale: Part I - Optimal Hyperparameter Scaling Law in Large Language Model Pretraining (495c0fd22341f46294236c9331b37e40cba1c028)
   - **Authors**: Li et al.
   - **Summary**: Establishes empirical hyperparameter scaling laws, providing descriptive relationships of what works in practice without theoretical explanation.
   - **Year**: 2025

8. **Title**: Data pruning and neural scaling laws (bb4721b1a806ac00308bfb174edf3c36b6f0b620)
   - **Authors**: Fadhel Ayed, Soufiane Hayou
   - **Summary**: Identifies fundamental limits of data pruning, establishing boundary conditions for where scaling laws apply and defining constraints on RG framework validity.
   - **Year**: 2023

**Key Challenges**
1. **Layer-wise vs. Model-size RG Application**: Peraza Coppola et al. 2025 applies RG to layer-wise transformations (treating depth as scale), while the hypothesis applies RG to model-size transformations (treating parameter count as scale), creating tension between different scale variables that must be resolved.

2. **Finite-Size Effects**: Traditional RG theory applies to infinite systems, but neural networks are finite. Requires specialized "scaling intervals" framework to bridge gap between theoretical infinite-size predictions and practical finite neural networks.

3. **Data Availability for Validation**: Published scaling studies from OpenAI, Google, and Meta may contain proprietary data not publicly accessible, potentially requiring costly independent scaling studies to validate β-function extraction methods.

4. **Functional Form Uncertainty**: β-functions could follow power-law, exponential, or logarithmic forms. Selection of appropriate functional form is critical but uncertain, with risk of overfitting if too many forms are tested.

5. **Architecture-Specific Universality**: Different neural network architectures (Transformers, CNNs, MLPs) may belong to different universality classes with distinct β-functions, requiring separate validation for each architecture class and limiting generalizability.

6. **Computational Cost of Validation**: Full validation requires training runs at target scales (e.g., 7B parameter models requiring ~$10-50K in compute per run), making comprehensive experimental validation prohibitively expensive.

7. **Gap Between Descriptive and Explanatory Frameworks**: Existing work (CARBS, Li et al. 2025) provides empirical descriptions of what hyperparameter relationships work, but lacks theoretical explanation for why they work, limiting predictive power beyond interpolation range.

8. **Collapse Robustness**: The collapse phenomenon observed by Bergsma et al. 2025 must be validated as a robust signature of optimal hyperparameter settings rather than a statistical artifact or dataset-specific effect.
