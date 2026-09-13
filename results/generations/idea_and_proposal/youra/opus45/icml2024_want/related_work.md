## Related Work

**Related Papers**
1. **Title**: H2: Towards Efficient Large-Scale LLM Training on Hyper-Heterogeneous Cluster over 1,000 Chips (Semantic Scholar ID: 25234a666e860f823ab04b9c6ab7688fc9183d6d)
   - **Authors**: Tang et al.
   - **Summary**: Proposes HeteroPP with HeteroAuto for large-scale LLM training on heterogeneous clusters, achieving 16.37% speedup by addressing compute, memory, and communication as key heterogeneity factors.
   - **Year**: 2025

2. **Title**: Optimal Distributed Training With Co-Adaptive Data Parallelism in Heterogeneous Environments (Semantic Scholar ID: da0026a2a25dcbb3de3a84bc51c9b646f4766512)
   - **Authors**: Chen et al.
   - **Summary**: Introduces C-ADP for co-adaptive data distribution in heterogeneous environments, achieving 21.6x FLOPS improvement through adaptive data parallelism approaches.
   - **Year**: 2025

3. **Title**: Heterogeneous Computational Scheduling Using Adaptive Neural Hyper-Heuristic
   - **Authors**: Allahverdyan et al.
   - **Summary**: Proposes a two-level neural and heuristic approach for heterogeneous computational scheduling, achieving 28.49% makespan reduction through adaptive strategy selection.
   - **Year**: 2025

4. **Title**: HAPT: Heterogeneity-Aware Automated Parallel Training
   - **Authors**: Not specified
   - **Summary**: Presents a fine-grained offline planner for inter-operator parallel strategy search in heterogeneous training environments.
   - **Year**: 2025

5. **Title**: CollaPipe: Adaptive Segment-Optimized Pipeline Parallelism
   - **Authors**: Chen et al.
   - **Summary**: Demonstrates the effectiveness of variable-sized segments for pipeline parallelism in encoder models, providing evidence for stage-level granularity approaches.
   - **Year**: 2025

6. **Title**: PyTorch FSDP Documentation
   - **Authors**: Not specified
   - **Summary**: Documents PyTorch's Fully Sharded Data Parallel implementation, noting that manual configuration is required for heterogeneous setups.
   - **Year**: Not specified

7. **Title**: Distributed Training Strategies Study (arXiv:2505.12832v1)
   - **Authors**: Ovi
   - **Summary**: Analyzes distributed training strategies, finding that FSDP reduces memory by 60% but increases training time by 6x compared to DDP, highlighting significant trade-offs between parallelism approaches.
   - **Year**: 2025

**Key Challenges**
1. **Manual Configuration Burden**: Current systems like PyTorch FSDP require manual configuration for heterogeneous setups, lacking automatic optimization capabilities for diverse hardware environments.

2. **Strategy Trade-offs**: Existing parallelism strategies present significant trade-offs (e.g., FSDP's 60% memory reduction comes with 6x training time increase), necessitating adaptive approaches that can balance these competing factors.

3. **Limited Multi-Strategy Adaptation**: Prior work like C-ADP focuses on single parallelism dimensions (data parallelism only) rather than comprehensive multi-strategy approaches that can adapt across different parallelism types.

4. **Offline vs Runtime Adaptation**: Existing heterogeneity-aware planners like HAPT rely on offline planning rather than runtime adaptive mechanisms, limiting their ability to respond to dynamic cluster conditions.

5. **Heterogeneity Factor Complexity**: Training on hyper-heterogeneous clusters requires simultaneously addressing compute, memory, and communication heterogeneity factors, which existing systems handle incompletely.
