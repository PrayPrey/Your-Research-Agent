# Human Review Notes (MINOR Issues — NOT Auto-Fixed)
**Generated**: 2026-03-17
**Rounds Completed**: R1
**Paper**: Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Argmax Instability After RLHF

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 4 |
| Formatting | 4 |

---

## Round 1 Issues

### Style

1. **Minor-BR-1**: Introduction sentence "that it generalizes across benchmarks without retraining is more surprising still." — the phrase "more surprising still" is rhetorical rather than factual. Consider replacing with a comparative factual statement (e.g., "more consequential still" or "more practically significant") to reduce subjectivity and improve tone for a technical paper.

2. **Minor-BR-3**: Broader Impact section closes with "All code, data, and model checkpoints are released publicly." This claim may conflict with double-blind submission requirements for ICML 2025. Verify that this claim is consistent with the conference's anonymization policy before submission; if submitting under double-blind review, consider replacing with a statement like "Code and data will be released upon acceptance."

---

### Clarity

1. **Minor-AC-2**: Introduction Paper Organization paragraph references "Section 4 reports results" and "Section 5 discusses implications." However, the actual section numbers in the paper are §4 = Experimental Setup, §5 = Results, §6 = Discussion. The navigation paragraph should read "Section 5 reports results" and "Section 6 discusses implications" to match the actual section numbering.

2. **Minor-SE-1**: Abstract phrase "dominant eigenvalue 2.9–4.6 times larger than remaining axes" — "remaining axes" is imprecise. The anisotropy ratio is λ₁ divided by the *mean* of λ₂, λ₃, λ₄, not larger than all remaining axes individually. Consider: "dominant eigenvalue 2.9–4.6 times larger than the mean of the remaining axes."

3. **Minor-SE-4**: Methodology section states the margin is "z-scored within each benchmark split" in the Implementation Details, but the Problem Formulation states σ is "the standard deviation of all raw margins within the model pair (i.e., z-scoring over the full evaluation set)." These descriptions may or may not be equivalent depending on whether the full evaluation set equals the union of benchmark splits. Clarify whether z-scoring is performed per-benchmark or globally across all benchmarks, and ensure the Methodology and Implementation Details are consistent.

4. **Minor-AC-4**: Conclusion states "Q1=0.71 to Q5=3.38 — a 4.79× gradient." The ratio 3.38/0.71 = 4.76×, not 4.79×. Table 3 reports Q1=0.707 and Q5=3.384; 3.384/0.707 = 4.787... ≈ 4.79×. The discrepancy arises from using rounded table display values (0.71, 3.38) vs. full-precision values. Add a note that ratios are computed from full-precision values rather than the rounded values shown in Table 3, or adjust the displayed table values to reduce the apparent inconsistency.

---

### Formatting

1. **Minor-AC-1**: Conclusion uses "2.90–4.58×" (two decimal places) while Abstract uses "2.9–4.6×" (one decimal place) for the same anisotropy range. Standardize to one rounding convention throughout (recommend two decimal places for precision, matching the Table 2 values).

2. **Minor-AC-3**: Table 1 column header "AUROC (ARC)" should read "AUROC (ARC-Challenge)" to match the full benchmark name used throughout the paper and avoid potential confusion with other ARC variants.

3. **Minor-SE-2**: Table 3 reports per-quintile logit delta variances as point estimates without confidence intervals or standard errors. Readers cannot assess the precision of the quintile variance estimates or determine whether adjacent quintiles differ significantly. Consider adding a standard error column or footnote with bootstrap confidence intervals for the Q5/Q1 ratio.

4. **Minor-SE-3**: The RQ2 non-isotropy analysis (H-M1) reports two one-tailed permutation test p-values (p=0.0028 for DPO, p=0.0047 for SFT). Since two tests are conducted on the same hypothesis (H-M1), a note on multiple comparisons correction is warranted — even if both p-values remain significant after Bonferroni correction (threshold would be α=0.025 for two tests), the paper should explicitly note that no correction was applied or confirm that results survive correction.

---

## Round 2 Issues

**Round**: R2
**Total minor issues**: 4

### Style

1. **Minor-R2-1 (RQ2 anisotropy framing)**: The RQ2 sentence in the Results section describing the anisotropy ratio still has slightly ambiguous framing in some places. The anisotropy ratio is defined as λ₁/mean(λ₂,λ₃,λ₄), but the Discussion (Finding 2) describes it as "a dominant eigenvalue 2.9× (DPO) and 4.6× (SFT) relative to the isotropic control of 1.13." This compares the raw anisotropy ratio against the control value, rather than expressing a ratio-of-ratios, which is the clearer reading. However, some readers may still read "2.9× relative to the isotropic control" as meaning 2.9 × 1.13 = 3.28. Consider rewording to: "anisotropy ratios of 2.90 (DPO) and 4.58 (SFT), compared to the isotropic control of 1.13" to eliminate the ambiguity.

2. **Minor-R2-3 (Introduction/Conclusion "fundamental difference" language)**: The Conclusion describes the DPO confidence-dependent amplification finding as revealing "a fundamental difference in how preference-optimization and supervised fine-tuning restructure the logit space." The ground truth verification for H-M2 is classified as a MEDIUM confidence result (null result on the original directional hypothesis, with the amplification pattern an unexpected finding). The phrase "fundamental difference" may overstate the confidence level. Consider toning down to "a notable behavioral asymmetry" or "a potentially fundamental difference" to better reflect the result's medium confidence classification.

### Clarity

3. **Minor-R2-2 (Abstract AUROC endpoint precision)**: The abstract states AUROC "range 0.80–0.91 across benchmarks." The lower endpoint "0.80" rounds from TruthfulQA AUROC = 0.8034. The R2 fix in the body of the paper now uses the more precise "0.803" consistently throughout Introduction and Discussion. For consistency, the abstract endpoint could be updated from "0.80" to "0.803" to match the precision used in the body. This is a minor precision issue; the current "0.80" is not incorrect but is less precise than the body text.

### Formatting

4. **Minor-R2-4 (Figure filename/number consistency)**: The R1 M-BR-1 fix renumbered figures in the Results section (e.g., fig1_anisotropy_gate_metrics.png became Figure 5, fig2_eigenvalue_spectrum.png became Figure 6). However, the actual figure filenames (e.g., "fig3_roc_curves.png" referenced as Figure 1, "fig2_quintile_trend.png" referenced as Figure 4) do not match the figure numbers now assigned in the text. This creates a persistent mismatch between filename conventions and paper figure numbers. When creating the final LaTeX/formatted version, ensure figure captions and cross-references use the paper figure numbers (1–9) rather than the original filename indices.
