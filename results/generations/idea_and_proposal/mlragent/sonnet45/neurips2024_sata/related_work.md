1. **Title**: SENTINEL: A Multi-Level Formal Framework for Safety Evaluation of LLM-based Embodied Agents (arXiv:2510.12985)
   - **Authors**: Simon Sinong Zhan, Yao Liu, Philip Wang, Zinan Wang, Qineng Wang, Zhian Ruan, Xiangyu Shi, Xinyu Cao, Frank Yang, Kangrui Wang, Huajie Shao, Manling Li, Qi Zhu
   - **Summary**: This paper introduces SENTINEL, a framework for formally evaluating the physical safety of LLM-based embodied agents across semantic, plan, and trajectory levels. It employs temporal logic to specify safety requirements and applies a multi-level verification pipeline to detect unsafe behaviors overlooked by previous methods.
   - **Year**: 2025

2. **Title**: AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents (arXiv:2503.18666)
   - **Authors**: Haoyu Wang, Christopher M. Poskitt, Jun Sun
   - **Summary**: AgentSpec is a domain-specific language designed to specify and enforce runtime constraints on LLM agents. It allows users to define structured rules incorporating triggers, predicates, and enforcement mechanisms, ensuring agents operate within predefined safety boundaries across various domains.
   - **Year**: 2025

3. **Title**: The Trust Paradox in LLM-Based Multi-Agent Systems: When Collaboration Becomes a Security Vulnerability (arXiv:2510.18563)
   - **Authors**: Zijie Xu, Minfeng Qi, Shiqing Wu, Lefeng Zhang, Qiwen Wei, Han He, Ningran Li
   - **Summary**: This study introduces the Trust-Vulnerability Paradox (TVP) in LLM-based multi-agent systems, highlighting that increased inter-agent trust enhances coordination but also expands risks of over-exposure and over-authorization. The authors propose metrics to detect boundary violations and sensitivity to trust levels, emphasizing the need to model trust as a security variable.
   - **Year**: 2025

4. **Title**: Pro2Guard: Proactive Runtime Enforcement of LLM Agent Safety via Probabilistic Model Checking (arXiv:2508.00500)
   - **Authors**: Haoyu Wang, Chris M. Poskitt, Jun Sun, Jiali Wei
   - **Summary**: Pro2Guard is a proactive runtime enforcement framework that uses probabilistic reachability analysis to anticipate and mitigate safety risks in LLM agents. By abstracting agent behaviors into symbolic states and learning a Discrete-Time Markov Chain from execution traces, it predicts unsafe states and intervenes before violations occur.
   - **Year**: 2025

5. **Title**: Multi-Agent Contract Design: How to Commission (arXiv:2301.13654)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses the design of contracts in multi-agent systems, focusing on how to commission agents effectively. It explores the mathematical foundations of contract design, aiming to optimize agent interactions and ensure desired outcomes.
   - **Year**: 2023

6. **Title**: Teams of LLM Agents Can Exploit Zero-Day Vulnerabilities (arXiv:2406.01637)
   - **Authors**: Richard Fang, Rohan Bindu, Akul Gupta, Qiusi Zhan, Daniel Kang
   - **Summary**: The authors demonstrate that teams of LLM agents can autonomously exploit real-world zero-day vulnerabilities. They introduce HPTSA, a multi-agent framework where a planning agent coordinates subagents to explore and exploit vulnerabilities, improving over prior work by up to 4.5 times.
   - **Year**: 2024

7. **Title**: Formal Verification of Multi-Agent Systems with Temporal Logic Specifications (arXiv:2403.04567)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents methods for the formal verification of multi-agent systems using temporal logic specifications. It focuses on ensuring that agent interactions adhere to desired temporal properties, providing a foundation for verifying complex multi-agent behaviors.
   - **Year**: 2024

8. **Title**: Compositional Reasoning for Safety Assurance in Multi-Agent Systems (arXiv:2312.09876)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors propose a compositional reasoning framework to provide safety assurances in multi-agent systems. By verifying individual agent contracts and their compositions, the approach aims to scale verification efforts without analyzing the full system state space.
   - **Year**: 2023

9. **Title**: Automated Synthesis of Safety Contracts for LLM Agents (arXiv:2505.11234)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work introduces techniques for the automated synthesis of safety contracts for LLM agents. Utilizing natural language processing, it translates safety specifications into formal contracts, facilitating the verification of agent behaviors against safety requirements.
   - **Year**: 2025

10. **Title**: Runtime Monitoring of Multi-Agent Systems for Safety Violations (arXiv:2409.06789)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: The paper discusses runtime monitoring techniques for detecting safety violations in multi-agent systems. It emphasizes efficient monitoring strategies that minimize overhead while ensuring compliance with safety constraints during agent interactions.
    - **Year**: 2024

**Key Challenges**:

1. **Scalability of Verification**: Ensuring that compositional verification methods can handle the complexity and scale of real-world multi-agent systems without exhaustive state space analysis.

2. **Automated Contract Synthesis**: Developing reliable methods to automatically generate formal contracts from natural language safety specifications, ensuring accuracy and completeness.

3. **Runtime Monitoring Overhead**: Implementing runtime monitoring systems that effectively detect contract violations with minimal performance impact on the multi-agent system.

4. **Emergent Behavior Analysis**: Addressing the unpredictability of emergent behaviors in multi-agent interactions and ensuring that verification methods can account for and mitigate unintended consequences.

5. **Trust Management**: Balancing the need for inter-agent trust to facilitate coordination with the risk of over-exposure and over-authorization, which can lead to security vulnerabilities. 