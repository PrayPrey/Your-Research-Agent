## Related Work

**Related Papers**

1. **Title**: IGL (Interaction-Grounded Learning) (NeurIPS 2022)
   - **Authors**: Not specified
   - **Summary**: Foundational IGL paradigm where agents learn reward decoder ψ(y) mapping arbitrary feedback signals to latent rewards without pre-specified reward functions, enabling learning from implicit human feedback.
   - **Year**: 2022

2. **Title**: IGL-P (ICLR 2023)
   - **Authors**: Not specified
   - **Summary**: Extension of IGL framework with policy identifiability assumptions and conditional independence constraints for reward decoder learning.
   - **Year**: 2023

3. **Title**: Multimodal Interactive Agents
   - **Authors**: Not specified
   - **Summary**: Framework for multimodal reinforcement learning from human feedback (RLHF), establishing architectural patterns for cross-modal integration in interactive agents.
   - **Year**: 2022 (37 citations)

4. **Title**: Variational Preference Learning
   - **Authors**: Not specified
   - **Summary**: Approach to learning user preferences through variational inference methods in interactive learning settings.
   - **Year**: 2024 (91 citations)

5. **Title**: RLIHF EEG
   - **Authors**: Not specified
   - **Summary**: Reinforcement learning from implicit human feedback using EEG signals as implicit feedback modality for reward learning.
   - **Year**: 2025

6. **Title**: Eye-tracking LLM
   - **Authors**: Not specified
   - **Summary**: Using eye-tracking data as implicit feedback for improving large language model interactions and preference learning.
   - **Year**: 2025

7. **Title**: Implicit Dialogue Feedback
   - **Authors**: Not specified
   - **Summary**: Methods for extracting and utilizing implicit feedback signals from dialogue interactions for conversational agent improvement.
   - **Year**: 2025

8. **Title**: Gazelle (CVPR 2025)
   - **Authors**: Not specified
   - **Summary**: Pre-trained CNN model for gaze direction prediction and feature extraction, capturing fixation duration, saccade velocity, and pupil dilation patterns.
   - **Year**: 2025 (807 GitHub stars)

9. **Title**: UniGaze
   - **Authors**: Not specified
   - **Summary**: Implementation framework for unified gaze estimation and eye-tracking applications.
   - **Year**: 2024

10. **Title**: OpenRLHF-M
    - **Authors**: Not specified
    - **Summary**: Multimodal extension of OpenRLHF framework with Bradley-Terry reward modeling for explicit multimodal human feedback.
    - **Year**: 2025

11. **Title**: OpenRLHF
    - **Authors**: Not specified
    - **Summary**: Open-source reinforcement learning from human feedback implementation framework.
    - **Year**: Not specified (7.9k GitHub stars)

12. **Title**: CLIP (Vision-Language Models)
    - **Authors**: Not specified
    - **Summary**: Vision-language model using hierarchical and attention-based architectures for multimodal understanding, demonstrating successful cross-modal integration.
    - **Year**: Not specified

13. **Title**: Flamingo (Vision-Language Models)
    - **Authors**: Not specified
    - **Summary**: Vision-language model architecture utilizing hierarchical processing and attention mechanisms for multimodal tasks.
    - **Year**: Not specified

14. **Title**: Wav2vec2
    - **Authors**: Not specified
    - **Summary**: Self-supervised speech representation learning model, used for prosody extraction including pitch contour, energy, speaking rate, and voice quality features.
    - **Year**: Not specified

15. **Title**: MediaPipe Holistic (Google)
    - **Authors**: Google
    - **Summary**: Framework for skeletal keypoint extraction from depth camera frames, providing 33 landmark tracking for gesture recognition.
    - **Year**: Not specified

**Key Challenges**

1. **Multimodal Implicit Feedback Fusion for IGL**: Existing IGL methods focus on single-modality feedback (e.g., gaze only or speech only), lacking architectures to process synchronous multimodal implicit feedback streams with heterogeneous sampling rates and modality-specific reward information.

2. **Non-Stationary Preference Learning**: Current IGL frameworks assume stationary reward functions throughout interaction, failing to adapt to evolving user preferences over time in online learning scenarios.

3. **HCI Design Principles for Interactive Learning**: Limited design patterns, ability-based feedback selection methods, transparency mechanisms, scalable deployment frameworks, and computational models of human pedagogical strategies for IGL systems.

4. **Cross-Modal Alignment**: Challenge of aligning multimodal signals with vastly different sampling rates (120Hz eye tracking, 16kHz speech audio, 30fps gesture video) to a common temporal representation without losing reward-relevant information.

5. **Modality Importance Weighting**: Need for context-dependent mechanisms to weight modality contributions based on task type (visual tasks should prioritize eye gaze, dialogue tasks should prioritize speech prosody).

6. **Conflicting Multimodal Signals**: Handling ambiguity when different modalities provide contradictory reward information, requiring uncertainty quantification to identify low-confidence predictions.

7. **Temporal Information Loss**: Risk of losing reward-critical temporal patterns when downsampling high-frequency signals (fast eye saccades, speech intonation changes) to common timebase through fixed pooling methods.

8. **Spurious Correlation Learning**: Attention mechanisms may learn to weight modalities based on noise patterns rather than true reward relevance without proper regularization.

9. **Generalization Across User Populations**: Results from homogeneous participant pools (e.g., university students) may not generalize to diverse age groups, abilities, and demographic backgrounds.

10. **Computational Efficiency**: Real-time processing requirements for multiple encoders and attention mechanisms may create latency issues (>100ms inference time) for deployment on edge devices in assistive robotics applications.

11. **IGL Identifiability in Multimodal Settings**: Extending theoretical identifiability guarantees (conditional independence, policy identifiability, low random-action rewards) from single-modality IGL to multimodal cases where cross-modal attention may violate conditional independence assumptions.
