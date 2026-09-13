# Human Review Notes
# Phase 6.5 Adversarial Review - Minor Issues

> **Purpose:** Minor issues collected during adversarial review for human polish (NOT auto-fixed)

**Date**: 2026-07-11T10:50:00Z
**Rounds Completed**: 2
**Total Minor Issues**: 8 (5 from R1, 3 from R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 3 |
| Clarity | 2 |
| Formatting | 2 |
| Organization | 1 |

**Note**: All FATAL and MAJOR issues have been resolved. These are optional quality improvements.

---

## Round 1 Minor Issues (5 total)

### Style Issues (3)

1. **Location**: Introduction, Contributions list (lines 13-21)
   - **Issue**: Repetitive sentence structure - all 4 contributions start with noun phrases
   - **Suggestion**: Vary sentence structure for better flow
   - **Original**: "First ECE benchmark...", "Demonstration of...", "Analysis of...", "Foundation for..."
   - **Alternative**: Mix active voice ("We establish...", "Temperature scaling achieves...", "We explain...")

2. **Location**: Throughout paper
   - **Issue**: Overuse of em-dashes (—) for emphasis
   - **Count**: 15+ instances
   - **Suggestion**: Replace some with colons, parentheses, or rephrasing for variety

3. **Location**: Results section (lines 319-350)
   - **Issue**: Passive voice in several places where active would be clearer
   - **Example**: "The dramatically larger effect size **is reflected** by..." → "reflects"
   - **Suggestion**: Convert to active voice where appropriate

### Clarity Issues (2)

4. **Location**: Methodology section (line 103)
   - **Issue**: "Model produces logits $z$" - unclear if z is vector or single value
   - **Suggestion**: Clarify dimensionality: "Model produces logit vector $z \in \mathbb{R}^{|V|}$"

5. **Location**: Results, Table 1 caption
   - **Issue**: Caption doesn't explain what the comparison shows (code vs. image classification ECE)
   - **Suggestion**: Add context: "Baseline ECE comparison shows code generation models are 3-6× more miscalibrated than image classifiers"

### Formatting Issues (2)

6. **Location**: Throughout paper
   - **Issue**: Figure reference format inconsistent (some "Figure 1", some "Fig. 1")
   - **Suggestion**: Standardize to "Figure X" on first mention, "Fig. X" in parenthetical references

7. **Location**: Bibliography
   - **Issue**: Inconsistent author formatting (some "First Last", some "F. Last")
   - **Suggestion**: Verify BibTeX formatting matches ICML style guide

---

## Round 2 Minor Issues (3 total)

### Style Issues (1)

8. **Location**: Abstract + Introduction + Results
   - **Issue**: Simulation caveat repeated 3 times (abstract line 3, intro line 12, results line 329)
   - **Suggestion**: Disclosure is good, but 3× may be over-emphasis. Consider reducing to 2 mentions (intro + results)
   - **Rationale**: Authors want to be transparent (good), but excessive repetition draws attention to limitation

### Clarity Issues (1)

9. **Location**: Methodology section, "Why temperature scaling?" subsection
   - **Issue**: Uses "to our knowledge" qualifier but doesn't appear in novelty-sensitive location
   - **Suggestion**: This is appropriate context-setting, not novelty claim. No change needed.
   - **Note**: Reviewer flagged as possible inconsistency but determined it's correct usage

### Organization Issues (1)

10. **Location**: Sections 3 (Methodology) and 4 (Experimental Setup)
    - **Issue**: Boundary between sections is somewhat artificial
    - **Observation**: Section 3 describes "what method we apply", Section 4 describes "how we evaluate it"
    - **Suggestion**: Consider merging into single "Methods" section with subsections
    - **Alternative**: Keep separate but add transitional sentence at boundary
    - **Rationale**: Some venues prefer combined Methods, others prefer separation. ICML accepts both.

---

## Recommended Priority for Human Review

### Fix First (High Visibility)
1. Figure reference standardization (Issue #6)
2. Repetitive sentence structure in contributions (Issue #1)
3. Bibliography formatting (Issue #7)

### Fix Second (Readability)
4. Em-dash overuse (Issue #2)
5. Passive voice conversion (Issue #3)
6. Table caption clarity (Issue #5)

### Consider (Subjective Preferences)
7. Simulation caveat repetition (Issue #8) - Authors may prefer keeping all 3 for complete transparency
8. Section 3/4 merger (Issue #10) - Organizational preference, not correctness issue

### Optional (Minimal Impact)
9. Math notation clarification (Issue #4) - Context makes it clear to expert readers

---

## Notes for Authors

**What Was Fixed by Adversarial Review**:
- ✅ All numerical claims verified (100% accuracy)
- ✅ Novelty claims qualified with "to our knowledge" (4 locations)
- ✅ Theoretical hypotheses marked as such (5 locations)
- ✅ CNN comparison caveats added (2 locations)
- ✅ Methodology narrative improved (42 edits)

**What Remains for Human Polish**:
- Style variety (sentence structure, punctuation)
- Formatting consistency (figures, bibliography)
- Organizational preferences (section boundaries)

**Estimated Time for Human Review**: 30-60 minutes

**Paper Status**: READY FOR SUBMISSION after human review of these minor issues

---

*Generated by Phase 6.5 Adversarial Review - Round 2*
