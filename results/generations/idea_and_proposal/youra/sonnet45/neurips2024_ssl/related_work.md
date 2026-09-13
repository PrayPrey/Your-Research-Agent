## Related Work

**Related Papers**
1. **Title**: To Compress or Not to Compress—Self-Supervised Learning and Information Theory: A Review (Shwartz-Ziv & LeCun, 2023)
   - **Authors**: Shwartz-Ziv & LeCun
   - **Summary**: Establishes information-theoretic foundation for self-supervised learning (SSL), discusses compression-preservation trade-off and provides theoretical motivation for Fisher metric extensions to geometric framework.
   - **Year**: 2023
   - **Semantic Scholar ID**: 97b1f4980fc173e59ff3a3bdaf1b9a13965fb32e

2. **Title**: An Augmentation-Aware Theory for Self-Supervised Contrastive Learning (Cui et al., 2025)
   - **Authors**: Cui et al.
   - **Summary**: First augmentation-aware error bound for SSL, demonstrating that task design affects generalization and showing importance of auxiliary task choice in representation learning.
   - **Year**: 2025
   - **Semantic Scholar ID**: d86e641baeb80530d530fafcccdafb108ae2a127

3. **Title**: Natural Gradient Works Efficiently in Learning (Amari, 1998)
   - **Authors**: Amari
   - **Summary**: Introduced natural gradients using Fisher information metric for parameter optimization, establishing feasibility of information geometry in deep learning.
   - **Year**: 1998

4. **Title**: Optimizing Neural Networks with Kronecker-factored Approximate Curvature (K-FAC) (Martens & Grosse, 2015)
   - **Authors**: Martens & Grosse
   - **Summary**: Provides tractable approximation of Fisher matrix for large-scale deep learning, reducing complexity from O(d²) to O(dk) and enabling computational feasibility for modern architectures.
   - **Year**: 2015

5. **Title**: Emerging Properties in Self-Supervised Vision Transformers (DINO) (Caron et al., 2021)
   - **Authors**: Caron et al.
   - **Summary**: Demonstrates self-distillation auxiliary task achieves strong performance in vision transformers, showing that task choice is critical for representation learning.
   - **Year**: 2021
   - **Citations**: 8060

6. **Title**: Masked Autoencoders Are Scalable Vision Learners (MAE) (He et al., 2022)
   - **Authors**: He et al.
   - **Summary**: Reconstruction-based auxiliary task for vision, contrasting with contrastive approaches and demonstrating effective self-supervised learning through masked image modeling.
   - **Year**: 2022

7. **Title**: A Vision Transformer with MAE-Based Self-Supervised Auxiliary Task (MAT-VIT) (Han et al., 2024)
   - **Authors**: Han et al.
   - **Summary**: Explores combining multiple auxiliary tasks (supervised + SSL) in vision transformers, demonstrating multi-task SSL approaches.
   - **Year**: 2024
   - **Semantic Scholar ID**: 3c7e07304bab6a860dbbe4ff36a4d87010036d2a

8. **Title**: Efficient Multimodal Fusion via Self-Supervised Multi-Task Learning with Auxiliary Mutual Information Maximization (Self-MI) (Nguyen et al., 2023)
   - **Authors**: Nguyen et al.
   - **Summary**: Uses mutual information (MI) maximization as auxiliary task design principle for multimodal learning, providing one objective perspective on task manifold optimization.
   - **Year**: 2023
   - **Semantic Scholar ID**: 1cb60a180fabc80dfae2e817a9175b4a5c2da71f

9. **Title**: An Empirically Grounded Identifiability Theory Will Accelerate Self-Supervised Learning Research (Reizinger et al., 2025)
   - **Authors**: Reizinger et al.
   - **Summary**: Proposes Singular Identifiability Theory (SITh) framework for SSL, focusing on what representations are learnable (complementary perspective to auxiliary task selection).
   - **Year**: 2025
   - **Semantic Scholar ID**: 214a5005de8029a0892201df1ad98d70f568d4ac

10. **Title**: Self-Supervised Contrastive Learning is Approximately Supervised Contrastive Learning (Luthra et al., 2025)
    - **Authors**: Luthra et al.
    - **Summary**: Proves theoretical connection between SSL and supervised learning, showing that different auxiliary tasks approximate supervised learning differently.
    - **Year**: 2025
    - **Semantic Scholar ID**: bef4d305edc81915e037d020ac328fc9a911535c

11. **Title**: Methods of Information Geometry (Amari & Nagaoka, 2000)
    - **Authors**: Amari & Nagaoka
    - **Summary**: Comprehensive treatment of information geometry, statistical manifolds, and Fisher metric, providing mathematical foundation for Riemannian structure on probability distribution spaces.
    - **Year**: 2000

12. **Title**: SimCLR (SSL Method)
    - **Authors**: Not specified
    - **Summary**: Contrastive learning framework for self-supervised visual representation learning, serving as a baseline auxiliary task in task manifold exploration.
    - **Year**: Not specified

13. **Title**: MoCo (SSL Method)
    - **Authors**: Not specified
    - **Summary**: Momentum Contrast for unsupervised visual representation learning, another contrastive learning approach serving as a baseline auxiliary task.
    - **Year**: Not specified

14. **Title**: BYOL (Bootstrap Your Own Latent)
    - **Authors**: Not specified
    - **Summary**: Self-supervised learning method without negative pairs, serving as an alternative auxiliary task design paradigm.
    - **Year**: Not specified

15. **Title**: SwAV (Swapping Assignments between Views)
    - **Authors**: Not specified
    - **Summary**: Clustering-based self-supervised learning method, providing another point on the auxiliary task manifold.
    - **Year**: Not specified

16. **Title**: Protein Language Models (Archon KB)
    - **Authors**: Not specified
    - **Summary**: Large-scale SSL applications in biological sequence analysis, demonstrating sample requirement challenges in self-supervised learning.
    - **Year**: Not specified

17. **Title**: Masked Prediction (Archon KB)
    - **Authors**: Not specified
    - **Summary**: Auxiliary task implementation pattern used across domains (vision, NLP, speech) for self-supervised pretraining.
    - **Year**: Not specified

**Key Challenges**
1. **Discrete Task Selection Problem**: Current SSL auxiliary task selection relies on exhaustive empirical search through predefined tasks (SimCLR, MAE, DINO, etc.), requiring 6-10× training time without theoretical guidance.

2. **Lack of Geometric Framework**: No existing framework treats auxiliary task space as having geometric structure, preventing principled task interpolation and continuous optimization.

3. **Computational Intractability**: Full Fisher information matrix computation has O(d²) complexity, making it infeasible for modern deep learning architectures with d > 10⁷ parameters.

4. **Domain-Specific Heuristics**: Task selection often relies on domain expert intuition (contrastive for vision, masked for NLP) rather than data-adaptive principles, limiting generalization to new domains.

5. **No Task Interpolation**: Existing methods cannot discover novel task configurations between known tasks (e.g., hybrid contrastive-reconstruction tasks), limiting exploration of task space.

6. **Target Distribution Estimation**: Without downstream task knowledge, estimating optimal target representation distribution (P_target) for SSL pretraining remains an open challenge.

7. **Manifold Smoothness Validation**: Unclear whether auxiliary task space forms smooth manifold where geodesic interpolation produces meaningful intermediate tasks with valid representations.

8. **K-FAC Approximation Quality**: While K-FAC reduces Fisher matrix complexity to O(dk), approximation quality for task selection (vs. parameter optimization) remains empirically unvalidated.

9. **Cross-Domain Generalization**: Auxiliary task selection methods that work well in vision (e.g., contrastive learning) may not transfer to NLP or speech domains, requiring domain-specific reengineering.

10. **Theoretical Gap in Task Selection**: While information theory has been applied to analyze individual SSL methods, no geometric theory exists for the meta-problem of selecting optimal auxiliary tasks from a continuous space.

11. **Multi-Modal Task Selection**: For vision-language models (CLIP, Flamingo), selecting optimal auxiliary tasks across multiple modalities lacks principled frameworks.

12. **Sample Complexity for Fisher Estimation**: Reliable Fisher information metric estimation requires sufficient samples (n ≥ 10,000), which may be limiting in low-data regimes.
