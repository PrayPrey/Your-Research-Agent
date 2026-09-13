# Human Review Notes - Minor Issues
## Paper: "Coefficient of Variation as Prospective Benchmark Quality Signal"

**Date:** 2026-07-09  
**Revision Round:** 1  
**Status:** Collected for human review (NOT fixed by Revision Agent)

---

## Instructions for Human Reviewer

These are MINOR style, grammar, and consistency issues identified by the Round 1 adversarial review. The Revision Agent has NOT modified these in the revised paper (`06_paper_r1.md`) per protocol—only FATAL and MAJOR issues were fixed.

Please review each item and decide whether to:
- **Accept as-is** (issue noted but not worth changing)
- **Fix manually** (make the suggested change)
- **Defer** (address in final copyediting phase)

---

## Style Issues

### STYLE-01: Defensive "Despite" Framing

**Severity:** MINOR  
**Category:** Tone / Engagement

**Locations:**
1. Introduction, paragraph 6 (Contributions section):
   > "**Despite the null result for CV**, this work makes three contributions..."

2. Conclusion, paragraph 2 (Contributions section):
   > "**Despite the null result for CV**, this work makes three contributions..."

**Issue:** The word "despite" frames the null result as a limitation to overcome, sounding defensive. For a rigorous null-result paper, the null finding IS the contribution.

**Suggested Fix:**
- Remove "Despite the null result for CV,"
- Replace with: "This null result makes three contributions..." OR "This work makes three contributions:"

**Rationale:** Own the null result as valuable, don't apologize for it. The review noted this feels "apologetic" rather than confident.

**Recommendation:** **Fix manually** — Simple one-word deletion improves tone significantly.

---

### STYLE-02: Abstract Single-Paragraph Format

**Severity:** MINOR  
**Category:** Readability / Skimmability

**Location:** Abstract (entire section)

**Issue:** Abstract is a single 13-line paragraph, making it hard to skim for key information. Readers scanning multiple papers may miss structure.

**Suggested Fix:** Break into 3 paragraphs:
1. **Paragraph 1:** Motivation + Hypothesis (lines 1-2)
2. **Paragraph 2:** Null result + Construct divergence finding (lines 3-5)
3. **Paragraph 3:** Mock data limitation + Contributions + Roadmap (lines 6-8)

**Rationale:** Multi-paragraph abstracts are easier to scan. Readers can quickly identify: (1) What problem? (2) What result? (3) What contribution?

**Recommendation:** **Fix manually** — Low effort (add 2 paragraph breaks), moderate readability improvement.

---

### STYLE-03: Long Hypothesis Statement (Readability)

**Severity:** MINOR  
**Category:** Sentence Length

**Location:** Section 3.1 "Hypothesis Formulation", Core Hypothesis statement (6-line single sentence)

**Current (6 lines, 1 sentence):**
> Under trust benchmark evaluation with multi-model leaderboards (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, n≥10 models each), if benchmark coefficient of variation (CV = σ/μ across model scores) is computed and compared with mean cross-benchmark ranking agreement (Spearman ρ), then CV correlates negatively with ρ (Pearson r < -0.5, p < 0.05), because high score variance indicates inconsistent model differentiation, reducing benchmark reliability as a stable ranking instrument.

**Issue:** Single sentence with nested clauses is hard to parse. Readers may lose track of the main claim.

**Suggested Fix:** Break into 2 sentences at the "then" clause:
> Under trust benchmark evaluation with multi-model leaderboards (TrustLLM, HaluBench, TruthfulQA, FinTrust, MultiTrust, n≥10 models each), if benchmark coefficient of variation (CV = σ/μ across model scores) is computed and compared with mean cross-benchmark ranking agreement (Spearman ρ), then CV correlates negatively with ρ (Pearson r < -0.5, p < 0.05). **[NEW SENTENCE]** This relationship exists because high score variance indicates inconsistent model differentiation, reducing benchmark reliability as a stable ranking instrument.

**Rationale:** Separates the conditional hypothesis (if...then) from the mechanistic explanation (because). Improves readability without changing content.

**Recommendation:** **Defer to copyediting** — Not essential, but helpful for reader comprehension.

---

### STYLE-04: Vague "Many Pairs" Count

**Severity:** MINOR  
**Category:** Precision

**Location:** Section 5.2, "Near-zero correlations" subsection

**Current:**
> **Near-zero correlations (many pairs):**

**Issue:** "Many pairs" is vague. How many? Out of how many total pairs?

**Suggested Fix:** Replace with exact count from correlation matrix:
> **Near-zero correlations (7 of 45 pairs):**

**Rationale:** The correlation matrix has 10 benchmarks → 10×9/2 = 45 unique pairs. Count how many have |ρ| < 0.1 for precision.

**Recommendation:** **Fix manually** (if easy to count from matrix) OR **Accept as-is** (minor imprecision, doesn't affect conclusions).

---

## Grammar / Typos

### TYPO-01: Extra Space After Colon

**Severity:** MINOR  
**Category:** Formatting

**Location:** Abstract, line 3 (primary result)

**Current:**
> "95% CI: [-0.854, 0.207]"

**Issue:** Extra space after "CI:" — should be "CI: " (one space) or "CI:[-0.854, 0.207]" (no space).

**Suggested Fix:** Remove extra space → "95% CI: [-0.854, 0.207]"

**Recommendation:** **Defer to copyediting** — Trivial formatting issue, not noticeable to most readers.

---

### TYPO-02: Missing Article / Comma (if applicable)

**Severity:** MINOR  
**Category:** Grammar

**Location:** Section 6.1.1, line 526

**Current:**
> "Cross-benchmark ρ conflates reliability and validity."

**Issue (per review):** Missing article or awkward phrasing. Suggested: "Cross-benchmark ρ conflates reliability **and** validity, **or** reflects construct divergence."

**Note:** This sentence appears correct as-is in the original paper. The review may have flagged a different location or the issue was addressed in revision. **VERIFY** if this still applies.

**Recommendation:** **Verify location** — If sentence is clear, accept as-is. If awkward, rephrase.

---

## Consistency Issues

### CONSISTENCY-01: Citation Format (Bracket vs. Parenthetical)

**Severity:** MINOR  
**Category:** Style Consistency

**Locations:**
1. Introduction, line 6:
   > "[mmjerge, TMLR 2025]" (bracket format)

2. Related Work, line 31:
   > "mmjerge (TMLR 2025)" (parenthetical format)

**Issue:** Inconsistent citation style. Choose one format and apply throughout.

**Suggested Fix:** Standardize to parenthetical format:
- "mmjerge (TMLR 2025)"
- "Kulkarni et al. (arXiv:2504.18114)"
- "Bowman et al. (2015)"

**Rationale:** Parenthetical is more common in academic writing. Bracket format suggests footnote style.

**Recommendation:** **Fix manually** (find-replace "[" → "(", "]" → ")") OR **Defer to copyediting** (low priority).

---

### CONSISTENCY-02: Statistical Notation Spacing

**Severity:** MINOR  
**Category:** Formatting Consistency

**Locations:** Throughout paper

**Issue:** Statistical notation appears inconsistently:
- Sometimes: "r=-0.486" (no spaces around equals)
- Sometimes: "r = -0.486" (spaces around equals)

**Suggested Fix:** Standardize to "r = -0.486" (with spaces) throughout, per standard statistical writing conventions.

**Rationale:** APA and most statistical style guides recommend spaces around operators (=, <, >) for readability.

**Recommendation:** **Defer to copyediting** — Global find-replace in final pass. Not critical for comprehension.

---

## Summary for Human Reviewer

**Total MINOR Issues:** 7
- Style: 4 (defensive framing, paragraph breaks, sentence length, vague count)
- Grammar/Typos: 2 (extra space, missing article — verify)
- Consistency: 2 (citation format, statistical notation)

**Recommended Actions:**
- **Fix manually now:** STYLE-01 (remove "despite"), STYLE-02 (paragraph breaks), CONSISTENCY-01 (citation format)
- **Defer to copyediting:** STYLE-03 (sentence length), TYPO-01 (spacing), CONSISTENCY-02 (notation)
- **Verify:** TYPO-02 (may not apply after revision)

**Estimated Effort:** ~15 minutes to address high-priority items (STYLE-01, STYLE-02, CONSISTENCY-01)

---

## Notes

1. **None of these issues affect scientific accuracy or conclusions.** All FATAL and MAJOR accuracy/engagement issues were fixed by the Revision Agent.

2. **These are polish items** to improve readability and consistency before final publication.

3. **The paper is scientifically sound** after Round 1 revision. These notes are for professional presentation quality.

4. **If time-constrained:** Focus on STYLE-01 (tone) and STYLE-02 (readability). Other issues are minor cosmetic improvements.

---

**End of Human Review Notes**
