# Human Review Notes — Phase 6.5 Adversarial Review

> MINOR issues collected from adversarial review rounds. Per protocol these are
> NOT fixed by the Revision Agent; they are for human review during final polish.

**Date**: 2026-08-05T12:25:00+00:00
**Rounds Completed**: 2 (R1, R2)

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 |
| Clarity | 3 |
| Formatting | 6 |
| **Total** | **12** (2 R2 items carried from R1; ~10 unique) |

## Recommended Priority

1. **Fix First**: `Chi2025Know` bib venue/year + author ordering (camera-ready blocker for citation correctness).
2. **Fix Second**: §5.4 "all five clauses" → "all five gate criteria" (small but reader-visible precision issue).
3. **Consider**: "to our knowledge" hedge propagation to Abstract/Conclusion priority claims.
4. **Optional**: word-count convention, thinnest-margin signal in Abstract, Figure-order consideration.

---

## Round 1 Issues

(from 065_review_r1.md Part 4, review of 06_paper.md; status notes reflect side effects of the R1 revision where applicable)

### Formatting

- **References / 06_references.bib (`Chi2025Know`)**: Cited as arXiv 2025 but DOI `10.18653/v1/2026.findings-acl.34` indicates Findings of ACL 2026; bib comment flags it PARTIAL. Resolve venue/year at camera-ready.
- **References (`Chi, C. S.`)**: Author "Cheang Seng Chi" — verify surname ordering/abbreviation ("Chi, C. S." vs "Cheang, S. C.") against the published record.
- **Front matter**: `word_count: 6528` vs assembled sections 6533 — trivial metadata drift. *(R1 note: frontmatter was updated to 6822 to reflect revision deltas; the underlying counting-convention drift of ~5 words is still unresolved and can be settled at camera-ready.)*
- **Sections vs assembled paper**: Only difference is figure path prefix (`../figures/` in sections vs `figures/` in 06_paper.md) — correct for each file's location; no action needed, noted for the record.

### Style

- **Abstract**: "adjacent-layer KL emerges as a first-time detection signal" — add the "to our knowledge" hedge used in §5.3, for consistency of the priority claim.
- **Figures / blueprint**: Blueprint coherence check certified the "Figure 1 test" against `gate_metrics_bar.png` (Figure 4 in the paper); consider whether the headline 6/6 grid should appear earlier, though the current Figure 1 (entropy heatmap) works as intuition.

### Clarity

- **Discussion, limitation 1 vs 3**: "the original rescue claim" was used (limitation 1) before the rescue framing is explained (limitation 3). *(R1 note: likely resolved — MAJOR-ENG-001's fix removed the term from limitation 1 and the Conclusion; it now appears only in limitation 3, self-defined. Verify on read-through.)*

### Typo / Grammar

- (none reported in Round 1)

## Round 2 Issues

(from 065_review_r2.md Part 4, review of 06_paper_r1.md; per protocol NOT fixed by the Revision Agent)

### Style

- **Abstract / Conclusion**: "adjacent-layer KL emerges as a first-time detection signal" (Abstract) and "the first detection-time use" (Conclusion §7) remain unhedged while §5.3 says "to our knowledge" — propagate the hedge for consistency of the priority claim. *(Carried from Round 1.)*

### Clarity

- **Abstract**: "beats the final layer's own entropy readout in every cell" — accurate as point estimates, but consider signaling the thinnest margin (+0.0035) the way §5.2 does; optional.
- **§5.4**: "passed all five clauses" — §3.5 defines three lettered clauses (a)–(c); the "five" are the five gate criteria (existence, a, b, screen health, c). Say "all five gate criteria" or "all three clauses plus both health checks".

### Formatting

- **Front matter**: `word_count` metadata (6822 in R1; updated to 6871 in R2 by the same convention) vs ~7,300–7,500 by whitespace count over the body incl. references/captions — counting-convention drift, method-dependent; settle the convention at camera-ready.
- **References (`Chi2025Know`)**: Venue/year ambiguity (arXiv 2025 vs Findings ACL 2026 DOI) and author-name ordering — carried from Round 1, unchanged; resolve at camera-ready.
