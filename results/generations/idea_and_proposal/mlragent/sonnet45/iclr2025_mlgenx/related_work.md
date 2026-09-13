1. **Title**: Interpretable Neural ODEs for Gene Regulatory Network Discovery under Perturbations (arXiv:2501.02409)
   - **Authors**: Zaikang Lin, Sei Chang, Aaron Zweig, Minseo Kang, Elham Azizi, David A. Knowles
   - **Summary**: This paper introduces PerturbODE, a framework that employs neural ordinary differential equations to model cell state trajectories under perturbations, facilitating the inference of causal gene regulatory networks. It demonstrates improved trajectory prediction and network inference on both simulated and real over-expression datasets.
   - **Year**: 2025

2. **Title**: DiscoGen: Learning to Discover Gene Regulatory Networks (arXiv:2304.05823)
   - **Authors**: Nan Rosemary Ke, Sara-Jane Dunn, Jorg Bornschein, Silvia Chiappa, Melanie Rey, Jean-Baptiste Lespiau, Albin Cassirer, Jane Wang, Theophane Weber, David Barrett, Matthew Botvinick, Anirudh Goyal, Mike Mozer, Danilo Rezende
   - **Summary**: DiscoGen presents a neural network-based method for inferring gene regulatory networks that can denoise gene expression data and handle interventional data. The model outperforms existing causal discovery methods, effectively identifying causal relationships within large-scale gene regulatory networks.
   - **Year**: 2023

3. **Title**: Targeted Cause Discovery with Data-Driven Learning (arXiv:2408.16218)
   - **Authors**: Jang-Hyun Kim, Claudia Skok Gibbs, Sangdoo Yun, Hyun Oh Song, Kyunghyun Cho
   - **Summary**: This study proposes a machine learning approach to infer causal variables of a target variable from observations, identifying both direct and indirect causes within a system. The method demonstrates effectiveness in identifying causal relationships within large-scale gene regulatory networks, outperforming existing causal discovery methods.
   - **Year**: 2024

4. **Title**: Efficient Data Selection for Training Genomic Perturbation Models (arXiv:2503.14571)
   - **Authors**: George Panagopoulos, Johannes Lutzeyer, Sofiane Ennadir, Michalis Vazirgiannis, Jun Pang
   - **Summary**: The paper introduces graph-based one-shot data selection methods for training gene expression models, aiming to mitigate the risks associated with poor model initialization in active learning. The proposed methods achieve comparable accuracy to state-of-the-art active learning approaches while alleviating initialization biases.
   - **Year**: 2025

5. **Title**: Towards Fair Graph Neural Networks via Graph Counterfactual (arXiv:2307.04937)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work addresses fairness in graph neural networks by introducing a graph counterfactual approach. It evaluates node classification performance and group fairness across real-world datasets, proposing methods to achieve counterfactual fairness in graph-based models.
   - **Year**: 2023

6. **Title**: Automatic Gradient Descent: Deep Learning without Hyperparameters (arXiv:2304.05187)
   - **Authors**: Jeremy Bernstein, Chris Mingard, Kevin Huang, Navid Azizan, Yisong Yue
   - **Summary**: The authors present a framework for deriving optimization algorithms that explicitly leverage neural architecture, resulting in automatic gradient descent—a first-order optimizer without hyperparameters. This method trains both fully-connected and convolutional networks effectively, offering a theoretical foundation for architecture-dependent optimizers.
   - **Year**: 2023

7. **Title**: LSCALE: Latent Space Clustering-Based Active Learning for Node Classification (arXiv:2012.07065)
   - **Authors**: Juncheng Liu, Yiwei Wang, Bryan Hooi, Renchi Yang, Xiaokui Xiao
   - **Summary**: LSCALE introduces a latent space clustering-based active learning framework for node classification on attributed graphs. By utilizing both labeled and unlabeled nodes, the method selects informative nodes for labeling, significantly outperforming state-of-the-art approaches in various datasets.
   - **Year**: 2023

8. **Title**: Interpretability Beyond Feature Attribution: Testing with Concept Activation Vectors (TCAV) (arXiv:1711.11279)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: TCAV offers a method to quantify a model's sensitivity to high-level concepts, providing insights into neural network decisions beyond feature attribution. It enables users to interpret model predictions in terms of human-understandable concepts without retraining or modifying the network.
   - **Year**: 2023

9. **Title**: Comprehensive Evaluation of Deep and Graph Learning on Drug-Drug Interactions Prediction (arXiv:2306.05257)
   - **Authors**: Xuan Lin, Lichang Dai, Yafang Zhou, Zu-Guo Yu, Wen Zhang, Jian-Yu Shi, Dong-Sheng Cao, Li Zeng, Haowen Chen, Bosheng Song, Philip S. Yu, Xiangxiang Zeng
   - **Summary**: This review summarizes deep and graph learning methods for predicting drug-drug interactions, discussing molecular representations and graph neural network models. It presents comparative experiments, highlighting advantages and challenges, and suggests future directions for accelerating DDI prediction.
   - **Year**: 2023

10. **Title**: Causal Gene Circuit Discovery via Differentiable Perturbation Masks and Counterfactual Reasoning
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper proposes a neural causal discovery framework integrating differentiable perturbation masks and counterfactual prediction modules. It aims to improve causal gene network recovery with fewer perturbation experiments, validated on benchmark datasets, facilitating efficient experimental design and robust target identification.
    - **Year**: [Year not specified in the provided excerpt]

**Key Challenges**:

1. **Distinguishing Correlation from Causation**: Accurately inferring causal relationships from observational genomics data remains challenging due to the complex interplay of gene regulatory networks and the prevalence of confounding factors.

2. **Integration of Observational and Perturbational Data**: Combining observational data with sparse perturbational experiments to construct comprehensive causal models is difficult, requiring sophisticated methods to handle data heterogeneity and sparsity.

3. **Scalability and Computational Efficiency**: Developing models that can efficiently process large-scale genomic datasets while maintaining accuracy and interpretability poses significant computational challenges.

4. **Active Learning for Experimental Design**: Designing active learning strategies that effectively prioritize perturbation experiments to maximize information gain and minimize experimental costs is a complex task.

5. **Validation and Generalization**: Ensuring that causal discovery methods generalize well across different biological contexts and are validated against independent datasets is essential for their applicability in real-world scenarios. 