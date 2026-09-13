## Related Work

**Related Papers**

1. **Title**: PubChemQCR (Fu et al., 2025)
   - **Authors**: Fu et al.
   - **Summary**: Provides 3.5M DFT relaxation trajectories and 300M molecular conformations, representing the largest public quantum chemistry dataset for molecular-scale ML benchmarking.
   - **Year**: 2025

2. **Title**: DeepProtein (Xie et al., 2024)
   - **Authors**: Xie et al.
   - **Summary**: Comprehensive deep learning library and benchmark for protein tasks with standardized evaluation protocols, demonstrating feasibility of unified evaluation infrastructure in biological domains.
   - **Year**: 2024

3. **Title**: Multi-indicator evaluation (Yu et al., 2024)
   - **Authors**: Yu et al.
   - **Summary**: Systematic multi-metric comparison framework for protein design methods, demonstrating the feasibility of multi-dimensional assessment approaches.
   - **Year**: 2024

4. **Title**: Atmospheric ML benchmarks (Dueben et al., 2022)
   - **Authors**: Dueben et al.
   - **Summary**: Framework for building proper benchmark datasets in scientific domains with community engagement principles, providing domain-general guidance for scientific benchmark validity.
   - **Year**: 2022

5. **Title**: ChEMBL database (Gaulton et al., 2023)
   - **Authors**: Gaulton et al.
   - **Summary**: Provides molecular→protein→cellular linkage for ~2M compounds with millions of bioassay results, enabling cross-scale data integration for biological ML research.
   - **Year**: 2023

6. **Title**: HoloProt (Somnath et al., 2022)
   - **Authors**: Somnath et al.
   - **Summary**: Demonstrated that explicit multi-scale graph construction (surface → structure → sequence) improves protein property prediction through hierarchical encoding.
   - **Year**: 2022

7. **Title**: S3F (Zhang et al., 2024)
   - **Authors**: Zhang et al.
   - **Summary**: Showed that integrating sequence, structure, and surface with GVP networks improves fitness prediction on ProteinGym benchmark.
   - **Year**: 2024

8. **Title**: ProteinMPNN (Dauparas et al., 2022)
   - **Authors**: Dauparas et al.
   - **Summary**: Highly cited protein design method that can be evaluated using CrossScaleBench for objective cross-scale consistency comparison.
   - **Year**: 2022

9. **Title**: GNN Transfer Learning (Buterez et al., 2024)
   - **Authors**: Buterez et al.
   - **Summary**: Establishes transfer learning methodologies for graph neural networks, providing theoretical foundation for cross-scale transfer metrics.
   - **Year**: 2024

10. **Title**: Centered Kernel Alignment (CKA) for neural network representations (Kornblith et al., 2019)
    - **Authors**: Kornblith et al.
    - **Summary**: Widely used method for comparing neural network representations across layers and models, robust to affine transformations, providing foundation for cross-scale alignment metrics.
    - **Year**: 2019

11. **Title**: Transfer Learning Survey (Pan & Yang, 2010)
    - **Authors**: Pan and Yang
    - **Summary**: Foundational survey establishing performance retention (accuracy drop) as standard metric for transfer learning effectiveness, informing PTS methodology.
    - **Year**: 2010

12. **Title**: ImageNet (Deng et al., 2009)
    - **Authors**: Deng et al.
    - **Summary**: Hierarchical evaluation structure (classification → localization → detection) enabled objective comparison and drove computer vision field progress, providing cross-domain precedent for unified benchmarking.
    - **Year**: 2009

13. **Title**: GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding (Wang et al., 2018)
    - **Authors**: Wang et al.
    - **Summary**: Unified multi-task benchmarking with single leaderboard accelerated NLP progress by enabling fair comparison across diverse language understanding tasks.
    - **Year**: 2018

14. **Title**: SuperGLUE (Wang et al., 2019)
    - **Authors**: Wang et al.
    - **Summary**: Extended GLUE benchmark with more challenging tasks, further transforming NLP evaluation through standardized multi-task assessment.
    - **Year**: 2019

15. **Title**: Attention Is All You Need (Vaswani et al., 2017)
    - **Authors**: Vaswani et al.
    - **Summary**: Introduced Transformer architecture with cross-attention mechanisms that enable information flow between modalities, applicable to cross-scale integration in biological ML.
    - **Year**: 2017

16. **Title**: ProteinGym (Community Standard)
    - **Authors**: Not specified
    - **Summary**: Comprehensive protein sequence/function benchmark widely adopted in protein ML research, demonstrating protein-scale evaluation feasibility and community acceptance.
    - **Year**: Not specified

**Key Challenges**

1. **Fragmented Single-Scale Benchmarking**: Current biological ML evaluation relies on isolated single-scale benchmarks (PubChemQCR for molecular, ProteinGym for protein) that evaluate scales independently, lacking standardized cross-scale consistency metrics.

2. **Absence of Scale-Transition Metrics**: Existing benchmarks (PubChemQCR, ProteinGym, DeepProtein) do not measure representation quality at scale boundaries, making objective comparison of multi-scale vs. single-scale approaches impossible.

3. **Data Availability for Cross-Scale Tasks**: Need for sufficient molecular→protein linkage data with complete compound structure, protein target, and binding assay measurements to define meaningful cross-scale evaluation tasks.

4. **Community Adoption Uncertainty**: Field fragmentation across molecular chemists, protein biologists, and systems biologists creates risk that unified benchmarking framework may not be adopted despite technical merit.

5. **Baseline Implementation Fairness**: Risk of biased comparisons if reference baseline implementations (single-scale specialist, naive multi-scale, SOTA multi-scale) are not optimally tuned, potentially undermining framework credibility.

6. **Metric Predictive Validity**: Scale-transition metrics (CKA, PTS, EECS) must demonstrate meaningful correlation with downstream task performance; weak correlation would indicate metrics do not capture relevant model properties.

7. **Trade-off Between Per-Scale Performance and Cross-Scale Consistency**: Multi-scale models may sacrifice individual scale optimization for cross-scale alignment; framework must accommodate diverse community priorities through multi-dimensional leaderboards.
