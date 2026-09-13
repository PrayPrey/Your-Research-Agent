## Related Work

**Related Papers**

1. **Title**: Designing Understandable and Fair AI for Learning: The PEARL Framework for Human-Centered Educational AI (Dakshit et al. 2026)
   - **Authors**: Dakshit et al.
   - **Summary**: Proposes PEARL framework with five dimensions (Pedagogical Personalization, Explainability/Engagement, Attribution/Accountability, Representation/Reflection, Localized Agency) for human-centered explainability and provides evaluation tool (PEARL Composite Score) demonstrated through simulated AI tutoring examples.
   - **Year**: 2026

2. **Title**: Automated Bias Assessment in AI-Generated Educational Content Using CEAT Framework (Peng et al. 2025)
   - **Authors**: Peng et al.
   - **Summary**: CEAT (Contextualized Embedding Association Test) achieves r=0.993 correlation with manual bias curation for AI-generated tutor training content through prompt-engineered word extraction for offline bias assessment.
   - **Year**: 2025

3. **Title**: Privacy-Preserved Automated Scoring using Federated Learning for Educational Research (Latif & Zhai 2025)
   - **Authors**: Latif & Zhai
   - **Summary**: Federated learning with LoRA (parameter-efficient fine-tuning) and adaptive weighted aggregation achieves 94.5% accuracy (within 0.5-1.0% of centralized model) on NGSS-aligned science assessments, eliminating centralized student data sharing.
   - **Year**: 2025

4. **Title**: Opportunities and Challenges of AI in Educational Assessment (Şahin et al. 2024)
   - **Authors**: Şahin et al.
   - **Summary**: Survey of seven articles identifies need for fair/responsible AI use in educational assessment, highlighting fragmentation across learning analytics, automated scoring, and fairness research.
   - **Year**: 2024

5. **Title**: A Framework for Responsible AI Systems: Building Societal Trust through Domain Definition, Trustworthy AI Design, Auditability, Accountability, and Governance (Herrera-Poyatos et al. 2025)
   - **Authors**: Herrera-Poyatos et al.
   - **Summary**: RAIS framework integrates five dimensions (domain definition, trustworthy design, auditability, accountability, governance) throughout AI system lifecycle with emphasis on inter-dependencies and iterative feedback loops for proactive/reactive accountability (cross-domain systems engineering framework).
   - **Year**: 2025

6. **Title**: Improving Trust and Accountability in AI Systems through Technological Era Advancement for Decision Support in Indonesian Manufacturing Companies (Mardiani et al. 2023)
   - **Authors**: Mardiani et al.
   - **Summary**: Multi-level stakeholder analysis reveals trust is impacted by dependability and transparency; different organizational roles/age groups/functions require differentiated transparency levels; strong accountability frameworks encourage prudent decision-making (organizational psychology trust dynamics study).
   - **Year**: 2023

7. **Title**: Artificial Intelligence Regulation: a framework for governance (Almeida et al. 2021)
   - **Authors**: Almeida et al.
   - **Summary**: Identifies fragmentation and implementation gaps in principles-based AI governance; emphasizes need for participatory governance, risk-based auditing, certification processes, and sector-specific adaptation of general AI principles (public policy governance framework).
   - **Year**: 2021

8. **Title**: Fairness in Automated Essay Scoring: A Comparative Analysis of Algorithms on German Learner Essays from Secondary Education (Schaller et al. 2024)
   - **Authors**: Schaller et al.
   - **Summary**: Comparative analysis of fairness algorithms for automated essay scoring across demographics (gender, migration background, native language), reporting demographic parity gap 0.08-0.12 depending on algorithm.
   - **Year**: 2024

9. **Title**: Educational Evaluation with MLLMs: Framework, Dataset, and Comprehensive Assessment (Chen et al. 2025)
   - **Authors**: Chen et al.
   - **Summary**: Multimodal dataset (essays, slides, videos) with expert annotations across 5 educational dimensions; tested 4 leading MLLMs (GPT-4o, Gemini 2.5, Doubao1.6, Kimi 1.5) revealing gaps in discourse-level assessment.
   - **Year**: 2025

10. **Title**: Multiple works on differential privacy, federated learning, secure multi-party computation
   - **Authors**: Not specified
   - **Summary**: Established techniques for privacy-preserving machine learning, providing isolated privacy solutions without fairness or explainability integration.
   - **Year**: Not specified

**Key Challenges**

1. **Component Fragmentation**: Existing work addresses fairness, explainability, privacy, and accountability as separate research threads with integration limited to API interfaces and data exchange protocols, lacking architectural coupling demonstrating synergistic benefits.

2. **Post-Hoc Validation Paradigm**: Current approaches validate trustworthiness after model deployment (detective approach) through fairness auditing, bias detection, and explanation generation as post-processing, without design-time embedding of trustworthiness mechanisms.

3. **Uniform Transparency Assumption**: Explainability research assumes all stakeholders need same explanations without differentiation based on stakeholder roles, expertise, or information needs; organizational trust dynamics not applied to AI transparency.

4. **Incomplete Accountability Systems**: External logging systems reconstruct audit trails post-hoc (85-95% completeness) with missing embedded context reducing accountability transparency; audit trails not integrated with explainability or fairness metrics.

5. **Privacy-Fairness Tension**: Privacy research and fairness research operate independently without solutions for fairness monitoring without demographic data exposure; federated learning focuses on model accuracy, not fairness implications.

6. **Accuracy vs. Trustworthiness Trade-off**: Simultaneous optimization of task performance (educational assessment accuracy) and trustworthiness mechanisms may lead to catastrophic accuracy degradation exceeding acceptable thresholds.

7. **Real-Time Computational Overhead**: Runtime trustworthiness monitoring (bias detection, fairness metrics, explanation generation) may incur prohibitive latency preventing practical deployment in real-time educational assessment contexts.

8. **Multi-Stakeholder Complexity**: Different stakeholders (students, teachers, administrators, policymakers) have distinct transparency needs requiring differentiated interfaces rather than uniform reporting approaches.

9. **Federated Learning Logistics**: Multi-site deployment requires institutional partnerships, IRB approvals, data sharing agreements, and computational infrastructure coordination across distributed educational institutions.

10. **Aggregate Fairness Granularity**: Using aggregate-level fairness statistics (privacy-preserving) instead of individual-level demographic analysis introduces coarser fairness assessment that may miss fine-grained bias patterns.
