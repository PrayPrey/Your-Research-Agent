## Related Work

**Related Papers**
1. **Title**: Diffusion Policy: Visuomotor Policy Learning via Action Diffusion (arXiv:2303.04137)
   - **Authors**: Chi, Feng, Du, Xu, Cousineau, Burchfiel, Song
   - **Summary**: Establishes diffusion models for visuomotor policy learning, achieving 46.9% improvement over prior methods. The work explicitly notes no safety mechanism is included and that multimodal distributions can include unsafe actions.
   - **Year**: 2023

2. **Title**: CoBL-Diffusion: Diffusion-Based Conditional Robot Planning Using CBF and Lyapunov Functions (arXiv:2406.05309)
   - **Authors**: Mizuta & Leung
   - **Summary**: First work to combine Control Barrier Functions (CBF) with diffusion models, applying safety constraints at inference time for robot planning.
   - **Year**: 2024

3. **Title**: Model-Free Safe RL Through Neural Barrier Certificate
   - **Authors**: Yang et al.
   - **Summary**: Demonstrates that differentiable neural CBFs can achieve near-zero safety violations, providing a mechanism for learning-based barrier certificates in reinforcement learning.
   - **Year**: 2023

4. **Title**: Augmented Proximal Policy Optimization for Safe RL
   - **Authors**: Dai, Ji, Yang, Zheng, Pan
   - **Summary**: Proposes an augmented Lagrangian approach that achieves stable convergence in constrained reinforcement learning, providing a mechanism for balancing safety constraints with performance objectives.
   - **Year**: 2023

5. **Title**: SRL-VIC
   - **Authors**: Not specified
   - **Summary**: Implements post-hoc safety filtering with variable impedance control, demonstrating the limitations of post-hoc approaches to safety in robot learning.
   - **Year**: Not specified

**Key Challenges**
1. **No Unified Safety-Performance Optimization**: Current diffusion-based policies lack a unified framework for jointly optimizing safety and task performance during training.
2. **Inference-Time Safety Limitations**: Existing approaches like CoBL-Diffusion apply safety constraints only at inference time, missing opportunities for safety-aware policy learning during training.
3. **Unsafe Multimodal Distributions**: Diffusion policies can generate multimodal action distributions that include unsafe actions, with no inherent mechanism to filter or prevent dangerous behaviors.
4. **Post-Hoc Safety Filtering Drawbacks**: Post-hoc approaches to safety filtering show limitations in effectively ensuring safe behavior while maintaining task performance.
