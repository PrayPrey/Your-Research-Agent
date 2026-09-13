# Human Review Notes — MINOR Issues (Round 1)

**Review Date:** 2026-07-09  
**Deferred From:** 065_review_r1.md  
**Status:** FOR HUMAN REVIEW — NOT AUTO-APPLIED

---

## Instructions

These MINOR issues (typos, grammar, style, clarity) were identified by the adversarial reviewer but are NOT automatically fixed by the revision agent. Human judgment is required to determine:
1. Whether the fix improves readability without changing meaning
2. Whether style preferences are appropriate for target venue (ICML 2025)
3. Whether "issues" are actually legitimate problems or reviewer nitpicks

**Review each issue and decide: ACCEPT / REJECT / MODIFY**

---

## Issue Table

| ID | Type | Location | Issue | Suggested Fix | Priority | Decision |
|----|------|----------|-------|---------------|----------|----------|
| MINOR-01 | Consistency | Line 10 (Abstract) | Inconsistent hyphenation: "literature-reported" vs "instruction-count" | Standardize: "literature-reported instruction-count CV" | Low | [ ] |
| MINOR-02 | Clarity | Line 183 (Section 3.1) | "Lagrangian relaxation" undefined on first use | Add brief explanation: "(a constrained optimization technique)" | Medium | [ ] |
| MINOR-03 | Consistency | Line 659 (Section 6.1) | Inconsistent capitalization: "High-Confidence Finding" (title case) vs other subsections (sentence case) | Change to: "High-confidence finding:" | Low | [ ] |
| MINOR-04 | Consistency | Line 701 (Section 6.3.2) | Math notation inconsistency: "execution correctness + CodeBLEU" vs "execution + CodeBLEU" (earlier) | Standardize to: "execution correctness + structural similarity (CodeBLEU)" | Low | [ ] |
| MINOR-05 | Citation | Lines 299, 537 | Patterson & Hennessy CPU time equation cited without full reference | Add: "Patterson, D. A., & Hennessy, J. L. (2017). *Computer Architecture: A Quantitative Approach* (6th ed.). Morgan Kaufmann. See Chapter 1.6." | High | [ ] |
| MINOR-06 | Clarity | Section 3 | Acronym overload: CV, Cohen's d, Spearman ρ, RL, PoC, AST, PMU, CPI introduced in 200 lines | Consider adding notation table in Methodology or Appendix | Medium | [ ] |
| MINOR-07 | Reference | Line 478 | "see Figure 1" but Figure 1 not visible (path: ../figures/fig_1.png) | If Figure not visible in review document, expand caption description | Low | [ ] |
| MINOR-08 | Style | Throughout | Overuse of em-dashes (47 in ~15,000 words, avg 3 per section). Example: "If proxies are noisy—high intra-implementation variance—or platform-specific—low cross-hardware correlation—RL training optimizes false signals" | Replace some em-dashes with periods or semicolons | Low | [ ] |
| MINOR-09 | Voice | Line 660, 831 | Passive voice in key claims: "CodeBLEU validation is high-confidence" (passive) | Consider active: "We have high confidence in CodeBLEU validation" | Low | [ ] |
| MINOR-10 | Repetition | Throughout | "Test before optimize" appears 5 times (Intro, 5.5.3, 6.7, Conclusion ×2) | Vary phrasing: "prerequisite validation", "independent proxy testing" | Low | [ ] |
| MINOR-11 | Definition | Lines 124, 126, 183, 166 | Terms used before defined: "Hierarchical regression" (line 124), "Leave-cluster-out validation" (line 126), "Lagrangian relaxation" (line 183), "Pooled standard deviation" (line 166) | Add "Key Terms" callout box in Section 3.1 or move definitions earlier | Medium | [ ] |
| MINOR-12 | Citation | Throughout | Inconsistent citation style: Author-prominent "Becker et al. (2025) demonstrated" vs Parenthetical "the literature confirms (COFFE, 2025)" | Pick one style (recommend author-prominent for key claims, parenthetical for supporting) | Low | [ ] |

---

## Detailed Issue Descriptions

### MINOR-01: Inconsistent Hyphenation

**Location:** Abstract, line 10

**Current text:**
> "efficiency metrics require hardware performance instrumentation to achieve comparable stability (PoC wall-clock CV=6.22% versus literature-reported instruction-count CV of 2-3%)"

**Issue:** "literature-reported" uses hyphen, "instruction-count" uses hyphen, but inconsistently applied (earlier text has "instruction count" without hyphen).

**Reviewer suggestion:** Standardize hyphenation throughout.

**Human decision needed:** 
- ACCEPT if standardization improves consistency
- REJECT if hyphenation rules are already correct per Chicago/APA style
- CHECK: Does ICML style guide specify hyphenation for compound modifiers?

---

### MINOR-02: Lagrangian Relaxation Undefined

**Location:** Section 3.1, line 183

**Current text:**
> "Lagrangian relaxation dynamically adjusts penalty coefficients when individual tasks violate constraints."

**Issue:** Technical term from optimization theory used without definition. General ML audience may not know this.

**Reviewer suggestion:** Add brief explanation or reference.

**Human decision needed:**
- ACCEPT to improve accessibility for non-optimization-expert readers
- REJECT if ICML audience expected to know this term
- MODIFY: Add footnote instead of inline definition?

---

### MINOR-03: Inconsistent Capitalization

**Location:** Section 6.1, line 659

**Current text:**
> "**High-Confidence Finding:** CodeBLEU demonstrates..."

**Issue:** Subsection headings elsewhere use sentence case ("High-confidence finding:"), this uses title case.

**Reviewer suggestion:** Standardize to sentence case.

**Human decision needed:**
- ACCEPT for consistency
- REJECT if emphasis (title case) is intentional here
- CHECK: Does ICML require specific heading capitalization?

---

### MINOR-04: Math Notation Inconsistency

**Location:** Section 6.3.2, line 701

**Current text:**
> "Multi-objective optimization proceeds with execution correctness + CodeBLEU (two objectives)"

**Earlier text (line 596):**
> "execution + CodeBLEU"

**Issue:** Inconsistent shorthand ("execution" vs "execution correctness").

**Reviewer suggestion:** Standardize to full form.

**Human decision needed:**
- ACCEPT to improve consistency
- REJECT if variation is stylistic (avoid repetition)

---

### MINOR-05: Patterson & Hennessy Citation Missing

**Location:** Lines 299, 537 (and other mentions of CPU time equation)

**Current text:**
> "The Patterson & Hennessy CPU time equation shows..."

**Issue:** Textbook claim without full citation. Should cite specific edition/chapter.

**Reviewer suggestion:**
> "Patterson, D. A., & Hennessy, J. L. (2017). *Computer Architecture: A Quantitative Approach* (6th ed.). Morgan Kaufmann. See Chapter 1.6: CPU Performance Equation."

**Human decision needed:**
- **ACCEPT (HIGH PRIORITY)** — This is standard practice for textbook citations
- CHECK: Which edition is actually referenced? 5th (2011)? 6th (2017)? RISC-V edition (2017)?

---

### MINOR-06: Acronym Overload

**Location:** Section 3 (Methodology)

**Issue:** Many technical acronyms introduced in short span:
- CV (Coefficient of Variation)
- Cohen's d (effect size)
- Spearman ρ (rank correlation)
- RL (reinforcement learning)
- PoC (proof-of-concept)
- AST (abstract syntax tree)
- PMU (performance monitoring unit)
- CPI (cycles per instruction)

**Reviewer suggestion:** Add notation table in Methodology or Appendix.

**Human decision needed:**
- ACCEPT to improve readability for readers skimming Methodology
- REJECT if acronyms are standard in target community (ICML ML/systems audience knows RL, AST, etc.)
- MODIFY: Define on first use only, no table?

---

### MINOR-07: Figure 1 Reference

**Location:** Line 478

**Current text:**
> "![Gate Metrics Comparison](../figures/fig_1.png)  
> **Figure 1:** Normalized gate metrics..."

**Issue:** If Figure not visible in review PDF, readers can't verify bar chart description.

**Reviewer suggestion:** Expand caption to describe bars/thresholds textually.

**Human decision needed:**
- ACCEPT if figures may not render in all review formats
- REJECT if ICML submission includes figures properly
- CHECK: Does camera-ready format guarantee figure visibility?

---

### MINOR-08: Overuse of Em-Dashes

**Location:** Throughout (47 occurrences in ~15,000 words)

**Example (lines 119-120):**
> "If proxies are noisy—high intra-implementation variance—or platform-specific—low cross-hardware correlation—RL training optimizes false signals"

**Issue:** Multiple nested em-dashes create dense, hard-to-parse sentences.

**Reviewer suggestion:** Replace some with periods or semicolons.

**Human decision needed:**
- ACCEPT to improve readability (simplify complex sentences)
- REJECT if em-dashes are stylistic choice for emphasis
- MODIFY: Fix only sentences with ≥3 em-dashes?

---

### MINOR-09: Passive Voice in Key Claims

**Location:** Lines 660, 831

**Example (line 660):**
> "CodeBLEU validation is high-confidence"

**Reviewer suggestion:** Use active voice:
> "We have high confidence in CodeBLEU validation"

**Human decision needed:**
- ACCEPT to improve clarity and directness
- REJECT if passive voice preferred in ICML style (some venues prefer passive for objectivity)
- CHECK: Does ICML style guide specify active vs passive preference?

---

### MINOR-10: Repetitive Phrasing

**Location:** Throughout

**Phrase:** "Test before optimize" appears 5 times:
1. Introduction
2. Section 5.5.3
3. Section 6.7
4. Conclusion (2×)

**Reviewer suggestion:** Vary phrasing:
- "prerequisite validation"
- "independent proxy testing"
- "modular reliability assessment"

**Human decision needed:**
- ACCEPT to reduce repetition
- REJECT if "test before optimize" is intentional tagline/slogan
- MODIFY: Keep 2-3 uses, vary the rest?

---

### MINOR-11: Terms Used Before Defined

**Location:** Various (lines 124, 126, 183, 166)

**Terms:**
1. "Hierarchical regression" (line 124) — not defined until Section 3.1 Stage 2
2. "Leave-cluster-out validation" (line 126) — not defined in main text
3. "Lagrangian relaxation" (line 183) — never defined
4. "Pooled standard deviation" (line 166) — formula given, not intuition

**Reviewer suggestion:** Add "Key Terms" callout box in Section 3.1 or move definitions earlier.

**Human decision needed:**
- ACCEPT to improve accessibility
- REJECT if terms are standard in ML/statistics (audience expected to know)
- MODIFY: Add footnotes instead of callout box?

---

### MINOR-12: Inconsistent Citation Style

**Location:** Throughout

**Examples:**
- Author-prominent: "Becker et al. (2025) demonstrated" (used in Related Work)
- Parenthetical: "the literature confirms (COFFE, 2025)" (used in Results)

**Reviewer suggestion:** Pick one style:
- Author-prominent for key claims
- Parenthetical for supporting citations

**Human decision needed:**
- ACCEPT to standardize
- REJECT if variation is stylistic (author-prominent emphasizes source, parenthetical emphasizes claim)
- CHECK: Does ICML require specific citation style?

---

## Recommendation Summary

**High Priority (Recommend ACCEPT):**
- MINOR-05: Add Patterson & Hennessy full citation

**Medium Priority (Review Carefully):**
- MINOR-02: Define Lagrangian relaxation
- MINOR-06: Add acronym table or check if needed
- MINOR-11: Define technical terms earlier

**Low Priority (Stylistic Preference):**
- MINOR-01, 03, 04, 07, 08, 09, 10, 12: Consistency/style/clarity tweaks

---

## Human Reviewer Action Items

1. **Review ICML 2025 style guide** for citation format, heading capitalization, active/passive voice
2. **Verify Patterson & Hennessy edition** cited (5th? 6th? RISC-V?)
3. **Decide on em-dash policy** (reduce density vs. preserve style)
4. **Check acronym density** against typical ICML papers (is this unusual?)
5. **Make final accept/reject decision** for each issue
6. **Apply accepted fixes** manually or instruct revision agent

---

## Notes

- These issues do NOT affect paper correctness (those are FATAL/MAJOR)
- These are presentation/clarity improvements
- Some may be reviewer personal preference, not objective issues
- Balance readability improvements vs. preserving author's voice

---

# Human Review Notes — MINOR Issues (Round 2)

**Review Date:** 2026-07-10  
**Deferred From:** 065_review_r2.md  
**Status:** FOR HUMAN REVIEW — NOT AUTO-APPLIED

---

## R2 MINOR Issues Summary

R2 adversarial review (numerical verification) identified 7 MINOR issues focusing on precision, clarity, and consistency. These are stylistic improvements that do not affect correctness.

---

## R2 Issue Table

| ID | Type | Location | Issue | Suggested Fix | Priority | Decision |
|----|------|----------|-------|---------------|----------|----------|
| MINOR-R2-01 | Precision | Lines 466, 862 (Table 1, Conclusion) | CodeBLEU CV reported as 1.39% (rounded from 1.38565872%) | Use consistent rounding: 1.39% is correct 2-decimal rounding | Low | [ ] |
| MINOR-R2-02 | Consistency | main.py line 84 | Code comment references "COFFE finding" despite COFFE removed from paper | Update comment: "# CV ~1-2% (theoretical CPU time equation expectation)" | Medium | [ ] |
| MINOR-R2-03 | Clarity | Throughout | "Provisional" vs "PoC" inconsistency: sometimes "provisional findings" (line 694), sometimes "PoC results" (line 700) | Standardize: use "PoC" for proof-of-concept scope, "provisional" for confidence level | Low | [ ] |
| MINOR-R2-04 | Notation | Section 5.3.2 (line 543) | CPU time equation repeated twice: "instruction count (program-dependent, not hardware-dependent), not hardware-dependent)" | Remove duplicate: "instruction count (program-dependent, not hardware-dependent)" | Low | [ ] |
| MINOR-R2-05 | Reference | Section 6.5.2 (line 798) | CPU time equation mentioned again without Patterson & Hennessy inline citation | Add inline: "The CPU time equation (Patterson & Hennessy, 2017) shows..." | Medium | [ ] |
| MINOR-R2-06 | Precision | Table 1 caption | "All values from PoC synthetic validation" could specify "synthetic measurements via random number generation" for clarity | Expand: "All values from proof-of-concept using synthetic measurements (random noise models; real hardware validation pending)" | Low | [ ] |
| MINOR-R2-07 | Clarity | Section 6.3.5 (new limitation) | New subsection uses "domain-specific validation" 3 times in 300 words | Vary phrasing: "code generation RL calibration", "empirical threshold testing", "task-specific validation" | Low | [ ] |

---

## Detailed R2 Issue Descriptions

### MINOR-R2-01: CodeBLEU CV Precision

**Location:** Table 1 (line 466), Results (line 492), Conclusion (line 862)

**Current text:**
> "CodeBLEU CV = 1.39%"

**Actual value (results.json):** 1.38565872138252%

**Issue:** Rounding 1.386% → 1.39% is standard 2-decimal rounding (correct per mathematical rules), but R2 reviewer flagged this as "rounding inconsistency" because it rounds UP from .386 to .39.

**Reviewer comment:** "Use 1.39% consistently (correct rounding) but note actual value was 1.386% for transparency."

**Human decision needed:**
- ACCEPT: 1.39% is mathematically correct rounding (1.386 rounds to 1.39 at 2 decimals)
- REJECT: If over-precision preferred, use 1.4% (1 decimal) throughout
- MODIFY: Add footnote in Table 1: "Rounded to 2 decimal places; actual PoC value 1.3857%"

**Priority:** LOW (does not affect conclusions; 0.004% discrepancy negligible)

---

### MINOR-R2-02: Code Comment References COFFE

**Location:** h-e1/main.py line 84

**Current text:**
```python
base_runtime + np.random.normal(0, 0.01)  # CV ~1-2% (COFFE finding)
```

**Issue:** Main paper removed all COFFE citations per R1 revision, but implementation code comment still references "COFFE finding."

**Reviewer suggestion:**
```python
base_runtime + np.random.normal(0, 0.01)  # CV ~1-2% (theoretical CPU time equation expectation)
```

**Human decision needed:**
- ACCEPT to align code comments with paper (remove COFFE)
- REJECT if code comments document implementation history (COFFE was original motivation)
- MODIFY: Add both: "# CV ~1-2% (CPU time equation expectation; originally based on COFFE 2025 pre-print, now using Patterson & Hennessy theory)"

**Priority:** MEDIUM (affects code/paper consistency; users reading implementation may be confused)

---

### MINOR-R2-03: Provisional vs PoC Inconsistency

**Location:** Throughout (Section 6.1 lines 694-700, Conclusion line 862)

**Examples:**
- "provisional quantitative results" (line 694)
- "PoC-specific" (line 778)
- "PoC results" (line 700)

**Issue:** Inconsistent terminology for describing proof-of-concept limitations. Sometimes "provisional" (low confidence), sometimes "PoC" (scope limitation).

**Reviewer suggestion:** Standardize usage:
- "PoC" = proof-of-concept scope (synthetic data, not real infrastructure)
- "Provisional" = confidence level (findings subject to confirmation)

**Human decision needed:**
- ACCEPT to clarify distinction (PoC scope vs provisional confidence)
- REJECT if variation is stylistic (avoid repetition)

**Priority:** LOW (clarity improvement, not correctness issue)

---

### MINOR-R2-04: Duplicate Text in Section 5.3.2

**Location:** Section 5.3.2, line 752

**Current text:**
> "The Patterson & Hennessy CPU time equation provides theoretical grounding that instruction count is program-dependent (not hardware-dependent), not hardware-dependent)."

**Issue:** Phrase "not hardware-dependent" appears twice (typo from editing).

**Reviewer suggestion:**
> "The Patterson & Hennessy CPU time equation provides theoretical grounding that instruction count is program-dependent, not hardware-dependent."

**Human decision needed:**
- **ACCEPT (HIGH PRIORITY)** — Clear typo/editing artifact

**Priority:** MEDIUM (grammatical error, easy fix)

---

### MINOR-R2-05: Inline Citation for CPU Time Equation

**Location:** Section 6.5.2 (line 798)

**Current text:**
> "The CPU time equation's separation of instruction count..."

**Issue:** R2 added Patterson & Hennessy to References section, but inline citations throughout paper still say "the CPU time equation" without (Patterson & Hennessy, 2017) parenthetical.

**Reviewer suggestion:**
> "The CPU time equation (Patterson & Hennessy, 2017) separates instruction count..."

**Alternative:** Keep first mention with full citation, subsequent mentions use "the CPU time equation" alone.

**Human decision needed:**
- ACCEPT to add inline citations (improves citability)
- PARTIAL: Add inline citation on first use only (Section 1, line 26)
- REJECT if References section citation is sufficient

**Priority:** MEDIUM (academic citation completeness)

---

### MINOR-R2-06: Table 1 Caption Clarity

**Location:** Section 5.1, Table 1 caption (line 471)

**Current text:**
> "Note: All values are from proof-of-concept synthetic validation; real infrastructure validation pending."

**Reviewer suggestion:**
> "Note: All values from proof-of-concept using synthetic measurements (random noise models; real hardware validation pending). Actual implementation with CodeLlama-7B + perf is immediate next work."

**Issue:** "Synthetic validation" could be clearer about what "synthetic" means (simulated noise models vs synthetic test cases).

**Human decision needed:**
- ACCEPT to clarify "synthetic" = random number generation
- REJECT if current phrasing is clear enough
- MODIFY: Add Appendix with full PoC methodology details instead

**Priority:** LOW (clarity improvement)

---

### MINOR-R2-07: Repetitive Phrasing in New Limitation

**Location:** Section 6.3.5 (new limitation subsection added in R2)

**Current text (3 uses of "domain-specific validation"):**
1. "CV ≤5% threshold... has not been empirically validated for code generation reinforcement learning specifically."
2. "...importing this threshold is a principled starting point. In the absence of code generation-specific calibration studies..."
3. "...we acknowledge the threshold as provisional and encourage domain-specific validation in future work."

**Reviewer suggestion:** Vary phrasing to reduce repetition:
- "task-specific calibration"
- "empirical threshold testing for code generation RL"
- "code generation domain validation"

**Human decision needed:**
- ACCEPT to improve readability (reduce repetition)
- REJECT if repetition emphasizes key limitation
- MODIFY: Keep 2 uses, vary the third

**Priority:** LOW (stylistic preference)

---

## R2 Human Reviewer Action Items

1. **Verify rounding policy** — Is 2-decimal precision standard (1.39%) or should Table 1 show more digits (1.386%)?
2. **Update code comments** — Should h-e1/main.py align with paper (remove COFFE references)?
3. **Fix typo in line 752** — Remove duplicate "not hardware-dependent"
4. **Decide inline citation policy** — Add (Patterson & Hennessy, 2017) throughout or only in References?
5. **Make final accept/reject decisions** for each R2 MINOR issue

---

## Notes (R2 Additions)

- R2 review confirmed NO FABRICATED NUMBERS (all values trace to results.json)
- Mathematical validity checks PASSED (CV margins, Cohen's d calculations, sample size arithmetic all correct)
- Statistical implementation VERIFIED CORRECT (CV formula, pooled std dev, Spearman ρ computation)
- R2 issues are presentation/precision improvements only
- All MAJOR issues from R2 addressed in main paper revision

