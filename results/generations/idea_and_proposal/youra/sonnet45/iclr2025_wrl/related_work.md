## Related Work

**Related Papers**

1. **Title**: EmbodieDreamer - PhysAligner (Wang et al. 2025)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates 29.17% improvement in task success through joint physics-policy alignment, establishing the foundation for co-optimization approaches in robot learning.
   - **Year**: 2025

2. **Title**: Differentiable sim-based system identification (Kovalev et al. 2025)
   - **Authors**: Kovalev et al.
   - **Summary**: Achieves 75% rotational error reduction through gradient-based parameter optimization in differentiable simulation, validating gradient-based approaches for learned systems.
   - **Year**: 2025

3. **Title**: DPSI - Differentiable Physics Parameter Inference for elastoplastic manipulation (Yang et al. 2024)
   - **Authors**: Yang et al.
   - **Summary**: Demonstrates single-interaction physics parameter inference for elastoplastic manipulation, showing data efficiency of differentiable simulation-based identification. Also notes elastoplastic materials as future work.
   - **Year**: 2024

4. **Title**: SPI-Active - Simulation Parameter Identification with Active Learning (Sobanbabu et al. 2025)
   - **Authors**: Sobanbabu et al.
   - **Summary**: Achieves 42-63% improvement over domain randomization through parameter identification, establishing parameter optimization's superiority over randomization approaches.
   - **Year**: 2025

5. **Title**: EquiBot - SIM(3)-equivariant diffusion for data-efficient robot learning (Yang et al. 2024)
   - **Authors**: Yang et al.
   - **Summary**: Enables learning from 5-minute demonstrations using SIM(3)-equivariant diffusion, establishing baseline for data-efficient imitation learning.
   - **Year**: 2024

6. **Title**: IntervenGen (Hoque et al. 2024)
   - **Authors**: Hoque et al.
   - **Summary**: Achieves 39× robustness improvement with only 10 human interventions through sparse intervention-based refinement methodology.
   - **Year**: 2024

7. **Title**: Surgical Manipulation Sim-to-Real Transfer (Scheikl et al. 2023)
   - **Authors**: Scheikl et al.
   - **Summary**: Achieves 50% success rate in surgical deformable object manipulation, establishing high-precision sim-to-real transfer feasibility in constrained environments.
   - **Year**: 2023

8. **Title**: TRANSIC - Online correction from human feedback for sim-to-real transfer (Jiang et al. 2024)
   - **Authors**: Jiang et al.
   - **Summary**: Implements online correction from human feedback for sim-to-real transfer, demonstrating online correction mechanisms without physics optimization.
   - **Year**: 2024

9. **Title**: Sensitivity analysis for ultra-precision machine tool error compensation (Geng et al. 2021)
   - **Authors**: Geng et al.
   - **Summary**: Establishes sensitivity-based parameter identification principle in manufacturing precision control, demonstrating that sensitivity analysis focuses calibration effort on critical factors.
   - **Year**: 2021

10. **Title**: Real-time Iterative Compensation (RIC) for precision motion control (Zhou et al. 2023)
    - **Authors**: Zhou et al.
    - **Summary**: Develops online compensation mechanism for precision motion control, establishing that online compensation achieves higher precision than offline methods in manufacturing control.
    - **Year**: 2023

11. **Title**: BeyondMimic - Compact motion formulations for agile humanoid control (Liao et al. 2025)
    - **Authors**: Liao et al.
    - **Summary**: Demonstrates compact motion formulations with latent diffusion for agile humanoid control, establishing principles of identifying critical parameters and versatile online deployment.
    - **Year**: 2025

12. **Title**: OpenVLA - 7B parameter vision-language-action model
    - **Authors**: Not specified
    - **Summary**: State-of-the-art generalist manipulation model trained on 970k episodes, representing the current paradigm of large-scale generalist approaches versus specialized precision methods.
    - **Year**: Not specified

13. **Title**: DiffTORI - Differentiable trajectory optimization for imitation learning (Wan et al. 2024)
    - **Authors**: Wan et al.
    - **Summary**: Focuses on trajectory optimization without sim-to-real transfer or precision metrics, demonstrating differentiable optimization in policy learning contexts.
    - **Year**: 2024

14. **Title**: AdaptSim - Task-driven simulation adaptation
    - **Authors**: IROM Lab
    - **Summary**: Develops adaptive simulation methods for task-driven scenarios, providing comparison point for simulation adaptation without sensitivity-based parameter selection.
    - **Year**: Not specified

15. **Title**: SimplerEnv Benchmark
    - **Authors**: Not specified
    - **Summary**: Establishes sim-to-real evaluation benchmark for general tabletop manipulation at cm-scale precision, providing standard baseline for manipulation evaluation.
    - **Year**: Not specified

**Key Challenges**

1. **Sim-to-Real Gap in Precision Tasks**: Traditional sim-to-real approaches with fixed simulation parameters struggle to achieve sub-millimeter accuracy, with existing methods achieving only cm-scale precision (SimplerEnv) or requiring constrained environments (surgical robotics at 50% success).

2. **Data Efficiency vs. Precision Trade-off**: Current methods either achieve high precision with extensive data (>50 demonstrations) or maintain data efficiency (5-10 demos) but sacrifice precision (cm-scale accuracy), lacking approaches that address both simultaneously.

3. **Unstructured Environment Limitations**: High-precision manipulation methods work primarily in constrained settings (surgical environments) and fail to generalize to unstructured household environments with clutter and variability.

4. **Parameter Selection Inefficiency**: Domain randomization approaches underperform targeted parameter identification by 42-63%, and existing physics optimization methods optimize all ~100 simulation parameters without identifying precision-critical subsets.

5. **Offline-Only Correction**: Methods relying solely on offline physics optimization or policy learning lack real-time online correction mechanisms to handle residual simulation-reality gaps during deployment.

6. **Real-time Inference Constraints**: Neural network-based correction methods must achieve <1ms inference latency to maintain control stability for sub-millimeter precision tasks, creating architectural constraints for online correction systems.

7. **Limited Cross-Domain Knowledge Transfer**: Manufacturing precision control principles (sensitivity analysis, iterative compensation) have not been systematically integrated with modern differentiable robot learning frameworks.

8. **Validation Hardware Requirements**: Sub-millimeter precision validation requires expensive specialized equipment (motion capture systems, high-frequency force-torque sensors) that may limit experimental reproducibility.

9. **Generalization Scope Uncertainty**: Unclear whether sensitivity analysis and precision-focused approaches transfer across different task categories (threading, assembly, pouring) or require task-specific recalibration.

10. **Lightweight Architecture Limitations**: Trade-off between residual network correction capacity and latency constraints (<100K parameters, <1ms) may be insufficient for very large sim-to-real gaps (>50% performance delta).
