## Related Work

**Related Papers**
1. **Title**: VLG-CBM: Training Concept Bottleneck Models with Vision-Language Guidance (arXiv:2408.01432)
   - **Authors**: Srivastava, Yan, Weng
   - **Summary**: Demonstrates that grounded concept annotation improves ANEC by 4-51% and introduces the NEC (Normalized Explanation Completeness) metric for evaluating concept-based models.
   - **Year**: 2024

2. **Title**: Post-hoc Concept Bottleneck Models (arXiv:2205.15480)
   - **Authors**: Yuksekgonul, Wang, Zou
   - **Summary**: Shows that any neural network can be converted to a Concept Bottleneck Model without sacrificing performance, enabling post-hoc interpretability.
   - **Year**: 2022

3. **Title**: Social semantics: the organization and grounding of abstract concepts
   - **Authors**: Pexman, Diveica, Binney
   - **Summary**: Establishes that abstract concepts are grounded through social interaction and language use, providing theoretical foundation for concept grounding approaches.
   - **Year**: 2021

4. **Title**: Self-explaining SAE features
   - **Authors**: Kharlapenko
   - **Summary**: Proposes post-hoc labeling of SAE features via Patchscopes/SelfIE methods, representing an alternative approach to feature interpretation.
   - **Year**: 2024

5. **Title**: Gemma Scope / Llama Scope
   - **Authors**: Not specified
   - **Summary**: Demonstrates the feasibility of industrial-scale SAE training with 128K+ features, establishing practical scalability of sparse autoencoder approaches.
   - **Year**: 2024

6. **Title**: Toy Models of Superposition
   - **Authors**: Elhage et al.
   - **Summary**: Establishes that polysemanticity in neural networks requires SAE decomposition and that extracted features need proper grounding for interpretability.
   - **Year**: 2022

7. **Title**: Towards Principled Evaluations of Sparse Autoencoders
   - **Authors**: Makelov et al.
   - **Summary**: Identifies that SAE evaluation currently lacks ground-truth benchmarks and argues for NEC-style metrics to enable principled assessment.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Ground-Truth Benchmarks**: SAE evaluation currently lacks established ground-truth benchmarks, making principled assessment of feature quality difficult.
2. **Polysemanticity in Neural Representations**: Neural network features exhibit polysemanticity, requiring decomposition methods like SAEs and subsequent grounding of extracted features.
3. **Post-hoc vs. Integrated Grounding**: Existing approaches rely on post-hoc labeling methods (e.g., Patchscopes/SelfIE) rather than integrated grounding during training.
4. **Abstract Concept Grounding**: Abstract concepts require grounding through social and linguistic contexts, presenting challenges for purely visual or computational approaches.
5. **Scalability of Interpretable Methods**: While industrial-scale SAE training is feasible, maintaining interpretability and concept grounding at scale (128K+ features) remains challenging.
