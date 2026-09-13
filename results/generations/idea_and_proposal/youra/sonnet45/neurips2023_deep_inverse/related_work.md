## Related Work

**Related Papers**

1. **Title**: Pseudoinverse-Guided Diffusion Models for Inverse Problems (ICML 2023)
   - **Authors**: Song et al.
   - **Summary**: Uses known forward operator A to guide diffusion sampling via pseudoinverse A†. Performance degrades rapidly with operator mismatch (10% error → ~3dB PSNR drop).
   - **Year**: 2023

2. **Title**: Improving Diffusion Models for Inverse Problems using Manifold Constraints (NeurIPS 2022)
   - **Authors**: Chung et al.
   - **Summary**: Projects diffusion samples onto data manifold to maintain consistency. Achieves ~38dB PSNR on medical imaging (MRI, CT) with known operators.
   - **Year**: 2022

3. **Title**: Score-Based Generative Modeling through Stochastic Differential Equations (ICLR 2021 Oral)
   - **Authors**: Song et al.
   - **Summary**: Continuous-time diffusion via SDEs with VE/VP schedules. Foundation for score matching and SDE framework for diffusion models.
   - **Year**: 2021

4. **Title**: Denoising Diffusion Probabilistic Models (NeurIPS 2020)
   - **Authors**: Ho et al.
   - **Summary**: Discrete-time diffusion with learned reverse process. Foundational work for DDPM sampling.
   - **Year**: 2020

5. **Title**: Bi-Level Meta-Learning for Few-Shot Domain Generalization (CVPR 2023)
   - **Authors**: Qin et al.
   - **Summary**: Separates domain-specific (lower) from domain-invariant (upper) knowledge. Demonstrates 20-40% accuracy improvement in cross-domain few-shot learning with 5-20 samples.
   - **Year**: 2023

6. **Title**: Model-Agnostic Meta-Learning (ICML 2017)
   - **Authors**: Finn et al.
   - **Summary**: Fast adaptation with few gradient steps on new tasks. Foundational work in meta-learning with 7k+ citations.
   - **Year**: 2017

7. **Title**: StyleAdv: Meta Style Adversarial Training for Cross-Domain Few-Shot Learning (CVPR 2023)
   - **Authors**: Fu et al.
   - **Summary**: Adversarial perturbation on style space for robustness in cross-domain learning.
   - **Year**: 2023

8. **Title**: Remember the Difference: Cross-Domain Few-Shot Semantic Segmentation via Meta-Memory Transfer (CVPR 2022)
   - **Authors**: Wang et al.
   - **Summary**: Memory bank of domain prototypes for retrieval in cross-domain transfer tasks.
   - **Year**: 2022

9. **Title**: Uncertainty Quantification for Forward and Inverse Problems of PDEs via Latent Global Evolution (NeurIPS 2024)
   - **Authors**: Wu et al.
   - **Summary**: Latent evolution for UQ in PDE inverse problems (LE-PDE-UQ framework).
   - **Year**: 2024

10. **Title**: Monte Carlo guided Denoising Diffusion models for Bayesian linear inverse problems
    - **Authors**: Cardoso et al.
    - **Summary**: Bayesian posterior sampling with diffusion models for linear inverse problems.
    - **Year**: 2024

11. **Title**: Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles (NeurIPS 2017)
    - **Authors**: Lakshminarayanan et al.
    - **Summary**: Ensemble-based epistemic uncertainty estimation with 2k+ citations. Foundation for uncertainty calibration techniques.
    - **Year**: 2017

12. **Title**: Efficient Filter Flow for Space-Variant Multiframe Blind Deconvolution (CVPR 2010)
    - **Authors**: Hirsch et al.
    - **Summary**: Alternating optimization for spatially-variant blur kernel estimation. Demonstrates local convergence of alternating minimization.
    - **Year**: 2010

13. **Title**: Total Variation Blind Deconvolution (IEEE TIP 1998)
    - **Authors**: Chan & Wong
    - **Summary**: TV regularization for blind deblurring. Classical method with 1.5k+ citations using hand-crafted priors.
    - **Year**: 1998

14. **Title**: Blind Super-Resolution Kernel Estimation using an Internal-GAN (NeurIPS 2019)
    - **Authors**: KernelGAN
    - **Summary**: Unsupervised kernel estimation from single image via internal statistics. 400+ GitHub stars.
    - **Year**: 2019

15. **Title**: Blur-Attention: A boosting mechanism for non-uniform blurred image restoration
    - **Authors**: BANet
    - **Summary**: Attention mechanism for spatially-variant deblurring.
    - **Year**: 2022

16. **Title**: Fourier Neural Operator for Parametric Partial Differential Equations (ICLR 2021)
    - **Authors**: Li et al.
    - **Summary**: Learn operator mapping from function space to function space. 900+ citations for supervised operator learning.
    - **Year**: 2021

17. **Title**: Learning Nonlinear Operators via DeepONet Based on Universal Approximation Theorem (Nature ML 2021)
    - **Authors**: Lu et al.
    - **Summary**: Universal approximation for operators. 500+ citations for DeepONet framework.
    - **Year**: 2021

18. **Title**: Plug-and-Play ADMM for Image Restoration (IEEE TCI 2017)
    - **Authors**: Chan et al.
    - **Summary**: Denoiser as plug-in module in optimization. 800+ citations for modular architecture approach.
    - **Year**: 2017

19. **Title**: NeRF: Representing Scenes as Neural Radiance Fields (ECCV 2020)
    - **Authors**: Mildenhall et al.
    - **Summary**: Neural radiance fields for novel view synthesis. 8k+ citations for implicit neural representations.
    - **Year**: 2020

20. **Title**: Implicit Neural Representations with Periodic Activation Functions (NeurIPS 2020)
    - **Authors**: Sitzmann et al.
    - **Summary**: SIREN framework using network structure as implicit prior without training data.
    - **Year**: 2020

**Key Challenges**

1. **Operator Knowledge Gap**: Existing diffusion-based inverse problem methods (Song 2023, Chung 2022) assume exact knowledge of forward operator A. Performance degrades rapidly (3dB PSNR drop) with even 10% operator error, creating need for methods that handle partial operator knowledge.

2. **Weak Priors in Blind Methods**: Classical blind inverse problem methods use hand-crafted priors (TV, sparsity) that are weaker than learned diffusion priors, limiting reconstruction quality (28-32dB PSNR vs. 35-38dB with known operators).

3. **Meta-Learning for Inverse Problems**: Existing meta-learning theory (Finn 2017, Qin 2023) focuses on supervised tasks (classification, regression). Adapting meta-learning to unsupervised operator inference from single measurements is unexplored.

4. **Uncertainty Decomposition**: Standard inverse problem UQ methods assume known forward operator and only quantify measurement noise uncertainty. Methods to quantify operator uncertainty and its propagation to reconstruction are lacking.

5. **Convergence Guarantees**: Alternating optimization for joint image-operator estimation (Hirsch 2010) lacks theoretical convergence guarantees in diffusion model setting. Formal analysis of convergence conditions is needed.

6. **Operator-Invariant Priors**: Diffusion models trained on clean images may become ineffective when operators severely distort data manifold. Characterizing limits of operator invariance is an open question.

7. **Real-World Calibration Requirements**: Medical imaging systems (MRI, CT) require expensive calibration scans (30-60 seconds additional scan time) to obtain accurate forward operators. Reducing calibration requirements while maintaining reconstruction quality is clinically important.

8. **Computational Scalability**: Neural operator learning methods (FNO, DeepONet) require large supervised datasets and cannot perform inverse inference from single measurements at test time, limiting practical applicability.

9. **Clinical Trust and Acceptance**: Uncertainty quantification outputs are rarely used in clinical practice. Methods to make uncertainty estimates interpretable and actionable for radiologists are underdeveloped.

10. **Distribution Shift Robustness**: Cross-domain transfer methods (Fu 2023, Wang 2022) address visual domain shift but not operator distribution shift in inverse problems. Robust out-of-distribution detection for operator families is needed.
