# 5. Results

## RQ1: Pre-Alignment Margin Predicts Post-Alignment Argmax Flip

**Main result.** Table 1 presents the mixed-effects logistic regression results and AUROC values for both evaluated model pairs across all three benchmarks. For pair 2 (tulu-2-7b → tulu-2-dpo-7b), the margin coefficient is β₁ = −4.33 with p ≈ 10⁻²²⁷ — a result so statistically overwhelming that it survives any reasonable multiple-comparisons correction. The negative sign confirms the theoretically predicted direction: items with higher pre-alignment confidence margin are less likely to experience an argmax flip after DPO alignment. The partial eta-squared η² = 0.289 indicates that margin alone accounts for approximately 29% of the variance in flip outcomes within pair 2, which substantially exceeds the gate threshold of η² ≥ 0.06.

**Table 1: Existence test results (H-E1).**

| Pair | Method | β₁ | p-value | AUROC (MMLU) | AUROC (TruthfulQA) | AUROC (ARC) | η² | Flip rate |
|------|--------|-----|---------|--------------|---------------------|-------------|-----|-----------|
| pair2 | DPO | −4.33 | ~10⁻²²⁷ | 0.8668 | 0.8034 | 0.9086 | 0.289 | 12.5% |
| pair4 | SFT | −0.062 | 0.00195 | 0.609 | — | — | — | — |

AUROC values for pair 2 span 0.8034–0.9086 across the three benchmarks, with MMLU at 0.8668, TruthfulQA at 0.8034, and ARC-Challenge at 0.9086 (Figure 3, fig3_roc_curves.png). These values exceed the 0.75 threshold across all three benchmarks, providing cross-benchmark generalization evidence that the margin-flip relationship is not an artifact of a single domain. The ARC-Challenge result (0.9086) is notably strong, suggesting that for items requiring multi-step reasoning — where confident wrong answers are more consequential — the geometric proximity to the alignment boundary is especially predictive. The gate summary visualization (Figure 1, fig1_gate_metrics.png) shows all three criteria (β₁, AUROC, η²) clearing their respective thresholds for pair 2.

For pair 4 (pythia-6.9b → oasst-pythia-6.9b SFT), the margin coefficient β₁ = −0.062 is significantly negative (p = 0.00195 < 0.005) but the AUROC of 0.609 falls below the 0.75 threshold. This means the direction of the effect replicates in SFT, but the effect size is substantially weaker. We interpret this as a scale and method interaction: the pythia pair is smaller (6.9B vs 7B with substantially fewer alignment-specific parameters updated under SFT), and SFT does not optimize a pairwise preference objective, reducing the extent to which the alignment procedure reshapes the confidence geometry near the decision boundary. The gate for pair 4 does not pass the AUROC criterion, but the directional replication is noted as supporting evidence.

**Quintile flip rate curve.** Figure 2 (fig2_quintile_flip_pair2.png) plots the empirical flip rate for pair 2 as a function of margin quintile across MMLU. The monotone decreasing pattern is striking: items in Q1 (lowest margin, closest to the alignment decision boundary) flip at a rate of approximately 25%, while items in Q5 (highest margin, farthest from the boundary) flip at approximately 1.5%. The intermediate quintiles follow the expected geometric gradient — Q2 at ~18%, Q3 at ~12%, Q4 at ~6% — tracing a near-exponential decay. This quintile curve translates the regression result into an operationally meaningful quantity: a practitioner can identify the ~20% of items in the lowest confidence quintile as a high-risk set with flip rates more than 16× higher than the top quintile. Figure 4 (fig4_margin_dist_pair2.png) further visualizes the separation of the margin distributions conditioned on flip outcome, confirming that flipped items have systematically lower base model margin.

**Gate: PASS** for pair 2 across all four criteria (β₁ < 0, p < 0.005, AUROC ≥ 0.75 cross-benchmark, η² ≥ 0.06). This constitutes an affirmative answer to RQ1: pre-alignment confidence margin is a reliable predictor of post-alignment argmax instability for DPO-aligned models.

---

## RQ2: Alignment-Induced Logit Perturbations Are Non-Isotropic

**Main result.** Table 2 presents the eigenvalue anisotropy ratios for both evaluated pairs alongside the isotropic Gaussian control. For pair 2 (DPO), the anisotropy ratio is 2.8996 (p = 0.0028, one-tailed). For pair 4 (SFT), the ratio is 4.5789 (p = 0.0047). Both values are substantially above the isotropic control of approximately 1.13, and both pass the one-tailed significance threshold (α = 0.05).

**Table 2: Non-isotropy test results (H-M1).**

| Pair | Method | Anisotropy ratio (λ₁/mean(λ₂,λ₃,λ₄)) | p-value (one-tailed) |
|------|--------|-----------------------------------------|----------------------|
| pair2 | DPO | 2.8996 | 0.0028 |
| pair4 | SFT | 4.5789 | 0.0047 |
| Isotropic control | — | ~1.13 | — |

The anisotropy ratio gate metric visualization (Figure 1, fig1_anisotropy_gate_metrics.png) shows both empirical ratios well above the isotropic control baseline. Figure 2 (fig2_eigenvalue_spectrum.png) displays the full eigenvalue spectrum λ₁ through λ₄ for both pairs. The dominant eigenvalue λ₁ is substantially larger than the remaining three in both cases, indicating that the alignment-induced logit perturbations are concentrated along a single principal direction in the 4-dimensional answer-token probability simplex.

The interpretation of this result is mechanistically important for the paper's central argument. If alignment perturbations were isotropic — that is, random noise distributed equally across all vocabulary dimensions — then there would be no privileged direction in logit space along which items near the boundary would be disproportionately pushed. The observed non-isotropy (ratios 2.6× to 4.1× above the isotropic reference) means that alignment systematically shifts logits along a structured axis. This structured shift is precisely what gives the pre-alignment margin its predictive power: items whose pre-alignment argmax falls close to the decision boundary are those for which a structured shift along the dominant perturbation axis is most likely to cross the boundary and induce a flip.

Notably, the SFT pair exhibits a higher anisotropy ratio (4.5789) than the DPO pair (2.8996), despite producing weaker margin-flip correlations. This apparent paradox is resolved in the RQ3 discussion: SFT perturbations are non-isotropic but applied relatively uniformly across confidence levels, while DPO perturbations are non-isotropic and concentration-weighted toward high-confidence items.

**Gate: PASS** for both evaluated pairs. Alignment-induced logit perturbations are geometrically structured in both DPO and SFT settings, which provides the mechanistic substrate for the margin-based predictability demonstrated in RQ1.

---

## RQ3: DPO and SFT Produce Distinguishably Different Quintile Variance Profiles

**Main result.** Contrary to our initial prediction that DPO would concentrate perturbations in low-confidence regions (i.e., that Q1 would show the highest logit delta variance), we observe the opposite pattern: DPO amplifies perturbation variance monotonically with pre-alignment confidence, reaching its maximum in the highest-confidence quintile. Table 3 presents per-quintile logit delta variances for both model pairs on MMLU.

**Table 3: Quintile logit delta variance (H-M2), MMLU.**

| Quintile | DPO variance (pair2) | SFT variance (pair4) |
|----------|----------------------|----------------------|
| Q1 (lowest margin) | 0.707 | 0.223 |
| Q2 | 0.996 | 0.225 |
| Q3 | 1.194 | 0.254 |
| Q4 | 2.611 | 0.294 |
| Q5 (highest margin) | 3.384 | 0.281 |
| Q5/Q1 ratio | 4.79× | 1.26× |

Figure 2 (fig2_quintile_trend.png) plots these quintile variance profiles side by side. The contrast is visually dramatic: the DPO profile rises steeply from Q1 to Q5 (Q5/Q1 ratio = 3.384/0.707 = 4.79×), while the SFT profile is nearly flat (Q5/Q1 ratio ≈ 1.26×). The original hypothesis for H-M2 predicted that DPO would concentrate perturbation energy in low-confidence regions (Q1 > SFT Q1). The one-tailed Welch's t-test for this specific directional hypothesis yields p = 1.000, Cohen's d = −0.490 on MMLU; p = 1.000, Cohen's d = −1.536 on TruthfulQA; and p = 0.992, Cohen's d = −0.225 on ARC-Challenge — the direction is reversed across all three benchmarks.

We present this null result not as a failure but as a novel empirical finding about DPO's behavioral signature. The correct characterization of the observed pattern is: **DPO exhibits confidence-dependent amplification**, wherein items that the base model answered confidently receive larger logit perturbations after alignment than items the base model answered hesitantly. SFT, by contrast, distributes perturbation variance uniformly across the confidence spectrum.

One interpretation of this asymmetry is that DPO's pairwise preference objective reinforces the base model's confident decisions — when the base model is already confident that answer A is correct, the DPO update may push logits further in that direction (since confident items are more likely to have been correctly labeled in the preference data), producing larger magnitude perturbations at high confidence. SFT, which optimizes a direct cross-entropy target, has no analogous amplification mechanism and produces roughly uniform perturbation magnitudes regardless of base confidence.

This finding reframes the mechanism behind RQ1: the margin-flip predictability is not because DPO preferentially perturbs low-confidence items in absolute terms. Rather, low-confidence items flip more often because they are geometrically near the decision boundary — a small perturbation of any magnitude is sufficient to cross it. High-confidence items receive larger perturbations (in DPO) but those perturbations must overcome a larger geometric gap before causing a flip. The margin captures this gap.

**Gate: NULL_RESULT (LIMITATION_RECORDED).** The directional hypothesis was falsified. The novel finding — DPO high-confidence amplification — is reported as an unexpected discovery and discussed further in Section 6.
