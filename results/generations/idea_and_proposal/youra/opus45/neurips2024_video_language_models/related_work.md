## Related Work

**Related Papers**
1. **Title**: T3: Transferable Tactile Transformers
   - **Authors**: Zhao et al.
   - **Summary**: Primary baseline for cross-sensor tactile transfer that uses a shared trunk architecture for learning transferable representations across different tactile sensors.
   - **Year**: 2024 (CoRL)

2. **Title**: AnyTouch
   - **Authors**: Not specified
   - **Summary**: Most recent baseline for tactile representation learning that employs unified tokenization for cross-sensor generalization.
   - **Year**: 2025 (arXiv)

3. **Title**: Sparsh
   - **Authors**: Higuera et al.
   - **Summary**: Self-supervised learning baseline for tactile sensing that uses appearance-based methods including DINO and IJEPA for representation learning.
   - **Year**: 2024 (RSS)

4. **Title**: TensorTouch
   - **Authors**: Do et al.
   - **Summary**: Validates the combination of Finite Element Method (FEM) with deep learning for tactile sensing, providing methodology for physics supervision labels.
   - **Year**: 2025

5. **Title**: DigiTac
   - **Authors**: Lepora et al.
   - **Summary**: Demonstrates that physics is transferable across tactile sensors by showing that the same contact produces the same pose, establishing the foundation for physics invariance.
   - **Year**: 2022

6. **Title**: Cross-Sensor Domain Adaptation
   - **Authors**: Jing & Qian
   - **Summary**: Demonstrates that disentanglement approaches work for tactile sensing by showing effective style-content separation for cross-sensor transfer.
   - **Year**: 2025

7. **Title**: VAMP
   - **Authors**: Li et al.
   - **Summary**: Introduces multimodal feature diversion architecture that can be adapted for tactile disentanglement of physics and appearance features.
   - **Year**: 2025

8. **Title**: PINN for Contact
   - **Authors**: Şahin et al.
   - **Summary**: Develops physics-informed neural network approaches for contact mechanics, providing physics-informed loss function design for contact problems.
   - **Year**: 2023

9. **Title**: DANN (Domain Adversarial Neural Networks)
   - **Authors**: Ganin et al.
   - **Summary**: Introduces domain adversarial training with gradient reversal layer, which can be applied for achieving sensor-invariance in tactile representations.
   - **Year**: 2016

10. **Title**: 3D-ViTac
    - **Authors**: Huang et al.
    - **Summary**: Proposes a 3D fusion architecture for tactile sensing, focusing on spatial representation rather than cross-sensor transfer.
    - **Year**: 2024

11. **Title**: EyeSight Hand
    - **Authors**: Romero et al.
    - **Summary**: Focuses on hardware-software co-design for tactile sensing systems rather than representation learning approaches.
    - **Year**: 2024

12. **Title**: SimTacLS
    - **Authors**: Luu et al.
    - **Summary**: Develops large-scale simulation for tactile sensing but focuses on single-sensor scenarios rather than cross-sensor generalization.
    - **Year**: 2023

**Key Challenges**
1. **Appearance-Based SSL Limitations**: Current self-supervised learning methods like DINO and IJEPA focus on appearance-based features, which may not capture the underlying physics essential for cross-sensor transfer.

2. **Cross-Sensor Generalization**: Existing approaches using shared trunks or unified tokenization do not explicitly model the physics-appearance disentanglement needed for robust transfer across different tactile sensor types.

3. **Physics-Appearance Entanglement**: Prior disentanglement work separates style from content, but tactile sensing requires specific separation of physics-invariant features from sensor-specific appearance features.

4. **Single-Sensor Focus**: Large-scale simulation efforts have concentrated on individual sensor types, limiting their applicability to multi-sensor scenarios and cross-sensor transfer learning.

5. **Lack of Physics Supervision**: Current cross-sensor methods do not leverage explicit physics supervision, missing the opportunity to learn representations grounded in contact mechanics principles.
