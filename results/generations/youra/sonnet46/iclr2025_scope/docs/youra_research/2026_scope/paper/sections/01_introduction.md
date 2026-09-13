# 1. Introduction

Fine-tuning a large language model requires deciding how many parameters to allocate to each
layer — yet this allocation is typically uniform across layers, made before training begins, despite
the fact that each layer contributes differently to model behavior. Low-Rank Adaptation
(LoRA; \citealt{hu2021lora}) has become the dominant paradigm for efficient fine-tuning:
by constraining weight updates to low-rank matrices, LoRA reduces trainable parameters by orders
of magnitude without sacrificing downstream performance. The rank $r$ of these updates, however,
is set uniformly across all transformer layers — a choice that ignores the heterogeneous
computational roles that emerge during pre-training.

This is not merely an aesthetic concern. Aghajanyan et al.~\shortcite{aghajanyan2021intrinsic}
demonstrate that pre-trained language models have low intrinsic dimension: more than 90\% of
full fine-tuning performance can be achieved in a subspace far smaller than the full parameter
space. Critically, this intrinsic dimension is not uniform across layers — structure-aware
methods (SAID) significantly outperform dimension-insensitive alternatives. If layers differ in
their fine-tuning dimensionality, allocating equal rank to all layers wastes parameters in
low-complexity layers while starving high-complexity ones.

The field has recognized this problem: AdaLoRA \citep{zhang2023adalora}, DyLoRA
\citep{valipour2022dylora}, and a growing family of adaptive rank methods
allocate rank dynamically based on layer importance. But all existing methods face a fundamental
constraint: **they learn the allocation during training**. AdaLoRA uses singular value
decomposition of weight updates to re-rank and prune during fine-tuning. DyLoRA trains across
multiple rank values simultaneously. These approaches create a circular dependency — you must
train to discover the allocation, but the allocation shapes training — and require per-experiment
optimization rather than a reusable, pre-computed signal.

We ask a different question: **Does the pre-trained model already carry a signal that predicts
which layers need more rank — before any fine-tuning begins?**

Our key observation is that LLaMA-3.1-8B's layer-wise MLP activation sparsity provides exactly
such a signal — and it is far more stable than one might expect. Using forward hooks to measure
the fraction of near-zero MLP activations across 512 calibration samples, we find that the
32-layer sparsity profile is remarkably invariant: across four diverse calibration distributions
(Alpaca, WikiText-103, SST-2 validation, MNLI validation), the intraclass correlation coefficient
ICC$(3,k)=0.9846$, with all six pairwise Kendall's $\tau \geq 0.734$. The layer rank ordering
is also invariant to epsilon threshold choice: all six cross-epsilon $\tau$ values exceed $0.96$
for $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$.

This result — near-perfect stability of the layer sparsity fingerprint — is surprising. The
existing literature on activation sparsity (e.g., Li et al.~\shortcite{li2022lazy}; Mirzadeh et
al.~\shortcite{mirzadeh2023relu}) documents the \emph{existence} of activation sparsity in
large transformers. But whether it constitutes a \emph{reliable, distribution-invariant
structural fingerprint} suitable as a prior for rank allocation decisions has not been
established. Our work provides this characterization, finding that the fingerprint is robust enough
to be extracted from any available calibration set in a single forward pass.

We make the following contributions:

\begin{enumerate}
  \item \textbf{Structural fingerprint characterization.} We provide the first systematic
    characterization of LLaMA-3.1-8B's layer-wise MLP activation sparsity profile, demonstrating
    significant layer-wise heterogeneity (CV$=0.544$) with a systematic depth gradient: early
    layers (0--2) consistently exhibit the highest sparsity, deep layers the lowest.

  \item \textbf{Cross-distribution stability.} We show that the sparsity profile is stable
    across four calibration distributions with ICC$(3,k)=0.9846$ and $\tau_{\min}=0.734$ — far
    exceeding our conservative gate threshold of ICC$>0.75$. This means any practitioner can use
    any available dataset for calibration and obtain the same layer rank ordering.

  \item \textbf{Threshold invariance.} We demonstrate that layer rank ordering is invariant to
    epsilon threshold choice across $[0.001, 0.1]$ (all cross-epsilon $\tau > 0.96$), eliminating
    the need to tune this hyperparameter.

  \item \textbf{Foundation for zero-cost rank allocation.} We establish the empirical foundation
    for using activation sparsity as a pre-training structural prior for LoRA rank allocation,
    with the rank-predictive utility (H-M3) and end-to-end performance (H-M4) identified as
    immediate next steps.
\end{enumerate}

The remainder of this paper is organized as follows: Section~2 reviews related work on adaptive
rank methods and activation sparsity. Section~3 describes our measurement methodology.
Section~4 details experimental setup. Section~5 presents results. Section~6 discusses
implications and limitations. Section~7 concludes.
