# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review. NOT auto-fixed.

**Date:** 2026-08-31
**Rounds Completed:** 2 (R1 + R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 6 |
| Style | 2 |
| Formatting | 1 |
| **Total** | **9** |

---

## Round 1 Issues

### Clarity

1. **MINOR-AC-004** — Section 3 (LLM Sampling), "Temperature=0.7 matches the setting used in SelfCheckGPT [Manakul et al., 2023]"
   - **Issue:** SelfCheckGPT (arXiv:2303.08896) may use temperature=1.0, not 0.7, in their main experiments. Verify the actual temperature from the paper before final submission.
   - **Suggested fix:** If different, change to: "We use temperature=0.7 within the sampling regime common in prior work [Manakul et al., 2023; Kuhn et al., 2023], balancing output diversity with coherence."

2. **MINOR-SE-001** — Throughout paper, term "systematic confabulation"
   - **Issue:** "Confabulation" has prior usage in LLM hallucination literature (e.g., Ji et al. 2023 survey). The paper uses it as if coining it without acknowledgment.
   - **Suggested fix:** Add a footnote on first use: "We use 'systematic confabulation' to denote the regime where RLHF fine-tuning produces consistent outputs for incorrect beliefs; the term 'confabulation' has appeared in adjacent literature [e.g., Ji et al., 2023] though not in this regime-specific sense."

3. **MINOR-SE-002** — Section 5 (Primary Result), AUROC values reported without confidence intervals
   - **Issue:** For a negative result, reporting bootstrap 95% CIs would strengthen the claim that these values are not significantly different from 0.50. Standard practice for AUROC negative results.
   - **Suggested fix:** Add CIs: "SMC-NLI AUROC=0.4933 (95% CI: [0.46, 0.53])" — expected range confirms chance level.

4. **MINOR-SE-003** — Section 3 (LLM Sampling), N=10 samples per question
   - **Issue:** No sensitivity analysis on N. Whether N=5 or N=20 changes conclusions is unaddressed.
   - **Suggested fix:** Add to Section 6 (Limitations) or Future Work: "We use N=10 samples following Kuhn et al. [2023]; sensitivity to N (whether larger N could reveal a small discriminative signal) remains future work."

### Style

5. **MINOR-BR-003** — Section 5 (Mechanism Analysis), last sentence: "The model is 'confidently consistent' regardless of factual accuracy."
   - **Issue:** "Confidently consistent" is a third informal term alongside the formally defined "stochastic hallucination" and "systematic confabulation." Creates minor terminological inconsistency.
   - **Suggested fix:** Replace with "The model exhibits systematic confabulation regardless of factual accuracy."

6. **MINOR-BR-004** — Section 6 (Discussion), subsection organization
   - **Issue:** Five subsections without clear hierarchy. "The Systematic Confabulation Regime" and "Alternative Explanation" are both interpretive and could be combined. "Broader Impact" (2 paragraphs) is short enough to fold into Conclusion.
   - **Suggested fix:** Consider merging to 3 subsections: "Interpreting the Failure" (combining subsections 1+2), "Implications for Practitioners," "Limitations." Move Broader Impact into Conclusion.

### Formatting

7. **MINOR-BR-002** — Abstract, length ~220 words
   - **Issue:** ICML 2025 guidelines typically expect abstracts 150-180 words. Current abstract is ~220 words.
   - **Suggested fix:** Trim C4 (Infrastructure contribution) description — reduce from 2 sentences to 1. Also trim the last sentence about "release validated SMC infrastructure" — this can be a footnote or in the Conclusion.

---

## Recommended Priority

1. **Fix First:** MINOR-AC-004 (verify T=0.7 citation accuracy — factual claim)
2. **Fix Second:** MINOR-SE-002 (add bootstrap CIs — strengthens negative result for reviewers)
3. **Consider:** MINOR-SE-001 (terminology footnote — prevents reviewer pedantry)
4. **Consider:** MINOR-BR-002 (abstract length — ICML compliance)
5. **Optional:** MINOR-BR-003, MINOR-BR-004 (style improvements)
6. **Future Work Note:** MINOR-SE-003 (N sensitivity — add to Limitations section)

---

## Round 2 Issues

### Clarity

8. **MINOR-R2-001** — Section 3 (Dataset): "standard error < 0.02 at this sample size"
   - **Issue:** DeLong SE formula for AUROC near 0.5 with N=500 per class gives approximately 0.022, not strictly < 0.02. Claim is slightly optimistic.
   - **Suggested fix:** Change to "standard error ≈ 0.02 at this sample size" or add "(SE ≈ 0.022 by DeLong estimator)."

9. **MINOR-R2-002** — Section 3 (LLM Sampling), "Temperature=0.7 matches the setting used in SelfCheckGPT [Manakul et al., 2023]"
   - **Issue:** Persists from MINOR-AC-004 (R1). SelfCheckGPT main experiments may use T=1.0 rather than T=0.7. Requires verification against the actual paper.
   - **Suggested fix:** If T differs, use: "We use temperature=0.7 within the sampling regime of prior work, balancing output diversity with coherence."

---

## Recommended Priority

1. **Fix First:** MINOR-AC-004 / MINOR-R2-002 (verify T=0.7 citation — factual claim, same issue)
2. **Fix Second:** MINOR-SE-002 (add bootstrap CIs — strengthens negative result)
3. **Fix Third:** MINOR-R2-001 (SE precision — "< 0.02" → "≈ 0.02")
4. **Consider:** MINOR-SE-001 (terminology footnote)
5. **Consider:** MINOR-BR-002 (abstract length — ICML compliance)
6. **Optional:** MINOR-BR-003, MINOR-BR-004 (style improvements)
7. **Future Work Note:** MINOR-SE-003 (N sensitivity — add to Limitations)

---

*These issues do not block paper acceptance but improve overall quality and reviewer experience.*
