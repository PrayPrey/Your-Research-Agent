## Related Work

**Related Papers**

1. **Title**: Neuron Spurious Score (2025)
   - **Authors**: Not specified
   - **Summary**: Proposed neuron-level spurious score to quantify dependence on spurious features using observational correlation, but does not test causal role under distribution shift.
   - **Year**: 2025

2. **Title**: Feature Visualization Literature (Distill, Network Dissection)
   - **Authors**: Olah et al. (and others)
   - **Summary**: Visualize what individual neurons detect through feature visualization techniques, enabling interpretation of neuron activations for specific patterns.
   - **Year**: Not specified

3. **Title**: Saliency Maps (GradCAM, etc.)
   - **Authors**: Not specified
   - **Summary**: Identify which input regions influence predictions through gradient-based visualization methods.
   - **Year**: Not specified

4. **Title**: Causality: Models, Reasoning, and Inference
   - **Authors**: Pearl
   - **Summary**: Formal framework for causal inference via intervention using the do-operator, establishing variable-level causality testing.
   - **Year**: 2009

5. **Title**: Neuroscience Causal Intervention Studies (Lesion Studies, Optogenetics)
   - **Authors**: Not specified
   - **Summary**: Established systematic neuron ablation as the gold standard for testing causality in biological neural systems.
   - **Year**: Not specified

6. **Title**: Causal Representation Learning
   - **Authors**: Schölkopf et al., Bengio
   - **Summary**: Learn representations encoding causal variables through specialized training objectives.
   - **Year**: 2021 (Schölkopf), 2019 (Bengio)

7. **Title**: Medical AI Shortcut Learning
   - **Authors**: Ong Ly C., Unnikrishnan B., et al.
   - **Summary**: Estimate generalizability without external data by measuring data acquisition bias, providing model-level data-intrinsic detection of shortcuts.
   - **Year**: 2024

8. **Title**: Shortcut Learning in Deep Neural Networks
   - **Authors**: Geirhos et al.
   - **Summary**: Comprehensive taxonomy of shortcut learning, defining various types of spurious correlations DNNs exploit.
   - **Year**: 2020

9. **Title**: The Pitfalls of Simplicity Bias in Neural Networks
   - **Authors**: Shah et al.
   - **Summary**: Proves DNNs exclusively rely on simplest features even when more complex features are equally predictive, explaining why spurious correlations are preferentially learned.
   - **Year**: 2020

10. **Title**: Distributionally Robust Optimization (Group DRO)
    - **Authors**: Sagawa et al.
    - **Summary**: Optimize for worst-group accuracy through training-time reweighting, but requires manual group annotations.
    - **Year**: 2020

11. **Title**: Invariant Risk Minimization (IRM)
    - **Authors**: Arjovsky et al.
    - **Summary**: Learn invariant predictors across environments by enforcing causal invariance during training, but requires multiple environments and known to fail in practice.
    - **Year**: 2019

12. **Title**: Deep Feature Reweighting (DFR)
    - **Authors**: Kirichenko et al., Izmailov et al.
    - **Summary**: Last-layer retraining recovers robust features from pre-trained representations without targeted neuron selection.
    - **Year**: 2022

13. **Title**: Waterbirds Dataset (Based on CUB-200-2011 + Places backgrounds)
    - **Authors**: Not specified
    - **Summary**: Benchmark dataset with known spurious correlation (water background → waterbird, 95% in training data) for evaluating spurious correlation methods.
    - **Year**: Not specified

14. **Title**: CelebA Dataset
    - **Authors**: Not specified
    - **Summary**: Dataset with 40 binary attributes and 200K+ images, containing gender/age biases in "Attractive" prediction for blind discovery validation.
    - **Year**: Not specified

15. **Title**: JailbreakBench (LLM Robustness)
    - **Authors**: Chao et al.
    - **Summary**: Standardized benchmark for evaluating LLM robustness against adversarial attacks and jailbreaking attempts.
    - **Year**: 2024

**Key Challenges**

1. **Observational-Only Spurious Detection**: Existing XAI methods (e.g., Neuron Spurious Score 2025) measure only observational correlations without testing causal role under distribution shift, failing to distinguish correlation from causation.

2. **Group Annotation Requirements**: Robustification methods like Group DRO and existing spurious detection approaches require manual group annotations, making them impractical for discovering unknown spurious correlations.

3. **Localized vs Distributed Representations**: Uncertainty about whether spurious correlations manifest in localized neuron groups or are fully distributed across the network, affecting the feasibility of neuron-level intervention approaches.

4. **Synthetic Shift Approximation Gap**: Synthetic distribution shifts (augmentation) may not perfectly capture real distribution shifts, creating uncertainty about whether OI discrepancy measured on synthetic shifts generalizes to real shifts.

5. **Multi-Environment Requirements**: Causal invariance methods like IRM require multiple environments with different spurious correlations, which are often unavailable in practice.

6. **Threshold Calibration Without Ground Truth**: Determining optimal OI discrepancy thresholds for spurious neuron detection without validation data containing known spurious features.

7. **Computational Scalability**: Neuron-level intervention analysis requires O(neurons × samples × 2) forward passes, making it computationally expensive for billion-parameter models without sampling strategies.

8. **Semantic Interpretation of Discovered Patterns**: Clustering flagged neurons reveals unknown patterns, but automated semantic labeling of discovered spurious patterns remains an open challenge requiring manual analysis.
