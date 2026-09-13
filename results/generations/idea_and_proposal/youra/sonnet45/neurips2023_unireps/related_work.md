## Related Work

**Related Papers**

1. **Title**: Understanding the Emergence of Multimodal Representation Alignment (arXiv ID: 929f6c03c891e6bc62908040b61d0e73baba5f83)
   - **Authors**: Tjandrasuwita et al.
   - **Summary**: Provides empirical evidence that alignment is NOT universally beneficial and depends on modality similarity and information redundancy. However, the work is analysis-only and lacks a predictive framework.
   - **Year**: 2025

2. **Title**: To Align or Not to Align (arXiv ID: 640e3bd5ef3962ec43af02d7c5b21bcbd8392c7d)
   - **Authors**: Fang et al.
   - **Summary**: Demonstrates that optimal alignment depends on modality redundancy, but relies on manual tuning approaches rather than automated methods.
   - **Year**: 2025

3. **Title**: DecAlign (arXiv ID: 8bcf57931ef79e35e711ef48795888dc7b4a9322)
   - **Authors**: Qian et al.
   - **Summary**: Proposes hierarchical cross-modal alignment with decoupling that decomposes representations into modality-unique and modality-common components using prototype-guided optimal transport, but uses a fixed decomposition ratio that is not data-adaptive.
   - **Year**: 2025

4. **Title**: Deconfounded Representation Similarity (arXiv ID: 7f4c9985c69d4cf474d78ddb4edc9e7e5e72160a)
   - **Authors**: Cui et al.
   - **Summary**: Adjusts Centered Kernel Alignment (CKA) for population structure confounding, providing robust measurement methods for representation similarity.
   - **Year**: 2022

5. **Title**: Correcting Biased CKA (arXiv ID: 9d7635db800929e947b8dbbf7ea00b1e33dfcc95)
   - **Authors**: Murphy et al.
   - **Summary**: Identifies and addresses bias in CKA metrics, particularly showing that biased CKA is insensitive in low-data regimes, providing important warnings for similarity measurement.
   - **Year**: 2024

6. **Title**: Equivalence between RSA, CKA, and CCA (arXiv ID: 7ad2a5214643b02167635afe0ec01bf6a1c96d65)
   - **Authors**: Williams
   - **Summary**: Establishes theoretical equivalence showing that Representational Similarity Analysis (RSA) is approximately equal to CKA with mean-centering, providing theoretical grounding for using CKA as a similarity metric.
   - **Year**: 2024

7. **Title**: CCA Merge (arXiv ID: 32eb03c411272a50f2ebddca2df036aab325ed79)
   - **Authors**: Horoi et al.
   - **Summary**: Uses Canonical Correlation Analysis to maximize feature correlations for model merging, learning linear transformations that align models in feature space and outperforming permutation-based methods. However, it is applied post-hoc after training rather than during training.
   - **Year**: 2024

8. **Title**: Low-rank bias and model merging (arXiv ID: aa6e4685b4883c6ee8071ccb6c72e04a0273ec0a)
   - **Authors**: Kuzborskij & Abbasi-Yadkori
   - **Summary**: Demonstrates that L2 regularization leads to low-rank bias which enables successful weight averaging, providing theoretical insight that structural properties facilitate alignment.
   - **Year**: 2025

9. **Title**: Generalized Linear Mode Connectivity for Transformers (arXiv ID: 9a1a9d3dda4be2fb3ffc0b1f64476275b0adca52)
   - **Authors**: Theus et al.
   - **Summary**: Achieves first zero-barrier linear mode connectivity for Vision Transformers and GPT-2 via 4 symmetry classes, addressing when models can be unified in parameter space through weight averaging.
   - **Year**: 2025

10. **Title**: Layerwise Linear Mode Connectivity (arXiv ID: 9eb06c7c06f96e9f2a44226a8d7ce321372319f5)
    - **Authors**: Adilova et al.
    - **Summary**: Demonstrates that deep networks lack layer-wise barriers in the loss landscape, suggesting potential for layer-wise budget allocation strategies.
    - **Year**: 2023

11. **Title**: Reptile: A Scalable Meta-Learning Algorithm
    - **Authors**: Nichol & Schulman
    - **Summary**: Introduces first-order meta-learning approximation that achieves comparable performance to MAML while reducing computational overhead from ~2.5x to ~1.5x training cost.
    - **Year**: 2018

12. **Title**: Model-Agnostic Meta-Learning (MAML)
    - **Authors**: Finn et al.
    - **Summary**: Proposes model-agnostic meta-learning framework using second-order optimization that enables fast adaptation to new tasks with few gradient steps.
    - **Year**: 2017

13. **Title**: Task similarity effects in brains and neural networks (arXiv ID: 99d4920b672eea5f3db473d96971b676ce94b048)
    - **Authors**: Menghi et al.
    - **Summary**: Demonstrates through MEG and network models that similar tasks initially perform worse and require orthogonalization, providing empirical support that alignment is not always beneficial and diversification may be needed.
    - **Year**: 2025

14. **Title**: Deep SNNs similarity to biological visual cortex (arXiv ID: 462b999f9e47915c89a0c70d797d3e82276f8410)
    - **Authors**: Huang et al.
    - **Summary**: Shows that Spiking Neural Networks (SNNs) exhibit higher similarity to biological visual cortex than Convolutional Neural Networks (CNNs), demonstrating the importance of alignment measurement across systems.
    - **Year**: 2023

15. **Title**: CLIP: Learning Transferable Visual Models From Natural Language Supervision
    - **Authors**: Radford et al.
    - **Summary**: Proposes contrastive vision-language alignment with fixed temperature parameter for controlling alignment strength, projecting vision and language to shared embedding space with uniform alignment across all samples.
    - **Year**: 2021

16. **Title**: TIES Adapter Merging
    - **Authors**: Not specified
    - **Summary**: Introduces density parameter to control merge sparsity in adapter fusion methods, inspiring the "alignment budget" formulation for resource allocation.
    - **Year**: Not specified

17. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
    - **Authors**: Not specified
    - **Summary**: Proposes low-rank adapter merging via weighted averaging for parameter-efficient fine-tuning of large language models.
    - **Year**: Not specified

18. **Title**: Mutual Information Neural Estimation (MINE)
    - **Authors**: Belghazi et al.
    - **Summary**: Provides estimator for mutual information that is stable with 1000+ samples, enabling measurement of information redundancy between modalities.
    - **Year**: 2018

**Key Challenges**

1. **Lack of Predictive Framework for Conditional Alignment**: While empirical evidence shows that alignment benefits are conditional on dataset characteristics, existing work lacks a predictive framework to automatically determine optimal alignment strategies from data properties.

2. **Manual Hyperparameter Tuning Burden**: Current approaches require extensive manual tuning of alignment hyperparameters (e.g., CLIP temperature, DecAlign decomposition ratio, TIES density parameter) through grid search or Bayesian optimization, resulting in 10-50x computational overhead.

3. **Fixed vs. Adaptive Alignment Trade-off**: Existing methods use either fixed alignment strategies (uniform across all datasets) or require dataset-specific manual tuning, lacking adaptive mechanisms that automatically adjust based on measured dataset characteristics.

4. **Fragmentation Across Application Domains**: Multimodal learning (DecAlign, CLIP), model merging (CCA Merge, Task Arithmetic), and transfer learning (domain adaptation methods) are addressed by separate specialized methods rather than unified frameworks, requiring separate implementations and expertise.

5. **Post-hoc vs. During-Training Optimization**: Many alignment methods (e.g., CCA Merge) are applied post-hoc after model training, missing opportunities to optimize alignment proactively during the training process itself.

6. **Computational Overhead of Meta-Learning**: Second-order meta-learning methods like MAML impose ~2.5x training cost overhead, creating barriers to practical deployment despite their theoretical advantages.

7. **Measurement Robustness Issues**: CKA and other similarity metrics suffer from bias in low-data regimes and confounding from population structure, requiring deconfounding techniques and ensemble approaches for reliable measurement.

8. **Alignment-Diversification Balance**: Excessive alignment can waste computation on redundant modalities and lose unique modality-specific information, while insufficient alignment misses opportunities to exploit shared structure, but principled methods to balance this trade-off are lacking.

9. **Generalization Boundary Uncertainty**: The extent to which alignment policies can generalize across radically different domains (e.g., vision to audio, multimodal to model merging) remains unclear, with potential need for domain-specific meta-training.

10. **Interpretability of Learned Allocation**: While explicit budget parameters are interpretable, fine-grained per-dimension allocation weights and the causal relationship between dataset characteristics and optimal budgets lack full explainability.
