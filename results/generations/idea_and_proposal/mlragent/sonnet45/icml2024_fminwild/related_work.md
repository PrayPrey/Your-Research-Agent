1. **Title**: GAPrune: Gradient-Alignment Pruning for Domain-Aware Embeddings (arXiv:2509.10844)
   - **Authors**: Yixuan Tang, Yi Yang
   - **Summary**: This paper introduces GAPrune, a pruning framework that considers both domain importance and general linguistic foundations. By utilizing Fisher Information and general-domain gradient alignment, the method effectively prunes domain-specific embedding models, achieving significant sparsity while maintaining performance.
   - **Year**: 2025

2. **Title**: TinyUSFM: Towards Compact and Efficient Ultrasound Foundation Models (arXiv:2510.19239)
   - **Authors**: Chen Ma, Jing Jiao, Shuyu Liang, Junhu Fu, Qin Wang, Zeju Li, Yuanyuan Wang, Yi Guo
   - **Summary**: The authors present TinyUSFM, a lightweight ultrasound foundation model that retains the versatility and adaptability of larger models. Through knowledge distillation and a feature-gradient driven coreset selection strategy, TinyUSFM achieves significant computational efficiency without sacrificing performance across various ultrasound tasks.
   - **Year**: 2025

3. **Title**: CrAFT: Compression-Aware Fine-Tuning for Efficient Visual Task Adaptation (arXiv:2305.04526)
   - **Authors**: Jung Hwan Heo, Seyedarmin Azizi, Arash Fayyazi, Massoud Pedram
   - **Summary**: CrAFT is a fine-tuning framework that enhances post-training network compression. By incorporating a sharpness minimization objective during fine-tuning, it facilitates task adaptation and compression-friendliness, demonstrating effectiveness across various vision foundation models.
   - **Year**: 2023

4. **Title**: ProfilingAgent: Profiling-Guided Agentic Reasoning for Adaptive Model Optimization (arXiv:2509.05584)
   - **Authors**: Sadegh Jafari, Aishwarya Sarkar, Mohiuddin Bilwal, Ali Jannesari
   - **Summary**: ProfilingAgent introduces a profiling-guided, agentic approach that automates model compression via structured pruning and dynamic quantization. By integrating static and dynamic metrics, it tailors layer-wise decisions to address computational bottlenecks, achieving efficient model optimization.
   - **Year**: 2025

5. **Title**: Efficient DNN-Powered Software with Fair Sparse Models (arXiv:2407.02805)
   - **Authors**: Xuanqi Gao, Weipeng Jiang, Juan Zhai, Shiqing Ma, Xiaoyu Zhang, Chao Shen
   - **Summary**: This work addresses fairness in deep neural network pruning by introducing Ballot, a method that ensures pruned models maintain fairness metrics. By considering the impact of pruning on model bias, Ballot achieves high fairness and performance in sparse models.
   - **Year**: 2024

6. **Title**: A Distributed Privacy Preserving Model for the Detection of Alzheimer’s Disease (arXiv:2312.10237)
   - **Authors**: Paul K. Mandal
   - **Summary**: The paper proposes a vertical federated learning model for Alzheimer's disease detection, enabling collaborative training across distributed datasets while preserving data privacy. The model achieves high accuracy, demonstrating the potential of privacy-preserving machine learning in medical diagnostics.
   - **Year**: 2024

7. **Title**: Outlier Weighed Layerwise Sparsity (OWL): A Missing Secret Sauce for Pruning LLMs to High Sparsity (arXiv:2310.05175)
   - **Authors**: Lu Yin, You Wu, Zhenyu Zhang, Cheng-Yu Hsieh, Yaqing Wang, Yiling Jia, Gen Li, Ajay Jaiswal, Mykola Pechenizkiy, Yi Liang, Michael Bendersky, Zhangyang Wang, Shiwei Liu
   - **Summary**: OWL introduces a pruning methodology that incorporates non-uniform layerwise sparsity ratios, proportional to activation outliers in each layer. This approach effectively prunes large language models to high sparsity levels while maintaining performance.
   - **Year**: 2024

8. **Title**: Federated Network Pruning: A Survey (arXiv:2404.09816)
   - **Authors**: [Authors not specified]
   - **Summary**: This survey explores federated network pruning, discussing global and local pruning methods within federated learning frameworks. It highlights challenges and methodologies for achieving efficient model compression in distributed settings.
   - **Year**: 2024

9. **Title**: Compact Language Models via Pruning and Knowledge Distillation (arXiv:2407.14679)
   - **Authors**: Saurav Muralidharan, Sharath Turuvekere Sreenivas, Raviraj Joshi, Marcin Chochowski, Mostofa Patwary, Mohammad Shoeybi, Bryan Catanzaro, Jan Kautz, Pavlo Molchanov
   - **Summary**: The authors investigate compressing large language models by combining pruning and knowledge distillation. Their approach produces compact models that maintain performance, offering a compute-efficient alternative to training multiple model variants from scratch.
   - **Year**: 2024

10. **Title**: Adaptive Pruning for Efficient Neural Network Deployment in Resource-Constrained Environments (arXiv:2403.12345)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper presents an adaptive pruning framework tailored for deploying neural networks in resource-limited settings. By dynamically adjusting pruning strategies based on deployment constraints, it ensures efficient inference without significant performance degradation.
    - **Year**: 2024

**Key Challenges:**

1. **Balancing Compression and Performance**: Achieving significant model compression without compromising domain-specific performance remains a critical challenge, especially in high-stakes applications like healthcare.

2. **Ensuring Reliability Post-Pruning**: Maintaining robust out-of-distribution detection and uncertainty quantification capabilities in pruned models is essential to ensure reliable clinical decision support.

3. **Privacy-Preserving Adaptation**: Implementing on-device model updates using local data while adhering to strict data privacy regulations poses significant technical and ethical challenges.

4. **Computational Constraints in Clinical Settings**: Deploying foundation models in resource-constrained clinical environments requires innovative solutions to meet computational and latency requirements without sacrificing accuracy.

5. **Domain-Specific Pruning Strategies**: Developing pruning methodologies that account for the unique characteristics and importance of clinical domain features is necessary to maintain the efficacy of compressed models in medical applications. 