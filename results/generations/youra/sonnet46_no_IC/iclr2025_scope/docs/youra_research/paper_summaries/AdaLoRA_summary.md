# AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning

## Key Metadata
- **Authors:** Zhang et al.
- **Year:** 2023
- **Venue:** ICLR 2023
- **Core Contribution:** Adaptive rank allocation for LoRA by pruning singular values of ΔW during training based on importance scores.

## Section Summaries

### Abstract
AdaLoRA adaptively allocates the parameter budget among weight matrices during fine-tuning. Matrices with higher sensitivity receive higher ranks, while less important ones are pruned. This results in improved fine-tuning performance under the same parameter budget compared to uniform rank LoRA.

### Introduction & Motivation
Uniform-rank LoRA treats all weight matrices identically, which is suboptimal because different layers and modules contribute differently to downstream task performance. The gap: no principled automatic way to allocate rank budgets before training. AdaLoRA addresses this with a training-time SVD-based approach.

### Methodology
AdaLoRA parameterizes ΔW = PΛQ^T where P and Q are orthogonal and Λ is a diagonal matrix of singular values. During training, it computes importance scores I_k for each singular value triplet (u_k, σ_k, v_k) using gradient information: I_k = |σ_k| · (|∂L/∂σ_k| + |∂L/∂u_k| + |∂L/∂v_k|). Singular value triplets with low importance are zeroed out (masked). This is an online rank allocation scheme — rank changes DURING training, not before it. The RankAllocator class manages masking and budget scheduling. Target rank r per layer is dynamically adjusted via a budget scheduler that decrements total budget B by ΔB each step. Orthogonality of P and Q is maintained via regularization term: R(P,Q) = ||P^T P - I||² + ||QQ^T - I||². Initial rank is set high (e.g., r_init = 2r_target) and pruned down over the first T_target steps.

### Experiments & Results
Primary benchmark: GLUE (NLU tasks), evaluated on DeBERTa-v3-base and DeBERTa-XXL. Compared against LoRA (uniform), prefix tuning, adapter methods. AdaLoRA achieves 0.3–1.2% improvement over LoRA at same parameter budget on MNLI, SST-2, MRPC, QQP. With DeBERTa-v3-base at 0.3M parameters, AdaLoRA scores 90.4 on MNLI vs 90.0 for LoRA. Key ablation: removing importance-based allocation (using uniform random pruning) drops performance by ~0.5%, confirming the allocation signal matters. Compute overhead: ~15% additional training time due to SVD maintenance. Does NOT evaluate ViT or vision tasks.

### Discussion & Conclusion
AdaLoRA shows that non-uniform rank allocation consistently outperforms uniform rank, validating the per-layer rank differentiation premise. Limitation: requires full training run to discover optimal allocation — no zero-shot rank prediction from W₀. Future: pre-training rank predictor from static W₀ properties.

## Key Contributions
- Training-time SVD-based adaptive rank allocation (no pre-training analysis needed)
- Importance score combining gradient magnitude and singular value size
- Orthogonality regularization for stable SVD decomposition during training

## Potential Relevance
AdaLoRA is the primary competitor to the erank hypothesis: it discovers per-layer rank allocation via gradient signals during training, while erank proposes predicting optimal rank from W₀ before training. The rank allocations AdaLoRA produces at convergence could serve as a proxy oracle for PARA ranks. The DeBERTa-v3 infrastructure in AdaLoRA's codebase is directly reusable for PARA oracle implementation.
