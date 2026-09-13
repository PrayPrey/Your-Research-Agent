# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI — collect for human decision.

**Generated:** 2026-04-30T16:45:00Z
**Rounds Completed:** R1 (R2 pending)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 2 |
| Formatting | 0 |
| **Total** | **3** |

---

## Round 1 Issues

### Style

1. **MINOR-001** — Introduction, paragraph 1 (hook sentence)
   - **Issue:** Blueprint specified opening with concrete numbers ("40% of the time on TruthfulQA, fail 30% of adversarial prompts") for maximum visceral impact. Actual paper uses vaguer language: "nearly half of TruthfulQA prompts, collapse under adversarial perturbations."
   - **Suggestion:** Consider replacing with: "A language model that achieves 70% accuracy on MMLU may still hallucinate on 40% of TruthfulQA prompts, fail 30% of adversarial inputs, and emit confidently wrong answers..."
   - **Note:** Concrete numbers in hooks are more memorable for busy reviewers; vague language weakens first impression.

### Clarity

2. **MINOR-002** — Section 7 (Conclusion), numbered list items 1–2
   - **Issue:** Numbered items 1–2 state findings as established facts without repeating the synthetic-data qualifier: "A latent epistemic reliability factor is detectable and statistically recoverable" and "Epistemic reliability is nearly orthogonal to MMLU capability." The paragraph above says "Under synthetic pipeline validation" but the list itself reads as clean empirical findings.
   - **Suggestion:** Add parenthetical to each item, e.g., "(under synthetic pipeline validation)" or restructure as "Under synthetic pipeline validation, a latent... is detectable..."
   - **Note:** MAJOR-001 fix already added "(under synthetic validation)" to item 2; item 1 may also benefit.

3. **MINOR-003** — Section 5.1, correlation table, ECE vs AdvGLUE row
   - **Issue:** Paper reports CI [−0.882, −0.386] for ECE vs AdvGLUE drop. The h-e1/04_validation.md source shows [−0.890, −0.380]; the h-m2/04_validation.md shows [−0.8822, −0.3862]. The paper value matches h-m2's rounded CI but the table is in the H-E1 results section.
   - **Suggestion:** Verify which source CI is the canonical one for Section 5.1. If using h-m2 values in an h-e1 result table, add a footnote or harmonize to h-e1 source.
   - **Note:** Within bootstrap variability; acceptable as-is but harmonization would prevent reviewer questions.

---

## Recommended Priority

1. **Fix First (high visibility):** MINOR-002 — Conclusion items missing synthetic qualifier
2. **Consider:** MINOR-001 — Hook strengthening (subjective but impactful)
3. **Optional:** MINOR-003 — CI source harmonization (acceptable as-is)

---

*Note: These issues do not block paper acceptance but improve overall quality.*
