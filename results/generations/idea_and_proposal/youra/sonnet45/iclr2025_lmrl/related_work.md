## Related Work

**Related Papers**

1. **Title**: Predicting cellular responses to complex perturbations in high‐throughput screens (2023)
   - **Authors**: Lotfollahi et al.
   - **Summary**: CPA establishes compositional perturbation modeling framework combining interpretability of linear models with deep learning flexibility, validating single-cell perturbation prediction approach without pathway structure.
   - **Year**: 2023

2. **Title**: VCWorld: A Biological World Model for Virtual Cell Simulation (arXiv:2512.00306)
   - **Authors**: Wei et al.
   - **Summary**: White-box simulator integrating structured biological knowledge with LLM reasoning achieves SOTA drug perturbation prediction with interpretable mechanistic pathways, demonstrating value of mechanistic integration.
   - **Year**: 2025

3. **Title**: GPO-VAE: modeling explainable gene perturbation responses utilizing GRN-aligned parameter optimization (arXiv:2501.18973)
   - **Authors**: Baek et al.
   - **Summary**: VAE with GRN-aligned parameter optimization (regularization approach) achieves SOTA performance with biological explainability, demonstrating feasibility of pathway integration in VAE latent space.
   - **Year**: 2025

4. **Title**: CPA (Compositional Perturbation Autoencoder)
   - **Authors**: Not specified
   - **Summary**: Primary data-driven baseline without pathway constraints for perturbation prediction; serves as comparison baseline for predictive accuracy and data efficiency.
   - **Year**: Not specified

5. **Title**: MAMMAL (Foundation Model)
   - **Authors**: Not specified
   - **Summary**: Data-driven foundation model identified in Phase 1 as lacking mechanistic integration, representing current black-box approach.
   - **Year**: Not specified

6. **Title**: BioVERSE (Foundation Model)
   - **Authors**: Not specified
   - **Summary**: Data-driven foundation model identified in Phase 1 as lacking mechanistic integration, representing current black-box approach.
   - **Year**: Not specified

7. **Title**: CellFlux (Foundation Model)
   - **Authors**: Not specified
   - **Summary**: Data-driven foundation model identified in Phase 1 as lacking mechanistic integration, representing current black-box approach.
   - **Year**: Not specified

**Key Challenges**

1. **Mechanistic Integration Gap**: Current foundation models (MAMMAL, BioVERSE, CellFlux) are predominantly data-driven black boxes lacking mechanistic integration, representing a VERY HIGH impact research gap in combining data-driven learning with biological knowledge.

2. **Regularization vs. Architectural Integration**: GPO-VAE demonstrates that GRN regularization (soft constraint via loss function) achieves SOTA results, raising the question of whether architectural integration (hard constraint via structure) provides additional benefits beyond regularization-only approaches.

3. **Data Efficiency in Perturbation Modeling**: Existing perturbation prediction models require large amounts of training data, creating barriers for applications with limited experimental samples where mechanistic priors could potentially compensate.

4. **Interpretability vs. Flexibility Trade-off**: Need to quantify trade-offs between mechanistic interpretability (pathway-structured models) and model expressiveness (unconstrained data-driven models) to understand when biological constraints improve versus hurt performance.

5. **Pathway Database Quality Dependency**: Performance of pathway-guided models depends on completeness and accuracy of pathway databases (KEGG, Reactome), which may be incomplete or incorrect for specific cell types and organisms.

6. **Dataset Availability and Quality**: Uncertainty about public accessibility and quality of CPA benchmarks and JUMP-CP datasets for 10K-100K cell experiments, including preprocessing requirements and ground truth availability for pathway activity validation.

7. **Implementation Complexity**: Realistic assessment needed for implementing GNN+ODE+Partitioned VAE architecture, including framework selection (PyG vs. DGL), ODE integration (torchdiffeq vs. custom), and pathway database preprocessing (estimated 2-6 months development timeline).
