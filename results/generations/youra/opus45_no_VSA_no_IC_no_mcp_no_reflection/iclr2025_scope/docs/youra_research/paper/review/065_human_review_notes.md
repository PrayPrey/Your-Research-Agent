# Human Review Notes

**Paper:** Testing Mamba-2 Duality for Cross-Architecture Distillation
**Generated:** 2026-08-31
**Purpose:** Minor issues requiring human judgment (NOT auto-fixed)

---

## Summary

| Type | Count |
|------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 0 |
| Clarity | 0 |
| Formatting | 2 |
| **Total** | **2** |

---

## Issues

### MINOR-001: Reference Formatting

**Location:** References section (lines 212-235)
**Type:** formatting
**Description:** Mix of arXiv identifiers and incomplete venue information. Some references have only arXiv IDs, others have venues.

**Recommendation:** Standardize all references to include:
- Full author list
- Complete title
- Venue or arXiv ID + year
- DOI where available

**Priority:** LOW — will be resolved in LaTeX/BibTeX conversion

---

### MINOR-002: Figure References

**Location:** Throughout paper
**Type:** formatting
**Description:** Paper references figures (gate_metrics.png, bar_comparison.png, etc.) but markdown format doesn't embed them inline.

**Recommendation:** During LaTeX conversion:
- Embed figures at appropriate locations
- Add proper figure captions
- Reference with \ref{} labels

**Priority:** LOW — expected for Phase 6 draft; resolved in Phase 6.5.1

---

## Notes for Phase 6.5.1

When converting to Overleaf:
1. Use `06_references.bib` for bibliography
2. Embed figures from `h-e1/code/figures/` and `h-m1/code/figures/`
3. Format per ICML 2025 template
4. Add line numbers for review
