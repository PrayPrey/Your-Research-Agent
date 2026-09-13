## Related Work

**Related Papers**
1. **Title**: HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution
   - **Authors**: Nguyen et al.
   - **Summary**: Introduces a sub-quadratic Hyena architecture that achieves 1M token context with 500x speedup over previous methods, achieving state-of-the-art performance on 12/17 regulatory prediction tasks and demonstrating that long-range sequence modeling is feasible.
   - **Year**: 2023

2. **Title**: Top-down perceptual inference shaping the activity of early visual cortex
   - **Authors**: Csikor, Meszéna, Ócsai, Orbán
   - **Summary**: Demonstrates that hierarchical deep generative models with bidirectional flow can predict V1/V2 activity, showing that top-down influences are inherent to hierarchical inference, providing theoretical foundation for bidirectional cross-scale attention design.
   - **Year**: 2025

3. **Title**: DNALONGBENCH: benchmark suite for long-range DNA prediction tasks
   - **Authors**: Cheng et al.
   - **Summary**: Provides a comprehensive benchmark for evaluating long-range dependencies up to 1M bp, assessing DNA foundation models across 5 key genomic tasks.
   - **Year**: 2025

4. **Title**: Geneformer
   - **Authors**: Theodoris et al.
   - **Summary**: A single-cell foundation model pre-trained on 30M cells using a gene-as-token architecture for expression modeling.
   - **Year**: 2023

5. **Title**: scGPT
   - **Authors**: Cui et al.
   - **Summary**: A generative pre-trained transformer designed for single-cell analysis, exploring multi-modal extensions for cellular representation learning.
   - **Year**: 2023

6. **Title**: Single-cell foundation models: bringing AI into cell biology
   - **Authors**: Baek, Song, Lee
   - **Summary**: Reviews single-cell foundation models and identifies that current scFMs treat genes as tokens but lack sequence context, highlighting a gap in unified multi-scale architecture.
   - **Year**: 2025

7. **Title**: HESCAPE: Large-Scale Benchmark of Cross-Modal Learning (arXiv:2508.01490)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that cross-modal contrastive pretraining improves classification but degrades expression prediction, with batch effects interfering with alignment.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Sequence Context in Single-Cell Models**: Current single-cell foundation models treat genes as tokens but fail to incorporate underlying DNA sequence context, limiting their ability to capture regulatory mechanisms.

2. **Absence of Unified Multi-Scale Architecture**: Existing approaches operate at either the sequence level or the expression level independently, with no unified architecture bridging DNA sequences to cellular phenotypes.

3. **Cross-Modal Alignment Degradation**: Cross-modal contrastive pretraining, while improving classification tasks, has been shown to degrade expression prediction performance.

4. **Batch Effect Interference**: Batch effects in multi-modal data interfere with proper alignment between modalities, complicating the integration of sequence and expression information.

5. **Computational Scalability for Long-Range Dependencies**: Modeling long-range genomic dependencies (up to 1M bp) requires architectures that can handle extended contexts efficiently without quadratic complexity.
