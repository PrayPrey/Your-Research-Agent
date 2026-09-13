## Related Work

**Related Papers**
1. **Title**: SurroundOcc: Multi-Camera 3D Occupancy Prediction for Autonomous Driving
   - **Authors**: Wei et al.
   - **Summary**: Proposes spatial 2D-3D attention mechanism to lift multi-camera features to 3D volume space, achieving 20.59% mIoU on occupancy prediction tasks.
   - **Year**: 2023

2. **Title**: Occ3D: A Large-Scale 3D Occupancy Prediction Benchmark for Autonomous Driving
   - **Authors**: Tian et al.
   - **Summary**: Introduces dense, visibility-aware occupancy labels and the CTF-Occ baseline for 3D occupancy prediction evaluation.
   - **Year**: 2023

3. **Title**: DiffVLA: Vision-Language Guided Diffusion Planning for Autonomous Driving
   - **Authors**: Jiang et al.
   - **Summary**: Presents sparse diffusion representation for efficient multi-modal driving and demonstrates the viability of differentiable planning approaches.
   - **Year**: 2025

4. **Title**: Integrating Decision-Making Into Differentiable Optimization Guided Learning
   - **Authors**: Liu et al.
   - **Summary**: Develops differentiable nonlinear optimization techniques enabling end-to-end trainable planning systems.
   - **Year**: 2024

5. **Title**: UniAD: Planning-oriented Autonomous Driving
   - **Authors**: Hu et al.
   - **Summary**: Proposes a unified perception, prediction, and planning approach achieving 1.65m L2 error at 3s horizon and 0.53% collision rate.
   - **Year**: 2023

6. **Title**: VAD: Vectorized Scene Representation for Efficient Autonomous Driving
   - **Authors**: Jiang et al.
   - **Summary**: Introduces vectorized scene representation achieving state-of-the-art planning performance with 1.05m L2 error at 3s horizon and 0.22% collision rate.
   - **Year**: 2023

7. **Title**: Joint Perception and Prediction for Autonomous Driving: A Survey
   - **Authors**: Dal'Col et al.
   - **Summary**: Surveys joint perception and prediction methods, identifying that while these components have been integrated, planning typically remains as a separate module.
   - **Year**: 2024

8. **Title**: TBP-Former: Learning Temporal Bird's-Eye-View Pyramid for Joint Perception and Prediction
   - **Authors**: Fang et al.
   - **Summary**: Proposes temporal BEV pyramid architecture achieving joint perception-prediction but relies on separate planning modules.
   - **Year**: 2023

**Key Challenges**
1. **Separation of Planning from Perception-Prediction**: Existing joint perception and prediction systems still treat planning as a separate downstream module, preventing true end-to-end optimization across all three components.

2. **Lack of Differentiable Planning Integration**: Current autonomous driving architectures do not fully leverage differentiable planning layers that would enable gradient flow from planning objectives back through perception and prediction modules.

3. **Unified P3 Architecture Gap**: While unified approaches like UniAD exist, there remains an opportunity to improve upon current state-of-the-art planning metrics achieved by methods like VAD through tighter integration of all three components.
