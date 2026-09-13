## Related Work

**Related Papers**
1. **Title**: An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale (Dosovitskiy et al. 2021)
   - **Authors**: Dosovitskiy et al.
   - **Summary**: Original Vision Transformer (ViT) paper introducing ViT-B/16 architecture achieving 79.9% ImageNet-1K top-1 accuracy with pre-training, and ~76-77% when training from scratch on ImageNet-1K only.
   - **Year**: 2021

2. **Title**: REPA (ICLR 2025)
   - **Authors**: sihyun-yu/REPA (GitHub implementation)
   - **Summary**: Demonstrated that REPA-style alignment intervention successfully increases CKA similarity in diffusion models using alignment loss L_total = (1-λ)L_task + λL_align. ICLR 2025 Oral presentation with 1000+ GitHub stars.
   - **Year**: 2025

3. **Title**: Khosla et al. (2024)
   - **Authors**: Khosla et al.
   - **Summary**: Correlational study showing that aligned representational axes correlate with computational efficiency measured through wiring costs in neural networks.
   - **Year**: 2024

4. **Title**: Mahner et al. (2024)
   - **Authors**: Mahner et al.
   - **Summary**: Descriptive analysis demonstrating that humans and deep neural networks (DNNs) can achieve similar task performance via different computational strategies despite showing representational alignment.
   - **Year**: 2024

5. **Title**: Damatac et al. (2024)
   - **Authors**: Damatac et al.
   - **Summary**: Neuroscience study showing that neural synchrony (inter-subject correlation of brain activity) and functional connectivity (directed information flow between brain regions) can dissociate under different task conditions (threatening vs. neutral movie clips), providing precedent for alignment-computation dissociability.
   - **Year**: 2024

6. **Title**: Similarity of Neural Network Representations Revisited (Kornblith et al. 2019)
   - **Authors**: Kornblith et al.
   - **Summary**: Established Centered Kernel Alignment (CKA) as standard metric for measuring representational similarity in deep learning, with invariance to orthogonal transformations and isotropic scaling. 311★ implementation.
   - **Year**: 2019

7. **Title**: Murphy et al. (2024)
   - **Authors**: Murphy et al.
   - **Summary**: Identified bias in standard CKA estimator in low-data high-dimensionality regimes and proposed debiased estimator variant for improved accuracy when feature-sample ratio < 0.1.
   - **Year**: 2024

8. **Title**: Opening the Black Box of Deep Neural Networks via Information (Tishby & Zaslavsky 2015)
   - **Authors**: Tishby & Zaslavsky
   - **Summary**: Information Bottleneck theory proposing that mutual information I(T;Y) relates to generalization performance, providing theoretical framework for understanding compression-relevance trade-offs in neural networks.
   - **Year**: 2015

**Key Challenges**
1. **Alignment-Computation Causality Unknown**: No established research directly testing whether representational alignment (measured by CKA) causally affects computational mechanisms (attention patterns, information flow) or whether these are merely correlated but dissociable properties.

2. **Transfer from Generative to Discriminative Models**: REPA demonstrated alignment intervention success in generative models (diffusion), but validity for discriminative models (ViT classification) remains untested assumption requiring empirical validation.

3. **Computational Metric Validity**: Attention entropy, Gini coefficient, and mutual information (I(X;T), I(T;Y)) are proxy metrics for "computational strategy" with uncertain validity - whether they truly capture meaningful computational mechanism differences is unvalidated.

4. **Accuracy-Alignment Confound Control**: Challenge of manipulating representational alignment while maintaining task performance within controlled tolerance (±5%) to enable clean causal inference without confounding effects.

5. **Reference System Dependency**: CKA alignment measurement requires choosing reference system (human fMRI vs pre-aligned DNN), and alignment interpretation depends on what the reference represents, affecting generalizability of findings.

6. **Architecture and Domain Specificity**: Existing alignment research lacks systematic investigation of whether alignment-computation relationships generalize across architectures (ViT vs CNN vs RNN) and modalities (vision vs language vs multimodal).

7. **Proxy Metrics Ground Truth Problem**: "Computational strategy" is conceptual construct without directly observable ground truth, limiting ability to validate whether proposed metrics (attention patterns, mutual information) capture the intended computational properties.

8. **Post-Training Analysis Only**: Current alignment research focuses on post-training inference-time measurements without studying how alignment and computational mechanisms co-evolve during training dynamics.
