## Related Work

**Related Papers**

1. **Title**: What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision? (NeurIPS 2017)
   - **Authors**: Kendall, A., & Gal, Y.
   - **Summary**: Introduced aleatoric (data) and epistemic (model) uncertainty for multi-task learning in computer vision, demonstrating how to model task-dependent uncertainty heteroscedasticity.
   - **Year**: 2017

2. **Title**: A theory of cortical responses (Philosophical Transactions of the Royal Society B)
   - **Authors**: Friston, K.
   - **Summary**: Foundational neuroscience work on predictive processing showing how the brain propagates uncertainty hierarchically through cortical layers.
   - **Year**: 2005

3. **Title**: GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks (ICML)
   - **Authors**: Chen, Z., et al.
   - **Summary**: Proposed adaptive task weighting method to balance gradient magnitudes in multi-task learning through gradient normalization.
   - **Year**: 2018

4. **Title**: BEVFormer: Learning Bird's-Eye-View Representation from Multi-Camera Images via Spatiotemporal Transformers (ECCV)
   - **Authors**: Li, Z., et al.
   - **Summary**: Introduced spatiotemporal transformer architecture for BEV perception using spatial cross-attention and temporal self-attention, achieving SOTA performance on nuScenes.
   - **Year**: 2022

5. **Title**: OccFormer: Dual-path Transformer for Vision-based 3D Semantic Occupancy Prediction (ICCV)
   - **Authors**: Zhang, Y., et al.
   - **Summary**: Proposed dual-path transformer (local and global) for 3D occupancy prediction from multi-camera images.
   - **Year**: 2023

6. **Title**: ST-P3: End-to-end Vision-based Autonomous Driving via Spatial-Temporal Feature Learning (ECCV)
   - **Authors**: Hu, S., et al.
   - **Summary**: Demonstrated benefits of joint perception-prediction-planning optimization through spatial-temporal BEV feature learning.
   - **Year**: 2022

7. **Title**: Planning-oriented Autonomous Driving (CVPR Best Paper)
   - **Authors**: Hu, Y., et al.
   - **Summary**: UniAD - Query-based unified architecture integrating detection, tracking, prediction, and planning in single model achieving 48.5% NDS on nuScenes.
   - **Year**: 2023

8. **Title**: VAD: Vectorized Scene Representation for Efficient Autonomous Driving (ICLR)
   - **Authors**: Bo, J., et al.
   - **Summary**: Proposed vectorized scene representation as alternative to raster BEV for efficient P3 integration achieving 50.2% NDS on nuScenes.
   - **Year**: 2024

9. **Title**: EgoFSD: Fusion Scene Descriptor for Autonomous Driving with Uncertainty (arXiv)
   - **Authors**: Liu, Y., et al.
   - **Summary**: Introduced uncertainty-aware scene fusion for post-hoc refinement of autonomous driving predictions.
   - **Year**: 2024

10. **Title**: On Calibration of Modern Neural Networks (ICML)
    - **Authors**: Guo, C., et al.
    - **Summary**: Established temperature scaling and Expected Calibration Error (ECE) as standard methods for neural network uncertainty calibration.
    - **Year**: 2017

11. **Title**: Gradient Surgery for Multi-Task Learning (NeurIPS)
    - **Authors**: Yu, T., et al.
    - **Summary**: PCGrad - Projects conflicting gradients to Pareto-optimal directions for improved multi-task learning performance.
    - **Year**: 2020

12. **Title**: Multi-task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics (CVPR)
    - **Authors**: Cipolla, R., Gal, Y., & Kendall, A.
    - **Summary**: Introduced homoscedastic uncertainty for task weighting by learning single uncertainty parameter per task for loss balancing.
    - **Year**: 2018

13. **Title**: SparseDrive: End-to-End Autonomous Driving via Sparse Scene Representation (arXiv)
    - **Authors**: Tang, H., et al.
    - **Summary**: Proposed sparse representation approach for computational efficiency in end-to-end autonomous driving.
    - **Year**: 2024

14. **Title**: ALN-P3: Unified Language Alignment for Perception, Prediction, and Planning in Autonomous Driving (arXiv)
    - **Authors**: Ma, Y., et al.
    - **Summary**: Introduced cross-modal vision-language alignment for interpretable P3 integration using language models.
    - **Year**: 2025

15. **Title**: UniDrive-WM: Unified Understanding, Planning and Generation World Model For Autonomous Driving (arXiv)
    - **Authors**: Xiong, Z., et al.
    - **Summary**: VLM-based world model for full P3 stack with future scene generation, achieving 5.9% L2 improvement and 9.2% collision reduction.
    - **Year**: 2026

16. **Title**: PnPNet (Referenced work)
    - **Authors**: Not specified
    - **Summary**: Sequential modular pipeline for perception-prediction-planning integration in autonomous driving.
    - **Year**: 2020

17. **Title**: TPVFormer (GitHub repository)
    - **Authors**: Not specified
    - **Summary**: Tri-perspective view representation for 3D scene understanding in autonomous driving.
    - **Year**: 2023

18. **Title**: HiP-AD (Referenced as 2024 work)
    - **Authors**: Not specified
    - **Summary**: Hierarchical perception architecture for autonomous driving without uncertainty encoding.
    - **Year**: 2024

19. **Title**: ColaVLA (Referenced as 2025 work)
    - **Authors**: Not specified
    - **Summary**: Vision-Language Model (VLM) approach for P3 integration in autonomous driving using discrete reasoning.
    - **Year**: 2025

20. **Title**: WorldRFT (Referenced as 2025 work)
    - **Authors**: Not specified
    - **Summary**: Reconstruction-based world model for autonomous driving scene understanding.
    - **Year**: 2025

**Key Challenges**

1. **Information Loss in Sequential Pipelines**: Current modular approaches (PnPNet) use sequential perception-prediction-planning architectures that lead to information loss between stages and suboptimal performance.

2. **Lack of Unified Representation**: Existing methods (ST-P3, UniAD) provide only partial integration with uniform task weighting, lacking systematic framework for multi-task representation learning with uncertainty-aware routing.

3. **Gradient Conflicts in Multi-Task Learning**: Multi-task learning suffers from gradient conflicts when tasks have opposing update directions (e.g., perception wants sharper features, planning wants smoother trajectories), leading to negative transfer.

4. **Missing Uncertainty Quantification in SOTA**: Current SOTA methods (UniAD, VAD, BEVFormer) lack uncertainty quantification necessary for safety-critical autonomous driving decisions.

5. **Post-Hoc vs Structural Uncertainty**: Existing uncertainty approaches (EgoFSD) add uncertainty post-hoc for refinement rather than encoding it as core representation structure.

6. **Computational Overhead vs Performance Trade-off**: Hierarchical and uncertainty-aware approaches risk prohibitive computational costs that limit real-time deployment on edge devices.

7. **Uncertainty Calibration Challenges**: Neural networks often produce poorly calibrated uncertainty estimates (overconfident or underconfident), which can corrupt gradient routing and degrade performance.

8. **Task Weighting in Joint P3 Optimization**: Uniform task weighting in existing joint P3 methods fails to account for task-specific confidence and abstraction levels, limiting optimization benefits.

9. **Hierarchy Design for Multi-Task Systems**: Determining optimal hierarchy depth and level alignment with task structure (e.g., voxel/object/scene) remains an open architectural design challenge.

10. **Generalization Across Driving Scenarios**: Benchmark datasets (nuScenes) represent specific scenarios (urban, daytime) with uncertain generalization to diverse real-world conditions (rural, nighttime, different geographies).

11. **Interpretability for Safety-Critical Systems**: Autonomous driving systems require interpretable confidence estimates for risk-aware decision making and human oversight, which flat representations cannot provide.

12. **Dataset and Benchmark Limitations**: Current benchmarks focus on perception accuracy without comprehensive evaluation of uncertainty quality, calibration, or safety-oriented metrics.
