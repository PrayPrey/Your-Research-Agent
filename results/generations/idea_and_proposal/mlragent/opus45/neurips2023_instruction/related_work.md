1. **Title**: BioInstruct: Instruction Tuning of Large Language Models for Biomedical Natural Language Processing (2310.19975)
   - **Authors**: Hieu Tran, Zhichao Yang, Zonghai Yao, Hong Yu
   - **Summary**: This paper introduces BioInstruct, a dataset comprising 25,005 biomedical instructions designed to fine-tune large language models (LLMs) for biomedical natural language processing tasks. The authors employ Low-Rank Adaptation (LoRA) for parameter-efficient fine-tuning and demonstrate significant performance improvements across question answering, information extraction, and text generation tasks.
   - **Year**: 2023

2. **Title**: Towards Alignment-Centric Paradigm: A Survey of Instruction Tuning in Large Language Models (2508.17184)
   - **Authors**: Xudong Han, Junjie Yang, Tianyang Wang, Ziqian Bi, Junfeng Hao, Junhao Song
   - **Summary**: This survey provides a comprehensive overview of instruction tuning in LLMs, covering data collection methodologies, fine-tuning strategies, and evaluation protocols. It categorizes data construction into expert annotation, distillation from larger models, and self-improvement mechanisms, highlighting the trade-offs between quality, scalability, and resource cost.
   - **Year**: 2025

3. **Title**: Mixture-of-Experts Meets Instruction Tuning: A Winning Combination for Large Language Models (2305.14705)
   - **Authors**: Sheng Shen, Le Hou, Yanqi Zhou, Nan Du, Shayne Longpre, Jason Wei, Hyung Won Chung, Barret Zoph, William Fedus, Xinyun Chen, Tu Vu, Yuexin Wu, Wuyang Chen, Albert Webson, Yunxuan Li, Vincent Zhao, Hongkun Yu, Kurt Keutzer, Trevor Darrell, Denny Zhou
   - **Summary**: The authors explore the combination of Sparse Mixture-of-Experts (MoE) architecture with instruction tuning in LLMs. They find that MoE models benefit more from instruction tuning than dense models, achieving superior performance on benchmark tasks while using fewer computational resources.
   - **Year**: 2023

4. **Title**: Phased Instruction Fine-Tuning for Large Language Models (2406.04371)
   - **Authors**: Wei Pang, Chuan Zhou, Xiao-Hua Zhou, Xiaojie Wang
   - **Summary**: This paper proposes Phased Instruction Fine-Tuning (Phased IFT), a method that assesses instruction difficulty and divides instruction data into subsets of increasing difficulty for sequential training. The approach significantly outperforms traditional one-off instruction fine-tuning, supporting the progressive alignment hypothesis and enhancing LLM performance.
   - **Year**: 2024

5. **Title**: TASTE: Teaching Large Language Models to Translate (2406.08434)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: TASTE introduces a framework for teaching LLMs to perform translation tasks effectively. The approach involves quality estimation and text classification to improve translation performance across multiple language pairs, demonstrating significant gains over existing models.
   - **Year**: 2024

6. **Title**: Contrastive Instruction Tuning (2402.11138)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work presents COIN, a contrastive instruction tuning method that aligns hidden representations of semantically equivalent instruction-instance pairs. Evaluation on PromptBench shows enhanced robustness of LLMs to semantic-invariant instruction variations, improving performance across various tasks.
   - **Year**: 2024

7. **Title**: PANGU-CODER2: Boosting Large Language Models for Code with Ranking Feedback (2307.14936)
   - **Authors**: Bo Shen, Jiaxin Zhang, Taihong Chen, Daoguang Zan, Bing Geng, An Fu, Muhan Zeng, Ailun Yu, Jichuan Ji, Jingyang Zhao, Yuenan Guo, Qianxiang Wang
   - **Summary**: The authors propose RRTF (Rank Responses to align Test&Teacher Feedback), a framework to enhance pre-trained LLMs for code generation. PanGu-Coder2, developed under this framework, achieves state-of-the-art performance on the OpenAI HumanEval benchmark, surpassing previous models.
   - **Year**: 2023

8. **Title**: DeAL: Decoding-time Alignment for Large Language Models (2402.06147)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: DeAL introduces a decoding-time alignment strategy for LLMs, aiming to improve adherence to alignment objectives without affecting task performance. The method demonstrates increased keyword coverage and alignment in generated text across various tasks.
   - **Year**: 2024

**Key Challenges**:

1. **Overconfidence in Ambiguous Instructions**: LLMs often exhibit overconfidence when processing ambiguous or underspecified instructions, leading to hallucinations and unreliable outputs.

2. **Lack of Quality Signals in Synthetic Data**: Synthetic data generation for instruction tuning typically lacks indicators of instruction clarity, resulting in models that cannot distinguish between clear and ambiguous instructions.

3. **Inability to Seek Clarification**: Current models are not trained to seek clarification when faced with ambiguous instructions, leading to incorrect outputs rather than appropriate uncertainty expressions.

4. **Computational Efficiency in Fine-Tuning**: Balancing computational efficiency with effective instruction tuning remains a challenge, especially when integrating complex architectures like MoE with instruction tuning.

5. **Robustness to Instruction Variations**: Ensuring that LLMs are robust to semantic-invariant instruction variations is crucial for reliable performance across diverse tasks and instructions. 