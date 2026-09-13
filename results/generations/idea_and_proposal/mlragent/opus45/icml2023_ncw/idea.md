# Title: Compression-Aware Distillation: Learning Student Networks via Rate-Distortion Optimization

## Motivation
Knowledge distillation typically transfers knowledge from teacher to student networks by minimizing output divergence, treating compression as a separate downstream step. However, this decoupled approach is suboptimal—students learn representations that may not be efficiently compressible, leading to significant performance degradation when quantization or pruning is applied post-hoc. By unifying distillation and compression through an information-theoretic lens, we can train students that simultaneously achieve high task performance and inherent compressibility, enabling more efficient deployment of foundation models.

## Main Idea
We propose a rate-distortion framework for knowledge distillation where the student network explicitly optimizes a Lagrangian objective: minimizing task distortion (matching teacher outputs) while constraining the information rate of intermediate representations. Specifically, we introduce learnable entropy models at each layer to estimate the bit-rate required to encode activations, inspired by neural image compression. The training objective becomes:

**L = D(teacher, student) + λ · R(representations)**

where R measures the entropy of quantized layer activations and λ controls the rate-distortion trade-off. We employ straight-through estimators for end-to-end differentiability and progressively anneal λ during training.

**Expected Outcomes:** Students that achieve superior accuracy-compression Pareto frontiers compared to distill-then-compress baselines. The learned representations will exhibit structured sparsity and lower entropy, enabling 2-4× better compression ratios at equivalent accuracy.

**Impact:** Enables efficient deployment of foundation models on resource-constrained devices while maintaining knowledge transfer quality.