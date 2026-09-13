## Related Work

**Related Papers**

1. **Title**: MinatoLoader: Accelerating Machine Learning Training Through Efficient Data Preprocessing (Semantic Scholar ID: f0eb84d48425995397b39d0023ef29925d442f23)
   - **Authors**: Nouaji, R., Bitchebe, S., Macedo, R., Balmau, O.
   - **Summary**: Demonstrates that priority-based sample scheduling achieves 7.5× speedup on heterogeneous preprocessing workloads. HPrefetch extends this work by adding adaptive thresholds and queueing theory formalization to MinatoLoader's static priority concept.
   - **Year**: 2025

2. **Title**: SpeedyLoader: Efficient Pipelining of Data Preprocessing and Machine Learning Training (Semantic Scholar ID: c3ae9fb7978010924507cdc900dcf8500d4a3fd0)
   - **Authors**: Nouaji, R., Bitchebe, S., Balmau, O.
   - **Summary**: Achieves 30% training time reduction through asynchronous preprocessing pipeline that overlaps preprocessing with training. However, it lacks priority awareness and treats all samples equally.
   - **Year**: 2024

3. **Title**: Lotus: Characterization of Machine Learning Preprocessing Pipelines via Framework and Hardware Profiling (Semantic Scholar ID: d17b0088f0249e7c9953ce3dab2769bd52b0c467)
   - **Authors**: Bachkaniwala, R., Lanka, H., Rong, K., Gavrilovska, A.
   - **Summary**: Provides microarchitecture-level profiling revealing CPU cache misses and instruction stalls in preprocessing with <5% measurement error. Used as methodology for warmup-based preprocessing time measurement.
   - **Year**: 2024

4. **Title**: Efficient Tabular Data Preprocessing of ML Pipelines (Semantic Scholar ID: 9ae57660c4cf3f96b420cab7df0f1f008c6ea683)
   - **Authors**: Zhu, Y., Jiang, W., Alonso, G.
   - **Summary**: Achieves high throughput for tabular preprocessing using FPGA hardware accelerator. Represents alternative hardware-based approach compared to software-only solutions.
   - **Year**: 2024

5. **Title**: Optimization of TOC Task Scheduling Based on T-Type Hybrid Preemption Priority Queueing System
   - **Authors**: Liu, J., et al.
   - **Summary**: Provides mathematical framework for hierarchical preemptive priority queueing. Proves that T-Type queueing with SPT discipline minimizes mean wait time when service time variance exists, reducing wait time by factor of (1 + CV²)/2 when CV > 0.
   - **Year**: 2020

6. **Title**: Joint Optimization of Container Resource Defragmentation and Task Scheduling in Queueing Cloud Computing: A DRL-Based Approach
   - **Authors**: Guo, Y., et al.
   - **Summary**: Demonstrates that online adaptive optimization of queueing parameters can improve resource utilization using Deep Reinforcement Learning. Inspired initial DRL adaptation idea, later simplified to rule-based approach in this work.
   - **Year**: 2025

7. **Title**: DYNAMIX: RL-based Adaptive Batch Size Optimization in Distributed Machine Learning Systems
   - **Authors**: Dai, Y., He, K., Wang, A.
   - **Summary**: Shows that RL-based optimization can learn in 100-1000 training steps, validating that adaptive systems can converge quickly enough for ML training context.
   - **Year**: 2025

8. **Title**: Spindle: Efficient Distributed Training of Multi-Task Large Models via Wavefront Scheduling
   - **Authors**: Wang, Y., et al.
   - **Summary**: Achieves 71% speedup using wavefront scheduling (rule-based priority) without DRL, justifying decision to simplify from DRL to rule-based adaptation for comparable gains with lower complexity.
   - **Year**: 2024

9. **Title**: PyTorch DataLoader
   - **Authors**: Not specified
   - **Summary**: Default PyTorch data loading tool serving as baseline with 46% GPU utilization. Lacks preprocessing-aware scheduling and uses only passive prefetching.
   - **Year**: Not specified

10. **Title**: NVIDIA DALI
    - **Authors**: Not specified
    - **Summary**: GPU-accelerated preprocessing library for operations like resize, normalize, and augment. Requires dedicated GPU (competing with training for compute) and has limited operation support.
    - **Year**: 2023

11. **Title**: PyTorch AMP (Automatic Mixed Precision)
    - **Authors**: Not specified
    - **Summary**: Production standard for rule-based adaptive system using simple conditional rules (if overflow: scale /= 2, else: scale *= 1.01) for loss scaling. Provides template pattern for rule-based threshold adaptation.
    - **Year**: Not specified

12. **Title**: HuggingFace Diffusers Training Scripts (Page ID: 7dc7759b-8463-4b4e-bffb-86f8a1e28969)
    - **Authors**: Not specified
    - **Summary**: Demonstrates drop-in API design pattern with minimal code changes for production features (e.g., accelerator.prepare() wraps model/optimizer). Inspired AdaptiveDataLoader drop-in API design.
    - **Year**: Not specified

**Key Challenges**

1. **Preprocessing Time Heterogeneity**: Heterogeneous preprocessing time distributions (high CV > 0.2) cause GPU starvation in default data loaders, reducing GPU utilization to ~46% and creating training bottlenecks.

2. **Static Priority Limitations**: Existing priority-based approaches (MinatoLoader) use fixed P25/P75 thresholds that cannot adapt to non-stationary preprocessing patterns during training.

3. **Lack of Fairness Mechanisms**: Priority scheduling without starvation prevention can cause slow samples to be indefinitely delayed, leading to dataset imbalance and poor model convergence.

4. **Production Readiness Gap**: Research prototypes lack automatic adaptation, homogeneity detection, and drop-in API compatibility, requiring manual tuning that negates their practical value for resource-constrained teams.

5. **Hardware Requirements**: Alternative approaches (NVIDIA DALI, Piper) require specialized hardware (dedicated GPU for DALI, FPGA for Piper) that is not accessible to all teams.

6. **Missing Theoretical Foundation**: Prior work on ML data loading optimization lacks rigorous mathematical frameworks (queueing theory formalization), relying on empirical trial-and-error rather than principled design.

7. **Single-GPU Limitation**: Existing priority-based data loaders (MinatoLoader, SpeedyLoader) only support single-GPU training, lacking distributed training extensions for multi-GPU setups.

8. **Homogeneity Detection Absence**: Systems lack safety mechanisms to prevent performance degradation on uniform datasets where priority scheduling provides no benefit.

9. **Recalibration Strategy Gap**: No established methodology exists for online queue boundary recalibration frequency and adaptation rules for non-stationary preprocessing patterns.

10. **Efficiency-Fairness Trade-off**: Unresolved tension between maximizing throughput (prioritizing fast samples) and ensuring fairness (preventing slow sample starvation) in ML training context.
