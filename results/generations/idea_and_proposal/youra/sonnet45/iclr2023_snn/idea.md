# SparseNetBench: A Cross-Platform Benchmark for Hardware-Aware Sparse Neural Network Deployment

## Motivation
Training billion-parameter models consumes massive computational resources, energy, and produces substantial carbon footprints. While sparsity (removing 50-90% of network weights) promises efficiency gains, current evaluations are fragmented across single hardware platforms, obscuring critical performance variability. Researchers lack standardized tools to answer: "Which sparsity pattern is optimal for my target hardware?" This gap leads to suboptimal deployment choices, leaving 1.5-3x potential speedups unrealized.

## Main Idea
We propose **SparseNetBench**, a vendor-neutral benchmark evaluating three representative sparsity patterns (unstructured magnitude pruning, NVIDIA's 2:4 N:M structured sparsity, and 4×4 block-sparse) across commodity hardware (NVIDIA GPUs, Intel CPUs, Google TPUs). The core hypothesis: **cross-platform performance variability for identical sparsity patterns will reach 1.5-3x speedup deltas**, revealing hardware-dependent optimal pairings currently hidden by single-platform studies.

Our methodology introduces **iso-metric normalization** (iso-power and iso-latency Pareto frontiers) to enable fair comparison across different power budgets, addressing the unfairness of comparing 300W GPUs to 65W CPUs. We provide Docker-containerized reference implementations with <±5% reproducibility guarantees.

Expected impact: Quantify the "optimization gap" between naive and vendor-optimized implementations, demonstrate that structured patterns (e.g., 2:4 N:M on Sparse Tensor Cores) outperform unstructured by 1.3-2x despite similar accuracy, and deliver an interactive decision tool mapping deployment constraints to optimal (pattern, hardware) recommendations—reducing deployment trial-and-error from weeks to minutes.