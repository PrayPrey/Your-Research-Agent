# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.  
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-04-15T04:47:00Z  
**Rounds Completed**: 1

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 2 |
| Formatting | 4 |
| Style | 2 |
| Credibility | 1 |

**Total**: 9 minor issues

---

## Round 1 Issues

### Clarity Issues

**MINOR-CLARITY-001: "pass@k" not defined on first use**
- **Location**: Abstract, line 32
- **Issue**: The term "pass@k" appears without definition in abstract
- **Suggestion**: Either define briefly ("pass@k: probability of solving with k samples") or use more accessible phrasing for abstract
- **Impact**: Minor - readers familiar with code generation will understand, but reduces accessibility

**MINOR-CLARITY-002: "comprehensive assessment" is vague**
- **Location**: Introduction, line 38
- **Issue**: Phrase "comprehensive assessment" is slightly vague without concrete examples
- **Suggestion**: Consider more specific phrasing like "multi-dimensional competency profiles"
- **Impact**: Minimal - meaning is clear from context

---

### Formatting Issues

**MINOR-FORMAT-001: Colon formatting inconsistent**
- **Location**: Methods section, line 122
- **Issue**: "Correctness Features (3):" - colon usage after feature category headers
- **Observation**: Some sections use colons, others don't
- **Suggestion**: Standardize colon usage in feature category headers
- **Impact**: Minimal - cosmetic consistency

**MINOR-FORMAT-002: Table formatting could be clearer**
- **Location**: Results section, ranking tables (lines 217-231)
- **Issue**: Tables lack visual borders, could be harder to read in some formats
- **Suggestion**: Consider adding markdown table borders or converting to figure format
- **Impact**: Minimal - tables are readable, just not optimal

**MINOR-FORMAT-003: Inconsistent decimal places**
- **Location**: Ranking tables (lines 217-231)
- **Issue**: Some scores use 2 decimal places (0.67, 0.57), others would benefit from consistency
- **Observation**: All scores currently use 2 decimal places, actually consistent
- **Suggestion**: Verify all pass@1 scores maintain 2 decimal place precision
- **Impact**: None - already consistent upon review

**MINOR-FORMAT-004: pass@k formatting consistency**
- **Location**: Throughout paper
- **Issue**: Ensure consistent formatting of "pass@1" vs "pass@k" vs "pass@10"
- **Suggestion**: Use consistent formatting (recommend: pass@1, pass@10, pass@100, pass@k)
- **Impact**: Minimal - minor consistency issue

---

### Style Issues

**MINOR-STYLE-001: "Theory A/B/C" labeling informal**
- **Location**: Discussion section, line 377
- **Issue**: Using "Theory A," "Theory B," "Theory C" for competing explanations is clear but slightly informal for ICML
- **Suggestion**: Consider more formal labels like "Hypothesis 1: Unidimensional Competency" or keep as-is for clarity
- **Impact**: Minimal - current approach is actually quite readable and clear
- **Trade-off**: Formality vs. accessibility - current style favors accessibility

**MINOR-STYLE-002: "Empirical Taxonomy" sounds grandiose**
- **Location**: Conclusion section, line 591 (Future work)
- **Issue**: "Empirical Taxonomy of Code Task Space" is slightly inflated language given limited evidence (n=6, 2 benchmarks)
- **Suggestion**: Consider "Dimensional Mapping of Code Evaluation Tasks" or similar
- **Impact**: Minor - this is future work, not a current claim, but could be toned down
- **Note**: Addressed in MAJOR-CRED-002 of adversarial review but downgraded to human review note

---

### Credibility/Style

**MINOR-CRED-001: References section separated**
- **Location**: References line 605
- **Issue**: Review notes references are in separate file - needs integration check
- **Suggestion**: Ensure all citations are properly integrated and formatted
- **Impact**: Requires verification - references must be complete for submission

---

## Notes for Human Reviewer

### What Was Fixed (FATAL/MAJOR)
- All numerical errors corrected (HumanEval rankings, MBPP rankings, feature statistics)
- Sample size prominently mentioned throughout
- Abstract restructured to lead with finding
- Introduction hook improved

### What Remains (MINOR)
These 9 issues are cosmetic or stylistic improvements that don't affect scientific validity:
- 2 clarity improvements (define pass@k, specify "comprehensive")
- 4 formatting consistency items (mostly already consistent)
- 2 style choices (Theory A/B/C labeling, future work phrasing)
- 1 integration check (references file)

### Recommendation
The paper is scientifically sound after R1 revisions. These minor issues can be addressed during:
- Final copyediting pass
- LaTeX template conversion (will standardize formatting)
- Reference integration (separate workflow)

**Priority**: LOW - Address during final polish, not blocking for R2 review

---

## Comparison to Review Standards

**From 065_review_r1.md Part 4:**
> "Minor issues for human review (NOT auto-fixed)"

The adversarial reviewer identified these as NOT blocking acceptance but improving quality. All issues align with this assessment - they are truly minor polish items, not substantive concerns.

---

*Note: These issues do not block paper acceptance but improve overall quality. Address during final preparation for submission.*

---

## Round 2 Issues

**Generated**: 2026-04-15T04:50:00Z

### Summary Update

| Category | R1 Count | R2 Count | Total |
|----------|----------|----------|-------|
| Clarity | 2 | 0 | 2 |
| Formatting | 4 | 0 | 4 |
| Style | 2 | 1 | 3 |
| Credibility | 1 | 0 | 1 |
| **TOTAL** | **9** | **1** | **10** |

---

### R2 New Issues

**MINOR-STYLE-R2-001: Abstract readability - long single sentence**
- **Location**: Abstract, full paragraph
- **Issue**: Abstract is currently one very long sentence (multiple clauses connected with semicolons and em-dashes)
- **Suggestion**: Consider splitting into 2-3 sentences for improved readability
- **Impact**: Minor - content is clear, but readability could be improved
- **Note**: R2 review praised the restructured abstract (finding now in sentences 2-3), but noted it could potentially be split for clarity

---

### R2 Verification Notes

**All R1 fixes verified successful:**
1. ✓ HumanEval rankings: All scores and ranks match ground truth exactly
2. ✓ MBPP rankings: All scores and ranks match ground truth exactly
3. ✓ Feature statistics: pass@1 means, SDs, and difference all correct
4. ✓ Sample size prominence: "n=6" appears in abstract, introduction (multiple times), and results with appropriate caveats
5. ✓ Abstract restructuring: Key finding now in sentences 2-3 instead of sentence 6
6. ✓ Introduction hook: Successfully avoids generic "X is routinely done" pattern

**R2 Review Praise Points:**
- Consistent use of "n=6" qualifier throughout - well done
- All model names now include size specifications (-15B, -7B, -2B-Multi)
- Mathematical validity: All statistical claims sound and appropriately qualified
- Limitations section: Transparent and thorough
- Theoretical depth: Three-theory framework shows intellectual honesty
- Negative result framing: Handled constructively, not defensively

---

## Overall Assessment After R2

**Paper Quality**: Publication-ready after both review rounds

**Strengths:**
- Numerical accuracy: 100% match with ground truth
- Scientific rigor: Excellent - negative result handled honestly
- Transparency: All limitations clearly documented
- Theoretical depth: Thoughtful analysis of competing explanations

**Remaining Polish Items (10 total):**
- 2 clarity improvements (define pass@k, specify "comprehensive")
- 4 formatting consistency checks (mostly already consistent)
- 3 style choices (Theory A/B/C labeling, future work phrasing, abstract sentence splitting)
- 1 integration check (references file)

**Recommendation**: Address during final LaTeX conversion and copyediting pass. None of these issues block publication.

---

**Status**: R2 review complete, 1 new minor issue identified, all MAJOR issues resolved
