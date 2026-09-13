# Adversarial Review Changelog
**Paper:** Epistemic Reliability as a Latent Dimension in LLM Trustworthiness
**Generated:** 2026-04-30T16:45:00Z

---

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

### MAJOR-001: Survival Fraction "<1%" Claim Corrected

**Issue:** Paper claimed "MMLU accounts for less than 1% of the calibration–hallucination correlation (survival fraction = 0.943)" — statistically imprecise. Survival fraction 0.943 means 5.7% confound reduction, not <1%.

**Changes made:**

1. **Abstract** — Changed: "calibration–hallucination correlation surviving MMLU control at 94% strength (partial ρ=−0.758)" → "surviving MMLU control with 94.3% retention (partial ρ=−0.758; controlling for MMLU reduces the correlation by only 5.7%)"

2. **Section 1, Contribution 2** — Changed: "MMLU accounts for less than 1% of the calibration–hallucination correlation (survival fraction = 0.943)" → "the survival fraction of 0.943 confirms that controlling for MMLU reduces the calibration–hallucination correlation by only 5.7% — capability explains a negligible share of this link"

3. **Section 5.2** — Changed: "The survival fraction is 0.943 — MMLU accounts for <1% of the raw correlation" → "The survival fraction is 0.943 — controlling for MMLU reduces the calibration–hallucination correlation by only 5.7%, confirming that capability is not a meaningful confound"

4. **Section 7, Contribution 2** — Changed: "Survival fraction = 0.943 — MMLU explains <1% of the calibration–hallucination correlation" → "Survival fraction = 0.943 — controlling for MMLU reduces the calibration–hallucination correlation by only 5.7%" (also added "(under synthetic validation)" qualifier)

---

### MAJOR-002: Section 6.1 Discussion Framing Corrected

**Issue:** Section 6.1 asserted real-world implications from synthetic data results, contradicting the paper's own L1 limitation and abstract framing.

**Changes made:**

5. **Section 6.1, Key Findings paragraph 1** — Replaced assertive framing ("has a direct practical implication: MMLU-based model screening is essentially blind...") with conditional framing ("If this pattern replicates with real LLM evaluations (FW1), it would imply that..."). Added: "These results motivate but do not yet establish this practical implication."

---

### MAJOR-003: L7 Limitation Added (Psychometric Independence Assumption)

**Issue:** Missing acknowledgment that models within the same family are not independent observations, potentially inflating Tucker's congruence and factor stability estimates.

**Changes made:**

6. **Section 6.2** — Added L7: "Within-family non-independence. The psychometric framing treats N=30 models as independent subjects. However, models from the same family share pretraining data, architecture, and alignment procedure — violating the classical independence assumption..."

---

---

## Final Summary (v2.0)

**Total Revisions Made:** 7 (6 in R1, 1 in R2)
**Sections Modified:** Abstract, Section 1, Section 5.1, Section 5.2, Section 6.1, Section 6.2, Section 7
**Word Count Change:** ~6,438 → ~6,575 (+~137 words)

**Review Process:**
- Started: 2026-04-30T16:30:00Z
- Completed: 2026-04-30T17:00:00Z
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)

---

## Round 2 Revisions (06_paper_r1.md → 06_paper_r2.md)

### MAJOR-R2-001: Tucker's Congruence Inline Greedy-Only Caveat Added

**Issue:** Section 5.1 stated "Tucker's congruence φ = 1.000 confirms factor stability" without noting this is within the greedy decoding regime only. Tucker's congruence is defined as cross-condition stability; the T=0.7 condition was not executed. Claim was misleading without inline qualifier.

**Changes made:**

1. **Section 5.1, factor analysis paragraph** — Changed: "Tucker's congruence φ = 1.000 confirms factor stability." → "Tucker's congruence φ = 1.000 within the greedy decoding regime (T=0.7 cross-condition replication pre-registered as FW1; cross-condition stability unconfirmed — see L4)."

---

## Round 2 Summary

| Metric | Value |
|--------|-------|
| MAJOR issues fixed | 1 |
| FATAL issues fixed | 0 |
| Sections modified | Section 5.1 |
| Word count delta | +~15 words |
| MINOR issues collected | 0 new |

---

## Round 1 Summary

| Metric | Value |
|--------|-------|
| MAJOR issues fixed | 3 |
| FATAL issues fixed | 0 |
| Sections modified | Abstract, Section 1, Section 5.2, Section 6.1, Section 6.2, Section 7 |
| Word count delta | +~120 words (added L7 + conditional framing) |
| MINOR issues collected | 3 (in 065_human_review_notes.md) |
