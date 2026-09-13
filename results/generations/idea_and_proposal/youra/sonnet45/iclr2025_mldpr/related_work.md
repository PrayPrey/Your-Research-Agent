## Related Work

**Related Papers**

1. **Title**: Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI (Pushkarna et al., 2022)
   - **Authors**: Pushkarna, M., Zaldivar, A., & Kjartansson, O.
   - **Summary**: Introduced human-readable documentation framework with structured sections for intended use and limitations. Deployed at Google with 20+ implementations, but relies on researchers reading and interpreting cards voluntarily without enforcement mechanisms.
   - **Year**: 2022

2. **Title**: A Standardized Machine-readable Dataset Documentation Format for Responsible AI (Jain et al., 2024)
   - **Authors**: Jain, N., Akhtar, M., et al.
   - **Summary**: Developed Croissant-RAI, a machine-readable metadata format extending Croissant with Responsible AI attributes. Integrated into Google Dataset Search and HuggingFace Hub, but lacks connection to enforcement mechanisms for usage validation.
   - **Year**: 2024

3. **Title**: Datasheets for Datasets (Gebru et al., 2018)
   - **Authors**: Gebru, T., et al.
   - **Summary**: Foundational documentation framework for datasets with 2000+ citations. Provides structured dataset documentation but lacks enforcement layer and relies on manual creation and reading.
   - **Year**: 2018

4. **Title**: Datasheets for AI and medical datasets (DAIMS): a data validation and documentation framework (Marandi et al., 2025)
   - **Authors**: Marandi, R.Z., Frahm, A.S., & Milojevic, M.
   - **Summary**: Validation tool with 24 standardization requirements for medical AI domain. Validates dataset quality at creation time but not usage context at load time.
   - **Year**: 2025

5. **Title**: Reproscreener: Leveraging LLMs for Assessing Computational Reproducibility of Machine Learning Pipelines (Bhaskar & Stodden, 2024)
   - **Authors**: Bhaskar, A., & Stodden, V.
   - **Summary**: Uses LLMs to validate reproducibility of ML pipelines through post-hoc analysis. Focuses on pipeline reproducibility rather than proactive prevention of dataset misuse.
   - **Year**: 2024

6. **Title**: Common Task Framework For a Critical Evaluation of Scientific Machine Learning Algorithms (Wyder et al., 2025)
   - **Authors**: Wyder, P., Goldfeder, J., et al.
   - **Summary**: Standardizes evaluation with hidden test sets for scientific ML algorithms. Ensures datasets match intended evaluation context but does not address runtime validation during dataset loading.
   - **Year**: 2025

7. **Title**: Machine Learning Pipelines: Provenance, Reproducibility and FAIR Data Principles (Samuel et al., 2020)
   - **Authors**: Samuel, S., Löffler, F., & König-Ries, B.
   - **Summary**: Investigates FAIR principles for ML workflows and proposes ProvBook tool for provenance tracking. Focuses on provenance rather than usage validation at runtime.
   - **Year**: 2020

8. **Title**: A review of the machine learning datasets in mammography, their adherence to the FAIR principles (Logan et al., 2023)
   - **Authors**: Logan, J., Kennedy, P.J., & Catchpoole, D.
   - **Summary**: Identifies FAIR violations (distribution variability issues like digital vs scanned mammography mixing) retrospectively through audit-based approach. Demonstrates detectable distribution mismatches but doesn't provide proactive detection mechanisms.
   - **Year**: 2023

9. **Title**: Runtime Verification with State Estimation (Erdogan et al., 2011)
   - **Authors**: Erdogan, C., Leucker, M., et al.
   - **Summary**: Provides theoretical foundation for runtime monitoring and specification violation detection in software engineering. Established principles for runtime verification that can be adapted to ML dataset loading context.
   - **Year**: 2011

10. **Title**: An Overview of AspectJ (Kiczales et al., 2001)
    - **Authors**: Kiczales, G., et al.
    - **Summary**: Foundational work on aspect-oriented programming with crosscutting concern injection patterns for security checks and logging. Architectural pattern can be adapted to Python ML frameworks for dataset loading interception.
    - **Year**: 2001

11. **Title**: IMLMA: An Intelligent Algorithm for Model Lifecycle Management with Automated Retraining, Versioning, and Monitoring (Cao et al., 2025)
    - **Authors**: Cao, Y., He, Y., & Zhang, C.
    - **Summary**: Addresses versioning and monitoring in ML lifecycle management. Drift monitoring mechanisms could potentially trigger dataset deprecation flags as a complementary system.
    - **Year**: 2025

12. **Title**: Model Lake: A New Alternative for Machine Learning Models Management and Governance (Garouani et al., 2025)
    - **Authors**: Garouani, M., Ravat, F., & Vallès-Parlangeau, N.
    - **Summary**: Proposes centralized management architecture for datasets, models, and code. Provides governance framework but lacks implementation of runtime validation enforcement mechanisms.
    - **Year**: 2025

13. **Title**: An empirical study of challenges in machine learning asset management (Zhao et al., 2024)
    - **Authors**: Zhao, Z., Chen, Y., et al.
    - **Summary**: Identifies 16 operational challenge topics from 15,065 Q&A posts, including dataset selection and quality assurance challenges. Provides empirical evidence for problems DatasetGuard aims to solve.
    - **Year**: 2024

14. **Title**: Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks (Reimers & Gurevych, 2019)
   - **Authors**: Reimers, N., & Gurevych, I.
   - **Summary**: Achieves 85%+ accuracy on semantic similarity tasks using Siamese BERT architecture. Provides the technical foundation for domain matching through sentence embeddings with cosine similarity.
   - **Year**: 2019

**Key Challenges**

1. **Passive Documentation Frameworks**: Existing systems (Data Cards, Datasheets, Croissant-RAI) rely on researchers voluntarily reading and interpreting documentation. No quantitative misuse prevention metrics exist, and there are no enforcement mechanisms to ensure compliance.

2. **Timing Gap - Creation vs Usage Validation**: Current tools like DAIMS validate dataset quality at creation time but fail to validate usage context at load time, when researchers actually access and apply datasets to potentially inappropriate contexts.

3. **Missing Runtime Enforcement Layer**: Machine-readable metadata formats (Croissant-RAI) exist and are integrated into platforms, but they lack connection to enforcement mechanisms that could actively prevent misuse during dataset loading operations.

4. **Retrospective Rather Than Proactive Detection**: Existing approaches (FAIR reviews, reproducibility assessments) identify misuse problems after-the-fact through audits and post-hoc analysis, rather than preventing misuse before training begins.

5. **No Automated Context Validation**: Current frameworks lack automated checking of whether a dataset's intended domain, distribution characteristics, and task types match the researcher's usage context. Manual interpretation is required, leading to human error.

6. **Lack of Graduated Enforcement Policies**: Existing systems operate in binary modes (documentation present/absent) without nuanced graduated responses based on violation severity that could balance strictness with research autonomy.

7. **Absence of Governance Analytics**: Repository administrators have no data-driven insights into dataset misuse patterns, frequencies, or trends that could inform policy enforcement and community education efforts.

8. **Cross-Domain Transfer Needed**: While software engineering has established runtime verification techniques (AspectJ, runtime monitoring), these have not been successfully adapted to ML dataset governance contexts with appropriate domain-specific validation methods.

9. **Metadata Quality and Coverage Uncertainty**: Unknown levels of Croissant-RAI adoption and README documentation quality across major dataset repositories create uncertainty about system utility and coverage.

10. **User Acceptance vs Strictness Trade-off**: No validated approaches for balancing enforcement strictness (preventing misuse) with user autonomy (allowing legitimate novel uses like transfer learning) without causing researcher frustration or system abandonment.
