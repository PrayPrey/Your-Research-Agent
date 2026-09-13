## Related Work

**Related Papers**

1. **Title**: A survey on augmenting knowledge graphs (KGs) with large language models (LLMs): models, evaluation metrics, benchmarks, and challenges
   - **Authors**: Ibrahim, N., AboulEla, S., Ibrahim, A., & Kashef, R.
   - **Summary**: Comprehensive taxonomy of evaluation metrics and benchmarks for LLM-KG systems; identifies need for standardized evaluation. Provides descriptive classification of existing evaluation approaches in the LLM-KG domain.
   - **Year**: 2024

2. **Title**: Towards trustworthy multi-modal motion prediction: Holistic evaluation and interpretability of outputs
   - **Authors**: Carrasco Limeros, S., Majchrowska, S., Johnander, J., et al.
   - **Summary**: Holistic evaluation framework for motion prediction addressing diversity, admissibility; proposes intent prediction layer for interpretability. Demonstrates domain-specific multi-dimensional assessment approach.
   - **Year**: 2022

3. **Title**: Rethinking Interpretability in the Era of Large Language Models
   - **Authors**: Singh, C., Inala, J., Galley, M., Caruana, R., & Gao, J.
   - **Summary**: Reviews LLM interpretation evaluation challenges; identifies new priorities including LLM-based dataset analysis and interactive explanations. Highlights scale-specific evaluation needs for large language models.
   - **Year**: 2024

4. **Title**: Mechanistic Interpretability for AI Safety - A Review
   - **Authors**: Bereska, L., & Gavves, E.
   - **Summary**: Comprehensive review of mechanistic interpretability methodologies; establishes foundational concepts including features and causal dissection. Provides systematic overview of mechanistic interpretability evaluation approaches.
   - **Year**: 2024

5. **Title**: Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability
   - **Authors**: Geiger, A., Ibeling, D., Zur, A., et al.
   - **Summary**: Theoretical foundation for mechanistic interpretability via causal abstraction; unifies activation patching, circuit analysis, and sparse autoencoders through formal causal graph framework.
   - **Year**: 2023

6. **Title**: Multidimensional Item Response Theory
   - **Authors**: Reckase, M. D.
   - **Summary**: Formalization of MIRT for multi-dimensional latent trait measurement; extends Rasch model to multiple dimensions, enabling adaptive measurement across heterogeneous populations.
   - **Year**: 2009

7. **Title**: Probabilistic Models for Some Intelligence and Attainment Tests
   - **Authors**: Rasch, G.
   - **Summary**: Foundational psychometric work introducing the Rasch model, enabling person-free measurement and item-free person measurement. Establishes principles for measurement independence from test composition.
   - **Year**: 1960

8. **Title**: Modeling the Heart - From Genes to Cells to the Whole Organ
   - **Authors**: Noble, D.
   - **Summary**: Multi-scale cardiac modeling demonstrating scale-bridging across molecular → cellular → tissue → organ levels. Shows how conservation laws can be preserved across organizational scales.
   - **Year**: 2002

9. **Title**: Shaping the Future of Healthcare: Ethical Clinical Challenges and Pathways to Trustworthy AI
   - **Authors**: Goktas, P., & Grzybowski, A. E.
   - **Summary**: Regulatory Genome framework for trustworthy healthcare AI; proposes quantifiable trustworthiness metrics aligned with Sustainable Development Goals for healthcare-specific AI evaluation.
   - **Year**: 2025

10. **Title**: Explainable Artificial Intelligence (AI) through human-AI collaborative frameworks
    - **Authors**: Okonkwo, R., Folorunso, A., Ogundipe, F., & Tettey, C. Y.
    - **Summary**: Framework quantifying trust metrics (reliability, fairness, transparency) across healthcare, finance, and criminal justice domains. Emphasizes human-AI collaboration in explainability.
    - **Year**: 2025

11. **Title**: EU AI Act (Regulation (EU) 2024/1689 on Artificial Intelligence)
    - **Authors**: European Union
    - **Summary**: Regulatory framework establishing transparency and explainability requirements for high-risk AI systems (Article 13). Mandates that deployers must understand AI system functioning and provides legal basis for interpretability requirements.
    - **Year**: 2024

**Key Challenges**

1. **Evaluation Fragmentation Across Paradigms**: Current interpretability evaluation approaches are paradigm-specific (rule-based, attribution-based, mechanistic) with no standardized way to compare methods across paradigms. Each paradigm uses distinct metrics that are incompatible for cross-paradigm comparison.

2. **Lack of Cross-Scale Standardization**: No evaluation metrics work consistently across model scales (tabular models → shallow neural networks → deep neural networks → transformers → multimodal foundation models). Scale-specific approaches prevent unified assessment.

3. **Domain-Agnostic Evaluation**: Existing evaluation methods do not adapt to domain-specific requirements (healthcare vs. criminal justice vs. autonomous systems), treating all application contexts identically despite different stakeholder priorities.

4. **Scalability vs. Reliability Trade-off**: Human expert evaluation provides reliable but unscalable assessment (expensive, time-consuming, low inter-rater reliability κ ~ 0.4-0.6), while automated single-metric approaches are scalable but reductionist and arbitrary.

5. **Absence of Theoretical Foundation**: Most interpretability evaluation approaches lack rigorous theoretical grounding, relying on ad-hoc metric selection rather than principled frameworks for measurement and aggregation.

6. **Multi-Dimensionality Challenge**: Interpretability is inherently multi-dimensional (transparency, reliability, fairness, utility), but single-metric proxies fail to capture this complexity, while multi-metric approaches lack standardized composition rules.

7. **Calibration Data Requirements**: Developing standardized evaluation frameworks requires extensive calibration data across diverse model-metric pairs, creating a cold-start problem for deployment.

8. **Regulatory Compliance Assessment**: Manual regulatory audits for AI transparency requirements (e.g., EU AI Act Article 13) are time-consuming (weeks) and lack reproducible assessment criteria.

9. **Cross-Domain Transfer Limitations**: Domain-specific frameworks (e.g., healthcare-specific trustworthiness metrics) do not generalize to other domains, requiring redundant framework development for each application area.

10. **Paradigm-Specific Depth vs. Cross-Paradigm Breadth**: Trade-off between maintaining paradigm-specific evaluation depth and achieving cross-paradigm comparability. Unified frameworks risk losing nuanced, paradigm-specific insights.
