## Related Work

**Related Papers**

1. **Title**: GreaseLM: Graph REASoning Enhanced Language Models for Question Answering (ICLR 2022)
   - **Authors**: Zhang, X., Bosselut, A., Yasunaga, M., Ren, H., Liang, P., Manning, C. D., & Leskovec, J.
   - **Summary**: Introduces bidirectional fusion between language models and GNNs via modality interaction layers for question answering tasks. Demonstrates effective fusion for small subgraphs (<10k nodes) but is limited by context window constraints and requires extracting small relevant subgraphs (at most 200 nodes per question).
   - **Year**: 2022

2. **Title**: ESCARGOT: an AI agent leveraging large language models, dynamic graph of thoughts, and biomedical knowledge graphs for enhanced reasoning
   - **Authors**: Matsumoto, N., Choi, H., Moran, J., et al.
   - **Summary**: Uses iterative knowledge graph retrieval guided by LLM reasoning in a Graph-of-Thoughts paradigm. Outperforms RAG methods on biomedical QA but faces "significant challenges with context length limitations" and requires multiple LLM calls (3-5 iterations, 5-10 seconds per question).
   - **Year**: 2025

3. **Title**: Natural Language Interface for Queries on Databases with Sensitive Information
   - **Authors**: Adeniye, S. C., Al-Atawi, F., & Sen, A.
   - **Summary**: Identifies that graph-to-text serialization loses structural information when converting graphs to natural language for LLM input, discarding connectivity patterns critical for reasoning.
   - **Year**: 2025

4. **Title**: Plexus: Taming Billion-edge Graphs with 3D Parallel Full-graph GNN Training (arXiv:2505.04083)
   - **Authors**: Plexus Team
   - **Summary**: Demonstrates billion-edge graphs are feasible with 3D parallelism (data, model, and pipeline parallelism). Achieves ~10 seconds per epoch for 1 billion edges and 100M nodes using 8 V100 GPUs with sub-linear scaling up to 16 GPUs.
   - **Year**: 2025

5. **Title**: DeepGNN: Framework for training ML models on large scale graph data
   - **Authors**: Microsoft Research
   - **Summary**: Production-ready distributed GNN training and inference framework supporting billion-node graphs (used in Bing, Azure). Provides APIs for graph sampling, neighbor aggregation, and distributed training with support for GraphSAGE, GAT, and GCN.
   - **Year**: 2022

6. **Title**: Graph Summarization Methods and Applications: A Survey
   - **Authors**: Liu, Y., Safavi, T., Dighe, A., & Koutra, D.
   - **Summary**: Comprehensive survey covering aggregation-based (community detection, clustering), influence-based (PageRank, degree centrality), and statistical methods for graph summarization. All methods optimize for structural objectives (coverage, modularity) rather than task-driven objectives.
   - **Year**: 2018

7. **Title**: Hierarchical Graph Representation Learning with Differentiable Pooling (DiffPool)
   - **Authors**: Ying, Z., You, J., Morris, C., Ren, X., Hamilton, W., & Leskovec, J.
   - **Summary**: Introduces hierarchical graph coarsening for GNN classification through learning assignment matrices that determine which nodes merge into super-nodes, optimizing GNN task performance for node/graph classification.
   - **Year**: 2018

8. **Title**: Self-Attention Graph Pooling (SAGPool)
   - **Authors**: Lee, J., Lee, I., & Kang, J.
   - **Summary**: Self-attention-based graph pooling where attention scores determine which nodes to keep or discard, designed for GNN-internal tasks like graph classification.
   - **Year**: 2019

9. **Title**: Training language models to follow instructions with human feedback (InstructGPT)
   - **Authors**: Ouyang, L., Wu, J., Jiang, X., et al.
   - **Summary**: Demonstrates RLHF technique using reinforcement learning (PPO) to fine-tune LLM policy maximizing reward from human preferences, enabling alignment without supervised examples. Shows reward-based training can preserve task quality.
   - **Year**: 2022

10. **Title**: Graph Foundation Models: A Comprehensive Survey
    - **Authors**: Wang, Z., et al.
    - **Summary**: Surveys graph foundation models and identifies key challenges including "structural alignment and heterogeneity across domains" where graphs from different domains (social, biomedical, commonsense) have different structures and current GFMs struggle to transfer across graph types.
    - **Year**: 2025

11. **Title**: LLM as GNN: Graph Vocabulary Learning for Text-Attributed Graph Foundation Models (PromptGFM)
    - **Authors**: Zhu, X., et al.
    - **Summary**: Learns transferable "graph vocabulary" (common substructures) across graphs with prompting mechanisms to adapt vocabulary to specific graphs and tasks.
    - **Year**: 2025

12. **Title**: Variational image compression with a scale hyperprior
    - **Authors**: Ballé, J., Minnen, D., Singh, S., Hwang, S. J., & Johnston, N.
    - **Summary**: Neural network-based image compression using variational autoencoders (VAEs) with end-to-end learning optimizing rate-distortion objectives, training encoder/decoder with combined distortion and rate loss.
    - **Year**: 2018

13. **Title**: Organization and maintenance of large ordered indices (B-tree)
    - **Authors**: Bayer, R., & McCreight, E.
    - **Summary**: Introduces B-tree data structure with multi-level hierarchy for efficient database indexing, achieving O(log N) access time through root (coarse summary) to internal nodes (medium) to leaves (fine details) organization.
    - **Year**: 1972

14. **Title**: R-trees: A dynamic index structure for spatial searching
    - **Authors**: Guttman, A.
    - **Summary**: Spatial index structure for geometric data using hierarchical organization for efficient query processing with logarithmic access times.
    - **Year**: 1984

15. **Title**: Coding theorems for a discrete source with a fidelity criterion (Rate-Distortion Theory)
    - **Authors**: Shannon, C. E.
    - **Summary**: Foundational information theory work establishing rate-distortion framework for balancing compression (rate R in bits) versus quality (distortion D), defining R(D) as minimum mutual information I(X; X̂) subject to distortion constraint.
    - **Year**: 1959

16. **Title**: Graph compression for storage
    - **Authors**: Toivonen, H., et al.
    - **Summary**: Methods for compressing graphs primarily for storage optimization, focusing on reducing graph size without task-specific objectives.
    - **Year**: 2011

**Key Challenges**

1. **Context Window Limitations**: Existing graph-LLM fusion methods (GreaseLM, ESCARGOT) face significant challenges with context length limitations, restricting graph sizes to <10k nodes and requiring iterative retrieval approaches that increase latency and cost.

2. **Scalability vs. Accuracy Trade-off**: Current approaches cannot scale to million-node graphs while preserving reasoning quality. GreaseLM limited to extracting small subgraphs (200 nodes), missing global structure. ESCARGOT's iterative approach is too slow for real-time applications (5-10s per question).

3. **Structural Information Loss**: Graph-to-text serialization for LLM consumption discards connectivity patterns and structural information critical for multi-hop reasoning, reducing effectiveness on complex questions.

4. **Lack of Task-Driven Compression**: Existing graph summarization methods optimize for structural properties (modularity, coverage, degree centrality) rather than downstream task performance, resulting in compression that may remove reasoning-critical structure.

5. **Single-Level Compression Limitations**: Current methods use all-or-nothing approaches (keep node or discard) without hierarchical granularity, preventing adaptive detail retrieval based on question complexity.

6. **Separate Retrieval Complexity**: Methods like ESCARGOT require separate iterative retrieval modules, increasing architectural complexity, latency (multiple LLM calls), and cost (3-5x versus single-pass).

7. **End-to-End Training Requirements**: Methods like GreaseLM require gradient access for end-to-end fine-tuning, limiting compatibility with API-only LLMs (GPT-4, Claude) and requiring substantial computational infrastructure.

8. **Cross-Modal Optimization Gap**: Graph pooling methods (DiffPool, SAGPool) optimize for GNN-internal tasks, not cross-modal LLM consumption. No existing work optimizes graph compression specifically for downstream LLM performance.

9. **Domain Transfer Challenges**: Graph foundation models struggle with structural heterogeneity across domains (social, biomedical, commonsense), with limited transferability of compression strategies across different graph types and reasoning tasks.

10. **Fixed Heuristic Limitations**: Simple baselines (top-k degree, community detection) use fixed heuristics that ignore task-specific relevance and cannot adapt to different reasoning patterns or question complexities.
