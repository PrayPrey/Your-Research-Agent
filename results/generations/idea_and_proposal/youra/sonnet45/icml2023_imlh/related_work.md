## Related Work

**Related Papers**

1. **Title**: Integration of Domain Knowledge using Medical Knowledge Graph Deep Learning for Cancer Phenotyping (Alawad et al., 2021)
   - **Authors**: Alawad et al.
   - **Summary**: Demonstrated that UMLS-based medical knowledge graph integration with word embeddings improves cancer phenotyping by 4.97% micro-F1 and 22.5% macro-F1, validating that medical knowledge graphs provide useful inductive bias for clinical prediction tasks.
   - **Year**: 2021

2. **Title**: Knowledge Graph and Deep Learning-based Text-to-GraphQL Model for Intelligent Medical Consultation Chatbot (Ni et al., 2022)
   - **Authors**: Ni et al.
   - **Summary**: Demonstrates knowledge graph and language model integration for medical human-robot interaction, showing feasibility of combining symbolic medical knowledge with neural models.
   - **Year**: 2022

3. **Title**: Uncertainty Quantification for Machine Learning in Healthcare: A Survey (López et al., 2025)
   - **Authors**: López et al.
   - **Summary**: Provides comprehensive uncertainty quantification framework covering variational inference, Monte Carlo methods, and calibration techniques across data/training/evaluation stages. Documents that variational inference methods enable principled UQ in deep learning.
   - **Year**: 2025

4. **Title**: The need for quantification of uncertainty in artificial intelligence for clinical data analysis (Abdar et al., 2022)
   - **Authors**: Abdar et al.
   - **Summary**: Established need for epistemic vs. aleatoric uncertainty separation in medical AI, providing practical UQ guidelines for trustworthy clinical decision support.
   - **Year**: 2022

5. **Title**: From engineering principles to healthcare practice: A hybrid reasoning framework for transparent clinical decision support (Domingues, 2026)
   - **Authors**: Domingues
   - **Summary**: Demonstrated hybrid AI with OWL2 ontology and SWRL rules achieving 78% reduction in clinical guideline violations, showing feasibility of symbolic-neural integration for clinical alignment but lacking uncertainty quantification.
   - **Year**: 2026

6. **Title**: Out-of-Distribution Detection as a Risk-Control Strategy for Medical Classification Machine Learning Models (Weng et al., 2025)
   - **Authors**: Weng et al.
   - **Summary**: Demonstrated that OOD detection filters underrepresented patients where model performs worse, improving safety through identification of distribution-shifted cases.
   - **Year**: 2025

7. **Title**: Out-of-Distribution Detection for Medical Applications: Guidelines for Practical Evaluation (Zadorozhny et al., 2021)
   - **Authors**: Zadorozhny et al.
   - **Summary**: Provides practical tests for selecting OOD detection methods for specific medical datasets with evaluation guidelines.
   - **Year**: 2021

8. **Title**: Multiple stakeholders drive diverse interpretability requirements for machine learning in healthcare (Imrie et al., 2023)
   - **Authors**: Imrie et al.
   - **Summary**: Identified that clinicians, patients, and regulators have distinct interpretability needs (clinicians need causal explanations, patients need understandable risk, regulators need auditable traces).
   - **Year**: 2023

9. **Title**: Designing explainable AI to improve human-AI team performance: A medical stakeholder-driven scoping review (Subramanian et al., 2024)
   - **Authors**: Subramanian et al.
   - **Summary**: Identifies explainable AI design principles for improving human-AI collaboration in medical settings.
   - **Year**: 2024

10. **Title**: A Survey on Explainable Artificial Intelligence (XAI) Techniques for Visualizing Deep Learning Models in Medical Imaging (Bhati et al., 2024)
    - **Authors**: Bhati et al.
    - **Summary**: Comprehensive survey of XAI visualization techniques including saliency maps, attention mechanisms, CAM, and Grad-CAM for medical imaging applications.
    - **Year**: 2024

11. **Title**: PyTorch Geometric
    - **Authors**: Not specified
    - **Summary**: Comprehensive graph neural network library for encoding medical knowledge graphs, providing efficient implementations of Graph Convolutional Networks (GCN), Graph Attention Networks (GAT), and message-passing layers.
    - **Year**: Not specified

12. **Title**: Pyro: Deep Universal Probabilistic Programming (Bingham et al., 2018)
    - **Authors**: Bingham et al.
    - **Summary**: Established variational inference framework for scaling Bayesian inference to deep learning, introducing Stochastic Variational Inference (SVI) for handling large datasets and complex models.
    - **Year**: 2018

13. **Title**: DRKnows - Diagnostic Reasoning Knowledge Graph
    - **Authors**: Not specified
    - **Summary**: Diagnostic reasoning knowledge graph for large language model diagnosis prediction, integrating knowledge graphs with LLMs but lacking uncertainty quantification.
    - **Year**: Not specified

14. **Title**: Clinical Trials Knowledge Graph (CTKG)
    - **Authors**: Not specified
    - **Summary**: Demonstrates large-scale medical knowledge graph construction from clinical trials data, providing reference for UMLS-based graph engineering.
    - **Year**: Not specified

15. **Title**: ProbLog (Probabilistic Logic Programming)
    - **Authors**: Not specified
    - **Summary**: Demonstrates that logic rules can be annotated with probabilities to represent uncertain knowledge, enabling reasoning under uncertainty in symbolic systems.
    - **Year**: Not specified

16. **Title**: UMLS Metathesaurus
    - **Authors**: Not specified
    - **Summary**: Medical knowledge base containing 4M+ concepts and 14M+ relations from curated medical sources, providing comprehensive medical domain knowledge.
    - **Year**: Not specified

17. **Title**: MIMIC-III/MIMIC-IV
    - **Authors**: Not specified
    - **Summary**: Publicly available healthcare datasets used for training and testing clinical prediction models with structured EHR data.
    - **Year**: Not specified

18. **Title**: eICU Database
    - **Authors**: Not specified
    - **Summary**: Critical care database with approximately 200,000 patient admissions, used for out-of-distribution testing across different hospital sites.
    - **Year**: Not specified

**Key Challenges**

1. **Limited Uncertainty Quantification in Hybrid Systems**: Existing hybrid symbolic-neural systems lack principled uncertainty quantification, treating symbolic reasoning and uncertainty as separate components rather than integrating them through bidirectional uncertainty propagation.

2. **Insufficient OOD Detection in Clinical AI**: Current neural-only OOD detection methods miss semantic distribution shifts where predictions violate domain knowledge, leading to unsafe clinical decisions on underrepresented patient populations.

3. **Fragmented Multi-Stakeholder Interpretability**: Existing explainable AI approaches provide either learned patterns (neural attention) or symbolic rules, but not dual explanations that simultaneously address the distinct needs of clinicians, patients, and regulators.

4. **Binary Knowledge Graph Integration**: Prior knowledge graph integration methods treat medical knowledge as binary relations (edge exists or doesn't) rather than probabilistic constraints reflecting evidence strength and uncertainty in medical literature.

5. **Calibration Degradation on Distribution Shift**: Uncertainty estimates calibrated on training distribution often degrade when deployed at different hospitals with different patient demographics and clinical protocols, reducing safety benefits.

6. **Complexity vs. Performance Trade-off**: Adding symbolic knowledge, graph neural networks, and variational inference increases implementation complexity, but it's unclear whether the benefits justify the added complexity compared to simpler baseline approaches.

7. **Knowledge Graph Coverage Limitations**: Medical knowledge graphs like UMLS may lack comprehensive coverage for rare diseases and emerging conditions, limiting the framework's applicability beyond common clinical scenarios.

8. **Scalability of Probabilistic Reasoning**: Variational inference over large medical knowledge graphs (millions of nodes and edges) faces computational scalability challenges requiring subgraph sampling strategies that may miss important long-range medical relations.
