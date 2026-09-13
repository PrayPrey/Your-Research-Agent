## Related Work

**Related Papers**
1. **Title**: Establishing ethical frameworks for scalable data engineering and governance in AI-driven healthcare systems (Adepoju et al. 2025)
   - **Authors**: Adepoju et al.
   - **Summary**: Proposes modular architecture for ethical data governance in AI-driven healthcare, identifying key pillars including consent/data provenance, fairness in model training, explainability, auditability, and inclusivity. Analysis of GDPR, HIPAA, and emerging AI Acts to align technological advancements with societal values.
   - **Year**: 2025

2. **Title**: ArGen: Auto-Regulation of Generative AI via GRPO and Policy-as-Code (Madan 2025)
   - **Authors**: Madan
   - **Summary**: Introduces 'Governable AI' systems using principle-based automated reward scoring, GRPO, and OPA-inspired governance layer. Achieved 70.9% improvement in domain-scope adherence for Dharmic ethics (Ahimsa, Dharma principles from Bhagavad Gita), validating Policy-as-Code paradigm transferability to AI domain.
   - **Year**: 2025

3. **Title**: Privacy-Preserving Automated QA Dataset Generation for Fine-Tuning LLMs with Local Models (Suryadi & Saputra 2026)
   - **Authors**: Suryadi & Saputra
   - **Summary**: Demonstrates privacy-aware dataset construction using PyPDF2, novel sentence segmentation, SmolLM2-360M-Instruct (local LLM), and IR techniques for question-answer alignment. Validates that ethical constraints can be operationalized during dataset generation through localized processing.
   - **Year**: 2026

4. **Title**: Manual audit failures in respiratory sound datasets (Sa'adah 2025)
   - **Authors**: Sa'adah
   - **Summary**: Documents ~15-25% compliance violations in respiratory sound datasets under manual audit processes, providing baseline violation rate for comparison with automated enforcement approaches.
   - **Year**: 2025

5. **Title**: NLP financial compliance automation (Kothari 2025)
   - **Authors**: Kothari
   - **Summary**: Demonstrates "substantially higher accuracy" in NLP-based financial compliance automation using risk-based sampling approaches, providing precedent for adaptive sampling in regulated industries.
   - **Year**: 2025

6. **Title**: Cross-cultural governance challenges (Ochang 2024)
   - **Authors**: Ochang
   - **Summary**: Identifies significant challenges in cross-cultural ethical governance, motivating the need for policy localization layers that can adapt ethical frameworks across different jurisdictions and cultural contexts.
   - **Year**: 2024

7. **Title**: GDPR policy parsing with E5 Transformer (Priescu 2025)
   - **Authors**: Priescu
   - **Summary**: Establishes 75% accuracy baseline for single-model foundation model policy parsing using E5 Transformer on GDPR compliance rules, providing benchmark for ensemble-based improvement targets.
   - **Year**: 2025

8. **Title**: Multi-modal governance patterns (Fan 2024)
   - **Authors**: Fan
   - **Summary**: Explores governance patterns across multi-modal data sources (text, image, audio), informing multi-modal provenance architecture requirements for comprehensive dataset governance.
   - **Year**: 2024

9. **Title**: Domain-specific healthcare governance (Zhu 2025)
   - **Authors**: Zhu
   - **Summary**: Examines domain-specific governance requirements in healthcare contexts, informing Policy DSL design patterns for healthcare compliance frameworks.
   - **Year**: 2025

10. **Title**: Open Policy Agent (OPA) Documentation
    - **Authors**: Not specified
    - **Summary**: Provides architectural precedent for Policy-as-Code DSL design through Rego language, demonstrating declarative policy specification and enforcement in infrastructure contexts.
    - **Year**: Not specified

11. **Title**: Git/Merkle Trees - Content-addressable provenance
    - **Authors**: Not specified
    - **Summary**: Establishes precedents for content-addressable provenance at scale through Git (software engineering) and Merkle trees (blockchain), validating scalability of cryptographic provenance tracking.
    - **Year**: Not specified

12. **Title**: Ensemble ML Literature - Multi-model consensus voting
    - **Authors**: Not specified
    - **Summary**: Provides foundational techniques for multi-model consensus voting to improve accuracy through ensemble methods, supporting hypothesis that ensemble approaches can exceed single-model baselines.
    - **Year**: Not specified

**Key Challenges**
1. **Theory-to-Practice Gap**: Gap 2 identifies zero implementations of ethical governance frameworks despite 5 academic papers (Adepoju, Ochang, Sa'adah, Fan, Zhu), demonstrating critical gap between documentary compliance approaches and executable enforcement systems.

2. **Single-Model Accuracy Limitations**: Priescu 2025 establishes 75% accuracy baseline for policy parsing with single foundation models, indicating need for ensemble methods to achieve 95%+ accuracy required for reliable compliance enforcement.

3. **Manual Audit Ineffectiveness**: Sa'adah 2025 documents ~15-25% violation rates in manual audit processes, demonstrating critical failure rate that motivates automated enforcement approaches.

4. **Cross-Cultural Adaptation**: Ochang 2024 identifies significant challenges in applying ethical frameworks across different cultural and jurisdictional contexts, requiring policy localization mechanisms.

5. **Performance Overhead**: Need to balance comprehensive compliance enforcement with <10% performance overhead in billion-token scale dataset construction, requiring efficient adaptive sampling strategies.

6. **Formalization Complexity**: Challenge of translating nuanced ethical principles (consent, fairness, explainability, auditability) into machine-readable declarative policies without semantic loss.

7. **Cold Start Problem**: Initial deployment requires ground truth policy-constraint mappings (n≥385 pairs) and human-in-the-loop validation corpus before automated system can achieve target accuracy.

8. **Provenance Scalability**: Need for cryptographic provenance tracking (Merkle trees) to maintain auditability at billion-token scale while supporting retroactive compliance audits.
