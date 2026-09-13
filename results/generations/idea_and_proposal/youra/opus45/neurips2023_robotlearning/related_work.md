## Related Work

**Related Papers**
1. **Title**: OpenVLA: An Open-Source Vision-Language-Action Model (arXiv:2406.09246)
   - **Authors**: Kim et al.
   - **Summary**: Presents a 7B parameter VLA with LoRA support that achieves 16.5% better performance than RT-2-X (55B), providing an efficient backbone architecture for VLA fine-tuning approaches.
   - **Year**: 2024

2. **Title**: GCBF+: A Neural Graph Control Barrier Function Framework (arXiv:2401.14554)
   - **Authors**: Zhang et al.
   - **Summary**: Introduces a neural CBF parameterization approach that achieves 20% improvement in safety performance, validating the effectiveness of differentiable safety methods.
   - **Year**: 2024

3. **Title**: Fine-Tuning VLAs: Optimizing Speed and Success (OpenVLA-OFT) (arXiv:2502.19645)
   - **Authors**: Kim et al.
   - **Summary**: Proposes an optimized fine-tuning recipe that improves LIBERO benchmark success rates from 76.5% to 97.1%, establishing a strong fine-tuning baseline for VLA models.
   - **Year**: 2025

4. **Title**: VLSA: Vision-Language-Safety-Action
   - **Authors**: Not specified
   - **Summary**: Integrates runtime CBF for VLA safety, achieving 59.16% improvement in obstacle avoidance through runtime safety monitoring.
   - **Year**: 2025

5. **Title**: SafeVLA
   - **Authors**: Not specified
   - **Summary**: Implements a runtime safety shield approach for VLA systems, representing an alternative paradigm of runtime versus training-time safety integration.
   - **Year**: 2025

6. **Title**: safe-control-gym
   - **Authors**: Yuan
   - **Summary**: Provides a benchmark for safe reinforcement learning with constraint satisfaction metrics, enabling standardized evaluation of safety-aware control methods.
   - **Year**: 2022

7. **Title**: SafeMindBench
   - **Authors**: Chen et al.
   - **Summary**: Introduces an embodied agent safety benchmark comprising 5,558 samples, demonstrating that leading LLMs and VLAs remain susceptible to safety failures.
   - **Year**: 2025

**Key Challenges**
1. **Runtime Overhead in Safety Integration**: Current approaches like VLSA and SafeVLA rely on runtime safety mechanisms, introducing computational overhead during deployment that may limit real-time performance.

2. **Disconnect Between Safe RL and VLA Fine-tuning**: Existing safe reinforcement learning methods have not been integrated with VLA fine-tuning pipelines, leaving a gap in training-time safety incorporation.

3. **VLA Safety Vulnerabilities**: Leading LLMs and VLAs remain susceptible to safety failures as demonstrated by SafeMindBench, indicating insufficient safety guarantees in current foundation models.

4. **Training-time vs Runtime Safety Trade-offs**: The field lacks methods that achieve comparable safety levels to runtime approaches while eliminating runtime computational costs through training-time integration.
