## Related Work

**Related Papers**

1. **Title**: Sparse MoE (Outrageously Large Neural Networks) (Shazeer et al., 2017)
   - **Authors**: Shazeer et al.
   - **Summary**: Foundation work for sparse expert activation using top-K routing mechanisms in Mixture-of-Experts architectures.
   - **Year**: 2017

2. **Title**: Switch Transformer (Fedus et al., 2021)
   - **Authors**: Fedus et al.
   - **Summary**: Simplified routing using top-1 selection, enabling massive scaling to 1.6T parameters with 7x speedup.
   - **Year**: 2021

3. **Title**: LLaMA-MoE (Zhu et al., 2024)
   - **Authors**: Zhu et al.
   - **Summary**: Dense-to-MoE upcycling approach that partitions existing FFN into 8 experts for efficient model scaling.
   - **Year**: 2024

4. **Title**: Intrinsic Dimensionality (Aghajanyan et al., 2020)
   - **Authors**: Aghajanyan et al.
   - **Summary**: Demonstrated that tasks have low-dimensional solutions, providing theoretical foundation for low-rank adaptation approaches.
   - **Year**: 2020

5. **Title**: LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
   - **Authors**: Hu et al.
   - **Summary**: Introduced low-rank adaptation for efficient fine-tuning of large language models using rank decomposition with 15K+ citations.
   - **Year**: 2021

6. **Title**: SplitLoRA (Lin et al., 2024)
   - **Authors**: Lin et al.
   - **Summary**: Uses LoRA for federated fine-tuning with privacy focus and collaborative LoRA training across distributed settings.
   - **Year**: 2024

7. **Title**: LoraHub (2023)
   - **Authors**: Not specified
   - **Summary**: Demonstrates LoRA composition via gradient-free optimization for LoRA selection and combination.
   - **Year**: 2023

8. **Title**: MoE Survey (Fedus et al., 2022)
   - **Authors**: Fedus et al.
   - **Summary**: Comprehensive survey covering routing mechanisms and load balancing strategies in Mixture-of-Experts architectures.
   - **Year**: 2022

9. **Title**: Sequential Merging (Tang et al., 2025)
   - **Authors**: Tang et al.
   - **Summary**: Proposes fixed merging strategies for combining multiple LoRA adapters without learned routing.
   - **Year**: 2025

**Key Challenges**

1. **Parameter Efficiency vs Capacity Trade-off**: Standard FFN-based MoE experts require large parameter counts (dimension 4096+) which limits scaling to 8-64 experts, while achieving both high capacity and parameter efficiency remains unsolved.

2. **Expert Collapse in MoE**: Routers tend to converge to using <20% of available experts despite load balancing mechanisms, leading to unutilized capacity and wasted parameters.

3. **Independent Training Coordination**: PEFT modules trained independently may produce incompatible parameter subspaces that cannot be effectively composed through routing, limiting collaborative model development approaches.

4. **Routing Overhead at Scale**: Computational cost of routing to 100+ experts can negate parameter efficiency gains, particularly with flat routing architectures that must evaluate all experts.

5. **Gap in PEFT-MoE Integration**: No existing work explicitly treats PEFT modules (like LoRA) as MoE expert specialists with learned routing mechanisms, representing an unexplored research direction with zero prior implementations.

6. **Capacity Constraint of Low-Rank Experts**: LoRA's low-rank bottleneck (rank 8-32) may limit individual expert expressiveness compared to full FFN experts, raising questions about performance equivalence.

7. **Evaluation Variance**: MMLU benchmark results can vary >3% across runs, making it difficult to detect small (2%) performance differences between architectures with statistical confidence.

8. **Load Balancing Effectiveness**: Balancing expert utilization without degrading task performance remains challenging, as load balancing losses may conflict with task accuracy objectives.
