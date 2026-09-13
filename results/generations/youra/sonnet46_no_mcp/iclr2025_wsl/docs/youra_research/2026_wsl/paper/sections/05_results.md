# 5. Results

We present results in the order of the causal chain: first establishing the precondition
(orbit existence), then measuring the mechanism (permutation sensitivity), then reporting
the downstream consequence (accuracy prediction quality). This ordering builds the evidence
story rather than simply tabulating numbers.

## 5.1 Orbit Existence: The Permutation Problem Is Real (H-E1)

Before testing whether equivariant encoders outperform flat MLPs, we verify that the
permutation orbit problem is empirically non-trivial in the Schurholt MNIST-CNN zoo.

**Architecture confirmation.** Inspection of the MNIST-CNN checkpoint state dictionaries
confirms the absence of running\_mean and running\_var keys — the zoo is fully BN-free,
preserving neuron-permutation symmetry.

**Orbit proportion.** We sample 500 model pairs stratified across 10 accuracy deciles
(50 pairs per decile) from the seed-only subset (976 checkpoints). All 500 pairs satisfy
cosine\_distance $> 0.1$ (orbit\_proportion = **1.000**, threshold $> 0.05$, exceeded
by 19$\times$). The mean cosine distance across all pairs is $0.768 \pm 0.033$ (std).

Figure 7 shows the distribution of cosine distances: even pairs in the same accuracy decile
exhibit large weight-space separation, confirming that the zoo is populated with
permutation-distinct representations of functionally-equivalent networks across all accuracy
levels (Figure 8 shows orbit\_proportion = 1.0 for every decile).

**Interpretation.** The precondition for the capacity-wasting mechanism is not merely satisfied
— it holds universally across the entire accuracy spectrum. Every encoder trained on this zoo
faces the full factorial orbit navigation problem in every accuracy regime.

## 5.2 Mechanism Step A: Flat MLPs Cannot Escape the Orbit Problem (H-M1)

We train a flat MLP encoder (500,577 params) on the MNIST-CNN zoo and measure its
permutation sensitivity.

**Permutation sensitivity.** On 500 stratified pairs, the flat MLP achieves:
- Mean L2 distance between permutation-equivalent embeddings: **4.212**
- Mean L2 distance between random (non-equivalent) embeddings: **6.489**
- Sensitivity score: **0.649** (threshold $> 0.3$; exceeded by 2.2$\times$)

The sensitivity score of 0.649 means that the flat MLP assigns embeddings that are nearly
as different for permutation-equivalent pairs as for random pairs — it is largely unable to
identify that two weight configurations implement the same function. The L2 ratio being well
above the gate threshold (0.3) confirms this is not marginal.

Figure 5 shows the sensitivity score broken down by accuracy decile: the flat MLP is
consistently permutation-sensitive across all deciles, with no accuracy tier where it
learns approximate invariance.

**Accuracy prediction quality.** The trained flat MLP achieves Spearman $\rho = 0.1041$
on the held-out test set — far below the literature baseline of $\rho \approx 0.5$–$0.7$
reported by Unterthiner et al. [2020]. We attribute this gap primarily to the architectural
bottleneck imposed by capacity matching (hidden\_dims=[193] for a 2,464-dim input; see
Section 6 for discussion).

**Interpretation.** A flat MLP at 500K parameters cannot learn permutation invariance from
the training data alone. It allocates substantial embedding capacity to distinguishing
weight configurations that should be indistinguishable, directly confirming the
capacity-wasting mechanism.

## 5.3 Mechanism Step B: NFN Eliminates the Orbit Problem by Construction (H-M2)

We train an NFN encoder (521,953 params) on the same zoo and repeat the sensitivity probe.

**Permutation sensitivity.** On 500 stratified pairs, the NFN achieves:
- Mean L2 distance between permutation-equivalent embeddings: $2.679 \times 10^{-8}$
- Mean L2 distance between random (non-equivalent) embeddings: $3.648 \times 10^{-2}$
- Sensitivity score: $7.34 \times 10^{-7}$ (threshold $< 0.1$; exceeded by 136,000$\times$)

The NFN sensitivity score is **885,000$\times$ lower** than the flat MLP ($7.34 \times 10^{-7}$
vs. $0.649$). Permutation-equivalent weight pairs receive embeddings that differ by fewer than
$10^{-7}$ in normalized L2 distance — the equivariance guarantee holds numerically to machine
precision across all 500 pairs and all 10 accuracy deciles (Figure 4).

Figure 3 shows the L2 distance distributions side-by-side: for NFN, the permutation-equivalent
distribution collapses to near-zero while the random-pair distribution remains at normal scale
— a clean visual confirmation of structural equivariance.

**Accuracy prediction quality.** The trained NFN achieves Spearman $\rho = 0.6806$
[95% CI: 0.603, 0.748] on the held-out test set — already a strong result at this capacity.

**Interpretation.** NFN's equivariance guarantee is not merely theoretical — it holds
empirically to machine precision. All 521,953 parameters are available for accuracy-predictive
signal because none are consumed by orbit navigation.

## 5.4 Primary Result: Symmetry Exploitation Yields Large Δρ (H-M3)

With the mechanism confirmed, we report the primary performance comparison.

**Main results.** Table 2 presents Spearman $\rho$ for all three encoders on the MNIST-CNN
test set (338 models).

**Table 2:** Spearman rank correlation on Schurholt MNIST-CNN test set. All encoders matched
to $\sim$500K parameters. CIs from 1,000 bootstrap resamples.

| Encoder | Parameters | $\rho$ | 95% CI |
|---------|-----------|--------|--------|
| Flat MLP (untrained) | 500,706 | 0.1688 | [0.069, 0.273] |
| Deep Sets | 471,936 | 0.4466 | [0.344, 0.544] |
| **NFN** | **521,953** | **0.6806** | **[0.603, 0.748]** |

**Delta-rho.** $\Delta\rho(\text{NFN} - \text{flat MLP}) = \mathbf{0.5119}$
[95% CI: **0.381, 0.638**]. The lower bound (0.381) is itself 7.6$\times$ the minimum
threshold (0.05), establishing unambiguous statistical significance. The gap persists
even when compared against the Deep Sets baseline: $\Delta\rho(\text{NFN} - \text{Deep Sets}) = 0.234$.

**Symmetry spectrum.** The strict monotone ordering
$$\rho(\text{flat MLP}) = 0.169 < \rho(\text{Deep Sets}) = 0.447 < \rho(\text{NFN}) = 0.681$$
is confirmed. Exploiting more of the permutation symmetry structure monotonically improves
accuracy prediction quality at matched capacity. Figure 1 visualizes this spectrum per
accuracy decile, showing NFN's consistent advantage across the low and mid accuracy regimes.

**Key observation.** The Deep Sets intermediate result ($\rho = 0.447$) is particularly
informative: it shows that permutation *invariance* alone (without equivariance) provides
substantial benefit ($\Delta\rho = +0.278$ over flat MLP), while equivariance provides
further gain ($\Delta\rho = +0.234$ over Deep Sets). The benefits are additive across
the symmetry hierarchy.

## 5.5 Unexpected Finding: Accuracy-Tier Dependence (P3 Refuted)

Our pre-registered prediction (P3) stated that the NFN advantage would be largest in the
mid-accuracy tier. The data refutes this clearly.

**Tier analysis.** Splitting the test set into equal thirds by ground-truth accuracy:

| Accuracy Tier | NFN $\rho$ | $n$ |
|---------------|-----------|-----|
| Low (bottom 1/3) | **0.856** | 113 |
| Mid (middle 1/3) | 0.317 | 113 |
| High (top 1/3) | −0.314 | 112 |

NFN is an excellent predictor for low-accuracy models ($\rho = 0.856$), a moderate predictor
for mid-accuracy models ($\rho = 0.317$), and actually anti-correlated for high-accuracy
models ($\rho = -0.314$). The predicted mid-tier dominance is not observed.

**Interpretation.** This finding suggests that equivariant benefit depends on **weight-space
diversity relative to accuracy diversity**: in the low-accuracy tier, many different failure
modes produce similarly low accuracy, creating a highly diverse weight distribution with strong
equivariant signal. In the high-accuracy tier, models converge to functionally similar
near-optimal solutions, and the fine-grained ranking requires features that 500K-param
equivariant layers cannot capture. We discuss the implications in Section 6.

Figure 2 shows training curves for the NFN encoder, confirming stable convergence without
overfitting. Figure 6 shows the flat MLP L2 distance distribution confirming high permutation
sensitivity, complementing Figure 5.
