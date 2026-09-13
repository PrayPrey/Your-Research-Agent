## Related Work

**Related Papers**
1. **Title**: Cerebellar circuit computations for predictive motor control
   - **Authors**: Nguyen, K.P. & Person, A.L.
   - **Summary**: Demonstrates that the cerebellum implements motor control through mechanisms resembling internal models but involving model-free implicit mappings of high-dimensional sensorimotor contexts to motor output, providing theoretical foundation for cerebellar-inspired predictive architectures.
   - **Year**: 2025

2. **Title**: OpenVLA: An Open-Source Vision-Language-Action Model (arXiv:2406.09246)
   - **Authors**: Kim, M.J. et al.
   - **Summary**: Presents a 7B-parameter open-source vision-language-action model achieving state-of-the-art manipulation performance, serving as a target VLA for integration with predictive control systems.
   - **Year**: 2024

3. **Title**: π0.5: a Vision-Language-Action Model with Open-World Generalization (arXiv:2504.16054)
   - **Authors**: Physical Intelligence
   - **Summary**: Demonstrates VLA generalization across diverse manipulation tasks, validating the importance of VLA semantic understanding for open-world robotic applications.
   - **Year**: 2025

4. **Title**: Corki: Enabling Real-time Embodied AI Robots via Algorithm-Architecture Co-Design
   - **Authors**: Huang et al.
   - **Summary**: Achieves 5.9× speedup via trajectory prediction through algorithm-architecture co-design, serving as a baseline for latency comparison in embodied AI systems.
   - **Year**: 2024

5. **Title**: TIC-VLA: Latency-Aware Vision-Language-Action Models
   - **Authors**: Not specified
   - **Summary**: Addresses latency challenges for VLA models in the navigation domain, representing domain-specific approaches to real-time embodied AI.
   - **Year**: 2026

6. **Title**: ReAct Agent Pattern
   - **Authors**: Not specified
   - **Summary**: Establishes planning-memory-tool decoupling patterns applicable to embodied agent control loops, supporting deliberative-reactive separation in robotic architectures.
   - **Year**: Not specified

7. **Title**: Neural Associative Skill Memories
   - **Authors**: Not specified
   - **Summary**: Introduces self-supervised predictive coding for temporal prediction in robotics, validating the transfer of predictive coding principles to robotic control applications.
   - **Year**: 2025

**Key Challenges**
1. **VLA Inference Latency**: Current vision-language-action models suffer from high inference latency that limits their applicability to real-time robotic manipulation tasks requiring fast reactive control.

2. **Domain-Specific Solutions**: Existing latency-aware approaches like TIC-VLA target navigation rather than manipulation, leaving a gap in solutions specifically designed for manipulation tasks.

3. **Deliberative-Reactive Integration**: Bridging the gap between high-level semantic understanding from VLAs and low-level reactive motor control remains challenging, requiring effective decoupling of planning and execution.

4. **Biologically-Inspired Transfer**: Translating neuroscience insights about cerebellar predictive control mechanisms into practical robotic architectures that can leverage model-free implicit mappings for motor output.

5. **Temporal Prediction in Robotics**: Implementing effective predictive coding for temporal prediction in robotic systems while maintaining real-time performance constraints.
