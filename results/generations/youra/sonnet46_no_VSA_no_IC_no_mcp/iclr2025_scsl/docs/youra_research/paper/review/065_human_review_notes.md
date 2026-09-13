# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> These were NOT auto-fixed. Review before submission.

**Date**: 2026-08-26  
**Rounds Completed**: 2 (R1 + R2)  

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 3 |
| Citation (unverified) | 3 |
| Formatting | 1 |
| Units inconsistency | 1 |
| **Total** | **8** |

---

## Round 1 Issues

### Clarity

1. **MINOR-ENG-001**: Abstract, sentence about DINO — "despite using no explicit labels" now fixed to "explicit class labels" (auto-fixed in R1). No further action needed.

2. **MINOR-ENG-002**: Figure 7 caption describes "MoCo-v3 vs ERM ratio on Waterbirds and CelebA (±1 SD)" — this describes the cross-dataset comparison data, which appears identical to what Figure 3 shows. Verify that Figure 7 (`gate_metrics.png`) actually contains distinct content from Figure 3 (`cross_dataset_bar.png`). If Figure 7 is the mechanism gate verification (pixel_diff plot), the caption should be updated accordingly.

3. **MINOR-SKE-004**: In Related Work, "Izmailov et al. [2022] provide a broader study of feature learning under spurious correlations, including comparisons with DINO on Waterbirds. Their analysis is closest to ours in scope, but does not use a controlled spurious/task ratio metric and does not perform a 4-paradigm comparison with Bonferroni-corrected pairwise tests." — This description of Izmailov et al. should be verified against the actual paper before submission. If the paper is "On Feature Learning in the Presence of Spurious Correlations" (NeurIPS 2022), confirm it indeed includes DINO on Waterbirds but not the spurious/task ratio metric.

### Citations (Unverified — must verify before submission)

4. **MINOR-SKE-001**: Robinson et al. [2021] — cited as "Contrastive Learning Avoids Shortcuts Only If Objective is Invariant to Shortcut Features" marked [UNVERIFIED] in paper. Verify title, venue, and that claim "SSL is not spurious-feature-free" is supported by this paper.

5. **MINOR-SKE-002**: Wen et al. [2021] — cited as "Toward Understanding the Feature Learning Process of Self-Supervised Contrastive Learning" marked [UNVERIFIED title/venue] in paper. Verify before submission.

6. **MINOR-SKE-003** (partially addressed in R1): Izmailov et al. [2022] title corrected to "On Feature Learning in the Presence of Spurious Correlations" in R1, but still marked [citation unverified]. Verify against actual paper before submission.

### Units Inconsistency

7. **MINOR-ACC-004**: Results 5.2 reports CelebA MoCo-v3 vs DINO diff as "3.59%" while all Waterbirds diffs are reported as proportions (0.025, 0.022, etc.). Consider standardizing — either all percentages or all proportions. Ground truth value is 0.0359 (proportion).

### Formatting

8. **MINOR-FMT-001**: Figure Captions section appears at end of paper as a separate named section rather than inline with the figures. ICML format typically expects captions embedded with figures. Confirm this is intentional for the draft format or adjust for submission.

---

## Recommended Priority

1. **Verify before submission**: Citations 4, 5, 6 (unverified references)
2. **Clarify**: Figure 7 caption content (issue 2)
3. **Verify**: Izmailov et al. description in Related Work (issue 3)
4. **Standardize**: Units for diff values (issue 7)
5. **Optional**: Formatting of figure captions (issue 8)

---

*Note: These issues do not block paper acceptance but should be resolved before final submission.*
