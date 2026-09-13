## Related Work

**Related Papers**

1. **Title**: A Simple Framework for Contrastive Learning of Visual Representations (SimCLR) (Chen et al., 2020)
   - **Authors**: Chen et al.
   - **Summary**: Introduced a simple contrastive learning framework that identifies augmentation composition as critical for SSL success. Achieved 22,633 citations and serves as primary baseline for SSL methods.
   - **Year**: 2020

2. **Title**: Improved Baselines with Momentum Contrastive Learning (MoCo v2) (Chen & He, 2020)
   - **Authors**: Chen & He
   - **Summary**: Alternative contrastive learning approach using momentum encoder and memory bank efficiency. Demonstrates that architectural improvements (MLP projection head) significantly impact SSL performance.
   - **Year**: 2020

3. **Title**: Supervised Contrastive Learning (Khosla et al., 2020)
   - **Authors**: Khosla et al.
   - **Summary**: Bridges SSL and supervised learning by incorporating label information into contrastive loss. Shows that multi-positive contrastive learning improves over standard contrastive approaches.
   - **Year**: 2020

4. **Title**: Masked Autoencoders Are Scalable Vision Learners (MAE) (He et al., 2022)
   - **Authors**: He et al.
   - **Summary**: Alternative SSL paradigm using masked image modeling (BERT for vision). Achieves strong results with generative objective using high masking ratios (75%).
   - **Year**: 2022

5. **Title**: Curriculum Learning (Bengio et al., 2009)
   - **Authors**: Bengio et al.
   - **Summary**: Foundational curriculum learning paper for supervised deep learning. Shows that training on progressively harder examples improves convergence and generalization in supervised settings.
   - **Year**: 2009

6. **Title**: On The Power of Curriculum Learning in Training Deep Networks (Hacohen & Weinshall, 2019)
   - **Authors**: Hacohen & Weinshall
   - **Summary**: Theoretical analysis of curriculum learning effectiveness in deep learning. Demonstrates that curriculum reduces training variance.
   - **Year**: 2019

7. **Title**: Curriculum Learning: A Survey (Soviany et al., 2022)
   - **Authors**: Soviany et al.
   - **Summary**: Comprehensive survey of curriculum learning across domains (supervised, RL, NLP). Identifies curriculum for SSL as under-explored research area.
   - **Year**: 2022

8. **Title**: To Compress or Not to Compress—Self-Supervised Learning and Information Theory: A Review (Shwartz-Ziv & LeCun, 2023)
   - **Authors**: Shwartz-Ziv & LeCun
   - **Summary**: Proposes information bottleneck principle for understanding SSL: encode task-relevant information while compressing nuisance variance. Provides theoretical foundation for task difficulty formalization.
   - **Year**: 2023

9. **Title**: The Information Bottleneck Method (Tishby et al., 1999)
   - **Authors**: Tishby et al.
   - **Summary**: Original information bottleneck principle paper providing mathematical framework for information compression and maximization. Foundational information theory work.
   - **Year**: 1999

10. **Title**: An Augmentation-Aware Theory for Self-Supervised Contrastive Learning (Cui et al., 2025)
    - **Authors**: Cui et al.
    - **Summary**: Recent theoretical work proving that augmentation strength affects error bounds: stronger augmentation yields tighter bounds up to an inflection point. Provides theoretical validation for dynamic augmentation adjustment.
    - **Year**: 2025

11. **Title**: An Empirically Grounded Identifiability Theory Will Accelerate Self-Supervised Learning Research (Reizinger et al., 2025)
    - **Authors**: Reizinger et al.
    - **Summary**: Proposes Singular Identifiability Theory (SITh) to bridge SSL theory-practice gap. Emphasizes finite sample effects and training dynamics over asymptotic guarantees.
    - **Year**: 2025

12. **Title**: Cognitive Load During Problem Solving: Effects on Learning (Sweller, 1988)
    - **Authors**: Sweller
    - **Summary**: Foundational cognitive load theory paper defining intrinsic load (task complexity), extraneous load (poor design), and germane load (beneficial difficulty). Establishes principles for matching task difficulty to learner capacity.
    - **Year**: 1988

13. **Title**: Re-examining cognitive load measures in real-world learning (Liu & Zhang, 2024)
    - **Authors**: Liu & Zhang
    - **Summary**: Modern cognitive load research demonstrating that task-capacity matching enables optimal learning. Shows positive task difficulty-effort correlation only exists within appropriate load levels.
    - **Year**: 2024

14. **Title**: Cognitive Load Theory and Complex Learning (Van Merriënboer & Sweller, 2005)
    - **Authors**: Van Merriënboer & Sweller
    - **Summary**: Extends cognitive load theory to complex skill acquisition. Emphasizes scaffolding and part-task training for effective learning of complex skills.
    - **Year**: 2005

15. **Title**: Multitask Learning (Caruana, 1997)
    - **Authors**: Caruana
    - **Summary**: Foundational multi-task learning paper showing that related tasks improve generalization through shared representations. Demonstrates diverse tasks learn complementary features.
    - **Year**: 1997

16. **Title**: Multi-Task Learning Using Uncertainty to Weigh Losses (Kendall et al., 2018)
    - **Authors**: Kendall et al.
    - **Summary**: Proposes uncertainty-based loss weighting for multi-task learning using heteroscedastic uncertainty. Enables adaptive balancing of multiple task losses.
    - **Year**: 2018

17. **Title**: Curriculum Labeling: Revisiting Pseudo-Labeling for Semi-Supervised Learning (Cascante-Bonilla et al., 2021)
    - **Authors**: Cascante-Bonilla et al.
    - **Summary**: Applies curriculum learning to pseudo-labeling in semi-supervised learning. Focuses on sample confidence ordering rather than task design.
    - **Year**: 2021

18. **Title**: Coresets for Data-Efficient Training of Deep Networks (Mirzasoleiman et al., 2020)
    - **Authors**: Mirzasoleiman et al.
    - **Summary**: Develops methods for selecting informative training samples for efficiency through curriculum sample selection. Focuses on data selection rather than task design.
    - **Year**: 2020

19. **Title**: Bootstrap Your Own Latent (BYOL) (Grill et al., 2020)
    - **Authors**: Grill et al.
    - **Summary**: SSL method without negative pairs using momentum encoder and predictor. Combines prediction and contrastive objectives implicitly in a single fixed objective.
    - **Year**: 2020

20. **Title**: Emerging Properties in Self-Supervised Vision Transformers (DINO) (Caron et al., 2021)
    - **Authors**: Caron et al.
    - **Summary**: Self-distillation approach with centering and sharpening achieving strong results with Vision Transformers. Uses single fixed-task method without curriculum.
    - **Year**: 2021

**Key Challenges**

1. **Lack of Principled SSL Task Design Framework**: Existing SSL methods (SimCLR, MoCo) identify augmentation composition as critical but provide no systematic framework for designing auxiliary tasks. Task design remains ad-hoc and empirical.

2. **Theory-Practice Gap in SSL**: Gap between theoretical guarantees (asymptotic convergence) and practical training dynamics (finite samples, optimization challenges). Recent work (Reizinger et al., 2025) identifies this as major barrier to SSL research progress.

3. **Under-Explored Curriculum Learning for SSL**: While curriculum learning proven effective in supervised settings (Bengio et al., 2009), its application to self-supervised learning remains under-explored (Soviany et al., 2022 survey).

4. **Limited Cross-Domain Transfer of Learning Principles**: Educational psychology principles like cognitive load theory have not been systematically transferred to neural network learning, despite potential applicability to SSL auxiliary task design.

5. **Fixed Task Difficulty in SSL Methods**: Current SSL methods use fixed augmentation strength throughout training, potentially causing suboptimal learning trajectories (either too-easy tasks leading to trivial solutions or too-hard tasks causing training instability).

6. **Single-Task Limitations**: Many SSL methods focus on single objectives (contrastive-only or generative-only) without systematic multi-task scaffolding, potentially missing complementary learning signals.

7. **Absence of Dynamic Difficulty Adjustment**: No existing SSL framework dynamically adjusts task difficulty based on real-time encoder capacity measurements during training.

8. **Unclear Invariance Hierarchy for SSL**: Visual SSL lacks explicit hierarchical structure for auxiliary task generation (pixel-level → texture-level → object-level invariances), unlike the well-established visual cortex hierarchy in neuroscience.

9. **Hyperparameter Sensitivity**: SSL methods require extensive hyperparameter tuning for augmentation strength, training schedules, and task composition without principled guidelines.

10. **Computational Cost vs. Performance Trade-offs**: Limited understanding of cost-benefit analysis for different SSL approaches, making it difficult to determine when increased computational investment (e.g., curriculum framework) is justified by accuracy improvements.
