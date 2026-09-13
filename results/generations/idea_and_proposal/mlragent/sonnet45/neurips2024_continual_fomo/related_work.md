1. **Title**: Context-Free Synthetic Data Mitigates Forgetting (arXiv:2505.13811)
   - **Authors**: Parikshit Bansal, Sujay Sanghavi
   - **Summary**: This paper introduces a method to mitigate catastrophic forgetting in language models by generating context-free synthetic data. By penalizing the KL divergence between the original and fine-tuned models, the approach preserves zero-shot performance and reasoning capabilities without access to original training data.
   - **Year**: 2025

2. **Title**: Real Time Detection and Quantitative Analysis of Spurious Forgetting in Continual Learning (arXiv:2512.20634)
   - **Authors**: Weiwei Wang
   - **Summary**: The study presents a framework for real-time detection and analysis of spurious forgetting in continual learning. It introduces quantitative metrics to measure alignment depth and proposes adaptive mitigation strategies to promote deep alignment, enhancing robustness against forgetting.
   - **Year**: 2025

3. **Title**: Unforgotten Safety: Preserving Safety Alignment of Large Language Models with Continual Learning (arXiv:2512.10150)
   - **Authors**: Lama Alssum, Hani Itani, Hasan Abed Al Kader Hammoud, Philip Torr, Adel Bibi, Bernard Ghanem
   - **Summary**: This paper addresses the degradation of safety alignment in large language models during fine-tuning. By framing the problem as a continual learning challenge, the authors adapt various approaches to mitigate safety degradation, demonstrating that methods like DER outperform existing baselines while maintaining task utility.
   - **Year**: 2025

4. **Title**: How to Alleviate Catastrophic Forgetting in LLMs Finetuning? Hierarchical Layer-Wise and Element-Wise Regularization (arXiv:2501.13669)
   - **Authors**: Shezheng Song, Hao Xu, Jun Ma, Shasha Li, Long Peng, Qian Wan, Xiaodong Liu, Jie Yu
   - **Summary**: The authors propose a novel approach to mitigate catastrophic forgetting in large language models by computing element-wise parameter importance and employing a dual-objective optimization strategy. This method enhances model adaptability while preserving general knowledge, demonstrating efficiency across various tasks.
   - **Year**: 2025

5. **Title**: Revisiting Catastrophic Forgetting in Large Language Model Tuning
   - **Authors**: Hongyu Li, Liang Ding, Meng Fang, Dacheng Tao
   - **Summary**: This paper investigates the link between the flatness of the model loss landscape and the extent of catastrophic forgetting in large language models. By introducing sharpness-aware minimization, the authors demonstrate its effectiveness in alleviating forgetting across multiple fine-tuning datasets.
   - **Year**: 2024

6. **Title**: Bayesian Parameter-Efficient Fine-Tuning for Overcoming Catastrophic Forgetting
   - **Authors**: Haolin Chen, Philip N. Garner
   - **Summary**: Focusing on text-to-speech models, this study applies Bayesian learning techniques to parameter-efficient fine-tuning to prevent catastrophic forgetting. Utilizing Laplace approximations, the approach effectively preserves pre-training knowledge without degrading fine-tuning performance.
   - **Year**: 2024

7. **Title**: An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning
   - **Authors**: [Not specified]
   - **Summary**: This empirical study evaluates catastrophic forgetting in large language models during continual instruction tuning, focusing on domain knowledge, reasoning, and reading comprehension. The findings reveal that larger models exhibit more severe forgetting, highlighting the need for effective mitigation strategies.
   - **Year**: 2023

8. **Title**: Mitigating Forgetting in LLM Fine-Tuning via Low-Perplexity Token Learning (arXiv:2501.14315)
   - **Authors**: [Not specified]
   - **Summary**: The paper addresses catastrophic forgetting during domain-specific fine-tuning of instruction-following large language models. It introduces Selective Token Masking (STM), which masks high-perplexity ground-truth tokens during training, achieving target-task gains while preserving non-target performance with reduced computation.
   - **Year**: 2025

9. **Title**: Improved Supervised Fine-Tuning for Large Language Models to Mitigate Catastrophic Forgetting (arXiv:2506.09428)
   - **Authors**: Fei Ding, Baiqiao Wang
   - **Summary**: This study proposes a cost-effective supervised fine-tuning method that mitigates catastrophic forgetting without access to original fine-tuning data. By reconstructing the instruction distribution of the base model and synthesizing a high-quality general-purpose dataset, the approach preserves generalization capabilities while improving task-specific performance.
   - **Year**: 2025

10. **Title**: Mitigating Catastrophic Forgetting in Large Language Models with Forgetting-aware Pruning
    - **Authors**: Wei Huang, Anda Cheng, Yinggui Wang
    - **Summary**: The authors introduce the Forgetting-Aware Pruning Metric (FAPM), a pruning-based approach that balances catastrophic forgetting and downstream task performance. By quantifying forgetting through the ratio of task vectors to pre-trained model parameters, FAPM effectively limits forgetting while maintaining accuracy across various datasets.
    - **Year**: 2025

**Key Challenges:**

1. **Catastrophic Forgetting**: Fine-tuning foundation models on new tasks often leads to the loss of previously acquired knowledge, hindering the model's ability to retain and integrate information over time.

2. **Computational Constraints**: As foundation models scale to billions of parameters, traditional methods like rehearsal-based learning or full parameter protection become computationally infeasible, necessitating more efficient approaches.

3. **Safety Alignment Preservation**: Ensuring that fine-tuned models maintain safety and ethical standards is challenging, as adapting to new tasks can compromise these alignments.

4. **Balancing Plasticity and Stability**: Developing methods that allow models to adapt to new tasks (plasticity) while preserving existing knowledge (stability) without excessive computational overhead remains a significant challenge.

5. **Lack of Access to Original Training Data**: In many scenarios, practitioners do not have access to the original pre-training data, making it difficult to implement strategies that rely on data replay or augmentation to mitigate forgetting. 