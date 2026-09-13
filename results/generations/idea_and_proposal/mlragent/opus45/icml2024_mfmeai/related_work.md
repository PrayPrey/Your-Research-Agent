1. **Title**: SkillDiffuser: Interpretable Hierarchical Planning via Skill Abstractions in Diffusion-Based Task Execution (arXiv:2312.11598)
   - **Authors**: Zhixuan Liang, Yao Mu, Hengbo Ma, Masayoshi Tomizuka, Mingyu Ding, Ping Luo
   - **Summary**: This paper introduces SkillDiffuser, a hierarchical planning framework that integrates skill learning with conditional diffusion models to generate coherent trajectories from high-level instructions. The approach involves learning discrete, interpretable skill representations from visual observations and language instructions, which are then used to condition diffusion models for trajectory generation. Experiments demonstrate state-of-the-art performance in multi-task robotic manipulation benchmarks.
   - **Year**: 2023

2. **Title**: Generalizable Hierarchical Skill Learning via Object-Centric Representation (arXiv:2510.21121)
   - **Authors**: Haibo Zhao, Yu Qi, Boce Hu, Yizhe Zhu, Ziyan Chen, Heng Tian, Xupeng Zhu, Owen Howell, Haojie Huang, Robin Walters, Dian Wang, Robert Platt
   - **Summary**: The authors present GSL, a framework for hierarchical policy learning that enhances policy generalization and sample efficiency in robot manipulation. GSL decomposes demonstrations into transferable, object-canonicalized skill primitives using foundation models, ensuring efficient low-level skill learning in the object frame. The structured design leads to substantial improvements in sample efficiency and generalization across unseen tasks.
   - **Year**: 2025

3. **Title**: RoboHiMan: A Hierarchical Evaluation Paradigm for Compositional Generalization in Long-Horizon Manipulation (arXiv:2510.13149)
   - **Authors**: Yangtao Chen, Zixuan Chen, Nga Teng Chan, Junting Chen, Junhui Yin, Jieqi Shi, Yang Gao, Yong-Lu Li, Jing Huo
   - **Summary**: RoboHiMan introduces a hierarchical evaluation paradigm to assess compositional generalization in long-horizon manipulation tasks. The framework includes a benchmark of atomic and compositional tasks under diverse perturbations and proposes evaluation paradigms that probe the necessity of skill composition, revealing bottlenecks in hierarchical architectures. Experiments highlight capability gaps across models, suggesting directions for advancing real-world long-horizon manipulation tasks.
   - **Year**: 2025

4. **Title**: SPECI: Skill Prompts based Hierarchical Continual Imitation Learning for Robot Manipulation (arXiv:2504.15561)
   - **Authors**: Jingkai Xu, Xiangli Nie
   - **Summary**: SPECI is an end-to-end hierarchical continual imitation learning framework for robot manipulation. It comprises a multimodal perception module, a high-level skill inference module for dynamic skill extraction and selection, and a low-level action execution module. SPECI performs continual implicit skill acquisition and reuse via an expandable skill codebook and an attention-driven skill selection mechanism, enhancing task-level knowledge transfer.
   - **Year**: 2025

5. **Title**: Adaptive Step Duration for Precise Foot Placement: Achieving Robust Bipedal Locomotion on Terrains with Restricted Footholds (arXiv:2403.17136)
   - **Authors**: Zhaoyang Xiang, Victor Paredes, Ayonga Hereid
   - **Summary**: This paper introduces a multi-step preview foot placement planning algorithm to enhance bipedal robotic walking across terrains with restricted footholds. The approach uses a discrete-time Model Predictive Control based on the Divergent Component of Motion, adaptively changing step duration for optimal foot placement under constraints, ensuring operational viability over multiple future steps.
   - **Year**: 2024

6. **Title**: BAKU: An Efficient Transformer for Multi-Task Policy Learning in Robotics (arXiv:2406.07539)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: BAKU is a transformer-based architecture designed for multi-task policy learning in robotics. It combines key ideas from prior work into a single, simple model that outperforms state-of-the-art methods in multi-task policy learning across various simulated and real-world domains.
   - **Year**: 2024

7. **Title**: Enabling Robots to Follow Abstract Instructions and Complete Complex Dynamic Tasks (arXiv:2406.11231)
   - **Authors**: Ruaridh Mon-Williams, Gen Li, Ran Long, Wenqian Du, Chris Lucas
   - **Summary**: This work presents a framework combining Large Language Models, a curated Knowledge Base, and Integrated Force and Visual Feedback to interpret abstract instructions and perform long-horizon tasks. The approach translates abstract instructions into actionable steps, generating custom code by employing retrieval-augmented generalization, allowing robots to respond to noise and disturbances during execution.
   - **Year**: 2024

8. **Title**: From Keyboard to Chatbot: An AI-powered Integration Platform with Robotic Agent for Young Learners (arXiv:2405.00750)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper introduces an AI-powered integration platform featuring a robotic agent designed for young learners. The system enables dynamic and engaging experiences by bridging virtual programming with tangible, physical outcomes, enhancing the learning process through interactive robotic agents.
   - **Year**: 2024

9. **Title**: SpatialVLM: Endowing Vision-Language Models with Spatial Reasoning Capabilities (arXiv:2401.12168)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: SpatialVLM aims to enhance vision-language models with spatial reasoning capabilities, enabling them to understand and interpret spatial relationships within visual data. This advancement is crucial for applications requiring spatial awareness and reasoning.
   - **Year**: 2024

10. **Title**: RoboVQA: Multimodal Long-Horizon Reasoning for Robotics (arXiv:2311.00899)
    - **Authors**: Pierre Sermanet, Tianli Ding, Jeffrey Zhao, Fei Xia, Debidatta Dwibedi, Keerthana Gopalakrishnan, Christine Chan, Gabriel Dulac-Arnold, Sharath Maddineni, Nikhil J Joshi, et al.
    - **Summary**: RoboVQA introduces a benchmark for evaluating multimodal long-horizon reasoning in robotics. It focuses on the integration of visual and language understanding to perform complex tasks, highlighting the challenges and potential solutions in this domain.
    - **Year**: 2023

**Key Challenges:**

1. **Semantic-to-Motor Gap**: Translating high-level semantic instructions from Multi-modal Foundation Models (MFMs) into precise, real-time motor commands remains a significant challenge, leading to brittle robot behaviors in dynamic environments.

2. **Computational Efficiency**: Fine-tuning entire MFMs for specific tasks is computationally expensive and often impractical for real-time applications, necessitating more efficient adaptation methods.

3. **Expressiveness of Action Primitives**: Existing approaches that utilize simple action primitives limit the expressiveness and adaptability of robot behaviors, especially in complex tasks requiring nuanced control.

4. **Generalization Across Tasks**: Developing frameworks that can generalize learned skills across diverse tasks and environments is challenging, particularly when dealing with unseen spatial arrangements and object appearances.

5. **Integration of High-Level Reasoning with Low-Level Control**: Effectively bridging the cognitive capabilities of MFMs with the nuanced requirements of low-level control in embodied systems remains an open challenge critical for practical deployment. 