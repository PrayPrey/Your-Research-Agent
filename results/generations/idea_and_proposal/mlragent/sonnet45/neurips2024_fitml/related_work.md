1. **Title**: GraLoRA: Granular Low-Rank Adaptation for Parameter-Efficient Fine-Tuning (arXiv:2505.20355)
   - **Authors**: Yeonjoon Jung, Daehyun Ahn, Hyungjun Kim, Taesu Kim, Eunhyeok Park
   - **Summary**: This paper introduces GraLoRA, a method that partitions weight matrices into sub-blocks, each with its own low-rank adapter. This structure aims to overcome LoRA's limitations by increasing representational capacity and closely approximating full fine-tuning behavior, achieving significant performance gains across various benchmarks.
   - **Year**: 2025

2. **Title**: DropLoRA: Sparse Low-Rank Adaptation for Parameter-Efficient Fine-Tuning (arXiv:2508.17337)
   - **Authors**: Haojie Zhang
   - **Summary**: DropLoRA introduces a pruning module between the two low-rank matrices in LoRA to simulate dynamic subspace learning. This approach allows for continuous adaptation of the learning subspace, enhancing performance without additional training or inference costs, and demonstrates superiority over traditional LoRA in various large language model generation tasks.
   - **Year**: 2025

3. **Title**: MELoRA: Mini-Ensemble Low-Rank Adapters for Parameter-Efficient Fine-Tuning (arXiv:2402.17263)
   - **Authors**: Pengjie Ren, Chengshun Shi, Shiguang Wu, Mengqi Zhang, Zhaochun Ren, Maarten de Rijke, Zhumin Chen, Jiahuan Pei
   - **Summary**: MELoRA proposes using a group of mini LoRAs with a small number of parameters to capture diversity among adapters, promoting better generalization. This method achieves better performance with significantly fewer trainable parameters compared to traditional LoRA, demonstrating effectiveness across various NLP tasks.
   - **Year**: 2024

4. **Title**: TriAdaptLoRA: Brain-Inspired Triangular Adaptive Low-Rank Adaptation for Parameter-Efficient Fine-Tuning (arXiv:2501.08008)
   - **Authors**: Yao Liang, Yuwei Wang, Yi Zeng
   - **Summary**: TriAdaptLoRA introduces a triangular split of transformation matrices into lower and upper triangular components, combined with an adaptive rank-growth strategy governed by dynamic thresholds. This framework dynamically optimizes the allocation of trainable parameters, achieving superior performance and enhanced stability in fine-tuning large language models.
   - **Year**: 2025

5. **Title**: Uncertainty-Penalized Reinforcement Learning from Human Feedback with Diverse Reward LoRA Ensembles (arXiv:2401.00243)
   - **Authors**: Not specified
   - **Summary**: This work proposes UP-RLHF, which augments reinforcement learning from human feedback with uncertainty regularization by penalizing rewards with uncertainties provided by the reward model. It introduces diverse LoRA ensembles to train uncertainty-aware reward models, effectively mitigating overoptimization and improving performance.
   - **Year**: 2024

6. **Title**: A Deep Dive into the Trade-Offs of Parameter-Efficient Fine-Tuning Methods (arXiv:2406.04879)
   - **Authors**: Not specified
   - **Summary**: This paper investigates the trade-offs in parameter-efficient fine-tuning methods, focusing on aspects such as alignment datasets, preference sets, and mixtures used for alignment. It provides insights into the effects of alignment datasets in terms of informativeness, quality, and the number of samples used, contributing to a better understanding of fine-tuning practices.
   - **Year**: 2024

7. **Title**: OpenELM: An Efficient Language Model Family with Open Training and Fine-Tuning (arXiv:2404.14619)
   - **Authors**: Not specified
   - **Summary**: OpenELM presents a family of efficient language models with open training and fine-tuning methodologies. It emphasizes the balance between model accuracy and deployment feasibility, addressing challenges in inference efficiency and scalability, and provides benchmarking results compared to other similar language models.
   - **Year**: 2024

8. **Title**: PI-Whisper: An Adaptive and Incremental ASR Framework for Diverse Speech Characteristics (arXiv:2406.15668)
   - **Authors**: Not specified
   - **Summary**: PI-Whisper introduces an adaptive and incremental automatic speech recognition framework that integrates multiple speaker characteristics. It utilizes a linear-time non-intrusive approach, allowing seamless integration of diverse speech profiles, and demonstrates improvements in transcription quality by incorporating additional speaker information.
   - **Year**: 2024

9. **Title**: Harnessing the Power of LLMs in Practice: A Survey on ChatGPT and Beyond (arXiv:2304.13712)
   - **Authors**: Not specified
   - **Summary**: This survey explores the practical applications of large language models like ChatGPT, discussing aspects such as parameter-efficient tuning, trustworthiness, robustness, and calibration. It provides insights into the challenges and considerations for deploying LLMs in real-world scenarios, emphasizing the importance of efficiency and reliability.
   - **Year**: 2023

10. **Title**: Adaptive Rank Allocation for Multi-Task Fine-Tuning via Dynamic Gradient Analysis
    - **Authors**: Not specified
    - **Summary**: This paper proposes a gradient-based method to dynamically allocate ranks during fine-tuning initialization. It involves gradient sensitivity analysis, rank budget optimization, and layer-wise rank assignment, aiming to improve fine-tuning efficiency and performance, particularly in multi-task scenarios.
    - **Year**: Not specified

**Key Challenges**:

1. **Gradient Entanglement**: Traditional low-rank adaptation methods like LoRA introduce structural bottlenecks that lead to gradient entanglement, distorting gradient propagation and limiting representational capacity.

2. **Overfitting at Higher Ranks**: Increasing the rank in low-rank adaptation methods often results in overfitting, causing performance stagnation or decline, and failing to match full fine-tuning performance.

3. **Static Subspace Limitations**: Conventional methods operate within a static subspace, restricting the model's ability to adapt dynamically to task-specific requirements, leading to suboptimal performance.

4. **Computational and Resource Constraints**: Full fine-tuning of large language models is computationally intensive and resource-demanding, posing challenges for deployment in resource-constrained environments.

5. **Generalization Across Tasks**: Achieving effective generalization across diverse tasks remains a challenge, as models fine-tuned on specific tasks may not perform well on others, necessitating efficient multi-task adaptation strategies. 