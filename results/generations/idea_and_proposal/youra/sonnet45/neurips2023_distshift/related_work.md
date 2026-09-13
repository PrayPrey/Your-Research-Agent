## Related Work

**Related Papers**

1. **Title**: Benchmarking Robustness of Adaptation Methods
   - **Authors**: Chen et al.
   - **Summary**: Empirically demonstrates that adapters achieve better robustness than full fine-tuning with comparable in-distribution accuracy. Provides critical empirical evidence for robustness differences between fine-tuning methods.
   - **Year**: 2023

2. **Title**: Understanding RLHF Effects on Output Diversity and OOD Generalization
   - **Authors**: Kirk et al.
   - **Summary**: Shows that output diversity reduction correlates with OOD generalization degradation in RLHF. Demonstrates that RLHF improves OOD generalization vs SFT, but reduces diversity by 30% (p < 0.001). Establishes diversity-robustness correlation.
   - **Year**: 2023

3. **Title**: Self-Learning for Distribution Shifts
   - **Authors**: Rusak et al.
   - **Summary**: Demonstrates that robustness patterns are consistent across different architectures (ResNet, DenseNet, ViT), providing evidence for architecture independence of robustness mechanisms.
   - **Year**: 2021

4. **Title**: WPO for RLHF
   - **Authors**: Zhou et al.
   - **Summary**: Addresses distribution mismatch in fine-tuning (off-policy RLHF). Shows off-policy distributional gap correlates with performance degradation (α=0.91, p < 0.001). Motivates parameter-level analysis of distributional issues in fine-tuning.
   - **Year**: 2024

5. **Title**: Intrinsic Dimensionality in Adversarial Training
   - **Authors**: Altinisik et al.
   - **Summary**: Provides critical validation that intrinsic dimensionality directly correlates with adversarial robustness and OOD generalization. Validates using ID as a robustness metric and shows ID reduction during training. This paper resolves the "feature diversity → robustness link lacks direct evidence" concern and elevates the hypothesis from plausible to empirically validated.
   - **Year**: 2024

6. **Title**: How transferable are features in deep neural networks?
   - **Authors**: Yosinski et al.
   - **Summary**: Foundational transfer learning study showing that early layers in CNNs learn general features. Provides standard understanding in deep learning about layer-wise feature generality.
   - **Year**: 2014

7. **Title**: WILDS: A Benchmark of in-the-Wild Distribution Shifts
   - **Authors**: Koh et al.
   - **Summary**: Establishes community consensus benchmark for meaningful distribution shifts with comprehensive evaluation protocols. Cited by 1664 papers, providing standard OOD evaluation framework.
   - **Year**: 2020

8. **Title**: Overcoming catastrophic forgetting in neural networks
   - **Authors**: Kirkpatrick et al.
   - **Summary**: Introduces Elastic Weight Consolidation (EWC) using Fisher Information for parameter importance estimation. Provides conceptual inspiration for synaptic consolidation analogy and Fisher Information-based importance scoring, adapted from catastrophic forgetting to robustness preservation.
   - **Year**: 2017

9. **Title**: Parameter-Efficient Transfer Learning for NLP (Adapters)
   - **Authors**: Houlsby et al.
   - **Summary**: Introduces bottleneck adapter architecture with adapters inserted after attention and feed-forward layers. Provides architectural specification used in experiments.
   - **Year**: 2019

10. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
    - **Authors**: Hu et al.
    - **Summary**: Proposes low-rank updates to attention weights as parameter-efficient fine-tuning method. Demonstrates effectiveness with minimal parameter updates while preserving model capacity.
    - **Year**: 2021

11. **Title**: Maximum Likelihood Estimation of Intrinsic Dimension
    - **Authors**: Levina & Bickel
    - **Summary**: Introduces Maximum Likelihood Estimator (MLE) for intrinsic dimensionality based on k-nearest neighbors. Provides theoretical foundation for ID measurement used throughout the hypothesis.
    - **Year**: 2004

12. **Title**: Estimating the intrinsic dimension of datasets by a minimal neighborhood information (TwoNN)
    - **Authors**: Facco et al.
    - **Summary**: Proposes TwoNN estimator as alternative intrinsic dimensionality measurement method. Used as comparison baseline for ID estimator validation.
    - **Year**: 2017

13. **Title**: Novel high intrinsic dimensionality estimators (MiND)
    - **Authors**: Rozza et al.
    - **Summary**: Introduces MiND estimator for intrinsic dimensionality. Provides third alternative ID estimator for robustness validation of ID measurement approach.
    - **Year**: 2012

14. **Title**: Benchmarking Neural Network Robustness to Common Corruptions and Perturbations (ImageNet-C)
    - **Authors**: Hendrycks & Dietterich
    - **Summary**: Introduces ImageNet-C benchmark with 15 corruption types at 5 severity levels, simulating natural image degradations (noise, blur, weather). Establishes standard OOD evaluation protocol for vision models.
    - **Year**: 2019

15. **Title**: DiGraP
    - **Authors**: Not specified
    - **Summary**: Recent engineering method that develops techniques to preserve robustness during fine-tuning but lacks mechanistic understanding of why robustness degrades.
    - **Year**: 2025

16. **Title**: LARGO
    - **Authors**: Not specified
    - **Summary**: Recent engineering method focused on robustness preservation during adaptation. Provides performance improvements without explaining underlying mechanisms.
    - **Year**: 2025

17. **Title**: MAPS
    - **Authors**: Not specified
    - **Summary**: Recent engineering method for maintaining robustness in fine-tuned models. Demonstrates practical techniques but lacks theoretical framework.
    - **Year**: 2025

**Key Challenges**

1. **Mechanistic Understanding Gap**: While empirical evidence shows full fine-tuning degrades OOD robustness compared to parameter-efficient methods (adapters, LoRA), the causal mechanism linking gradient-based updates during fine-tuning to robustness loss is not understood.

2. **Robustness-Critical Parameter Identification**: No framework exists to identify which parameters in a foundation model are critical for OOD generalization before fine-tuning occurs.

3. **Adapter Superiority Explanation**: It is unclear whether adapters preserve robustness due to inherent architectural superiority or accidentally through their architectural constraints (frozen backbone + added modules).

4. **Feature Diversity and Robustness Link**: The relationship between feature diversity (measured via intrinsic dimensionality) and OOD robustness needs validation across different architectures and shift types.

5. **Layer-Wise Update Patterns**: The differential impact of fine-tuning on early vs. late layers and how this affects representation quality and generalization is not well characterized.

6. **Distributional Shift Coverage**: Standard benchmarks may not adequately represent all real-world distribution shift scenarios, limiting generalization of findings across different shift types (corruption, domain, adversarial).

7. **Architecture Generalization**: Robustness patterns studied primarily in CNNs may not generalize to Transformer architectures (ViT, BERT, GPT) which have different inductive biases and layer structures.

8. **Engineering vs. Understanding Trade-off**: Recent methods (DiGraP, LARGO, MAPS 2025) achieve robustness improvements through engineering but lack mechanistic explanations, limiting principled design of future methods.

9. **ID Estimator Validity**: Different intrinsic dimensionality estimators (MLE, TwoNN, MiND) may produce inconsistent results, requiring validation of which estimator most accurately reflects robustness-relevant diversity.

10. **Fisher Information on OOD Data**: Using Fisher Information computed on out-of-distribution data (rather than standard in-distribution training data) for parameter importance is non-standard and requires empirical validation.

11. **Causal vs. Correlational Evidence**: Most existing evidence for diversity-robustness relationships is correlational; establishing causal links requires intervention experiments (selective freezing, controlled manipulations).

12. **Practical Applicability**: Translating mechanistic insights into actionable guidance for practitioners fine-tuning foundation models in safety-critical domains requires bridging theory and practice.
