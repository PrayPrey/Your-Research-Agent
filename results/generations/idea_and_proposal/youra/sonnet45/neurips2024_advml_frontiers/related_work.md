## Related Work

**Related Papers**
1. **Title**: Certified Adversarial Robustness via Randomized Smoothing (Cohen et al. 2019)
   - **Authors**: Cohen et al.
   - **Summary**: Foundational work proving that Gaussian noise injection enables L2 robustness certification for image classifiers. Establishes the certified radius formula r_v = σ_v * Φ^{-1}(p_v) and Monte Carlo certification protocol with 1000 samples.
   - **Year**: 2019

2. **Title**: SAFER: A Structure-free Approach for Certified Robustness to Adversarial Word Substitutions (Jia et al. 2019)
   - **Authors**: Jia et al.
   - **Summary**: Extends randomized smoothing to discrete text domain, providing foundation for discrete smoothing with token-level perturbations. Enables certification of language models against token substitution attacks.
   - **Year**: 2019

3. **Title**: Modular Neural Verification (MNV 2023)
   - **Authors**: Not specified
   - **Summary**: Demonstrates 100x speedup via modular decomposition in network verification. Provides evidence that compositional verification enables tractable analysis of large neural networks through architectural decomposition.
   - **Year**: 2023

4. **Title**: ECLipsE: Efficient Compositional Lipschitz Estimation (2024)
   - **Authors**: Not specified
   - **Summary**: Validates Interval Bound Propagation (IBP) based Lipschitz estimation for neural network layers, achieving thousand-fold speedup vs. exact computation. Provides methodology for tractable fusion layer Lipschitz constant estimation.
   - **Year**: 2024

5. **Title**: APT: Adversarial Prompt Tuning (Li et al. 2024)
   - **Authors**: Li et al.
   - **Summary**: Empirical defense for multimodal models using adversarial prompt learning. Achieves ~65% robust accuracy (estimated) through lightweight prompt-based robustness enhancement. State-of-the-art empirical baseline.
   - **Year**: 2024

6. **Title**: PMG-AFT: Pre-Trained Model Guided Adversarial Fine-Tuning (Wang et al. 2024)
   - **Authors**: Wang et al.
   - **Summary**: Empirical defense achieving ~68% robust accuracy through pre-trained guided fine-tuning. Preserves zero-shot generalization while improving robustness (+4.99% robust accuracy reported).
   - **Year**: 2024

7. **Title**: MMCoA: Multimodal Contrastive Adversarial Training (Zhou et al. 2024)
   - **Authors**: Zhou et al.
   - **Summary**: State-of-the-art empirical adversarial training approach for multimodal models achieving ~62% empirical robustness. Addresses cross-modal robustness through adversarial training across modalities.
   - **Year**: 2024

8. **Title**: Medical VLM Certification (2025)
   - **Authors**: Not specified
   - **Summary**: First certified multimodal defense using monolithic randomized smoothing for medical vision-language models. Achieves ~70% certified accuracy but limited to small models (~100M parameters) due to computational constraints.
   - **Year**: 2025

9. **Title**: Adversarial Training for Robust Deep Learning (Madry et al. 2018)
   - **Authors**: Madry et al.
   - **Summary**: Foundational work on adversarial training providing standard assumptions used in robust optimization literature. Establishes adversarial training paradigm for improving model robustness.
   - **Year**: 2018

10. **Title**: Robust Optimization with Lipschitz Regularization (Anil et al. 2019)
    - **Authors**: Anil et al.
    - **Summary**: Validates that Lipschitz minimization via adversarial training improves certified robustness. Provides theoretical foundation for fusion layer Lipschitz regularization approach.
    - **Year**: 2019

11. **Title**: Improved Discrete Smoothing (Ye et al. 2020)
    - **Authors**: Ye et al.
    - **Summary**: Recent advances improving tightness of discrete text smoothing beyond Jia et al. 2019. Enhances certification quality for language models.
    - **Year**: 2020

12. **Title**: CLIP: Contrastive Language-Image Pre-training
    - **Authors**: Not specified
    - **Summary**: Foundation model with modular architecture (separate vision encoder ViT, language encoder Transformer, cosine similarity fusion). Target architecture for MCS implementation with 427M vision + 63M language parameters.
    - **Year**: Not specified

13. **Title**: BLIP: Bootstrapping Language-Image Pre-training
    - **Authors**: Not specified
    - **Summary**: Multimodal model with moderate early fusion (2-4 layer cross-attention). Used to validate hierarchical fusion handling in MCS framework.
    - **Year**: Not specified

14. **Title**: ALIGN: Scaling Up Visual and Vision-Language Representation Learning
    - **Authors**: Not specified
    - **Summary**: Late fusion LMM using contrastive learning. Exemplifies modular architecture suitable for compositional certification.
    - **Year**: Not specified

**Key Challenges**
1. **Computational Intractability of Monolithic Certification**: Existing certified defenses (Cohen et al. 2019) scale to unimodal models but monolithic randomized smoothing requires O(N_v * N_t) complexity for multimodal models, making billion-parameter LMM certification intractable (≥80 GPU-hours estimated).

2. **Lack of Formal Guarantees for Multimodal Defenses**: State-of-the-art multimodal defenses (APT, PMG-AFT, MMCoA) provide only empirical robustness without provable worst-case guarantees, insufficient for safety-critical applications (medical diagnosis, autonomous systems).

3. **Scalability Barrier for Large Multimodal Models**: Medical VLM Certification (2025) provides multimodal certification but only for small models (~100M parameters). No existing approach enables certified defenses for billion-parameter LMMs (CLIP ViT-L/14: 490M params).

4. **Composition Bound Tightness Uncertainty**: Compositional verification approaches risk loose bounds (tightness ratio ρ < 0.3) that yield impractical certificates. Need to validate acceptable tightness (target ρ ≥ 0.5) for compositional multimodal smoothing.

5. **Discrete Text Smoothing Immaturity**: Token-level smoothing for language models is less developed than image smoothing (Gaussian noise). Discrete smoothing (Jia 2019) provides foundation but may yield looser certificates compared to vision smoothing.

6. **Fusion Layer Sensitivity**: Large fusion Lipschitz constants (L_f > 3.0) degrade compositional bounds via the term (1 - L_f * (r_v + r_t)), potentially yielding trivial certificates. Requires Lipschitz regularization during training.

7. **Clean Accuracy Trade-off**: Certified robustness inherently trades clean accuracy for robustness guarantees. Need to maintain ≥85% clean accuracy (vs. 94% for undefended CLIP) while achieving ≥70% certified accuracy.

8. **Early Fusion Architecture Incompatibility**: Models with tight vision-language coupling from early layers (VisualBERT, LXMERT) lack functional independence required for modular decomposition, limiting MCS applicability to late/moderate fusion architectures.
