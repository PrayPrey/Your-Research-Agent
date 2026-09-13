## Related Work

**Related Papers**

1. **Title**: Towards Automated Circuit Discovery (ACDC) (Conmy et al., 2023)
   - **Authors**: Conmy et al.
   - **Summary**: Automated algorithm for identifying circuits (minimal subgraphs that implement specific model behaviors) via iterative edge pruning. Successfully identified IOI (indirect object identification) circuit in GPT-2, name mover heads, and S-inhibition circuit.
   - **Year**: 2023

2. **Title**: Progress Measures for Grokking via Mechanistic Interpretability (Nanda et al., 2023)
   - **Authors**: Nanda et al.
   - **Summary**: Reverse-engineered algorithm implementing modular arithmetic in grokking phenomenon using Fourier feature analysis and circuit tracing. Demonstrated that modular arithmetic is implemented via Fourier basis with critical residual connections for gradient flow.
   - **Year**: 2023

3. **Title**: Open Problems in Mechanistic Interpretability (Sharkey, Chughtai, et al., 2025)
   - **Authors**: Sharkey, Chughtai, et al.
   - **Summary**: Comprehensive survey of unsolved problems in mechanistic interpretability research, identifying key challenges including scalability of circuit discovery to large models, generalization of interpretability methods across architectures, and standardized evaluation frameworks for interpretability quality.
   - **Year**: 2025

4. **Title**: Hierarchical Attribution Graph Decomposition (HAGD)
   - **Authors**: Not specified
   - **Summary**: Cross-architecture circuit discovery using hierarchical attribution graphs and cross-layer transcoders. Achieved 67% structural similarity across model families (transformers, CNNs, vision transformers) through attribution-based approach.
   - **Year**: 2026

5. **Title**: Comparative Connectomics: Conserved Synaptic Motifs in Drosophila
   - **Authors**: Not specified
   - **Summary**: Demonstrates conserved synaptic motifs (convergent connections, divergent connections, reciprocal pairs) across different Drosophila individuals and brain regions despite structural diversity. Motifs conserved at 80-95% rate across structurally different brain regions using high-resolution connectome reconstruction.
   - **Year**: 2025

6. **Title**: Weisfeiler and Leman Go Neural (Morris et al., 2019)
   - **Authors**: Morris et al.
   - **Summary**: Theoretical analysis of GNN expressive power for subgraph detection and isomorphism testing, establishing foundational understanding of what graph neural networks can and cannot distinguish.
   - **Year**: 2019

7. **Title**: How Powerful are Graph Neural Networks? (Xu et al., 2019)
   - **Authors**: Xu et al.
   - **Summary**: Introduces Graph Isomorphism Network (GIN) architecture for graph classification, demonstrating that message-passing GNNs can distinguish many graph patterns and that GIN maximizes expressive power within message-passing framework.
   - **Year**: 2019

8. **Title**: Code2Vec (Alon et al., 2019)
   - **Authors**: Alon et al.
   - **Summary**: Uses GNNs to analyze program abstract syntax trees (ASTs) for code understanding, demonstrating that GNNs outperform sequence models on code analysis tasks requiring structural understanding.
   - **Year**: 2019

9. **Title**: GraphCodeBERT (Guo et al., 2021)
   - **Authors**: Guo et al.
   - **Summary**: Application of GNNs to program control flow graphs for code understanding tasks such as function name prediction and bug detection, showing generalization across programming languages despite syntactic differences.
   - **Year**: 2021

10. **Title**: Emergent Abilities of Large Language Models (Wei et al., 2022)
    - **Authors**: Wei et al.
    - **Summary**: Documents unpredictable emergent abilities that appear at scale in large language models (e.g., multi-step reasoning, few-shot prompting), showing certain capabilities absent in small models emerge sharply at specific scale thresholds.
    - **Year**: 2022

11. **Title**: Are Emergent Abilities of Large Language Models a Mirage? (Schaeffer et al., 2023)
    - **Authors**: Schaeffer et al.
    - **Summary**: Challenges the emergent abilities hypothesis by showing that emergence is an artifact of discontinuous evaluation metrics. When measured with smooth metrics (e.g., Brier score instead of accuracy), abilities emerge gradually, not sharply.
    - **Year**: 2023

12. **Title**: Transformers Learn In-Context via Preconditioned Gradient Descent (Ahn et al., 2023)
    - **Authors**: Ahn et al.
    - **Summary**: Proves linear transformers trained on linear regression tasks learn to implement preconditioned gradient descent at test time (in-context learning). Uses loss landscape analysis to show in-context learning is mechanistically explainable as gradient descent implementation.
    - **Year**: 2023

**Key Challenges**

1. **Architecture-Specific Circuit Discovery**: Current automated methods like ACDC require specifying task-relevant nodes for each architecture, creating a per-architecture manual setup bottleneck that limits scalability across different model families.

2. **Scalability of Circuit Discovery to Large Models**: Manual mechanistic analysis doesn't scale to large models, requiring automated approaches that can handle increasing model complexity without proportional human effort.

3. **Generalization of Interpretability Methods Across Architectures**: Architecture-specific interpretability tools limit transfer learning and prevent unified understanding across different deep learning architectures (transformers, diffusion models, state space models, etc.).

4. **Standardized Evaluation Frameworks for Interpretability Quality**: Lack of consensus metrics for evaluating the quality and usefulness of mechanistic interpretability methods, making it difficult to compare approaches objectively.

5. **Limited Cross-Architecture Structural Similarity**: Current cross-architecture methods like HAGD achieve only 67% structural similarity across model families, suggesting significant architecture-specific components remain that prevent full universality.

6. **GNN Expressive Power Limitations**: Weisfeiler-Leman test limitations mean GNNs cannot distinguish all graph patterns, potentially missing subtle motif variations in computational graphs.

7. **Architecture-Specific Mechanistic Insights**: Results like in-context learning explanations being specific to linear transformers on linear regression tasks highlight the risk that mechanistic insights may not generalize across architectures.

8. **Training Data Sufficiency for Motif Detection**: Uncertainty about whether manually extracted motif instances provide sufficient training data for GNN-based automated detection across diverse architectures.

9. **Validation of Cross-Domain Analogies**: Cross-domain analogies (e.g., biological synaptic motifs to deep learning computational motifs) require rigorous empirical validation rather than assumption, as biological systems have different evolutionary pressures than artificial neural networks.
