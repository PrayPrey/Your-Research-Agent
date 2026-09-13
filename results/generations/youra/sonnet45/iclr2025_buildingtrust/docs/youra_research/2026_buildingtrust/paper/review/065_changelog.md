# Adversarial Review Changelog
**Paper**: Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Argmax Instability After RLHF
**Generated**: 2026-03-17
**Revision Round**: R1
**Issues Addressed**: 6 of 6 MAJOR

---

## Round 1 Changes

### M-AC-1: Abstract AUROC range visibility

**Issue**: Abstract stated AUROC=0.91 as a single anchor without disclosing the cross-benchmark range, giving readers a misleadingly optimistic single-number impression.

**Fix**: Changed abstract sentence from "...with area under the receiver operating characteristic curve (AUROC) of 0.91, generalizing cross-benchmark..." to "...with area under the receiver operating characteristic curve (AUROC) of 0.91 (range 0.80–0.91 across benchmarks), generalizing cross-benchmark...". The parenthetical "(range 0.80–0.91 across benchmarks)" now makes the full performance range visible in the abstract.

---

### M-AC-3: RQ2 ratio-of-ratios language replaced with direct table values

**Issue**: The original RQ2 text stated "The observed non-isotropy (ratios 2.6× to 4.1× above the isotropic reference)" — a derived ratio-of-ratios (2.8996/1.13 and 4.5789/1.13) that does not appear in Table 2, creating a citation gap and an arithmetic that readers cannot verify directly from the table.

**Fix**: Replaced that sentence with: "The observed non-isotropy corresponds to dominant eigenvalues of 2.8996 (DPO) and 4.5789 (SFT) relative to the isotropic control baseline of 1.13 — all values shown in Table 2." This directly references the Table 2 values (2.8996 and 4.5789) rather than computed ratios of those values against the baseline.

---

### M-BR-1: Figure numbering conflict resolved

**Issue**: The Results section referenced two different figures both numbered "Figure 1": fig3_roc_curves.png (RQ1 ROC curves) and fig1_anisotropy_gate_metrics.png (RQ2 anisotropy gate). This created an irreconcilable numbering conflict.

**Fix**: Renumbered figures throughout the Results section to eliminate the conflict:
- Figure 1 (fig3_roc_curves.png) — RQ1 ROC curves — retains "Figure 1"
- fig2_quintile_flip_pair2.png → Figure 2 (no change, already correct)
- fig4_margin_dist_pair2.png → Figure 3 (no change, already correct)
- fig2_quintile_trend.png → Figure 4 (was previously unnumbered/conflicting)
- fig1_anisotropy_gate_metrics.png → Figure 5 (was previously also "Figure 4/Figure 1" — now Figure 5 to avoid all conflicts)
- fig2_eigenvalue_spectrum.png → Figure 6 (was previously "Figure 5")

All figure references in the RQ2 subsection now use Figure 5 and Figure 6, resolving the conflict.

---

### M-BR-2: Duplicate gap statement removed from Related Work subsections 1 and 2

**Issue**: The sentence "However, none of these works predict per-item vulnerability before alignment runs." appeared verbatim at the end of three consecutive Related Work subsections (LLM Calibration, Pre-Alignment Predictors, Geometric Analysis), creating a repetitive structure that weakens the rhetorical effect of the gap statement.

**Fix**: Removed the sentence from the end of subsection 1 ("LLM Calibration and Reliability Under Alignment") and subsection 2 ("Pre-Alignment Predictors of Post-Alignment Behavior"). The sentence is retained in the Gap Statement section (§2.4) as: "No existing work poses this prediction problem... No existing work predicts per-item vulnerability before alignment runs." The gap statement in §2.4 was also lightly edited to make the retained version read as a concluding statement rather than a mid-paragraph aside. The subsection on Geometric Analysis (subsection 3) also had its trailing instance removed, leaving the statement only in the Gap Statement section.

---

### M-SE-1: Limitation 2 expanded with bounding argument for model identity confound

**Issue**: Limitation 2 ("Primary evidence from one DPO pair") noted the model identity confound without providing any quantitative bounding argument, leaving readers unable to assess how seriously the confound threatens the DPO vs. SFT comparison.

**Fix**: Expanded Limitation 2 with 3 additional sentences: "The observed gap between DPO (gradient magnitude Q5/Q1 = 4.79×) and SFT (Q5/Q1 = 1.26×) corresponds to a 3.8-fold ratio difference. For model identity confounds alone to explain this gap, differences in scale or architecture between tulu-2-7b and pythia-6.9b would need to account for this 3.8-fold difference — which is implausible given that the two models have similar parameter counts (~7B and ~6.9B). While this bounding argument makes a model-identity explanation unlikely, the ideal test remains a same-base-model DPO vs. SFT comparison using identical pythia-6.9b-base models, which is the highest-priority next experiment." This provides a quantitative basis for readers to assess the confound without overclaiming.

---

### M-SE-2: Causal attribution for SFT weak result weakened

**Issue**: The original Results RQ1 section explained the weaker SFT result with a single causal claim: "SFT does not optimize a pairwise preference objective, reducing the extent to which the alignment procedure reshapes the confidence geometry near the decision boundary." This overclaimed causality given the model identity confound (different base models for DPO and SFT pairs).

**Fix**: Replaced the implicit single-cause framing with an explicit multi-explanation paragraph in the RQ1 section: "The weaker SFT result is consistent with multiple explanations: SFT does not optimize a pairwise preference objective (which may reduce the extent to which the alignment procedure reshapes confidence geometry near the decision boundary), but differences in model scale, architecture, or training data quality between the tulu-2-7b and pythia-6.9b base models could also contribute to the gap. Isolating the method effect from these confounds requires a same-base-model DPO vs. SFT comparison, which is identified as the highest-priority next experiment in the Conclusion." This preserves the objective observation while accurately representing the epistemic status of the causal attribution.

---

## Round 2 Changes

**Revision Round**: R2
**Issues Addressed**: 1 of 1 MAJOR

### M-SE-1 (R2): Full cross-benchmark AUROC range corrected throughout Introduction and Discussion

**Issue**: The abstract correctly disclosed the full cross-benchmark AUROC range as "0.80–0.91" (encompassing TruthfulQA at 0.803). However, four locations in the Introduction and Discussion used the narrower "0.867–0.909" or "0.87–0.91" range without qualification, which excluded TruthfulQA (0.803) and could mislead readers into believing the full cross-benchmark range was narrower than reported in the abstract.

**Affected locations and fixes**:

1. **Introduction §1 Contributions (First contribution)**: Changed "achieves AUROC 0.87–0.91 across three benchmarks" to "achieves AUROC 0.803–0.909 across three benchmarks (MMLU: 0.867, TruthfulQA: 0.803, ARC-Challenge: 0.909)".

2. **Introduction §2 Gap Statement (§2.4)**: Changed "achieves AUROC 0.87–0.91 across three benchmarks" to "achieves AUROC 0.803–0.909 across three benchmarks (MMLU: 0.867, TruthfulQA: 0.803, ARC-Challenge: 0.909)".

3. **Experimental Setup §4**: Changed "AUROC in the range 0.867–0.909 across benchmarks" to "AUROC in the full cross-benchmark range 0.803–0.909 (MMLU: 0.867, TruthfulQA: 0.803, ARC-Challenge: 0.909)".

4. **Discussion Finding 1**: Changed "AUROC = 0.867–0.909 for DPO-aligned models" to "AUROC = 0.803–0.909 across three benchmarks for DPO-aligned models (MMLU: 0.867, TruthfulQA: 0.803, ARC-Challenge: 0.909)".

5. **Conclusion**: Changed "AUROC values of 0.867–0.909 across MMLU, TruthfulQA, and ARC-Challenge" to "AUROC values of 0.803–0.909 across MMLU, TruthfulQA, and ARC-Challenge (MMLU: 0.867, TruthfulQA: 0.803, ARC-Challenge: 0.909)".

**Ground truth values used**: AUROC MMLU = 0.8668 → 0.867; AUROC TruthfulQA = 0.8034 → 0.803; AUROC ARC = 0.9086 → 0.909. Full cross-benchmark range = 0.803–0.909.

**Strategy applied**: Option (a) — changed to the full cross-benchmark range "0.803–0.909" with per-benchmark breakdown in parentheses, maintaining consistency with the abstract's "0.80–0.91" range.
