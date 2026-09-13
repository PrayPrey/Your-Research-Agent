# Abstract

Low-Rank Adaptation (LoRA) fine-tunes large language models efficiently, but typically assigns
uniform rank across all layers — ignoring the heterogeneous computational roles that emerge
during pre-training. Existing adaptive rank methods learn the allocation during training, creating
a circular dependency and per-experiment overhead. We ask whether the pre-trained model already
encodes a reliable signal for rank allocation decisions.

We characterize the layer-wise MLP activation sparsity profile of LLaMA-3.1-8B as a structural
fingerprint measurable from a single forward pass. Using forward hooks on 512 calibration samples,
we find that this fingerprint exhibits significant heterogeneity across 32 layers (CV$=0.544$)
and is remarkably stable: across four diverse calibration distributions, the intraclass
correlation ICC$(3,k)=0.9846$, and across epsilon thresholds spanning two orders of magnitude,
all cross-threshold Kendall's $\tau$ exceed $0.96$. Any calibration dataset, any threshold choice
— the same layer rank ordering emerges.

This near-perfect stability suggests that LLaMA-3.1-8B's sparsity profile reflects pre-training
geometry rather than input content, establishing it as a zero-cost structural prior for LoRA rank
allocation. We provide the empirical foundation; whether the fingerprint predicts rank requirements
and enables efficient allocation at 60\% parameter budget is the natural and now well-motivated
next experiment.
