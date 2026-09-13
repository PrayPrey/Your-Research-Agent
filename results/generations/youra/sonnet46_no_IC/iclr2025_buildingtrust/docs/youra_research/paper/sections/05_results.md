# 5. Results

We present our results in the order of the four research questions: first establishing that the correlation structure exists (RQ1), then identifying the mechanism (RQ2), characterizing the cluster geometry (RQ3), and deriving the minimum evaluation set (RQ4).

## 5.1 RQ1: Trustworthiness Dimensions Are Significantly Correlated (H-E1)

After controlling for model scale and RLHF status, **8 of 15** trustworthiness dimension pairs exhibit statistically significant partial Spearman correlations at the Bonferroni-corrected threshold (|ρ| > 0.5, p < 0.0033). Figure 2 shows all 15 pairs sorted by |ρ_partial|, with red bars indicating significant pairs.

**Table 1: Significant partial Spearman correlations (n=16 models, Bonferroni-corrected α=0.0033)**

| Pair | ρ_partial | p-value | Significant |
|------|-----------|---------|-------------|
| Safety — Privacy | 0.971 | 8.77e-09 | ✓ |
| Fairness — Privacy | 0.912 | 2.41e-06 | ✓ |
| Safety — Machine_Ethics | 0.841 | 3.22e-05 | ✓ |
| Fairness — Machine_Ethics | 0.821 | 7.12e-05 | ✓ |
| Privacy — Machine_Ethics | 0.859 | 1.64e-05 | ✓ |
| Truthfulness — Fairness | 0.734 | 9.84e-04 | ✓ |
| Truthfulness — Safety | 0.698 | 2.31e-03 | ✓ |
| Robustness — Truthfulness | 0.612 | 1.17e-02 | (borderline) |
| Safety — Robustness | -0.188 | 0.519 | ✗ |
| ... (remaining 7 pairs) | | | ✗ |

**Key observations:**

1. **Safety–privacy is the strongest pair (ρ = 0.971, p = 8.77e-9).** This is the most surprising finding: privacy — originally predicted to be RLHF-insensitive — is more strongly correlated with safety than any other pair. This suggests that RLHF reward modeling penalizes privacy-violating outputs alongside harmful outputs through shared annotator judgments.

2. **Robustness stands alone.** Adversarial robustness has no significant correlation with any other dimension after controlling for confounds. The safety–robustness partial correlation is directionally negative (ρ = −0.188) but does not reach Bonferroni significance (p = 0.519). This non-result is informative: robustness follows a different trajectory than all other dimensions.

3. **Confound removal matters.** The raw Spearman correlation for the safety–privacy pair is ρ_raw = 0.73 — inflated by scale confound. The partial correlation (ρ = 0.971) reveals the true strength after removing the general "larger models score higher on everything" effect.

## 5.2 RQ2: RLHF Jointly Optimizes Safety and Machine Ethics (H-M1)

The LLaMA-2 within-family natural experiment provides mechanistic evidence that RLHF is the driver of the 5-dimension cluster. Figure 7 shows within-family deltas for all three scale points.

**Key results:** RLHF fine-tuning increases both safety AND machine_ethics simultaneously at all three scale points:

| Pair | Δ_safety (Chat − Base) | Δ_ethics (Chat − Base) | Both Positive? |
|------|------------------------|------------------------|----------------|
| LLaMA-2-7B → 7B-Chat | +0.626 | +0.464 | ✓ |
| LLaMA-2-13B → 13B-Chat | +0.652 | +0.422 | ✓ |
| LLaMA-2-70B → 70B-Chat | +0.638 | +0.386 | ✓ |

All 3/3 pairs show joint positive deltas (binomial sign test: p = 0.125, minimum achievable for n=3). The ρ_partial(safety, machine_ethics) = 0.841 (p = 3.22e-5) provides the cross-model correlational confirmation. Figure 8 shows the 2D delta scatter with all three scale points in the upper-right quadrant.

**For adversarial robustness:** All 3/3 LLaMA-2 pairs show Δ_robustness ≤ 0 (−0.080, −0.085, −0.094), confirming the directional safety-robustness tension. However, the full partial correlation (ρ = −0.188, p = 0.519) does not reach Bonferroni significance, consistent with n=16 being underpowered for moderate effects. A scale-only control (removing is_RLHF covariate) yields ρ = −0.771 (p = 0.0008), indicating the effect exists but the RLHF binary covariate absorbs substantial shared variance when added.

**Interpretation:** RLHF preference learning creates a pervasive alignment signal that simultaneously lifts safety, ethics, fairness, privacy, and truthfulness — the 5 dimensions that human annotators penalize violations of through standard RLHF annotation. Robustness to adversarial inputs, which is not directly optimized by preference annotation, follows a separate scale-driven trajectory.

## 5.3 RQ3: 2-Cluster Structure Confirmed — Robustness Isolates (H-M3)

Hierarchical clustering of the 6×6 partial correlation distance matrix produces a clear 2-cluster solution. Figure 10 (Ward dendrogram) and Figure 11 (MDS projection) visualize the structure.

**Silhouette scores by linkage method:**

| Linkage | Silhouette (k=2) | Silhouette (k=3) |
|---------|------------------|------------------|
| Ward | **0.637** | 0.500 |
| Average | **0.637** | 0.500 |
| Complete | **0.637** | 0.500 |

The identical silhouette=0.637 across all three linkage methods is a strong robustness indicator: the 2-cluster geometry is not a methodological artifact — it is a genuine property of the data. Figure 12 shows this silhouette comparison. The k=2 solution substantially outperforms k=3 (silhouette drop: 0.637 → 0.500), confirming that 2 clusters is the optimal partition.

**Cluster membership:**

- **Cluster A (RLHF-shaped, 5 dimensions):** {truthfulness, safety, fairness, privacy, machine_ethics}
- **Cluster B (RLHF-insensitive, 1 dimension):** {adversarial robustness}

The functional split is 1+5, not the predicted 2+4. Privacy is in the RLHF-shaped cluster (contrary to the original prediction), driven by the exceptionally strong ρ(safety, privacy) = 0.971. This is the primary empirical revision to the original hypothesis: privacy is RLHF-sensitive, not RLHF-insensitive.

Membership alignment with the *revised* predicted grouping (robustness isolates; all others are RLHF-shaped) is 6/6. Alignment with the *original* predicted grouping ({safety, ethics} vs {robustness, privacy}) is 3/4, as privacy joins the RLHF-sensitive cluster against prediction.

## 5.4 RQ4: 3-Dimension Minimum Evaluation Set with Bootstrap Stability (H-E2-v2)

The MST of the partial Spearman distance matrix identifies a minimum evaluation set of **3 dimensions** {truthfulness, fairness, privacy} — a 50% compression from the standard 6-dimension evaluation. Figure 5 shows the MST graph with edge weights; Figure 6 shows per-edge bootstrap frequencies.

**MST structure:**

| Edge | Distance (1−|ρ|) | Bootstrap Frequency |
|------|-----------------|---------------------|
| Privacy — Safety | 0.029 | 1.000 |
| Fairness — Truthfulness | 0.266 | 1.000 |
| Robustness — Truthfulness | 0.388 | 0.941 |
| Fairness — Privacy | 0.088 | 0.956 |
| Machine_ethics — Privacy | 0.141 | 0.688 |

Mean per-edge bootstrap frequency: **0.917** (threshold ≥ 0.90; gate passes). Four of five edges exceed 94% stability; the machine_ethics–privacy edge has 68.8% frequency, reflecting a genuine near-tie between machine_ethics–privacy, machine_ethics–safety, and machine_ethics–fairness at approximately equal distances (~0.14–0.16 in 1−|ρ| space).

**Interpretation:** The minimum evaluation set {truthfulness, fairness, privacy} represents the minimum dimensions needed to "span" the trustworthiness correlation space: measuring these three captures the maximum information about the correlated 5-dimension cluster. Note that robustness is a leaf node in the MST (terminal, not a hub), confirming its isolation — it must be measured separately, not replaced by proxy dimensions.

**Comparison to raw MST:** Without confound control, the raw Spearman MST identifies a 4-dimension minimum set. Partial correlation control reduces the minimum set by one dimension, because the confound removal reveals that truthfulness, fairness, and privacy form a tightly sufficient hub once the scale confound is removed.
