## Related Work

**Related Papers**
1. **Title**: HE-LRM: Encrypted Deep Learning Recommendation Models using Fully Homomorphic Encryption (Garimella et al., 2025)
   - **Authors**: Garimella et al.
   - **Summary**: Achieved 77× speedup via embedding compression with 24-489s latency on DLRM for encrypted deep learning recommendation models. Uses uniform encryption parameters across all layers.
   - **Year**: 2025
   - **Identifier**: Semantic Scholar ID: 457f8af2d170f0e782c0e51bed213041163d61e3

2. **Title**: Development of Privacy-preserving Deep Learning with Homomorphic Encryption: Kidney CT Imaging (Lee et al., 2025)
   - **Authors**: Lee et al.
   - **Summary**: Demonstrated 50 min CPU to 90s GPU acceleration for encrypted CT classification using homomorphic encryption, achieving AUC 0.99 to 0.97 with minimal accuracy loss (<2%).
   - **Year**: 2025
   - **Identifier**: Semantic Scholar ID: c63f3cd27a8f3582aeec4d21d49f3c40733da17e

3. **Title**: Touch of Privacy: Homomorphic Encryption-Powered Deep Learning for Fingerprint Authentication (Sumalatha et al., 2025)
   - **Authors**: Sumalatha et al.
   - **Summary**: Proved FHE can achieve real-time performance (0.025s) for simple operations like encrypted fingerprint comparison using simple CNN architectures.
   - **Year**: 2025
   - **Identifier**: Semantic Scholar ID: 44f47d1c0ff5c5d91b3ffb64ccb6d3b098481031

4. **Title**: Opacus: Differential Privacy for PyTorch (Meta, 2019)
   - **Authors**: Meta (formerly Facebook AI Research)
   - **Summary**: Framework providing per-sample gradient clipping, privacy budget allocation, and noise injection for differential privacy in PyTorch models. Demonstrates resource allocation pattern for privacy budgets per sample.
   - **Year**: 2019
   - **Identifier**: https://github.com/meta-pytorch/opacus

5. **Title**: How to DP-fy ML: A Practical Guide to Machine Learning with Differential Privacy (Ponomareva et al., Google, 2023)
   - **Authors**: Ponomareva et al.
   - **Summary**: Comprehensive differential privacy implementation guide for machine learning with 243 citations, demonstrating trade-offs between privacy and utility via noise injection.
   - **Year**: 2023
   - **Identifier**: Semantic Scholar ID: 5b0f2ff37a977fd4b0c845b27726b65682bf8ac6

6. **Title**: ML Privacy Meter (Murakonda & Shokri, 2020)
   - **Authors**: Murakonda & Shokri
   - **Summary**: Tool for GDPR Article 35 Data Protection Impact Assessment (DPIA) that quantifies membership inference attack risk with 99 citations. Used for empirical privacy evaluation.
   - **Year**: 2020
   - **Identifier**: Semantic Scholar ID: 2a63d18efaee5f61a7083d548dacdb5ada979de4

7. **Title**: TenSEAL (OpenMined, 2020)
   - **Authors**: OpenMined
   - **Summary**: CKKS/BFV tensor operations framework with NumPy-like API providing parameter tuning support for homomorphic encryption, serving as primary implementation framework for FHE-ML research.
   - **Year**: 2020
   - **Identifier**: https://github.com/OpenMined/TenSEAL

8. **Title**: Concrete ML (Zama, 2022)
   - **Authors**: Zama
   - **Summary**: TFHE-based framework with scikit-learn/PyTorch integration providing FHE-optimized operations and model conversion capabilities for privacy-preserving machine learning.
   - **Year**: 2022
   - **Identifier**: https://github.com/zama-ai/concrete-ml

**Key Challenges**
1. **Computational Feasibility of FHE for Real-Time ML Inference at Scale**: Current state-of-the-art achieves 24s minimum latency (HE-LRM) or 90s GPU latency (Kidney CT), which is too slow for real-time applications requiring <1 second response times. No prior work explores layer-wise precision adaptation in FHE neural networks.

2. **Uniform Encryption Parameters Limitation**: Existing FHE-ML implementations (HE-LRM, TenSEAL, Concrete ML) treat encryption parameters as global hyperparameters selected once during setup, without considering heterogeneous allocation based on layer-specific privacy-accuracy-latency trade-offs.

3. **Noise Accumulation in Deep Networks**: Very deep networks (>12 layers) may require frequent bootstrapping operations to refresh noise budgets, with each bootstrapping adding ~10s overhead per inference according to TenSEAL benchmarks, potentially negating speedup gains.

4. **Privacy Validation Gap**: Lack of formal proofs that variable precision preserves semantic security in FHE neural networks. Current approaches rely on empirical membership inference attack (MIA) testing rather than theoretical guarantees.

5. **Plaintext-Encrypted Sensitivity Correlation Uncertainty**: Unvalidated assumption that layer sensitivity rankings computed on plaintext models via gradient analysis transfer accurately to encrypted models, as encrypted gradient computation is expensive.

6. **Limited Real-Time Application Deployment**: Current FHE-ML latency (24-489 seconds) prevents deployment in production scenarios requiring 5-15 second response times such as medical diagnosis decision support, fraud detection with alert windows, and personalized recommendation serving.

7. **Trade-off Between Privacy Mechanisms**: Differential privacy protects aggregate statistics but not individual inferences, Trusted Execution Environments (TEE) provide near-native speed but are vulnerable to side-channel attacks, and Secure Multi-Party Computation requires multi-party setup complexity compared to two-party client-server models.

8. **Hardware Dependency and Accessibility**: Practical FHE-ML performance requires GPU acceleration (NVIDIA A100/V100 class), with CPU-only deployment being 30-100× slower, creating computational inequity for resource-constrained organizations.

9. **Cross-Domain Methodology Transfer Gap**: Limited application of optimization patterns from related domains (Level-of-Detail rendering from graphics, Adaptive QoS management from real-time systems) to FHE-ML resource allocation problems.

10. **Scalability and Generalization Uncertainty**: Unclear whether adaptive precision techniques maintain advantages at billion-sample scale or extend effectively to very deep transformers (>24 layers) and unstructured data processing without pre-trained embeddings.
