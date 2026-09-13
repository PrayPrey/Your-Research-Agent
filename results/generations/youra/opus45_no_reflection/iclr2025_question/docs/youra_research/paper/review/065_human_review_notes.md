# Human Review Notes - Phase 6.5 Adversarial Review

These MINOR issues were collected during adversarial review but NOT auto-fixed.
Human review recommended before final publication.

---

## Round 1 Notes

### R1-N01: Future-dated citation
- **Location:** Section 2.3, Related Work
- **Issue:** "Aiersilan et al. (2026)" - future date suggests synthetic citation
- **Suggested Action:** Verify citation year or mark as placeholder

### R1-N02: Tilde on exact value
- **Location:** Section 3.3 Methodology
- **Issue:** "~60 iterations" uses tilde when ground truth shows exactly 60
- **Suggested Action:** Remove tilde, use "60 iterations"

### R1-N03: Hook overhead sign ambiguity
- **Location:** Section 3.2
- **Issue:** Paper says "<5% runtime overhead" but ground truth shows -3.4% (negative = faster)
- **Suggested Action:** If hooks make inference faster, state this explicitly as a benefit

### R1-N04: Tilde on AUROC values
- **Location:** Abstract, Introduction
- **Issue:** Uses "~0.62 AUROC" when ground truth shows exact 0.623
- **Suggested Action:** Use exact value 0.623 (or 0.62 without tilde)

### R1-N05: Novelty framing
- **Location:** Section 1, Introduction
- **Issue:** "We propose probing" overstates when Burns 2023, Kossen 2024 already probe hidden states
- **Suggested Action:** Reframe as "we apply probing to correctness prediction" vs "we propose probing"
- **Severity Note:** Borderline between MINOR style and substantive claim - flagged for human judgment

### R1-N06: Baseline scope
- **Location:** Section 4, Experiments
- **Issue:** Missing comparisons to Semantic Entropy Probes (Kossen 2024), self-consistency
- **Suggested Action:** Add to Limitations section or run additional experiments

### R1-N07: Dataset scope
- **Location:** Section 4.1
- **Issue:** Only TriviaQA tested despite narrative blueprint listing Natural Questions
- **Suggested Action:** Acknowledge single-dataset limitation explicitly

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 3 (N02, N04, N05) |
| Clarity | 2 (N01, N03) |
| Scope | 2 (N06, N07) |
| **Total** | **7** |

---

*Generated: 2026-08-18 | Phase 6.5 Round 1*
