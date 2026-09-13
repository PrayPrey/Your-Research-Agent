## Related Work

**Related Papers**
1. **Title**: Orthogonal neural codes for compositional memory in prefrontal cortex
   - **Authors**: Park, Holmes, Snyder
   - **Summary**: Demonstrates that spatial memory representations are preserved across tasks using orthogonal subspace encoding, with task identity encoded in orthogonal subspaces, providing the primary mechanism for compositional memory organization.
   - **Year**: 2025

2. **Title**: An explainable transformer circuit for compositional generalization
   - **Authors**: Tang, Lake, Jazayeri
   - **Summary**: Identifies compositional induction circuits in transformers using disentangled token representations, supporting the feasibility of implementing geometric constraints in transformer architectures.
   - **Year**: 2025

3. **Title**: Human-like systematic generalization through meta-learning neural network
   - **Authors**: Lake, Baroni
   - **Summary**: Demonstrates that MLC achieves human-like systematicity and flexibility through meta-learning optimization, establishing that neural networks can achieve compositionality and providing a baseline for compositional generalization.
   - **Year**: 2023

4. **Title**: GameBench: Evaluating Strategic Reasoning in LLMs
   - **Authors**: Costarelli et al.
   - **Summary**: Reveals that GPT-4 performs worse than random on novel games, providing an evaluation framework for assessing strategic reasoning capabilities in language models.
   - **Year**: 2024

5. **Title**: MIRAGE: A Neuroscience-Inspired Dual-Process Model (arXiv:2507.18868)
   - **Authors**: Noviello, Beger, Groner, Ellis, Sun
   - **Summary**: Demonstrates that dual-process neuroscience-to-deep-learning transfer achieves over 99% accuracy on SCAN benchmarks, validating neuroscience-inspired architectural approaches for compositional tasks.
   - **Year**: 2025

6. **Title**: OSF/PSOFT
   - **Authors**: Not specified
   - **Summary**: Successfully implements orthogonality constraints in 7B parameter transformers for continual learning, proving the implementation feasibility of orthogonal subspace methods at scale.
   - **Year**: 2025

7. **Title**: Measuring Compositional Generalization (arXiv:1912.09713)
   - **Authors**: Keysers et al.
   - **Summary**: Introduces compound divergence methodology for creating systematic compositional generalization benchmarks, providing principled approaches for evaluating compositional capabilities.
   - **Year**: 2020

8. **Title**: Compositional generalization through meta sequence-to-sequence learning
   - **Authors**: Lake
   - **Summary**: Shows that memory-augmented networks improve compositional generalization but evaluates only on synthetic benchmarks, highlighting limitations in testing scope.
   - **Year**: 2019

9. **Title**: Curriculum learning for human compositional generalization
   - **Authors**: Dekker et al.
   - **Summary**: Demonstrates that training curriculum has greater impact than architecture choice for achieving compositionality, informing training procedure design for compositional systems.
   - **Year**: 2022

**Key Challenges**
1. **Synthetic-to-Open-World Gap**: Existing compositional generalization methods have been tested primarily on synthetic benchmarks, leaving a significant gap in understanding performance on open-world, real-world tasks.

2. **Novel Task Generalization Failure**: State-of-the-art large language models like GPT-4 perform worse than random on novel games, indicating fundamental limitations in strategic reasoning and compositional transfer to unseen scenarios.

3. **Scalable Orthogonality Implementation**: While orthogonal subspace methods show promise in neuroscience and smaller models, implementing these constraints effectively in large-scale transformers remains an engineering and theoretical challenge.

4. **Architecture vs. Training Trade-offs**: Evidence suggests training curriculum may matter more than architectural choices for compositionality, creating uncertainty about optimal design priorities for compositional systems.

5. **Compositional Representation Disentanglement**: Achieving properly disentangled token representations that support compositional induction circuits in transformers requires careful geometric constraints that are not yet standard practice.
