1. **Title**: Bridging Critical Gaps in Convergent Learning: How Representational Alignment Evolves Across Layers, Training, and Distribution Shifts (arXiv:2502.18710)
   - **Authors**: Chaitanya Kapoor, Sudhanshu Srivastava, Meenakshi Khosla
   - **Summary**: This paper investigates the evolution of representational alignment in neural networks, focusing on how alignment develops across different layers, during training, and under distribution shifts. The authors compare various alignment metrics and find that significant convergence occurs early in training, suggesting that shared input statistics and architectural biases drive alignment rather than task-specific learning.
   - **Year**: 2025

2. **Title**: Representational Alignment Across Model Layers and Brain Regions with Hierarchical Optimal Transport (arXiv:2510.01706)
   - **Authors**: Shaan Shah, Meenakshi Khosla
   - **Summary**: This study introduces Hierarchical Optimal Transport (HOT), a framework for aligning representations between neural network layers and brain regions. HOT jointly infers soft, globally consistent layer-to-layer couplings and neuron-level transport plans, enabling more interpretable comparisons between representations, especially when networks differ in architecture or depth.
   - **Year**: 2025

3. **Title**: Neural Representational Consistency Emerges from Probabilistic Neural-Behavioral Representation Alignment (arXiv:2505.04331)
   - **Authors**: Yu Zhu, Chunfeng Song, Wanli Ouyang, Shan Yu, Tiejun Huang
   - **Summary**: The authors present the Probabilistic Neural-Behavioral Representation Alignment (PNBA) framework, which leverages probabilistic modeling to address variability across trials, sessions, and subjects. PNBA reveals robust preserved neural representations in primate motor cortex and mouse visual cortex, providing insights into neural coding and enabling zero-shot behavior decoding.
   - **Year**: 2025

4. **Title**: Towards Fair Graph Neural Networks via Graph Counterfactual
   - **Authors**: [Authors not specified]
   - **Summary**: This paper addresses fairness in Graph Neural Networks (GNNs) by introducing a causal framework that utilizes graph counterfactuals. The approach aims to disentangle content and environment features to mitigate bias, providing a method to design fair GNN classifiers.
   - **Year**: 2023

5. **Title**: Understanding Neural Networks through Representation Erasure
   - **Authors**: Jiwei Li, Will Monroe, Dan Jurafsky
   - **Summary**: The authors propose a methodology to interpret neural network decisions by analyzing the effects of erasing various parts of the representation, such as input word-vector dimensions and hidden units. This approach offers insights into the importance of different representations and aids in error analysis.
   - **Year**: 2023

6. **Title**: Visualizing and Understanding Neural Models in NLP
   - **Authors**: Jiwei Li, Xinlei Chen, Eduard Hovy, Dan Jurafsky
   - **Summary**: This work explores strategies for visualizing compositionality in neural models for NLP, including plotting unit values and measuring a unit's salience. The methods provide insights into how neural models achieve meaning composition and interpretability.
   - **Year**: 2023

7. **Title**: Improving Compositionality of Neural Networks by Decoding Representations to Inputs
   - **Authors**: Mike Wu, Noah Goodman, Stefano Ermon
   - **Summary**: The authors propose Decodable Neural Networks (DecNN), which jointly train a classifier with a generative model to map activations back to inputs. This design enables compositionality in neural networks, allowing for applications such as out-of-distribution detection and adversarial example detection.
   - **Year**: 2023

8. **Title**: A Causal Framework for Explaining the Predictions of Black-Box Sequence-to-Sequence Models
   - **Authors**: David Alvarez-Melis, Tommi S. Jaakkola
   - **Summary**: This paper introduces a method to interpret predictions of black-box sequence-to-sequence models by identifying sets of input and output tokens that are causally related. The approach involves analyzing perturbed inputs to infer causal dependencies, providing explanations for model predictions.
   - **Year**: 2023

**Key Challenges**:

1. **Metric Limitations**: Existing alignment metrics may not fully capture the complexities of representational alignment, leading to incomplete or misleading assessments.

2. **Early Convergence**: Alignment occurring early in training suggests that factors other than task-specific learning, such as shared input statistics and architectural biases, drive alignment.

3. **Distribution Shifts**: Representational alignment can be affected by changes in input distributions, with out-of-distribution inputs amplifying differences in later layers.

4. **Architectural Differences**: Comparing representations across models with different architectures or depths poses challenges in establishing meaningful correspondences.

5. **Interpretability**: Understanding and controlling representational alignment is crucial for interpretability, yet current methods may lack the ability to systematically manipulate alignment. 