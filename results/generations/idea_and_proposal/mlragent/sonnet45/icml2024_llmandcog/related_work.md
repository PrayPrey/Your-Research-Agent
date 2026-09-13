1. **Title**: Reasoning Curriculum: Bootstrapping Broad LLM Reasoning from Math (arXiv:2510.26143)
   - **Authors**: Bo Pang, Deqian Kong, Silvio Savarese, Caiming Xiong, Yingbo Zhou
   - **Summary**: This paper introduces a two-stage curriculum learning approach to enhance reasoning in large language models (LLMs). The first stage focuses on developing reasoning skills through math-related tasks, while the second stage adapts these skills to other domains via joint reinforcement learning. The method is designed to be minimal and backbone-agnostic, requiring no specialized reward models beyond standard verifiability checks.
   - **Year**: 2025

2. **Title**: VL-Cogito: Progressive Curriculum Reinforcement Learning for Advanced Multimodal Reasoning (arXiv:2507.22607)
   - **Authors**: Ruifeng Yuan, Chenghao Xiao, Sicong Leng, Jianyu Wang, Long Li, Weiwen Xu, Hou Pong Chan, Deli Zhao, Tingyang Xu, Zhongyu Wei, Hao Zhang, Yu Rong
   - **Summary**: The authors propose VL-Cogito, a multimodal reasoning model trained using a multi-stage Progressive Curriculum Reinforcement Learning framework. This approach guides the model through tasks of increasing difficulty, improving reasoning abilities across diverse multimodal contexts. Key innovations include an online difficulty soft weighting mechanism and a dynamic length reward mechanism to balance reasoning efficiency with correctness.
   - **Year**: 2025

3. **Title**: Unveiling the Learning Mind of Language Models: A Cognitive Framework and Empirical Study (arXiv:2506.13464)
   - **Authors**: Zhengyu Hu, Jianxun Lian, Zheyuan Xiao, Seraphina Zhang, Tianfu Wang, Nicholas Jing Yuan, Xing Xie, Hui Xiong
   - **Summary**: This study introduces a framework inspired by cognitive psychology to assess LLMs' learning abilities, decomposing them into three dimensions: Learning from Instructor, Learning from Concept, and Learning from Experience. The authors conduct an empirical study across these dimensions, identifying insights such as the benefits of interaction and the scale-emergent nature of conceptual understanding.
   - **Year**: 2025

4. **Title**: Learning When to Look: A Disentangled Curriculum for Strategic Perception in Multimodal Reasoning (arXiv:2512.17227)
   - **Authors**: Siqi Yang, Zilve Gao, Haibo Qiu, Fanfan Liu, Peng Shi, Zhixiong Zeng, Qingmin Liao, Lin Ma
   - **Summary**: The paper addresses the issue of "visual forgetting" in Multimodal Large Language Models (MLLMs) during complex visual reasoning tasks. The authors propose a curriculum-based framework that disentangles abstract logical reasoning from strategic visual perception, introducing a Perception-Grounded Chain-of-Thought paradigm and a Pivotal Perception Reward to teach models when to engage in visual perception.
   - **Year**: 2025

5. **Title**: Self-Evolving Curriculum for LLM Reasoning (arXiv:2505.14970)
   - **Authors**: Xiaoyin Chen, Jiarui Lu, Minsu Kim, Dinghuai Zhang, Jian Tang, Alexandre Piché, Nicolas Gontier, Yoshua Bengio, Ehsan Kamalloo
   - **Summary**: This work introduces Self-Evolving Curriculum (SEC), an automatic curriculum learning method that concurrently learns a curriculum policy with the reinforcement learning fine-tuning process. SEC aims to address limitations in existing curricula by providing a more efficient and effective approach to enhancing LLM reasoning capabilities.
   - **Year**: 2025

6. **Title**: LLM+P: Empowering Large Language Models with Optimal Planning Proficiency (arXiv:2304.11477)
   - **Authors**: Bo Liu, Yuqian Jiang, Xiaohan Zhang, Qiang Liu, Shiqi Zhang, Joydeep Biswas, Peter Stone
   - **Summary**: The authors present LLM+P, a framework that integrates classical planners into LLMs to solve long-horizon planning problems. The approach involves converting natural language descriptions into the Planning Domain Definition Language (PDDL), utilizing classical planners to find solutions, and translating these solutions back into natural language.
   - **Year**: 2023

7. **Title**: Large Language Models with Controllable Working Memory (arXiv:2211.05110)
   - **Authors**: Daliang Li, Ankit Singh Rawat, Manzil Zaheer, Xin Wang, Michal Lukasik, Andreas Veit, Felix Yu, Sanjiv Kumar
   - **Summary**: This paper explores the integration of controllable working memory into LLMs to enhance their ability to adapt to dynamic environments and acquire new knowledge. The authors propose mechanisms to manage the interaction between the model's world knowledge and task-relevant information presented in context.
   - **Year**: 2022

8. **Title**: Text Classification via Large Language Models (arXiv:2305.08377)
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: The study introduces Clue And Reasoning Prompting (CARP), a strategy that employs a progressive reasoning approach tailored to address complex linguistic phenomena in text classification. CARP combines LLMs' generalization abilities with task-specific evidence from labeled datasets to improve performance, especially in low-resource and domain-adaptation scenarios.
   - **Year**: 2023

9. **Title**: Model of Hierarchical Complexity
   - **Authors**: [Not applicable]
   - **Summary**: The Model of Hierarchical Complexity (MHC) is a formal theory that quantifies the complexity of behaviors based on hierarchical task actions. It outlines 16 orders of hierarchical complexity, providing a framework to assess cognitive development stages and their corresponding tasks.
   - **Year**: [Not specified]

10. **Title**: Piaget's Theory of Cognitive Development
    - **Authors**: Jean Piaget
    - **Summary**: Piaget's theory outlines four stages of cognitive development: sensorimotor, preoperational, concrete operational, and formal operational. Each stage represents a different level of cognitive maturity, providing insights into the developmental progression of human cognition.
    - **Year**: [Original work published in 1936; referenced here for foundational context]

**Key Challenges**:

1. **Mapping Human Developmental Stages to LLM Training**: Accurately identifying and translating human cognitive developmental stages into corresponding training phases for LLMs is complex, requiring interdisciplinary expertise and careful design of synthetic datasets and tasks.

2. **Designing Effective Curriculum Learning Strategies**: Developing curriculum learning frameworks that effectively guide LLMs through progressive training stages without introducing biases or inefficiencies remains a significant challenge.

3. **Balancing Generalization and Specialization**: Ensuring that LLMs trained with developmental curricula can generalize across diverse tasks while maintaining specialized skills acquired during specific training phases is difficult.

4. **Evaluating Emergent Cognitive Abilities**: Establishing robust benchmarks and evaluation methods to assess the emergence and progression of cognitive abilities in LLMs trained with developmental curricula is essential but challenging.

5. **Computational Resource Constraints**: Implementing progressive training protocols inspired by human cognitive development may require substantial computational resources, posing practical limitations for large-scale training of LLMs. 