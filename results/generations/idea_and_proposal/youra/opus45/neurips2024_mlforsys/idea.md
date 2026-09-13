# Research Idea

## Title
StigmergyPart: Decentralized Stigmergic Coordination for Fault-Tolerant Large-Scale Heterogeneous DL Training

## Motivation
Training large language models across 1000+ heterogeneous accelerators (GPUs, TPUs, NPUs) faces critical challenges: centralized partitioning solvers create coordination bottlenecks, and fault recovery typically requires >60 seconds or full restarts. Existing approaches like SPPO achieve good throughput but scale poorly, while manual DAG construction (FusionLLM) cannot adapt dynamically. As cloud infrastructure becomes increasingly heterogeneous and failure-prone, a scalable, self-healing coordination mechanism is urgently needed.

## Main Idea
We propose StigmergyPart, where decentralized PPO agents coordinate operator placement through bio-inspired stigmergic pheromone signals. Each accelerator deposits pheromones encoding historical performance and LSTM-predicted bottlenecks. Agents read local pheromone matrices from K neighbors to compute placement decisions, enabling O(A·K) communication instead of O(A²) global coordination.

**Core mechanism:** When accelerators fail, their pheromone signals decay to zero, causing operators to automatically "repel" toward healthy alternatives—achieving fault recovery in <10 seconds without central coordination.

**Methodology:** We test across cluster sizes (64-2048 accelerators), heterogeneity levels, and failure rates (0-10/hour), comparing against SPPO and PyTorch FSDP baselines. Ablation studies validate each causal step.

**Expected impact:** Sub-10-second fault recovery, >90% throughput efficiency, and <1% communication overhead at 1000+ accelerator scale, enabling resilient training on dynamic heterogeneous infrastructure.