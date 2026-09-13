## Related Work

**Related Papers**
1. **Title**: OpenVLA (Kim et al. 2024)
   - **Authors**: Kim et al.
   - **Summary**: 7B parameter vision-language-action model with always-planning architecture that provides foundation for VLA research, but suffers from slow inference (100-200ms latency).
   - **Year**: 2024

2. **Title**: SmolVLA (Shukor et al. 2025)
   - **Authors**: Shukor et al.
   - **Summary**: Static compression approach reducing VLA to 685M parameters for efficiency, but limited capability on complex tasks due to fixed reduced model size.
   - **Year**: 2025

3. **Title**: F1 (Lv et al. 2025)
   - **Authors**: Lv et al.
   - **Summary**: Multi-scale VLA architecture that always computes all temporal scales simultaneously, providing inspiration but no computational savings due to lack of adaptive allocation.
   - **Year**: 2025

4. **Title**: UnderwaterVLA (Wang et al. 2025)
   - **Authors**: Wang et al.
   - **Summary**: Static binary dual-brain architecture for underwater robotics, demonstrates value of hierarchical approach but uses fixed two-level split without safe constraints.
   - **Year**: 2025

5. **Title**: Dual-Process Theory (Evans & Stanovich 2013)
   - **Authors**: Evans & Stanovich
   - **Summary**: Cognitive science framework distinguishing System 1 (fast, automatic) and System 2 (slow, deliberate) thinking processes, providing theoretical foundation for adaptive computation allocation.
   - **Year**: 2013

6. **Title**: Motor Control Hierarchies (Grafton & Hamilton 2010)
   - **Authors**: Grafton & Hamilton
   - **Summary**: Biological motor control research demonstrating multi-timescale hierarchical organization from spinal reflexes to task planning, providing inspiration for temporal abstraction levels.
   - **Year**: 2010

7. **Title**: FeudalNets (Vezhnevets 2017)
   - **Authors**: Vezhnevets et al.
   - **Summary**: Manager-worker hierarchical reinforcement learning architecture demonstrating multi-timescale control, adapted for VLA-specific requirements with adaptive activation and safe constraints.
   - **Year**: 2017

8. **Title**: k-NN OOD Detection (Hendrycks 2019)
   - **Authors**: Hendrycks et al.
   - **Summary**: Fast out-of-distribution detection using k-nearest neighbors in embedding space, demonstrating effectiveness for novelty detection with minimal computational overhead.
   - **Year**: 2019

9. **Title**: Elastic Weight Consolidation (EWC) (Kirkpatrick 2017, PNAS)
   - **Authors**: Kirkpatrick et al.
   - **Summary**: Continual learning method using Fisher Information Matrix to prevent catastrophic forgetting by protecting important weights during sequential task training.
   - **Year**: 2017

10. **Title**: VLA Survey (Ma et al. 2024)
    - **Authors**: Ma et al.
    - **Summary**: Comprehensive survey of vision-language-action models identifying critical gap in bridging high-level planning and low-level control, which AHTA directly addresses.
    - **Year**: 2024

11. **Title**: CALVIN Benchmark (Mees 2022)
    - **Authors**: Mees et al.
    - **Summary**: Standard benchmark for long-horizon language-conditioned manipulation tasks, providing evaluation protocol for multi-step robotic reasoning.
    - **Year**: 2022

12. **Title**: Control Barrier Functions (Ames et al. 2017)
    - **Authors**: Ames et al.
    - **Summary**: Formal framework for constraint satisfaction guarantees in control systems, providing theoretical foundation for safe region constraints in hierarchical architectures.
    - **Year**: 2017

**Key Challenges**
1. **Latency-Capability Trade-off**: Existing VLAs either provide fast inference with limited capability (SmolVLA 685M) or high capability with slow inference (OpenVLA 7B 100-200ms), lacking adaptive allocation between efficiency and reasoning depth.

2. **Static Computation Allocation**: Current approaches use fixed model sizes or always-compute-all-scales architectures (F1), resulting in computational waste on familiar tasks that don't require full planning capacity.

3. **Hierarchical Coherence**: Multi-level architectures (UnderwaterVLA) lack formal mechanisms to ensure reactive decisions align with strategic goals, risking task failure from constraint violations.

4. **Novelty Detection Overhead**: Reliable task familiarity assessment required for adaptive allocation must operate within sub-millisecond budget to preserve real-time performance on familiar tasks.

5. **Real-Time Safety-Critical Control**: VLA inference latencies (100-200ms) prevent deployment in domains requiring <5ms response times like autonomous vehicles or surgical robotics.

6. **Edge Deployment Constraints**: Full VLA models require cloud infrastructure or large GPUs, limiting mobile and consumer robot applications where selective computation could enable on-device inference.

7. **Continual Learning for Reactive Pathways**: Training compressed reactive models risks overfitting to specific task instances, requiring methods like EWC to maintain generalization across task variations.

8. **Bridging High-Level and Low-Level Control**: Gap identified in VLA research between abstract planning and precise action execution, requiring unified hierarchical framework with multiple temporal scales.
