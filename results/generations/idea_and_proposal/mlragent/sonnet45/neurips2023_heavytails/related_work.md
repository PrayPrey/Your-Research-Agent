1. **Title**: Multiplicative Noise and Heavy Tails in Stochastic Optimization (arXiv:2006.06293)
   - **Authors**: Liam Hodgkinson, Michael W. Mahoney
   - **Summary**: This paper models stochastic optimization algorithms as discrete random recurrence relations and demonstrates that multiplicative noise, arising from variance in local convergence rates, leads to heavy-tailed stationary behavior in parameters. The authors provide a detailed analysis for SGD applied to linear regression and extend their results to a broader class of models and optimizers, highlighting the role of multiplicative noise in enhancing exploration of non-convex loss surfaces.
   - **Year**: 2020

2. **Title**: Second-order Optimization under Heavy-Tailed Noise: Hessian Clipping and Sample Complexity Limits (arXiv:2510.10690)
   - **Authors**: Abdurakhmon Sadiev, Peter Richtárik, Ilyas Fatkhullin
   - **Summary**: This work addresses the challenges of second-order optimization in the presence of heavy-tailed noise. The authors establish tight lower bounds on the sample complexity of any second-order method under such noise conditions and introduce a novel algorithm based on gradient and Hessian clipping. They provide high-probability upper bounds that nearly match the fundamental limits, positioning Hessian clipping as a robust strategy for second-order optimization in heavy-tailed regimes.
   - **Year**: 2025

3. **Title**: Nonconvex Decentralized Stochastic Bilevel Optimization under Heavy-Tailed Noises (arXiv:2509.15543)
   - **Authors**: Xinwen Zhang, Yihan Zhang, Hongchang Gao
   - **Summary**: The authors develop a decentralized stochastic bilevel optimization algorithm tailored for nonconvex problems under heavy-tailed noise. They propose a normalized stochastic variance-reduced bilevel gradient descent algorithm that avoids clipping operations and establish its convergence rate by innovatively bounding interdependent gradient sequences. This work provides the first decentralized bilevel optimization algorithm with rigorous theoretical guarantees under heavy-tailed noise.
   - **Year**: 2025

4. **Title**: Can SGD Handle Heavy-Tailed Noise? (arXiv:2508.04860)
   - **Authors**: Ilyas Fatkhullin, Florian Hübler, Guanghui Lan
   - **Summary**: This paper investigates the performance of vanilla SGD under heavy-tailed noise conditions. Assuming stochastic gradients with bounded p-th moments for some p in (1, 2], the authors establish sharp convergence guarantees for SGD across convex, strongly convex, and non-convex problem classes. Their results challenge the prevailing view that heavy-tailed noise renders SGD ineffective, positioning it as a robust baseline even in regimes with unbounded variance.
   - **Year**: 2025

5. **Title**: Heavy-Ball Momentum Accelerated Actor-Critic With Function Approximation (arXiv:2408.06945)
   - **Authors**: Yanjie Dong, Haijun Zhang, Gang Wang, Shisheng Cui, Xiping Hu
   - **Summary**: The authors propose a heavy-ball momentum-based advantage actor-critic (HB-A2C) algorithm by integrating heavy-ball momentum into the critic recursion parameterized by a linear function. They quantitatively certify the acceleration capability of HB-A2C and demonstrate its convergence to an ε-approximate stationary point with O(ε⁻²) iterations for reinforcement learning tasks with Markovian noise.
   - **Year**: 2024

6. **Title**: A Large Batch Optimizer Reality Check: Traditional, Generic Optimizers Suffice Across Batch Sizes (arXiv:2102.06356)
   - **Authors**: Zachary Nado, Justin M. Gilmer, Rohan Anil, Christopher J. Shallue, George E. Dahl
   - **Summary**: This study evaluates the performance of standard optimization algorithms like Nesterov momentum and Adam in large batch training scenarios. The authors demonstrate that these traditional optimizers can match or exceed the results of specialized algorithms like LARS and LAMB at large batch sizes, establishing stronger baselines for future comparisons and shedding light on the difficulties of comparing optimizers for neural network training.
   - **Year**: 2021

7. **Title**: Technical Report: A Totally Asynchronous Nesterov’s Accelerated Gradient Algorithm for Optimization (arXiv:2406.10124)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper presents a totally asynchronous implementation of Nesterov’s accelerated gradient algorithm for optimization. The authors show that this algorithm converges linearly in the number of agents' computations and communications when counted in a certain sequence, and simulations demonstrate that it converges faster than comparable heavy-ball and gradient descent algorithms.
   - **Year**: 2024

8. **Title**: Automatic Gradient Descent: Optimizer Reference Hyperparameter Free Width Scaling Depth Scaling Automatic Schedule Memory Cost (arXiv:2304.05187)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces Automatic Gradient Descent (AGD), an optimizer derived by applying the majorize-minimize meta-algorithm to deep network objective functions. AGD trains various network architectures without hyperparameters and scales to deep networks such as ResNet-50 and large datasets like ImageNet. It operates out-of-the-box even when Adam and SGD fail with their default hyperparameters.
   - **Year**: 2023

9. **Title**: Machine Learning for Combinatorial Optimization: Optimiser Reference Hyperparameter Free Width Scaling Depth Scaling Automatic Schedule Memory Cost (arXiv:1811.06128)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses the application of machine learning techniques to combinatorial optimization problems. It highlights the use of deep learning architectures to handle structured data and the challenges associated with training such models, including issues related to optimization and generalization.
   - **Year**: 2018

10. **Title**: SPAM: Stochastic Proximal Point Method with Momentum Variance Reduction for Non-convex Cross-Device Federated Learning (arXiv:2405.20127)
    - **Authors**: Avetik Karagulyan, Egor Shulgin, Abdurakhmon Sadiev, Peter Richtárik
    - **Summary**: The authors propose SPAM, a stochastic proximal point method with momentum variance reduction, tailored for non-convex cross-device federated learning. They provide sharp analysis under second-order similarity, a condition satisfied by various machine learning problems in practice, and extend their results to the partial participation setting, where a cohort of selected clients communicates with the server at each round.
    - **Year**: 2024

**Key Challenges**:

1. **Modeling Heavy-Tailed Noise**: Accurately modeling and estimating heavy-tailed noise in gradient distributions remains complex, requiring sophisticated statistical tools and assumptions.

2. **Algorithm Stability**: Designing optimization algorithms that remain stable and converge efficiently in the presence of heavy-tailed noise is challenging due to the potential for large deviations and instability.

3. **Adaptive Mechanisms**: Developing adaptive mechanisms that can dynamically adjust algorithm parameters, such as the stability parameter α in α-stable processes, based on real-time estimates of gradient distributions is non-trivial.

4. **Generalization Performance**: Ensuring that optimization algorithms leveraging heavy-tailed dynamics not only converge but also generalize well to unseen data is a significant challenge.

5. **Computational Overhead**: Implementing heavy-tail-aware optimization algorithms may introduce additional computational overhead, making them less practical for large-scale machine learning tasks. 