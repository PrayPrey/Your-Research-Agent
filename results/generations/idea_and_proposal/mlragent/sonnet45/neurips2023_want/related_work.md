1. **Title**: SpikeRL: A Scalable and Energy-efficient Framework for Deep Spiking Reinforcement Learning (arXiv:2502.17496)
   - **Authors**: Tokey Tahmid, Mark Gates, Piotr Luszczek, Catherine D. Schuman
   - **Summary**: This paper introduces SpikeRL, a framework that integrates spiking neural networks with deep reinforcement learning to enhance energy efficiency and scalability in continuous control tasks. The authors implement mixed-precision training and distributed learning to achieve significant improvements in training speed and energy consumption.
   - **Year**: 2025

2. **Title**: Tri-Accel: Curvature-Aware Precision-Adaptive and Memory-Elastic Optimization for Efficient GPU Usage (arXiv:2508.16905)
   - **Authors**: Mohsen Sheibanian, Pouya Shaeri, Alimohammad Beigi, Ryan T. Woo, Aryan Keluskar
   - **Summary**: Tri-Accel presents a unified optimization framework that co-adapts precision levels, second-order signals, and batch sizes during training. By dynamically assigning mixed-precision levels based on curvature and gradient variance, the framework achieves reductions in training time and memory usage while improving model accuracy.
   - **Year**: 2025

3. **Title**: Lyapunov-Driven Deep Reinforcement Learning for Edge Inference Empowered by Reconfigurable Intelligent Surfaces (arXiv:2305.10931)
   - **Authors**: Kyriakos Stylianopoulos, Mattia Merluzzi, Paolo Di Lorenzo, George C. Alexandropoulos
   - **Summary**: This study proposes a dynamic learning algorithm that jointly optimizes data compression, radio and computation resource allocation, and RIS reflectivity parameters. The approach aims to perform energy-efficient edge classification with constraints on delay and inference accuracy, adapting to time-varying channels and task arrivals.
   - **Year**: 2023

4. **Title**: EARL: Energy-Aware Optimization of Liquid State Machines for Pervasive AI (arXiv:2601.05205)
   - **Authors**: Zain Iqbal, Lorenzo Valerio
   - **Summary**: EARL introduces an energy-aware reinforcement learning framework that integrates Bayesian optimization with adaptive selection policies to optimize both accuracy and energy consumption in Liquid State Machines. The framework demonstrates significant improvements in accuracy, energy efficiency, and optimization time for resource-constrained on-device AI applications.
   - **Year**: 2026

5. **Title**: FP8-LM: Training FP8 Large Language Models (arXiv:2310.18313)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents a mixed-precision training framework utilizing FP8 formats for large language models. The approach achieves reductions in training time and memory consumption while maintaining model performance, demonstrating the potential of low-precision training for large-scale models.
   - **Year**: 2024

6. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji Lin
   - **Summary**: The paper reviews advancements in TinyML, focusing on enabling deep learning on resource-constrained devices. It discusses challenges and solutions related to model design, backpropagation schemes, and co-design strategies, highlighting the importance of energy-efficient training and inference.
   - **Year**: 2024

7. **Title**: On Optimizing the Communication of Model Parallelism (arXiv:2211.05322)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study addresses the communication overhead in model parallelism by proposing an overlapping-friendly pipeline schedule. The approach aims to reduce communication costs and improve training throughput, which is crucial for efficient large-scale model training.
   - **Year**: 2024

**Key Challenges**:

1. **Dynamic Precision Allocation**: Developing methods to dynamically adjust precision levels during training without compromising model accuracy remains a significant challenge.

2. **Resource-Constrained Environments**: Implementing energy-efficient training frameworks that perform effectively in resource-limited settings, such as edge devices, is complex and requires innovative solutions.

3. **Scalability of Adaptive Techniques**: Ensuring that adaptive precision and resource allocation methods scale effectively with increasing model sizes and complexities is a persistent issue.

4. **Real-Time Monitoring Overhead**: Continuously monitoring gradient sensitivity and hardware performance in real-time can introduce computational overhead, potentially offsetting the benefits of adaptive strategies.

5. **Integration with Existing Hardware**: Adapting new training frameworks to work seamlessly with diverse and existing hardware architectures poses compatibility and optimization challenges. 