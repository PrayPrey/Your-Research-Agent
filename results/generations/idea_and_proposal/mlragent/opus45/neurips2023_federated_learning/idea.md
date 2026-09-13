# Title: Prompt Gradient Routing: Communication-Efficient Federated Prompt Tuning via Sparse Gradient Selection

## Motivation
Fine-tuning foundation models in federated settings faces a critical communication bottleneck. While parameter-efficient methods like prompt tuning reduce trainable parameters, clients must still exchange gradients for soft prompts across communication rounds. In heterogeneous FL environments with non-IID data, prompt gradients can diverge significantly across clients, leading to slow convergence and excessive communication overhead. Current FL aggregation methods treat all gradient dimensions equally, ignoring that different prompt tokens may be relevant to different client data distributions.

## Main Idea
We propose **Prompt Gradient Routing (PGR)**, a communication-efficient federated prompt tuning framework that leverages gradient sparsity patterns to enable selective aggregation. The key insight is that in heterogeneous settings, specific prompt token gradients carry task-relevant information for subsets of clients.

**Methodology:**
1. Each client computes prompt gradients and generates a sparse mask identifying the top-k most significant gradient dimensions based on magnitude and directional consistency across local batches
2. Clients transmit only masked gradients along with lightweight routing metadata
3. The server performs cluster-aware aggregation, grouping clients with similar gradient sparsity patterns and computing weighted averages within clusters
4. Aggregated updates are routed back selectively based on cluster membership

**Expected Outcomes:** 60-80% communication reduction while maintaining or improving convergence compared to FedAvg-based prompt tuning. The approach naturally enables personalization through routing, addressing heterogeneity without additional computation.