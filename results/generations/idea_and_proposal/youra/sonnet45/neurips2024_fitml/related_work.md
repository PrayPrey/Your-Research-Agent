## Related Work

**Related Papers**
1. **Title**: LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
   - **Authors**: Hu et al.
   - **Summary**: Original LoRA paper that introduces the ΔW = BA low-rank parameterization for parameter-efficient fine-tuning. Foundation for low-rank adaptation methods but provides no guidance on selecting optimal rank r.
   - **Year**: 2021

2. **Title**: QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)
   - **Authors**: Dettmers et al.
   - **Summary**: Combines 4-bit quantization with LoRA for efficient fine-tuning. Empirically observes that "rank r is unrelated to performance if all layers are adapted" but uses fixed heuristics (r=64, α=16) without theoretical justification.
   - **Year**: 2023

3. **Title**: AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning (Zhang et al., 2023)
   - **Authors**: Zhang et al.
   - **Summary**: Adapts LoRA rank dynamically during training via SVD decomposition and importance scoring, enabling during-training rank optimization at the cost of additional computational overhead.
   - **Year**: 2023

4. **Title**: Computational Limits of Low-Rank Adaptation (LoRA) for Transformer Models (Hu et al., 2024)
   - **Authors**: Hu et al.
   - **Summary**: Provides fine-grained complexity analysis using SETH (Strong Exponential Time Hypothesis), identifying phase transition behavior in LoRA. Establishes post-hoc theoretical characterization of LoRA complexity.
   - **Year**: 2024

5. **Title**: On the Generalization for Transfer Learning: An Information-Theoretic Analysis (Wu et al., 2022)
   - **Authors**: Wu et al.
   - **Summary**: Establishes information-theoretic bounds showing that adaptation capacity (measured by KL divergence) must match task complexity for successful transfer learning. Provides theoretical foundation for capacity-matching principles.
   - **Year**: 2022

6. **Title**: Intrinsic Dimensionality Emerges from Training Dynamics (Ansuini et al., 2019)
   - **Authors**: Ansuini et al.
   - **Summary**: Demonstrates that neural network representations have low effective dimensionality measurable early in training. Shows tasks with higher complexity (e.g., CIFAR-100 vs. CIFAR-10) exhibit higher intrinsic dimensionality.
   - **Year**: 2019

7. **Title**: Visualizing the Loss Landscape of Neural Networks (Li et al., 2018)
   - **Authors**: Li et al.
   - **Summary**: Shows that early loss landscape geometry (Hessian eigenspectra) predicts final training dynamics. Demonstrates that curvature measured at initialization correlates with final minima.
   - **Year**: 2018

8. **Title**: Gradient Starvation: A Learning Proclivity in Neural Networks (Pezeshki et al., 2021)
   - **Authors**: Pezeshki et al.
   - **Summary**: Demonstrates that gradients concentrate on a subset of features early in training and this pattern persists throughout training, supporting gradient structure stability assumptions.
   - **Year**: 2021

9. **Title**: Communication in the Presence of Noise (Shannon, 1949)
   - **Authors**: Shannon
   - **Summary**: Foundation of signal processing establishing the Nyquist-Shannon Sampling Theorem: sampling rate must exceed 2× bandwidth for perfect reconstruction. Provides conceptual analogy for capacity-matching principles.
   - **Year**: 1949

10. **Title**: LLM-Adapters: An Adapter Family for Parameter-Efficient Fine-Tuning of Large Language Models (Hu et al., 2023)
    - **Authors**: Hu et al.
    - **Summary**: Empirical study of adapter methods, ranks, and hyperparameters across architectures. Documents current trial-and-error practices and demonstrates need for principled rank selection methods.
    - **Year**: 2023

11. **Title**: Parameter-Efficient Fine-Tuning for Large Models: A Comprehensive Survey (Lialin et al., 2024)
    - **Authors**: Lialin et al.
    - **Summary**: Comprehensive survey of PEFT methods including LoRA, adapters, prefix tuning, and prompt tuning. Positions LoRA rank selection within broader parameter-efficient fine-tuning landscape.
    - **Year**: 2024

**Key Challenges**
1. **Lack of Theoretical Guidance for LoRA Rank Selection**: Current practice relies on trial-and-error or fixed heuristics (r=8,16,32,64) without principled methods for determining optimal rank, leading to inefficient hyperparameter search requiring 5-10 full training runs.

2. **Gap Between Theory and Practice**: Post-hoc theoretical analyses (e.g., Hu et al. 2024 complexity analysis) explain existing behavior but don't provide predictive tools for practical hyperparameter selection before training.

3. **Computational Cost of Hyperparameter Search**: Exhaustive grid search over LoRA ranks requires 5-10× the compute cost of a single training run, making efficient fine-tuning inaccessible to resource-constrained researchers.

4. **Uniform Rank Allocation Inefficiency**: Fixed uniform ranks across all layers (Q, K, V, FFN) ignore layer-specific adaptation requirements, leading to over-allocation and wasted parameters as suggested by QLoRA's observation that "rank is unrelated to performance if all layers are adapted."

5. **Gradient Non-Stationarity**: Gradient distributions evolve during training, making single-snapshot measurements potentially unreliable for predicting final fine-tuning requirements without trajectory-based analysis.

6. **Limited Understanding of Task Complexity**: No established quantitative measures exist for determining which tasks require high-dimensional vs. low-dimensional adaptations, making it difficult to predict appropriate LoRA capacity requirements.

7. **Transfer of Theoretical Frameworks**: Linear signal processing principles (Nyquist-Shannon sampling theorem) don't directly transfer to non-linear neural network optimization without empirical calibration, creating gaps between conceptual analogies and practical implementation.
