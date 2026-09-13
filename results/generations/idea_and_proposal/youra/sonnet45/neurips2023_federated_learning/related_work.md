## Related Work

**Related Papers**

1. **Title**: Federated Foundation Models (Yu et al., 2023)
   - **Authors**: Yu et al.
   - **Summary**: Proposes FFM paradigm covering pre-training, fine-tuning, federated prompt tuning. Focuses on supervised fine-tuning and mentions pre-training but provides no SSL implementation.
   - **Year**: 2023
   - **Citations**: 65 cites

2. **Title**: FedFMSL (Wu et al., 2024)
   - **Authors**: Wu et al.
   - **Summary**: Two-stage federated learning with sparsely activated LoRA achieving <0.3% parameter tuning and 59% improvement. Limitation: supervised learning only, requires labeled data at each client.
   - **Year**: 2024
   - **Citations**: 19 cites

3. **Title**: FedHPL (Ma et al., 2024)
   - **Authors**: Ma et al.
   - **Summary**: Heterogeneous federated learning with prompt tuning and logit distillation achieving 230x communication reduction. Limitation: supervised learning with labels required.
   - **Year**: 2024
   - **Citations**: 3 cites

4. **Title**: SimCLR (Chen et al., 2020)
   - **Authors**: Chen et al.
   - **Summary**: Contrastive learning framework with multi-view augmentation and large negative sets. Proves multi-view data augmentation enables contrastive learning convergence in centralized settings.
   - **Year**: 2020
   - **Citations**: 5000+ cites

5. **Title**: MoCo (He et al., 2020)
   - **Authors**: He et al.
   - **Summary**: Momentum-based contrastive learning with queue for negatives. Proves InfoNCE with large negative sets learns discriminative representations in centralized settings.
   - **Year**: 2020
   - **Citations**: 3000+ cites

6. **Title**: FedPCC (2025)
   - **Authors**: Not specified
   - **Summary**: Uses K=20 prototype clusters to reduce false negatives by 23% in federated learning for supervised classification tasks.
   - **Year**: 2025

7. **Title**: FedAF (Wang et al., 2024)
   - **Authors**: Wang et al.
   - **Summary**: Aggregation-free federated learning using condensed data and soft labels. Handles heterogeneity but requires labels.
   - **Year**: 2024
   - **Citations**: 64 cites

8. **Title**: LoRA (Hu et al., 2021)
   - **Authors**: Hu et al.
   - **Summary**: Low-rank adaptation for efficient fine-tuning (r=8-32, <0.5% params). Designed for supervised tasks, enables parameter-efficient fine-tuning.
   - **Year**: 2021
   - **Citations**: 3000+ cites

9. **Title**: DePT (Shi & Lipani, 2023)
   - **Authors**: Shi & Lipani
   - **Summary**: Decomposed prompt tuning for parameter efficiency in supervised learning tasks.
   - **Year**: 2023
   - **Citations**: 41 cites

**Key Challenges**

1. **Federated Foundation Models Require Labels**: All existing federated foundation model approaches (Yu 2023, Wu 2024, Ma 2024) rely on supervised learning and require labeled data at each client, limiting applicability to unlabeled federated data scenarios.

2. **SSL Methods Not Adapted for Federated Settings**: Self-supervised learning methods like SimCLR and MoCo demonstrate success in centralized settings but lack federated adaptations that handle data heterogeneity and communication constraints.

3. **Heterogeneity Handling Requires Supervision**: Existing heterogeneity handling approaches (FedAF, FedPCC) require labeled data and do not address the challenge of false negative sampling in contrastive self-supervised learning under federated heterogeneity.

4. **PEFT Focused on Supervised Tasks**: Parameter-efficient fine-tuning methods (LoRA, DePT) are designed and validated for supervised tasks, with no existing work applying PEFT to contrastive SSL projection heads in federated settings.

5. **Communication Efficiency vs. SSL Trade-off**: While approaches like FedHPL achieve 230x communication reduction, they are limited to supervised settings. No existing work demonstrates communication-efficient self-supervised learning in federated foundation models.

6. **False Negative Problem in Federated Contrastive Learning**: Heterogeneous client data distributions create false negatives in contrastive learning (semantically similar samples from different clients treated as negatives), but no existing work provides systematic solutions using prototype-aware negative sampling.

7. **No Unified Framework**: No existing work combines federated learning, self-supervised learning, foundation models, and parameter-efficient fine-tuning in a single unified framework.

8. **Client Heterogeneity Viewed as Challenge**: Traditional federated learning views data heterogeneity as an optimization challenge (client drift, slow convergence) rather than as a potential benefit for contrastive learning's need for diverse negative samples.

9. **Convergence Uncertainty in Federated SSL**: Lack of evidence that contrastive SSL objectives (InfoNCE) can converge in federated settings with heterogeneous unlabeled data without labeled supervision signals.

10. **Privacy-Utility Trade-off in Prototype Exchange**: Prototype-based approaches may leak information about client data distributions, but formal privacy guarantees (differential privacy) for federated SSL remain unexplored.
