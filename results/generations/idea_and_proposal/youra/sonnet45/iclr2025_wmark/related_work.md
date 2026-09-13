## Related Work

**Related Papers**

1. **Title**: Certified Adversarial Robustness via Randomized Smoothing (Cohen et al., 2019)
   - **Authors**: Cohen et al.
   - **Summary**: Introduces provable ℓ₂ robustness certificates for classifiers by constructing smoothed classifier f̄(x) = E[f(x + ε)], establishing the foundation for certification theorems using Gaussian convolution.
   - **Year**: 2019

2. **Title**: Unigram - Text Watermarking with Statistical Guarantees (Kirchenbauer et al., 2024)
   - **Authors**: Kirchenbauer et al.
   - **Summary**: Provides provable detectability under token-level attacks by analyzing unigram distribution of LLM outputs, demonstrating feasibility of provable watermark robustness for text-specific applications.
   - **Year**: 2024

3. **Title**: ROBIN - Adversarial Optimization Framework (Hannah1102, 2024)
   - **Authors**: Hannah1102
   - **Summary**: Bi-level optimization for adversarially robust watermarks in diffusion models, achieving 99.8% detection accuracy through empirical testing but lacking formal guarantees against adaptive attacks.
   - **Year**: 2024

4. **Title**: RAWatermark - Plug-and-Play with Provable Guarantees (jeremyxianx, 2024)
   - **Authors**: jeremyxianx
   - **Summary**: Robust and agile watermark framework for images and videos claiming "provable guarantees" but providing only empirical robustness without formal ℓ₂ certificates.
   - **Year**: 2024

5. **Title**: MACER - Certified Radius Maximization (Zhai et al., 2020)
   - **Authors**: Zhai et al.
   - **Summary**: Trains classifiers to maximize certified radius directly without adversarial examples, offering potential approach for watermark embedder optimization.
   - **Year**: 2020

6. **Title**: Recipe for Watermarking Diffusion Models (Zhao et al., 2023)
   - **Authors**: Zhao et al.
   - **Summary**: Training recipes for efficiently watermarking Stable Diffusion and multimodal diffusion models, providing base detector training methodology for image/video certification.
   - **Year**: 2023

7. **Title**: VLA-Mark - Cross-Modal Vision-Language Watermarking (Liu et al., 2025)
   - **Authors**: Liu et al.
   - **Summary**: Entropy-sensitive watermarking preserving multimodal coherence with 98.8% detection AUC, achieving cross-modal watermarking through joint training.
   - **Year**: 2025

8. **Title**: MarkLLM - LLM Watermarking Toolkit (THU-BPM, 2024)
   - **Authors**: THU-BPM
   - **Summary**: Open-source framework for LLM watermarking implementing KGW, SWEET, and SynthID-Text methods, providing base detector implementations for text modality certification.
   - **Year**: 2024

9. **Title**: IP Protection for ML Models (Lederer et al., 2023)
   - **Authors**: Lederer et al.
   - **Summary**: Unified threat model and taxonomy for ML model watermarking attacks, providing formal framework for characterizing adversary capabilities and certification requirements.
   - **Year**: 2023

10. **Title**: Adversarial Watermarking for Face Recognition (Yao et al., 2024)
    - **Authors**: Yao et al.
    - **Summary**: Demonstrates that watermarks can be exploited for adversarial attacks causing 67-96% accuracy degradation, highlighting critical need for certified robustness beyond empirical methods.
    - **Year**: 2024

11. **Title**: Watermarking Without Standards (Nemecek et al., 2025)
    - **Authors**: Nemecek et al.
    - **Summary**: Argues that current watermarking implementations risk symbolic compliance without enforceable standards, motivating need for formal certification enabling regulatory verification.
    - **Year**: 2025

12. **Title**: Interval Bound Propagation (Wang et al., 2021)
    - **Authors**: Wang et al.
    - **Summary**: Deterministic neural network verification via interval arithmetic offering complementary verification approach but computationally intractable for large networks like watermark detectors.
    - **Year**: 2021

13. **Title**: watermark_robustness - Attack Evaluation Suite (mehrdadsaberi)
    - **Authors**: mehrdadsaberi
    - **Summary**: Comprehensive attack taxonomy for watermark robustness testing, providing benchmark attacks for certified robustness evaluation.
    - **Year**: Not specified

**Key Challenges**

1. **Lack of Formal Robustness Guarantees**: Current watermarking methods provide empirical robustness only without formal mathematical certificates, making them insufficient for regulatory compliance and security-critical applications.

2. **Text-Specific Provable Methods**: Existing provable watermarking approaches like Unigram are watermark-specific and modality-specific (text only), lacking generalization to neural detectors and other modalities.

3. **Clean Accuracy vs. Robustness Trade-off**: Applying randomized smoothing creates fundamental tension between detection accuracy on clean samples and certified robustness radius, requiring careful optimization.

4. **Computational Cost of Certification**: Monte Carlo sampling with N=10,000+ samples for certification requires significant computational resources (10-100 seconds per sample), limiting real-time applicability.

5. **Limited Attack Scope**: ℓ₂-bounded adversary model does not cover spatial transformations, compression attacks, re-generation attacks, and semantic attacks that commonly occur in practice.

6. **Regulatory Compliance Gap**: Current implementations lack enforceable technical standards and audit infrastructure needed for EU AI Act Article 52 and California AB 3211 compliance.

7. **Cross-Modality Consistency**: Watermark strength normalization across modalities (images, text, audio, video) presents challenges for fair comparison and unified certification framework.

8. **Adaptive Attack Vulnerability**: Empirical robustness testing methods like ROBIN are vulnerable to adaptive attacks outside their test set, lacking provable guarantees.

9. **Certification Magnitude Uncertainty**: Unclear whether certified radius r will be sufficiently large for practical adversarial budgets (typical ε_attack ~ 0.1-0.3) with realistic watermark strengths.

10. **Real-Time Deployment Constraints**: Certification as offline process creates gap between detection-time requirements and regulatory verification needs for auditable documentation.
