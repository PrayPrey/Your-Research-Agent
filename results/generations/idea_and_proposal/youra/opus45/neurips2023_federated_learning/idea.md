## Title
FILIA: Fisher Information-Weighted Aggregation for Efficient Federated Fine-Tuning of Foundation Models

## Motivation
Federated learning enables privacy-preserving collaborative training, but fine-tuning foundation models across heterogeneous data distributions remains challenging. Standard aggregation methods like FedAvg treat all parameter updates equally, ignoring that different clients contribute varying amounts of task-relevant information. This uniform averaging causes slow convergence under non-IID conditions—a critical bottleneck when communication rounds are expensive. While parameter-efficient fine-tuning (PEFT) methods like LoRA reduce computational costs, the aggregation problem persists. We address this gap by leveraging Fisher Information to identify which parameters encode the most valuable local knowledge.

## Main Idea
We propose FILIA (Fisher Information-weighted Local Importance Aggregation), which weights parameter contributions during federated aggregation based on their Fisher Information scores. The core mechanism: parameters with higher Fisher values capture more task-relevant gradients and should receive proportionally higher aggregation weights. Each client computes diagonal Fisher approximations for LoRA adapter parameters (computationally efficient due to low-rank structure), transmits quantized scores alongside updates, and the server performs importance-weighted averaging.

**Key methodology:** Compare FILIA against FedAvg/FedProx baselines across varying heterogeneity levels (Dirichlet α=0.1-10.0) on LLaMA-7B and RoBERTa, measuring communication rounds to target accuracy.

**Expected outcomes:** 1.5-2x faster convergence under high heterogeneity, with <2% communication overhead. This enables practical federated fine-tuning of foundation models while respecting data privacy constraints.