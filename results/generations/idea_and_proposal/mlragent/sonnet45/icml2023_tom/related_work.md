```
1. **Title**: An Explainable Collaborative Dialogue System using a Theory of Mind (arXiv:2302.09646)
   - **Authors**: Philip R. Cohen, Lucian Galescu, Maayan Shvo
   - **Summary**: This paper introduces Eva, a neuro-symbolic, domain-independent, multimodal collaborative dialogue system that assists users by inferring their intentions and plans. Eva maintains and reasons with its own beliefs, goals, and intentions, and explicitly models those of its users, enabling engagement in multi-party dialogues.
   - **Year**: 2023

2. **Title**: MetaMind: Modeling Human Social Thoughts with Metacognitive Multi-Agent Systems (arXiv:2505.18943)
   - **Authors**: Xuanming Zhang, Yuxuan Chen, Min-Hsuan Yeh, Yixuan Li
   - **Summary**: MetaMind is a multi-agent framework inspired by psychological theories of metacognition, designed to emulate human-like social reasoning. It decomposes social understanding into three stages: generating hypotheses about user mental states, refining these hypotheses using cultural norms, and generating contextually appropriate responses.
   - **Year**: 2025

3. **Title**: MuMA-ToM: Multi-modal Multi-Agent Theory of Mind (arXiv:2408.12574)
   - **Authors**: Haojun Shi, Suyu Ye, Xinyu Fang, Chuanyang Jin, Leyla Isik, Yen-Ling Kuo, Tianmin Shu
   - **Summary**: This work introduces MuMA-ToM, a benchmark for evaluating Theory of Mind reasoning in multi-agent interactions using multi-modal information. It provides video and text descriptions of people's interactions in realistic environments and assesses understanding of goals, beliefs, and beliefs about others' goals.
   - **Year**: 2024

4. **Title**: DialSim: A Dialogue Simulator for Evaluating Long-Term Multi-Party Dialogue Understanding of Conversational Agents (arXiv:2406.13144)
   - **Authors**: Jiho Kim, Woosog Chay, Hyeonji Hwang, Daeun Kyung, Hyunseung Chung, Eunbyeol Cho, Yeonsu Kwon, Yohan Jo, Edward Choi
   - **Summary**: DialSim introduces a dialogue simulation-based evaluation framework to assess conversational agents' understanding in long-term, multi-party dialogues. It highlights the challenges agents face in maintaining accurate comprehension over extended interactions.
   - **Year**: 2024

5. **Title**: Theory of Mind for Multi-Agent Collaboration via Large Language Models (arXiv:2310.10701)
   - **Authors**: [Authors not specified]
   - **Summary**: This study evaluates large language model-based agents in cooperative multi-agent tasks requiring Theory of Mind inference, comparing their performance with multi-agent reinforcement learning and planning-based baselines. It explores the use of explicit belief state representations to enhance task performance and ToM accuracy.
   - **Year**: 2023

6. **Title**: Agent-to-Agent Theory of Mind: Testing Interlocutor Awareness among Large Language Models (arXiv:2506.22957)
   - **Authors**: Younwoo Choi, Changling Li, Yongjin Yang, Zhijing Jin
   - **Summary**: This paper formalizes the concept of interlocutor awareness in large language models, examining their ability to identify and adapt to the identity and characteristics of dialogue partners. It evaluates LLMs' capacity to infer reasoning patterns, linguistic styles, and alignment preferences of their interlocutors.
   - **Year**: 2025

7. **Title**: Towards Collaborative Plan Acquisition through Theory of Mind Modeling in Situated Dialogue (IJCAI 2023)
   - **Authors**: Cristian-Paul Bara, Ziqiao Ma, Yingzhuo Yu, Julie Shah, Joyce Chai
   - **Summary**: This work addresses collaborative plan acquisition, where humans and agents learn and communicate to acquire complete plans for joint tasks. It formulates a problem for agents to predict missing task knowledge for themselves and their partners based on perceptual and dialogue history, emphasizing the importance of modeling partners' mental states.
   - **Year**: 2023

8. **Title**: MindCraft: Theory of Mind Modeling for Situated Dialogue in Collaborative Tasks (EMNLP 2021)
   - **Authors**: Cristian-Paul Bara, Sky CH-Wang, Joyce Chai
   - **Summary**: MindCraft introduces a dataset of collaborative tasks performed by human pairs in a 3D virtual environment, capturing partners' beliefs as interactions unfold. It presents computational models for Theory of Mind tasks, aiming to develop AI agents capable of inferring belief states of collaborative partners in situ.
   - **Year**: 2021

9. **Title**: ToM2C: Target-oriented Multi-agent Communication and Cooperation with Theory of Mind (arXiv:2111.09189)
   - **Authors**: Yuanfei Wang, Fangwei Zhong, Jing Xu, Yizhou Wang
   - **Summary**: ToM2C introduces Theory of Mind into multi-agent systems to enhance communication and cooperation. Each agent infers the mental states and intentions of others based on local observations, deciding when and with whom to share intentions, and reaching consensus on sub-goals.
   - **Year**: 2021

10. **Title**: Dialogue State Tracking with Incremental Reasoning (TACL 2021)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper presents a dialogue state tracking approach that simulates the dialogue procedure as a recursive process, where the current joint belief relies on the last joint belief and the current turn belief. It employs a bipartite graph belief propagator to perform belief propagation over the agent's database for belief update.
    - **Year**: 2021
```

**Key Challenges:**

1. **Modeling Nested Beliefs**: Accurately representing and tracking hierarchical mental states in multi-party dialogues remains complex, especially as the depth of nested beliefs increases.

2. **Scalability**: Ensuring that recursive belief state trackers can efficiently handle the combinatorial explosion of possible belief states in dynamic, multi-agent environments.

3. **Data Availability**: The scarcity of annotated datasets with explicit multi-agent belief states hampers the training and evaluation of models designed for hierarchical Theory of Mind reasoning.

4. **Integration with Language Models**: Seamlessly combining structured belief tracking mechanisms with large language models to enhance dialogue understanding without compromising performance.

5. **Evaluation Metrics**: Developing standardized benchmarks and metrics to assess the effectiveness of hierarchical Theory of Mind models in multi-party dialogue systems.
``` 