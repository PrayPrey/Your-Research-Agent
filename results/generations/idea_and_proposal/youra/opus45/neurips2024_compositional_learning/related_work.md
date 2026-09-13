## Related Work

**Related Papers**
1. **Title**: Human-like systematic generalization through a meta-learning neural network (Nature 2023)
   - **Authors**: Lake, Baroni
   - **Summary**: Demonstrates that MLC (Meta-Learning for Compositionality) achieves human-like systematicity through dynamic compositional task streams, establishing state-of-the-art performance on SCAN and COGS benchmarks.
   - **Year**: 2023

2. **Title**: Position: Categorical Deep Learning is an Algebraic Theory of All Architectures (arXiv:2402.15332)
   - **Authors**: Gavranovic, Lessard, Dudzik, von Glehn, Araújo, Veličković
   - **Summary**: Proposes that category theory provides a universal framework for neural architectures, demonstrating that functors preserve compositional structure across different representations.
   - **Year**: 2024

3. **Title**: Neural Language of Thought Models (arXiv:2402.01203)
   - **Authors**: Wu, Lee, Ahn
   - **Summary**: Introduces object-centric VQ-VAE that extracts hierarchical composable representations to enable compositional generalization in neural systems.
   - **Year**: 2024

4. **Title**: TripletCLIP
   - **Authors**: Not specified
   - **Summary**: Addresses vision-language compositional reasoning through the use of synthetic negatives, serving as a baseline for compositional generalization in the vision domain.
   - **Year**: 2024

5. **Title**: MLC-ML (brendenlake/MLC-ML)
   - **Authors**: Not specified
   - **Summary**: Official implementation of MLC for SCAN and COGS benchmarks, serving as the primary comparison baseline for compositional generalization in the NLP domain.
   - **Year**: Not specified

6. **Title**: COGS: A Compositional Generalization Challenge
   - **Authors**: Kim, Linzen
   - **Summary**: Introduces a benchmark demonstrating that standard transformers achieve only 16-35% generalization accuracy, highlighting significant limitations in compositional generalization capabilities.
   - **Year**: 2020

7. **Title**: Are Neural Nets Modular?
   - **Authors**: Csordás, van Steenkiste, Schmidhuber
   - **Summary**: Investigates modularity in neural networks and finds that they fail to reuse submodules effectively, providing motivation for explicit functorial constraints in network design.
   - **Year**: 2020

**Key Challenges**
1. **Poor Compositional Generalization in Standard Architectures**: Standard transformers achieve only 16-35% generalization on compositional benchmarks like COGS, demonstrating a significant gap between neural network performance and human-like systematic generalization.

2. **Lack of Modular Reuse**: Neural networks fail to reuse learned submodules when encountering novel compositions, limiting their ability to generalize compositionally to unseen combinations of known primitives.

3. **Absence of Structure-Preserving Mechanisms**: Current architectures lack explicit mechanisms to preserve compositional structure across transformations, motivating the need for functorial constraints that maintain algebraic relationships between representations.
