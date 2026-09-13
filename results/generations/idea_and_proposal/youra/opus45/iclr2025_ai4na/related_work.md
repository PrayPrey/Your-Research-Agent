## Related Work

**Related Papers**
1. **Title**: Hierarchical State Space Models for Continuous Sequence-to-Sequence Modeling (arXiv:2402.10211)
   - **Authors**: Bhirangi, Wang, Pattabiraman et al.
   - **Summary**: Demonstrates that stacked SSMs with temporal hierarchy outperform flat Mamba/S4/Transformers by 23% MSE, supporting hierarchical architecture design approaches.
   - **Year**: 2024

2. **Title**: Orthrus: Towards Evolutionary and Functional RNA Foundation Models (bioRxiv:2024.10.10.617658)
   - **Authors**: Fradkin, Shi, Dalal et al.
   - **Summary**: Shows that contrastive learning with biological augmentations using orthologs and isoforms creates superior RNA representations for downstream tasks.
   - **Year**: 2024

3. **Title**: BEACON: Benchmark for Comprehensive RNA Tasks and Language Models (NeurIPS 2024)
   - **Authors**: Ren, Chen, Qiao et al.
   - **Summary**: Establishes a standardized 13-task benchmark for RNA model evaluation, finding that single nucleotide tokenization and ALiBi outperform alternative approaches.
   - **Year**: 2024

4. **Title**: DGRNA: Long-context RNA Foundation Model with Bidirectional Mamba2
   - **Authors**: Yuan, Chen, Pan
   - **Summary**: Demonstrates that Mamba architecture efficiently handles long RNA sequences, serving as a foundation for flat Mamba baseline architectures.
   - **Year**: 2024

5. **Title**: HydraRNA
   - **Authors**: Not specified
   - **Summary**: Proposes a hybrid SSM+attention architecture for full-length RNA achieving F1=0.76 on secondary structure prediction and comparable RBP binding prediction, though lacking contrastive alignment.
   - **Year**: 2025

6. **Title**: PlantRNA-FM
   - **Authors**: Not specified
   - **Summary**: Develops a plant-specific RNA foundation model achieving F1=0.974 on genic annotation, demonstrating RNA FM viability but limited to plant species.
   - **Year**: 2024

7. **Title**: Benchmarking pre-trained genomic language models for RNA sequence-related predictive applications (Nature Communications)
   - **Authors**: Not specified
   - **Summary**: Provides a comprehensive benchmark showing no single genomic language model dominates all RNA tasks, highlighting the need for unified approaches.
   - **Year**: 2025

8. **Title**: CASP16 RNA Structure Assessment
   - **Authors**: Not specified
   - **Summary**: Evaluates RNA structure prediction methods, finding that no method achieves >0.8 TM-score for novel RNA structures.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Unified Multimodal RNA Foundation Models**: Comprehensive benchmarking reveals no single genomic language model dominates across all RNA tasks, indicating the need for unified multimodal approaches that can generalize across diverse RNA prediction challenges.

2. **RNA Structure Prediction Gap**: Current methods fail to achieve high accuracy (>0.8 TM-score) for novel RNA structures, demonstrating that RNA structure prediction significantly lags behind protein structure prediction capabilities.

3. **Limited Cross-Species Generalization**: Existing RNA foundation models like PlantRNA-FM demonstrate strong performance but are restricted to specific species, lacking broader applicability across diverse organisms.

4. **Absence of Contrastive Alignment in Hybrid Architectures**: While hybrid SSM+attention approaches like HydraRNA show promise for RNA modeling, they lack contrastive alignment mechanisms that could improve representation learning through biological augmentations.

5. **Long-Context RNA Sequence Handling**: Processing full-length RNA sequences efficiently remains challenging, requiring specialized architectures like hierarchical SSMs or bidirectional Mamba to handle extended sequence contexts effectively.
