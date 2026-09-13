## Related Work

**Related Papers**

1. **Title**: Evaluating the Social Impact of Generative AI Systems in Systems and Society (arXiv → ACM FAccT 2024)
   - **Authors**: Solaiman et al. (23 authors)
   - **Summary**: Provides 7 evaluation dimensions (bias, cultural values, disparate performance, privacy, financial costs, environmental costs, labor costs) for assessing generative AI societal impact. Establishes framework for categorizing societal impact evaluations.
   - **Year**: 2023

2. **Title**: Can We Trust AI Benchmarks? An Interdisciplinary Review of Current Issues in AI Evaluation (AI & Society)
   - **Authors**: Eriksson et al.
   - **Summary**: Meta-review of 110 AI evaluation studies identifying inadequate documentation, lack of standardization, construct validity failures, and inability to distinguish signal from noise across studies.
   - **Year**: 2025

3. **Title**: CRAI-MCF: A Context-Aware Hierarchical Model Card Framework for Responsible AI (arXiv)
   - **Authors**: Yang et al.
   - **Summary**: Uses weighted hierarchy for LLM model cards with Value Sensitive Design methodology, focused on text modality with technical emphasis rather than societal impact.
   - **Year**: 2025

4. **Title**: AI Risk-Assessment System (AIRS) (arXiv)
   - **Authors**: Nathanson et al.
   - **Summary**: Applies assurance cases to AI security with structured documentation, focusing on security domain using assurance case architecture.
   - **Year**: 2025

5. **Title**: WHO International Clinical Trials Registry Platform (ICTRP)
   - **Authors**: WHO
   - **Summary**: Hierarchical schema (Universal Core + Disease Extensions) with controlled vocabularies (SNOMED CT) enabling meta-analysis of 500,000+ clinical trials with >95% field completion.
   - **Year**: 2004-present

6. **Title**: NIST AI Risk Management Framework (AI RMF 1.0)
   - **Authors**: NIST (240+ organizations)
   - **Summary**: Multi-stakeholder developed framework providing high-level principles for AI risk management through 4 functions (Govern, Map, Measure, Manage), using narrative format without detailed machine-readable schema.
   - **Year**: 2023

7. **Title**: A Rapid Review of Responsible AI Frameworks (Journal of Responsible Technology)
   - **Authors**: Barletta et al.
   - **Summary**: Comparative review finding RAI frameworks lack operationalization, focus only on Requirements phase, and no comprehensive "catching-all" framework exists.
   - **Year**: 2023

8. **Title**: Understanding Industry Practitioners' Experiences in Generative AI Governance (CHI 2025)
   - **Authors**: Do et al.
   - **Summary**: Empirical study identifying practitioner pain points including difficulties in assessing societal impact and translating to actionable guidance.
   - **Year**: 2025

9. **Title**: Presenting a Comprehensive Multi-Scale Evaluation Framework for Participatory Modelling Programs (Environmental Modelling & Software)
   - **Authors**: Lee et al.
   - **Summary**: Multi-scale framework (project/individual/group/system) with 30 criteria demonstrating participatory evaluation in environmental modelling domain.
   - **Year**: 2022

10. **Title**: Fairness Indicators
    - **Authors**: TensorFlow team (Google)
    - **Summary**: Visualization toolkit for fairness metrics demonstrating technical feasibility of fairness measurement, focused on fairness dimension only.
    - **Year**: 2019-present

11. **Title**: AI Fairness 360 (AIF360)
    - **Authors**: IBM Research
    - **Summary**: Comprehensive fairness metrics library with 2,700+ GitHub stars, providing toolkit for practitioners focused on fairness dimension with no documentation standardization.
    - **Year**: 2018-present

12. **Title**: EU AI Act
    - **Authors**: European Union
    - **Summary**: Regulation mandating documentation for high-risk AI systems through Article 9 but not specifying implementation format, enforcement begins 2026+.
    - **Year**: 2024

13. **Title**: UK Government Magenta Book AI Guidance
    - **Authors**: UK Government
    - **Summary**: Government evaluation guidance for AI interventions using narrative-based approach without machine-readable schema, UK-specific scope.
    - **Year**: 2024 (updated 2025)

14. **Title**: Model Cards for Model Reporting (ACM FAccT)
    - **Authors**: Mitchell et al.
    - **Summary**: Structured template for ML model documentation with single-level structure, no controlled vocabularies or governance model.
    - **Year**: 2019

15. **Title**: Datasheets for Datasets (arXiv → Communications of ACM)
    - **Authors**: Gebru et al.
    - **Summary**: Structured questionnaire for dataset documentation focused on dataset characteristics without cross-system comparison support.
    - **Year**: 2018

16. **Title**: ClinicalTrials.gov
    - **Authors**: US National Library of Medicine
    - **Summary**: REST API implementation with XML/JSON schema validation and versioning for clinical trial protocol amendments, processing 50,000+ queries/day with <1% parsing failures.
    - **Year**: 2000-present

17. **Title**: SNOMED CT
    - **Authors**: SNOMED International
    - **Summary**: 350,000+ medical terminology concepts maintained via quarterly reviews for 50+ years, reducing diagnostic coding ambiguity by 67% vs. free-text documentation.
    - **Year**: 1965-present

18. **Title**: Microsoft RAI Standard v2
    - **Authors**: Microsoft
    - **Summary**: Requirements checklist with narrative justifications using internal tooling, limited cross-system comparison within Microsoft products only.
    - **Year**: 2022

19. **Title**: Partnership on AI Case Studies
    - **Authors**: Partnership on AI
    - **Summary**: Narrative case reports for AI impact documentation with low machine-readability, achieving 15-20% voluntary participation from major tech companies.
    - **Year**: 2017-2024

**Key Challenges**

1. **Inadequate Documentation Preventing Cross-Study Synthesis**: Meta-review findings show that 110 AI evaluation studies suffered from documentation failures that prevented systematic comparison and meta-analysis, similar to issues preventing Cochrane-style systematic reviews in AI ethics.

2. **Lack of Standardization for Machine-Readable Comparison**: Current frameworks (NIST AI RMF, Microsoft RAI Standard v2) use narrative formats with no mandatory fields or controlled vocabularies, resulting in <30% cross-system comparison success rate.

3. **Construct Validity Failures Due to Inconsistent Terminology**: Free-text descriptions use terms like "bias," "fairness," and "discrimination" interchangeably without definitions, leading to semantic ambiguity and inter-rater reliability κ<0.40.

4. **Cross-Modal Heterogeneity Challenge**: Generative AI systems span text, image, audio, and video modalities with modality-specific metrics (perplexity for text, FID for images) that cannot be compared, yet societal impact comparison requires standardized documentation.

5. **Standardization-Flexibility Trade-Off**: Flat schemas force all modalities into identical structure becoming either too generic (losing modality-specific insights) or too specific (incomparable across modalities).

6. **Low Voluntary Adoption Density**: Historical AI transparency initiatives (Partnership on AI, IEEE Ethically Aligned Design) achieve only 15-20% voluntary industry participation, insufficient critical mass for meaningful meta-analysis.

7. **Proprietary Information Protection Barriers**: Companies resist public disclosure of evaluation results due to competitive concerns, limiting participation in transparency initiatives even when frameworks exist.

8. **Governance Viability for Contested AI Ethics Concepts**: AI ethics stakeholders more fragmented than other standardization efforts, with societal impact definitions more contested than technical standards, making consensus difficult.

9. **Continuous AI System Evolution Tracking**: GenAI systems undergo frequent updates (model retraining, prompt modifications, deployment context changes) requiring versioning systems that balance granularity vs. documentation burden proliferation.

10. **Regulatory Implementation Gap**: EU AI Act Article 9 mandates documentation for high-risk AI systems but doesn't specify format, creating compliance uncertainty and potential for incompatible documentation approaches.

11. **Operationalization Gap in RAI Frameworks**: Existing frameworks provide high-level principles but lack concrete implementation guidance for practitioners assessing societal impact.

12. **Data Contamination Undetected**: Poor documentation practices prevent detection of issues like training-evaluation data overlap that compromise evaluation validity.

13. **Signal-to-Noise Discrimination Failure**: Inability to distinguish meaningful evaluation differences from measurement noise across studies due to inconsistent documentation and reporting practices.

14. **Meta-Analysis Infeasibility**: Current narrative documentation prevents quantitative aggregation of evaluation results necessary for evidence-based AI policy development.

15. **International Harmonization Challenge**: Divergent regulatory approaches (EU AI Act, US NIST framework, China's AI regulations, UK guidance) risk creating fragmented documentation standards preventing cross-border comparison.
