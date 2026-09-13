# Research Idea

## Title
Multi-Scale Hierarchical Sparse Diffusion for Million-Node Graph Generation

## Motivation
Current graph diffusion models face a critical scalability barrier: generating graphs beyond 100K nodes becomes computationally prohibitive due to quadratic complexity in edge operations. While sparse diffusion methods achieve linear complexity, they operate at a single scale and struggle with large graphs. Real-world applications—social networks, knowledge graphs, molecular structures—require generating graphs with millions of nodes while preserving structural properties. This gap between theoretical capability and practical scalability limits the deployment of generative models for scientific and industrial applications.

## Main Idea
We propose Multi-Scale Hierarchical Sparse Diffusion (MS-HSD), which combines spectral-preserving graph coarsening with sparse diffusion across multiple hierarchy levels. The core mechanism operates in four steps: (1) spectral coarsening reduces graph size while preserving eigenvalue structure, (2) sparse diffusion operates efficiently at each coarsened level with O(|E|/K) per-step complexity, (3) GNN-based cross-scale refinement conditions fine-level generation on coarse structure, and (4) consistency loss enforces coherent multi-scale generation. We hypothesize that with K=3 hierarchical levels, MS-HSD can generate 1M+ node graphs while maintaining generation quality (MMD metrics) within 5% of single-scale baselines. Validation involves scaling experiments on community-structured graphs, ablation studies isolating each mechanism component, and comparison against SparseDiff baselines. Success would enable practical large-scale graph generation for scientific discovery and network analysis.