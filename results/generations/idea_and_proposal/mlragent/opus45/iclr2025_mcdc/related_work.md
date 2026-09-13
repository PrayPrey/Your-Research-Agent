1. **Title**: Mixture of Modular Experts: Distilling Knowledge from a Multilingual Teacher into Specialized Modular Language Models (arXiv:2407.19610)
   - **Authors**: Mohammed Al-Maamari, Mehdi Ben Amor, Michael Granitzer
   - **Summary**: This paper integrates Knowledge Distillation (KD) with Mixture of Experts (MoE) to create modular, efficient multilingual language models. It evaluates adaptive versus fixed alpha methods in KD and compares modular MoE architectures for handling multi-domain inputs and preventing catastrophic forgetting. The study finds that both KD methods perform similarly, with marginal improvements from adaptive alpha. A combined loss approach provides more stable learning. The MoE architecture effectively preserves knowledge across multiple languages, mitigating catastrophic forgetting.
   - **Year**: 2024

2. **Title**: MixtureKit: A General Framework for Composing, Training, and Visualizing Mixture-of-Experts Models (arXiv:2512.12121)
   - **Authors**: Ahmad Chamma, Omar El Herraoui, Guokan Shang
   - **Summary**: MixtureKit is an open-source framework for constructing, training, and analyzing MoE models from arbitrary pre-trained or fine-tuned models. It supports three methods: Traditional MoE, BTX (Branch-Train-Mix), and BTS (Branch-Train-Stitch). MixtureKit automatically modifies model configurations, patches decoder and causal LM classes, and saves unified checkpoints ready for inference or fine-tuning. A visualization interface is provided to inspect per-token routing decisions, expert weight distributions, and layer-wise contributions. Experiments with multilingual code-switched data show that a BTX-based model trained using MixtureKit can outperform baseline dense models on multiple benchmarks.
   - **Year**: 2025

3. **Title**: GRIP: Algorithm-Agnostic Machine Unlearning for Mixture-of-Experts via Geometric Router Constraints (arXiv:2601.16905)
   - **Authors**: Andy Zhu, Rongzhe Wei, Yupu Gu, Pan Li
   - **Summary**: GRIP introduces a framework for machine unlearning in MoE architectures by implementing geometric constraints on router parameters. This approach prevents superficial forgetting by ensuring that unlearning operations erase knowledge directly from expert parameters rather than manipulating routers to redirect queries. GRIP functions as an adapter, constraining router parameter updates without modifying the underlying unlearning algorithm, thereby preserving model utility while achieving effective unlearning.
   - **Year**: 2026

4. **Title**: Scalable Multi-Domain Adaptation of Language Models using Modular Experts (arXiv:2410.10181)
   - **Authors**: Peter Schafhalter, Shun Liao, Yanqi Zhou, Chih-Kuan Yeh, Arun Kandoor, James Laudon
   - **Summary**: This work proposes Modular Domain Experts (MoDE), a MoE architecture that augments general pre-trained language models with modular, domain-specialized experts. These experts are trained independently and composed via a lightweight training process. MoDE achieves comparable target performances to full parameter fine-tuning while improving retention performance and training speeds. The architecture enables flexible sharding configurations and efficient training, making it suitable for resource-constrained environments.
   - **Year**: 2024

5. **Title**: Offset Unlearning for Large Language Models (arXiv:2404.11045)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper addresses the challenge of machine unlearning in large language models by introducing offset unlearning techniques. It evaluates various unlearning strategies, including gradient ascent, gradient difference, KL minimization, and data relabeling, across different subsets of the TOFU benchmark. The study highlights the effectiveness of these methods in achieving unlearning objectives while maintaining model utility.
   - **Year**: 2024

6. **Title**: Mixture of Experts Models for Multilevel Data: Modelling Framework and Approximation Theory (arXiv:2209.15207)
   - **Authors**: Tsz Chai Fung, Spark C. Tseung
   - **Summary**: This research extends the MoE framework to multilevel data by introducing the Mixed MoE (MMoE) model. The authors prove that MMoE is dense in the space of continuous mixed effects models, allowing it to accurately capture characteristics inherent in multilevel data, including marginal distributions, dependence structures, regression links, random intercepts, and random slopes. The study provides a theoretical foundation for applying MoE models to complex hierarchical data structures.
   - **Year**: 2024

7. **Title**: MM1: Methods, Analysis & Insights from Multimodal LLM Pre-training (arXiv:2403.09611)
   - **Authors**: Brandon McKinzie, Zhe Gan, Jean-Philippe Fauconnier, et al.
   - **Summary**: This paper discusses the development of performant Multimodal Large Language Models (MLLMs) by studying the importance of various architectural components and data choices. Through comprehensive ablations of the image encoder, vision-language connector, and pre-training data, the authors identify crucial design lessons. They introduce MM1, a family of multimodal models, including both dense and MoE variants, that achieve state-of-the-art few-shot results across multiple benchmarks.
   - **Year**: 2024

8. **Title**: Efficient Transformers: A Survey (arXiv:2009.06732)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This survey explores various efficient Transformer models, including MoE-based sparse models like GShard, Switch Transformer, and GLaM. It discusses the key idea behind MoE, which involves routing tokens to selected experts determined by a routing function, typically computed as a linear combination over experts using the softmax function. The survey provides insights into the design and evaluation of efficient Transformer architectures.
   - **Year**: 2024

9. **Title**: Learning an Evolved Mixture Model for Task-Free Continual Learning (arXiv:2207.05080)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work introduces an evolved mixture model (EMM) for task-free continual learning. The model employs an expansion and dropout mechanism to adaptively add new experts or remove outdated ones based on the Hilbert-Schmidt Independence Criterion (HSIC). This approach enables the model to learn new information while mitigating catastrophic forgetting, making it suitable for continual learning scenarios.
   - **Year**: 2024

10. **Title**: Modular Unlearning via Expert Isolation and Surgical Removal in MoE Architectures
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This research proposes Isolation-Aware MoE Training (IA-MoE), a framework that encourages knowledge compartmentalization during training to enable efficient unlearning. The approach involves domain-guided routing regularization, sparse activation tracking, and a surgical unlearning protocol. Expected outcomes include near-instantaneous unlearning with minimal performance degradation on retained knowledge, evaluated on text and image domains using standard unlearning benchmarks.
    - **Year**: [Year not specified in the provided excerpt]

**Key Challenges:**

1. **Knowledge Entanglement**: In MoE architectures, knowledge is often distributed across multiple experts, making it challenging to isolate and remove specific information without affecting the overall model performance.

2. **Routing Stability**: Ensuring that routers consistently assign data to the appropriate experts is crucial for effective unlearning. Instabilities in routing can lead to superficial forgetting and loss of model utility.

3. **Computational Efficiency**: Traditional unlearning methods can be computationally expensive, especially when applied to large-scale MoE models. Developing efficient unlearning protocols that minimize computational overhead is essential.

4. **Catastrophic Forgetting**: Removing specific knowledge from a model can inadvertently lead to the forgetting of unrelated but important information. Strategies to mitigate catastrophic forgetting are necessary to maintain model utility.

5. **Evaluation Metrics**: Establishing standardized benchmarks and metrics to assess the effectiveness of unlearning methods in MoE architectures is critical for comparing different approaches and ensuring progress in the field. 