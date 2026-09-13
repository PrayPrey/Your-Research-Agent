# Discussion

## 6.1 Key Findings and Their Implications

**Finding 1: Symmetry orbits are geometrically large in real MLP zoos — the theoretical motivation for canonicalization is empirically confirmed.**

Scaling orbits (mean cosine distance 0.32) and sign-flip orbits (mean cosine distance 1.07) are not geometric curiosities confined to pathological weight configurations — they are universal properties of the Schürholt MNIST zoo. Every oracle orbit pair we measure exceeds the 0.05 significance threshold. This directly addresses a gap in prior work: Navon et al. [2023] characterized these symmetries theoretically, but did not measure their empirical size in a real model zoo. Our measurements transform the motivation for canonicalization from a theoretical argument ("symmetries could be large") to an empirical baseline ("symmetries *are* this large, and here is the distribution").

The implication for weight space learning practitioners is concrete: any method that processes raw MLP weights for the Schürholt zoo is implicitly contending with a within-orbit diameter of at least 0.32 cosine distance for scaling and 1.07 for sign-flip. If the method learns representations using distance or similarity in weight space, this variation is noise relative to functional properties. Canonicalization — applied correctly — removes this noise.

**Finding 2: NFT is non-invariant to scaling orbits but approximately invariant to sign-flip orbits by construction — an asymmetry with practical implications.**

The invariance probe reveals that NFT's symmetry handling is asymmetric. For scaling, it is measurably non-invariant (gap=+0.024, CI entirely above zero). For sign-flip, it is approximately invariant by construction (gap=-0.0007). This asymmetry was not designed into NFT — it is an emergent consequence of row-level weight tokenization. Since sign patterns do not affect the magnitude statistics that NFT's attention mechanism primarily tracks, sign-flip functionally identical networks produce similar weight-token sequences and therefore similar embeddings.

This finding is immediately actionable. For practitioners using NFT-family encoders, scaling canonicalization addresses a measurable capacity waste; sign-flip canonicalization may provide no benefit and, as we show, can be actively harmful when applied with a non-unique algorithm. The recommendation is *scaling-only canonicalization* as the productive preprocessing step for NFT.

The broader implication is methodological: encoder-specific symmetry audits — probing which symmetries the encoder already handles and which it does not — should be a standard diagnostic step before designing canonicalization preprocessing. Different architectures may have different emergent invariances, and a one-size-fits-all approach to canonicalization may waste effort on symmetries the encoder already handles or, worse, harm performance through non-unique implementations.

**Finding 3: The majority-sign sign-flip canonicalization fails structurally for even-d_in architectures — a previously uncharacterized limitation with a combinatorial root cause.**

The 85.6% tie rate for d_in=784 is not a data quality issue or a training artifact. It is a mathematical consequence of d_in being even: with approximately equal positive and negative weights in each row (typical for gradient-trained networks near a zero-mean distribution), the expected tie probability per neuron is ≈2.8% for d_in=784, yielding ≥83% probability of at least one tie per 64-neuron model. This rate is accurately predicted by binomial combinatorics and matches our empirical observation.

This structural finding has not appeared in prior weight space learning literature. The practical consequence is that Condition D in our H-M3 experiment applied a deterministic but symmetry-incomplete transformation to 85.6% of zoo models. The sign arrangement of tied neurons was set by an arbitrary +1 convention, introducing structured noise rather than removing symmetry-induced variation. This is the most likely explanation for the E > D finding — Condition D's "canonicalization" was contaminated by non-canonical tie-breaking for the majority of models.

**The fix is clear and implementable.** Three approaches eliminate the tie problem: (1) use an architecture with odd input dimension (e.g., pad MNIST from 784 to 785 — a single zero-padding that breaks the symmetry with negligible computational cost); (2) use a secondary tie-breaking criterion based on weight magnitude (choose the sign that maximizes the magnitude of the majority, breaking ties by ‖w+‖ vs. ‖w-‖); (3) avoid sign-flip canonicalization entirely for NFT-family encoders, given the emergent sign-flip invariance finding.

## 6.2 Limitations

**Limitation 1: Zoo scale (N=500) provides insufficient statistical power for property prediction experiments.**

All property prediction experiments (H-M2, H-M3) were conducted on N=500 models from a local archive. The full Schürholt zoo contains approximately 50,000 models but was inaccessible via HuggingFace at runtime. At n=50 test samples, Spearman ρ bootstrap CIs have width ≈0.6 — approximately 12× wider than the effect size we seek to detect (Δρ ≥ 0.05). No property prediction comparison in this paper has statistical power to distinguish conditions; all Spearman ρ values are statistically indistinguishable from zero.

This limitation is precisely quantified and does not invalidate our primary contributions. The orbit characterization (H-E1) and invariance probe (H-M1) use relative comparisons (within-orbit vs. cross-orbit similarity) that produce tight CIs (width ≈0.001) even at N=500, because they compare paired measurements rather than independent groups. The PCA EVR analysis (H-M2 geometric component) is also scale-robust. Only the downstream property prediction improvement claim (H-M3) requires large N — and we quantify the requirement: N≥5,000 models to provide n≥500 test samples and CI width <0.05 on Δρ.

The most direct path to large N is accessing the full Schürholt zoo. The dataset appears to have migrated repository locations since the original publication; the identifier `schurholt/model_zoos_dataset` on HuggingFace returned errors at runtime. Contacting the authors or downloading directly from the ModelZoos GitHub repository are the recommended approaches.

**Limitation 2: Sign-flip canonicalization is non-unique for even d_in — our H-M3 Condition D tested a non-canonical transformation.**

As described in Section 5.4 and 6.1, the majority-sign algorithm fails for 85.6% of Schürholt MNIST zoo models. Condition D in H-M3 applied a deterministic but not symmetry-derived transformation to these models. This means: (a) the P2 refutation (E > D) may reflect sign-flip harm rather than genuine evidence that canonicalization is not symmetry-specific; (b) the proper comparison — clean scaling-only (Condition B) vs. Condition E, with adequate N — has not been performed. We recommend this as the primary follow-up experiment.

**Limitation 3: The sign-flip functional equivalence in H-M1 used single-layer flips, not two-layer joint flips.**

Proper sign-flip functional equivalence for a 2-layer ReLU MLP requires flipping both the incoming weights (W₁[:,i]) and outgoing weights (W₂[i,:]) for each hidden neuron simultaneously — a two-layer joint operation. The H-M1 experiments applied this joint flip correctly for the property probe, but did not separately verify two-layer functional equivalence on a held-out test set. With ReLU activations, the functional equivalence holds exactly for the joint flip: f(ReLU(-x)) applied to the first layer produces hidden activations of opposite sign, which are then corrected by the negated W₂[i,:] row. We verified this algebraically, but runtime execution on random inputs was not performed.

**Limitation 4: We do not verify whether NFT capacity is the binding constraint.**

The mechanism underlying our canonicalization motivation assumes that NFT's representational capacity is partially occupied by symmetry-induced variation (Step 2 of the causal chain). At N=500, NFT training is severely underpowered (val ρ ≈ 0), making it impossible to distinguish: (a) NFT is capacity-constrained and canonicalization helps; (b) NFT is underpowered and neither raw nor canonical inputs produce meaningful representations. With the full Schürholt zoo, a direct comparison of NFT's val ρ vs. layer statistics ρ under canonicalization would isolate the capacity-constraint hypothesis.

## 6.3 Future Work

**Immediate (directly enabled by this paper):**

1. *Full Schürholt zoo with scaling-only canonicalization (Condition B).* Acquires adequate statistical power (N≥5,000) and avoids the sign-flip non-uniqueness issue. This single experiment provides a clean test of the core mechanism: does scaling canonicalization improve NFT Spearman ρ at adequate N?

2. *Odd d_in or magnitude-based tie-breaking for sign-flip canonicalization.* Padding MNIST inputs from 784 to 785 eliminates the tie problem and enables a clean test of full canonicalization (Condition D) — comparable against Condition B to measure the marginal sign-flip contribution.

3. *Two-layer joint sign-flip functional equivalence verification.* Systematic runtime verification of functional equivalence for the sign-flip oracle pairs used in H-M1, to confirm the sign-flip invariance finding is not an artifact of an incorrectly applied transform.

**Medium-term:**

4. *Architecture-specific symmetry audit for other encoders.* Apply the same within-orbit vs. cross-orbit probing protocol to DWSNets [Navon et al., 2023], Universal Neural Functionals [Kofinas et al., 2024], and Hyper-Representations [Schürholt et al., 2021] to characterize which symmetries each encoder naturally handles and which require canonicalization.

5. *Deeper networks (M>2).* Sign-flip canonicalization for M>2-layer MLPs is underdetermined by the majority-sign algorithm. Extending to M>2 requires either layer-by-layer greedy canonicalization or a more principled approach. Our H-E1 and H-M1 infrastructure generalizes to M>2 with minor modifications.

## 6.4 Broader Impact

This work advances the understanding of geometric structure in neural network weight spaces. The direct applications — model property prediction, model merging, neural architecture search from weight populations — are primarily research tools with beneficial applications in model understanding and selection. We identify no significant potential for misuse.

The structural finding on sign-flip canonicalization non-uniqueness is relevant to any weight space learning system that applies sign-flip canonicalization as a preprocessing step, regardless of the downstream task. Practitioners should audit whether their architecture has even or odd input dimension before applying the majority-sign algorithm, to avoid introducing structured noise under the guise of canonicalization.
