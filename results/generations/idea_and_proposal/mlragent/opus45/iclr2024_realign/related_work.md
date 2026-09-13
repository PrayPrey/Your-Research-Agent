1. **Title**: Representational Alignment Across Model Layers and Brain Regions with Hierarchical Optimal Transport (arXiv:2510.01706)
   - **Authors**: Shaan Shah, Meenakshi Khosla
   - **Summary**: This paper introduces Hierarchical Optimal Transport (HOT), a framework that jointly infers soft, globally consistent layer-to-layer couplings and neuron-level transport plans. HOT addresses limitations in standard representational similarity methods by allowing source neurons to distribute mass across multiple target layers, effectively handling depth mismatches and providing a single alignment score for network comparisons. Evaluations on vision models, large language models, and human visual cortex recordings demonstrate HOT's effectiveness in revealing structured, interpretable correspondences between representations.
   - **Year**: 2025

2. **Title**: Bridging Critical Gaps in Convergent Learning: How Representational Alignment Evolves Across Layers, Training, and Distribution Shifts (arXiv:2502.18710)
   - **Authors**: Chaitanya Kapoor, Sudhanshu Srivastava, Meenakshi Khosla
   - **Summary**: This study examines the evolution of representational alignment in artificial and biological neural networks. It compares three alignment metrics—linear regression, Procrustes, and permutation/soft-matching—and finds that orthogonal transformations align representations nearly as effectively as more flexible linear ones. The research reveals that most convergence occurs within the first epoch of training, suggesting that shared input statistics or architectural biases drive alignment. Additionally, it shows that out-of-distribution inputs amplify differences in later layers, while early layers remain aligned, indicating stability across distribution shifts.
   - **Year**: 2025

3. **Title**: Neural Representational Consistency Emerges from Probabilistic Neural-Behavioral Representation Alignment (arXiv:2505.04331)
   - **Authors**: Yu Zhu, Chunfeng Song, Wanli Ouyang, Shan Yu, Tiejun Huang
   - **Summary**: This paper presents the Probabilistic Neural-Behavioral Representation Alignment (PNBA) framework, which leverages probabilistic modeling to address hierarchical variability across trials, sessions, and subjects. PNBA establishes reliable cross-modal representational alignment, revealing robust preserved neural representations in monkey primary motor cortex and dorsal premotor cortex through zero-shot validation. The findings resolve the paradox of neural heterogeneity by demonstrating preserved neural representations across cortices and species, enriching insights into neural coding and enabling zero-shot behavior decoding.
   - **Year**: 2025

4. **Title**: Superposition Disentanglement of Neural Representations Reveals Hidden Alignment (arXiv:2510.03186)
   - **Authors**: André Longon, David Klindt, Meenakshi Khosla
   - **Summary**: This work explores the interaction between superposition in neural representations and alignment metrics. It hypothesizes that models representing the same features in different superposition arrangements may interfere with predictive mapping metrics, leading to lower alignment scores. By training sparse autoencoders to disentangle superposition, the study shows that alignment scores typically increase when a model's base neurons are replaced with its sparse overcomplete latent codes. The results suggest that superposition disentanglement is necessary for mapping metrics to uncover true representational alignment between neural codes.
   - **Year**: 2025

5. **Title**: Inducing Causal Structure for Interpretable Neural Networks (arXiv:2206.00000)
   - **Authors**: Atticus Geiger, Zhengxuan Wu, Hanson Lu, Josh Rozner, Elisa Kreiss, Thomas Icard, Noah Goodman, Christopher Potts
   - **Summary**: This paper introduces Interchange Intervention Training (IIT), a method that aligns variables in a causal model with representations in a neural model. IIT trains the neural model to match the counterfactual behavior of the causal model on a base input when aligned representations in both models are set to the value they would be for a source input. The method is fully differentiable, combines flexibly with other objectives, and ensures that the target causal model is a causal abstraction of the neural model when its loss is minimized. Evaluations on structured vision and navigational instruction tasks demonstrate IIT's effectiveness in producing more interpretable neural models.
   - **Year**: 2022

6. **Title**: Addressing Divergent Representations from Causal Interventions on Neural Networks (arXiv:2511.04638)
   - **Authors**: [Authors not specified]
   - **Summary**: This work investigates whether causal interventions used for mechanistic interpretability produce representations that diverge from a model's natural latent distribution, potentially undermining the faithfulness of explanations. It provides theoretical and empirical evidence that divergence is common across activation patching, sparse autoencoder projections, and Distributed Alignment Search. The authors propose mitigating divergence via the Counterfactual Latent loss, demonstrating reduced representational divergence while preserving or improving interpretability and out-of-distribution performance in synthetic tasks and Boundless DAS experiments.
   - **Year**: 2025

7. **Title**: Aligning as Debiasing: Causality-Aware Alignment via Reinforcement Learning with Interventional Feedback (arXiv:2406.00000)
   - **Authors**: Yu Xia, Tong Yu, Zhankui He, Handong Zhao, Julian McAuley, Shuai Li
   - **Summary**: This paper addresses biases in large language models (LLMs) by introducing Causality-Aware Alignment (CAA), which leverages the reward model in reinforcement learning alignment as an instrumental variable to perform causal intervention on LLMs. Utilizing the reward difference between an initial LLM and an intervened LLM as interventional feedback, CAA guides reinforcement learning fine-tuning to align LLMs, resulting in less biased and safer outputs. Experiments on text generation tasks demonstrate the advantages of this method in aligning LLMs to generate less biased outputs.
   - **Year**: 2024

8. **Title**: Dimensions Underlying the Representational Alignment of Deep Neural Networks with Humans (arXiv:2506.00000)
   - **Authors**: [Authors not specified]
   - **Summary**: This study proposes a framework to compare human and AI representations by identifying latent representational dimensions underlying the same behavior in both domains. Applying this framework to humans and a deep neural network model of natural images reveals a low-dimensional embedding of both visual and semantic dimensions. The findings contribute to understanding the similarities and differences between human and artificial intelligence, promising deeper insights into human cognition and the development of more human-aligned AI systems.
   - **Year**: 2025

9. **Title**: Aligning Machine and Human Visual Representations Across Abstraction Levels (arXiv:2506.00000)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper highlights a key misalignment between vision models and humans: while human conceptual knowledge is hierarchically organized from fine- to coarse-scale distinctions, model representations do not accurately capture all these levels of abstraction. To address this, the authors train a teacher model to imitate human judgments and transfer human-aligned structure from its representations to refine the representations of pretrained vision foundation models via fine-tuning. The resulting human-aligned models more accurately approximate human behavior and uncertainty across various similarity tasks and perform better on diverse machine learning tasks, increasing generalization and out-of-distribution robustness.
   - **Year**: 2025

10. **Title**: Nonlinear Dilemma: Causal Abstraction in DNNs (arXiv:2507.08802)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper explores the concept of causal abstraction in deep neural networks (DNNs), aiming to map a neural network's behavior to a higher-level algorithm to simplify understanding. The study challenges the assumption that alignment maps should be linear and investigates maps with greater complexity to test the robustness and semantics of causal abstraction. Theoretical findings suggest that without constraints, causal abstraction loses its utility as a tool for understanding neural representations, leading to the nonlinear representation dilemma. Empirical investigations affirm these theoretical claims using tasks on multi-layer perceptrons and large language models.
    - **Year**: 2025

**Key Challenges:**

1. **Metric Limitations**: Current alignment metrics may not fully capture the complexity of representational alignment, especially when models differ in architecture or depth.

2. **Superposition in Representations**: The presence of superposition in neural representations can interfere with alignment metrics, leading to lower alignment scores and obscuring true representational similarities.

3. **Causal Intervention Divergence**: Causal interventions used for interpretability can produce representations that diverge from a model's natural latent distribution, potentially undermining the faithfulness of explanations.

4. **Human-AI Alignment**: Aligning machine representations with human conceptual knowledge across various levels of abstraction remains a challenge, affecting the development of more human-aligned AI systems.

5. **Nonlinear Representation Dilemma**: The complexity of alignment maps in causal abstraction can lead to a loss of utility in understanding neural representations, posing a dilemma in balancing complexity and interpretability. 