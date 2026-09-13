## Related Work

**Related Papers**

1. **Title**: Neural Fields in Robotics: A Survey (Irshad et al.)
   - **Authors**: Irshad et al.
   - **Summary**: Comprehensive survey reviewing 200+ robotics papers, demonstrating consistent patterns where encoding modules adapt for SE(3)-equivariance (domain-specific), backbone modules (SIREN, ReLU MLP) remain unchanged (domain-invariant), and loss modules adapt for manipulation metrics (domain-specific).
   - **Year**: 2024
   - **Citations**: 20
   - **Identifier**: SS ID: 15a0767449238a0d4481e3ce0ed8faebf266cbd4

2. **Title**: PhyRecon: Physically Plausible Neural Scene Reconstruction (Ni et al.)
   - **Authors**: Ni et al.
   - **Summary**: Demonstrates physics applications that keep encoding (positional encoding) and backbone (NeRF MLP) from vision domain while adapting loss module (adding PDE residual terms) and conditioning module (differentiable physics parameters) to incorporate physical constraints.
   - **Year**: 2024
   - **Citations**: 27
   - **Identifier**: SS ID: ce1e604fb2ec79f25adb7f6a96cc52c5fc56d8cc

3. **Title**: Attention Beats Concatenation for Conditioning Neural Fields (Rebain et al.)
   - **Authors**: Rebain et al.
   - **Summary**: Empirical comparison showing attention-based conditioning outperforms concatenation for high-dimensional conditioning (>64D), while concatenation is acceptable for low-dimensional (<64D), providing explicit adaptation rules with thresholds.
   - **Year**: 2022
   - **Citations**: 25
   - **Identifier**: SS ID: 2ea820473b4a232e196f7bd874f5b9605d194a65

4. **Title**: Mixture of neural fields for heterogeneous reconstruction in cryo-EM (Levy et al.)
   - **Authors**: Levy et al.
   - **Summary**: Biology domain (Cryo-EM protein reconstruction) work that adapts decoder module with mixture model components to handle compositional/conformational heterogeneity, while keeping standard coordinate encoding and SIREN backbone unchanged.
   - **Year**: 2024
   - **Citations**: 4
   - **Identifier**: SS ID: 50687a158c0a7b4fae975312b718a003e3c486fe

5. **Title**: Scalable spatiotemporal prediction with Bayesian neural fields (Saad et al.)
   - **Authors**: Saad et al.
   - **Summary**: Framework for temperature and precipitation forecasting using Bayesian neural fields with spatiotemporal coordinate encoding, variational inference for uncertainty quantification, and covariate conditioning for climate applications.
   - **Year**: 2024
   - **Citations**: 23
   - **Identifier**: SS ID: 29d16e00da123029e3b0ecc309bf1d07d44e89b7

6. **Title**: Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields (Barron et al.)
   - **Authors**: Barron et al.
   - **Summary**: Establishes vision domain baseline for neural radiance fields with integrated positional encoding (mip-mapping for anti-aliasing), achieving 30-35 dB PSNR on standard benchmarks for novel view synthesis and 3D scene reconstruction.
   - **Year**: 2021
   - **Citations**: 2271
   - **Identifier**: SS ID: ec90ffa017a2cc6a51342509ce42b81b478aefb3

7. **Title**: 3DShape2VecSet: A 3D Shape Representation for Neural Fields and Generative Diffusion Models (Zhang et al.)
   - **Authors**: Zhang et al.
   - **Summary**: Novel shape representation combining neural fields with set-based vectors, demonstrating that domain-appropriate decoder design for shape generation achieves high-quality 3D generation outperforming generic neural field decoders.
   - **Year**: 2023
   - **Citations**: 352
   - **Identifier**: SS ID: eb35863662544c977780299c21e669555ae83e81

8. **Title**: Neural Descriptor Fields: SE(3)-Equivariant Object Representations for Manipulation (Simeonov et al.)
   - **Authors**: Simeonov et al.
   - **Summary**: Robotics manipulation baseline using SE(3)-equivariant encoder custom-designed for robotics manipulation symmetries, combined with SIREN backbone and contrastive loss for descriptor learning, achieving 85-90% success rate on YCB object manipulation tasks.
   - **Year**: Not specified
   - **Repository**: anthonysimeonov/ndf_robot (214★)

9. **Title**: NTFields - Neural Temporal Fields (Implementation)
   - **Authors**: Not specified
   - **Summary**: Physics-informed temporal neural fields implementation that adds physics constraint terms to loss module while preserving encoding (Fourier features) and backbone (MLP), demonstrating systematic addition of domain-specific components following PDE residual augmentation rules.
   - **Year**: Not specified
   - **Repository**: ruiqini/NTFields (26★)

10. **Title**: GINR-IPC - Instance Pattern Composers (Implementation)
    - **Authors**: kakaobrain
    - **Summary**: Modular architecture where encoding, conditioning, and decoder components adapt independently based on task requirements, achieving CVPR 2023 Highlight recognition for generalization performance and demonstrating module independence.
    - **Year**: 2023
    - **Repository**: kakaobrain/ginr-ipc

11. **Title**: NeuralFeels - Visuo-tactile Perception (Implementation)
    - **Authors**: Facebook Research
    - **Summary**: Visuo-tactile perception for in-hand manipulation using multi-modal conditioning (domain-specific for robotics sensor fusion), achieving task success rates comparable to custom vision-only or tactile-only solutions.
    - **Year**: Not specified
    - **Repository**: facebookresearch/neuralfeels

12. **Title**: DeepXDE Framework
    - **Authors**: Not specified
    - **Summary**: Physics-Informed Neural Networks (PINNs) framework for solving PDEs (heat equation, Burgers equation) using neural fields with PDE residual loss augmentation, serving as standard baseline for physics domain applications.
    - **Year**: Not specified
    - **Repository**: https://deepxde.readthedocs.io

13. **Title**: Neural Jacobian Field (Implementation)
    - **Authors**: Sizhe Li
    - **Summary**: Implementation demonstrating neural field applications with Jacobian-based representations for robotics and deformation modeling.
    - **Year**: Not specified
    - **Repository**: sizhe-li/neural-jacobian-field

14. **Title**: Shacira (Implementation)
    - **Authors**: Sharath Girish
    - **Summary**: Neural field implementation resource demonstrating practical applications of modular architecture design.
    - **Year**: Not specified
    - **Repository**: Sharath-girish/Shacira

**Key Challenges**

1. **Lack of Cross-Domain Transfer Guidelines**: Absence of systematic frameworks for transferring neural field architectures across domains (robotics, physics, biology, climate, vision), forcing practitioners to rely on ad-hoc trial-and-error approaches requiring extensive domain expertise and ≥10 design iterations.

2. **Module Adaptation Complexity**: Difficulty identifying which architecture components (encoding, backbone, conditioning, decoder, loss) should be domain-specific versus domain-invariant when transferring from vision to new domains, without clear adaptation rules.

3. **Domain Property Characterization**: Lack of standardized schema for characterizing domain properties (input structure, symmetries, data characteristics, constraints) that determine architecture requirements, making systematic transfer infeasible.

4. **Confidence Calibration for Adaptation Rules**: Absence of validated confidence scores for architecture adaptation patterns, preventing practitioners from distinguishing high-confidence systematic rules from emerging patterns with limited empirical support.

5. **Performance-Efficiency Trade-off**: Challenge of achieving ≥95% performance parity with custom domain-expert solutions while reducing development iterations by ≥50% through systematic frameworks versus ad-hoc approaches.

6. **Evaluation Metric Heterogeneity**: Inconsistency in using domain-appropriate evaluation metrics (PSNR/SSIM for vision insufficient for robotics manipulation success rates, physics PDE residuals, biology structural validity, climate RMSE), complicating cross-domain performance comparison.

7. **Scalability and Generalization**: Uncertainty about framework validity when extending beyond initial 5 validated domains (robotics, physics, biology, climate, vision) to new domains with different property profiles or when neural field architectures evolve beyond current paradigms.

8. **Modular Independence Assumption**: Risk that strong module interactions (e.g., equivariant encoding with standard loss producing degenerate solutions, physics-informed loss with standard backbone failing to capture high-frequency details) may violate assumed module separability.
