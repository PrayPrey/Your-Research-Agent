# Human Review Notes - Round 1 Minor Issues

**Date**: 2026-03-18T10:30:00Z
**Source**: Adversarial Review R1 (Part 4: Human Review Notes)
**Status**: FOR HUMAN REVIEW (Not auto-fixed by Revision Agent)

---

## Purpose

These are **MINOR issues** identified by the Adversary Agent that are style, formatting, or minor clarity improvements. Per Revision Agent protocol v2.0, MINOR issues are NOT automatically fixed but collected here for human review during final polish phase.

**Why not auto-fix?** Minor issues are subjective (style preferences, formatting choices, optional clarity tweaks) and risk introducing unnecessary changes or conflicts with venue style guides. Human judgment is better suited for final polish.

---

## MINOR Issues from R1 Review (8 total)

| # | Location | Issue | Type | Suggested Action |
|---|----------|-------|------|------------------|
| 1 | Abstract, line 8 | "96% below threshold" could be clearer | clarity | Consider "achieves only 4% of the 0.60 threshold" for clarity |
| 2 | Introduction, line 15 | NMI precision inconsistent (0.02 in Abstract, 0.0229 in Introduction) | consistency | Use consistent precision: 0.02 in Abstract, 0.023 elsewhere, or 0.0229 for precision |
| 3 | Results, Table | "Mean" row in κ table could be emphasized | formatting | Bold or highlight mean row for visual emphasis |
| 4 | Methodology, line 7 | "Stage 1 (H-E1)" - spell out hypothesis naming on first use | clarity | Add: "Hypothesis 1 - Existence validation (H-E1)" on first mention |
| 5 | Discussion, line 23 | "K-means cluster sizes (287:13) nearly match class balance (275:25)" - good insight, could be more prominent | emphasis | Consider making this a highlighted insight box or moving to Results |
| 6 | Conclusion, line 19 | "How few? That is the next question" - strong closing but risks being too informal | style | Consider more formal alternative: "Determining the minimal annotation budget required for reliable cross-repository mapping represents the critical next research direction." |
| 7 | References | Not included in reviewed draft | citation check | Ensure Gebru 2018, Roman 2023 are prominently cited in References section |
| 8 | Section transitions | Could add preview sentences at end of sections | flow | Consider adding 1-sentence transition at end of each section previewing next section for smoother flow |

---

## Issue Details

### Issue 1: Abstract clarity - "96% below threshold"

**Location**: Abstract, line describing NMI shortfall

**Current text** (in R1 revision): "achieves only 4% of the 0.60 threshold"

**Status**: ALREADY ADDRESSED in R1 revision (improved from original "96% below threshold")

**Action**: No further action needed.

---

### Issue 2: NMI precision consistency

**Location**: Multiple sections (Abstract vs. Introduction vs. Results)

**Current practice**:
- Abstract: Rounds to 0.02 for readability
- Introduction: Uses 0.0229 for precision
- Results: Uses 0.0229 ± 0.0031 with full precision

**Adversary suggestion**: Standardize precision across sections

**Human decision needed**:
- **Option A**: Keep current practice (abstract rounds for readability, technical sections use full precision) - common in scientific writing
- **Option B**: Standardize to 0.02 everywhere for consistency
- **Option C**: Standardize to 0.023 as middle ground

**Recommendation**: Keep current practice (Option A). Abstract rounding is standard; technical sections need full precision for reproducibility.

---

### Issue 3: Results table formatting

**Location**: Results section, Inter-Annotator Agreement table

**Current table**:
```markdown
| DTS Section | κ | Agreement Level |
|-------------|---|----------------|
| Motivation | 0.586 | Moderate |
| ...
| **Mean** | **0.645** | **Substantial** |
```

**Adversary suggestion**: Add additional emphasis (bold + highlight)

**Human decision needed**: Check venue style guide for table formatting. Some venues prefer minimal formatting; others allow highlighting.

**Action**: Review ICML style guide during LaTeX conversion phase.

---

### Issue 4: Hypothesis naming clarity

**Location**: Methodology section, first mention of "H-E1"

**Current text**: "Stage 1 (H-E1) validates signal existence..."

**Adversary suggestion**: Spell out "Hypothesis 1 - Existence validation (H-E1)" on first use

**Human decision needed**: Does this improve clarity or add clutter?

**Recommendation**: Add brief expansion on first use: "Stage 1 (Hypothesis 1: Existence validation, H-E1)" then use "H-E1" throughout.

---

### Issue 5: Cluster size insight prominence

**Location**: Discussion section, mechanistic attribution paragraph

**Current text**: "Cluster sizes match class distribution: K-means assigns 287:13 fields (96%:4%), nearly identical to the 275:25 (91.7%:8.3%) ground truth—trivial majority-class assignment."

**Adversary suggestion**: This is a KEY mechanistic insight; consider making it more prominent (highlight box, move to Results)

**Human decision needed**:
- **Option A**: Keep in Discussion (current location makes sense for mechanistic explanation)
- **Option B**: Add to Results section as separate finding
- **Option C**: Create visual figure showing cluster assignments overlaid with ground truth distribution

**Recommendation**: Option C - create simple bar chart comparing cluster sizes to class distribution. This is a strong visual proof of the mechanism.

---

### Issue 6: Conclusion informality

**Location**: Conclusion, final sentence

**Current text**: "The path forward is not 'can we avoid labels?' but 'how few labels suffice?' That is the next question for enabling ecosystem-wide metadata quality assessment at scale."

**Adversary concern**: "That is the next question" may be too informal for some venues

**Human decision needed**: Does the informal tone strengthen engagement or hurt credibility?

**Alternative (more formal)**: "The path forward is not whether labels can be avoided, but rather determining the minimal annotation budget required for reliable cross-repository mapping—a critical research direction for enabling ecosystem-wide metadata quality assessment at scale."

**Recommendation**: Keep current version for engagement, but defer to venue style norms. Some venues (NeurIPS, ICML) tolerate conversational conclusions; others (TACL, journals) prefer formal.

---

### Issue 7: References completeness

**Location**: References section

**Current status**: References section includes placeholder text: "See `06_references.bib` for complete BibTeX entries."

**Action needed**: Verify all citations are included in final BibTeX file, especially:
- Gebru et al. (2018) - Datasheets for Datasets
- Roman et al. (2023) - Open Datasheets
- Reimers & Gurevych (2019) - Sentence-BERT
- Lloyd (1982) - K-means clustering
- Landis & Koch (1977) - Inter-annotator agreement

**Status**: NOT BLOCKING - this is handled during LaTeX conversion, not during content revision.

---

### Issue 8: Section transitions

**Location**: All major section boundaries

**Adversary suggestion**: Add 1-sentence preview at end of each section to improve flow

**Example**:
- End of Introduction: "We begin by positioning our work relative to documentation frameworks, semantic metadata analysis, and clustering methods (Section 2)."
- End of Related Work: "Having established the gap in prior work, we now describe our two-stage validation methodology (Section 3)."

**Human decision needed**: Do transitions improve flow or add redundant text?

**Recommendation**: OPTIONAL. Some readers appreciate explicit signposting; others find it repetitive. Check venue style guide and reviewer feedback from past submissions.

---

## Summary for Human Reviewer

**HIGH PRIORITY** (should address before final submission):
- Issue 5: Create visual figure for cluster size vs. class distribution comparison

**MEDIUM PRIORITY** (venue-dependent):
- Issue 3: Check table formatting against ICML style guide
- Issue 6: Assess conclusion tone against venue norms
- Issue 7: Verify References section completeness during LaTeX conversion

**LOW PRIORITY** (optional improvements):
- Issue 2: Consider NMI precision standardization (current practice is acceptable)
- Issue 4: Expand hypothesis naming on first use (minor clarity improvement)
- Issue 8: Add section transitions if preferred by venue style

**NO ACTION NEEDED** (already addressed or not applicable):
- Issue 1: Already fixed in R1 revision

---

## Notes

- All MAJOR issues (9 total) were addressed in R1 revision
- These MINOR issues are polish-level improvements
- None affect scientific validity or core claims
- Human judgment better suited for style/formatting decisions
- Review during LaTeX conversion and final copyediting phase
