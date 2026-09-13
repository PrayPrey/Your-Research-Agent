## Related Work

**Related Papers**
1. **Title**: The Forward-Forward Algorithm: Some Preliminary Investigations (2022)
   - **Authors**: Geoffrey E. Hinton
   - **Summary**: Introduces the Forward-Forward algorithm with layer-local goodness objectives using dual forward passes (positive/negative data), eliminating backpropagation. This foundational work demonstrates the mechanism for per-layer memory reduction by optimizing local "goodness" functions without storing intermediate activations for backward pass gradient computation.
   - **Year**: 2022

2. **Title**: Distance-Forward Learning: Enhancing the Forward-Forward Algorithm Towards High-Performance On-Chip Learning (2024)
   - **Authors**: Yujie Wu, Siyuan Xu, et al.
   - **Summary**: Achieves 88.2% CIFAR-10 accuracy with less than 40% memory cost versus backpropagation, empirically validating Forward-Forward memory efficiency. Notes that standard FF struggles on complex datasets without modifications, requiring distance metric learning for CIFAR-10 performance.
   - **Year**: 2024

3. **Title**: Module-wise Training of Neural Networks via the Minimizing Movement Scheme (2023)
   - **Authors**: Skander Karkar, Ibrahim Ayed, et al.
   - **Summary**: Introduces TRGL regularization enabling 60% memory reduction with module-wise training, solving the greedy stagnation problem. Provides evidence for cross-layer memory isolation benefits, though uses end-to-end backpropagation within modules rather than FF local objectives.
   - **Year**: 2023

4. **Title**: OmniLearn: A Framework for Distributed Deep Learning Over Heterogeneous Clusters (2025)
   - **Authors**: Sahil Tyagi, Prateek Sharma
   - **Summary**: Demonstrates adaptive batch-scaling reducing training time by 14-85% on heterogeneous clusters. Validates the feasibility of distributed training with device heterogeneity through adaptive batch adjustment based on device capability.
   - **Year**: 2025

5. **Title**: Hivemind: A Library for Decentralized Deep Learning
   - **Authors**: Not specified
   - **Summary**: Open-source framework providing production-ready distributed consensus primitives for asynchronous coordination, supporting target device scales of 10-100 nodes. Serves as the framework basis for quorum-based protocol coordination in distributed async learning.
   - **Year**: Not specified

6. **Title**: SymBa: Symmetric Backpropagation-Free Contrastive Learning with Forward-Forward Algorithm (2023)
   - **Authors**: Heung-Chang Lee, Jeonggeun Song
   - **Summary**: Solves the asymmetric gradient problem in Forward-Forward algorithm but still uses single-device training, highlighting the need for distributed approaches to extend FF's applicability to heterogeneous environments.
   - **Year**: 2023

**Key Challenges**
1. **FF Convergence on Complex Tasks**: Forward-Forward converges well on simple tasks (MNIST) but struggles on complex datasets (CIFAR-10) without modifications such as distance metric learning, raising questions about reliability across different task complexities.

2. **Interaction Between FF and Greedy Layer-wise Training**: No existing work validates whether FF local objectives are compatible with greedy layer-wise expansion. Module-wise TRGL demonstrates greedy training success but uses backpropagation within modules, leaving the FF+greedy interaction empirically unvalidated.

3. **Asynchronous Coordination Overhead**: While Hivemind provides async coordination primitives, the overhead impact on training time in the context of layer-wise greedy expansion with FF objectives remains unmeasured, with uncertainty about whether coordination latency negates memory efficiency benefits.

4. **Heterogeneous Device Scalability**: OmniLearn demonstrates adaptive batch-scaling for heterogeneity, but whether quorum-based consensus scales effectively to 10-100 devices with varying compute capabilities without prohibitive network overhead is unverified.

5. **Accuracy-Memory Tradeoff Gap**: Existing localized learning methods (FF, module-wise training) are studied in isolation. No systematic investigation exists of hybrid architectures combining multiple local methods to achieve multiplicative efficiency gains while maintaining acceptable accuracy degradation.

6. **Convergence Detection Reliability**: The goodness variance threshold (< 0.01) for detecting FF layer convergence lacks validation across different architectures and datasets, with uncertainty about whether architecture-specific or dataset-specific tuning is required.

7. **Distributed Training on Unreliable Hardware**: While individual components (async coordination, heterogeneous batch-scaling) exist, no framework combines them with localized learning methods to enable training on unreliable edge devices where connectivity and compute availability are intermittent.
