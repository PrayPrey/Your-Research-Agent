Here is a literature review on the topic of "Data-Efficient Calibration via Selective Self-Training under Distribution Shift," focusing on papers published between 2023 and 2025:

**1. Related Papers**

1. **Title**: Flexible Distribution Alignment: Towards Long-tailed Semi-supervised Learning with Proper Calibration (arXiv:2306.04621)
   - **Authors**: Emanuel Sanchez Aimar, Nathaniel Helgesen, Yonghao Xu, Marco Kuhlmann, Michael Felsberg
   - **Summary**: This paper introduces Flexible Distribution Alignment (FlexDA), an adaptive logit-adjusted loss framework designed to dynamically estimate and align predictions with the actual distribution of unlabeled data. It aims to achieve a balanced classifier by the end of training, addressing issues like biased pseudo-labels and poorly calibrated probabilities in long-tailed semi-supervised learning scenarios.
   - **Year**: 2023

2. **Title**: Adaptive Calibrator Ensemble for Model Calibration under Distribution Shift (arXiv:2303.05331)
   - **Authors**: Yuli Zou, Weijian Deng, Liang Zheng
   - **Summary**: The authors propose an Adaptive Calibrator Ensemble (ACE) method to calibrate models under distribution shifts. ACE trains two calibration functions for in-distribution and severely out-of-distribution data, respectively, and uses an adaptive weighting method to balance between the two, improving calibration performance without additional computational overhead.
   - **Year**: 2023

3. **Title**: Ciliate: Towards Fairer Class-based Incremental Learning by Dataset and Training Refinement (arXiv:2304.04222)
   - **Authors**: Xuanqi Gao, Juan Zhai, Shiqing Ma, Chao Shen, Yufei Chen, Shiwei Wang
   - **Summary**: This work addresses fairness issues in class-based incremental learning (CIL) by proposing Ciliate, a framework that identifies unique and important samples overlooked by existing CIL methods. It enforces the model to learn from these samples, improving fairness and calibration in incremental learning scenarios.
   - **Year**: 2023

4. **Title**: Covariance-Aware Feature Alignment with Pre-computed Source Statistics for Test-Time Adaptation (arXiv:2204.13263)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The paper proposes Covariance-Aware Feature Alignment (CAFe), a test-time adaptation method that aligns feature distributions without accessing the source dataset. By incorporating pre-computed source statistics, CAFe effectively adapts models to target domains under distribution shifts, improving calibration and accuracy.
   - **Year**: 2023

5. **Title**: Frustratingly Easy Uncertainty Estimation for Deep Neural Networks (arXiv:2106.03762)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work introduces simple post-hoc methods for model calibration under distributional shifts, focusing on unsupervised scenarios where only unlabeled test data is available. The proposed methods provide superior calibration results without requiring retraining or additional computational resources.
   - **Year**: 2023

6. **Title**: Improving Self-Training under Distribution Shifts via Anchored Confidence with Theoretical Guarantees (arXiv:2411.00586)
   - **Authors**: Taejong Joo, Diego Klabjan
   - **Summary**: The authors develop a principled method to improve self-training under distribution shifts based on temporal consistency. By building an uncertainty-aware temporal ensemble with relative thresholding, the method smooths noisy pseudo-labels and promotes selective temporal consistency, leading to improved calibration and accuracy.
   - **Year**: 2024

7. **Title**: Learning Calibrated Uncertainties for Domain Shift: A Distributionally Robust Learning Approach (arXiv:2010.05784)
   - **Authors**: Haoxuan Wang, Zhiding Yu, Yisong Yue, Anima Anandkumar, Anqi Liu, Junchi Yan
   - **Summary**: This paper proposes a framework for learning calibrated uncertainties under domain shifts by detecting such shifts via a differentiable density ratio estimator. The approach adjusts the uncertainty of predictions in the task network, leading to improved calibration and performance in unsupervised domain adaptation and semi-supervised learning tasks.
   - **Year**: 2023

8. **Title**: Collaboration and Transition: Distilling Item Transitions into Sequential Recommendation (arXiv:2311.01056)
   - **Authors**: Tianyu Zhu, et al.
   - **Summary**: The paper introduces a method to integrate global item transition patterns into sequential recommendation models through knowledge distillation. By constructing a global item transition graph and distilling this information into the model, the approach enhances calibration and accuracy in recommendation systems.
   - **Year**: 2024

9. **Title**: Learning to Simulate Self-Driven Particles System (arXiv:2110.13827)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work presents a novel multi-agent reinforcement learning algorithm called Coordinated Policy Optimization (CoPO) to facilitate the coordination of agents in self-driven particle systems. The approach incorporates local and global coordination mechanisms, leading to improved calibration and performance in complex systems.
   - **Year**: 2023

10. **Title**: COVARIANCE-AWARE FEATURE ALIGNMENT WITH PRE-COMPUTED SOURCE STATISTICS FOR TEST-TIME ADAPTATION (arXiv:2204.13263)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: The paper proposes Covariance-Aware Feature Alignment (CAFe), a test-time adaptation method that aligns feature distributions without accessing the source dataset. By incorporating pre-computed source statistics, CAFe effectively adapts models to target domains under distribution shifts, improving calibration and accuracy.
    - **Year**: 2023

**2. Key Challenges**

1. **Limited Labeled Data**: Calibration methods often require substantial labeled data, and their effectiveness diminishes when labeled data is scarce.

2. **Distribution Shift**: Models calibrated on source data may become miscalibrated when deployed in target domains with different distributions.

3. **Pseudo-Label Selection**: In self-training, selecting pseudo-labels that improve both accuracy and calibration is challenging, especially under distribution shifts.

4. **Computational Constraints**: Some calibration methods involve computationally intensive processes, making them impractical in resource-constrained settings.

5. **Trade-off Between Accuracy and Calibration**: Achieving high accuracy and proper calibration simultaneously is often difficult, as improvements in one can lead to degradation in the other. 