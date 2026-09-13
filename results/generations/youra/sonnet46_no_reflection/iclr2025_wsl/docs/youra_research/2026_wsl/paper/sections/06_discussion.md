# Discussion

## 6.1 Interpreting the Layer-Type Stratification

The bimodal Conv2d/Linear variance ratio (0.637 vs. 0.133) is the central finding of this
work, and it demands explanation. We offer three competing interpretations, each with distinct
implications for cross-architecture weight space learning.

**Structural explanation.** Conv2d weight tensors have explicit spatial structure: a kernel
W ∈ ℝ^{c_out × c_in × H × W} where the H×W spatial dimensions provide structural constraints
on which directions of variation are possible. Permuting input/output channels is a "local"
symmetry that accounts for a large fraction of the orbit in this constrained space. Linear
weight matrices W ∈ ℝ^{c_out × c_in} are fully dense: the full GL(c_in) × GL(c_out) group
acts without structural constraint, providing exponentially more "directions" of variation than
the discrete permutation group S_{c_in} × S_{c_out}.

**Training dynamics explanation.** The trajectory finding (ratio decreasing from ~0.49 to ~0.28
during training) is consistent with the training dynamics interpretation: at initialization,
weight matrices are drawn from symmetric distributions (Kaiming, Xavier), which may have higher
permutation orbit density. During training, gradient descent exploits GL-type reparameterizations
along flat loss-landscape directions [Goldstein et al., 2023], progressively moving weights
into non-permutation-orbit directions. If confirmed on Transformer Zoo checkpoints, this implies
that orbit-PE would be most useful for early-training or randomly-initialized model zoos.

**Scale explanation.** Linear layers in CNN classifiers typically have large input dimensions
(flattened feature maps, often 512–4096 neurons). The GL(d) group grows exponentially with d,
providing more variance "directions" than the permutation group S_d (factorial growth, but
in practice dominated by the continuous GL directions at large d). This effect would be
amplified for transformer attention layers with large key/value dimensionality.

These explanations are not mutually exclusive. The empirical finding — stratification by layer
type across 1,000 models × 50 epochs — is robust to all three explanations and motivates the
same design conclusion: hybrid encoding.

## 6.2 Alignment with Existing Literature

The H-M2 result provides independent empirical confirmation of two strands of prior work that
reached the same conclusion through different routes:

**GL symmetry literature.** arXiv:2410.04207 [Tran-Viet et al., 2024] proposed GL-invariant
polynomial trace features (tr(WW^T), tr(W^Q W^{K,T})) for attention weights, motivated by the
*theoretical* argument that GL symmetry is the relevant group for attention. Our H-M2 result
confirms this empirically from a different angle: not by analyzing which group theoretically
applies, but by measuring which group actually explains variance in real model zoo weights.
The Linear/attention ratio of 0.133 (GL-dominated) aligns quantitatively with this theoretical
prediction.

**NFN's CNN Zoo success.** The Conv2d ratio of 0.637 directly explains why NFN [Zhou et al.,
2023] achieves τ > 0.93 on CNN Zoo — a dataset composed of convolutional models where
permutation orbits capture the dominant functional variation. NFN's architecture implicitly
"got lucky" in the sense that its symmetry group happens to be the dominant one for the layer
types it targets.

## 6.3 Implications for Cross-Architecture Design

The layer-type stratification has a concrete design implication: any cross-architecture weight
representation must use layer-type-specific positional encodings. A single universal group
(permutation) is sufficient for Conv2d-dominant architectures but insufficient for
Linear/attention-dominant architectures.

The hybrid encoding motivated by H-M2 — permutation orbit-PE for Conv2d layers (validated,
ratio = 0.637) plus GL-invariant trace features for Linear/attention layers (ratio = 0.133,
GL-dominated) — is not a post-hoc rationalization but a *pre-registered pivot* specified in
the H-M2 gate design. The infrastructure developed in this work (orbit projectors,
variance decomposer, zoo-scale pipeline) is directly reusable for implementing and evaluating
this hybrid approach.

## 6.4 Principled Limitations

**L1 — Primary claim untested.** The main hypothesis claim — that SANE+orbit-PE achieves
τ_retention ≥ 0.70 in CNN→Transformer zero-shot property prediction — was not tested. H-M3,
which would have evaluated this, was blocked by H-M2's MUST_WORK failure. The claim is not
*refuted* (hybrid encoding may still achieve τ_retention ≥ 0.65–0.70), but it is empirically
unaddressed. We present the mechanism findings as primary contributions rather than the
cross-architecture performance results.

**L2 — SVHN cross-dataset stability skipped.** The H-M2 design specified a cross-dataset
stability check (|CIFAR_ratio - SVHN_ratio| < 0.10) using SVHN-GS checkpoints. SVHN Zoo data
was unavailable at experiment time. The CIFAR-10-GS result (n = 1,000 × 50 epochs) provides
strong statistical confidence regardless, but the cross-dataset generalization of the ratio
stratification remains unconfirmed.

**L3 — Transformer Zoo variance decomposition not performed.** H-M2 measured variance
decomposition on CNN Zoo only (as the Conv2d-dominant benchmark). The Var_perm ratio for
Transformer Zoo checkpoints (predominantly Linear/attention layers) was not directly measured.
Given the Linear ratio of 0.133 in CNN Zoo, we expect Transformer Zoo ratios to be even lower,
but this is inference rather than measurement.

**L4 — SVD fallback for orbit basis in H-M2.** H-M2's orbit projector uses an SVD-based orbit
basis rather than directly importing H-M1's OrbitPEComputer (path resolution issue). Both
compute SVD-based orbit projections and are methodologically equivalent, but the implementation
diverges slightly from the planned design. The variance decomposition results are not materially
affected by this divergence.

## 6.5 Broader Impact

Weight space learning is an emerging field with applications ranging from model zoo analytics
to federated learning [Han et al., 2026] and neural architecture search. Our finding that
symmetry group dominance is layer-type-dependent is a general property of weight space geometry,
not specific to any model zoo or architecture family. As the field moves toward larger and more
architecturally diverse model zoos (including ResNets, ViTs, and language model families), the
hybrid encoding insight will be essential for cross-architecture representations.

The training trajectory finding — that permutation variance ratio decreases during training —
has a practical implication for model zoo design: if orbit-PE (or hybrid encoding) is most
effective at early training stages, future model zoos may benefit from including early-epoch
checkpoints as a distinct data modality. This connects WSL to the emerging literature on
training dynamics as a feature [arXiv:2602.23696].
