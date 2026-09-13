1. **Title**: Efficient Data Selection for Training Genomic Perturbation Models (arXiv:2503.14571)
   - **Authors**: George Panagopoulos, Johannes Lutzeyer, Sofiane Ennadir, Michalis Vazirgiannis, Jun Pang
   - **Summary**: This paper addresses the challenge of selecting informative gene perturbations for training gene expression models. The authors propose graph-based one-shot data selection methods that predefine gene perturbations before training, mitigating initialization bias in active learning. Their approach optimizes criteria over the input graph using submodular maximization, achieving comparable accuracy to state-of-the-art active learning methods while reducing risks associated with poor model initialization.
   - **Year**: 2025

2. **Title**: ALLSH: Active Learning Guided by Local Sensitivity and Hardness (arXiv:2205.04980)
   - **Authors**: Shujian Zhang, Chengyue Gong, Xingchao Liu, Pengcheng He, Weizhu Chen, Mingyuan Zhou
   - **Summary**: The authors introduce an active learning strategy that selects data points based on local sensitivity and hardness. By generating data copies through local perturbations and selecting samples whose predictive likelihoods diverge most from their copies, the method effectively identifies informative data points. This approach demonstrates consistent improvements over common active learning strategies across various classification tasks.
   - **Year**: 2022

3. **Title**: Poisson Reweighted Laplacian Uncertainty Sampling for Graph-based Active Learning (arXiv:2210.15786)
   - **Authors**: Kevin Miller, Jeff Calder
   - **Summary**: This paper presents a graph-based active learning method that utilizes Poisson ReWeighted Laplace Learning (PWLL) to measure uncertainty in classifiers. The authors introduce a diagonal perturbation in PWLL, resulting in exponential localization of solutions and effectively balancing exploration and exploitation in active learning. The method is rigorously analyzed and validated on various graph-based image classification problems.
   - **Year**: 2022

4. **Title**: Bayesian Semi-Supervised Learning for Uncertainty-Calibrated Prediction of Molecular Properties and Active Learning (arXiv:1902.00925)
   - **Authors**: Yao Zhang, Alpha A. Lee
   - **Summary**: The authors propose a Bayesian semi-supervised graph convolutional neural network for predicting molecular properties with uncertainty quantification. This approach enables active learning by suggesting informative training sets and provides reliable uncertainty estimates, even with biased training data. The study highlights the potential of Bayesian deep learning in chemistry applications.
   - **Year**: 2019

5. **Title**: Divide-and-Conquer Predictive Coding: A Structured Bayesian Inference Algorithm (arXiv:2408.05834)
   - **Authors**: Eli Sennesh, Hao Wu, Tommaso Salvatori
   - **Summary**: This paper introduces a novel predictive coding algorithm for structured generative models, termed divide-and-conquer predictive coding (DCPC). DCPC respects the correlation structure of the generative model and performs maximum-likelihood updates of model parameters without sacrificing biological plausibility. Empirically, DCPC achieves superior numerical performance compared to competing algorithms and provides accurate inference in various problems not previously addressed with predictive coding.
   - **Year**: 2024

6. **Title**: Meta-Learning to Calibrate Gaussian Processes with Deep Kernels for Regression Uncertainty Estimation (arXiv:2312.07952)
   - **Authors**: Tomoharu Iwata, Atsutoshi Kumagai
   - **Summary**: The authors propose a meta-learning method for calibrating deep kernel Gaussian Processes to improve regression uncertainty estimation with limited training data. The approach meta-learns how to calibrate uncertainty using data from various tasks by minimizing the test expected calibration error, enabling effective uncertainty estimation in few-shot settings.
   - **Year**: 2023

7. **Title**: AutoML: A Survey of the State-of-the-Art (arXiv:1908.00709v3)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This survey provides a comprehensive overview of the state-of-the-art in Automated Machine Learning (AutoML). It discusses various approaches, including Bayesian optimization, reinforcement learning, and gradient-based methods, highlighting their applications and effectiveness in automating the machine learning pipeline.
   - **Year**: 2019

8. **Title**: A Survey of Active Learning for Natural Language Processing (arXiv:2210.10109)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This survey examines active learning strategies in the context of natural language processing (NLP). It reviews various methods, including uncertainty-based query strategies, and discusses their effectiveness in reducing annotation costs while maintaining model performance.
   - **Year**: 2022

**Key Challenges:**

1. **High Dimensionality and Complexity of Genomic Data**: Genomic datasets are often high-dimensional and complex, making it challenging to develop models that can effectively capture the intricate relationships between genes and their functions.

2. **Uncertainty Quantification**: Accurately quantifying uncertainty in model predictions is crucial for active learning strategies. However, existing methods may struggle to provide reliable uncertainty estimates, especially in the context of limited or biased training data.

3. **Efficient Experimental Design**: Designing efficient experiments that prioritize informative gene perturbations is essential to reduce costs and accelerate discoveries. Developing strategies that balance exploration and exploitation remains a significant challenge.

4. **Integration of Multimodal Data**: Combining various types of omics data (e.g., transcriptomics, proteomics) to create comprehensive models poses challenges in data integration and interpretation.

5. **Scalability of Active Learning Methods**: Ensuring that active learning methods can scale effectively to large genomic datasets without compromising performance or computational efficiency is a critical challenge in the field. 