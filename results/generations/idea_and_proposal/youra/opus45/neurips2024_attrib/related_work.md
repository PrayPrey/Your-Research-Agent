## Related Work

**Related Papers**
1. **Title**: MIB: A Mechanistic Interpretability Benchmark (ICML 2025)
   - **Authors**: Mueller, Geiger, Wiegreffe et al.
   - **Summary**: Demonstrates synthetic benchmark methodology with ground truth for circuit and causal variable localization; finds DAS outperforms SAE features.
   - **Year**: 2025

2. **Title**: Towards Unified Attribution in Explainable AI, Data-Centric AI, and Mechanistic Interpretability
   - **Authors**: Zhang et al.
   - **Summary**: Proposes unified attribution framework connecting data, mechanistic, and concept attribution; provides conceptual foundation for cross-paradigm evaluation.
   - **Year**: 2025

3. **Title**: CausalGym: Benchmarking Causal Interpretability Methods on Linguistic Tasks (arXiv:2402.12560)
   - **Authors**: Arora, Jurafsky, Potts
   - **Summary**: Adapts SyntaxGym for causal interpretability benchmarking; validates synthetic task approach for linguistic domain.
   - **Year**: 2024

4. **Title**: A Validity-Guided Workflow for Robust Large Language Model Research in Psychology
   - **Authors**: Lin
   - **Summary**: Integrates psychometrics with causal inference; proposes dual-validity framework that scales requirements to research ambition.
   - **Year**: 2025

5. **Title**: DATE-LM: Benchmarking Data Attribution Evaluation for LLMs
   - **Authors**: Jiao et al.
   - **Summary**: Provides data attribution benchmark for LLMs using a single-paradigm approach.
   - **Year**: 2025

6. **Title**: Post-hoc Concept Bottleneck Models (ICLR 2023 Spotlight)
   - **Authors**: Yuksekgonul et al.
   - **Summary**: Demonstrates method to convert any neural network to a Concept Bottleneck Model without performance loss.
   - **Year**: 2022

7. **Title**: Towards Best Practices of Activation Patching
   - **Authors**: Zhang & Nanda
   - **Summary**: Shows that different evaluation metrics and methods produce conflicting rankings; highlights absence of standardized benchmarks.
   - **Year**: 2023

8. **Title**: Universal Neurons in GPT2 Language Models
   - **Authors**: Gurnee et al.
   - **Summary**: Finds that only 1-5% of neurons are universal across seeds; documents the polysemanticity challenge in neural networks.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Unified Evaluation Standards**: Different evaluation metrics and methods produce conflicting rankings across attribution approaches, with no standardized benchmark for comparison.
2. **Single-Paradigm Limitations**: Existing benchmarks focus on individual attribution paradigms (data, mechanistic, or concept) rather than providing unified cross-paradigm evaluation.
3. **Polysemanticity and Universality**: Only 1-5% of neurons are universal across random seeds, presenting challenges for interpretability methods and limiting scalability to larger models.
4. **Absence of Ground Truth**: Current evaluation approaches lack synthetic benchmarks with known ground truth for validating circuit and causal variable localization across multiple paradigms.
5. **Scaling Constraints**: Interpretability findings may not generalize to models beyond ~10B parameters due to fundamental differences in neural representations at scale.
