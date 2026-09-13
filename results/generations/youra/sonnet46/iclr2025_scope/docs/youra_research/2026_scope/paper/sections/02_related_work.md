# 2. Related Work

Our work sits at the intersection of three research streams: adaptive rank allocation for
parameter-efficient fine-tuning, activation sparsity in large language models, and structural
analysis of pre-trained representations. We review each in turn, identifying how existing work
motivates but does not address our central question.

## 2.1 Parameter-Efficient Fine-Tuning and Adaptive Rank

LoRA \citep{hu2021lora} constrains weight updates to low-rank matrices, dramatically reducing
trainable parameters. The original LoRA formulation assigns a uniform rank $r$ across all target
layers — a simplification acknowledged by the authors as potentially suboptimal. Subsequent work
has explored non-uniform allocation, but exclusively using training-time signals.

**AdaLoRA** \citep{zhang2023adalora} extends LoRA with singular value decomposition: weight
update matrices are decomposed, and singular values are adaptively pruned during training via an
importance score. This achieves better parameter efficiency, but requires a full training run to
discover the allocation — making it computationally expensive and per-task. The allocation cannot
be precomputed or transferred to new tasks without re-running.

**DyLoRA** \citep{valipour2022dylora} addresses rank search by training across multiple rank
values simultaneously via stochastic rank sampling, enabling post-hoc rank selection without
multiple training runs. However, DyLoRA still requires full training to produce the rank
distribution — the final allocation is a product of the training dynamics, not a pre-training signal.

More recent methods including ARD-LoRA, La-LoRA, and Sensitivity-LoRA \citep{[CITATION NEEDED]}
use gradient norms, Hessian approximations, or layer sensitivity analysis — all computed during
or after training. None exploits pre-training model structure as a zero-cost prior.

The closest work to ours is Act-LoRA \citep{[CITATION NEEDED — MDPI 2025]}, which uses layer-wise
L2 activation norms to perform binary layer selection (include/exclude layer in LoRA). However,
Act-LoRA focuses on layer selection (binary), not rank magnitude allocation (continuous), and does
not characterize the stability or threshold-invariance of the activation signal. Our work provides
exactly this characterization for the near-zero sparsity signal, establishing whether it is
reliable enough to serve as a pre-training prior.

## 2.2 Activation Sparsity in Large Language Models

Activation sparsity — the phenomenon whereby a significant fraction of activations are near-zero
— has been extensively documented in large transformer models.

Li et al.~\shortcite{li2022lazy} characterize the "Lazy Neuron Phenomenon" in transformers:
during training, neurons become increasingly sparse, with attention layers and FFN activations
exhibiting significantly concentrated activity. This phenomenon is architecture-dependent:
models with ReLU activations exhibit harder sparsity than those with GELU or SiLU. Our work
extends this characterization specifically to LLaMA-3.1-8B's SiLU-gated MLP layers, providing
cross-distribution stability analysis that goes beyond prior observational work.

Mirzadeh et al.~\shortcite{mirzadeh2023relu} demonstrate in "ReLU Strikes Back" that modern
LLMs trained with ReLU or ReLU-like activations achieve remarkable sparsity at inference time,
enabling efficient hardware utilization. TEAL \citep{liu2024teal} provides a training-free
approach to exploiting activation sparsity via magnitude-based thresholding.

Szatkowski et al.~\shortcite{szatkowski2025universal} identify universal structural properties
across LLM families, finding that sparsity patterns exhibit cross-model consistency. This
motivates our cross-distribution stability analysis: if sparsity reflects architecture-intrinsic
geometry rather than input content, it should be stable across calibration distributions. Our
ICC$(3,k)=0.9846$ result strongly confirms this for LLaMA-3.1-8B.

A critical distinction separates the above work from ours: the existing literature characterizes
sparsity as an observable property of inference or training dynamics. **No prior work establishes
whether the sparsity fingerprint is stable enough, and threshold-invariant enough, to serve as a
pre-training structural prior for downstream rank allocation decisions.** This is our central
empirical contribution.

## 2.3 Intrinsic Dimensionality and Layer Structure

Aghajanyan et al.~\shortcite{aghajanyan2021intrinsic} demonstrate that pre-trained language
models have low intrinsic dimension for fine-tuning: a random projection to a $d$-dimensional
subspace (with $d \ll D$) captures more than 90\% of full fine-tuning performance. Crucially,
structure-aware projections (SAID) significantly outperform dimension-insensitive alternatives
(DID), suggesting that layer structure matters for adaptation efficiency. This provides the
theoretical bridge for our hypothesis: if sparsity proxies the intrinsic dimension of each
layer's computational subspace (a connection we term A3 in Section~6), it could directly inform
rank allocation decisions.

Clark et al.~\shortcite{clark2019bert} and Tenney et al.~\shortcite{tenney2019bert} demonstrate
a linguistic hierarchy in transformer layers: syntactic processing concentrated in early-to-middle
layers, semantic integration in deeper layers. Our observed depth gradient — early layers most
sparse, deep layers least sparse — is consistent with this specialization: syntactic processing
may require fewer dimensions, semantic integration more. We identify this as a motivated
interpretive connection, not yet a verified causal claim.

## 2.4 Summary and Positioning

Table~\ref{tab:comparison} summarizes how our work differs from prior approaches:

| Method | Signal | Cost | Allocation Type | Stability Characterized? |
|--------|--------|------|----------------|--------------------------|
| AdaLoRA \citep{zhang2023adalora} | SVD importance | Training-time | Continuous | No |
| DyLoRA \citep{valipour2022dylora} | Rank sampling | Training-time | Continuous | No |
| Act-LoRA | L2 activation norm | Inference-time | Binary (layer) | No |
| TEAL \citep{liu2024teal} | Magnitude threshold | Inference-time | Pruning | No |
| **SparsityLoRA (ours)** | **Sparsity profile** | **Single forward pass** | **Continuous (rank)** | **Yes (ICC, tau)** |

Our work is the first to (1) systematically characterize the cross-distribution and
cross-threshold stability of the sparsity fingerprint, and (2) propose it as a zero-cost
pre-training prior for continuous LoRA rank allocation — rather than using it for inference
pruning or binary selection.
