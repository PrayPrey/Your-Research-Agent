1. **Title**: EvoSLD: Automated Neural Scaling Law Discovery With Large Language Models (arXiv:2507.21184)
   - **Authors**: Haowei Lin, Xiangyu Wang, Jianzhu Ma, Yitao Liang
   - **Summary**: This paper introduces EvoSLD, an automated framework that employs evolutionary algorithms guided by large language models to discover scaling laws in neural networks. EvoSLD identifies functional relationships between model performance and variables like size and data, achieving superior accuracy and interpretability compared to traditional methods.
   - **Year**: 2025

2. **Title**: Predictable Scale: Part I -- Optimal Hyperparameter Scaling Law in Large Language Model Pretraining (arXiv:2503.04715)
   - **Authors**: Houyi Li, Wenzheng Zheng, Jingcheng Hu, Qiufeng Wang, Hanshan Zhang, Zili Wang, Shijie Xuyang, Yuantao Fan, Shuigeng Zhou, Xiangyu Zhang, Daxin Jiang
   - **Summary**: The authors present universal scaling laws for hyperparameters in large language model pretraining, revealing power-law relationships between optimal learning rates, model parameters, and data sizes. They provide a tool that estimates optimal hyperparameters, closely matching globally optimal performance, and demonstrate robustness across various model structures and data distributions.
   - **Year**: 2025

3. **Title**: A Latent Variable Framework for Scaling Laws in Large Language Models (arXiv:2512.06553)
   - **Authors**: Peiyao Cai, Chengyu Cui, Felipe Maia Polo, Seamus Somerstep, Leshem Choshen, Mikhail Yurochkin, Moulinath Banerjee, Yuekai Sun, Kean Ming Tan, Gongjun Xu
   - **Summary**: This work proposes a statistical framework based on latent variable modeling to understand scaling laws in large language models. By associating each model family with latent variables capturing underlying features, the framework explains performance variations across different architectures and benchmarks, offering a unified approach to model scaling behavior.
   - **Year**: 2025

4. **Title**: Scaling Behaviors of LLM Reinforcement Learning Post-Training: An Empirical Study in Mathematical Reasoning (arXiv:2509.25300)
   - **Authors**: Zelin Tan, Hejia Geng, Mulei Zhang, Xiaohang Yu, Guancheng Wan, Yifan Zhou, Qiang He, Xiangyuan Xue, Heng Zhou, Yutao Fan, Zhongzhi Li, Zaibin Zhang, Guibin Zhang, Chen Zhang, Zhenfei Yin, Lei Bai
   - **Summary**: The authors conduct an empirical study on the scaling behaviors of large language models during reinforcement learning post-training, focusing on mathematical reasoning tasks. They find that larger models trained for fewer steps outperform smaller models trained longer, and that data reuse is effective in data-constrained scenarios, providing insights into efficient scaling strategies.
   - **Year**: 2025

5. **Title**: DeepSeek LLM (arXiv:2401.02954)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses the pre-training, scaling laws, alignment, and evaluation of the DeepSeek large language model. It provides insights into the model's architecture, hyperparameters, and performance across various benchmarks, contributing to the understanding of scaling behaviors in large language models.
   - **Year**: 2024

6. **Title**: RLAIF: Scaling Reinforcement Learning from Human Feedback (arXiv:2309.00267)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The paper explores the scaling of reinforcement learning from human feedback in large language models. It examines the challenges and methodologies for effectively incorporating human feedback at scale, aiming to improve model alignment and performance in complex tasks.
   - **Year**: 2024

7. **Title**: A Large Batch Optimizer Reality Check (arXiv:2102.06356)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study evaluates the effectiveness of large batch optimizers in training deep neural networks. It provides a comprehensive analysis of various optimization strategies, highlighting the challenges and trade-offs associated with scaling batch sizes during training.
   - **Year**: 2024

8. **Title**: Revisiting OPRO: The Limitations of Small-Scale LLMs as Optimizers (arXiv:2405.10276)
   - **Authors**: Tuo Zhang, Jinyue Yuan, Salman Avestimehr
   - **Summary**: The authors revisit the Optimization by PROmpting (OPRO) approach, assessing its effectiveness when applied to small-scale large language models. They find that limited inference capabilities constrain optimization performance, suggesting that OPRO's benefits are diminished in smaller models.
   - **Year**: 2024

9. **Title**: HLAT: High-quality Large Language Model Pre-trained on AWS Trainium (arXiv:2404.10630)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents HLAT, a high-quality large language model pre-trained on AWS Trainium. It details the training process, infrastructure, and performance evaluations, contributing to the understanding of efficient large-scale model training on specialized hardware.
   - **Year**: 2024

**Key Challenges**:

1. **Transferability of Hyperparameters**: Developing reliable methods to predict optimal hyperparameters for large-scale models based on small-scale experiments remains challenging due to differences in model dynamics and training behaviors across scales.

2. **Computational Resource Constraints**: Conducting extensive hyperparameter searches and training large models require significant computational resources, posing barriers to research accessibility and increasing environmental impact.

3. **Model Performance Variability**: Ensuring consistent performance improvements when scaling models is difficult, as factors like data quality, model architecture, and training procedures can lead to variability in outcomes.

4. **Data Efficiency**: Achieving high performance with limited data is a persistent challenge, necessitating strategies for effective data utilization and augmentation to train large models efficiently.

5. **Optimization Landscape Complexity**: The non-convex and high-dimensional nature of optimization landscapes in large models complicates the development of effective learning rate schedules and optimization strategies. 