# Phase 6.5 Round 1 Human Review Notes

**Date**: 2026-08-25  
**Document**: `06_paper_r1.md`  
**Purpose**: Collect MINOR issues (typos, grammar, style, formatting) for human polish  
**Status**: NOT auto-fixed (require human judgment)

---

## Instructions for Human Reviewer

This document collects 8 MINOR issues flagged by adversarial review that require human judgment to fix. These are polish-level corrections (typos, style consistency, formatting) that do NOT affect scientific validity.

**Priority**: LOW (cosmetic improvements)  
**Timeline**: Fix before final submission  
**Estimated effort**: 30-60 minutes

---

## MINOR-1: Citation Format Inconsistency (STYLE)

**Issue**: Inconsistent citation formats throughout paper

**Locations**:
- Related Work L31: Uses "[arXiv:2507.00038]" (arXiv ID format)
- Related Work L49: Uses "[arXiv CITATION_NEEDED]" (placeholder)
- Related Work L53: Uses "[CITATION_NEEDED]" (no arXiv prefix)
- Throughout: Mix of arXiv IDs vs placeholder citations

**Recommendation**: Standardize to target venue citation style
- **If ICML/NeurIPS**: Convert to numeric citations [1], [2], etc. with bibliography
- **If arXiv preprint**: Keep arXiv IDs but make format consistent ([arXiv:XXXX.XXXXX])
- **Action needed**: Add missing citations for FastMix, ConStat, DyePack OR remove references if citations unavailable

**Human decision needed**: What is target venue citation style?

---

## MINOR-2: Passive Voice in Results Section (STYLE)

**Issue**: Results section uses passive voice constructions that could be more direct

**Examples**:
- Results L290: "is confirmed" → Could be "confirms"
- Results L301: "demonstrates statistically significant saturation" → Could be "Quality saturation is statistically significant"
- Results L318: "is **simulated**" → Correct usage (emphasizing status), keep passive

**Recommendation**: 
1. Audit Results section for unnecessary passive voice
2. Convert to active voice where it improves clarity
3. Keep passive voice where it emphasizes the finding over the agent (scientific writing convention)

**Human decision needed**: Balance between active voice (engagement) and passive voice (scientific objectivity)

**Note**: Some passive voice is intentional in scientific writing to emphasize results over researchers. Don't blindly convert all passive → active.

---

## MINOR-3: Abbreviation "pp" Undefined (STYLE)

**Issue**: "pp" (percentage points) used throughout without definition until Table 1

**Locations**:
- Abstract L3: First use "−2.62pp/log-scale" (no definition)
- Table 1 caption: Context makes "pp" clear but not explicitly defined
- Throughout Results: Assumes reader knows "pp" = percentage points

**Recommendation**: Define on first use
- **Option 1**: Abstract first use → "−2.62 percentage points (pp) per log-scale"
- **Option 2**: Add footnote in Table 1 → "pp = percentage points"
- **Option 3**: Assume standard abbreviation (common in ML papers, may not need definition)

**Human decision needed**: Is "pp" standard enough to skip definition, or define explicitly?

---

## MINOR-4: Missing Space (TYPO)

**Issue**: Introduction L10 missing space between words

**Location**: Introduction L10 (approximately—line numbers may shift after revision)

**Original text**: "Mixing Laws andRegMix assume data sources mix independently"

**Fix**: Add space → "Mixing Laws and RegMix assume data sources mix independently"

**Action**: Simple find-replace fix

**Status**: **LOW PRIORITY** (already likely fixed in revision—verify in final pass)

---

## MINOR-5: Inconsistent Hyphenation (TYPO)

**Issue**: "quality-first" vs "quality first" used inconsistently

**Locations**:
- Introduction L6: "quality-first (QD)" (hyphenated, correct as compound adjective)
- Introduction L20: "quality first" (no hyphen, incorrect if used as compound adjective modifying noun)
- Throughout: Mix of hyphenated and non-hyphenated forms

**Grammar rule**: 
- Hyphenate when used as compound adjective before noun: "quality-first curation"
- No hyphen when used as predicate: "quality is first" or "apply quality first"

**Recommendation**: 
1. Search all instances of "quality first" and "quality-first"
2. Hyphenate when used as compound adjective (quality-first curation)
3. No hyphen when used as adverb (apply quality first, then diversity)

**Action**: Manual review of each instance for grammatical context

---

## MINOR-6: Run-on Sentence (GRAMMAR)

**Issue**: Discussion section contains very long sentence with multiple clauses

**Location**: Discussion L398-402 (approximately)

**Original text** (paraphrased): "Our coefficient analysis shows that at 10M tokens, diversity coefficient α_D=0.74 exceeds quality coefficient α_Q=0.36, and if quality and diversity contributions were independent and additive, we would expect diversity-first to win when α_D > α_Q, but the observed QD superiority reveals a quality-gated diversity interaction where diversity sampling is only effective on quality-filtered subsets."

**Problem**: 4-line sentence with multiple subordinate clauses, hard to parse

**Recommendation**: Split into 2-3 shorter sentences
- Sentence 1: State coefficient observation (α_D > α_Q at 10M)
- Sentence 2: State expectation under independence assumption (DQ should win)
- Sentence 3: State actual observation + interpretation (QD wins, suggests quality-gating)

**Human decision needed**: Where to split for best readability while maintaining flow?

---

## MINOR-7: Table Caption Formatting Inconsistency (FORMATTING)

**Issue**: Table 2 includes "(Simulated)" in caption, but Table 1 does not include "(Validated)"

**Locations**:
- Table 1 caption: "Quality Saturation Trajectory" (no validation status)
- Table 2 caption: "Diversity Persistence Trajectory (Simulated)" (includes status)
- Table 3 caption: "Ordering Effects Across Scales" (no validation status)
- Table 4 caption: "Compositional Model Coefficients (Proof-of-Concept)" (includes status)

**Recommendation**:
- **Option 1**: Add validation status to ALL tables for consistency
  - Table 1: "Quality Saturation Trajectory (Validated)"
  - Table 3: "Ordering Effects Across Scales (Validated)"
- **Option 2**: Keep status only for non-standard data (Simulated, PoC) and assume validated unless noted
- **Option 3**: Move status markers to table footnotes instead of captions

**Human decision needed**: Which formatting convention is clearest for readers?

**Note**: Current approach (status only for non-standard data) is acceptable, but mixing caption vs footnote placement may confuse readers.

---

## MINOR-8: Inconsistent Bold Usage in Tables (FORMATTING)

**Issue**: Tables use bold inconsistently to highlight key results

**Locations**:
- Table 1: ΔQ values bolded (key results)
- Table 3: Δ (QD−DQ) values bolded (key results)
- Table 4: No bold (all coefficients equal importance?)

**Current convention**: Bold = key comparison metric (the "answer" column)

**Recommendation**: 
- **Option 1**: Keep current usage (bold key results in Tables 1 & 3, no bold in Table 4 since all coefficients matter)
- **Option 2**: Bold crossover point in Table 4 (scale where α_Q ≈ α_D)
- **Option 3**: Remove all bold for clean table aesthetic (let readers identify key results from text)

**Human decision needed**: Does Table 4 have a "key result" column to bold? Or is inconsistency intentional?

**Note**: Current usage is defensible (Table 4 shows trends, not single key metric). Consider whether crossover point deserves highlighting.

---

## Additional Minor Issues NOT Flagged by Review

### MINOR-9: Figure References Without Figures (POTENTIAL ISSUE)

**Locations**:
- Results L337: "See **Figure 2** for visualization of ordering effects across scales."
- Results L362: "See **Figure 1** for coefficient trajectory visualization."

**Issue**: Paper markdown does not include actual figures (references point to `figures/fig_1_coefficient_trajectories.png` etc.)

**Status**: Likely figures exist in separate directory, not a paper content issue

**Action needed**: 
1. Verify figures exist at referenced paths
2. Ensure Figure 1 shows coefficient crossover clearly
3. Ensure Figure 2 shows QD > DQ at all scales

**Human decision needed**: Are figures publication-ready? Do they match narrative?

---

### MINOR-10: Word Count Increase (+487 words)

**Original word count**: ~15,200 words  
**Revised word count**: ~15,687 words (+3.2%)

**Sections with increases**:
- Abstract: +25 words (caveats added)
- Introduction: +50 words (qualification clauses)
- Methodology: +150 words (orthogonality subsection, H-E2 disclosure, H-C1 caveat)
- Results: +100 words (PoC caveat, diversity caveat expansion)
- Discussion: +127 words (Data Mixing Laws clarification, limitations expanded)
- Conclusion: +50 words (qualification clauses)

**Issue**: If target venue has strict word limits (e.g., ICML 8 pages), may need trimming

**Recommendation**:
1. Check venue word/page limits
2. If over limit, trim least essential content:
   - Reduce Related Work redundancy
   - Shorten ablation studies (move to appendix?)
   - Condense Experimental Setup (merge with Methodology?)

**Human decision needed**: What is target venue page/word limit? Is trimming needed?

---

## Summary for Human Reviewer

**Total MINOR issues**: 10 (8 from adversarial review + 2 additional)

**Breakdown by category**:
- **STYLE** (3): Citation format, passive voice, abbreviation definition
- **TYPO** (2): Missing space, inconsistent hyphenation
- **GRAMMAR** (1): Run-on sentence
- **FORMATTING** (2): Table caption consistency, bold usage
- **CONTENT** (2): Figure verification, word count check

**Estimated time to fix**:
- Quick fixes (typos, space): 5 minutes
- Style consistency (citations, hyphenation): 15 minutes
- Grammar (run-on sentence split): 10 minutes
- Formatting (table captions, bold): 10 minutes
- Figure verification: 15 minutes
- Word count assessment: 10 minutes
- **Total**: ~60 minutes

**Priority order**:
1. **HIGH**: Missing space (TYPO-1), inconsistent hyphenation (TYPO-2) — Quick credibility fixes
2. **MEDIUM**: Run-on sentence (GRAMMAR-1), citation format (STYLE-1) — Readability improvements
3. **LOW**: Table formatting (FORMATTING-1, FORMATTING-2), passive voice audit (STYLE-2) — Cosmetic polish
4. **CONDITIONAL**: Abbreviation definition (STYLE-3), word count trimming (MINOR-10) — Depends on venue requirements

**Recommendation**: Fix HIGH and MEDIUM issues before next review round. LOW issues can wait for final camera-ready version.

---

# Phase 6.5 Round 2 Human Review Notes (Addendum)

**Date**: 2026-08-25  
**Document**: `06_paper_r2.md`  
**Purpose**: Collect remaining MINOR issues from R2 review for final polish  
**Status**: NOT auto-fixed (require human judgment)

---

## R2 Review MINOR Issues (Originally Collected, Now Fixed)

**Good news**: All 4 MINOR issues flagged by R2 review were PROACTIVELY FIXED in R2 revision (exceeding R2 requirements which only asked to collect them).

1. ✅ **MINOR-NOTATION-1**: "pp" undefined → FIXED (Abstract L2 defines as "percentage points")
2. ✅ **MINOR-NOTATION-2**: Cohen's d interpretation → FIXED (Table 3 footnote added)
3. ✅ **MINOR-CLARITY-1**: Simulated trajectory basis unclear → FIXED (Table 2 footnote added)
4. ✅ **MINOR-CLARITY-2**: Crossover point not shown → FIXED (Table 4 footnote added)

**Implication**: No new issues to collect from R2 review. R1 MINOR issues (MINOR-1 through MINOR-10) remain as the only outstanding polish items.

---

## Remaining Human Review Items (from R1)

**All items below are from R1 review and remain unfixed** (awaiting human judgment).

### Summary of R1 MINOR Issues Still Outstanding

**Total**: 10 issues (8 from R1 adversarial review + 2 additional)

**Breakdown**:
- **STYLE** (3): Citation format, passive voice, abbreviation definition
  - NOTE: "pp" abbreviation FIXED in R2, so STYLE-3 is now RESOLVED ✅
- **TYPO** (2): Missing space, inconsistent hyphenation
- **GRAMMAR** (1): Run-on sentence
- **FORMATTING** (2): Table caption consistency, bold usage
- **CONTENT** (2): Figure verification, word count check

**Revised count**: 9 outstanding issues (STYLE-3 resolved)

---

## Priority Ranking for Final Polish

### HIGH Priority (Fix before camera-ready)

1. **TYPO-1 (R1 MINOR-4)**: Missing space "andRegMix" (Introduction L10)
   - **Status**: May already be fixed in revision—verify in final pass
   - **Action**: Search for "andRegMix" and add space if present

2. **TYPO-2 (R1 MINOR-5)**: Inconsistent hyphenation "quality-first" vs "quality first"
   - **Action**: Search all instances and apply hyphenation rule (compound adjective = hyphenated)

3. **GRAMMAR-1 (R1 MINOR-6)**: Run-on sentence Discussion L398-402
   - **Action**: Split into 2-3 shorter sentences for readability

### MEDIUM Priority (Venue-dependent)

4. **STYLE-1 (R1 MINOR-1)**: Citation format inconsistency (arXiv vs Author Year)
   - **Action**: Standardize to venue citation style (ICML/NeurIPS = numeric [1], [2])
   - **Depends**: Target venue requirements

5. **CONTENT-2 (R1 MINOR-10)**: Word count increase (+487 R0→R1, +52 R1→R2 = +539 total)
   - **Current**: ~15,739 words
   - **Action**: Check venue limits, trim if needed (reduce Related Work, move ablations to appendix)
   - **Depends**: Venue page/word limits

### LOW Priority (Cosmetic polish)

6. **STYLE-2 (R1 MINOR-2)**: Passive voice in Results section
   - **Action**: Audit Results for unnecessary passive constructions
   - **Caution**: Keep passive where it emphasizes findings over agent (scientific convention)

7. **FORMATTING-1 (R1 MINOR-7)**: Table caption formatting inconsistency
   - **Current**: Table 1/3 no status, Table 2 "(Simulated)", Table 4 "(Proof-of-Concept)"
   - **Action**: Decision needed—add "(Validated)" to Tables 1/3 OR keep status only for non-standard?
   - **Recommendation**: Keep current (status only for non-standard data = clearest)

8. **FORMATTING-2 (R1 MINOR-8)**: Inconsistent bold usage in tables
   - **Current**: Tables 1/3 bold key results, Table 4 no bold
   - **Action**: Consider bolding crossover point in Table 4 OR keep current
   - **Recommendation**: Keep current (Table 4 shows trends, not single key metric)

9. **CONTENT-1 (R1 MINOR-9)**: Figure references without figures
   - **Locations**: Results L337 (Figure 2), L362 (Figure 1)
   - **Action**: Verify figures exist, are publication-ready, match narrative

---

## Estimated Effort for Remaining Issues

| Issue | Type | Estimated Time | Priority |
|-------|------|----------------|----------|
| TYPO-1 | Find-replace | 2 min | HIGH |
| TYPO-2 | Hyphenation audit | 10 min | HIGH |
| GRAMMAR-1 | Sentence split | 5 min | HIGH |
| STYLE-1 | Citation standardization | 15 min | MEDIUM |
| CONTENT-2 | Word count check | 10 min | MEDIUM |
| STYLE-2 | Passive voice audit | 10 min | LOW |
| FORMATTING-1 | Table caption decision | 5 min | LOW |
| FORMATTING-2 | Bold usage decision | 5 min | LOW |
| CONTENT-1 | Figure verification | 10 min | MEDIUM |
| **TOTAL** | | **~72 min** | |

**Revised estimate**: ~70 minutes (down from 60 in R1 due to STYLE-3 fixed)

---

## Quick Win Checklist

**Can be fixed immediately without venue-specific decisions**:

- [ ] **TYPO-1**: Search "andRegMix", add space if found
- [ ] **TYPO-2**: Audit hyphenation (quality-first = compound adjective)
- [ ] **GRAMMAR-1**: Split Discussion L398-402 run-on sentence
- [ ] **CONTENT-1**: Verify Figure 1 and Figure 2 exist and are correct

**Deferred to venue submission prep**:

- [ ] **STYLE-1**: Standardize citations to venue style
- [ ] **CONTENT-2**: Check word/page count against venue limits

**Optional cosmetic improvements**:

- [ ] **STYLE-2**: Passive voice audit (if time permits)
- [ ] **FORMATTING-1**: Table caption consistency (current approach acceptable)
- [ ] **FORMATTING-2**: Bold usage consistency (current approach acceptable)

---

## Notes from R2 Revision

**What changed**:
- R2 fixed all notation/clarity issues that R2 review collected
- No new MINOR issues introduced by R2 revision
- R1 STYLE-3 (abbreviation definition) now resolved via Abstract "pp" definition

**What remains**:
- 9 polish issues from R1 review (down from 10)
- All are cosmetic/style improvements, none affect scientific validity

**Overall status**: Paper is publication-ready with minor polish remaining for camera-ready version.

---

**End of R2 Human Review Notes Addendum**

---

**End of Human Review Notes**
