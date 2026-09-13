## Related Work

**Related Papers**
1. **Title**: FusionLLM: A Decentralized LLM Training System on Geo-distributed GPUs (arXiv:2410.12707)
   - **Authors**: Tang et al.
   - **Summary**: Introduces OP-DAG representation for decentralized training achieving 1.45-9.39x speedup over baselines, though requiring manual DAG construction.
   - **Year**: 2024

2. **Title**: SPPO: Efficient Long-sequence LLM Training via Adaptive Sequence Pipeline Parallel Offloading (arXiv:2503.10377)
   - **Authors**: Chen et al.
   - **Summary**: Proposes a heuristic solver for sequence pipeline parallel offloading that achieves 3.38x throughput on 128 A100s, using centralized optimization.
   - **Year**: 2025

3. **Title**: Dual-Signaling ACO: Proactive Pheromone Injection for Adaptive Load Balancing (IEEE:11234105)
   - **Authors**: Verma et al.
   - **Summary**: Introduces proactive pheromone injection using prediction to accelerate load redistribution in ant colony optimization systems.
   - **Year**: 2025

4. **Title**: Cephalo: Harnessing Heterogeneous GPU Clusters for Training Transformer Models (arXiv:2411.01075)
   - **Authors**: Guo et al.
   - **Summary**: Decouples compute from memory assignment to achieve 1.2-10.8x throughput improvements on heterogeneous GPU clusters.
   - **Year**: 2024

5. **Title**: Model Parallelism on Distributed Infrastructure: A Literature Review
   - **Authors**: Brakel et al.
   - **Summary**: Comprehensive survey of distributed deep learning training that identifies heterogeneity as a critical unsolved challenge.
   - **Year**: 2024

6. **Title**: PyTorch DDP/FSDP Documentation
   - **Authors**: Not specified
   - **Summary**: Official documentation for PyTorch's distributed data parallel and fully sharded data parallel implementations, which assume homogeneous GPU clusters.
   - **Year**: Not specified

7. **Title**: NoSync: Particle Swarm Inspired Distributed DNN Training
   - **Authors**: Isakov & Kinsy
   - **Summary**: Demonstrates a PSO-inspired approach that achieves linear speedup without synchronization barriers, validating decentralized coordination for deep learning.
   - **Year**: 2018

8. **Title**: SplitQuant: Resource-Efficient LLM Serving on Heterogeneous GPUs
   - **Authors**: Zhao et al.
   - **Summary**: Proposes phase-aware partitioning with adaptive quantization to achieve 2.34x throughput improvement for LLM serving on heterogeneous hardware.
   - **Year**: 2025

**Key Challenges**
1. **Manual DAG Construction**: Existing decentralized training systems like FusionLLM require manual construction of operation DAGs, limiting automation and scalability.
2. **Centralized Optimization Bottleneck**: Heuristic solvers for pipeline parallelism rely on centralized optimization that becomes a bottleneck at larger scales.
3. **Heterogeneous GPU Cluster Support**: Mainstream frameworks like PyTorch DDP/FSDP assume homogeneous GPU clusters, failing to efficiently utilize heterogeneous hardware configurations.
4. **Heterogeneity as Unsolved Challenge**: Literature surveys confirm that handling hardware heterogeneity remains a critical unsolved problem in distributed deep learning training.
5. **Adaptive Load Balancing**: Dynamic workload redistribution across heterogeneous resources requires predictive mechanisms to proactively respond to changing conditions.
