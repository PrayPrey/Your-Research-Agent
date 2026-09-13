# Research Idea

## Title
EcoParallel: Neural Hyper-Heuristic Parallelism Selection via Ecological-Niche-Inspired Geometric Partitioning for Heterogeneous GPU Clusters

## Motivation
Training large neural networks on heterogeneous GPU clusters (mixing A100/V100/T4) is increasingly common but poorly optimized. Current parallelism strategies (FSDP, tensor/pipeline parallelism) are either static or require expensive per-configuration tuning, leaving 15-30% performance on the table. While recent work like H2 achieves 16% speedup through offline heterogeneous optimization, no method dynamically adapts parallelism strategies at runtime based on learned hardware-workload affinity. This gap prevents smaller research teams from efficiently utilizing mixed-generation GPU resources.

## Main Idea
We propose EcoParallel, a neural hyper-heuristic that dynamically selects parallelism strategies (TP/PP/DP/FSDP) at stage-level granularity using ecological-niche-inspired geometric partitioning. The core mechanism operates in four steps: (1) profile GPU capabilities into a 3D feature space [compute_TFLOPS, memory_GB, bandwidth_GB/s], (2) apply Voronoi-like clustering to group devices with similar capability profiles, (3) train a lightweight 3-layer MLP to predict optimal strategy per model stage, and (4) coordinate multi-strategy execution with minimal synchronization overhead.

The key innovation is transfer learning from proxy models (GPT-2 small) to target models (LLaMA-7B), amortizing optimization costs. We predict 12-18% throughput improvement over static baselines, with falsification threshold at ≤8%. Validation requires 20+ runs across 18 configurations testing heterogeneity degrees, model sizes, and cluster compositions.