## Related Work

**Related Papers**

1. **Title**: AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration
   - **Authors**: Lin, J., et al.
   - **Summary**: Post-training quantization using per-channel scaling based on activation sensitivity analysis; no retraining required. Achieves 0.8% perplexity increase on WikiText-103 for LLaMA-7B at 4-bit.
   - **Year**: 2023

2. **Title**: Unified Data-Free Compression: Pruning and Quantization without Fine-Tuning
   - **Authors**: Bai, H., et al.
   - **Summary**: Simultaneous post-training pruning and quantization without data or fine-tuning; demonstrates 20.54% accuracy improvement on ImageNet.
   - **Year**: 2023

3. **Title**: Differentiable Soft Quantization (DSQ)
   - **Authors**: Gong, R., et al.
   - **Summary**: Tanh-based soft quantization with learnable temperature for gradient flow: q(w) = tanh(T × w). Enables gradient backpropagation through quantization operations.
   - **Year**: 2019

4. **Title**: Multi-Task Learning as Multi-Objective Optimization (MGDA)
   - **Authors**: Sener, O., & Koltun, V.
   - **Summary**: Multiple Gradient Descent Algorithm (MGDA) finds Pareto-optimal descent direction for multiple task losses; provides provable convergence to Pareto front.
   - **Year**: 2018

5. **Title**: Gradient-Based Multi-Objective Deep Learning: Algorithms, Theories (2024 Survey)
   - **Authors**: Not specified
   - **Summary**: Survey of multi-objective optimization methods; covers gradient balancing vs. loss balancing and convergence properties.
   - **Year**: 2024

6. **Title**: An Information-Theoretic Justification for Model Pruning
   - **Authors**: Isik, B., Weissman, T., & No, A.
   - **Summary**: Proves pruning is necessary for optimal compression via rate-distortion theory; Information Bottleneck (IB) principle shows pruning aids generalization.
   - **Year**: 2021

7. **Title**: Deep learning and the information bottleneck principle
   - **Authors**: Tishby, N., & Zaslavsky, N.
   - **Summary**: DNNs can be quantified by mutual information I(X; Z) and I(Z; Y); compression phase in training aids generalization.
   - **Year**: 2015

8. **Title**: Mist: Efficient Distributed Training of Large Language Models via Memory-Parallelism Co-Optimization
   - **Authors**: Zhu, Y., et al.
   - **Summary**: Achieves 1.28× speedup over Megatron-LM through overlap-centric scheduling and imbalance-aware tuning; co-optimizes memory and parallelism.
   - **Year**: 2025

9. **Title**: OpenFedLLM: Training Large Language Models on Decentralized Private Data via Federated Learning
   - **Authors**: Ye, R., et al.
   - **Summary**: Federated LLM training with communication-constrained gradient optimization; demonstrates feasibility of gradient compression during distributed training.
   - **Year**: 2024

10. **Title**: Language Modeling is Compression
    - **Authors**: Not specified
    - **Summary**: Views language modeling as data compression problem (minimizing KL divergence = optimal compression); focuses on data compression rather than model compression.
    - **Year**: 2024

11. **Title**: Two-phase collaborative model compression training for joint pruning and quantization
    - **Authors**: Not specified
    - **Summary**: Joint pruning+quantization during training, applied to pre-trained networks during post-pre-training fine-tuning phase.
    - **Year**: 2025

12. **Title**: Quantization-Aware Training (QAT) - General Paradigm
    - **Authors**: Not specified
    - **Summary**: Insert quantization operations in forward pass during fine-tuning/retraining; backpropagate through Straight-Through Estimator (STE). Typically requires 10-20% of original training steps.
    - **Year**: Not specified

**Key Challenges**

1. **Sequential Train-Then-Compress Paradigm**: All existing compression methods apply post-training (AWQ) or during retraining (QAT), requiring separate computational phases that add 20-30% overhead to total compute budget.

2. **Single-Objective Optimization Limitation**: Most compression methods optimize single objective (quantization OR pruning) rather than jointly optimizing multiple compression objectives.

3. **Lack of Gradient Flow During Compression**: Post-training compression methods have no gradients; QAT applies gradient flow only during retraining phase, not from pre-training start.

4. **MGDA Scalability Uncertainty**: Multiple Gradient Descent Algorithm proven for multi-task learning at moderate scale (100M-1B params), but no published work demonstrates MGDA at 10B+ parameter scale with >2 objectives.

5. **Compression-Awareness Gap**: Standard pre-training does not consider compression objectives, resulting in models that require separate compression phases with potential performance degradation.

6. **Distributed Training Compression State Management**: Distributed training frameworks (DeepSpeed, Megatron) do not account for compression state partitioning; federated learning focuses on privacy rather than compression-aware training.

7. **Empirical IB Principle Application**: Information Bottleneck principle observed emergently in neural networks, but not explicitly designed into training objectives for compression purposes.

8. **Compute-Accuracy Trade-off Inefficiency**: Existing methods produce suboptimal Pareto frontiers (accuracy vs. compression) due to sequential optimization rather than joint multi-objective training.

9. **Phase Boundary Selection for Multi-Objective Training**: No theoretical guidance on optimal timing for introducing compression objectives during training; current approaches rely on heuristics from multi-task learning.

10. **Compression-Readiness Metric Formalization**: Lack of theoretically-justified metrics to measure model compressibility during training; existing proxies (activation variance, weight entropy) are empirical without formal validation.
