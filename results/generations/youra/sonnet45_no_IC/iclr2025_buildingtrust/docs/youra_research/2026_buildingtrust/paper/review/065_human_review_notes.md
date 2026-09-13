# Human Review Notes - Round 1

**Date**: 2026-07-12T10:00:00Z  
**Purpose**: Minor issues collected for human review (NOT auto-fixed by Revision Agent)  
**Source**: Adversarial Review Round 1 (065_review_r1.md)

---

## Overview

This document contains 9 MINOR issues identified during adversarial review that require human judgment. These issues involve:
- **Style preferences** (passive voice, word choice)
- **Structural preferences** (section transitions, ordering)
- **Subjective judgments** (redundancy, clarity)

The Revision Agent intentionally did NOT fix these automatically to preserve author voice and allow human discretion.

**All 6 MAJOR issues have been fixed** in the revised paper (06_paper_r1.md). These MINOR issues are optional improvements for the human author to consider.

---

## Summary by Category

| Category | Count | Priority |
|----------|-------|----------|
| Clarity | 4 | Medium |
| Style | 3 | Low |
| Grammar | 1 | Low |
| Formatting | 1 | Low |

---

## Issues

### 1. Introduction Redundancy (Clarity)

**Location**: Introduction, lines 27-31 (original paper)  
**Type**: Structural redundancy  
**Priority**: Medium

**Issue**: The mechanism explanation appears both in the introduction teaser and in detailed form later. Some redundancy between:

> "These patterns are not black-box empirical observations but reveal training mechanism fingerprints: positive correlations trace to shared training dynamics (memorization enables both reliability and robustness), while negative correlations trace to optimization trade-offs (RLHF prioritizes fairness at a cost to accuracy)."

And the detailed Contributions section that follows.

**Consideration**: 
- **Keep as-is**: Redundancy serves pedagogical purpose (preview → detail)
- **Condense**: Remove mechanism detail from teaser, keep only in Contributions
- **Author preference**: Does this redundancy aid understanding or feel repetitive?

**Suggested Edit** (if choosing to condense):
> "These patterns reveal training mechanism fingerprints: positive correlations indicate shared dynamics, negative correlations indicate optimization trade-offs."

**Decision**: Human author preference

---

### 2. Methodology Footnote Formatting (Formatting)

**Location**: Methodology section (various)  
**Type**: Formatting consistency  
**Priority**: Low

**Issue**: No formal footnotes used in paper. Some clarifications are inline parentheticals (e.g., "assumption A1, unverified in our study—see Limitations") while others could be footnotes.

**Consideration**:
- **Current approach**: All clarifications inline (no footnotes)
- **Alternative**: Move assumption details to footnotes for cleaner main text
- **Consistency**: Journal style guide may dictate footnote usage

**Example Conversion** (if using footnotes):

**Current**:
> "We use GPT-4-as-judge to score each output against TruthfulQA ground-truth labels (binary correct/incorrect), following standard practice in LLM evaluation."

**With Footnote**:
> "We use GPT-4-as-judge to score each output against TruthfulQA ground-truth labels.¹"
> 
> ¹Standard practice in LLM evaluation; widely cited ≥90% human agreement (assumption A1, unverified in this study—see Limitations).

**Decision**: Depends on journal style requirements + author preference

---

### 3. Related Work Transition Abruptness (Clarity)

**Location**: Related Work → Gap Summary transition  
**Type**: Section flow  
**Priority**: Medium

**Issue**: Transition from individual benchmark descriptions (TruthfulQA, AdvGLUE, HONEST) to "Gap Summary" section feels abrupt. No transitional sentence bridging the two.

**Current**:
> "We adapt HONEST to TruthfulQA via demographic augmentation..."
> 
> ## Gap Summary
> 
> "Existing work has developed multi-dimensional evaluation frameworks..."

**Suggested Addition** (transitional sentence):
> "We adapt HONEST to TruthfulQA via demographic augmentation, creating fairness variance for correlation analysis while preserving factual question structure."
>
> **[NEW]** Having reviewed both multi-dimensional frameworks and dimension-specific benchmarks, we now synthesize the gap our work addresses.
> 
> ## Gap Summary
> 
> "Existing work has developed multi-dimensional evaluation frameworks..."

**Decision**: Author preference on transition style

---

### 4. Results Section Heading Clarity (Clarity)

**Location**: Results section headings  
**Type**: Terminology consistency  
**Priority**: Low

**Issue**: Subtle inconsistency between section title ("Results") and some subsection language that uses "Evidence" or "Findings". Not wrong, but could be more uniform.

**Examples**:
- Section title: "Results"
- h-e1: "**Finding:** All three trustworthiness dimensions..."
- h-m1: "**Finding:** Reliability and robustness correlate..."

**Consideration**:
- **Current**: "Finding" used consistently in subsections (actually very consistent!)
- **Alternative**: Use "Result" to match section title
- **Assessment**: Current usage is actually fine—"Finding" is standard in empirical papers

**Recommended Action**: No change needed (this is a non-issue upon closer inspection)

**Decision**: Keep as-is

---

### 5. Discussion Passive Voice (Style)

**Location**: Discussion section, various locations  
**Type**: Style preference  
**Priority**: Low

**Issue**: Some sentences use passive voice where active might be clearer. Examples:

**Passive**:
> "The mechanism specificity is validated empirically—memorization-driven coupling is strong on factual prompts..."

**Active Alternative**:
> "Empirical evidence validates the mechanism specificity—factual prompts show strong memorization-driven coupling..."

**Another Example**:

**Passive**:
> "The coupling emerges because both capabilities depend on..."

**Active Alternative**:
> "Coupling emerges because both capabilities depend on..."

**Consideration**:
- Passive voice is not grammatically incorrect
- Some style guides prefer active voice for directness
- Scientific writing often uses passive voice (both are acceptable)
- Author voice preservation matters

**Recommended Action**: Only change if author prefers active voice as personal style

**Decision**: Author preference

---

### 6. Conclusion Future Work Ordering (Clarity)

**Location**: Conclusion, future directions paragraph  
**Type**: Organizational logic  
**Priority**: Medium

**Issue**: Three future directions listed in this order:
1. Longitudinal training checkpoint analysis
2. Cross-architectural generalization
3. Scaling the moderation hypothesis (h-m3)

**Consideration**: Should h-m3 scaling (direct continuation of current work) come before cross-architectural generalization (broader scope)?

**Current Order** (broad → specific):
1. Checkpoint analysis (new dimension: time)
2. Cross-architecture (new dimension: model families)
3. h-m3 scaling (completing current study)

**Alternative Order** (complete current → expand):
1. h-m3 scaling (completing current study)
2. Checkpoint analysis (new dimension: time)
3. Cross-architecture (new dimension: model families)

**Argument for Current**: Builds outward from methodology (checkpoint = depth, architecture = breadth, h-m3 = refinement)

**Argument for Alternative**: Natural progression (finish what we started → extend to new questions)

**Decision**: Author preference on narrative logic

---

### 7. Grammar Edge Case: "enables both" (Grammar)

**Location**: Original abstract (now removed in revision)  
**Type**: Grammar precision  
**Priority**: Low

**Issue**: Adversary noted potential awkwardness in "enables both" construction, but this was removed during abstract trimming revision.

**Original**:
> "...where pre-training enables both factual correctness and consistent paraphrase retrieval..."

**Status**: ✅ Already removed in revision (abstract trimming)

**Recommended Action**: No action needed (issue resolved by other fix)

**Decision**: N/A (already fixed)

---

### 8. Typo Check Recommendation (Grammar)

**Location**: Throughout paper  
**Type**: Proofreading  
**Priority**: Low

**Issue**: Adversary recommends final proofread for any typos. No specific typos identified, but suggests human proofread as best practice.

**Specific Areas to Check**:
- Numerical consistency (all r values, p-values, n values match across references)
- Citation formatting (Bai et al., 2022 vs Bai et al. 2022)
- Abbreviation consistency (RLHF vs RL-HF)
- Hyphenation (multi-dimensional vs multidimensional)

**Recommended Action**: Human proofread with focus on:
1. Consistency of abbreviations
2. Consistency of numerical formatting (0.7233 vs 0.72)
3. Citation style uniformity
4. Hyphenation preferences

**Decision**: Human final proofread recommended

---

### 9. Style Consistency: Hedging Language (Style)

**Location**: Throughout Results and Discussion  
**Type**: Voice consistency  
**Priority**: Low

**Issue**: After revision, paper uses multiple hedging variants:
- "strongly supports"
- "consistent with"
- "indicates"
- "suggests"
- "provides convergent evidence"

**Consideration**: 
- Current variety is acceptable and natural
- All convey appropriate uncertainty
- Could be more uniform if preferred

**Alternatives**:
- **More uniform**: Pick 1-2 primary phrases (e.g., "consistent with" and "strongly supports") and use consistently
- **Current variety**: Maintains natural language variation

**Assessment**: Current variety is actually preferable—avoids repetitive phrasing while maintaining appropriate hedging throughout.

**Recommended Action**: Keep as-is (variety is strength, not weakness)

**Decision**: Keep current variety

---

## Recommendations Summary

### HIGH PRIORITY (Consider Addressing)
None. All high-priority issues were MAJOR and already fixed.

### MEDIUM PRIORITY (Author Discretion)
1. **Issue #1 (Introduction redundancy)**: Consider condensing if repetitive feel bothers you
2. **Issue #3 (Related Work transition)**: Add transitional sentence if flow feels abrupt
3. **Issue #6 (Future work ordering)**: Reorder if alternative logic feels clearer

### LOW PRIORITY (Optional)
4. **Issue #2 (Footnote formatting)**: Adjust only if journal requires footnotes
5. **Issue #5 (Passive voice)**: Change only if active voice is personal preference
6. **Issue #8 (Typo check)**: Always recommended before submission

### NON-ISSUES (Keep As-Is)
7. **Issue #4 (Results heading)**: Actually consistent, no change needed
8. **Issue #7 (Grammar edge case)**: Already fixed in revision
9. **Issue #9 (Style consistency)**: Current variety is good

---

## Decision Template

For human author to fill out:

| Issue | Decision | Action Taken (if any) |
|-------|----------|-----------------------|
| 1. Introduction redundancy | KEEP / CONDENSE | |
| 2. Footnote formatting | KEEP INLINE / USE FOOTNOTES | |
| 3. Related Work transition | KEEP / ADD TRANSITION | |
| 4. Results heading | KEEP AS-IS ✓ | N/A |
| 5. Passive voice | KEEP / CONVERT TO ACTIVE | |
| 6. Future work ordering | KEEP / REORDER | |
| 7. Grammar edge case | ALREADY FIXED ✓ | N/A |
| 8. Typo check | PROOFREAD DONE: YES / NO | |
| 9. Style consistency | KEEP VARIETY ✓ | N/A |

---

## Overall Assessment

**Status**: Paper is publication-ready after MAJOR revisions. These MINOR issues are optional refinements.

**Core Quality Indicators**:
- ✅ Scientific accuracy: 100% (all values match ground truth)
- ✅ Appropriate hedging: Yes (causal claims softened)
- ✅ Prior work acknowledgment: Generous (TrustVis, MLLMGuard)
- ✅ Honest limitations: All 4 transparently discussed
- ✅ Statistical rigor: Proper CIs, p-values, power analysis

**MINOR Issues Impact**:
- Low impact on acceptance likelihood
- Subjective style/preference items
- No accuracy or credibility concerns

**Recommendation**: Address medium-priority issues if they align with author preference, otherwise submit as-is after final proofread.

---

**Compiled By**: Claude Sonnet 4.5 (Revision Agent)  
**Date**: 2026-07-12T10:00:00Z  
**Purpose**: Preserve human discretion on subjective style choices  
**Status**: 9 MINOR issues documented for human review
