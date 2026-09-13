1. **Title**: A Scalable Measure of Loss Landscape Curvature for Analyzing the Training Dynamics of LLMs (arXiv:2601.16979)
   - **Authors**: Dayal Singh Kalra, Jean-Christophe Gagnon-Audet, Andrey Gromov, Ishita Mediratta, Kelvin Niu, Alexander H Miller, Michael Shvartsman
   - **Summary**: This paper introduces a computationally efficient measure called critical sharpness to analyze the curvature evolution of the loss landscape in large language models (LLMs). The authors demonstrate that critical sharpness captures key Hessian sharpness phenomena, such as progressive sharpening and the Edge of Stability, up to 7 billion parameters. They also propose relative critical sharpness to study transitions from pre-training to fine-tuning, providing a practical tool for diagnosing curvature dynamics and informing data composition choices at scale.
   - **Year**: 2026

2. **Title**: Implicit Bias Produces Neural Scaling Laws in Learning Curves, from Perceptrons to Deep Networks (arXiv:2505.13230)
   - **Authors**: Francesco D'Amico, Dario Bocchi, Matteo Negri
   - **Summary**: The authors uncover dynamical scaling laws governing performance evolution during training by analyzing spectral complexity norms. They provide a mechanistic explanation of generalization emergence, consistent across various architectures and datasets, and offer analytical support using a solvable model.
   - **Year**: 2025

3. **Title**: A Multi-Power Law for Loss Curve Prediction Across Learning Rate Schedules (arXiv:2503.12811)
   - **Authors**: Kairong Luo, Haodong Wen, Shengding Hu, Zhenbo Sun, Zhiyuan Liu, Maosong Sun, Kaifeng Lyu, Wenguang Chen
   - **Summary**: This paper presents an empirical law describing how the pretraining loss of large language models evolves under different learning rate schedules. The proposed multi-power law combines a power law based on the sum of learning rates and additional power laws to account for loss reduction effects induced by learning rate decay. The authors validate this law across various model sizes and architectures, demonstrating its accuracy in predicting loss curves for unseen schedules and its utility in designing efficient learning rate schedules.
   - **Year**: 2025

4. **Title**: Robust Layerwise Scaling Rules by Proper Weight Decay Tuning (arXiv:2510.15262)
   - **Authors**: Zhiyuan Fan, Yifeng Liu, Qingyue Zhao, Angela Yuan, Quanquan Gu
   - **Summary**: The authors introduce a weight-decay scaling rule for AdamW optimizer that preserves sublayer gain across model widths. They observe that the top singular value of each matrix parameter scales with the square root of the learning rate divided by weight decay, and propose a weight-decay scaling rule proportional to the square root of the width scaling factor. This approach enables zero-shot transfer of both learning rate and weight decay from proxy to target widths, removing the need for per-width hyperparameter sweeps.
   - **Year**: 2025

5. **Title**: Language Models are Few-Shot Learners (arXiv:2005.14165)
   - **Authors**: Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D. Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, Dario Amodei
   - **Summary**: This seminal paper introduces GPT-3, a 175-billion parameter language model, and demonstrates its few-shot learning capabilities. The authors provide detailed information on model sizes, architectures, and learning hyperparameters, including batch sizes and learning rates, offering valuable insights into the scaling of language models and their training dynamics.
   - **Year**: 2020

6. **Title**: Compute Trends Across Three Eras of Machine Learning (arXiv:2202.05924)
   - **Authors**: Jaime Sevilla, Lennart Heim, Anson Ho, Tamay Besiroglu, Marius Hobbhahn, Pablo Villalobos
   - **Summary**: The authors analyze the growth of compute requirements in machine learning, identifying three distinct eras: the Pre Deep Learning Era, the Deep Learning Era, and the Large-Scale Era. They provide estimates of doubling times for training compute during each era, highlighting the rapid increase in computational demands and its implications for model scaling and optimization.
   - **Year**: 2022

7. **Title**: DeepSeek LLM (arXiv:2401.02954)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses the development of DeepSeek LLM models and explores scaling laws for hyperparameters. The authors establish empirical frameworks for determining optimal hyperparameters and analyze the impact of data quality on model/data scaling strategies, providing insights into efficient training of large-scale language models.
   - **Year**: 2024

8. **Title**: A Simple Framework for Contrastive Learning of Visual Representations (arXiv:2002.05709)
   - **Authors**: Ting Chen, Simon Kornblith, Mohammad Norouzi, Geoffrey Hinton
   - **Summary**: The authors present SimCLR, a framework for contrastive learning of visual representations. They investigate the effects of batch size and training steps on model performance, providing insights into the relationship between learning rate scaling and batch size, which is relevant for understanding optimization dynamics in large-scale models.
   - **Year**: 2020

9. **Title**: May 21, 2024 (arXiv:2405.10957)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper examines the loss landscape of neural networks, focusing on the curvature along Hessian directions. The authors demonstrate that optimizing along dominant negative curvature directions can lead to improved training loss values, highlighting the importance of curvature information in guiding optimization strategies.
   - **Year**: 2024

10. **Title**: Scaling Laws for Neural Language Models (arXiv:2001.08361)
    - **Authors**: Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, Dario Amodei
    - **Summary**: The authors investigate how the performance of neural language models scales with model size, dataset size, and the amount of compute used for training. They identify empirical scaling laws that predict performance improvements, providing a framework for understanding and optimizing the scaling of language models.
    - **Year**: 2020

**Key Challenges**:

1. **Computational Cost of Curvature Measurement**: Accurately measuring loss landscape curvature, such as Hessian sharpness, is computationally intensive, especially for large-scale models, making it impractical for routine use in hyperparameter tuning.

2. **Transferability of Hyperparameters Across Scales**: Developing methods to predict optimal hyperparameters for large models based on small-scale experiments is challenging due to differences in training dynamics and loss landscapes across model sizes.

3. **Data Quality and Scaling Strategies**: The quality of training data significantly influences the effectiveness of scaling laws and hyperparameter optimization, necessitating robust methods to assess and incorporate data quality into scaling strategies.

4. **Balancing Learning Rate and Weight Decay**: Properly tuning learning rate and weight decay parameters to maintain stable training and optimal performance across different model sizes requires a nuanced understanding of their interplay and impact on training dynamics.

5. **Environmental Impact of Large-Scale Training**: The increasing computational demands for training large models raise concerns about energy consumption and environmental impact, highlighting the need for more efficient training methods and scaling strategies. 