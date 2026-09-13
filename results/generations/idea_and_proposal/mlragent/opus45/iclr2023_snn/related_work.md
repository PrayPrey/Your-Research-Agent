1. **Title**: Reinforcement Learning Finetunes Small Subnetworks in Large Language Models (arXiv:2505.11711)
   - **Authors**: Sagnik Mukherjee, Lifan Yuan, Dilek Hakkani-Tur, Hao Peng
   - **Summary**: This study reveals that reinforcement learning (RL) fine-tuning in large language models (LLMs) predominantly updates a small subnetwork, comprising 5% to 30% of the parameters, while the majority remain unchanged. This phenomenon, termed RL-induced parameter update sparsity, occurs without explicit sparsity constraints and is consistent across various RL algorithms and LLM families.
   - **Year**: 2025

2. **Title**: Reinforcement Learning Fine-Tunes a Sparse Subnetwork in Large Language Models (arXiv:2507.17107)
   - **Authors**: Andrii Balashov
   - **Summary**: Challenging the assumption that RL fine-tuning requires updating most model parameters, this paper demonstrates that RL fine-tuning consistently modifies only a small subnetwork (5-30% of weights), leaving most parameters unchanged. This RL-induced parameter update sparsity is observed across multiple RL algorithms and model families, suggesting a partially transferable structure in pretrained models.
   - **Year**: 2025

3. **Title**: Sparsity-Driven Plasticity in Multi-Task Reinforcement Learning (arXiv:2508.06871)
   - **Authors**: Aleksandar Todorov, Juan Cardenas-Cartagena, Rafael F. Cunha, Marco Zullich, Matthia Sabatelli
   - **Summary**: Addressing plasticity loss in multi-task reinforcement learning (MTRL), this research explores how sparsification methods like Gradual Magnitude Pruning (GMP) and Sparse Evolutionary Training (SET) enhance plasticity and performance. The study evaluates these approaches across different MTRL architectures, demonstrating that dynamic sparsification effectively mitigates plasticity degradation indicators and often leads to improved multi-task performance.
   - **Year**: 2025

4. **Title**: Environment-Aware Transfer Reinforcement Learning for Sustainable Beam Selection (arXiv:2511.11647)
   - **Authors**: Dariush Salami, Ramin Hashemi, Parham Kazemi, Mikko A. Uusitalo
   - **Summary**: This paper presents a sustainable approach to beam selection in 5G and beyond networks using transfer learning and RL. By modeling environments as point clouds and computing Chamfer distances, structurally similar environments are identified, enabling the reuse of pre-trained models. This method achieves a 16x reduction in training time and computational overhead, contributing to energy efficiency and supporting green AI in wireless systems.
   - **Year**: 2025

5. **Title**: Network Sparsity Unlocks the Scaling Potential of Deep Reinforcement Learning (arXiv:2506.17204)
   - **Authors**: Guozheng Ma, Lu Li, Zilin Wang, Li Shen, Pierre-Luc Bacon, Dacheng Tao
   - **Summary**: This study demonstrates that introducing static network sparsity through one-shot random pruning can unlock scaling potential in deep reinforcement learning (DRL) models. Sparse networks achieve higher parameter efficiency and are more resistant to optimization challenges like plasticity loss and gradient interference, compared to their dense counterparts.
   - **Year**: 2025

6. **Title**: Efficient Reinforcement Finetuning via Adaptive Curriculum Learning (arXiv:2504.05520)
   - **Authors**: Taiwei Shi, Yiyang Wu, Linxin Song, Tianyi Zhou, Jieyu Zhao
   - **Summary**: Introducing AdaRFT (Adaptive Curriculum Reinforcement Finetuning), this paper proposes a method that dynamically adjusts training difficulty based on the model's reward signals. AdaRFT enhances both efficiency and accuracy in RL fine-tuning by ensuring the model trains on tasks that are challenging yet solvable, reducing training steps by up to 2x and improving accuracy on mathematical reasoning benchmarks.
   - **Year**: 2025

7. **Title**: Self-Evolving Curriculum for LLM Reasoning (arXiv:2505.14970)
   - **Authors**: Xiaoyin Chen, Jiarui Lu, Minsu Kim, Dinghuai Zhang, Jian Tang, Alexandre Piché, Nicolas Gontier, Yoshua Bengio, Ehsan Kamalloo
   - **Summary**: This paper introduces Self-Evolving Curriculum (SEC), an automatic curriculum learning method that concurrently learns a curriculum policy with the RL fine-tuning process. SEC dynamically adjusts the training curriculum, enhancing the reasoning abilities of large language models by presenting training problems in an optimal order.
   - **Year**: 2025

8. **Title**: Neural Network Compression for Reinforcement Learning Tasks
   - **Authors**: D.A. Ivanov, D.A. Larionov, O.V. Maslennikov, et al.
   - **Summary**: This research explores neural network compression techniques, such as pruning and quantization, in the context of reinforcement learning tasks. The study demonstrates that compressed networks can maintain performance levels comparable to their uncompressed counterparts while significantly reducing computational requirements, thereby enhancing the sustainability of RL applications.
   - **Year**: 2025

9. **Title**: Demonstration and Offset Augmented Meta Reinforcement Learning with Sparse Rewards
   - **Authors**: H. Li, J. Liang, X. Wang, et al.
   - **Summary**: Addressing the challenge of sparse rewards in meta reinforcement learning, this paper proposes a method that combines demonstration data and offset augmentation. The approach enhances learning efficiency and performance in environments with sparse rewards by leveraging suboptimal demonstrations and offset augmentation techniques.
   - **Year**: 2025

10. **Title**: Experimental Data-Efficient Reinforcement Learning with an Ensemble of Surrogate Models
    - **Authors**: [Authors not specified]
    - **Summary**: This study presents a model-based reinforcement learning method that enhances sample efficiency by generating synthetic data during training. By employing an ensemble of surrogate models created using symbolic regression, the approach uncovers fundamental physical principles governing system behavior, enabling more data-efficient real-world applications.
    - **Year**: 2025

**Key Challenges:**

1. **Non-Stationary Data Distributions**: RL environments often exhibit shifting data distributions as policies evolve, making static pruning methods less effective.

2. **Balancing Exploration and Exploitation**: Determining the optimal network capacity during different training phases to support both exploration and exploitation remains challenging.

3. **Maintaining Performance Post-Pruning**: Ensuring that performance remains within acceptable margins after applying sparsity techniques is critical.

4. **Adaptive Sparsity Scheduling**: Developing mechanisms to dynamically adjust network sparsity in response to training progress and environmental changes is complex.

5. **Sustainability vs. Performance Trade-offs**: Achieving significant reductions in computational resources without compromising the effectiveness of RL models poses a significant challenge. 