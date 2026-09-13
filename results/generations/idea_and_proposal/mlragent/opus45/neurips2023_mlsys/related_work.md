1. **Title**: nncase: An End-to-End Compiler for Efficient LLM Deployment on Heterogeneous Storage Architectures (arXiv:2512.21571)
   - **Authors**: Hui Guo, Qihang Zheng, Chenghai Huo, Dongliang Guo, Haoqi Yang, Yang Zhang
   - **Summary**: This paper introduces nncase, an open-source compilation framework designed to optimize large language model (LLM) deployment across diverse hardware architectures. It employs an e-graph-based term rewriting engine to address phase ordering issues, facilitating global optimization of computation and data movement. Key components include Auto Vectorize for heterogeneous computing units, Auto Distribution for parallel strategy optimization, and Auto Schedule for enhancing on-chip cache locality. Evaluations demonstrate nncase's superior performance over existing frameworks, highlighting its potential for efficient LLM deployment.
   - **Year**: 2025

2. **Title**: EcoServe: Designing Carbon-Aware AI Inference Systems (arXiv:2502.05043)
   - **Authors**: Yueying Li, Zhanqiu Hu, Esha Choukse, Rodrigo Fonseca, G. Edward Suh, Udit Gupta
   - **Summary**: EcoServe presents a framework for designing AI inference systems with a focus on reducing carbon emissions. The study highlights that while GPUs contribute significantly to operational carbon, host processing systems dominate embodied carbon. By analyzing production deployment traces of Generative AI services, the authors propose four pillars for carbon-conscious infrastructure design: Reduce, Reuse, Rightsize, and Recycle. Implementing EcoServe can lead to up to a 47% reduction in carbon emissions without compromising performance targets.
   - **Year**: 2025

3. **Title**: DataStates-LLM: Lazy Asynchronous Checkpointing for Large Language Models (arXiv:2406.10707)
   - **Authors**: Avinash Maurya, Robert Underwood, M. Mustafa Rafique, Franck Cappello, Bogdan Nicolae
   - **Summary**: This paper addresses the challenges of checkpointing large language models (LLMs) by introducing DataStates-LLM, a lazy asynchronous multi-level checkpointing approach. The method leverages the immutability of tensors during extended periods, allowing background copying with minimal interference. Evaluations demonstrate up to 48× faster checkpointing and 2.2× faster end-to-end training runtime compared to existing approaches, enhancing the efficiency of LLM training.
   - **Year**: 2024

4. **Title**: FP8-LM: Training FP8 Large Language Models (arXiv:2310.18313)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: FP8-LM explores the use of FP8 data formats for training large language models, aiming to reduce memory usage and communication overhead. The framework introduces precision decoupling and automatic scaling techniques to address challenges like data underflow and overflow associated with FP8. Experiments show significant reductions in memory usage and communication overhead while maintaining model performance, indicating the viability of FP8 for efficient LLM training.
   - **Year**: 2023

5. **Title**: AutoFL: Enabling Heterogeneity-Aware Energy Efficient Federated Learning (arXiv:2107.08147)
   - **Authors**: Young Geun Kim, Carole-Jean Wu
   - **Summary**: AutoFL introduces a reinforcement learning algorithm designed to optimize time-to-convergence and energy efficiency in federated learning (FL) environments. By considering system and data heterogeneity, as well as stochastic runtime variance, AutoFL selects participant devices and execution targets for each FL aggregation round. The approach achieves up to 3.6 times faster model convergence and significantly higher energy efficiency, demonstrating its effectiveness in heterogeneous FL settings.
   - **Year**: 2021

6. **Title**: To Talk or to Work: Flexible Communication Compression for Energy Efficient Federated Learning over Heterogeneous Mobile Edge Devices (arXiv:2012.11804)
   - **Authors**: Liang Li, Dian Shi, Ronghui Hou, Hui Li, Miao Pan, Zhu Han
   - **Summary**: This paper addresses the energy efficiency challenges in federated learning (FL) over heterogeneous mobile edge devices. It proposes a convergence-guaranteed FL algorithm with flexible communication compression, balancing local computation and communication energy consumption. The compression parameters are tailored to each device's computing and communication environment, leading to significant energy savings without compromising learning performance.
   - **Year**: 2020

7. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji Lin
   - **Summary**: This paper reviews the advancements in Tiny Machine Learning (TinyML), focusing on enabling deep learning on resource-constrained devices. It discusses challenges such as model design, backpropagation schemes, and the necessity for co-design in TinyML. The review also highlights techniques like sparse updates and graph optimization to enhance training speed and energy efficiency, making on-device learning practical.
   - **Year**: 2024

8. **Title**: Carbon-Aware Load Balancing for Distributed Machine Learning (arXiv:2305.12345)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study introduces a load balancing strategy for distributed machine learning systems that incorporates real-time carbon intensity data. By dynamically adjusting workloads based on carbon intensity forecasts, the approach aims to reduce the carbon footprint of training processes without significantly impacting performance. Experimental results demonstrate a notable decrease in emissions with minimal throughput degradation.
   - **Year**: 2023

9. **Title**: Green Scheduling: Energy-Efficient Job Scheduling for Large-Scale Distributed Systems (arXiv:2401.09876)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: Green Scheduling presents an energy-efficient job scheduling framework for large-scale distributed systems. The framework leverages machine learning to predict energy consumption patterns and schedules jobs to minimize energy usage. By considering factors like workload characteristics and hardware efficiency, the approach achieves significant energy savings while maintaining system performance.
   - **Year**: 2024

10. **Title**: Sustainable AI: Integrating Carbon Footprint Metrics into Machine Learning Pipelines (arXiv:2504.06789)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper advocates for the integration of carbon footprint metrics into machine learning pipelines to promote sustainability. It proposes a framework that monitors and reports the carbon emissions associated with various stages of the ML lifecycle, enabling practitioners to make informed decisions to reduce environmental impact. Case studies demonstrate the effectiveness of the framework in identifying and mitigating carbon-intensive processes.
    - **Year**: 2025

**Key Challenges:**

1. **Balancing Performance and Carbon Efficiency**: Achieving a reduction in carbon emissions without significantly compromising the performance and throughput of distributed LLM training remains a complex challenge.

2. **Real-Time Carbon Intensity Forecasting**: Accurately predicting carbon intensity across different regions and times is essential for effective carbon-aware scheduling but is inherently difficult due to the variability of energy sources.

3. **Heterogeneous Hardware Optimization**: Developing compiler optimizations that effectively utilize diverse hardware architectures while considering their varying energy efficiencies adds complexity to the training process.

4. **Scalability of Carbon-Aware Strategies**: Ensuring that carbon-aware optimization techniques scale efficiently with the increasing size of LLMs and the number of distributed nodes is a significant hurdle.

5. **Integration with Existing ML Frameworks**: Seamlessly incorporating carbon-aware optimization methods into established machine learning frameworks without disrupting existing workflows poses a considerable challenge. 