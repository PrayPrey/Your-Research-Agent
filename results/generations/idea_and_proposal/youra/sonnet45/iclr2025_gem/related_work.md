## Related Work

**Related Papers**
1. **Title**: Model-based systems engineering: Evaluating perceived value, metrics, and evidence
   - **Authors**: Campo, E., Morbach, J., Ricci, N., et al.
   - **Summary**: Establishes V&V framework from Systems Engineering showing 86% of MBSE claims lack validation metrics, providing theoretical foundation for separating verification from validation.
   - **Year**: 2022

2. **Title**: Broadly applicable and accurate protein design by integrating structure prediction networks and diffusion generative models (RFdiffusion)
   - **Authors**: Watson, J.L., Juergens, D., Bennett, N., et al.
   - **Summary**: Presents diffusion models for protein backbone generation, serving as verification tier tool for structurally valid designs.
   - **Year**: 2022

3. **Title**: Generative Flows on Discrete State-Spaces: Enabling Multimodal Flows with Applications to Protein Co-Design
   - **Authors**: Campbell, A., Yim, J., Barzilay, R., et al.
   - **Summary**: Introduces Discrete Flow Models for joint sequence-structure co-design, representing state-of-art generative models for verification tier.
   - **Year**: 2024

4. **Title**: Accelerating Computational Materials Discovery with Machine Learning and Cloud High-Performance Computing: from Large-Scale Screening to Experimental Validation
   - **Authors**: Chen, C., Nguyen, D., Lee, S.J., et al.
   - **Summary**: Demonstrates verification-validation gap with 32 million computational screens resulting in only 18 synthesized candidates (99.9994% gap), motivating need for validation oracle.
   - **Year**: 2024

5. **Title**: Engineering of highly active and diverse nuclease enzymes by combining machine learning and ultra-high-throughput screening (TeleProt)
   - **Authors**: Thomas, N., Belanger, D., Xu, C.A., et al.
   - **Summary**: Provides 55K nuclease variants dataset demonstrating feasibility of oracle training data with large-scale ML and experimental validation integration.
   - **Year**: 2024

6. **Title**: FLIGHTED: Inferring Fitness Landscapes from Noisy High-Throughput Experimental Data
   - **Authors**: Sundar, V., Klesmith, J.R., et al.
   - **Summary**: Presents Bayesian inference approach for modeling fitness landscapes from noisy high-throughput data, serving as methodological foundation for oracle noise modeling.
   - **Year**: 2024

7. **Title**: Effective sequence-to-expression prediction for a model membrane protein using machine learning and computational protein design
   - **Authors**: Shen, C., et al.
   - **Summary**: Validates that computational prediction to experimental outcome training data exists by demonstrating ML prediction of protein expression from sequence.
   - **Year**: 2026

8. **Title**: A Multi-Omics, Machine Learning-Aware, Genome-Wide Metabolic Model of Bacillus Subtilis Refines the Gene Expression and Cell Growth Prediction
   - **Authors**: Bi, Y., et al.
   - **Summary**: Demonstrates multi-omics datasets enable accurate expression and growth prediction, validating computational-to-experimental prediction feasibility.
   - **Year**: 2024

9. **Title**: FoldBench: An All-atom Benchmark for Biomolecular Structure Prediction
   - **Authors**: Xu, Y., et al.
   - **Summary**: Presents comprehensive computational-only benchmark for structure prediction, highlighting gap in experimental validation metrics in current benchmarks.
   - **Year**: 2025

10. **Title**: Scaling experiments post-hoc (post-hoc validation approach)
    - **Authors**: Qian, Y., et al.
    - **Summary**: Tests all designs experimentally without predictive oracle, representing brute force approach versus oracle-based filtering.
    - **Year**: 2025

11. **Title**: LLM agents with validation (specific designs approach)
    - **Authors**: Wang, X., et al.
    - **Summary**: Focuses on validation for specific designs rather than systematic V&V framework, representing alternative approach.
    - **Year**: 2025

12. **Title**: AlphaFold2 (protein structure prediction)
    - **Authors**: Not specified
    - **Summary**: Structure prediction model providing verification tier metrics (pLDDT, pAE) for computational validation of designs.
    - **Year**: Not specified

13. **Title**: AlphaFold3 (improved structure prediction)
    - **Authors**: Not specified
    - **Summary**: Enhanced structure prediction model representing better computational models that still don't address verification-validation gap.
    - **Year**: Not specified

14. **Title**: ProteinMPNN (sequence design)
    - **Authors**: Dauparas et al.
    - **Summary**: Sequence design model for generating protein sequences given backbone structures, used in verification tier of pipeline.
    - **Year**: Not specified

15. **Title**: ESM-2 (protein language model)
    - **Authors**: Facebook AI
    - **Summary**: Protein language model providing sequence embeddings and perplexity metrics for verification tier evaluation.
    - **Year**: Not specified

**Key Challenges**
1. **Verification-Validation Gap**: Current biomolecular design pipelines show 70-90% experimental failure rate despite passing computational validation (AlphaFold, ESM), indicating computational benchmarks measure verification ("structurally valid") but not validation ("experimentally successful").

2. **Insufficient Experimental-Aware Benchmarks**: All existing benchmarks (FoldBench, CATH) focus on computational metrics without experimental validation metrics, failing to predict experimental success (10-30% baseline).

3. **Lack of Predictive Oracles**: No standardized framework exists for predicting experimental outcomes from computational predictions, resulting in brute-force experimental validation approaches.

4. **Experimental Noise Modeling**: Standard ML approaches don't account for assay variability, batch effects, and experimental noise in protein engineering workflows.

5. **Data Scarcity for Oracle Training**: Limited availability of (computational_prediction, experimental_outcome) paired datasets due to publication bias toward successes and lack of failed design reporting.

6. **Computational-Experimental Integration**: No systematic closed-loop framework integrating generative models with high-throughput experimental validation and iterative refinement.

7. **Overfitting to Computational Proxies**: ML models optimize for computational metrics (sequence recovery, RMSD, binding affinity predictions) rather than experimental utility (expression yield, stability, functional binding).

8. **Lab-to-Lab Variability**: Experimental outcomes vary across different labs, expression systems, and assay protocols, limiting generalization of predictive models.

9. **Interpretability Gap**: ML latent spaces are opaque to biologists, making it difficult to debug verification versus validation failures and understand model predictions.

10. **Alternative Approaches Limitations**: Two-stage training requires large experimental datasets and lacks explicit verification-validation structure; multi-task learning assumes objective compatibility; active learning requires multiple expensive experimental rounds.
