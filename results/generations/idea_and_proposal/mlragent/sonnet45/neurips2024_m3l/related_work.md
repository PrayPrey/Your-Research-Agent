1. **Title**: Heavy-Ball Momentum Method in Continuous Time and Discretization Error Analysis (arXiv:2506.14806)
   - **Authors**: Bochen Lyu, Xiaojing Zhang, Fangyi Zheng, He Wang, Zheng Wang, Zhanxing Zhu
   - **Summary**: This paper establishes a continuous-time approximation for the discrete Heavy-Ball momentum method, explicitly accounting for discretization errors. The authors design a piecewise continuous differential equation that includes counter terms to control discretization error to arbitrary orders of the step size. The study also explores the implicit regularization effects of Heavy-Ball momentum and its bias in diagonal linear networks, providing insights into deep learning optimization.
   - **Year**: 2025

2. **Title**: Closed-form Continuous-time Neural Models (arXiv:2106.13898)
   - **Authors**: Ramin Hasani, Mathias Lechner, Alexander Amini, Lucas Liebenwein, Aaron Ray, Max Tschaikowski, Gerald Teschl, Daniela Rus
   - **Summary**: The authors present a method to approximate the interaction between neurons and synapses in continuous-time neural networks using closed-form solutions. By deriving a tightly-bounded approximation for an integral in liquid time-constant networks, they eliminate the need for complex numerical solvers. This approach results in models that are significantly faster in training and inference compared to traditional differential equation-based counterparts, and they demonstrate strong performance in time series modeling.
   - **Year**: 2021

3. **Title**: Deep Learning via Dynamical Systems: An Approximation Perspective (arXiv:1912.10382)
   - **Authors**: Qianxiao Li, Ting Lin, Zuowei Shen
   - **Summary**: This work explores the dynamical systems approach to deep learning by idealizing deep residual networks as continuous-time dynamical systems. The authors establish sufficient conditions for universal approximation using continuous-time deep residual networks and provide approximation theories in \( L^p \) spaces using flow maps of dynamical systems. The results offer a new paradigm in approximation theory and contribute to the mathematical framework for investigating deep learning.
   - **Year**: 2019

4. **Title**: Stochastic Gradient Descent in Continuous Time (arXiv:1611.05545)
   - **Authors**: Justin Sirignano, Konstantinos Spiliopoulos
   - **Summary**: The paper introduces a continuous-time version of stochastic gradient descent (SGDCT) for the statistical learning of continuous-time models. The SGDCT algorithm follows a noisy descent direction along a continuous stream of data, with parameter updates governed by a stochastic differential equation. The authors prove convergence properties and demonstrate the application of SGDCT in pricing high-dimensional American options using deep neural networks.
   - **Year**: 2016

5. **Title**: Geometric Deep Learning (arXiv:2104.13478)
   - **Authors**: Michael M. Bronstein, Joan Bruna, Taco Cohen, Petar Veličković
   - **Summary**: This paper provides a comprehensive overview of geometric deep learning, which extends deep learning techniques to non-Euclidean domains such as graphs and manifolds. The authors discuss the theoretical foundations, including the role of symmetry and invariance, and explore applications in various fields. The work is relevant for understanding how continuous-time approximations can be applied in complex, structured data settings.
   - **Year**: 2021

6. **Title**: Predictive Coding Approximates Backpropagation Along Arbitrary Computation Graphs (arXiv:2006.04182)
   - **Authors**: Thomas P. Lillicrap, Adam Santoro, Luke Marris, Colin J. Akerman, Geoffrey Hinton
   - **Summary**: The authors demonstrate that predictive coding can serve as a local and biologically plausible approximation to backpropagation in arbitrary, deep, and branching computation graphs. They show that convergence to exact backpropagation gradients is rapid and robust, even in deep networks like unrolled LSTMs. This work suggests that predictive coding could be a scalable alternative to backpropagation in training deep networks.
   - **Year**: 2020

7. **Title**: Deep Adversarial Koopman Model for Nonlinear Dynamical Systems (arXiv:2006.05547)
   - **Authors**: Karthik Duraisamy, Krishnan Raghavan, Ramachandra A. Sathye
   - **Summary**: This paper introduces a deep adversarial Koopman model that combines generative adversarial networks (GANs) with autoencoder-based Koopman models to learn representations of nonlinear dynamical systems. The approach is applied to chaotic and reaction-diffusion systems, demonstrating robustness and effectiveness in predicting future states and handling noisy or missing data scenarios.
   - **Year**: 2020

8. **Title**: The Cost-Accuracy Trade-Off in Operator Learning with Neural Networks (arXiv:2203.13181)
   - **Authors**: Maarten V. de Hoop, Daniel Zhengyu Huang, Elizabeth Qian, Andrew M. Stuart
   - **Summary**: The authors conduct a numerical study comparing various neural network architectures for operator approximation in the context of partial differential equations. They focus on the cost-accuracy trade-off, assessing the computational resources required to achieve desired accuracy levels. The study provides insights into the efficiency and effectiveness of different neural network-based surrogate models for solving PDEs.
   - **Year**: 2022

9. **Title**: Adaptive Deep Density Approximation for Stochastic Systems (arXiv:2405.02810)
   - **Authors**: [Authors not specified]
   - **Summary**: This work presents an adaptive sampling-based physics-informed training method for temporal Koopman residual networks (tKRnet) applied to stochastic systems. The approach addresses challenges in long-time integration and demonstrates efficient performance through temporal decomposition and adaptive sampling. The method is particularly relevant for modeling stochastic differential equations in deep learning contexts.
   - **Year**: 2024

10. **Title**: Journal of Machine Learning (arXiv:2203.13181)
    - **Authors**: [Authors not specified]
    - **Summary**: This article discusses the cost-accuracy trade-off in operator learning with neural networks, focusing on surrogate modeling for partial differential equations. The authors provide a careful numerical study comparing different neural network architectures, assessing computational resources required to achieve desired accuracy levels, and offering insights into the efficiency of various approaches.
    - **Year**: 2022

**Key Challenges:**

1. **Validity of Continuous-Time Approximations**: Ensuring that continuous-time models accurately represent discrete training dynamics, especially near stability thresholds, remains a significant challenge.

2. **Modeling Time-Varying Learning Rates**: Developing theoretical frameworks that effectively incorporate time-varying learning rates into continuous-time models is complex and requires further research.

3. **Edge of Stability Phenomenon**: Understanding and characterizing the Edge of Stability in deep learning optimization, particularly how it interacts with learning rate schedules, is an ongoing area of investigation.

4. **Implicit Regularization Effects**: Analyzing how different optimization methods, such as momentum-based approaches, implicitly regularize training dynamics and influence generalization performance is crucial.

5. **Scalability and Computational Efficiency**: Designing continuous-time models that are computationally efficient and scalable to large-scale neural networks without compromising accuracy is a persistent challenge. 