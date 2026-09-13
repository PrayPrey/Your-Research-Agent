## Related Work

**Related Papers**
1. **Title**: GNN-SCM ([Zecevic 2021])
   - **Authors**: Zecevic et al.
   - **Summary**: Demonstrates that neural attention mechanisms can represent causal structure, proving neural networks CAN encode causal effects. Provides foundational evidence for using attention-based architectures in causal discovery.
   - **Year**: 2021
   - **Citations**: 67 citations

2. **Title**: CausalVAE ([Yang 2020])
   - **Authors**: Yang et al.
   - **Summary**: Introduces VAE with separate causal layer for DAG-based discovery, demonstrating that staged approaches (encoder → causal layer) work but have limitations. Serves as baseline for causal representation learning methods.
   - **Year**: 2020
   - **Citations**: 345 citations

3. **Title**: Invariance Principle ([Yao 2024])
   - **Authors**: Yao et al.
   - **Summary**: Provides theoretical basis for multi-view identifiability in causal representation learning, supporting the use of multi-head attention as multiple views for learning causal structures without interventions.
   - **Year**: 2024
   - **Citations**: 22 citations

4. **Title**: Vision Transformer (ViT) ([Dosovitskiy 2020])
   - **Authors**: Dosovitskiy et al.
   - **Summary**: Foundational architecture demonstrating that pure attention mechanisms can achieve 81.0% ImageNet accuracy. Establishes that attention weights can represent relationship strengths between tokens.
   - **Year**: 2020

5. **Title**: Asymmetric Masking Validation ([Zheng & Liu 2025])
   - **Authors**: Zheng and Liu
   - **Summary**: Validates that asymmetric masks in attention mechanisms can encode directional flow, achieving 15.3% improvement in causal structure learning tasks.
   - **Year**: 2025
   - **Citations**: 16 citations

6. **Title**: ENCO: Differentiable DAG Penalty Implementation ([phlippe/ENCO])
   - **Authors**: Not specified
   - **Summary**: Provides scalable implementation of differentiable DAG penalty constraints, demonstrated to work with approximately 100 nodes, enabling practical enforcement of acyclicity in neural networks.
   - **Year**: Not specified
   - **GitHub Stars**: 88 stars

7. **Title**: Sparsity Principle ([Xu 2024])
   - **Authors**: Xu et al.
   - **Summary**: Establishes theoretical and empirical basis for using L1 sparsity regularization to select true causal edges in learned graph structures, supporting sparse causal edge discovery.
   - **Year**: 2024
   - **Citations**: 22 citations

8. **Title**: Head Specialization in Transformers ([Voita 2019])
   - **Authors**: Voita et al.
   - **Summary**: Demonstrates that transformer attention heads naturally specialize for different functions, supporting the hybrid architecture approach where different heads can serve global context versus causal structure learning roles.
   - **Year**: 2019

9. **Title**: Post-hoc Granger Causality ([Mahesh 2024])
   - **Authors**: Mahesh et al.
   - **Summary**: Applies Granger causality analysis to transformer attention weights post-training, representing the current state of separate post-hoc causal analysis rather than integrated causal learning.
   - **Year**: 2024

10. **Title**: PC/FCI Algorithms (causal-learn library)
    - **Authors**: Not specified
    - **Summary**: Classical constraint-based algorithms for causal graph recovery, serving as traditional baselines for DAG structure discovery in causal discovery literature.
    - **Year**: Not specified

11. **Title**: ConvNeXt-XL
    - **Authors**: Not specified
    - **Summary**: State-of-the-art vision model achieving 87.8% ImageNet accuracy, representing current performance benchmarks (not targeted by this research).
    - **Year**: Not specified

12. **Title**: ViT-22B
    - **Authors**: Not specified
    - **Summary**: Large-scale vision transformer achieving 90.5% ImageNet accuracy, representing state-of-the-art performance (not targeted by this research).
    - **Year**: Not specified

**Key Challenges**
1. **Limited Integration with Foundation Model Architectures**: 60% of current causal representation learning (CRL) methods are VAE-based and 25% are flow-based, making them incompatible with transformer architectures. Minimal work exists on integrating CRL directly into transformers.

2. **Separate Module Architecture Limitations**: Current approaches like CausalVAE use staged architectures with separate encoder and causal layer modules, limiting the integration between task performance and causal structure learning.

3. **Lack of Neuroscience-Inspired Constraints**: Existing methods do not leverage neuroscience principles such as directed transfer functions (dDTF) and generalized partial directed coherence (gPDC) for encoding causal directionality in neural attention mechanisms.

4. **Global Context vs. Causal Sparsity Tension**: Transformers rely on full attention for global context, while causal discovery requires sparse, directed edge selection, creating a fundamental architectural tension.

5. **Empirical vs. Provable Identifiability**: Current methods lack clear pathways to achieve identifiable causal representations without costly interventional data, limiting their theoretical guarantees.

6. **Post-hoc vs. Integrated Causal Learning**: Existing approaches apply causal analysis to pre-trained models post-hoc rather than learning causal structures jointly with task objectives during training.

7. **Scalability to High-Dimensional Tokens**: Classical causal discovery algorithms (PC, FCI) and some neural methods face computational challenges scaling to transformer token sequences (256-1024+ tokens).

8. **Evaluation of Counterfactual Quality**: Limited established methods exist for evaluating the quality of counterfactual reasoning in learned causal representations on real-world visual data without ground-truth causal graphs.
