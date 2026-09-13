**Related Papers**

1. **Title**: Contextual Memory Reweaving in Large Language Models Using Layered Latent State Reconstruction (arXiv:2502.02046)
   - **Authors**: Frederick Dillon, Gregor Halvorsen, Simon Tattershall, Magnus Rowntree, Gareth Vanderpool
   - **Summary**: This paper introduces a structured approach to enhance memory retention in deep neural architectures by reweaving latent states captured at different processing layers. The proposed framework systematically integrates past contextual embeddings without external memory modules, improving recall accuracy across various sequence lengths and enhancing continuity in long-form text generation.
   - **Year**: 2025

2. **Title**: CogMem: A Cognitive Memory Architecture for Sustained Multi-Turn Reasoning in Large Language Models (arXiv:2512.14118)
   - **Authors**: Yiran Zhang, Jincheng Hu, Mark Dras, Usman Naseem
   - **Summary**: CogMem presents a memory-augmented LLM architecture inspired by cognitive processes, designed to support sustained iterative reasoning through structured, persistent memory. It incorporates a layered design with Long-Term Memory, Direct Access memory, and a Focus of Attention mechanism, mitigating reasoning failures and improving consistency across extended reasoning chains.
   - **Year**: 2025

3. **Title**: TiMem: Temporal-Hierarchical Memory Consolidation for Long-Horizon Conversational Agents (arXiv:2601.02845)
   - **Authors**: Kai Li, Xuanqing Yu, Ziyi Ni, Yi Zeng, Yao Xu, Zheqing Zhang, Xin Li, Jitao Sang, Xiaogang Duan, Xuelei Wang, Chengbao Liu, Jie Tan
   - **Summary**: TiMem introduces a temporal-hierarchical memory framework that organizes conversations through a Temporal Memory Tree, enabling systematic memory consolidation from raw conversational observations to progressively abstracted persona representations. It achieves state-of-the-art accuracy on long-horizon memory benchmarks while reducing recalled memory length significantly.
   - **Year**: 2026

4. **Title**: Memory Retrieval and Consolidation in Large Language Models through Function Tokens (arXiv:2510.08203)
   - **Authors**: Shaohua Zhang, Yuan Lin, Hang Li
   - **Summary**: This study proposes the function token hypothesis to explain memory retrieval and consolidation in LLMs. It suggests that function tokens activate predictive features from context during inference and govern next token prediction, while during pre-training, predicting content tokens following function tokens increases learned features and updates model parameters.
   - **Year**: 2025

5. **Title**: Mental-LLM: Leveraging Large Language Models for Mental Health Prediction via Online Text Data (arXiv:2307.14385)
   - **Authors**: Xuhai Xu, Bingsheng Yao, Yuanzhe Dong, Saadia Gabriel, Hong Yu, James Hendler, Marzyeh Ghassemi, Anind K. Dey, Dakuo Wang
   - **Summary**: Mental-LLM evaluates multiple LLMs on mental health prediction tasks using online text data. The study explores zero-shot prompting, few-shot prompting, and instruction fine-tuning, demonstrating that instruction fine-tuning significantly boosts performance across tasks, outperforming larger models with optimized prompt designs.
   - **Year**: 2024

6. **Title**: Offset Unlearning for Large Language Models (arXiv:2404.11045)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper addresses the challenge of unlearning specific information in LLMs by introducing offset unlearning techniques. It evaluates various unlearning strategies, including gradient ascent, gradient difference, KL minimization, and data relabeling, assessing their effectiveness in removing target information while maintaining model utility.
   - **Year**: 2024

7. **Title**: Accelerating Clinical Evidence Synthesis with Large Language Models (arXiv:2406.17755)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study presents TrialMind, a system leveraging LLMs to enhance literature screening and ranking in clinical evidence synthesis. It demonstrates that TrialMind significantly improves recall and ranking performance over traditional methods, streamlining the process of identifying relevant studies for systematic reviews.
   - **Year**: 2024

8. **Title**: DataStates-LLM: Lazy Asynchronous Checkpointing for Large Language Models (arXiv:2406.10707)
   - **Authors**: Avinash Maurya, [Additional authors not specified in the provided excerpt]
   - **Summary**: DataStates-LLM introduces a checkpointing strategy designed to minimize overhead during LLM training. By overlapping checkpoint I/O with training phases and utilizing efficient data transfer techniques, it achieves faster checkpointing and reduces training slowdowns compared to existing methods.
   - **Year**: 2024

9. **Title**: Published in Transactions on Machine Learning Research (07/2022) (arXiv:2204.05133)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses levels of experience generation in humans and other animals, outlining a hierarchy from direct experience to mental time travel. It explores how these concepts relate to memory and imagination, providing insights into cognitive processes that could inform artificial intelligence systems.
   - **Year**: 2022

10. **Title**: [Title not specified in the provided excerpt] (arXiv:2401.00134)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This work addresses the problem of high overheads incurred due to checkpointing in large-scale distributed LLM training. It proposes DataStates-LLM, which efficiently overlaps checkpoint I/O with training phases, achieving faster checkpointing and reducing training slowdowns compared to existing methods.
    - **Year**: 2024

**Key Challenges**

1. **Context Window Limitations**: LLMs often struggle with long-horizon tasks due to finite context windows, leading to degraded performance as sequence length increases.

2. **Inefficient Memory Management**: Existing memory frameworks may not effectively handle temporally structured information across hierarchical levels, resulting in fragmented memories and unstable long-horizon personalization.

3. **Balancing Memory Retention and Compression**: Developing mechanisms that selectively retain important information while compressing less critical data without significant loss remains a challenge.

4. **Dynamic Retrieval and Reconsolidation**: Implementing systems that can dynamically retrieve and update memories based on new contexts to form generalized knowledge is complex.

5. **Computational Efficiency**: Ensuring that memory consolidation and retrieval processes do not introduce prohibitive computational overhead is crucial for practical deployment. 