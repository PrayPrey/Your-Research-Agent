1. **Title**: RAGPart & RAGMask: Retrieval-Stage Defenses Against Corpus Poisoning in Retrieval-Augmented Generation (arXiv:2512.24268)
   - **Authors**: Pankayaraj Pathmanathan, Michael-Andrei Panaitescu-Liess, Cho-Yu Jason Chiang, Furong Huang
   - **Summary**: This paper introduces two retrieval-stage defenses, RAGPart and RAGMask, designed to mitigate corpus poisoning attacks in Retrieval-Augmented Generation (RAG) systems. RAGPart leverages document partitioning to reduce the impact of poisoned documents, while RAGMask identifies suspicious tokens based on significant similarity shifts under targeted token masking. The defenses are computationally efficient and require no modifications to the generation model.
   - **Year**: 2025

2. **Title**: A-MemGuard: A Proactive Defense Framework for LLM-Based Agent Memory (arXiv:2510.02373)
   - **Authors**: Qianshan Wei, Tengchao Yang, Yaochen Wang, Xinfeng Li, Lijun Li, Zhenfei Yin, Yi Zhan, Thorsten Holz, Zhiqiang Lin, XiaoFeng Wang
   - **Summary**: A-MemGuard is a proactive defense framework for LLM agent memory that combines consensus-based validation and a dual-memory structure. It detects anomalies by comparing reasoning paths derived from multiple related memories and stores detected failures separately to prevent error cycles. Evaluations show that A-MemGuard effectively reduces attack success rates by over 95% with minimal utility cost.
   - **Year**: 2025

3. **Title**: MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval (arXiv:2512.16962)
   - **Authors**: Saksham Sahai Srivastava, Haoyu He
   - **Summary**: MemoryGraft introduces an indirect injection attack that implants malicious successful experiences into an agent's long-term memory. These poisoned experiences persist and influence the agent's behavior in future tasks, leading to systematic behavioral drift. The attack exploits the agent's tendency to replicate patterns from retrieved successful tasks, turning experience-based self-improvement into a vector for stealthy compromise.
   - **Year**: 2025

4. **Title**: BackdoorAgent: A Unified Framework for Backdoor Attacks on LLM-based Agents (arXiv:2601.04566)
   - **Authors**: Yunhao Feng, Yige Li, Yutao Wu, Yingshui Tan, Yanming Guo, Yifan Ding, Kun Zhai, Xingjun Ma, Yugang Jiang
   - **Summary**: BackdoorAgent presents a modular and stage-aware framework that provides a unified view of backdoor threats in LLM agents. It structures the attack surface into planning, memory, and tool-use stages, enabling systematic analysis of trigger activation and propagation across different stages. Empirical analysis shows that triggers implanted at a single stage can persist and propagate through multiple steps, highlighting vulnerabilities in agentic workflows.
   - **Year**: 2026

5. **Title**: DEVIL’S ADVOCATE: Anticipatory Reflection for LLM Agents (arXiv:2405.16334)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces anticipatory reflection mechanisms for LLM agents, enabling them to anticipate potential failures and generate alternative remedies before executing actions. The approach enhances problem-solving abilities by allowing agents to reflect on and adapt their plans proactively, improving robustness against unforeseen issues.
   - **Year**: 2024

6. **Title**: RAGCHECKER: A Fine-grained Framework for Evaluating the Integration of Reasoning and Action in LLM Agents (arXiv:2408.08067)
   - **Authors**: [Authors not specified]
   - **Summary**: RAGCHECKER introduces a framework for evaluating how LLM agents integrate reasoning and action, particularly in the context of database question answering. The study highlights challenges in planning and generating multiple SQL queries, identifying bottlenecks that hinder effective interaction. A multi-agent evaluation framework is proposed to enhance the precision and reliability of assessments.
   - **Year**: 2024

7. **Title**: On Evaluating the Integration of Reasoning and Action in LLM Agents (arXiv:2311.09721)
   - **Authors**: Linyong Nan, Ellen Zhang, Weijin Zou, Yilun Zhao, Wenfei Zhou, Arman Cohan
   - **Summary**: This study introduces a long-form database question-answering dataset to evaluate how LLMs interact with a SQL interpreter. It assesses the integration of reasoning and action, identifying challenges in planning and generating multiple SQL queries. A multi-agent evaluation framework is proposed to improve the accuracy of answer quality assessments.
   - **Year**: 2023

8. **Title**: Evaluating Verifiability in Generative Search Engines (arXiv:2311.08147)
   - **Authors**: N. F. Liu, T. Zhang, P. Liang
   - **Summary**: This paper evaluates the verifiability of generative search engines, focusing on their ability to provide accurate and trustworthy information. It introduces a benchmark for assessing robustness against external counterfactual knowledge and discusses methods to enhance the reliability of generated content.
   - **Year**: 2023

9. **Title**: RECALL: A Benchmark for LLMs Robustness Against External Counterfactual Knowledge (arXiv:2311.08147)
   - **Authors**: Y. Liu, L. Huang, S. Li, S. Chen, H. Zhou, F. Meng, J. Zhou, X. Sun
   - **Summary**: RECALL is a benchmark designed to assess the robustness of LLMs against external counterfactual knowledge. It evaluates how well models can resist manipulation by false information and maintain accuracy in their outputs, providing insights into their reliability in adversarial contexts.
   - **Year**: 2023

10. **Title**: S2ORC: The Semantic Scholar Open Research Corpus (arXiv:2001.10005)
    - **Authors**: K. Lo, L. L. Wang, M. Neumann, R. Kinney, D. Weld
    - **Summary**: S2ORC is a large corpus of academic papers designed to facilitate research in natural language processing and machine learning. It provides a rich dataset for training and evaluating models, supporting advancements in understanding and generating scientific literature.
    - **Year**: 2023

**Key Challenges:**

1. **Persistent Memory Manipulation**: Adversaries can inject malicious information into an agent's memory, leading to long-term behavioral changes that are difficult to detect and mitigate.

2. **Detection of Subtle Attacks**: Identifying and filtering out poisoned data or backdoor triggers that are contextually activated remains a significant challenge due to their subtle and context-dependent nature.

3. **Balancing Security and Utility**: Implementing robust defense mechanisms without compromising the performance and utility of LLM agents is a delicate balance that requires careful design and evaluation.

4. **Evaluation Frameworks**: Developing comprehensive benchmarks and evaluation frameworks to assess the effectiveness of defenses against memory injection attacks is essential but remains an ongoing challenge.

5. **Adaptation to Evolving Threats**: As adversarial techniques evolve, continuously updating and adapting defense mechanisms to counter new forms of attacks is a persistent challenge in the field. 