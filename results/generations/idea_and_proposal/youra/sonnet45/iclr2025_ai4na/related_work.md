## Related Work

**Related Papers**

1. **Title**: Systematic benchmarking of deep-learning methods for tertiary RNA structure prediction (Bahai et al. 2024)
   - **Authors**: Bahai et al.
   - **Summary**: Systematic benchmarking demonstrated that ML methods fail on novel RNA families due to pattern-matching limitations, defining the core problem of limited generalization to out-of-distribution RNA structures.
   - **Year**: 2024

2. **Title**: RNA3DB: A structurally-dissimilar dataset split for training and benchmarking (Szikszai et al. 2024)
   - **Authors**: Szikszai et al.
   - **Summary**: Developed structurally-dissimilar splits required for rigorous generalization testing, providing evaluation framework for assessing out-of-distribution performance on novel RNA families.
   - **Year**: 2024

3. **Title**: Differentiable physics-based energy functions + GNN for protein-ligand binding (Hong et al. 2024)
   - **Authors**: Hong et al.
   - **Summary**: Demonstrated feasibility of integrating differentiable physics energy functions with graph neural networks for protein-ligand binding prediction, validating physics+neural integration and gradient flow.
   - **Year**: 2024

4. **Title**: CParty: Hierarchical constrained partition function for pseudoknots (Trinity et al. 2024)
   - **Authors**: Trinity et al.
   - **Summary**: Extended Turner thermodynamics model to handle pseudoknots through hierarchical partition function with O(n³) computational complexity, making extended RNA thermodynamics tractable.
   - **Year**: 2024

5. **Title**: RNA3D-SSCL: Secondary structure constraints improve tertiary prediction (Lu et al. 2025)
   - **Authors**: Lu et al.
   - **Summary**: Demonstrated that adding secondary structure physics constraints directly improves tertiary structure prediction, providing direct evidence that physics constraints help 3D RNA structure prediction.
   - **Year**: 2025

6. **Title**: Orthogonal meta-component decomposition (Zeng 2025)
   - **Authors**: Zeng
   - **Summary**: Proposed orthogonal component decomposition framework that enables disentangled transferable learning through enforcing orthogonality constraints on meta-learned components.
   - **Year**: 2025

7. **Title**: MetaFold-RNA: Meta-learning for RNA secondary structure prediction (MetaFold-RNA 2025)
   - **Authors**: Not specified
   - **Summary**: Demonstrated applicability of meta-learning to RNA domain for secondary structure (2D) prediction, establishing precedent for RNA structure prediction with few-shot learning approaches.
   - **Year**: 2025

8. **Title**: Model-Agnostic Meta-Learning for Fast Adaptation (Finn et al. 2017, MAML)
   - **Authors**: Finn et al.
   - **Summary**: Introduced episodic meta-learning framework enabling few-shot adaptation through inner-loop fast adaptation and outer-loop meta-optimization, with broad applicability across computer vision, NLP, and reinforcement learning.
   - **Year**: 2017

9. **Title**: DeepFoldRNA: De novo RNA tertiary structure prediction at atomic resolution (Pearce et al. 2022)
   - **Authors**: Pearce et al.
   - **Summary**: Self-attention-based approach with gradient-based folding simulation for RNA tertiary structure prediction, achieving RMSD 2.69Å and TM-score 0.743 as baseline performance.
   - **Year**: 2022

10. **Title**: NuFold: End-to-end approach for RNA tertiary structure prediction (Kagaya et al. 2025)
    - **Authors**: Kagaya et al.
    - **Summary**: End-to-end neural network with flexible nucleobase representation for RNA tertiary structure prediction, achieving TM-score ~0.75 without explicit physics decomposition.
    - **Year**: 2025

11. **Title**: RhoFold+: Language model-based RNA structure prediction
    - **Authors**: Not specified
    - **Summary**: Pre-trained RNA language model approach with structure prediction head for tertiary structure prediction, achieving TM-score ~0.76 through large-scale pre-training.
    - **Year**: Not specified

12. **Title**: M. tuberculosis phase variation mechanisms (Modlin et al. 2025)
    - **Authors**: Modlin et al.
    - **Summary**: Characterized evolutionary phase variation mechanisms with invariant core genes and adaptive regulatory elements (genetic switches), providing conceptual inspiration for separating invariant physics from family-specific adaptation.
    - **Year**: 2025

13. **Title**: Meta-TGLink: Structure-enhanced graph meta-learning for gene regulatory networks (Yu et al. 2025)
    - **Authors**: Yu et al.
    - **Summary**: Applied structure-enhanced graph meta-learning to gene regulatory network prediction, demonstrating meta-learning applicability to biological structure prediction problems.
    - **Year**: 2025

14. **Title**: Few-shot structure-activity relationships: MAML vs ADKF for molecular property prediction (Kötter et al. 2024)
    - **Authors**: Kötter et al.
    - **Summary**: Compared meta-learning approaches (MAML vs ADKF) for few-shot molecular property prediction, showing increasing application of meta-learning to biological domains.
    - **Year**: 2024

15. **Title**: Turner nearest-neighbor thermodynamics model
    - **Authors**: Mathews et al.
    - **Summary**: Empirically validated RNA thermodynamics model with experimental data, providing foundational nearest-neighbor energy parameters for Watson-Crick pairing, stacking interactions, and loop penalties.
    - **Year**: Not specified

16. **Title**: Physics-Informed Neural Networks (PINNs) for sound fields (Olivieri et al. 2024)
    - **Authors**: Olivieri et al.
    - **Summary**: Applied physics-informed neural networks to sound field prediction, demonstrating physics+neural integration in acoustic domain with validated gradient stability.
    - **Year**: 2024

17. **Title**: Physics-Informed Neural Networks (PINNs) for Navier-Stokes equations (Zhang et al. 2025)
    - **Authors**: Zhang et al.
    - **Summary**: Applied PINNs to Navier-Stokes fluid dynamics, showing physics+neural integration increasingly mainstream across domains.
    - **Year**: 2025

18. **Title**: Physics-Informed Neural Networks (PINNs) for wind turbine wakes (Gafoor et al. 2025)
    - **Authors**: Gafoor et al.
    - **Summary**: Applied PINNs to wind turbine wake modeling, validating gradient stability and physics-neural integration for complex physical systems.
    - **Year**: 2025

**Key Challenges**

1. **Limited Generalization to Novel RNA Families**: Current machine learning methods fail on structurally-dissimilar novel RNA families because they learn patterns through interpolation rather than universal physical principles, resulting in poor out-of-distribution generalization (generalization gap typically 0.10-0.15 TM-score).

2. **Data Inefficiency**: Existing methods require extensive retraining with 100+ family-specific examples to adapt to new RNA families, limiting practical applicability to newly discovered or synthetic RNAs with sparse data.

3. **MSA Dependency**: Baseline approaches rely on multiple sequence alignments (MSAs) which are unavailable for novel, synthetic, or engineered RNA molecules, preventing structure prediction for therapeutic RNA design applications.

4. **Physics Model Incompleteness**: Extended RNA thermodynamics models may miss critical tertiary interactions (long-range contacts, non-canonical base pairs), potentially limiting physics-only prediction accuracy.

5. **Tertiary Structure Meta-Learning Validation Gap**: While meta-learning has been demonstrated for RNA secondary structure (2D), applicability to more heterogeneous tertiary structures (3D) remains unproven and may face scalability challenges.

6. **Physics-Neural Integration Complexity**: Differentiable physics+neural integration introduces gradient stability challenges, hyperparameter sensitivity, and implementation complexity requiring careful validation protocols.

7. **Dataset Bias**: RNA structure datasets derived from PDB may not represent full RNA diversity, potentially overestimating real-world generalization performance on truly novel RNAs beyond experimentally solved structures.

8. **Pattern-Matching vs Principle-Learning**: Fundamental limitation where end-to-end black-box approaches learn to interpolate patterns from training data rather than extrapolate using universal physical principles, limiting robustness to distribution shifts.
