## Related Work

**Related Papers**
1. **Title**: GFT: Graph Foundation Model with Transferable Tree Vocabulary (arXiv:2024)
   - **Authors**: Wang, Zhang, Chawla, Zhang, Ye
   - **Summary**: Introduces a tree vocabulary approach that enables cross-task and cross-domain transfer for graph foundation models, providing a fixed tree vocabulary for graph representation.
   - **Year**: 2024

2. **Title**: Learning Structure from the Ground up - Hierarchical Representation Learning by Chunking
   - **Authors**: Wu, Éltető, Dasgupta, Schulz
   - **Summary**: Proposes a cognitive-inspired chunking mechanism that learns interpretable hierarchical representations, providing foundational insights for adaptive chunking in structured data.
   - **Year**: 2022

3. **Title**: A Hierarchical Quantized Tokenization Framework for Task-Adaptive Graph Representation Learning
   - **Authors**: Xiang, Fan, Yin, Ji
   - **Summary**: Develops task-conditioned routing over residual vector quantization depths to improve graph tokenization, demonstrating the benefits of task-adaptive mechanisms for graph representation.
   - **Year**: 2025

4. **Title**: HIGHT: Hierarchical Graph Tokenization
   - **Authors**: Not specified
   - **Summary**: Employs fixed chemical decomposition rules for tokenizing molecular graphs, providing a rule-based approach to hierarchical graph representation.
   - **Year**: 2024

5. **Title**: SAMGPT: Text-free Multi-domain Graph Foundation Model
   - **Authors**: Not specified
   - **Summary**: Introduces domain tokens for multi-domain pre-training of graph models, enabling text-free graph foundation model training across multiple domains.
   - **Year**: 2025

6. **Title**: GraphToken Survey
   - **Authors**: Yu et al.
   - **Summary**: Documents a comprehensive taxonomy of graph tokenization approaches spanning node2token, group2token, and holistic methods, providing a systematic overview of the field.
   - **Year**: 2025

7. **Title**: GLBench: Comprehensive Benchmark for Graph with LLMs
   - **Authors**: Not specified
   - **Summary**: Establishes a comprehensive benchmark demonstrating that LLM-as-enhancers outperform GNNs in supervised settings, providing evaluation infrastructure for graph-LLM integration.
   - **Year**: 2024

**Key Challenges**
1. **Fixed Vocabulary Limitations**: Existing graph foundation models like GFT rely on fixed tree vocabularies that cannot adapt to varying graph structures and domains, limiting transferability.
2. **Rule-Based Decomposition Rigidity**: Methods like HIGHT depend on fixed chemical decomposition rules, which lack flexibility for diverse graph types beyond molecular domains.
3. **Lack of Unified Adaptive Tokenization**: Current approaches do not provide unified adaptive tokenization that works across all granularities (node, group, holistic levels) as documented in the GraphToken Survey.
4. **Missing Tokenization Strategy Benchmarks**: Despite advances in graph-LLM integration, there exists no comprehensive benchmark specifically designed for comparing different tokenization strategies, as highlighted by GLBench's focus on other aspects.
5. **Cross-Domain Generalization**: Existing multi-domain approaches like SAMGPT use domain-specific tokens rather than adaptive mechanisms that can generalize chunking strategies across domains.
