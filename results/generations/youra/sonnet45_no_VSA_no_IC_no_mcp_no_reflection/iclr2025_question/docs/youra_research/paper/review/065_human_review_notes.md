# Human Review Notes - Round 1
# MINOR Issues for Final Polish

**Date**: 2026-08-28  
**Paper**: 06_paper.md  
**Review**: 065_review_r1.md

---

## MINOR Issues (Do NOT fix in automated revision)

These are minor style, formatting, and grammatical issues collected for human review during final polish.

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Abstract, sentence 2 | 60+ word sentence — split for readability | clarity | Split long sentence about entropy-based uncertainty |
| Line 8 (Introduction) | "deploy large language models need" — grammatical error | grammar | Change to "deploying large language models requires" |
| Line 14 (Introduction) | Long sentence (60+ words) starting "We discovered this dependency..." | clarity | Split into 2-3 shorter sentences |
| Line 20 (Introduction) | "threefold" contributions | style | Consider "three contributions" (less formal) |
| Line 56 (Related Work) | "meta-contribution" — jargon | clarity | Consider "methodological contribution to experimental design" |
| Line 289 (Results) | "Mean: 4.72 nats" — precision | style | Round to 4.7 unless precision matters |
| Line 296 (Results) | Inconsistent decimal precision (0.285 vs 4.72) | formatting | Standardize to 2-3 decimal places throughout |
| Line 91 (Methodology) | "torch.sum(probs * torch.log(probs + ε), dim=-1)" — missing negative sign? | technical | Verify formula matches Shannon entropy (negative sign) |
| Line 312 (Results) | Table alignment may be off | formatting | Check table rendering in final output |
| Line 429 (Discussion) | "(Fanelli, 2012)" citation not in Related Work | citation | Add citation to Related Work or remove |
| Line 517 (Conclusion) | "Both statements are true" — slightly informal | tone | Rephrase for formal conclusion style |

---

## Notes

These issues are marked as MINOR in the adversarial review and should be addressed by human reviewers during final polish. They do not affect the paper's scientific validity, argument structure, or credibility.

**Total MINOR issues**: 11

---

# Human Review Notes - Round 2
# MINOR Issues for Final Polish (Additional)

**Date**: 2026-08-28  
**Paper**: 06_paper_r1.md  
**Review**: 065_review_r2.md

---

## MINOR Issues from R2 (Do NOT fix in automated revision)

These are additional minor style and terminology issues identified in Round 2 review.

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Abstract, sentence 2 | 60+ word sentence — split for readability | clarity | Split: "We demonstrate this through entropy extraction experiments on TriviaQA. Infrastructure validation succeeded (100% extraction rate, 8.20% disagreement cases). Hypothesis testing failed (Spearman ρ = NaN due to zero-variance correctness)." |
| Introduction, paragraph 1 | Dense paragraph (8 sentences, 180+ words) | clarity | Break after sentence 3: Para 1 (problem) = sentences 1-3 (LLMs in high-stakes, selective prediction, max-prob limitations); Para 2 (our work) = sentences 4-8 (entropy hypothesis, test failure, model substitution discovery) |
| Abstract, line 3 | "validity threshold" used before defined | terminology | Replace with "invalidate such experiments" (already used earlier in abstract for coherence) |

---

## Notes

R2 review confirmed all R1 MAJOR issues successfully resolved. These 3 new MINOR issues are polish-only improvements for final readability.

**R2 Recommendation**: CONDITIONAL_ACCEPT (publication-ready with optional minor polish)

**Total MINOR issues (cumulative)**: 14 (11 from R1 + 3 from R2)
