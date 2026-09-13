## Related Work

**Related Papers**
1. **Title**: A global geometric framework for nonlinear dimensionality reduction (Isomap)
   - **Authors**: Tenenbaum, J. B., De Silva, V., & Langford, J. C.
   - **Summary**: Introduces Isomap, a geodesic distance-preserving manifold embedding technique via shortest-path graph distances, providing foundational approach for nonlinear dimensionality reduction.
   - **Year**: 2000

2. **Title**: Topology and data (Persistent Homology)
   - **Authors**: Carlsson, G.
   - **Summary**: Establishes topological data analysis framework for detecting multi-scale structural features (holes, connected components) using persistent homology and persistence diagrams.
   - **Year**: 2009

3. **Title**: Geometric deep learning: Going beyond Euclidean data
   - **Authors**: Bronstein, M. M., Bruna, J., LeCun, Y., Szlam, A., & Vandergheynst, P.
   - **Summary**: Survey on geometry-based neural network analysis including graph neural networks, manifold learning, and symmetry exploitation, establishing theoretical foundation for coordinate-free analysis.
   - **Year**: 2017

4. **Title**: BackdoorBox
   - **Authors**: Li et al.
   - **Summary**: CV-focused backdoor defense toolkit with multiple methods (Fine-Pruning, Neural Cleanse, Spectral Signatures) providing modular defender base class for unified evaluation. Reported TPR: 0.85-0.92.
   - **Year**: 2022

5. **Title**: Unified evaluation of textual backdoor learning: Frameworks and benchmarks (OpenBackdoor)
   - **Authors**: Cui, G., et al.
   - **Summary**: NLP backdoor defense toolkit featuring ONION detector using outlier detection on token embeddings with pre-tune and post-tune defense modes. Reported TPR: 0.88-0.94, FPR: 0.06-0.12.
   - **Year**: 2022

6. **Title**: Backdoor defense via decoupling the training process (Random-Shuffling)
   - **Authors**: Huang, K., et al.
   - **Summary**: Clean-data-free backdoor detection for CV domain via randomized channel shuffling, exploiting sensitivity of backdoor neurons to channel permutations. Reported TPR: 0.79-0.86.
   - **Year**: 2022

7. **Title**: ULRL (Unlearning-Relearning for Backdoor Removal)
   - **Authors**: Not specified
   - **Summary**: Backdoor removal technique using few clean samples (10-100) through two phases: unlearning identifies suspicious neurons via weight perturbation, relearning reinitializes them via weight shifting. Demonstrates backdoor neuron specialization through weight clustering analysis.
   - **Year**: 2023

8. **Title**: Internal consistency regularization for LLM backdoor elimination (CROW)
   - **Authors**: Min, N. M.
   - **Summary**: LLM backdoor defense via consistency regularization exploiting semantic consistency between clean and perturbed inputs, demonstrating backdoor neurons violate consistency. Reported TPR: 0.87-0.93.
   - **Year**: 2025

9. **Title**: Backdoor Secrets Unveiled
   - **Authors**: Not specified
   - **Summary**: Backdoor detection WITHOUT clean data via neuron activation analysis, demonstrating backdoor models contain neurons with >90% activation correlation with triggers. Provides direct evidence for backdoor neuron specialization.
   - **Year**: 2024

10. **Title**: Multi-Domain Backdoor Review
   - **Authors**: Not specified
   - **Summary**: First comprehensive backdoor survey covering CV/NLP/audio/video domains, identifying domain-specific approaches dominate with no unified framework existing. Provides taxonomy of backdoor attacks across domains.
   - **Year**: 2024

11. **Title**: FL Backdoor Survey
   - **Authors**: Not specified
   - **Summary**: Comprehensive federated learning backdoor taxonomy covering attack phases, threat models, and defenses. Demonstrates FL backdoor attacks manifest at gradient level distinct from CV pixel-level and NLP token-level attacks.
   - **Year**: 2023

12. **Title**: Mitigating backdoor attack by injecting proactive defensive backdoor (Proactive_Defensive_Backdoor)
   - **Authors**: Kui, S.
   - **Summary**: Proactive defense paradigm via defensive backdoor injection (counter-backdoor that neutralizes malicious backdoor), representing shift from reactive detection to proactive prevention at training time.
   - **Year**: 2024

13. **Title**: Certified sample-specific backdoor defense via randomized noise (Cert-SSB)
   - **Authors**: Not specified
   - **Summary**: Certified sample-specific backdoor defense using sample-specific noise injection with certified radius computation, similar to randomized smoothing for adversarial robustness. Provides formal certification rather than empirical detection.
   - **Year**: 2025

14. **Title**: TextGuard
   - **Authors**: Not specified
   - **Summary**: Provable defense against NLP backdoor attacks via certified word substitution bounds using randomized token replacement and certification via Lipschitz continuity, demonstrating feasibility of formal guarantees for backdoor defense.
   - **Year**: Not specified

15. **Title**: FLIP: A provable defense framework for backdoor mitigation in federated learning
   - **Authors**: Zhang, K., et al.
   - **Summary**: Provable FL backdoor defense framework with formal guarantees using gradient clipping and certified aggregation bounds. Best Paper Award at ECCV'22 AROW Workshop.
   - **Year**: 2023

16. **Title**: FedDefender
   - **Authors**: Not specified
   - **Summary**: FL-specific backdoor defense using gradient norm analysis for detecting malicious clients, requiring centralized server for aggregation. Reported TPR: 0.81-0.89, FPR: 0.05-0.11.
   - **Year**: 2021

17. **Title**: Neural Cleanse
   - **Authors**: Not specified
   - **Summary**: CV backdoor detection via trigger inversion technique that reconstructs potential triggers through optimization, providing interpretable trigger visualization. Reported TPR: 0.82-0.89. Slow with CV-only applicability.
   - **Year**: 2019

18. **Title**: Data-free_Backdoor
   - **Authors**: Not specified
   - **Summary**: Zero clean data backdoor detection for CV domain achieving lower accuracy trade-off for scenarios without clean validation data. Reported TPR: 0.76-0.84, FPR: 0.08-0.14.
   - **Year**: 2023

**Key Challenges**
1. **Domain-Specific Detection Methods**: Current backdoor detection methods are domain-specific (separate toolkits for CV, NLP, FL), requiring organizations to implement and maintain multiple codebases with significant development and training costs.

2. **Clean Data Dependency**: Most state-of-the-art detection methods require clean validation data for training or calibration, limiting applicability in scenarios where clean data is unavailable or scarce.

3. **Lack of Unified Framework**: No existing framework provides consistent backdoor detection performance across multiple domains (CV, NLP, FL) with domain-invariant principles.

4. **High False Positive Rates**: Several methods exhibit high false positive rates (e.g., OpenBackdoor ONION: FPR 0.06-0.12), limiting practical deployment for model auditing.

5. **Computational Constraints for Real-Time**: Existing methods face computational complexity challenges (O(N²)-O(N³)) making them unsuitable for real-time per-inference detection in high-throughput systems.

6. **Threshold Generalization**: Detection thresholds learned from one architecture family may not generalize to dissimilar families, requiring recalibration for different network architectures.

7. **Stealthy Backdoors**: Adaptive attacks that intentionally minimize detection signatures (e.g., low-curvature triggers, frequency-domain triggers, semantic-preserving triggers) may evade detection methods.

8. **Lack of Formal Certification**: Most methods provide empirical detection metrics (TPR/FPR) but not formal guarantees or mathematical robustness certification required for regulated domains (medical AI, financial AI).

9. **Limited Cross-Domain Consistency**: Detection accuracy variance across domains remains high (10-15%) with existing methods, limiting reliability for multi-domain deployments.

10. **Manifold Embedding Quality**: For geometry-based approaches, manifold reconstruction quality (measured by residual variance) directly impacts detection accuracy, with degradation occurring when embedding quality is insufficient.
