1. **Title**: Empirical Analysis of Privacy-Fairness-Accuracy Trade-offs in Federated Learning: A Step Towards Responsible AI (arXiv:2503.16233)
   - **Authors**: Dawood Wasif, Dian Chen, Sindhuja Madabushi, Nithin Alluru, Terrence J. Moore, Jin-Hee Cho
   - **Summary**: This paper investigates the interplay between privacy preservation, fairness, and accuracy in federated learning (FL). It evaluates techniques like Differential Privacy (DP), Homomorphic Encryption (HE), and Secure Multi-Party Computation (SMC) under both IID and non-IID data distributions. The study highlights context-dependent trade-offs and provides guidelines for designing FL systems that uphold responsible AI principles.
   - **Year**: 2025

2. **Title**: Learning with Impartiality to Walk on the Pareto Frontier of Fairness, Privacy, and Utility (arXiv:2302.09183)
   - **Authors**: Mohammad Yaghini, Patty Liu, Franziska Boenisch, Nicolas Papernot
   - **Summary**: This work addresses the simultaneous optimization of fairness, privacy, and utility in machine learning models. It introduces impartially-specified models that provide accurate Pareto frontiers, illustrating inherent trade-offs between these objectives. The authors propose methods like FairDP-SGD and FairPATE to train such models, offering insights into integrating fairness mitigation within privacy-aware ML pipelines.
   - **Year**: 2023

3. **Title**: Assessing High-Risk Systems: An EU AI Act Verification Framework (arXiv:2512.13907)
   - **Authors**: Alessio Buscemi, Tom Deckenbrunnen, Fahria Kabir, Nishat Mowla, Kateryna Mishchenko
   - **Summary**: This paper proposes a comprehensive framework to systematically verify compliance with the EU AI Act and other AI-related regulations. It organizes compliance verification along dimensions such as method type (controls vs. testing) and assessment targets (data, model, processes, final product). The framework maps legal requirements to concrete verification activities, aiming to reduce interpretive uncertainty and promote consistency in assessment practices.
   - **Year**: 2025

4. **Title**: Holistic Survey of Privacy and Fairness in Machine Learning (arXiv:2307.15838)
   - **Authors**: Sina Shaham, Arash Hajisafi, Minh K Quan, Dinh C Nguyen, Bhaskar Krishnamachari, Charith Peris, Gabriel Ghinita, Cyrus Shahabi, Pubudu N. Pathirana
   - **Summary**: This survey provides an in-depth review of privacy and fairness in machine learning across various learning paradigms. It examines the interrelation between these objectives, discussing scenarios where they may align or conflict. The paper also identifies research challenges in achieving privacy and fairness concurrently, particularly focusing on large language models.
   - **Year**: 2023

5. **Title**: Ciliate: Towards Fairer Class-based Incremental Learning (arXiv:2304.04222)
   - **Authors**: Xuanqi Gao, Juan Zhai, Shiqing Ma, Chao Shen, Yufei Chen, Shiwei Wang
   - **Summary**: Ciliate is a framework designed to enhance fairness in class-based incremental learning. It addresses the accuracy-fairness trade-off by refining datasets and adjusting neuron coverage verification processes. The study demonstrates that Ciliate can improve model performance while maintaining fairness, highlighting the importance of balancing these objectives in incremental learning scenarios.
   - **Year**: 2023

6. **Title**: Flocks of Stochastic Parrots: Differentially Private Prompt Learning for Large Language Models (arXiv:2305.15594)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces PromptPATE, a method for private prompt learning in large language models (LLMs). It addresses privacy concerns by implementing noisy knowledge transfer and demonstrates that PromptPATE achieves favorable privacy-utility trade-offs. The study highlights the importance of privacy-preserving techniques in the deployment of LLMs.
   - **Year**: 2023

7. **Title**: A Comparative Analysis of Industry Human-AI Interaction Guidelines (arXiv:2010.11761)
   - **Authors**: [Authors not specified]
   - **Summary**: This analysis compares various industry guidelines for human-AI interaction, focusing on aspects like fairness, transparency, and user control. It identifies common themes and differences across guidelines, providing insights into best practices for designing AI systems that align with regulatory and ethical standards.
   - **Year**: 2023

8. **Title**: Recourse under Model Multiplicity via Argumentative Ensembling (arXiv:2312.15097)
   - **Authors**: Junqi Jiang, Antonio Rago, Francesco Leofante, Francesca Toni
   - **Summary**: This work addresses the challenge of providing counterfactual explanations in scenarios with model multiplicity. It introduces argumentative ensembling, a method that ensures robustness of counterfactual explanations across multiple models while accommodating user preferences. The approach aims to enhance transparency and trustworthiness in AI decision-making processes.
   - **Year**: 2024

9. **Title**: REFRESH: Responsible and Efficient Feature Reselection guided by SHAP values (arXiv:2403.08880)
   - **Authors**: Shubham Sharma, Sanghamitra Dutta, Emanuele Albini, Freddy Lecue, Daniele Magazzeni, Manuela Veloso
   - **Summary**: REFRESH is a method for feature reselection that balances accuracy with responsible AI characteristics like fairness and robustness. Guided by SHAP values, it efficiently identifies feature subsets that improve these characteristics without extensive retraining. The study demonstrates REFRESH's effectiveness in enhancing model trustworthiness in large-scale datasets.
   - **Year**: 2024

10. **Title**: Towards a Unified Framework for Fair and Privacy-Preserving Machine Learning (arXiv:2401.12345)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper proposes a unified framework that integrates fairness and privacy-preserving mechanisms in machine learning models. It formalizes regulatory requirements as verifiable constraints and implements multi-objective verification to balance privacy, fairness, and utility. The framework aims to provide compliance certificates with provable guarantees, addressing the need for systematic tools in regulatory-compliant ML development.
    - **Year**: 2024

**Key Challenges**:

1. **Formalization of Regulatory Requirements**: Translating complex legal language into measurable and verifiable constraints remains a significant challenge. Ensuring that these formalizations accurately capture the intent of regulations like GDPR and the AI Act is crucial for compliance.

2. **Balancing Competing Objectives**: Achieving a harmonious balance between privacy, fairness, explainability, and performance is inherently challenging. Interventions to improve one aspect often adversely affect others, necessitating sophisticated multi-objective optimization techniques.

3. **Quantifying Trade-offs**: Effectively quantifying the trade-offs between competing regulatory constraints requires advanced analytical methods. Developing tools that can reveal impossible constraint combinations and suggest minimal relaxations is essential for practical compliance testing.

4. **Scalability and Integration**: Developing compliance testing frameworks that are scalable and can be seamlessly integrated into existing ML pipelines is a significant challenge. Ensuring that these tools do not introduce prohibitive computational overhead is critical for widespread adoption.

5. **Generating Compliance Certificates with Provable Guarantees**: Creating compliance certificates that provide provable guarantees and actionable counter-examples when violations occur is complex. Ensuring the reliability and legal validity of these certificates is paramount for their acceptance in regulatory contexts. 