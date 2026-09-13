## Related Work

**Related Papers**
1. **Title**: Conflict-Averse Gradient Descent for Multi-task Learning (arXiv:2110.14048)
   - **Authors**: Liu, B., Liu, X., Jin, X., Stone, P., Liu, Q.
   - **Summary**: Proposes CAGrad which provably converges to Pareto-stationary point while minimizing average loss, demonstrating superior performance compared to prior multi-objective optimization methods.
   - **Year**: 2021

2. **Title**: FUTURE AI: International consensus guideline for trustworthy and deployable artificial intelligence in healthcare (DOI: 10.1136/bmj-2024-081554)
   - **Authors**: FUTURE-AI Consortium (117 experts, 50 countries)
   - **Summary**: Establishes 6 unified principles for trustworthy medical AI, providing a foundation for translating governance requirements into technical implementations.
   - **Year**: 2024

3. **Title**: Unified Framework for Explainable and Robust Artificial Intelligence (DOI: 10.47485/3069-8006.1010)
   - **Authors**: Ferrara, M.
   - **Summary**: Provides theoretical demonstration that explainability and robustness can be synergistic rather than requiring trade-offs between them.
   - **Year**: 2026

4. **Title**: Attention Consistency Regularization for Interpretable Early-Exit Neural Networks (arXiv:2601.08891)
   - **Authors**: Zhao, Y.
   - **Summary**: Proposes ACR to align attention maps across network exits, achieving 98.97% accuracy with 18.5% consistency improvement for interpretable neural networks.
   - **Year**: 2026

5. **Title**: A Survey on Trustworthiness in Foundation Models for Medical Image Analysis
   - **Authors**: Shi et al.
   - **Summary**: Provides comprehensive taxonomy confirming that trustworthiness dimensions in medical AI have been studied in isolation, with no unified framework existing.
   - **Year**: 2024

6. **Title**: MediConfusion: Probing Reliability of Multimodal Medical Foundation Models
   - **Authors**: Sepehri et al.
   - **Summary**: Demonstrates that state-of-the-art multimodal large language models perform below random guessing on visual confusion benchmarks, highlighting urgent robustness needs.
   - **Year**: 2024

7. **Title**: Differential privacy for medical deep learning: methods, tradeoffs, and deployment implications
   - **Authors**: Mohammadi et al.
   - **Summary**: Shows that DP-SGD at strict privacy levels (ε≈1) often leads to substantial accuracy loss, indicating the need for alternative privacy-preserving mechanisms.
   - **Year**: 2026

**Key Challenges**
1. **Isolated Trustworthiness Dimensions**: Current research addresses explainability, robustness, and privacy as separate objectives without a unified framework that optimizes them jointly.

2. **Robustness Failures in Medical MLLMs**: State-of-the-art multimodal medical foundation models exhibit critical reliability issues, performing worse than random guessing on visual confusion tasks.

3. **Privacy-Utility Trade-off**: Differential privacy mechanisms like DP-SGD cause substantial accuracy degradation at strict privacy levels, necessitating alternative approaches that better balance privacy and model performance.

4. **Lack of Governance-to-Technical Translation**: While consensus guidelines for trustworthy medical AI exist, practical frameworks for translating these governance principles into technical implementations remain underdeveloped.

5. **Multi-Objective Optimization Convergence**: Achieving Pareto-optimal solutions across competing trustworthiness objectives requires specialized optimization methods that can handle conflicting gradients effectively.
