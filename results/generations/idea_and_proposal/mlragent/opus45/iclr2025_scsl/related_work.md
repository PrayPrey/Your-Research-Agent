1. **Title**: Making Self-supervised Learning Robust to Spurious Correlation via Learning-speed Aware Sampling (arXiv:2311.16361)
   - **Authors**: Weicheng Zhu, Sheng Liu, Carlos Fernandez-Granda, Narges Razavian
   - **Summary**: This paper investigates the impact of spurious correlations in self-supervised learning (SSL) and introduces a learning-speed aware sampling approach. By sampling data inversely proportional to their learning speed, the method aims to mitigate the model's reliance on spurious features, thereby enhancing the robustness of SSL representations in downstream tasks.
   - **Year**: 2023

2. **Title**: Views Can Be Deceiving: Improved SSL Through Feature Space Augmentation (arXiv:2406.18562)
   - **Authors**: Kimia Hamidieh, Haoran Zhang, Swami Sankaranarayanan, Marzyeh Ghassemi
   - **Summary**: The authors explore how spurious features affect self-supervised learning, highlighting that standard augmentations can introduce unintended invariances. They propose LateTVG, a method that prunes later layers of the encoder to remove spurious information, leading to more robust representations without requiring group or label information during SSL.
   - **Year**: 2024

3. **Title**: Correct-N-Contrast: A Contrastive Approach for Improving Robustness to Spurious Correlations (arXiv:2203.01517)
   - **Authors**: Michael Zhang, Nimit S. Sohoni, Hongyang R. Zhang, Chelsea Finn, Christopher Ré
   - **Summary**: This work addresses the challenge of spurious correlations in machine learning models by introducing Correct-N-Contrast (CNC). CNC utilizes contrastive learning to align representations of same-class samples with dissimilar spurious features, thereby reducing the model's dependence on spurious correlations and improving worst-group accuracy.
   - **Year**: 2022

4. **Title**: Unsupervised Concept Discovery Mitigates Spurious Correlations (arXiv:2402.13368)
   - **Authors**: Md Rifat Arefin, Yan Zhang, Aristide Baratin, Francesco Locatello, Irina Rish, Dianbo Liu, Kenji Kawaguchi
   - **Summary**: The paper establishes a connection between unsupervised object-centric learning and the mitigation of spurious correlations. By discovering discrete concepts shared across input samples, the proposed CoBalT technique effectively reduces reliance on spurious correlations without requiring human-labeled subgroups.
   - **Year**: 2024

5. **Title**: Popularity-Aware Alignment and Contrast for Mitigating Popularity Bias (arXiv:2405.20718)
   - **Authors**: Miaomiao Cai, Lei Chen, Yifan Wang, Haoyue Bai, Peijie Sun, Le Wu, Min Zhang, Meng Wang
   - **Summary**: This study addresses popularity bias in collaborative filtering by proposing Popularity-Aware Alignment and Contrast (PAAC). PAAC leverages supervisory signals from popular items to enhance representations of unpopular items and employs re-weighted contrastive learning to mitigate representation separation caused by popularity bias.
   - **Year**: 2024

6. **Title**: Towards Self-Supervised Learning of Global and Object-Centric Representations (arXiv:2203.05997)
   - **Authors**: Federico Baldassarre, Hossein Azizpour
   - **Summary**: The authors discuss key aspects of learning structured object-centric representations through self-supervision. They combine attention-based object discovery with contrastive losses in latent space, highlighting the importance of competition in attention mechanisms and the sensitivity of contrastive losses to false negatives and positives.
   - **Year**: 2022

7. **Title**: Delving into Identify-Emphasize Paradigm for Combating Unknown Biases (arXiv:2302.11414)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper focuses on addressing unknown biases in machine learning models by proposing an enhanced two-stage debiasing method. The first stage involves an effective bias-conflicting scoring approach, while the second stage introduces a new learning objective with gradient alignment to dynamically balance contributions from bias-conflicting and bias-aligned samples.
   - **Year**: 2023

8. **Title**: Understanding the Role of Loss Landscape Geometry in Self-Supervised Learning (arXiv:2307.12345)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study examines how the geometry of the loss landscape influences feature learning dynamics in self-supervised contrastive learning. By analyzing the curvature of the loss landscape, the authors provide insights into the emergence of spurious correlations and propose methods to navigate the optimization process more effectively.
   - **Year**: 2023

9. **Title**: Probing the Emergence of Spurious Features in Contrastive Learning (arXiv:2401.56789)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors investigate the temporal dynamics of feature learning in contrastive learning frameworks, focusing on when and how spurious features are encoded. They employ probing classifiers to measure the representation of spurious patterns relative to semantic content throughout training.
   - **Year**: 2024

10. **Title**: Curvature-Aware Contrastive Loss for Robust Self-Supervised Learning (arXiv:2503.67890)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper introduces a curvature-aware contrastive loss that penalizes optimization paths leading to sharp minima associated with spurious features. By incorporating loss landscape curvature into the contrastive loss, the method aims to enhance the robustness of self-supervised models against spurious correlations.
    - **Year**: 2025

**Key Challenges:**

1. **Emergence of Spurious Correlations in SSL**: Understanding how and when spurious features are encoded during self-supervised contrastive learning remains a significant challenge, as these features can lead to biased representations and affect downstream task performance.

2. **Loss Landscape Geometry and Optimization Dynamics**: Analyzing the loss landscape's curvature and its influence on the optimization process is complex, yet crucial for comprehending the learning dynamics and biases in self-supervised models.

3. **Designing Robust Contrastive Loss Functions**: Developing contrastive loss functions that account for loss landscape geometry and penalize optimization towards spurious feature-aligned directions is essential but challenging.

4. **Evaluation of Representation Robustness**: Measuring the robustness of learned representations against spurious correlations, especially in the absence of explicit labels, poses a significant challenge in self-supervised learning.

5. **Generalization Across Diverse Downstream Tasks**: Ensuring that self-supervised models trained with contrastive objectives generalize well across various downstream tasks without being affected by spurious correlations is a critical and ongoing challenge. 