## Related Work

**Related Papers**
1. **Title**: Policy-Driven World Model Adaptation for Robust Offline MBRL (arXiv:2505.13709)
   - **Authors**: Chen, Venugopal, Schneider
   - **Summary**: Introduces Stackelberg learning dynamics for joint world-policy optimization and identifies objective mismatch as the root cause of performance degradation in model-based RL.
   - **Year**: 2025

2. **Title**: Decision Transformer: RL via Sequence Modeling
   - **Authors**: Chen et al.
   - **Summary**: Demonstrates that Transformer architecture is effective for unified state-action-return modeling, reframing reinforcement learning as a sequence modeling problem.
   - **Year**: 2021

3. **Title**: Descending Predictive Feedback in Sensorimotor Systems
   - **Authors**: Li, Sarma, Doyle
   - **Summary**: Establishes that bidirectional signaling between prediction and control is necessary even for optimal control in sensorimotor systems.
   - **Year**: 2021

4. **Title**: Human Somatosensory Cortex Modulated during Motor Planning
   - **Authors**: Gale, Flanagan, Gallivan
   - **Summary**: Provides evidence for shared M1-S1 predictive representations that emerge before movement execution in human motor planning.
   - **Year**: 2021

5. **Title**: DreamerV3
   - **Authors**: Not specified
   - **Summary**: Implements separate world model and actor-critic architecture; serves as primary adaptation baseline for model-based RL approaches.
   - **Year**: Not specified

6. **Title**: TD-MPC2
   - **Authors**: Not specified
   - **Summary**: Current state-of-the-art for efficient model-based RL using implicit world models; provides comparison baseline for adaptation speed.
   - **Year**: Not specified

7. **Title**: AdaWM
   - **Authors**: Not specified
   - **Summary**: Identifies policy-model mismatch as the cause of fine-tuning degradation in world model adaptation.
   - **Year**: 2025

8. **Title**: L2M
   - **Authors**: Not specified
   - **Summary**: Demonstrates catastrophic forgetting during fine-tuning, providing motivation for shared representations in model-based approaches.
   - **Year**: 2023

**Key Challenges**
1. **Objective Mismatch**: Separate optimization of world models and policies leads to misaligned objectives, causing performance degradation in model-based RL.
2. **Policy-Model Mismatch**: Fine-tuning world models independently from policies results in degradation due to distributional mismatch between the two components.
3. **Catastrophic Forgetting**: Standard fine-tuning approaches suffer from catastrophic forgetting of previously learned knowledge, necessitating alternative architectural solutions such as shared representations.
4. **Bidirectional Information Flow**: Effective sensorimotor control requires bidirectional signaling between prediction and control modules, which is not captured by traditional separate architectures.
