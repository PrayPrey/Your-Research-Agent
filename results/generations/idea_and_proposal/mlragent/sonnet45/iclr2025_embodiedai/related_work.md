1. **Title**: Mem4Nav: Boosting Vision-and-Language Navigation in Urban Environments with a Hierarchical Spatial-Cognition Long-Short Memory System (arXiv:2506.19433)
   - **Authors**: Lixuan He, Haoyu Dong, Zhenxing Chen, Yangcheng Yu, Jie Feng, Yong Li
   - **Summary**: Mem4Nav introduces a hierarchical spatial-cognition memory system to enhance vision-and-language navigation in urban settings. It combines a sparse octree for fine-grained voxel indexing with a semantic topology graph for high-level landmark connectivity. The system employs long-term and short-term memory modules to store and retrieve spatial experiences, leading to improved navigation accuracy and efficiency.
   - **Year**: 2025

2. **Title**: CityNavAgent: Aerial Vision-and-Language Navigation with Hierarchical Semantic Planning and Global Memory (arXiv:2505.05622)
   - **Authors**: Weichen Zhang, Chen Gao, Shiquan Yu, Ruiying Peng, Baining Zhao, Qian Zhang, Jinqiang Cui, Xinlei Chen, Yong Li
   - **Summary**: CityNavAgent presents an LLM-empowered agent designed for aerial vision-and-language navigation in urban environments. It features a hierarchical semantic planning module that decomposes long-horizon tasks into sub-goals and a global memory module that stores historical trajectories in a topological graph. This approach significantly reduces navigation complexity and enhances performance in urban aerial navigation tasks.
   - **Year**: 2025

3. **Title**: SSR-ZSON: Zero-Shot Object Navigation via Spatial-Semantic Relations within a Hierarchical Exploration Framework (arXiv:2509.24763)
   - **Authors**: Xiangyi Meng, Delun Li, Zihao Mao, Yi Yang, Wenjie Song
   - **Summary**: SSR-ZSON addresses zero-shot object navigation in unknown environments by integrating a viewpoint generation strategy that balances spatial coverage and semantic density with an LLM-based global guidance mechanism. This method prioritizes areas of high semantic density and assesses semantic associations to direct navigation, resulting in improved success rates and efficiency.
   - **Year**: 2025

4. **Title**: GeoNav: Empowering MLLMs with Explicit Geospatial Reasoning Abilities for Language-Goal Aerial Navigation (arXiv:2504.09587)
   - **Authors**: Haotian Xu, Yue Hu, Chen Gao, Zhengqiu Zhu, Yong Zhao, Yong Li, Quanjun Yin
   - **Summary**: GeoNav introduces a geospatially aware multimodal agent for long-range language-goal aerial navigation. It operates in three phases—landmark navigation, target search, and precise localization—mimicking human coarse-to-fine spatial strategies. The system dynamically builds a global cognitive map and a local scene graph, enabling efficient and interpretable decision-making across navigation stages.
   - **Year**: 2025

5. **Title**: A Biologically-Inspired Dual Stream World Model (arXiv:2209.08035)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper proposes a Dual Stream World Model (DSWM) inspired by human cognitive processes, utilizing separate context and content streams, a differentiable memory store, and a forward model over context variables. The model outperforms single-stream world models in generative modeling tasks and learns latent representations resembling place cells, serving as a useful basis for downstream reinforcement learning tasks.
   - **Year**: 2022

6. **Title**: IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING (arXiv:2104.13030)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper provides a comprehensive comparison of methods modeling temporal and sequential effects in recommender systems, including recurrent neural networks, memory network-based models, and attention-based models. It discusses the evolution of user and item embeddings over time and the application of memory networks to capture long-term user interests.
   - **Year**: 2021

7. **Title**: AutoML: A Survey of the State-of-the-Art (arXiv:1908.00709v2)
   - **Authors**: [Authors not specified]
   - **Summary**: This survey reviews the state-of-the-art in automated machine learning (AutoML), focusing on neural architecture search (NAS) methods. It discusses various search spaces, including cell-based and hierarchical structures, and highlights the challenges and advancements in designing efficient and transferable neural architectures.
   - **Year**: 2019

8. **Title**: Video Question Answering: Datasets, Algorithms and Challenges (arXiv:2203.01225)
   - **Authors**: Yaoyao Zhong, Junbin Xiao, Wei Ji, Yicong Li, Weihong Deng, Tat-Seng Chua
   - **Summary**: This survey organizes recent advances in video question answering (VideoQA), categorizing datasets and summarizing techniques such as spatio-temporal attention, motion-appearance memory, and graph-structured methods. It discusses the challenges in comprehending questions and deriving correct answers in VideoQA tasks.
   - **Year**: 2022

9. **Title**: P/D-Serve: Serving Disaggregated Large Language Model at Scale (arXiv:2408.08147)
   - **Authors**: [Authors not specified]
   - **Summary**: P/D-Serve introduces a system for serving disaggregated large language models at scale, addressing challenges in batch scheduling and memory utilization. It proposes a fine-grained organization of prefill and decoding instances, on-demand forwarding, and efficient KVCache transfer to improve inference performance and throughput.
   - **Year**: 2024

10. **Title**: Mem4Nav: Boosting Vision-and-Language Navigation in Urban Environments with a Hierarchical Spatial-Cognition Long-Short Memory System (arXiv:2506.19433)
    - **Authors**: Lixuan He, Haoyu Dong, Zhenxing Chen, Yangcheng Yu, Jie Feng, Yong Li
    - **Summary**: Mem4Nav introduces a hierarchical spatial-cognition memory system to enhance vision-and-language navigation in urban settings. It combines a sparse octree for fine-grained voxel indexing with a semantic topology graph for high-level landmark connectivity. The system employs long-term and short-term memory modules to store and retrieve spatial experiences, leading to improved navigation accuracy and efficiency.
    - **Year**: 2025

**Key Challenges:**

1. **Limited Context Windows in LLMs**: LLMs often have fixed context windows, restricting their ability to maintain and utilize long-term spatial information necessary for coherent navigation in extensive urban environments.

2. **Lack of Persistent Spatial Memory**: Current LLM agents lack mechanisms to build and retrieve persistent spatial memories, hindering their capacity to perform tasks requiring historical awareness and spatial coherence.

3. **Efficient Integration of Multimodal Inputs**: Processing and integrating diverse perceptual inputs such as street views, GPS data, and landmarks into a unified spatial representation pose significant challenges for LLM-based navigation systems.

4. **Dynamic and Complex Urban Environments**: Urban settings are dynamic and complex, requiring navigation systems to adapt to changing conditions and unexpected obstacles, which is challenging for LLMs lacking real-time spatial reasoning capabilities.

5. **Generalization to Novel Urban Areas**: Ensuring that LLM-based navigation systems can generalize learned spatial reasoning to unfamiliar urban areas remains a significant challenge, necessitating robust and flexible memory architectures. 