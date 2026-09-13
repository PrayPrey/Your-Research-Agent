# Phase 6.5 Human Review Notes

**Paper:** Memory Horizon Separation in SSM Adaptation
**Generated:** 2026-03-28T02:10:00Z
**Purpose:** Minor issues collected for human review (NOT auto-fixed per v2.0 protocol)

---

## About This File

Per Phase 6.5 v2.0 workflow, MINOR issues (typos, grammar, style, clarity, formatting) are **collected but not auto-fixed**. This preserves author voice and allows human judgment on stylistic choices.

These notes are suggestions, not requirements. Review at your discretion.

---

## Collected Notes

### MINOR-001: Clarity
**Location:** Section 2.3, paragraph on eigenvalue analysis
**Type:** clarity
**Note:** This paragraph is dense with control theory concepts. Consider adding a brief intuitive explanation before the technical details for readers less familiar with dynamical systems theory.

**Current text snippet:**
> "The connection between eigenvalue magnitude and memory capacity in recurrent systems is well-established in control theory and dynamical systems. For discrete-time linear systems $h_t = Ah_{t-1} + Bu_t$, eigenvalues $|\lambda| < 1$ ensure stability..."

**Suggestion:** Add 1-2 sentences of intuition before diving into formulas.

---

### MINOR-002: Formatting
**Location:** Section 4, Tables
**Type:** formatting
**Note:** Table formatting is inconsistent across the section. Some tables use markdown pipe syntax consistently, others have alignment issues.

**Suggestion:** Standardize table formatting for camera-ready version.

---

### MINOR-003: Style
**Location:** Section 5.4
**Type:** style
**Note:** "essentially *zero*" uses italics for emphasis, which reads as informal in academic writing.

**Current:** "The energy redistribution is essentially *zero*."

**Suggestion:** Consider "The energy redistribution is negligible" or "essentially zero" without italics.

---

### MINOR-004: Clarity
**Location:** Section 3.3, Energy Distribution Measurement
**Type:** clarity
**Note:** The KL divergence formulation is mentioned ("using KL divergence formulation") but the actual formula is not provided. This may confuse readers expecting to see the derivation.

**Suggestion:** Either add the KL formulation or remove the reference and just use "nats" as the unit.

---

### MINOR-005: Formatting
**Location:** Appendix A, Figure References
**Type:** formatting
**Note:** Figure references use inconsistent naming (fig_1, Figure 1, hspec_distribution.png). For camera-ready, standardize to "Figure N" format.

**Current:**
> "- **Figure 1:** H_spec distribution across 1000 input sequences (h-e1/figures/hspec_distribution.png)"

**Suggestion:** Use consistent "Figure N: Description" format without file paths in main text.

---

## Summary

| Type | Count |
|------|-------|
| typo | 0 |
| grammar | 0 |
| style | 1 |
| clarity | 2 |
| formatting | 2 |
| **Total** | **5** |

---

## Reviewer Notes

These issues are cosmetic and do not affect the scientific validity of the paper. All can be addressed during camera-ready preparation if the paper is accepted.

**Priority:** Low (address before final submission, not blocking for review)
