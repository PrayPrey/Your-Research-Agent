# Human Review Notes
**Paper:** Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding
**Purpose:** Minor issues collected during adversarial review for human review. NOT auto-fixed.
**Date:** 2026-08-27
**Rounds Completed:** 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 4 |
| Clarity | 4 |
| Formatting | 2 |
| **Total** | **10** |

---

## Round 1 Issues

### Style

1. **MINOR-001** — Abstract, sentence 2 is a run-on: "Two neural networks can compute the same function yet occupy nearly orthogonal positions in weight space — a geometric reality with concrete consequences for any method that learns from raw neural network weights." Consider splitting at the em-dash.

2. **MINOR-002** — Abstract: "approximately invariant to sign-flip orbits by construction — an emergent consequence of its row-level tokenization" — the em-dash interruption weakens the causal claim. Consider: "which is an emergent consequence of its row-level tokenization."

3. **MINOR-003** — Abstract final sentence: "these findings transform the argument for symmetry canonicalization from a theoretical expectation into a measurement-grounded framework" — mixed metaphor (an argument becomes a framework). Consider: "these findings ground the argument for symmetry canonicalization in measurement, specifying..."

4. **MINOR-004** — Introduction contributions section: "Together, these contributions transform..." — weak connector for a 4-claim summary. Consider restructuring as a numbered or bullet synthesis.

### Clarity

5. **MINOR-005** — Section 5.4 (Table 4): Explicitly verify and state that 72 + 428 = 500 in the table caption or immediately following text, for transparency. Ground truth confirms 72/500 and 428/500; this is a simple reproducibility annotation.

6. **MINOR-006** — Section 5.4: The connection between mean_tied_neurons=2.20 and the binomial prediction of 83% per-model probability is not explained inline. Add a brief bridge: "Under the binomial model, the expected number of tied neurons per model is 64 × 0.028 ≈ 1.8, consistent with the observed mean of 2.20 (slight upward deviation consistent with gradient-trained weight distributions being slightly more symmetric than Bernoulli(0.5))."

7. **MINOR-007** — Related Work: Contributions 2 (NFT invariance probe) and 3 (geometric concentration) are adjacent in both the contribution list and the results. Add a brief transition sentence distinguishing them: "While Contribution 2 measures how NFT responds to symmetric weight variation, Contribution 3 measures whether removing that variation via canonicalization concentrates geometry."

8. **MINOR-008** — Table 2 caption: Does not explicitly state that CIs are at 95% confidence. Add "95% bootstrap CIs" to caption.

### Formatting

9. **MINOR-009** — Kofinas et al. [2024] citation: Venue and publication year flagged as potentially unverified in the BibTeX (marked [UNVERIFIED]). Verify title, authors, venue via Semantic Scholar before submission. The arXiv ID 2403.12143 may correspond to a 2024 preprint; check for a conference proceedings version.

10. **MINOR-010** — Check "canonicalization" spelling consistency throughout. British ("canonicalisation") vs. American ("canonicalization") should be uniform. Current draft appears to use "canonicalization" consistently (American), but verify no instances of the British variant exist.

---

## Recommended Priority

1. **Fix First** (high-visibility): MINOR-001 (abstract run-on), MINOR-008 (Table 2 CI label)
2. **Fix Second** (readability): MINOR-006 (bridge sentence for tied_neurons/binomial), MINOR-007 (contribution 2 vs 3 transition)
3. **Consider** (subjective style): MINOR-002, MINOR-003, MINOR-004
4. **Verify before submission** (critical): MINOR-009 (Kofinas citation), MINOR-010 (spelling check)
5. **Optional** (minor annotation): MINOR-005

---

*Note: These issues do not block paper acceptance but improve overall quality. All FATAL and MAJOR issues have been addressed in R1 and R2 revisions. The final paper (06_paper_final.md) is ready for human polish and citation verification.*
