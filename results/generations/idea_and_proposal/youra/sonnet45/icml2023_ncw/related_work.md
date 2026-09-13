## Related Work

**Related Papers**

1. **Title**: A Mathematical Theory of Communication
   - **Authors**: Shannon
   - **Summary**: Foundational information theory establishing discrete channel capacity and compression limits. Established the theoretical framework for understanding information transmission and compression.
   - **Year**: 1948

2. **Title**: Auto-Encoding Variational Bayes
   - **Authors**: Kingma & Welling
   - **Summary**: Introduced Variational Autoencoder (VAE) framework with reparameterization trick enabling differentiable sampling from learned distributions. Foundation for probabilistic latent representations.
   - **Year**: 2013

3. **Title**: Variational image compression with a scale hyperprior
   - **Authors**: Ballé et al.
   - **Summary**: Established learned image compression using entropy models and neural networks, introducing scale hyperprior for improved compression. Uses quantization for entropy coding.
   - **Year**: 2018

4. **Title**: An Introduction to Neural Data Compression (146 citations)
   - **Authors**: Yang et al.
   - **Summary**: Tutorial establishing that quantization is universal in neural compression, documenting that quantization creates non-differentiable rounding operations requiring straight-through estimators which introduce gradient bias and variance.
   - **Year**: 2022

5. **Title**: Soft then Hard: Rethinking the Quantization in Neural Image Compression (90 citations)
   - **Authors**: Guo et al.
   - **Summary**: Addresses training-inference mismatch problem where soft quantization is used during training but hard quantization during inference. Closest existing approach to CVDC but still maintains quantization at inference.
   - **Year**: 2021

6. **Title**: A Survey on Continuous Variable Quantum Key Distribution (3 citations)
   - **Authors**: Motaharifar et al.
   - **Summary**: Demonstrates information transmission using continuous variables (Gaussian modulation) without discretization in quantum communication. Provides theoretical foundation from continuous-variable quantum information theory.
   - **Year**: 2025

7. **Title**: High-Fidelity Generative Image Compression (559 citations)
   - **Authors**: Mentzer et al.
   - **Summary**: State-of-the-art perceptual compression using GANs for high-quality image compression. Still uses quantization in latent space.
   - **Year**: 2020

8. **Title**: Optimization Methods for Large-Scale Machine Learning
   - **Authors**: Bottou et al.
   - **Summary**: Standard optimization theory establishing that smoother loss landscapes with continuous gradients reduce gradient variance and improve convergence rates.
   - **Year**: 2018

9. **Title**: Information Bottleneck Principle
   - **Authors**: Tishby & Zaslavsky
   - **Summary**: Theoretical framework for understanding information compression in neural networks through information-theoretic lens.
   - **Year**: 2015

10. **Title**: Elements of Information Theory (textbook)
   - **Authors**: Cover & Thomas
   - **Summary**: Foundational textbook covering rate-distortion theory for continuous sources, providing theoretical basis for compression of continuous distributions.
   - **Year**: Not specified

**Key Challenges**

1. **Quantization-Induced Gradient Discontinuities**: Quantization creates non-differentiable rounding operations requiring straight-through estimator approximations, which introduce gradient bias and variance during neural network training.

2. **Training-Inference Mismatch**: Current neural compression methods use soft quantization (additive noise) during training but hard quantization (rounding) during inference, creating operational inconsistency and performance gaps.

3. **Universal Reliance on Quantization**: Existing neural compression paradigms treat quantization as necessary for entropy coding, limiting exploration of alternative continuous-variable approaches.

4. **Compression Efficiency vs Optimization Quality Trade-off**: Quantization enables efficient entropy coding (fewer bits per latent) but creates optimization challenges, while continuous representations improve gradients but require more bits for parameter storage.

5. **Limited Cross-Domain Transfer from Quantum Information Theory**: Continuous-variable principles from quantum communication (CV-QKD) showing information transmission without discretization have not been applied to neural compression frameworks.

6. **Lack of Continuous Distributional Compression Methods**: No existing neural compression methods maintain continuous distributional representations throughout both training and inference, eliminating quantization entirely.
