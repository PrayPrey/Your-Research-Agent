## Related Work

**Related Papers**
1. **Title**: How Bad is Training on Synthetic Data? A Statistical Analysis of Language Model Collapse (Semantic Scholar ID: 1f71820a)
   - **Authors**: Seddik et al.
   - **Summary**: Proves that model collapse is inevitable when training with pure synthetic data and establishes theoretical bounds on the maximal synthetic ratio that can be safely used.
   - **Year**: 2024

2. **Title**: Collapse or Thrive? Perils and Promises of Synthetic Data in a Self-Generating World (Semantic Scholar ID: 4b510679)
   - **Authors**: Kazdan et al.
   - **Summary**: Demonstrates that accumulation workflow prevents model collapse and shows that both the synthetic-to-real ratio and the training workflow significantly impact outcomes.
   - **Year**: 2024

3. **Title**: Diffusion Curriculum (DisCL): Synthetic-to-Real Data Curriculum via Image-Guided Diffusion (arXiv:2410.13674)
   - **Authors**: Liang, Bhardwaj, Zhou
   - **Summary**: Proposes a static curriculum approach for synthetic-to-real data transition, achieving +4.02% accuracy on ImageNet-LT and +2.7% OOD improvement on iWildCam.
   - **Year**: 2025 (ICCV)

4. **Title**: Data Mixing Laws: Optimizing Data Mixtures by Predicting Language Modeling Performance (arXiv:2403.16952)
   - **Authors**: Ye et al.
   - **Summary**: Demonstrates that mixing ratios for training data are predictable via scaling laws and proposes offline optimization methods for data mixture selection.
   - **Year**: 2024

5. **Title**: AutoMixAlign: Adaptive Data Mixing for Multi-Task Preference Optimization
   - **Authors**: Not specified
   - **Summary**: Applies EXP3 bandit algorithms for adaptive mixing in multi-task RLHF settings, focusing on preference optimization across multiple tasks.
   - **Year**: 2025 (ACL)

6. **Title**: A Theoretical Perspective: How to Prevent Model Collapse in Self-consuming Training Loops (Semantic Scholar ID: 36262f5e)
   - **Authors**: Fu et al.
   - **Summary**: Provides the first generalization analysis examining how both architecture and data proportion jointly affect model collapse in self-consuming training scenarios.
   - **Year**: 2025

7. **Title**: RL on Incorrect Synthetic Data Scales the Efficiency of LLM Math Reasoning by Eight-Fold (Semantic Scholar ID: 490f8721)
   - **Authors**: Setlur et al.
   - **Summary**: Shows that the method of synthetic data utilization significantly impacts outcomes, demonstrating 8× efficiency gains by applying reinforcement learning on negative synthetic examples.
   - **Year**: 2024

8. **Title**: Ecological Succession Theory (as applied to ML)
   - **Authors**: Zhu et al.; Lei et al.
   - **Summary**: Establishes that community composition adapts to environmental feedback through stochastic drift governing transitions, providing conceptual inspiration for adaptive training dynamics.
   - **Year**: 2024; 2025

**Key Challenges**
1. **Inevitable Model Collapse with Pure Synthetic Data**: Training exclusively on synthetic data leads to model collapse, with theoretical bounds limiting the maximum safe synthetic ratio.

2. **Static vs. Adaptive Data Mixing**: Existing approaches rely on offline optimization or static curricula for data mixing, failing to adapt ratios dynamically during training based on model state.

3. **Workflow Dependency**: The effectiveness of synthetic data depends not only on the ratio but also on how it is integrated into the training workflow, requiring more sophisticated usage strategies.

4. **Lack of Runtime Adaptation**: Current data mixing laws optimize ratios offline and cannot respond to changing training dynamics, leaving potential performance gains unrealized.

5. **Domain-Specific Solutions**: Existing adaptive mixing approaches focus on specific settings (e.g., multi-task RLHF) rather than providing general-purpose solutions for synthetic-real data integration.
