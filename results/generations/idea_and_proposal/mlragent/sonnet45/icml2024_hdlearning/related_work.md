1. **Title**: Implicit bias produces neural scaling laws in learning curves, from perceptrons to deep networks (arXiv:2505.13230)
   - **Authors**: Francesco D'Amico, Dario Bocchi, Matteo Negri
   - **Summary**: This paper uncovers dynamical scaling laws governing performance evolution during training, linking implicit bias to generalization emergence. The authors analyze training dynamics through spectral complexity norms and provide analytical support using a single-layer perceptron model.
   - **Year**: 2025

2. **Title**: Scaling Law for Stochastic Gradient Descent in Quadratically Parameterized Linear Regression (arXiv:2502.09106)
   - **Authors**: Shihong Ding, Haihan Zhang, Hanzhen Zhao, Cong Fang
   - **Summary**: The authors study scaling laws in linear regression with quadratic parameterization, focusing on feature learning. They demonstrate that stochastic gradient descent adapts to ground truth, providing explicit separations for generalization curves and connecting learning dynamics to model scaling.
   - **Year**: 2025

3. **Title**: Learning to shine: Neuroevolution enables optical control of phase transitions (arXiv:2511.03895)
   - **Authors**: Sraddha Agrawal, Stephen Whitelam, Pierre Darancet
   - **Summary**: This work addresses active optical steering of structural phase transitions in solids using reinforcement learning. The approach derives optimal time-dependent electric fields, enabling stabilization of non-thermal structural phases, and provides a practical route for controlling non-equilibrium structural dynamics.
   - **Year**: 2025

4. **Title**: Discontinuity-aware physics-informed neural networks for phase-field method in three-phase flows (arXiv:2511.23102)
   - **Authors**: Guoqiang Lei, Zhihua Wang, Lijing Zhou, D. Exposito, Xuerui Mao
   - **Summary**: The authors present a discontinuity-aware physics-informed neural network (DPINN) that solves an energy-stable phase-field model for three-phase flows. The method accurately resolves sharp interfacial dynamics and extends to complex three-phase droplet-icing cases.
   - **Year**: 2025

5. **Title**: Statistical Mechanics and Artificial Neural Networks: Principles, Models, and Applications (arXiv:2405.10957)
   - **Authors**: Lucas Böttcher, Gregory Wheeler
   - **Summary**: This chapter provides an overview of artificial neural networks, highlighting their connections to statistical mechanics and statistical learning theory. It focuses on quantifying geometric properties and visualizing loss functions associated with deep neural networks.
   - **Year**: 2024

6. **Title**: Benign overfitting in Fixed Dimension via (arXiv:2406.09194)
   - **Authors**: [Authors not specified]
   - **Summary**: The study investigates kernel ridge and ridgeless regression methods for linear inverse problems governed by elliptic partial differential equations. It reveals that the PDE operator can stabilize variance and lead to benign overfitting in fixed-dimensional problems, emphasizing the importance of smooth inductive biases.
   - **Year**: 2024

7. **Title**: A Large Batch Optimizer Reality Check (arXiv:2102.06356)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper examines the performance of large batch optimizers like LARS and LAMB, demonstrating that standard optimizers can match or improve upon their results. It highlights the need for careful hyperparameter tuning and the role of implicit regularization from gradient noise.
   - **Year**: 2024

8. **Title**: Springer Nature 2021 LATEX template (arXiv:2304.00320)
   - **Authors**: [Authors not specified]
   - **Summary**: This document discusses the implicit regularization effects in neural networks, focusing on the impact of unbiased random label noises in stochastic gradient descent. It provides insights into the additional noise term as an implicit regularizer and its influence on training dynamics.
   - **Year**: 2023

9. **Title**: Published as a conference paper at ICLR 2018 (arXiv:1705.04977)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper compares regularization methods in neural networks, including L1, L2, and group lasso regularization. It evaluates their impact on interaction detection performance and discusses the importance of regularization in training dynamics.
   - **Year**: 2023

**Key Challenges**:

1. **Understanding Implicit Regularization Mechanisms**: Deciphering how different optimizers induce implicit biases at various scales remains complex, requiring advanced mathematical frameworks to predict transitions from memorization to generalization.

2. **Characterizing Critical Thresholds**: Identifying precise scaling exponents where optimization dynamics shift between regimes is challenging due to the intricate interplay between model capacity and data complexity.

3. **Loss Landscape Geometry Analysis**: Linking spectral properties of loss landscapes to generalization behaviors necessitates comprehensive studies of Hessian eigenvalue distributions and their variations across different optimizers.

4. **Validation on Large-Scale Models**: Empirically testing theoretical predictions on large language models and synthetic tasks is resource-intensive and requires meticulous experimental design to isolate implicit regularization effects.

5. **Designing Optimal Scaling Strategies**: Developing mathematical tools to predict optimal model scaling and optimizer selection based on data characteristics involves balancing computational efficiency with model performance, posing significant design challenges. 