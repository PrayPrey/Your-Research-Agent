## Related Work

**Related Papers**

1. **Title**: ML for Synthetic Data Generation: a Review (Lu et al., 2023)
   - **Authors**: Lu et al.
   - **Summary**: Comprehensive survey of synthetic data generation techniques including GANs, VAEs, and Diffusion models. Identifies data quality and scarcity as key challenges in synthetic data generation.
   - **Year**: 2023

2. **Title**: A review of ensemble learning and data augmentation models for class imbalanced problems (Khan et al., 2023)
   - **Authors**: Khan et al.
   - **Summary**: Evaluates data augmentation methods including SMOTE, ROS, and GANs. Shows that traditional methods outperform GANs in some scenarios, demonstrating that mixing strategies affect training dynamics.
   - **Year**: 2023

3. **Title**: Improving the Performance of IIoT Intrusion Detection System Using Hybrid Synthetic Data (Chen et al., 2024)
   - **Authors**: Chen et al.
   - **Summary**: Hybrid approach combining CTGAN with fuzzing achieved 20% accuracy improvement in IIoT intrusion detection, demonstrating that synthetic data quality affects model performance.
   - **Year**: 2024

4. **Title**: Challenges of Using Synthetic Data Generation Methods for Tabular Microdata (Miletic & Sariyar, 2024)
   - **Authors**: Miletic & Sariyar
   - **Summary**: Comprehensive evaluation of GANs and TVAE on diverse datasets showing "no single model universally excels" - performance is context-dependent.
   - **Year**: 2024

5. **Title**: SMOTE-DP: Improving Privacy-Utility Tradeoff with Synthetic Data (Zhou et al., 2025)
   - **Authors**: Zhou et al.
   - **Summary**: Combines SMOTE with differential privacy to improve privacy-utility trade-off in synthetic data generation.
   - **Year**: 2025

6. **Title**: Can Synthetic Data be Fair and Private? A Comparative Study (Liu et al., 2025)
   - **Authors**: Liu et al.
   - **Summary**: DECAF algorithm achieves best privacy-fairness balance for CTGAN, demonstrating that multiple objectives (performance, privacy, fairness) require multi-objective optimization.
   - **Year**: 2025

7. **Title**: Portfolio Selection (Markowitz, 1952)
   - **Authors**: Markowitz
   - **Summary**: Original portfolio theory paper introducing Mean-Variance Optimization framework, providing the theoretical foundation for asset allocation with 70+ years of validation in finance.
   - **Year**: 1952

8. **Title**: Convex Optimization (Boyd & Vandenberghe, 2004)
   - **Authors**: Boyd & Vandenberghe
   - **Summary**: Standard reference for convex optimization including quadratic programming. Provides convergence guarantees for QP solvers under constraint satisfaction.
   - **Year**: 2004

9. **Title**: Curriculum Learning (Bengio et al., 2009)
   - **Authors**: Bengio et al.
   - **Summary**: Foundational work on training with gradually increasing data complexity, demonstrating that training benefits from starting with easier/diverse data and progressing to harder/specific data.
   - **Year**: 2009

10. **Title**: Curriculum Learning: A Survey (Soviany et al., 2022)
    - **Authors**: Soviany et al.
    - **Summary**: Comprehensive survey of curriculum learning methods and applications validating that training dynamics benefit from adaptive data composition.
    - **Year**: 2022

**Key Challenges**

1. **Optimal Mixing Strategies**: Current approaches rely on ad-hoc heuristics (e.g., "20-30% synthetic") without theoretical justification or empirical validation, leading to suboptimal model performance and wasted computational resources.

2. **Quality Metric Correlation**: Synthetic data quality metrics (SDMetrics fidelity, utility scores) are used for evaluation but not validated as performance proxies for downstream model accuracy.

3. **Dynamic Adaptation Gap**: Existing work uses fixed mixing ratios determined pre-training, lacking dynamic adaptation during training to match data composition to the model's current learning needs.

4. **Multi-Source Optimization**: Most work compares individual synthetic data generation methods rather than optimizing weighted combinations of multiple sources (CTGAN, VAE, Diffusion models).

5. **Constraint Handling**: Prior work doesn't explicitly model privacy budgets and cost constraints in mixing optimization, despite these being critical in production scenarios.

6. **Privacy-Utility Trade-off**: Balancing synthetic data privacy guarantees with model utility remains challenging, particularly under strict privacy regulations (GDPR, HIPAA).

7. **Context-Dependent Performance**: No single synthetic data generation model universally excels across all datasets and tasks, making it difficult to select the best method without extensive experimentation.

8. **Training Stability with Dynamic Rebalancing**: Frequent changes to data distribution during training can destabilize gradient descent, requiring safeguards to maintain convergence.
