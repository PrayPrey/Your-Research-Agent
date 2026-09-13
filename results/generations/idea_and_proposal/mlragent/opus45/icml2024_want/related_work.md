1. **Title**: DPQuant: Efficient and Differentially-Private Model Training via Dynamic Quantization Scheduling (arXiv:2509.03472)
   - **Authors**: Yubo Gao, Renbo Tu, Gennady Pekhimenko, Nandita Vijaykumar
   - **Summary**: This paper introduces DPQuant, a dynamic quantization framework designed to enhance the efficiency of differentially-private stochastic gradient descent (DP-SGD). By adaptively selecting layers for quantization based on probabilistic sampling and loss-aware prioritization, DPQuant achieves up to 2.21x theoretical throughput improvements on low-precision hardware with less than 2% accuracy degradation.
   - **Year**: 2025

2. **Title**: Tri-Accel: Curvature-Aware Precision-Adaptive and Memory-Elastic Optimization for Efficient GPU Usage (arXiv:2508.16905)
   - **Authors**: Mohsen Sheibanian, Pouya Shaeri, Alimohammad Beigi, Ryan T. Woo, Aryan Keluskar
   - **Summary**: Tri-Accel presents a unified optimization framework that co-adapts precision levels, second-order signals, and batch sizes during training. By dynamically assigning mixed-precision levels based on curvature and gradient variance, and adjusting batch sizes according to VRAM availability, it achieves up to 9.9% reduction in training time and 13.3% lower memory usage, while improving accuracy by 1.1 percentage points over FP32 baselines.
   - **Year**: 2025

3. **Title**: Physics-Constrained Adaptive Neural Networks Enable Real-Time Semiconductor Manufacturing Optimization with Minimal Training Data (arXiv:2511.12788)
   - **Authors**: Rubén Darío Guerrero
   - **Summary**: This work introduces a physics-constrained adaptive learning framework that calibrates electromagnetic approximations through learnable parameters while minimizing edge placement error. The approach achieves consistent sub-nanometer precision using minimal training data, demonstrating significant improvements over CNN baselines without physics constraints.
   - **Year**: 2025

4. **Title**: Efficient DNN-Powered Software with Fair Sparse Models (arXiv:2407.02805)
   - **Authors**: Xuanqi Gao, Weipeng Jiang, Juan Zhai, Shiqing Ma, Xiaoyu Zhang, Chao Shen
   - **Summary**: The paper addresses fairness issues in model pruning, particularly with the Lottery Ticket Hypothesis (LTH). It proposes Ballot, a pruning framework that employs conflict-detection-based subnetwork selection and a refined training process to improve fairness in DNN-powered software, achieving up to 38% improvement over state-of-the-art baselines.
   - **Year**: 2024

5. **Title**: DataStates-LLM: Lazy Asynchronous Checkpointing for Large Language Models (arXiv:2406.10707)
   - **Authors**: Avinash Maurya, M. Mustafa Rafique, Franck Cappello, Bogdan Nicolae
   - **Summary**: DataStates-LLM introduces a lazy asynchronous checkpointing mechanism tailored for large language models. By optimizing I/O scheduling and leveraging GPU-enabled asynchronous multi-level checkpoint caching, it enhances training efficiency and fault tolerance in large-scale neural network training.
   - **Year**: 2024

6. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji Lin
   - **Summary**: This paper reviews advancements in tiny machine learning, focusing on techniques to deploy deep learning models on resource-constrained devices. It discusses methods like quantization, pruning, and efficient training strategies that align with the goals of energy-efficient large-scale neural network training.
   - **Year**: 2024

7. **Title**: Tempo: Accelerating Transformer-Based Model Training Through Adaptive Precision Scheduling (arXiv:2210.10246)
   - **Authors**: [Authors not specified]
   - **Summary**: Tempo proposes an adaptive precision scheduling method for transformer-based models, dynamically adjusting numerical precision during training phases. This approach aims to reduce energy consumption and training time while maintaining model accuracy, aligning with the objectives of dynamic precision scheduling.
   - **Year**: 2023

8. **Title**: SqueezeNext: Hardware-Aware Neural Network Design (arXiv:1803.10615)
   - **Authors**: [Authors not specified]
   - **Summary**: SqueezeNext introduces a hardware-aware neural network architecture optimized for efficient inference. By redesigning network modules and employing strategies like group convolutions, it achieves significant reductions in model size and computational requirements, contributing to energy-efficient neural network training.
   - **Year**: 2023

9. **Title**: LDP: Learnable Dynamic Precision for Efficient Deep Neural Network Training and Inference (arXiv:2203.07713)
   - **Authors**: Zhongzhi Yu, Yonggan Fu, Shang Wu, Mengquan Li, Haoran You, Yingyan Lin
   - **Summary**: LDP introduces a framework that learns dynamic precision schedules during training, adjusting precision both temporally and spatially. This method achieves better accuracy and efficiency trade-offs compared to static precision training, demonstrating the benefits of adaptive precision in neural network training.
   - **Year**: 2023

10. **Title**: DataStates-LLM: Lazy Asynchronous Checkpointing for Large Language Models (arXiv:2406.10707)
    - **Authors**: Avinash Maurya, M. Mustafa Rafique, Franck Cappello, Bogdan Nicolae
    - **Summary**: DataStates-LLM introduces a lazy asynchronous checkpointing mechanism tailored for large language models. By optimizing I/O scheduling and leveraging GPU-enabled asynchronous multi-level checkpoint caching, it enhances training efficiency and fault tolerance in large-scale neural network training.
    - **Year**: 2024

**Key Challenges:**

1. **Precision-Accuracy Trade-off**: Balancing reduced numerical precision with model accuracy remains a significant challenge. Lowering precision can lead to faster computations and energy savings but may degrade model performance.

2. **Dynamic Precision Scheduling Complexity**: Implementing adaptive precision strategies that respond to real-time training dynamics adds complexity to the training process. Developing efficient algorithms for dynamic scheduling without introducing significant overhead is challenging.

3. **Hardware Compatibility**: Ensuring that adaptive precision methods are compatible with various hardware architectures is crucial. Different hardware may have varying support for low-precision computations, affecting the generalizability of precision scheduling techniques.

4. **Energy Consumption Measurement**: Accurately measuring and optimizing energy consumption during training is complex. Developing standardized metrics and tools to assess energy efficiency in neural network training is necessary for meaningful comparisons and improvements.

5. **Scalability to Large Models**: Applying adaptive precision scheduling to large-scale models, such as vision transformers and large language models, presents scalability challenges. Ensuring that these methods effectively reduce energy consumption without compromising performance in large models is a key area of research. 