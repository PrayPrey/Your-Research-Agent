## Related Work

**Related Papers**

1. **Title**: Beyond Euclid: An Illustrated Guide to Modern Machine Learning with Geometric, Topological, and Algebraic Structures (Papillon et al., 2024) [SS ID: 530b26ee44d4d565ee8661da86e03ef1f473385a]
   - **Authors**: Papillon et al.
   - **Summary**: Demonstrates that geometric, topological, and algebraic structures capture complementary aspects of data through a graphical taxonomy showing distinct mathematical properties. Each TAG structure extracts different invariants: geometric (geodesic distances, graph connectivity), topological (homology classes, persistence diagrams), and algebraic (group orbits, equivariant features).
   - **Year**: 2024

2. **Title**: Model Theory of Deduction (Johnson-Laird, 1992)
   - **Authors**: P.N. Johnson-Laird
   - **Summary**: Foundational cognitive psychology work showing that humans construct spatial mental models to reason about abstract systems. Provides theoretical grounding for geometric mental model approach to explainability.
   - **Year**: 1992

3. **Title**: Mental Models in Chemistry Education (Coll & Treagust, 2003)
   - **Authors**: Coll & Treagust
   - **Summary**: Chemistry education literature demonstrating that chemists naturally reason about molecular properties via 3D spatial models, supporting the assumption that domain experts prefer geometric visualizations.
   - **Year**: 2003

4. **Title**: Topology Layer (Gabrielsson et al., 2020) [Implementation: bruel-gabrielsson/TopologyLayer]
   - **Authors**: Gabrielsson et al.
   - **Summary**: Demonstrates that persistent homology features in activation spaces correlate with model decisions through a differentiable topology layer. Shows topological invariants capture decision boundary structure including connected components (H₀), loops/cyclic patterns (H₁), and higher-order structure (H₂).
   - **Year**: 2020

5. **Title**: Principles of Equivariant Networks (Kondor, 2025) [SS ID: a26840e13f3ab6f45933aad505c15b7fc95b7dbc]
   - **Authors**: Kondor
   - **Summary**: Establishes group theory foundations showing E(3)-equivariant networks guarantee prediction consistency under rotations/translations. e3nn SO(3)-equivariant layers satisfy φ(Rg) = R·φ(g) for rotation matrices R, ensuring explanation consistency.
   - **Year**: 2025

6. **Title**: UMAP: Uniform Manifold Approximation and Projection (McInnes et al., 2018)
   - **Authors**: McInnes et al.
   - **Summary**: Dimension reduction technique using Riemannian manifold approximation to preserve both local topological structure (k-nearest neighbors) and global geometric relationships (fuzzy simplicial complex), enabling meaningful 2D/3D projections.
   - **Year**: 2018

7. **Title**: TDA Applications Review (Su & Wei, 2025)
   - **Authors**: Su & Wei
   - **Summary**: Review showing TDA features improve molecular property prediction, suggesting chemical relevance of topological features. Acknowledges persistent homology scalability as an open challenge.
   - **Year**: 2025

8. **Title**: GNNExplainer: Generating Explanations for Graph Neural Networks (Ying et al., 2019)
   - **Authors**: Ying et al.
   - **Summary**: Learns binary masks on edges and node features to identify minimal decision-relevant subgraphs by optimizing mask M via gradient descent. Serves as primary geometric baseline, built into PyTorch Geometric.
   - **Year**: 2019

9. **Title**: A Unified Approach to Interpreting Model Predictions (SHAP) (Lundberg & Lee, 2017)
   - **Authors**: Lundberg & Lee
   - **Summary**: Shapley value-based feature attribution from cooperative game theory using KernelSHAP approximation. De facto standard for XAI but model-agnostic approach ignores graph structure.
   - **Year**: 2017

10. **Title**: "Why Should I Trust You?": Explaining the Predictions of Any Classifier (LIME) (Ribeiro et al., 2016)
    - **Authors**: Ribeiro et al.
    - **Summary**: Local Interpretable Model-agnostic Explanations via linear approximation by sampling perturbed neighbors and fitting local linear model. Widely cited (15,000+ citations) but less stable on graph data.
    - **Year**: 2016

11. **Title**: Trustworthiness Metric for Dimension Reduction (Venna & Kaski, 2006)
    - **Authors**: Venna & Kaski
    - **Summary**: Develops metric for measuring preservation of high-dimensional structure in low-dimensional projections, particularly k-nearest neighbor relationships. Used to validate UMAP projection quality.
    - **Year**: 2006

12. **Title**: PGExplainer: Parametric Graph Explainer (Luo et al., 2020)
    - **Authors**: Luo et al.
    - **Summary**: Learns parametric explainer model that generates explanations via neural network rather than optimization. Faster and more stable than GNNExplainer with amortized computation.
    - **Year**: 2020

13. **Title**: SubgraphX: Explaining Graph Neural Networks with Structure-Aware Cooperative Computation (Yuan et al., 2021)
    - **Authors**: Yuan et al.
    - **Summary**: Uses Monte Carlo Tree Search to find optimal explaining subgraph through combinatorial optimization. More faithful than GNNExplainer with expected fidelity around 0.35.
    - **Year**: 2021

14. **Title**: Topological XAI (Rathore et al., 2021)
    - **Authors**: Rathore et al.
    - **Summary**: Uses persistent homology for explainability with topology-only approach (no geometry/algebra integration). Provides direct comparison baseline for isolating topology contribution.
    - **Year**: 2021

15. **Title**: Thematic Analysis (Braun & Clarke, 2006)
    - **Authors**: Braun & Clarke
    - **Summary**: Qualitative research methodology for identifying patterns/themes in data through coding. Provides methodological framework for analyzing expert interview feedback.
    - **Year**: 2006

**Key Challenges**

1. **Topological Semantic Meaningfulness**: Persistent homology features computed on activation manifolds may be model-specific artifacts without genuine chemical interpretation. Risk that activation space topology doesn't align with domain intuition despite correlations.

2. **UMAP Information Loss**: Dimension reduction from high-dimensional TAG-ML feature space (d≈100-500) to 2D/3D mental models inevitably loses information. Critical explanation features may be discarded, potentially degrading faithfulness.

3. **Expert Cognitive Preferences**: Domain experts may prefer statistical/tabular explanations over geometric visualizations despite chemistry's 3D focus. Expert training and domain culture could favor feature importance rankings.

4. **Computational Tractability**: Persistent homology has O(n³) worst-case complexity, potentially exceeding interactive latency budgets (<5 seconds) for large graphs (>1000 nodes) despite sparse algorithms and GPU acceleration.

5. **Limited Graph-Structured Data**: Current XAI methods (SHAP, LIME, attention visualization) lack mathematical rigor and fail to leverage topological/algebraic/geometric structure inherent in graph-structured data.

6. **Baseline Comparison Fairness**: Need to ensure unbiased comparison through validation-based hyperparameter tuning for all methods (TAG-ML and baselines) using same metrics and computational budget.

7. **Cross-Domain Generalization**: Framework designed for graph-structured scientific domains may not transfer to non-scientific applications (social networks, e-commerce) where different explanation paradigms are needed.

8. **Post-Hoc Limitation**: Framework explains existing model decisions but doesn't improve predictions or architecture. More powerful ante-hoc interpretability requires equivariant architectures (SchNet, DimeNet) from design stage.
