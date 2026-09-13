1. **Title**: nncase: An End-to-End Compiler for Efficient LLM Deployment on Heterogeneous Storage Architectures (arXiv:2512.21571)
   - **Authors**: Hui Guo, Qihang Zheng, Chenghai Huo, Dongliang Guo, Haoqi Yang, Yang Zhang
   - **Summary**: This paper introduces nncase, an open-source compilation framework designed to optimize large language model (LLM) deployment across diverse hardware architectures. It employs an e-graph-based term rewriting engine to address phase ordering issues, facilitating global optimization of computation and data movement. Key components include Auto Vectorize for adapting to heterogeneous computing units, Auto Distribution for parallel strategy optimization, and Auto Schedule for enhancing on-chip cache locality. Evaluations demonstrate nncase's superior performance over existing frameworks like MLC LLM and Intel IPEX, achieving results comparable to hand-optimized implementations on CPUs. ([arxiv.org](https://arxiv.org/abs/2512.21571?utm_source=openai))
   - **Year**: 2025

2. **Title**: Cronus: Efficient LLM Inference on Heterogeneous GPU Clusters via Partially Disaggregated Prefill (arXiv:2509.17357)
   - **Authors**: Yunzhao Liu, Qiang Xu, Y. Charlie Hu
   - **Summary**: Cronus presents a novel system for large language model inference in heterogeneous GPU clusters. It introduces a partially disaggregated prefill strategy that partitions the prefill stage, executing its initial portion on low-end GPUs while overlapping the remaining prefill and decode stages on high-end GPUs. This dynamic workload balancing approach significantly enhances throughput and reduces tail latencies compared to existing methods. ([arxiv.org](https://arxiv.org/abs/2509.17357?utm_source=openai))
   - **Year**: 2025

3. **Title**: Hetis: Serving LLMs in Heterogeneous GPU Clusters with Fine-grained and Dynamic Parallelism (arXiv:2509.08309)
   - **Authors**: Zizhao Mo, Jianxiong Liao, Huanle Xu, Zhi Zhou, Chengzhong Xu
   - **Summary**: Hetis introduces a system tailored for serving large language models in heterogeneous GPU clusters. It addresses memory and computational inefficiencies by employing fine-grained and dynamic parallelism, selectively parallelizing compute-intensive operations and dynamically distributing attention computations to low-end GPUs at a head granularity. An online load dispatching policy continuously optimizes serving performance by balancing network latency, computational load, and memory intensity. Evaluations show improvements in throughput and latency over existing systems. ([arxiv.org](https://arxiv.org/abs/2509.08309?utm_source=openai))
   - **Year**: 2025

4. **Title**: Efficiently Executing High-throughput Lightweight LLM Inference Applications on Heterogeneous Opportunistic GPU Clusters with Pervasive Context Management (arXiv:2510.14024)
   - **Authors**: Thanh Son Phung, Douglas Thain
   - **Summary**: This work addresses the challenges of deploying lightweight LLMs in high-throughput applications on heterogeneous GPU clusters. It proposes "Pervasive Context Management," a technique that decouples LLM initialization from inference, retaining the context in GPUs until no longer needed. This approach reduces execution time and scales opportunistically across available GPUs, demonstrating significant performance improvements in a fact verification application. ([arxiv.org](https://arxiv.org/abs/2510.14024?utm_source=openai))
   - **Year**: 2025

5. **Title**: Optimizing Large Language Models in Distributed Environments: A Holistic Approach to Efficiency, Ethics, and Governance
   - **Authors**: [Not specified]
   - **Summary**: This paper introduces a scalable framework for optimizing LLMs in distributed environments, addressing computational efficiency, ethical fairness, and governance. It proposes a three-tier architecture integrating topology-aware parallelism, communication-efficient gradient aggregation, and memory-aware rematerialization to enhance performance and transparency in LLM deployment. ([link.springer.com](https://link.springer.com/article/10.1007/s44196-025-00992-4?utm_source=openai))
   - **Year**: 2025

6. **Title**: DeepCompile: A Compiler-Driven Approach to Optimizing Distributed Deep Learning Training (arXiv:2504.09983)
   - **Authors**: M. Tanaka, D. Li, U. Chand, A. Zafar, H. Shen, O. Ruwase
   - **Summary**: DeepCompile presents a compiler-driven approach to optimize distributed deep learning training. It focuses on enhancing performance by leveraging compiler techniques to manage computation and communication efficiently across distributed systems. The approach demonstrates improvements in training speed and resource utilization. ([cs.virginia.edu](https://www.cs.virginia.edu/~hs6ms/publications-selected.htm?utm_source=openai))
   - **Year**: 2025

7. **Title**: A Carbon-Efficient Framework for Deep Learning Workloads on GPU Clusters
   - **Authors**: [Not specified]
   - **Summary**: This study introduces the CA-RM framework, designed to manage GPU clusters with a focus on reducing carbon emissions. It achieves over 35% carbon reduction compared to existing methods while maintaining acceptable deep neural network processing performance, making it suitable for sustainable AI data centers. ([mdpi.com](https://www.mdpi.com/2076-3417/16/2/633?utm_source=openai))
   - **Year**: 2025

8. **Title**: LLM-PQ: Serving LLM on Heterogeneous Clusters with Phase-Aware Partition and Adaptive Quantization
   - **Authors**: Juntao Zhao, Borui Wan, Yanghua Peng, Haibin Lin, Chuan Wu
   - **Summary**: LLM-PQ proposes a system for serving large language models on heterogeneous GPU clusters. It introduces phase-aware partitioning and adaptive quantization to improve inference throughput while meeting user-specified model quality targets. The approach effectively balances workload distribution and resource utilization in heterogeneous environments. ([bohrium.dp.tech](https://bohrium.dp.tech/paper/arxiv/2405.06856?utm_source=openai))
   - **Year**: 2024

9. **Title**: Cephalo: Harnessing Heterogeneous GPU Clusters for Efficient LLM Inference
   - **Authors**: Runsheng Benson Guo, Utkarsh Anand, Arthur Chen, Khuzaima Daudjee
   - **Summary**: Cephalo introduces a system that leverages heterogeneous GPU clusters for efficient LLM inference. It focuses on optimizing resource allocation and workload distribution to enhance inference performance, demonstrating significant improvements over existing methods. ([hpcrl.github.io](https://hpcrl.github.io/ICS2025-webpage/program/Proceedings_ICS25/ics25-58.pdf?utm_source=openai))
   - **Year**: 2025

10. **Title**: EdgeLLM: A Highly Efficient CPU-FPGA Heterogeneous Edge Accelerator for Large Language Models
    - **Authors**: Mingqiang Huang, Ao Shen, Kai Li, Haoxiang Peng, Boyu Li, Hao Yu
    - **Summary**: EdgeLLM presents an efficient CPU-FPGA heterogeneous acceleration framework for deploying large language models on edge devices. It introduces a universal data parallelism scheme and fully-customized hardware operators, achieving higher throughput and energy efficiency compared to commercial GPUs. ([bohrium.dp.tech](https://bohrium.dp.tech/paper/arxiv/2405.14371?utm_source=openai))
    - **Year**: 2024

**Key Challenges:**

1. **Hardware Heterogeneity**: Managing and optimizing LLM deployment across diverse hardware architectures, including varying GPU capabilities and configurations, remains complex.

2. **Dynamic Workload Balancing**: Efficiently distributing and balancing workloads in real-time across heterogeneous systems to maximize performance and resource utilization is challenging.

3. **Energy Efficiency and Carbon Footprint**: Reducing the energy consumption and carbon emissions associated with training and deploying large language models is increasingly important for sustainable AI practices.

4. **Compiler Optimization**: Developing compilers that can adaptively optimize code for heterogeneous environments, considering both performance and energy efficiency, is a significant challenge.

5. **Real-time Adaptation**: Implementing systems that can dynamically adjust to changing runtime conditions, such as varying workloads and hardware availability, to maintain optimal performance and efficiency. 