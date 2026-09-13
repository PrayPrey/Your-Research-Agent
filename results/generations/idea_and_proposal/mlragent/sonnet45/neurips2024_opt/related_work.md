1. **Title**: Predictable Scale: Part I -- Optimal Hyperparameter Scaling Law in Large Language Model Pretraining (arXiv:2503.04715)
   - **Authors**: Houyi Li, Wenzheng Zheng, Jingcheng Hu, Qiufeng Wang, Hanshan Zhang, Zili Wang, Shijie Xuyang, Yuantao Fan, Shuigeng Zhou, Xiangyu Zhang, Daxin Jiang
   - **Summary**: This paper presents universal scaling laws for hyperparameters in large language model (LLM) pretraining. Through extensive empirical studies, the authors discover that optimal learning rates follow a power-law relationship with model parameters and data sizes, while optimal batch sizes scale primarily with data sizes. They provide a plug-and-play tool for estimating optimal hyperparameters, achieving performance within 0.09% of the global optimum found via exhaustive search.
   - **Year**: 2025

2. **Title**: Optimal Scaling Needs Optimal Norm (arXiv:2510.03871)
   - **Authors**: Oleg Filatov, Jiangtao Wang, Jan Ebert, Stefan Kesselheim
   - **Summary**: The authors investigate hyperparameter scaling across model and dataset sizes, identifying the operator norm of the output layer as a key invariant. They find that the optimal learning rate and batch size pair consistently maintain the same operator norm value, termed "norm transfer." The study provides practical insights into norm-guided optimal scaling and introduces the Distributed Scion (Disco) implementation to support research on LLM training dynamics.
   - **Year**: 2025

3. **Title**: Weight Decay May Matter More Than μP for Learning Rate Transfer in Practice (arXiv:2510.19093)
   - **Authors**: Atli Kosson, Jeremy Welborn, Yang Liu, Martin Jaggi, Xi Chen
   - **Summary**: This study examines the effectiveness of the Maximal Update Parameterization (μP) in transferring optimal learning rates from small to large neural networks. The authors find that μP's assumptions hold only briefly at the start of training. They suggest that weight decay, rather than μP, plays a crucial role in stabilizing update dynamics across model widths, facilitating learning rate transfer.
   - **Year**: 2025

4. **Title**: Scaling Laws for Hyperparameter Optimization (arXiv:2302.00441)
   - **Authors**: Arlind Kadra, Maciej Janowski, Martin Wistuba, Josif Grabocka
   - **Summary**: The authors propose Deep Power Laws (DPL), an ensemble of neural network models conditioned to yield predictions following a power-law scaling pattern. DPL dynamically decides which configurations to pause and train incrementally using gray-box evaluations. The method outperforms seven state-of-the-art competitors across benchmarks related to tabular, image, and NLP datasets, achieving the best any-time results.
   - **Year**: 2023

5. **Title**: Hyperparameter Transfer Enables Consistent Gains of Matrix-Preconditioned Optimizers Across Scales (arXiv:2512.05620)
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: This paper investigates scaling matrix-preconditioned optimizers (Shampoo, Muon, SOAP) with model width and depth by deriving hyperparameter transfer rules under the Maximal Update Parameterization (μP). The authors find that μP improves learning-rate transfer across widths but note that finite-width effects can skew optimal scales unless mitigated by blocking and explicit spectral normalization. They provide practical guidelines for achieving consistent gains with these optimizers.
   - **Year**: 2025

6. **Title**: Scaling Exponents Across Parameterizations and Optimizers (arXiv:2407.05872)
   - **Authors**: Katie Everett, Lechao Xiao, Mitchell Wortsman, Alexander A. Alemi, Roman Novak, Peter J. Liu, Izzeddin Gur, Jascha Sohl-Dickstein, Leslie Pack Kaelbling, Jaehoon Lee, Jeffrey Pennington
   - **Summary**: The authors conduct an extensive empirical investigation into the scaling of models from small to large widths, considering various parameterizations and optimizers. They propose a new perspective on parameterization by examining assumptions about the alignment between parameters and data, deriving new theoretical results under broader assumptions. The study includes tens of thousands of models trained with different combinations of optimizers, parameterizations, learning rates, and model sizes up to 27B parameters.
   - **Year**: 2024

7. **Title**: Tune As You Scale: Hyperparameter Optimization for Compute Efficient Training (arXiv:2306.08055)
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: This paper introduces Cost-Aware Pareto Region Bayesian Search (CARBS), a Bayesian optimization algorithm that performs local search around the performance-cost Pareto frontier. CARBS effectively tunes large models by learning scaling relationships, automating much of the hyperparameter tuning process. The method demonstrates significant performance gains, including effectively solving the entire ProcGen benchmark by tuning a simple baseline.
   - **Year**: 2023

8. **Title**: Scaling Laws Refined: Learning Rate Optimization for Large Language Models
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: This study reveals that smaller learning rates are key to efficient training for large language models, offering a rule-of-thumb for transferring hyperparameters and improving overall performance. The research involves a large-scale empirical study investigating how the optimal learning rate changes with token horizon during LLM training.
   - **Year**: 2024

9. **Title**: MetaLR: Meta-Tuning of Learning Rates for Transfer Learning in Medical Imaging
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: The authors introduce MetaLR, a method that assigns adaptive learning rates for each layer to control their adaptation strength to downstream tasks. Unlike common meta-learning paradigms that focus on initializing model parameters, MetaLR focuses on learning learning rates instead of parameters. The method is designed to be efficient by learning layer-wise learning rates, ensuring scalability.
   - **Year**: 2023

10. **Title**: Scaling Laws for Every Hyperparameter via Cost-Aware HPO
    - **Authors**: Abraham J. Fetterman, Ellie Kitanidis, Joshua Albrecht, Zachary Polizzi, Bryden Fogelman, Maksis Knutins, Bartosz Wróblewski, James B. Simon, Kanjun Qiu
    - **Summary**: The authors introduce CARBS, a cost-aware hyperparameter optimizer that automatically reproduces scaling laws for large language models while discovering scaling laws for other hyperparameters. CARBS uses significantly less compute and is applicable to any deep learning problem, not just language models. The method demonstrates effectiveness in tuning models as they are scaled up, automating much of the hyperparameter tuning process.
    - **Year**: 2023

**Key Challenges:**

1. **Generalization Across Model Architectures**: Developing meta-transfer functions that generalize across diverse model architectures remains challenging due to varying dynamics and optimization landscapes.

2. **Optimizer-Specific Behaviors**: Capturing optimizer-specific behaviors in transfer functions is complex, as different optimizers may exhibit unique scaling properties and convergence characteristics.

3. **Computational Resource Constraints**: Training meta-datasets across multiple scales and hyperparameter configurations demands substantial computational resources, posing practical limitations.

4. **Robustness to Data Distribution Variations**: Ensuring that learned transfer functions remain robust across different data distributions is critical for their applicability in real-world scenarios.

5. **Balancing Exploration and Exploitation**: Efficiently exploring the hyperparameter space while exploiting known scaling laws to minimize computational costs requires careful algorithm design. 