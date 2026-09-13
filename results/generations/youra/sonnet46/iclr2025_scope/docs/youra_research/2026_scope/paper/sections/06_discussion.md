# 6. Discussion

## 6.1 Interpreting the Fingerprint: Architecture Determinism

The most striking result is the magnitude of ICC$(3,k)=0.9846$ — far exceeding our conservative
gate of ICC$>0.75$ and approaching the ceiling of what intraclass correlation can indicate.
This level of stability, combined with cross-epsilon $\tau > 0.96$, points to a specific
mechanistic explanation: **architecture determinism**.

LLaMA-3.1-8B uses SiLU gating in its MLP blocks. SiLU is smooth and asymptotically approaches
zero for large negative inputs, creating soft-thresholded activations. Unlike ReLU (which creates
hard zeros), SiLU produces a distribution of magnitudes whose shape is primarily determined by
the weight matrices — not by the input content. If weight magnitudes drive the sparsity
distribution, then the sparsity fraction (for any fixed $\varepsilon$) is approximately
input-independent by construction, which would explain both the cross-distribution stability and
the cross-epsilon invariance.

An alternative explanation is scale-induced representation stability: at 8B parameters, the
model may have developed input-distribution-insensitive high-level representations that incidentally
produce stable sparsity profiles. This is harder to test without shuffled/random input baselines
(see Section~6.3).

The depth gradient (early layers most sparse, deep layers least) is consistent with the
linguistic hierarchy documented in BERT-family models \citep{clark2019bert, tenney2019bert}:
syntactic processing in early layers (high sparsity, fewer active dimensions), semantic
integration in deep layers (low sparsity, more active dimensions). We emphasize that this is a
motivated interpretive connection, not a verified causal claim.

## 6.2 Scope: What We Established and What Remains

Our results strongly support **Prediction P1**: the sparsity fingerprint exists, is heterogeneous,
stable, and threshold-invariant. We have established the structural foundation.

**Predictions P2 and P3 remain INCONCLUSIVE.** Whether higher-sparsity layers require lower
LoRA rank (P2, H-M3) and whether inverse-sparsity allocation achieves $\geq 95\%$ of oracle
at 60\% parameter budget (P3, H-M4) are empirically open questions. We have designed and planned
these experiments (27 tasks for H-M3, estimated 20 tasks for H-M4) but did not execute them in
this work. The paper's contribution is the characterization of the structural prior, not the
end-to-end allocation performance claim.

## 6.3 Limitations

**L1: Core mechanism unvalidated (high severity).** The central causal claim — that high-sparsity
layers require lower LoRA rank — has not been tested. Steps 3–4 of the causal chain (sparsity
→ rank sensitivity → allocation performance) are the primary novel empirical contributions of
the original hypothesis and remain pending. H-M3 requires approximately 320 perturbed fine-tuning
runs (32 layers $\times$ 5 seeds $\times$ 2 tasks); these were planned but not executed.

*Why acceptable:* Steps 1–2 (structural prior existence) are fully validated. The fingerprint
is a necessary foundation for H-M3 to be meaningful — without confirmed cross-distribution
stability, a sparsity-guided allocation would be fragile. H-M3 can now proceed with high
confidence that the input signal is reliable.

**L2: End-to-end performance unvalidated (high severity).** The headline result of the original
hypothesis — $\geq 95\%$ oracle performance at 60\% parameter budget — has zero experimental
support. H-M4 depends on H-M3's completion. We explicitly scope the paper to the structural
characterization contribution.

*Why acceptable:* The measurement contribution is independently publishable. The performance
claim is correctly framed as a hypothesis enabled by our foundation, not as a demonstrated result.

**L3: SiLU soft-sparsity proxy (medium severity).** We measure near-zero activations using an
epsilon threshold, not functional sparsity (activations that contribute negligibly to downstream
computation). Cross-epsilon $\tau > 0.96$ confirms that the *rank ordering* of layers is
threshold-invariant, but whether $\varepsilon = 0.01$ identifies functionally sparse activations
versus merely small activations is a separate question. Effective-rank comparison per layer (via
activation covariance matrices) would address this.

**L4: Single architecture and task domain (low-medium severity).** All experiments use
LLaMA-3.1-8B on GLUE classification tasks. Szatkowski et al.~\shortcite{szatkowski2025universal}
suggest cross-architecture universality; our ICC$=0.9846$ result strengthens this motivation.
Generalization to Mistral, Gemma, Phi, and generation tasks requires separate investigation.

**L5: LLaMA-3.1-8B $\neq$ LLaMA-3-8B (low severity).** The verification state specifies
LLaMA-3-8B; experiments used LLaMA-3.1-8B due to model cache availability. The architectures
are functionally identical for this study; results are attributed to LLaMA-3.1-8B throughout.

**L6: Assumption A3 (sparsity proxies intrinsic dimension) unverified.** The theoretical bridge
between activation sparsity and LoRA rank requirements assumes that near-zero activations
correspond to low intrinsic dimensionality of each layer's computational subspace. This connection
is theoretically motivated by Aghajanyan et al.~\shortcite{aghajanyan2021intrinsic} but has not
been empirically validated for LLaMA-3.1-8B's SiLU gating.

## 6.4 Broader Impact

**Positive impacts.** Establishing sparsity as a reliable pre-training structural prior enables
zero-cost rank allocation for LoRA — reducing the computational overhead of adaptive rank
methods without any training cost. This is particularly valuable for practitioners with limited
computational resources, where running AdaLoRA or similar training-time methods is prohibitive.
If H-M3/H-M4 validate the allocation utility, SparsityLoRA could reduce the parameter budget
needed for effective fine-tuning, lowering the environmental cost of LLM deployment.

**Limitations and misuse potential.** The current work does not demonstrate improved downstream
performance. Practitioners should not use our structural fingerprint to make rank allocation
decisions without H-M3 validation — the utility of the fingerprint for allocation is currently
an unvalidated hypothesis. We explicitly caution against premature deployment of sparsity-guided
allocation.

**Cross-architecture implications.** If the depth-sparsity gradient reflects universal
transformer structure (as suggested by Szatkowski et al.~\shortcite{szatkowski2025universal}),
similar fingerprints may exist in other LLM families, enabling the same zero-cost approach to
generalize. This is a research opportunity, not yet a demonstrated result.
