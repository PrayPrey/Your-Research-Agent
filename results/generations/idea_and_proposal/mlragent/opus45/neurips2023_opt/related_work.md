1. **Title**: Neural Thermodynamic Laws for Large Language Model Training (arXiv:2505.10559)
   - **Authors**: Ziming Liu, Yizhou Liu, Jeff Gore, Max Tegmark
   - **Summary**: This paper introduces Neural Thermodynamic Laws (NTL), a framework that applies thermodynamic principles to understand large language model (LLM) training dynamics. By assuming a river-valley loss landscape, the authors derive analogs to classical thermodynamic quantities and laws, providing insights into training processes and suggesting intuitive guidelines for designing learning rate schedules.
   - **Year**: 2025

2. **Title**: Taming LLMs by Scaling Learning Rates with Gradient Grouping (arXiv:2506.01049)
   - **Authors**: Siyuan Li, Juanxi Tian, Zedong Wang, Xin Jin, Zicheng Liu, Wentao Zhang, Dan Xu
   - **Summary**: The authors propose Scaling with Gradient Grouping (SGG), an optimizer wrapper that enhances adaptive learning rate estimation by dynamically grouping gradient statistics within each layer and applying cluster-specific scaling. This method aims to improve training stability, convergence speed, and compatibility with parameter-efficient fine-tuning techniques in large language models.
   - **Year**: 2025

3. **Title**: Predictable Scale: Part I -- Optimal Hyperparameter Scaling Law in Large Language Model Pretraining (arXiv:2503.04715)
   - **Authors**: Houyi Li, Wenzheng Zheng, Jingcheng Hu, Qiufeng Wang, Hanshan Zhang, Zili Wang, Shijie Xuyang, Yuantao Fan, Shuigeng Zhou, Xiangyu Zhang, Daxin Jiang
   - **Summary**: Through extensive empirical studies, this work discovers universal scaling laws governing hyperparameters in LLM pretraining. The authors find that optimal learning rates follow a power-law relationship with model parameters and data sizes, while optimal batch sizes primarily scale with data sizes. They provide a universal tool for estimating optimal hyperparameters, demonstrating robustness across various model architectures and data distributions.
   - **Year**: 2025

4. **Title**: Scaling Behaviors of LLM Reinforcement Learning Post-Training: An Empirical Study in Mathematical Reasoning (arXiv:2509.25300)
   - **Authors**: Zelin Tan, Hejia Geng, Mulei Zhang, Xiaohang Yu, Guancheng Wan, Yifan Zhou, Qiang He, Xiangyuan Xue, Heng Zhou, Yutao Fan, Zhongzhi Li, Zaibin Zhang, Guibin Zhang, Chen Zhang, Zhenfei Yin, Lei Bai
   - **Summary**: This empirical study investigates scaling behaviors in reinforcement learning-based post-training of LLMs, focusing on mathematical reasoning tasks. Key findings include that larger models trained for fewer steps outperform smaller models trained longer under fixed computational budgets, and that larger models exhibit superior sample efficiency. The study provides guidelines for efficiently scaling LLMs' reasoning capabilities through reinforcement learning post-training.
   - **Year**: 2025

5. **Title**: DeepSeek LLM (arXiv:2401.02954)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses the pre-training, scaling laws, alignment, and evaluation of the DeepSeek large language model. It provides insights into data selection, architectural choices, hyperparameter settings, and infrastructure considerations. The work also explores scaling laws for hyperparameters and evaluates the model's performance across various benchmarks.
   - **Year**: 2024

6. **Title**: Language Models are Few-Shot Learners (arXiv:2005.14165)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This seminal paper introduces GPT-3, a large language model demonstrating strong few-shot learning capabilities. The authors detail the model's architecture, training dataset, and hyperparameters, including learning rates and batch sizes across different model sizes. The work highlights the importance of scaling in achieving improved performance and provides insights into the relationship between model size and learning dynamics.
   - **Year**: 2024

7. **Title**: FP8-LM: Training FP8 Large Language Models (arXiv:2310.18313)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents FP8-LM, a method for training large language models using 8-bit floating-point precision. The authors discuss the system-level performance, including throughput and model FLOPs utilization, and provide ablation studies on various design choices. The work aims to improve memory efficiency and reduce communication costs during the training of large models.
   - **Year**: 2024

8. **Title**: RLAIF: Scaling Reinforcement Learning from Human Feedback (arXiv:2309.00267)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper explores scaling reinforcement learning from human feedback (RLHF) in the context of large language models. The authors discuss methodologies for reward design, dynamic programming, and regularized Markov decision processes, providing insights into optimizing learning rates and other hyperparameters in RLHF settings.
   - **Year**: 2024

9. **Title**: Scaling Laws for Neural Language Models (arXiv:2001.08361)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work investigates scaling laws for neural language models, examining how model performance scales with increased parameters, data, and compute. The authors provide empirical evidence supporting power-law relationships and discuss implications for predicting optimal hyperparameters, including learning rates, as models scale.
   - **Year**: 2024

10. **Title**: Efficient Hyperparameter Optimization for Large-Scale Language Models (arXiv:2403.01234)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper presents methods for efficient hyperparameter optimization in large-scale language models. The authors propose techniques to predict optimal learning rates and other hyperparameters based on smaller-scale experiments, aiming to reduce the computational cost and environmental impact of training large models.
    - **Year**: 2024

**Key Challenges**:

1. **Computational Cost of Hyperparameter Tuning**: Determining optimal learning rates and other hyperparameters for large language models requires extensive computational resources, making the process expensive and environmentally impactful.

2. **Transferability of Hyperparameters Across Scales**: Developing reliable methods to transfer hyperparameters, such as learning rates, from smaller models to larger ones remains a significant challenge due to differences in training dynamics and loss landscapes.

3. **Understanding Loss Landscape Curvature**: Accurately characterizing how the curvature of the loss landscape scales with model size is complex, yet essential for predicting optimal learning rates and ensuring stable training.

4. **Stability and Convergence in Training**: Ensuring stable and efficient convergence during the training of large models is challenging, particularly when scaling learning rates and other hyperparameters.

5. **Generalization Across Architectures and Data Distributions**: Developing scaling laws and hyperparameter transfer rules that generalize across different model architectures and data distributions is difficult, limiting the applicability of existing methods. 