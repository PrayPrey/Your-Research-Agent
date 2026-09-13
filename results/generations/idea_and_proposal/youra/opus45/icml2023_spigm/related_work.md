## Related Work

**Related Papers**
1. **Title**: Sparse Training of Discrete Diffusion Models for Graph Generation (Semantic Scholar ID: 912273639b82822e94e6585438aac5de4d9e5c63)
   - **Authors**: Qin et al.
   - **Summary**: SparseDiff achieves linear complexity O(|E|) through sparse edge selection, providing a foundation architecture for per-level sparse diffusion in graph generation.
   - **Year**: 2023

2. **Title**: SwinGNN: Rethinking Permutation Invariance in Diffusion Models (Semantic Scholar ID: 7e243fd3fc349ff9fc7c3011543823645ac25ed6)
   - **Authors**: Yan et al.
   - **Summary**: Demonstrates that non-invariant diffusion with post-hoc permutation achieves state-of-the-art quality, informing permutation handling approaches in multi-scale settings.
   - **Year**: 2023

3. **Title**: Modeling Hierarchical Brain Networks via Volumetric Sparse Deep Belief Network (DOI: 10.1109/TBME.2019.2945231)
   - **Authors**: Dong et al.
   - **Summary**: Shows that brain networks exhibit efficient multi-scale hierarchical organization, providing cross-domain inspiration for hierarchical decomposition principles in graph generation.
   - **Year**: 2020

4. **Title**: Graph Coarsening with Preserved Spectral Properties
   - **Authors**: Loukas
   - **Summary**: Provides spectral approximation guarantees for graph coarsening, establishing theoretical foundations for spectral-preserving coarsening methods.
   - **Year**: 2019

5. **Title**: DiGress
   - **Authors**: Vignac et al.
   - **Summary**: Presents a dense discrete diffusion approach for graph generation, serving as a comparison baseline for evaluating sparse and hierarchical methods.
   - **Year**: 2022

6. **Title**: HiGen
   - **Authors**: Karami et al.
   - **Summary**: Proposes a hierarchical non-diffusion approach to graph generation, providing a baseline for comparing hierarchical generation strategies.
   - **Year**: 2023

7. **Title**: Evaluation Metrics for Graph Generative Models
   - **Authors**: O'Bray et al.
   - **Summary**: Demonstrates limitations of current evaluation approaches for graph generative models, noting that no models have been tested beyond 10K nodes.
   - **Year**: 2021

8. **Title**: Neural Graph Generator
   - **Authors**: Evdaimon et al.
   - **Summary**: Shows the potential of latent diffusion for graph generation but remains limited to moderate scale graphs.
   - **Year**: 2024

**Key Challenges**
1. **Scalability Beyond 10K Nodes**: Current evaluation metrics and graph generative models have not been tested or demonstrated to work effectively on graphs larger than 10,000 nodes.
2. **Single-Scale Limitations**: Existing sparse diffusion methods like SparseDiff operate at a single scale, potentially missing hierarchical structure in complex graphs.
3. **Permutation Handling in Multi-Scale Settings**: Adapting permutation invariance or non-invariance strategies from single-scale to multi-scale hierarchical generation remains an open problem.
4. **Moderate Scale Constraints in Latent Diffusion**: Current latent diffusion approaches for graphs show promise but are limited to moderate-scale graphs rather than large-scale applications.
