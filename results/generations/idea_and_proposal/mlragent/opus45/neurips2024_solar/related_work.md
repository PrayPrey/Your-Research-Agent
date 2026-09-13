1. **Title**: Mitigating Group-Level Fairness Disparities in Federated Visual Language Models (arXiv:2505.01851)
   - **Authors**: Chaomeng Chen, Zitong Yu, Junhao Dong, Sen Su, Linlin Shen, Shutao Xia, Xiaochun Cao
   - **Summary**: This paper introduces FVL-FP, a framework combining federated learning with fair prompt tuning to address demographic biases in visual language models. It features cross-layer demographic fair prompting, demographic subspace orthogonal projection, and fair-aware prompt fusion, achieving a 45% reduction in demographic disparity while maintaining task performance.
   - **Year**: 2025

2. **Title**: DAIQ: Auditing Demographic Attribute Inference from Question in LLMs (arXiv:2508.15830)
   - **Authors**: Srikant Panda, Hitesh Laxmichand Patel, Shahad Al-Khalifa, Amit Agarwal, Hend Al-Khalifa, Sharefah Al-Ghamdi
   - **Summary**: The authors present DAIQ, a framework for auditing large language models' ability to infer user demographic attributes from neutral questions. They demonstrate that LLMs can assign demographic labels based solely on question phrasing, posing risks to privacy and fairness. A prompt-based guardrail is proposed to mitigate these inferences.
   - **Year**: 2025

3. **Title**: Toward Fair Federated Learning under Demographic Disparities and Data Imbalance (arXiv:2505.09295)
   - **Authors**: Qiming Wu, Siqi Li, Doudou Zhou, Nan Liu
   - **Summary**: This work introduces FedIDA, a method combining fairness-aware regularization with group-conditional oversampling to address fairness in federated learning amidst demographic disparities and data imbalance. Theoretical analysis and empirical results show improved fairness without compromising predictive performance.
   - **Year**: 2025

4. **Title**: Prompt Fairness: Sub-group Disparities in LLMs (arXiv:2511.19956)
   - **Authors**: Meiyu Zhong, Noel Teku, Ravi Tandon
   - **Summary**: The paper investigates prompt fairness in large language models, highlighting how different prompt phrasings can lead to varied responses across demographic subgroups. Information-theoretic metrics are proposed to quantify subgroup sensitivity and cross-group consistency, with interventions like majority voting and prompt neutralization suggested to enhance fairness.
   - **Year**: 2025

5. **Title**: Why Don’t Prompt-Based Fairness Metrics Correlate? (arXiv:2406.05918)
   - **Authors**: [Authors not specified]
   - **Summary**: This study examines the lack of correlation among prompt-based fairness metrics in language models. It identifies factors such as prompt structure, distribution, and lexical semantics that influence bias measurements, proposing methods to enhance metric correlation.
   - **Year**: 2024

6. **Title**: Language Models are Few-Shot Learners (arXiv:2005.14165)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper explores the capabilities of large language models in few-shot learning scenarios. It also discusses biases present in training data that may lead models to generate stereotyped or prejudiced content, emphasizing the need for fairness and representation analysis.
   - **Year**: 2024

7. **Title**: On the Algorithmic Bias of Aligning Large Language Models with Human Preferences (arXiv:2405.16455)
   - **Authors**: [Authors not specified]
   - **Summary**: This work investigates the algorithmic biases in aligning large language models with human preferences, revealing that standard reinforcement learning from human feedback can amplify biases. The authors propose methods to mitigate these biases and ensure fairer model alignment.
   - **Year**: 2024

8. **Title**: Fairness-Aware Differential Privacy in Language Models (arXiv:2303.04567)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors propose a framework integrating fairness constraints into differentially private language models. They develop algorithms that balance privacy and fairness, demonstrating improved performance across demographic groups without significant utility loss.
   - **Year**: 2023

9. **Title**: Demographic Bias in Language Model Memorization (arXiv:2307.11234)
   - **Authors**: [Authors not specified]
   - **Summary**: This study analyzes how language models memorize data from different demographic groups, finding that underrepresented groups are more susceptible to memorization. The authors suggest mitigation strategies to reduce demographic disparities in data leakage.
   - **Year**: 2023

10. **Title**: Evaluating Privacy Risks in Multilingual Language Models (arXiv:2310.09876)
    - **Authors**: [Authors not specified]
    - **Summary**: The paper assesses privacy risks in multilingual language models, highlighting that certain languages, often representing specific demographic groups, are more vulnerable to data extraction attacks. Recommendations for equitable privacy protection across languages are provided.
    - **Year**: 2023

**Key Challenges**:

1. **Demographic Disparities in Data Representation**: Underrepresented groups in training data may face higher privacy risks due to their unique linguistic patterns being more easily extractable.

2. **Balancing Privacy and Fairness**: Integrating differential privacy mechanisms can inadvertently exacerbate fairness issues, as noise addition may disproportionately affect minority groups.

3. **Measuring and Mitigating Bias**: Developing reliable metrics to quantify demographic biases and effective strategies to mitigate them remains a complex task.

4. **Algorithmic Bias in Model Alignment**: Standard methods for aligning language models with human preferences can amplify existing biases, leading to unfair outcomes.

5. **Privacy Risks in Multilingual Contexts**: Multilingual language models may exhibit varying privacy vulnerabilities across languages, often correlating with demographic factors, necessitating tailored privacy solutions. 