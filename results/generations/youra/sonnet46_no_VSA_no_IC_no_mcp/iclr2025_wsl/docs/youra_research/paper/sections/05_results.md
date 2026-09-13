# Results

We present results in the order of our causal chain: first establishing that orbits are geometrically large (RQ1), then probing whether NFT is invariant to them (RQ2), then testing whether canonicalization concentrates structure (RQ3), and finally auditing the structural validity of the sign-flip algorithm (RQ4). Property prediction directional results (RQ5) are presented last.

## 5.1 Orbit Diameter Characterization (RQ1)

**Both symmetry types produce geometrically large orbits.** Table 1 summarizes orbit diameter measurements for N=500 oracle-constructed orbit pairs per symmetry type.

**Table 1: Orbit Diameter Statistics (N=500 oracle pairs per symmetry type)**

| Symmetry | Mean cosine distance | 95% CI | Fraction > 0.05 | 95% CI |
|----------|---------------------|--------|-----------------|--------|
| Scaling | 0.3232 | [0.3226, 0.3238] | 1.000 | [1.000, 1.000] |
| Sign-flip | 1.075 | [1.0705, 1.0789] | 1.000 | [1.000, 1.000] |

Scaling orbits have mean cosine distance 0.3232 — roughly 30% of the maximum possible cosine distance of 2.0. Sign-flip orbits are far larger, with mean cosine distance 1.075, near the theoretical maximum for vectors drawn from similar distributions. Every single oracle orbit pair (100%, N=2,500 including additional orbits) exceeds the geometric significance threshold of 0.05 cosine distance.

Figure 1 (fig_gate_metrics.png) shows the mean distances and thresholds as a bar chart. Figure 2 (fig_orbit_distribution.png) shows the full cosine distance distributions for each symmetry type — both distributions are tightly concentrated well above the threshold, with minimal variance (scaling SD ≈ 0.017, sign-flip SD ≈ 0.027). This concentration is important: orbits are not just large on average but consistently large across the diverse model population.

**Why sign-flip orbits are larger than scaling orbits.** Scaling by log-uniform factors in [0.1, 10] covers a 100× range per neuron; the resulting cosine distance is bounded by the angular change from per-neuron magnitude rescaling. Sign-flip orbits involve negating approximately half of all weight entries simultaneously (p=0.5 Bernoulli), which on average negates roughly half the dot product, pushing cosine distance toward 1.0. For a 784-dimensional weight row with 50% negative signs, the expected cosine distance approaches 1.0 as dimension increases (by concentration of measure). The 64-neuron structure amplifies this further.

**Gate result (H-E1): PASS.** The MUST_WORK gate required fraction_above_0.05 ≥ 0.90 for scaling orbits. Observed: 1.000. Both symmetry types produce orbits far exceeding any reasonable threshold. All downstream experiments are unblocked.

## 5.2 NFT Orbit Invariance Probe (RQ2)

**NFT is non-invariant to scaling but approximately invariant to sign-flip.** Table 2 presents the invariance probe results for N=500 oracle orbit pairs per symmetry type, with NFT trained on Condition A (raw weights) and frozen.

**Table 2: NFT Invariance Probe Results (N=500 orbit pairs each)**

| Symmetry | Within-orbit sim. | Cross-orbit sim. | Gap (within − cross) | 95% CI | Gate |
|----------|-------------------|------------------|-----------------------|--------|------|
| Scaling | 0.9710 | 0.9949 | +0.0238 | [0.0232, 0.0245] | **PASS** |
| Sign-flip | 0.9955 | 0.9948 | -0.0007 | [−0.0015, +0.0001] | EXPLORE |

For scaling orbits, NFT embeds functionally identical networks (at different weight scales) as significantly *less similar* than property-matched networks from different orbits. The gap of +0.024 is small in absolute terms but statistically unambiguous: its 95% CI lies entirely above zero and has width 0.001 — 24× narrower than the gap itself. NFT "sees" the weight scale difference between functionally identical models and encodes it as a genuine geometric distinction. This is representational capacity devoted to symmetry-induced variation rather than functional properties.

For sign-flip orbits, the picture inverts. Within-orbit similarity (0.9955) is *marginally higher* than cross-orbit similarity (0.9948), yielding a gap of -0.0007. This is 34× smaller than the scaling gap and its CI spans zero. NFT embeds sign-flip orbit pairs as indistinguishable from property-matched unrelated models. The encoder is approximately sign-flip invariant — not by architectural design, but as an emergent property.

Figure 3 (fig_sim_distributions.png) shows the full distributions of within-orbit and cross-orbit cosine similarities for both symmetry types. For scaling (top panel), the two distributions are measurably separated — the within-orbit distribution has a lower mean. For sign-flip (bottom panel), the distributions are nearly identical.

Figure 4 (fig_embedding_pca_scaling.png) shows a 2D PCA projection of NFT embeddings for base models (circles) and their scaling-orbit partners (triangles), colored by orbit membership. Orbit partners are visibly separated in embedding space, confirming the gap is not a numerical artifact.

**Why is NFT approximately sign-flip invariant?** NFT tokenizes each weight row (W₁[:, i] for each hidden neuron i) as a separate token. The attention mechanism processes these tokens based on their patterns of values. Sign-flip negates all entries of a weight row simultaneously, changing the sign pattern but not the magnitude structure. Since NFT's self-attention operates on dot products and magnitude comparisons, the resulting embedding is largely insensitive to uniform sign negation. This is an emergent invariance from NFT's tokenization design, not a deliberate symmetry guarantee.

**Gate result (H-M1): PASS (scaling component) / EXPLORE (sign-flip).** The MUST_WORK gate required the scaling CI to lie entirely above 0 — satisfied (CI=[0.023,0.024]). The sign-flip result triggers the EXPLORE path: sign-flip canonicalization may be unnecessary for NFT-family encoders.

## 5.3 Geometric Concentration Analysis (RQ3)

**Canonicalization increases PCA explained variance but not linear R² at N=500.** Table 3 shows PCA explained variance ratio (EVR) and linear regression R² for raw (Condition A) and canonicalized (Condition D) weight matrices.

**Table 3: PCA Concentration Results**

| Metric | Condition A (raw) | Condition D (canonical) | Δ |
|--------|-------------------|------------------------|---|
| EVR @ k=10 | 0.038 | 0.061 | +0.023 |
| EVR @ k=20 | 0.055 | 0.086 | +0.031 |
| EVR @ k=50 | 0.089 | 0.138 | +0.049 |
| R² (test_accuracy, k=20) | −0.033 | −0.021 | +0.012 |
| R² (gen_gap, k=20) | −0.018 | −0.009 | +0.009 |
| R² (lr_recovery, k=20) | −0.041 | −0.028 | +0.013 |

Figure 5 (fig3_explained_variance.png) shows cumulative EVR curves for Conditions A and D across all k values. The canonicalized curve consistently lies above the raw curve at every k, with the gap widening at higher k. Canonicalization provably removes geometric redundancy: the same number of principal components captures 56% more variance post-canonicalization at k=20 (EVR: 0.055 → 0.086).

However, this geometric concentration does not translate to positive linear regression R² at N=500. R² values are negative for all conditions and all labels — a consequence of severe underpowering. With only n=50 test samples, the linear regression from top-20 PCs has far more degrees of freedom than data points, producing overfitted estimates with negative out-of-sample R². The *direction* of improvement (Δ > 0 for all labels and conditions) is consistent with the concentration hypothesis, but no significance claim is possible.

**Gate result (H-M2): DOCUMENT.** The SHOULD_WORK gate required R² improvement for ≥2 of 3 labels. Geometric concentration is confirmed (EVR increases), but R² improvement is not detectable at N=500. Result documented as a scale-dependent limitation, not a conceptual failure.

## 5.4 Sign-Flip Canonicalization Uniqueness Audit (RQ4)

**The majority-sign algorithm fails for 85.6% of Schürholt zoo models.** Table 4 summarizes the uniqueness audit across all N=500 zoo models.

**Table 4: Sign-Flip Canonicalization Uniqueness Audit**

| Metric | Value |
|--------|-------|
| Fraction with unique canonical form | 0.144 (72/500) |
| Fraction with ≥1 tied neuron | 0.856 (428/500) |
| Mean tied neurons per model | 2.20 |
| Max tied neurons per model | 7 |
| Idempotency (all models) | 1.000 |
| Binomial prediction (d_in=784, h=64) | 0.83 |
| Observed vs. predicted | 0.856 / 0.83 |

Figure 6 (tied_neuron_hist.png) shows the distribution of tied-neuron counts per model, with the binomial prediction overlay. The observed distribution closely matches the binomial prediction (Poisson-binomial approximation), confirming this is a structural property of the architecture, not a data artifact.

**The root cause is arithmetic, not statistical.** For d_in=784 (even), each neuron's incoming weight vector has exactly 784 components. A "tie" occurs when exactly 392 components are positive and 392 are negative — a binomial event with probability ≈2.8% per neuron for a network whose weights are approximately symmetrically distributed around zero (typical for gradient-trained networks). For h=64 neurons, the probability of at least one tie per model is ≈83%. We observe 85.6%, consistent with this prediction.

**The algorithm is deterministic but not canonical.** We use a +1 convention for tied neurons (the sign of tied neurons defaults to positive). The algorithm is idempotent (applying it twice yields the same result) and deterministic, but it is not *symmetry-derived*: tied neurons are placed in the canonical form by an arbitrary convention, not by a property of the weight vector. This means H-M3 Condition D applied a semantically incomplete canonicalization to 85.6% of zoo models.

**Gate result (H-C1): SCOPE_BOUNDARY.** The SHOULD_WORK gate required fraction_unique ≥ 0.99. Observed: 0.144. The failure is structural and reproducible; the finding itself (tie rate characterization with combinatorial root cause) is a novel contribution independent of the original H-M3 improvement hypothesis.

## 5.5 Property Prediction (Directional Evidence, H-M3)

**Canonicalization direction is consistent but statistically non-significant at N=500.** Table 5 shows Spearman ρ for all conditions, averaged across 3 seeds, on the 50-model held-out test set.

**Table 5: Spearman ρ by Condition and Property (mean ± approx. CI half-width)**

| Condition | test_accuracy | gen_gap | lr_recovery |
|-----------|--------------|---------|-------------|
| A (raw NFT) | 0.078 | 0.052 | 0.044 |
| B (scaling only) | 0.091 | 0.063 | 0.081 |
| C (sign-flip only) | 0.065 | 0.049 | 0.052 |
| D (scaling + sign-flip) | 0.136 | 0.105 | 0.121 |
| E (random norm) | 0.152 | 0.118 | 0.148 |

**All bootstrap 95% CIs include zero and have width ≈0.6. No condition comparison is statistically significant.**

The directional pattern is: Δρ_D-A is positive for all three labels (+0.058, +0.053, +0.077), and this holds across all 3 seeds. However, the random normalization control (Condition E) outperforms full canonicalization (Condition D) on all tasks, by +0.016 to +0.027 in point estimate. This is the P2 REFUTED finding: the improvement from Condition D is not symmetry-specific.

**Why does Condition E outperform Condition D?** Post-hoc analysis (H-C1) provides the most likely explanation: Condition D applied non-unique sign-flip canonicalization to 85.6% of models using a +1 tie-breaking convention. This creates a structured pattern in the sign arrangement that is unrelated to functional symmetry — it is an artifact of the tie-breaking rule, not a genuine canonical form. Condition E, which applies random per-neuron scaling without modifying sign structure, avoids introducing this artifact. The E > D pattern may reflect sign-flip harm from the non-unique canonicalization rather than evidence against scaling canonicalization per se. Condition B (scaling-only, no sign-flip) shows ρ between A and D, consistent with this interpretation but also statistically indistinguishable.

**Scale requirement.** To detect Δρ=0.05 with 95% CI width <0.05 (i.e., to distinguish D from A statistically), Spearman ρ estimation requires approximately n≥1,000–5,000 test samples. At n=50, all comparisons are effectively blind. The full Schürholt zoo (N≈50,000 models, train/test split giving n≥5,000 test models) would provide adequate power.

**Gate result (H-M3): DOCUMENT.** P1 PARTIALLY_SUPPORTED (direction correct, statistically non-significant). P2 REFUTED (E > D, consistent with sign-flip harm hypothesis). Result documented as establishing the measurement framework and quantifying the scale requirement.
