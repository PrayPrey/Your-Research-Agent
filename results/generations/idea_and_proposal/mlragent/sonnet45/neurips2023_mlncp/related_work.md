1. **Title**: Variance-Aware Noisy Training: Hardening DNNs against Unstable Analog Computations (arXiv:2503.16183)
   - **Authors**: Xiao Wang, Hendrik Borras, Bernhard Klein, Holger Fröning
   - **Summary**: This paper addresses the challenges posed by dynamic noise in analog computing systems used for deep learning. The authors propose Variance-Aware Noisy Training, a method that incorporates noise schedules emulating evolving noise conditions during inference. This approach significantly enhances model robustness without additional training overhead, achieving notable accuracy improvements on datasets like CIFAR-10 and Tiny ImageNet.
   - **Year**: 2025

2. **Title**: Variational Adaptive Noise and Dropout towards Stable Recurrent Neural Networks (arXiv:2506.01350)
   - **Authors**: Taisuke Kobayashi, Shingo Murata
   - **Summary**: The authors introduce Variational Adaptive Noise and Dropout (VAND), a stable learning theory for recurrent neural networks. By reinterpreting the optimization problem of RNNs as variational inference, they derive noise and dropout mechanisms that can be adjusted to optimize the main objective of RNNs. VAND demonstrates effectiveness in imitation learning scenarios, enabling the replication of sequential and periodic behaviors.
   - **Year**: 2025

3. **Title**: Data-Efficient Quantum Noise Modeling via Machine Learning (arXiv:2509.12933)
   - **Authors**: Yanjun Ji, Marco Roth, David A. Kreplin, Ilia Polian, Frank K. Wilhelm
   - **Summary**: This study presents a machine learning-based framework for constructing accurate, parameterized noise models for superconducting quantum processors. By learning hardware-specific error parameters directly from measurement data, the approach circumvents costly characterization protocols and achieves significant improvements in model fidelity, providing a practical paradigm for noise characterization in quantum computing.
   - **Year**: 2025

4. **Title**: Extending Straight-Through Estimation for Robust Neural Networks on Analog CIM Hardware (arXiv:2508.11940)
   - **Authors**: Yuannuo Feng, Wenyong Zhou, Yuexi Lyu, Yixiang Zhang, Zhengwu Liu, Ngai Wong, Wang Kang
   - **Summary**: The paper proposes an extension of the Straight-Through Estimator (STE) framework to enhance the robustness of neural networks deployed on analog Compute-In-Memory (CIM) hardware. By decoupling forward noise simulation from backward gradient computation, the method enables noise-aware training with accurate noise modeling, resulting in improved accuracy, training speed, and reduced memory usage.
   - **Year**: 2025

5. **Title**: Improving Analog Neural Network Robustness: A Noise-Agnostic Approach with Explainable Regularizations (arXiv:2409.08633)
   - **Authors**: Alice Duque, Pedro Freire, Egor Manuylovich, Dmitrii Stoliarov, Jaroslaw Prilepsky, Sergei Turitsyn
   - **Summary**: This work addresses the challenge of mitigating hardware noise in deep analog neural networks. The authors propose a hardware-agnostic solution that introduces an explainable regularization framework, enhancing noise robustness by revealing mechanisms that reduce sensitivity to noise. The approach achieves significant accuracy improvements in noisy environments compared to standard training methods.
   - **Year**: 2024

6. **Title**: Method for Noise-Induced Regularization in Quantum Neural Networks (arXiv:2410.19921)
   - **Authors**: Wilfrid Somogyi, Ekaterina Pankovets, Viacheslav Kuzmin, Alexey Melnikov
   - **Summary**: The authors present a method for leveraging noise as a regularization tool in quantum neural networks. By introducing controlled noise during training, the approach aims to enhance the generalization capabilities of quantum models, providing insights into the interplay between noise and learning in quantum systems.
   - **Year**: 2024

7. **Title**: Generalization Bounds for Noisy Iterative Algorithms Using Properties of Additive Noise Channels
   - **Authors**: Hao Wang, Rui Gao, Flavio P. Calmon
   - **Summary**: This paper analyzes the generalization behavior of models trained by noisy iterative algorithms. By connecting these algorithms to additive noise channels from information theory, the authors derive distribution-dependent generalization bounds, offering insights into applications like differentially private stochastic gradient descent and federated learning.
   - **Year**: 2023

8. **Title**: Enhancing Convolutional Neural Network Robustness Against Image Noise via an Artificial Visual System
   - **Authors**: Bin Li, Yuki Todo, Sichen Tao, Cheng Tang, Yu Wang
   - **Summary**: The study proposes an artificial visual system to improve the robustness of convolutional neural networks against image noise. By mimicking biological visual processing, the system enhances feature extraction and noise suppression, leading to improved performance in noisy imaging conditions.
   - **Year**: 2025

9. **Title**: Improving the Robustness of Analog Deep Neural Networks through a Bayes-Optimized Noise Injection Approach
   - **Authors**: Nanyang Ye, Linfeng Cao, Liujia Yang, Ziqing Zhang, Zhicheng Fang, Qinying Gu, Guang-Zhong Yang
   - **Summary**: This paper introduces a Bayes-optimized noise injection method to enhance the robustness of analog deep neural networks. By systematically injecting noise during training, the approach mitigates the instability caused by hardware imperfections, leading to more reliable analog DNNs suitable for resource-limited platforms.
   - **Year**: 2023

10. **Title**: Exploiting Noise as a Resource for Computation and Learning in Spiking Neural Networks
    - **Authors**: Gehua Ma, Rui Yan, Huajin Tang
    - **Summary**: The authors introduce the concept of noisy spiking neural networks (NSNNs) and a noise-driven learning rule. By incorporating noisy neuronal dynamics, the framework leverages noise for scalable, flexible, and reliable computation and learning, demonstrating improved robustness and performance in spiking neural models.
    - **Year**: 2023

**Key Challenges:**

1. **Characterization of Hardware Noise Profiles**: Accurately modeling and characterizing the noise inherent in analog hardware is complex, requiring detailed understanding and measurement of various noise sources and their impact on neural network computations.

2. **Designing Noise-Aware Training Algorithms**: Developing training algorithms that effectively incorporate hardware noise as a form of regularization without compromising performance is challenging, necessitating innovative approaches to balance noise exploitation and task accuracy.

3. **Adaptation of Network Architectures**: Modifying neural network architectures to be robust against hardware-induced noise involves selecting appropriate activation functions, designing skip connections, and ensuring overall stability, which can be intricate and hardware-dependent.

4. **Validation on Energy-Based and Equilibrium Models**: Demonstrating the effectiveness of noise-adaptive training on specific model classes like energy-based models and equilibrium models requires tailored validation strategies and may face unique challenges due to the models' inherent properties.

5. **Achieving Energy Efficiency without Performance Trade-offs**: While leveraging hardware noise aims to improve energy efficiency, ensuring that this does not lead to significant performance degradation is a critical challenge, requiring careful optimization and co-design of hardware and algorithms. 