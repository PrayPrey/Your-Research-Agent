## Related Work

**Related Papers**
1. **Title**: DeCOS: Data-Efficient RL for Compiler Optimization Selection Ignited by LLM (2025)
   - **Authors**: Tianming Cui, P. Yew, Stephen McCamant, Antonia Zhai
   - **Summary**: Demonstrates that LLM-initialized RL reduces sample complexity by approximately 40% for compiler optimization tasks, establishing the viability of hybrid RL+LLM approaches for compiler optimization.
   - **Year**: 2025

2. **Title**: PartIR: Composing SPMD Partitioning Strategies for Machine Learning (arXiv:2401.11202)
   - **Authors**: Alabed et al. (Google)
   - **Summary**: Provides mathematical proof that composable SPMD strategies (data/tensor/pipeline/sequence parallelism) form a complete partitioning space for distributed machine learning.
   - **Year**: 2024

3. **Title**: Alpa: Automating Inter- and Intra-Operator Parallelism for Distributed DL (arXiv:2201.12023)
   - **Authors**: Zheng et al. (UC Berkeley, Google)
   - **Summary**: State-of-the-art heuristic-based automatic parallelism system that demonstrates the limitations of non-adaptive heuristic approaches (brittleness and lack of learning).
   - **Year**: 2022

4. **Title**: pytorch/torchtitan
   - **Authors**: Not specified
   - **Summary**: Production LLM training framework with hand-tuned 3D parallelism (FSDP + tensor parallel + pipeline parallel) using heuristic partitioning rules.
   - **Year**: 2024

5. **Title**: openxla/shardy
   - **Authors**: Not specified
   - **Summary**: Rule-based MLIR partitioning system for distributed machine learning compilation.
   - **Year**: 2024

6. **Title**: alibaba/TePDist
   - **Authors**: Not specified
   - **Summary**: Heuristic-based HLO-level automatic tensor program distribution for distributed training, limited to <1000 GPU deployments.
   - **Year**: 2023

7. **Title**: Co-Evolution With DRL for Energy-Aware Distributed Scheduling
   - **Authors**: Rui Li, Wenyin Gong, Ling Wang, Chao Lu, Chenxin Dong
   - **Summary**: Demonstrates that weighted multi-objective deep reinforcement learning achieves 20-30% performance gains in manufacturing scheduling, validating multi-objective RL approaches.
   - **Year**: 2024

8. **Title**: Designing Cost-Effective Cache Replacement Policy Using ML
   - **Authors**: Subhash Sethumurugan, Jieming Yin, J. Sartori
   - **Summary**: Establishes precedent that learned RL policies can outperform hand-crafted heuristics by 3-5% in cache replacement with low overhead (<17KB), demonstrating viability of learned system heuristics.
   - **Year**: 2021

9. **Title**: Learning to Shard (RL for parallelism - inference-focused)
   - **Authors**: Not specified
   - **Summary**: Uses reinforcement learning for parallelism optimization focused on inference workloads (to be retrieved in Phase 2B for detailed comparison).
   - **Year**: Not specified

**Key Challenges**
1. **Production-Scale Scalability**: Existing ML models for compiler optimization have not been validated for 1000+ GPU clusters in reasonable time, representing a critical gap in production-scale ML compiler optimization.

2. **Generalization Across Workloads**: Fundamental question remains unanswered about whether RL policies can learn abstract partitioning principles that transfer across model architectures and hardware topologies, or if they inherently overfit to training distributions.

3. **LLM Knowledge Transfer Uncertainty**: High risk that LLMs lack sufficient distributed training system knowledge, creating uncertainty about whether LLM-guided exploration will be effective for SPMD partitioning tasks.

4. **PartIR Action Space Completeness**: PartIR's composable strategy space may need extensions for LLM-specific patterns (e.g., context parallelism for long sequences, expert parallelism for MoE models).

5. **Fixed Reward Weight Robustness**: Uncertainty about whether expert-determined fixed weights are robust across diverse production use cases or if multi-objective Pareto approaches are needed.

6. **Cost-Benefit Tradeoffs**: Need to establish that RL training cost is justified by deployment savings over realistic numbers of production training runs.

7. **Heuristic Brittleness**: State-of-the-art automated approaches (Alpa, TePDist) rely on heuristics that are non-adaptive and brittle across diverse workloads and scales.

8. **Training-Inference Gap**: Most existing parallelism optimization work focuses on inference scenarios, while training requires fundamentally different partitioning strategies due to backward pass and optimizer state requirements.
