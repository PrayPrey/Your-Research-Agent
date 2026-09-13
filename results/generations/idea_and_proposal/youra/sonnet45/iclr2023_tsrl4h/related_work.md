## Related Work

**Related Papers**
1. **Title**: Self-Supervised Contrastive Learning for Medical Time Series: A Systematic Review (2023)
   - **Authors**: Liu, Alavi, Li, Zhang
   - **Summary**: Systematic review of 43 SSL papers providing augmentation taxonomy (temporal masking, jittering, scaling) demonstrating that augmentation strategy is critical for SSL success. Shows SSL effectively addresses limited labels but does not address fairness.
   - **Year**: 2023

2. **Title**: Self-Supervised Learning for Clinical Time Series via Robust Optimization and Adaptive Data Augmentation (2025)
   - **Authors**: Zhu, Huang, Shi
   - **Summary**: Introduces parameterized augmentor with min-max optimization emphasizing challenging samples, demonstrating that adaptive augmentation significantly outperforms fixed strategies especially with limited labeled data.
   - **Year**: 2025

3. **Title**: Advancing Equal Opportunity Fairness and Group Robustness through Group-Level Cost-Sensitive Deep Learning (2025)
   - **Authors**: Sulaiman
   - **Summary**: Group-level cost-sensitive learning achieves equal opportunity fairness (similar TPR across demographic groups) without sacrificing overall accuracy, demonstrating synergy between group robustness and fairness with ~70% fairness gap reduction.
   - **Year**: 2025

4. **Title**: COMET: Hierarchical Contrastive Framework for Medical Time Series (2023)
   - **Authors**: Not specified
   - **Summary**: Hierarchical contrastive framework for medical time series (NeurIPS 2023) representing uniform augmentation SSL without fairness considerations. Implementation available at DL4mHealth/COMET.
   - **Year**: 2023

5. **Title**: CARLA: Self-Supervised Contrastive Learning with Masking-Invariant Loss (2024)
   - **Authors**: Zamanzadeh (and collaborators)
   - **Summary**: Self-supervised contrastive learning with masking-invariant loss for missing data robustness, demonstrating SSL can handle missing values with ~10-12% robustness improvement.
   - **Year**: 2024

6. **Title**: Merlin: Multi-View Representation Learning for Robust Multivariate Time Series (2025)
   - **Authors**: Not specified
   - **Summary**: Addresses missing data via multi-view learning but does not address fairness across patient subgroups, showing SSL methods handle robustness OR fairness but not both.
   - **Year**: 2025

7. **Title**: Alifuse: Aligning and Fusing Multimodal Medical Data (2024)
   - **Authors**: Not specified
   - **Summary**: Multimodal fusion with attention interpretability but no fairness considerations, representing state-of-art in multimodal SSL without addressing subgroup equity.
   - **Year**: 2024

**Key Challenges**
1. **Limited Labels with Fairness**: Existing SSL methods (COMET, CARLA, Liu et al. 2023) use uniform augmentation across all patients, implicitly biasing toward majority subgroups, failing to address fairness in limited labeled data scenarios.

2. **Subgroup Imbalance**: No single work addresses all five challenges simultaneously (limited labels, multimodal, missing data, fairness, interpretability) - each approach addresses only 1-2 dimensions in isolation.

3. **Augmentation Strategy**: Tension between strong augmentation for maximizing SSL difficulty (40-60% masking rates as advocated by Liu et al. 2023) versus subgroup-specific weaker augmentation needed to preserve physiological characteristics (e.g., 20% masking for pediatric short-duration patterns).

4. **Missing Data with Fairness**: While CARLA demonstrates missing data robustness, it does not incorporate fairness constraints or subgroup-specific missing pattern simulation (pediatric burst missing vs elderly gradual degradation).

5. **Fairness Transfer**: No existing work demonstrates that fairness properties learned during SSL pretraining transfer to downstream tasks while maintaining missing data robustness.

6. **Physiological Heterogeneity**: Current approaches do not account for measurably distinct physiological characteristics across patient age subgroups (pediatric 80-180 bpm heart rate vs adult 60-100 bpm) in augmentation design.

7. **Multi-Objective Complexity**: Existing fairness-aware methods require complex multi-objective optimization with 15-20 hyperparameters, limiting practical deployment feasibility.
