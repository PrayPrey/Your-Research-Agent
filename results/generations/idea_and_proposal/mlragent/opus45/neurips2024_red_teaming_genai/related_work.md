Here is a literature review on the topic of "Adaptive Red Teaming via Reinforcement Learning with Evolving Attack Taxonomies," focusing on papers published between 2023 and 2025.

**1. Related Papers**

1. **Title**: Active Attacks: Red-teaming LLMs via Adaptive Environments (arXiv:2509.21947)
   - **Authors**: Taeyoung Yun, Pierre-Luc St-Charles, Jinkyoo Park, Yoshua Bengio, Minsu Kim
   - **Summary**: This paper introduces "Active Attacks," an RL-based red-teaming algorithm that adapts its attacks as the victim model evolves. By periodically fine-tuning the victim LLM with collected attack prompts, the method encourages exploration of new vulnerabilities, leading to a comprehensive coverage of potential attack modes.
   - **Year**: 2025

2. **Title**: Red-Bandit: Test-Time Adaptation for LLM Red-Teaming via Bandit-Guided LoRA Experts (arXiv:2510.07239)
   - **Authors**: Christos Ziakas, Nicholas Loo, Nishita Jain, Alessandra Russo
   - **Summary**: Red-Bandit presents a framework that adapts online to identify and exploit model-specific vulnerabilities using a set of LoRA experts specialized in various attack styles. A multi-armed bandit policy dynamically selects among these experts, balancing exploration and exploitation to uncover unsafe behaviors in LLMs.
   - **Year**: 2025

3. **Title**: AgenticRed: Optimizing Agentic Systems for Automated Red-teaming (arXiv:2601.13518)
   - **Authors**: Jiayi Yuan, Jonathan Nöther, Natasha Jaques, Goran Radanović
   - **Summary**: AgenticRed leverages LLMs' in-context learning to iteratively design and refine red-teaming systems without human intervention. By treating red-teaming as a system design problem, it evolves agentic systems using evolutionary selection, achieving high attack success rates and strong transferability to proprietary models.
   - **Year**: 2026

4. **Title**: AutoRedTeamer: Autonomous Red Teaming with Lifelong Attack Integration (arXiv:2503.15754)
   - **Authors**: Andy Zhou, Kevin Wu, Francesco Pinto, Zhaorun Chen, Yi Zeng, Yu Yang, Shuang Yang, Sanmi Koyejo, James Zou, Bo Li
   - **Summary**: AutoRedTeamer introduces a fully automated red-teaming framework combining a multi-agent architecture with a memory-guided attack selection mechanism. It continuously discovers and integrates new attack vectors, adapting to emerging threats while maintaining strong performance on existing ones.
   - **Year**: 2025

5. **Title**: SLEEPER AGENTS: TRAINING DECEPTIVE LLMS THAT
   - **Authors**: [Authors not specified]
   - **Summary**: This paper explores strategies to detect and mitigate model poisoning and deceptive alignment beyond standard safety fine-tuning. It examines the use of LLMs to generate red-teaming inputs designed to elicit undesirable behavior, highlighting the challenges in detecting and training away backdoors.
   - **Year**: 2024

6. **Title**: Learning to Attack: Towards Textual Adversarial Attacking in
   - **Authors**: Yuan Zang, Bairu Hou, Fanchao Qi, Zhiyuan Liu, Xiaojun Meng, Maosong Sun
   - **Summary**: This work proposes a reinforcement learning-based attack model that learns from attack history to launch more efficient textual adversarial attacks. It demonstrates improved attack performance and efficiency across various NLP tasks, highlighting the potential of RL in adversarial settings.
   - **Year**: 2024

7. **Title**: Red Teaming
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses the application of red teaming in AI security, emphasizing the importance of systematic stress-testing of AI systems to uncover vulnerabilities. It highlights the need for ongoing red team exercises to keep pace with rapidly evolving AI technologies.
   - **Year**: 2024

**2. Key Challenges**

1. **Dynamic Nature of AI Models**: As AI models rapidly evolve, static benchmarks and attack strategies become obsolete, necessitating continuous adaptation in red teaming approaches.

2. **Exploration of Vast Vulnerability Spaces**: Systematically exploring the combinatorial space of potential vulnerabilities is challenging, often leaving critical blind spots in safety evaluations.

3. **Balancing Exploration and Exploitation**: Developing methods that effectively balance the discovery of new attack vectors (exploration) with the optimization of known successful strategies (exploitation) remains a significant challenge.

4. **Automated Taxonomy Development**: Creating and maintaining an evolving taxonomy of attack strategies without human intervention requires sophisticated clustering and categorization techniques.

5. **Transferability Across Models**: Ensuring that red teaming strategies are effective across different AI models, including proprietary ones, poses challenges in generalization and adaptability. 