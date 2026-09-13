## Related Work

**Related Papers**
1. **Title**: Deep Variational Information Bottleneck (arXiv:1612.00410)
   - **Authors**: Alemi et al.
   - **Summary**: Introduces a variational approximation to the Information Bottleneck using the reparameterization trick, enabling practical training while improving generalization and adversarial robustness.
   - **Year**: 2017

2. **Title**: How Does Information Bottleneck Help Deep Learning? (arXiv:2305.18887)
   - **Authors**: Kawaguchi et al.
   - **Summary**: Provides the first rigorous bounds relating Information Bottleneck degree to generalization errors, demonstrating that generalization scales with IB rather than parameter count.
   - **Year**: 2023

3. **Title**: Variational Image Compression with a Scale Hyperprior (arXiv:1802.01436)
   - **Authors**: Ballé et al.
   - **Summary**: Introduces a hyperprior mechanism to capture spatial dependencies in latent representations, achieving state-of-the-art image compression performance via VAE architecture.
   - **Year**: 2018

4. **Title**: Learned Image Compression with Mixed Transformer-CNN Architectures (arXiv:2303.14978)
   - **Authors**: Liu et al.
   - **Summary**: Proposes TCM blocks combining CNN local modeling with Transformer non-local modeling, achieving state-of-the-art results on Kodak and CLIC benchmarks.
   - **Year**: 2023

5. **Title**: The Unreasonable Effectiveness of Deep Features as a Perceptual Metric (arXiv:1801.03924)
   - **Authors**: Zhang et al.
   - **Summary**: Demonstrates that LPIPS using deep features achieves 97% agreement with human perceptual judgments, validating VGG features for perceptual similarity measurement.
   - **Year**: 2018

6. **Title**: HiFiC - High-Fidelity Generative Image Compression
   - **Authors**: Mentzer et al.
   - **Summary**: Introduces GAN-based perceptual compression that empirically bridges the rate-distortion-perception tradeoff for high-fidelity image reconstruction.
   - **Year**: 2020

7. **Title**: CompressAI Hyperprior
   - **Authors**: InterDigital
   - **Summary**: Provides a standard VAE baseline implementation with hyperprior for learned image compression.
   - **Year**: 2020

8. **Title**: SVI - Synonymous Visual Input
   - **Authors**: Not specified
   - **Summary**: Proposes learned synonymous sets for perceptual compression, using learned representations rather than frozen networks.
   - **Year**: 2025

9. **Title**: On the Information Bottleneck Theory of Deep Learning
   - **Authors**: Saxe et al.
   - **Summary**: Provides critical analysis of the IB-generalization link, particularly questioning its applicability to ReLU networks.
   - **Year**: 2018

10. **Title**: Exploring Action-Centric Representations Through Rate-Distortion Theory
    - **Authors**: De Llanza et al.
    - **Summary**: Demonstrates that VAEs learn task-relevant invariances under rate-distortion constraints, providing cross-domain validation for compression approaches.
    - **Year**: 2024

**Key Challenges**
1. **Theoretical Grounding for Perceptual Compression**: Existing GAN-based approaches like HiFiC bridge rate-distortion-perception empirically without rigorous theoretical justification.

2. **IB-Generalization Link Validity**: Critiques of Information Bottleneck theory for ReLU networks raised concerns about its applicability, requiring more rigorous frameworks to establish the connection.

3. **Cross-Domain Validation**: Rate-distortion approaches validated for task-relevant representations need extension to perceptual (rather than pixel-level) compression domains.

4. **Learned vs. Frozen Representations**: Trade-offs exist between approaches using learned synonymous sets versus frozen pretrained networks for perceptual similarity measurement.
