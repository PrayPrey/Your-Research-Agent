# Human Review Notes - Phase 6.5 Adversarial Review

> **Purpose:** Minor issues collected during adversarial review for human review.
> These issues do NOT block acceptance. Fix during final manuscript polish.

**Date**: 2026-08-04T20:05:00Z
**Rounds Completed**: 1 (R1)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Unsupported value | 1 |
| Overclaim (small n) | 1 |
| Citation | 2 |
| Minor clarity | 1 |
| Word choice | 1 |
| Epistemic precision | 1 |
| **Total** | **7** |

---

## Round 1 Issues

### MN-1 — Unsupported ~95% import error figure
- **Location**: Section 5.1, Phase C Failure Analysis table
- **Issue**: `import_error | Dominant (~95%)` — the ~95% figure appears nowhere in `ground_truth.yaml` or `04_validation.md` with a specific percentage. It is an undocumented approximation.
- **Fix**: Either compute the exact fraction from the error type distribution in validation outputs and cite it (e.g., "92% of Phase B positives that failed Phase C produced ImportError"), or soften to "large majority."

### MN-2 — "Ruling out file size as a confound" is too strong for n=10
- **Location**: Section 5.3, last sentence
- **Issue**: "ruling out file size as a confound" is a strong inference from a distribution plot with only n=10 executable files. Insufficient statistical power for this claim.
- **Fix**: Soften to "consistent with file size not being a primary confound" or "no obvious size difference is visible, though n=10 precludes statistical inference."

### MN-3 — Citation unverified: Kocetkov et al. 2022
- **Location**: References; also cited in Sections 1.2, 3.2, 2.2
- **Issue**: [Kocetkov et al., 2022] listed as UNVERIFIED in adversarial review citation audit.
- **Fix**: Verify arXiv:2211.15533 metadata (authors, title, year) via Semantic Scholar before submission.

### MN-4 — Citation unverified: Hui et al. 2024
- **Location**: References; also cited in Section 3.5
- **Issue**: [Hui et al., 2024] listed as UNVERIFIED in adversarial review citation audit.
- **Fix**: Verify arXiv:2409.12186 metadata via Semantic Scholar before submission.

### MN-5 — Phase B code snippet missing function context
- **Location**: Section 3.3, Phase B: AST Extraction code block
- **Issue**: `return True  # Phase B positive` ends the snippet but the enclosing function signature is not shown, which may confuse readers unfamiliar with the codebase structure.
- **Fix**: Add a one-line comment above the snippet noting the context (e.g., `# Inside check_phase_b(source_code: str) -> bool`), or show the function signature line.

### MN-6 — "Theoretical precedent" should be "empirical precedent"
- **Location**: Section 6.2, Limitation L2
- **Issue**: "The compile-only SFT benefit claim is supported by theoretical precedent (phi-1, EffiCoder)" — phi-1 and EffiCoder are empirical results, not theoretical ones.
- **Fix**: Change "theoretical precedent" to "empirical precedent."

### MN-7 — "Confirming" implies independent verification in Figure 4 description
- **Location**: Section 5.1, Phase C Failure Analysis paragraph; also Figure 4 caption
- **Issue**: "Import errors dominate, confirming third-party dependency isolation as the primary failure mode" — "confirming" implies the hypothesis was independently verified. Import isolation was the predicted cause; the data is consistent with it, not an independent confirmation.
- **Fix**: Change "confirming" to "consistent with" in the body text and Figure 4 caption.

---

## Round 2 Issues

**Date**: 2026-08-04T21:00:00Z

### MN-8 — ~95% import error figure not sourced
- **Location**: Section 5.1, Phase C Failure Analysis
- **Issue**: The "~95%" import error figure is not sourced in any verified output file (ground_truth.yaml, 04_validation.md, or error_type_distribution.png figure data). It is an undocumented approximation.
- **Fix**: Compute the exact fraction from error_type_distribution.png figure data and cite it explicitly, or soften to "large majority."

### MN-9 — "Ruling out file size as a confound" overstates inference from n=10
- **Location**: Section 5.3, last sentence
- **Issue**: "ruling out file size as a confound" is a strong causal inference from a distribution plot with only n=10 executable files. Insufficient statistical power for this claim.
- **Fix**: Soften to "suggesting file size is not a primary driver" or add explicit note: "though n=10 executable files precludes formal statistical inference."
