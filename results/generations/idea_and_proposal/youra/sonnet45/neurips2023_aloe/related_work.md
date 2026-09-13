## Related Work

**Related Papers**

1. **Title**: Mind in Society: The Development of Higher Psychological Processes (Vygotsky, 1978)
   - **Authors**: L. S. Vygotsky
   - **Summary**: Introduces the Zone of Proximal Development (ZPD) concept demonstrating that learners progress optimally when challenged at the boundary between independent and assisted capability. This foundational work provides the theoretical basis for identifying capability frontiers in learning systems.
   - **Year**: 1978

2. **Title**: Curriculum learning
   - **Authors**: Bengio, Y., Louradour, J., Collobert, R., & Weston, J.
   - **Summary**: Demonstrates that training on examples ordered by difficulty improves learning efficiency in machine learning systems. Establishes curriculum learning as an effective strategy for neural network training.
   - **Year**: 2009

3. **Title**: Catastrophic interference in connectionist networks: The sequential learning problem
   - **Authors**: McCloskey, M., & Cohen, N. J.
   - **Summary**: Identifies the catastrophic forgetting problem in neural networks during sequential learning, showing how networks lose previously learned information when trained on new tasks.
   - **Year**: 1989

4. **Title**: Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design
   - **Authors**: Dennis, M., Jaques, N., Vinitsky, E., Bayen, A., Russell, S., Critch, A., & Levine, S.
   - **Summary**: Introduces Unsupervised Environment Design (UED) concept for generating training environments at an agent's capability boundary in reinforcement learning contexts.
   - **Year**: 2020

5. **Title**: MAESTRO: Open-Ended Environment Design for Multi-Agent Reinforcement Learning
   - **Authors**: Samvelyan, M., Khan, A., Dennis, M., Parker-Holder, J., Raileanu, R., Rocktäschel, T., & Whiteson, S.
   - **Summary**: Extends UED to multi-agent settings with joint curricula generation. Demonstrates how UED principles can be applied to complex multi-agent learning scenarios.
   - **Year**: 2023

6. **Title**: Efficient Reinforcement Finetuning via Adaptive Curriculum Learning
   - **Authors**: Shi, T., Wu, Y., Song, L., Zhou, T., & Zhao, J.
   - **Summary**: Demonstrates that adaptive curriculum achieves 2x speedup for LLM fine-tuning through dynamic difficulty adjustment. Shows practical effectiveness of curriculum learning for large language models.
   - **Year**: 2025

7. **Title**: Investigating the Zone of Proximal Development of Language Models for In-Context Learning
   - **Authors**: Cui, P., & Sachan, M.
   - **Summary**: Empirically validates the ZPD concept for large language models using Item Response Theory. Provides direct evidence that LLMs exhibit capability boundaries analogous to human learning zones.
   - **Year**: 2025

8. **Title**: How do language models learn facts? Dynamics, curricula and hallucinations
   - **Authors**: Zucchet, N., Bornschein, J., Chan, S., et al.
   - **Summary**: Studies LLM training dynamics showing three-phase learning patterns and curriculum effects on fact acquisition and hallucination behaviors.
   - **Year**: 2025

9. **Title**: Leveraging Implicit Feedback from Deployment Data in Dialogue
   - **Authors**: Pang, R. Y., Roller, S., Cho, K., He, H., & Weston, J.
   - **Summary**: Used BlenderBot deployment data with implicit signals (conversation length, sentiment, reactions). Found that optimizing for conversation length led to controversial responses, demonstrating the risks of unvalidated implicit signal optimization.
   - **Year**: 2023

10. **Title**: User Feedback in Human-LLM Dialogues: A Lens to Understand Users But Noisy as a Learning Signal
    - **Authors**: Liu, Y., Zhang, M. J. Q., & Choi, E.
    - **Summary**: Confirms that implicit signals from user behavior are noisy learning signals with mixed results across different benchmarks (MTBench vs. WildBench), highlighting the need for validation mechanisms.
    - **Year**: 2025

11. **Title**: Rethinking the Evaluation of Dialogue Systems: Effects of User Feedback on Crowdworkers and LLMs
    - **Authors**: Siro, C., Aliannejadi, M., & de Rijke, M.
    - **Summary**: Shows that user follow-up utterances and behaviors significantly influence dialogue system evaluation. Validates that follow-up behavior contains quality signals usable for capability assessment.
    - **Year**: 2024

12. **Title**: An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-Tuning
    - **Authors**: Luo, Y., Yang, Z., Meng, F., Li, Y., Zhou, J., & Zhang, Y.
    - **Summary**: Confirms that catastrophic forgetting occurs in large language models and intensifies with model scale (1B-7B parameter range). Provides extensive empirical evidence of the forgetting phenomenon during continual adaptation.
    - **Year**: 2023

13. **Title**: Continual Learning of Large Language Models: A Comprehensive Survey
    - **Authors**: Shi, H., Xu, Z., Wang, H., Qin, W., Wang, W., Wang, Y., & Wang, H.
    - **Summary**: Provides comprehensive toolkit and survey of catastrophic forgetting mitigation strategies including replay buffers, knowledge distillation, elastic weight consolidation, and parameter-efficient fine-tuning approaches.
    - **Year**: 2024

14. **Title**: Distilling the knowledge in a neural network
    - **Authors**: Hinton, G., Vinyals, O., & Dean, J.
    - **Summary**: Introduces knowledge distillation technique where a smaller network learns to mimic a larger teacher network's outputs. This technique is applied in continual learning contexts to preserve model capabilities.
    - **Year**: 2015

15. **Title**: Self-improving reactive agents based on reinforcement learning, planning and teaching
    - **Authors**: Lin, L.-J.
    - **Summary**: Introduces the experience replay concept where agents store and reuse past experiences for learning. This approach is foundational for preventing catastrophic forgetting in sequential learning scenarios.
    - **Year**: 1992

16. **Title**: Training language models to follow instructions with human feedback
   - **Authors**: Ouyang, L., Wu, J., Jiang, X., et al.
   - **Summary**: Establishes Reinforcement Learning from Human Feedback (RLHF) as the standard approach for LLM alignment through explicit human preference collection and reward modeling.
   - **Year**: 2022

17. **Title**: Direct Preference Optimization: Your Language Model is Secretly a Reward Model
    - **Authors**: Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C.
    - **Summary**: Simplifies RLHF by eliminating the separate reward model training phase. Still requires explicit preference labels but provides a more efficient optimization approach.
    - **Year**: 2023

18. **Title**: Learning to summarize user information for personalized reinforcement learning from human feedback
    - **Authors**: Nam, H., et al.
    - **Summary**: Learns user preference representations from interaction history to enable personalized reward modeling. Requires explicit preference labels for effective personalization.
    - **Year**: 2025

19. **Title**: Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity
    - **Authors**: Faldor, M., & Cully, A.
    - **Summary**: Demonstrates how quality-diversity algorithms enable unbounded diversity generation in continuous cellular automata systems. Shows principles for generating diverse yet high-quality training examples.
    - **Year**: 2024

20. **Title**: Rainbow Teaming: Open-Ended Generation of Diverse Adversarial Prompts (arXiv)
    - **Authors**: Samvelyan, M., Raparthy, S., et al.
    - **Summary**: Applies quality-diversity principles to LLM adversarial prompt generation for safety testing. Demonstrates how to generate diverse challenging examples targeting specific model vulnerabilities.
    - **Year**: 2024

**Key Challenges**

1. **Active vs. Passive Learning Gap**: Traditional Unsupervised Environment Design (UED) methods require active environment control and simulation capabilities, making them inapplicable to deployed systems where only passive observation of user interactions is possible.

2. **Noisy Implicit Signals**: User behavioral signals (conversation continuation, reformulation, abandonment) are inherently noisy and can be misleading without proper validation, as demonstrated by instances where optimizing for implicit signals led to controversial or undesirable model behaviors.

3. **Catastrophic Forgetting in Continual Learning**: Neural networks, especially large language models, suffer from catastrophic forgetting when trained sequentially on new tasks, with the problem intensifying as model scale increases from 1B to 7B+ parameters.

4. **High Annotation Costs**: Current state-of-the-art approaches like RLHF and DPO require extensive explicit human feedback (10k-100k+ labeled examples), creating prohibitively expensive and slow feedback loops for continuous model improvement.

5. **Lack of Frontier Targeting**: Existing post-deployment adaptation methods train on all available data without distinguishing between mastered capabilities and frontier capabilities, leading to inefficient resource allocation and slower improvement rates.

6. **Synthetic-to-Real Transfer Uncertainty**: While generative models can create synthetic training examples, there is limited evidence that these synthetic examples effectively transfer to real-world capability improvements, particularly when targeting specific skill boundaries.

7. **Balancing Improvement and Preservation**: Post-deployment adaptation systems must simultaneously improve on new frontier capabilities while preserving existing mastered skills, requiring careful balance between plasticity (learning new) and stability (preserving old).

8. **Infrastructure and Operational Complexity**: Implementing continuous adaptation systems requires sophisticated ML production infrastructure including model versioning, A/B testing frameworks, automated evaluation pipelines, and rollback mechanisms that may be unavailable in resource-constrained deployments.
