## Related Work

**Related Papers**

1. **Title**: Integrating experimental feedback improves generative models for biological sequences (Calvanese et al., 2025)
   - **Authors**: Calvanese et al.
   - **Summary**: Demonstrates likelihood-based reintegration method for incorporating experimental feedback into generative models, achieving 9.5× improvement in functional rate (6.7% → 63.7%) for RNA self-splicing ribozyme design.
   - **Year**: 2025

2. **Title**: Lab-in-the-loop machine learning for brain-targeting delivery system
   - **Authors**: Not specified
   - **Summary**: Applies Bayesian optimization with Gaussian process surrogate for nanoparticle design, achieving target efficacy in 15 iterations (vs. estimated 100+ for random screening).
   - **Year**: 2025

3. **Title**: CA-SMART - Confidence Adjusted Surprise Measure for Active Learning (Raihan et al., 2025)
   - **Authors**: Raihan et al.
   - **Summary**: Active learning strategy for materials science using confidence-adjusted acquisition, achieving 30% reduction in experiments needed vs. random search for crystal structure stability and band gap optimization.
   - **Year**: 2025

4. **Title**: FDA Center for Drug Evaluation and Research (CDER) - Clinical Trials Endpoint Frameworks
   - **Authors**: FDA
   - **Summary**: Establishes standardized methodology for evaluating pharmaceutical interventions using primary endpoints (efficacy), secondary endpoints (safety, quality of life), and composite endpoints (benefit-risk ratio).
   - **Year**: Not specified

5. **Title**: ImageNet Large Scale Visual Recognition Challenge (Deng et al., 2009)
   - **Authors**: Deng et al.
   - **Summary**: Foundational computer vision benchmark providing standardized image classification task with top-1/top-5 accuracy metrics, accelerating method iteration from AlexNet to ResNet to EfficientNet.
   - **Year**: 2009

6. **Title**: GLUE - General Language Understanding Evaluation (Wang et al., 2018)
   - **Authors**: Wang et al.
   - **Summary**: Multi-task NLP benchmark suite with standardized reporting protocol enabling systematic transformer comparison across diverse language understanding tasks.
   - **Year**: 2018

7. **Title**: ProTherm - Thermodynamic Database for Proteins and Mutants (Kumar et al., 2006)
   - **Authors**: Kumar et al.
   - **Summary**: Curated database of experimental protein thermal stability data containing >10,000 mutants across diverse protein families, serving as standard reference in protein engineering field.
   - **Year**: 2006

8. **Title**: FireProtDB - Database of Protein Stability Data (Musil et al., 2017)
   - **Authors**: Musil et al.
   - **Summary**: Complementary protein stability dataset enriching oracle diversity with recent experimental data (2010-2020), including thermophilic proteins and extremophiles for diverse stability regimes.
   - **Year**: 2017

9. **Title**: Global analysis of protein folding using massively parallel design, synthesis, and testing (Rocklin et al., 2017)
   - **Authors**: Rocklin et al.
   - **Summary**: Large-scale experimental validation of protein design testing >15,000 sequences, demonstrating feasibility of high-throughput experimental feedback but at significant cost ($1-2M).
   - **Year**: 2017

10. **Title**: Evaluating the Effectiveness of Parameter-Efficient Fine-Tuning in Genomic Classification Tasks (Berman et al., 2025)
   - **Authors**: Berman et al.
   - **Summary**: Parameter-efficient methods for biological foundation models enabling efficient model deployment in resource-constrained labs.
   - **Year**: 2025

11. **Title**: CytoDINO - Risk-Aware and Biologically-Informed Adaptation of DINOv3 (Muminov & Pham, 2025)
   - **Authors**: Muminov & Pham
   - **Summary**: Consumer GPU deployment achieving 88.2% F1 with 8% trainable parameters via LoRA on single RTX 5080, demonstrating accessible model training for biological applications.
   - **Year**: 2025

12. **Title**: Lyra - Efficient Subquadratic Architecture for Modeling Biological Sequences (Ramesh et al., 2025)
   - **Authors**: Ramesh et al.
   - **Summary**: Achieves 120,000-fold parameter reduction vs. standard biological foundation models, training on 2 GPUs in <2 hours for rapid model iteration in lab-in-the-loop systems.
   - **Year**: 2025

**Key Challenges**

1. **Incompatible Evaluation Metrics**: Current lab-in-the-loop studies use task-specific metrics (functional rate improvement, iteration count, materials properties) that prevent direct comparison across different feedback integration strategies.

2. **Dataset Heterogeneity and Reproducibility**: Custom wet-lab data, proprietary formulations, and computational databases create reproducibility barriers, making independent replication of lab-in-the-loop studies impossible.

3. **Lack of Standardized Comparison Framework**: Each study optimizes for narrow domain with custom evaluation protocols, creating adoption barriers for researchers selecting feedback strategies without ability to compare methods systematically.

4. **Missing Multi-Dimensional Evaluation**: Existing approaches evaluate single dimensions (efficacy OR cost OR diversity) but fail to comprehensively assess functional hit rate + sequence diversity + experimental cost simultaneously.

5. **Trade-off Between Ecological Validity and Reproducibility**: Real wet-lab experiments capture true constraints but prevent reproducible benchmarking due to experimental variability; simulated oracles enable reproducibility but may not reflect all real-world complexities.

6. **Task Transferability Uncertainty**: Methods validated on specific tasks (RNA design, drug delivery, materials science) have unclear generalization to other biological domains due to orthogonal evaluation frameworks.

7. **Accessibility Gap for Resource-Constrained Labs**: High experimental costs ($1-2M for large-scale validation) and technical complexity create barriers for wet-lab biologists to adopt iterative ML-experiment systems without validated performance guarantees.

8. **Baseline Method Implementation Ambiguity**: Literature descriptions of feedback integration methods may omit critical implementation details (hyperparameters, convergence criteria), creating variance in replicated results.
