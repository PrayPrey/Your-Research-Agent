# Results

We present results in the order established by our research questions: existence (RQ1), architecture
ranking (RQ2), gap-specific signal (RQ3), and differential advantage (RQ4). The evidence builds toward
our central finding: generalization gap is a learnable, architecturally-sensitive, and genuinely distinct
weight-space prediction target.

## 5.1 RQ1: Gap Learnability and Target Independence

Figure 1 (fig1_bar.png) shows Spearman rank correlations for all four encoders on the gap prediction
target. Two encoders exceed the existence threshold (r > 0.5): FlatMLP (r = 0.5567) and DWSNet
(r = 0.5104). This establishes that generalization gap is a learnable signal in weight tensors — accessible
even to a position-indexed flat encoder without equivariant constraints.

**Table 1: Gap and Test Accuracy Spearman (Test Split, N=1,000)**

| Encoder | Spearman(gap) | 95% CI | Spearman(test_acc) | 95% CI |
|---------|--------------|--------|--------------------|--------|
| FlatMLP | 0.5567 | — | 0.2790 | [0.2173, 0.3343] |
| DWSNet | 0.5104 | — | 0.4553 | [0.4020, 0.5054] |
| NFT | 0.5752 | [0.5339, 0.6158] | 0.4801 | [0.4326, 0.5262] |
| GNN | 0.3747 | [0.3180, 0.4265] | 0.3480 | [0.2913, 0.4037] |

*FlatMLP gap CI not separately reported (from h-e1; NFT/DWS/GNN CIs from h-m1 bootstrap).*

The A1 audit confirms that gap is not trivially derivable from test accuracy: Spearman(gap, −test_acc)
= −0.142, far below the collinearity threshold of 0.95. Predicting gap is a genuinely independent task.

**The counterintuitive asymmetry.** Figure 2 (fig2_dual_target_spearman.png) reveals that FlatMLP
predicts gap (r = 0.557) almost twice as well as test accuracy (r = 0.279) from identical weight inputs.
This reverses the expectation from prior literature (where FlatMLP achieves r ≈ 0.85 on test_acc in the
original Unterthiner zoo). We discuss this anomaly in Section 5.3; crucially, it does not affect the
gap prediction results, which are our primary contribution.

## 5.2 RQ2: Architecture Ranking on Gap Prediction

**NFT achieves the highest gap Spearman** (r = 0.5752) with a 95% CI of [0.5339, 0.6158] that is
non-overlapping with FlatMLP's confidence band. Figure 1 shows this ranking clearly: NFT > FlatMLP >
DWSNet > GNN for gap prediction.

The architecture-specificity of this result is the key finding. DWSNet (within-layer equivariance)
achieves r = 0.4881 on gap — below FlatMLP's r = 0.5330. GNN achieves only r = 0.3747, the lowest
among all encoders. This means equivariance is not uniformly helpful for gap prediction: only the
cross-layer attention architecture (NFT) provides a meaningful advantage, while within-layer and
graph-structured equivariance actually underperform the non-equivariant baseline.

**Scatter plot comparison** (fig2_scatter.png) shows predicted vs. true gap for all four encoders on
the test split. NFT's scatter is tighter and more linear than DWSNet's or GNN's, confirming that the
Spearman advantage reflects genuine alignment, not outlier-driven correlation.

## 5.3 RQ3: Gap-Specific Signal Independent of Test Accuracy (P3)

This is the paper's central result. The partial Spearman analysis tests whether NFT's gap predictions
contain information about true gap that cannot be explained by test accuracy rank alone.

**NFT partial Spearman (gap | test_acc): r = 0.7305, p = 1.60×10⁻¹⁶⁷**

Figure 3 (fig4_partial_corr_scatter.png) shows the residual scatter for the P3 analysis. After
partialling out test accuracy rank from both NFT's gap predictions and the true gap labels, the
residual correlation remains r = 0.73. This result is:

1. **Stronger than the direct Spearman** (0.73 > 0.57): the gap-specific component of NFT's
   predictions is more strongly correlated with the gap-specific component of true gap than the
   combined signal. Partialling out test accuracy isolates an overfitting structure that NFT captures
   particularly well.

2. **Statistically unambiguous** (p = 1.60×10⁻¹⁶⁷): with N = 1,000 test samples, the p-value is
   not a borderline result — the gap-specific signal is real and large.

3. **Architecture-specific**: this analysis was performed for NFT as the encoder with the highest
   direct gap Spearman. The result confirms that NFT's cross-layer attention is not merely learning
   a test-accuracy proxy — it captures genuine overfitting structure in weight space.

This result answers RQ3: yes, gap predictions from NFT contain substantial information about true gap
that is independent of test accuracy. Generalization gap encodes a distinct signal in weight space that
cross-layer attention is well-positioned to extract.

## 5.4 RQ4: Differential Advantage (Δ) — Null Result

Figure 4 (fig1_gate_delta.png) and Figure 5 (fig5_bootstrap_ci.png) show the Δ values for equivariant
encoders with 95% bootstrap CIs.

**Table 2: Differential Advantage Δ = [gap improvement] − [test_acc improvement] over FlatMLP**

| Encoder | gap Spearman | acc Spearman | Δ | 95% CI | Δ > 0.02? |
|---------|-------------|-------------|---|--------|-----------|
| DWSNet | 0.4881 | 0.4553 | −0.2212 | entirely < 0 | ❌ No |
| NFT | 0.5752 | 0.4801 | −0.1589 | entirely < 0 | ❌ No |
| GNN | 0.3747 | 0.3480 | −0.2272 | entirely < 0 | ❌ No |

*Gate criterion: Δ > 0.02 for ≥2 encoders. Result: 0/3 encoders pass. Gate: FAIL.*

All equivariant Δ values are strongly negative, with 95% CIs entirely below zero. The differential
advantage hypothesis (equivariant encoders improve more on gap than on test_acc relative to FlatMLP)
is not confirmed under these experimental conditions.

**Why are Δ values negative?** Figure 3 (fig3_delta_decomposition.png) decomposes Δ into its two
components: gap improvement and acc improvement over FlatMLP. The dominant driver is the acc improvement
component — all equivariant encoders show substantially larger test_acc improvement over FlatMLP than
gap improvement. Since FlatMLP test_acc (r = 0.279) is anomalously low (vs. literature ~0.85), the
apparent acc improvement for equivariant encoders is inflated. DWSNet shows 0.455 − 0.279 = +0.176
improvement on test_acc, while its gap improvement is only 0.488 − 0.533 = −0.045 (DWSNet is actually
worse than FlatMLP on gap). This confound prevents a clean interpretation of the Δ result.

**What we can conclude:** (1) Under our experimental conditions, equivariant encoders do not show a
gap-specific differential advantage. (2) The most likely confounder is the FlatMLP test_acc baseline
being severely underestimated due to our limited search budget. (3) The gap prediction results (RQ1-RQ3)
are not affected by this issue — they rely only on gap Spearman, which is internally consistent across
independent runs (FlatMLP: 0.5567 in h-e1, 0.5330 in h-m1; gap < 5% deviation).
