1. **Title**: Lyra: Orchestrating Dual Correction in Automated Theorem Proving (arXiv:2309.15806)
   - **Authors**: Chuanyang Zheng, Haiming Wang, Enze Xie, Zhengying Liu, Jiankai Sun, Huajian Xin, Jianhao Shen, Zhenguo Li, Yu Li
   - **Summary**: This paper introduces Lyra, a framework that enhances large language models (LLMs) in formal theorem proving by implementing two correction mechanisms: Tool Correction (TC) and Conjecture Correction (CC). TC utilizes predefined prover tools to replace incorrect tools, mitigating hallucinations, while CC refines formal proof conjectures using prover error messages. Lyra achieved state-of-the-art performance on the miniF2F benchmark, improving validation accuracy from 48.0% to 55.3% and test accuracy from 45.5% to 51.2%.
   - **Year**: 2023

2. **Title**: APOLLO: Automated LLM and Lean Collaboration for Advanced Formal Reasoning (arXiv:2505.05758)
   - **Authors**: Azim Ospanov, Roozbeh Yousefzadeh
   - **Summary**: APOLLO is a modular, model-agnostic pipeline that combines the Lean compiler with LLMs to improve proof generation efficiency and correctness. It automates the process of generating proofs, analyzing and fixing syntax errors, identifying mistakes using Lean, isolating failing sub-lemmas, and invoking LLMs on remaining goals with a low top-K budget. APOLLO achieved a new state-of-the-art accuracy of 75.0% on the miniF2F benchmark among 7B-parameter models, with a sampling budget below one thousand.
   - **Year**: 2025

3. **Title**: ProofBridge: Auto-Formalization of Natural Language Proofs in Lean via Joint Embeddings (arXiv:2510.15681)
   - **Authors**: Prithwish Jana, Kaan Kale, Ahmet Ege Tanriverdi, Cruise Song, Sriram Vishwanath, Vijay Ganesh
   - **Summary**: ProofBridge presents a unified framework for translating natural language theorems and proofs into Lean 4. It employs a joint embedding model that aligns natural language and formal language theorem-proof pairs in a shared semantic space, enabling cross-modal retrieval of semantically relevant examples to guide translation. The framework integrates retrieval-augmented fine-tuning with iterative proof repair, leveraging Lean's type checker and semantic equivalence feedback to ensure syntactic correctness and semantic fidelity. Experiments showed substantial improvements in proof auto-formalization over strong baselines.
   - **Year**: 2025

4. **Title**: ProofNet++: A Neuro-Symbolic System for Formal Proof Verification with Self-Correction (arXiv:2505.24230)
   - **Authors**: Murari Ambati
   - **Summary**: ProofNet++ is a neuro-symbolic framework that enhances automated theorem proving by combining LLMs with formal proof verification and self-correction mechanisms. It integrates symbolic proof tree supervision, a reinforcement learning loop using verifiers as reward functions, and an iterative self-correction module. Experiments on miniF2F, Lean's mathlib, and HOL Light demonstrated significant improvements in proof accuracy, correctness, and formal verifiability over prior models.
   - **Year**: 2025

5. **Title**: Certifying Robustness of Convolutional Neural Networks with Tight Linear Approximation (arXiv:2211.09810)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper addresses the certification of robustness in convolutional neural networks (CNNs) by proposing a tight linear approximation method. The approach aims to provide more accurate robustness guarantees for CNNs, which is crucial for applications requiring high reliability.
   - **Year**: 2022

6. **Title**: The XZZX Surface Code (arXiv:2009.07851)
   - **Authors**: J. Pablo Bonilla Ataides, David K. Tuckett, Stephen D. Bartlett, Steven T. Flammia, Benjamin J. Brown
   - **Summary**: This paper introduces the XZZX surface code, a variant of the surface code that offers remarkable performance for fault-tolerant quantum computation. The code achieves error thresholds matching those of random codes for every single-qubit Pauli noise channel and demonstrates favorable sub-threshold resource scaling.
   - **Year**: 2021

7. **Title**: Meta-Weight Graph Neural Network: Push the Limits Beyond Global Homophily (arXiv:2203.10280)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper presents the Meta-Weight Graph Neural Network, which aims to address limitations in graph neural networks related to global homophily. The approach involves novel weighting mechanisms to enhance performance on graphs with diverse structures.
   - **Year**: 2022

8. **Title**: Symbolic Abstractions for Quantum Protocol Verification (arXiv:1904.04186)
   - **Authors**: Lucca Hirschi
   - **Summary**: This paper proposes symbolic abstractions for the verification of quantum protocols, aiming to provide formal and automated verification techniques that can exhaustively explore all possible intruder behaviors and scale well. The approach is motivated by the need for rigorous security proofs in quantum protocol design.
   - **Year**: 2019

**Key Challenges**:

1. **Error Localization**: Accurately identifying erroneous steps within complex proof structures remains challenging, as errors can be subtle and dispersed throughout the proof.

2. **Repair Strategy Generation**: Developing effective repair strategies requires models to understand and generate valid proof steps, which demands a deep comprehension of formal logic and theorem-proving tactics.

3. **Verification Integration**: Ensuring that repair suggestions are formally verified before integration is essential but computationally intensive, potentially hindering the efficiency of the proof repair process.

4. **Data Availability**: Access to large-scale, high-quality proof corpora and human proof edits is limited, which constrains the training and evaluation of neural proof repair systems.

5. **Generalization to Other Domains**: Adapting proof repair frameworks to related areas such as software verification and formal code generation presents challenges due to domain-specific differences in logic and proof structures. 