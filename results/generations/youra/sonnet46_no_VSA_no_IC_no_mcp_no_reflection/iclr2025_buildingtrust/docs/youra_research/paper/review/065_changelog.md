# Adversarial Review Changelog
# Paper: Alignment Fingerprinting: DPO and SFT Models Are Separable by Truthfulness, Not Fairness
# Started: 2026-08-31T06:00:00+00:00

---

## Round 1 Revisions (R1 → 06_paper_r1.md)

### FATAL-001 Fix: Table 1 alignment label ambiguity for zephyr-7b-alpha

**Issue:** Table 1 listed zephyr-7b-alpha as the DPO model in P1, but Table 5 and ground truth label it as SFT. Contradiction between the mechanism analysis pair assignments and the existence analysis alignment labels.

**Fix:** Renamed Table 1 column from "DPO Model" to "DPO-aligned Model" and added explanatory footnotes (†, ‡) for zephyr-7b-alpha (SFT-labeled but paired as DPO-counterpart in mechanism analysis) and Llama-2-7b-chat (RLHF, not pure SFT). Table 1 title updated to clarify it applies to h-m1 mechanism analysis pairs.

**Sections modified:** Section 3 (Table 1, footnotes added)

---

### MAJOR-001 Fix: "+4.6pp" qualified as per-pair mean delta

**Issue:** "DPO models score +4.6pp higher on truthfulness on average" was ambiguous — group mean difference is only +1.1pp; +4.6pp is the per-pair mean delta.

**Fix:** Added "(per-pair mean delta)" qualifier at every occurrence of +4.6pp throughout the paper.

**Sections modified:** Abstract, Section 1 (C2), Section 5.2 (BBQ discussion), Section 7 (Summary point 2)

---

### MAJOR-002 Fix: BBQ group-mean vs per-pair discrepancy acknowledged

**Issue:** DPO BBQ group mean = 0.460 vs SFT = 0.422 (+3.8pp) appears to contradict the "null result" (per-pair delta = +0.5pp, k=3/6, p=0.66). This discrepancy was unacknowledged.

**Fix:** Added explanation before Table 7 in Section 5.2: the +3.8pp group mean is driven by model quality confounds; the paired comparison controls for this and yields the null result (+0.5pp, k=3/6).

**Sections modified:** Section 5.2 (paragraph before Table 7)

---

### MAJOR-003 Fix: C4 "first" claim hedged

**Issue:** Contribution C4 stated "the first paired DPO/SFT comparison" without epistemic hedge.

**Fix:** Added "to our knowledge" — "to our knowledge, the first paired DPO/SFT comparison..."

**Sections modified:** Section 1 (C4)

---

### MAJOR-004 Fix: P4 RLHF sensitivity analysis added to L4

**Issue:** Pair P4 uses RLHF model (Llama-2-chat) as SFT in mechanism analysis; no sensitivity analysis existed.

**Fix:** Extended L4 in Section 6 to include: "Sensitivity analysis excluding P4 yields k_TruthfulQA=3/5 pairs with DPO higher and mean delta≈+3.8pp — qualitative conclusion unchanged."

**Sections modified:** Section 6 (L4 paragraph)

---

### MAJOR-005 Fix: Abstract "establishes" softened

**Issue:** "establish practical alignment auditing" overclaims for n=12 pilot study.

**Fix:** Changed to "demonstrate the feasibility of practical alignment auditing."

**Sections modified:** Abstract (last sentence of paragraph 1)

---

## Minor Issues Collected from R1 (NOT auto-fixed — see 065_human_review_notes.md)

- MINOR-001: Figure 1 caption lacks DPO/SFT color specification
- MINOR-002: Introduction frames classification as "key insight" when truthfulness finding is the real insight

---

## Round 2 Revisions (R1 → 06_paper_r2.md)

### R2-MAJOR-001 Fix: Sensitivity analysis delta corrected from +3.8pp to +3.6pp

**Issue:** L4 sensitivity analysis stated "mean delta≈+3.8pp" but calculation excluding P4 yields (−0.0096+0.0223+0.0967−0.0097+0.0792)/5 = 0.1789/5 = 0.03578 ≈ +3.6pp.

**Fix:** Changed "≈+3.8pp" to "≈+3.6pp" in Section 6 (L4 paragraph).

**Sections modified:** Section 6 (L4)

---

### R2-MAJOR-002 Fix: "establishes" softened in Section 6 and Section 7

**Issue:** Two remaining instances of "establishes" with overclaiming tone missed in R1.

**Fix:**
- Section 6, Finding 1: "establishes that DPO and SFT training produce" → "provides evidence that DPO and SFT training produce"
- Section 7, Conclusion: "establishes that the alignment fingerprint is real and statistically reliable" → "confirms that the alignment fingerprint is present and statistically significant at pilot scale"

**Sections modified:** Section 6 (Finding 1), Section 7 (Conclusion paragraph 1)

---

## Minor Issues Collected from R2 (NOT auto-fixed — see 065_human_review_notes.md)

- R2-MINOR-001: Figure number vs filename (fig3_fisher_criterion.png vs Figure 6) — human verification needed
- R2-MINOR-002: "0.5–4.6pp range" in Section 6 conflates different benchmark deltas

---

## Final Summary

**Total Revisions Made:** 7 (5 MAJOR R1, 2 MAJOR R2)
**Sections Modified:** Abstract, Section 1 (C2, C4), Section 3 (Table 1), Section 5.2, Section 6 (L4, Finding 1), Section 7
**Word Count Change:** ~+120 words (additions for BBQ explanation, footnotes, sensitivity analysis)

**Review Process:**
- Started: 2026-08-31T06:00:00+00:00
- Completed: 2026-08-31T07:00:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert (R1); accuracy_checker, skeptical_expert (R2)

**Files Generated:**
- 06_paper_r1.md (after Round 1 revisions)
- 06_paper_r2.md (after Round 2 revisions — FINAL)
- 06_paper_final.md (copy of r2)
- 065_review_r1.md (Round 1 adversary report)
- 065_review_r2.md (Round 2 adversary report)
- 065_review_summary.md (consolidated summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
