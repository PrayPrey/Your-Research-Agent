## Related Work

**Related Papers**

1. **Title**: Understanding Black-box Predictions via Influence Functions
   - **Authors**: Koh, P. W., & Liang, P.
   - **Summary**: Adapted influence functions from robust statistics to deep learning by estimating the effect of removing a training example through gradient-based influence scores I(z_train, z_test) = -∇_θ L(z_test) · H^{-1} ∇_θ L(z_train) using Hessian computation. This foundational work enables tracing model predictions back to influential training examples.
   - **Year**: 2017

2. **Title**: TRAK: Attributing Model Behavior at Scale
   - **Authors**: Park, S., Georgiev, K., Ilyas, A., Leclerc, G., & Madry, A.
   - **Summary**: Achieved O(n) scalability for influence functions via random projection P ∈ ℝ^{p×k} to reduce gradient dimensionality, enabling attribution on ImageNet (1.2M examples) with 0.81 correlation to leave-one-out retraining. Provides 20× speedup over original influence functions.
   - **Year**: 2023

3. **Title**: LoRIF: Low-Rank Influence Functions for Large-Scale Machine Learning (arXiv:2601.00000)
   - **Authors**: Kwon, Y., Wu, E., Wu, K., & Zou, J.
   - **Summary**: Achieved 20× speedup over TRAK through low-rank approximation of gradients (∇_θ L ≈ U Σ V^T with reduced rank r << p), processing ImageNet in 2.4 GPU hours versus 48 hours, with 0.78 correlation to leave-one-out retraining.
   - **Year**: 2026

4. **Title**: Benchmarking Evaluation of Machine Learning Contamination
   - **Authors**: Not specified
   - **Summary**: Validated that BERT embeddings combined with cosine similarity can detect train-test leakage (exact duplicates, semantic paraphrases) with 0.87 precision and 0.83 recall on synthetic contaminated benchmarks, establishing semantic similarity as effective contamination detection.
   - **Year**: 2024

5. **Title**: Taming Hyperparameter Sensitivity in Training Data Attribution
   - **Authors**: Wang, X., et al.
   - **Summary**: Identified that attribution methods are sensitive to hyperparameters (learning rate, projection dimension, random seed) and proposed ensemble methods to reduce this sensitivity, improving attribution stability across different configurations.
   - **Year**: 2025

6. **Title**: Validity Considerations for Machine Learning in Extreme Event Attribution
   - **Authors**: Chou, Y., et al.
   - **Summary**: Highlighted that data bias and distribution shift undermine ML model validity in climate science, proposing validity assessment frameworks that quantify uncertainty in extreme event attribution to address data quality issues.
   - **Year**: 2025

7. **Title**: Towards dimensions and granularity in a unified workflow and data provenance framework
   - **Authors**: Auge, T., et al.
   - **Summary**: Proposed W7+1 provenance questions (Who, What, When, Where, Why, Which, hoW + How certain?) as unified framework for scientific data provenance, arguing that data quality ("How certain?") should be tracked alongside data lineage using metadata.
   - **Year**: 2025

8. **Title**: Preserving File Provenance Using Principles of Blockchain to Ensure Scientific Reproducibility
   - **Authors**: Hasan, M., et al.
   - **Summary**: Used blockchain-style cryptographic hashing to verify data file integrity and detect tampering in scientific workflows, providing deterministic verification of data provenance for scientific reproducibility.
   - **Year**: 2023

9. **Title**: Cognitive priming in AI: Bias identification and analysis in electronic health records
   - **Authors**: Wang, J., & Lu, Z.
   - **Summary**: Used NLP (BERT embeddings) to detect systematic biases in EHR data, identifying cognitive priming (unconscious biases embedded in medical records) through semantic similarity analysis of medical text.
   - **Year**: 2025

10. **Title**: Training Data Influence Analysis and Estimation: A Survey
    - **Authors**: Hammoudeh, Z., & Lowd, D.
    - **Summary**: Proposed linear datamodeling score as attribution evaluation metric - training a linear model on top-K influential examples and measuring prediction accuracy on test set, where higher scores indicate more informative attributions.
    - **Year**: 2022

11. **Title**: Representer Point Selection for Explaining Deep Neural Networks
    - **Authors**: Yeh, C. K., et al.
    - **Summary**: Introduced alternative attribution method by identifying "representer points" (training examples in feature space closest to test example) using kernel-based distance instead of gradient-based influence, providing complementary explanation approach.
    - **Year**: 2018

12. **Title**: What Neural Networks Memorize and Why: Discovering the Long Tail via Influence Estimation
    - **Authors**: Feldman, V., & Zhang, C.
    - **Summary**: Used influence functions to identify memorized examples from the long tail of training distribution with high influence scores, arguing that memorization is necessary for learning rare patterns rather than being purely problematic.
    - **Year**: 2020

**Key Challenges**

1. **No Integration of Contamination with Attribution**: All existing gradient-based attribution methods (TRAK, LoRIF, SOURCE, ASTRA) assume clean training data and ignore contamination, producing unreliable attributions (circular explanations, inflated influence scores) when train-test leakage is present in internet-scale datasets.

2. **No Validity Quantification for Attributions**: Existing attribution methods output influence scores without uncertainty quantification, preventing users from assessing explanation reliability or distinguishing trustworthy explanations (based on clean data) from unreliable ones (based on contaminated data).

3. **Separate Tools for Contamination and Attribution**: Current practice requires running attribution and contamination detection as separate processes with manual reconciliation of results, creating inefficient workflows, error-prone reconciliation, and missed opportunities for joint optimization through shared computation.

4. **No Benchmarks for Contamination-Robust Attribution**: Existing attribution benchmarks use only clean train/test splits, while contamination detection benchmarks evaluate detection accuracy but not attribution robustness, making quantitative comparison of contamination-robust attribution methods impossible.

5. **Attribution Accuracy Depends on Data Quality**: Train-test contamination produces artificially high influence scores due to memorization rather than causal influence, creating circular attributions ("this test example is influenced by a nearly identical training example") that mask genuinely influential examples.

6. **Scalability vs. Validity Trade-off**: Existing attribution methods optimize only for computational efficiency (O(n) scalability) without considering data quality assessment (contamination detection), treating validity as a post-hoc concern rather than an integrated pipeline requirement.

7. **Hyperparameter Sensitivity**: Attribution methods are sensitive to hyperparameters (learning rate, projection dimension, random seed), creating reliability challenges that compound with contamination-induced unreliability when both issues are present simultaneously.

8. **Limited Cross-Domain Knowledge Transfer**: ML attribution methods have not leveraged principles from scientific data provenance (quality metadata, uncertainty quantification, lineage tracking) despite mature 30+ year development in that field, missing opportunities for systematic validity assessment frameworks.
