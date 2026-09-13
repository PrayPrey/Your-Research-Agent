## Related Work

**Related Papers**
1. **Title**: Sparsh SSL: Self-supervised learning for tactile representation (Higuera 2024)
   - **Authors**: Higuera et al.
   - **Summary**: Introduces self-supervised learning approach for tactile representation learning, establishing foundation for tactile feature extraction without labeled data.
   - **Year**: 2024
   - **Citations**: 48

2. **Title**: Surformer v2: Late fusion with learnable weights for vision-tactile integration (Kansana 2025)
   - **Authors**: Kansana et al.
   - **Summary**: Proposes late fusion architecture with learnable weighting mechanisms for combining vision and tactile modalities, enabling adaptive multi-modal integration.
   - **Year**: 2025
   - **Citations**: 1

3. **Title**: STNet: Spatio-temporal attention for tactile sequences (Lu 2024)
   - **Authors**: Lu et al.
   - **Summary**: Develops spatio-temporal attention mechanisms specifically designed for processing sequential tactile data with temporal dynamics.
   - **Year**: 2024
   - **Citations**: 5

4. **Title**: Bridging vision-touch: Self-supervised multimodal learning (Li 2024)
   - **Authors**: Li et al.
   - **Summary**: Presents self-supervised approach for learning joint vision-tactile representations without requiring paired supervision.
   - **Year**: 2024
   - **Citations**: 1

5. **Title**: Look-to-Touch: Vision-enhanced tactile prediction (Dong 2025)
   - **Authors**: Dong et al.
   - **Summary**: Demonstrates that visual information can predict where tactile sensing will be most informative, enabling vision-guided touch exploration.
   - **Year**: 2025
   - **Citations**: 3

6. **Title**: Bayesian Active Recognition for tactile sensing (Zheng 2024)
   - **Authors**: Zheng et al.
   - **Summary**: Establishes Bayesian active sensing baseline for tactile object recognition using probabilistic uncertainty estimation.
   - **Year**: 2024
   - **Citations**: 0

7. **Title**: Transfer Learning from Vision to Touch (Rouhafzay 2020)
   - **Authors**: Rouhafzay et al.
   - **Summary**: Validates that tactile learning can benefit from demonstration-based transfer learning, particularly for cross-domain knowledge transfer from vision.
   - **Year**: 2020
   - **Citations**: 18

8. **Title**: Active Vision research (cross-domain)
   - **Authors**: Not specified
   - **Summary**: Provides saccadic attention analogy for active exploration, demonstrating how gaze selection mechanisms can inform tactile exploration policies.
   - **Year**: Not specified

9. **Title**: Transformer Architectures (Archon KB: a900d1a2)
   - **Authors**: Not specified
   - **Summary**: Architectural pattern for self-attention mechanisms applied to spatial and temporal modeling, transferable to tactile data processing.
   - **Year**: Not specified

10. **Title**: Attention Mechanisms (Archon KB: 82bd2ffa)
   - **Authors**: Not specified
   - **Summary**: Implementation patterns for selective information processing using attention, applicable to cross-modal fusion architectures.
   - **Year**: Not specified

11. **Title**: MagicGripper
   - **Authors**: Not specified
   - **Summary**: Baseline method for tactile object recognition, used for SOTA comparison.
   - **Year**: Not specified

**Key Challenges**
1. **Active Sensing Control Policies Gap**: Current tactile research focuses predominantly on passive perception (processing data from fixed contact points), while active sensing—where robots intelligently explore through controlled touch movements guided by real-time perception—remains critically underdeveloped, preventing deployment in unstructured environments where pre-programmed patterns fail.

2. **Cross-Modal Integration**: No existing work combines cross-modal attention, active exploration, and learned policies in a unified framework, leaving unexplored the potential of leveraging complementary information from vision (broad spatial coverage) and touch (precise contact information).

3. **Sim-to-Real Gap in Tactile Sensing**: Tactile simulators are less mature than vision or manipulation simulators, creating significant challenges for transferring policies trained in simulation to real-world robotic applications.

4. **Real-Time Computational Overhead**: Cross-modal attention architectures may violate real-time constraints (<100ms) required for closed-loop robotic control, necessitating architectural innovations like dual-speed processing.

5. **Sample Efficiency in Reinforcement Learning**: Pure RL approaches may not converge efficiently in the tactile domain due to sparse rewards and high-dimensional action spaces, requiring hybrid approaches like imitation learning combined with model-based RL.

6. **Sensor Generalization**: Tactile policies may be sensor-specific (e.g., GelSight vs. ReSkin vs. DIGIT), limiting generalization across different tactile sensor platforms without multi-sensor training strategies.

7. **Attention Collapse**: Multi-modal attention mechanisms risk collapsing to single-modality processing, failing to utilize the complementary information from vision-tactile fusion.

8. **Temporal Dynamics and Local Spatial Embedding**: Touch sensing data has unique structural properties including temporal dynamics and local spatial embedding that require specialized computational models beyond standard vision or language processing approaches.
