# Revision Log - Round 1

**Date**: 2026-04-22T12:00:00Z
**Input Paper**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/paper/06_paper.md`
**Review File**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/paper/review/065_review_r1.md`
**Output Paper**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/paper/06_paper_r1.md`

---

## Issues Addressed

### FATAL Issues

None received.

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-ACC-001 | Correlation Matrix Inconsistency | ACCEPT | Corrected Table 1 to show 0.208 in Semantic Entropy × Verbalized Confidence cell (was -0.167) |
| MAJOR-CRED-001 | Tone Overclaiming Relative to Pilot-Scale | ACCEPT | Calibrated language throughout to reflect 100-sample, single-model scope with appropriate hedging |

---

## Detailed Changes by Issue

### MAJOR-ACC-001: Correlation Matrix Inconsistency

**Problem**: Text claimed "maximum observed correlation is 0.208 between semantic entropy and verbalized confidence" but Table 1 showed -0.167 in that cell.

**Root Cause**: Table entry error - the actual correlation from ground truth is 0.208 (positive), not -0.167.

**Fix Applied**:
- **Location**: Section 5.2, Table 1
- **Change**: Updated Semantic Entropy × Verbalized Confidence cell from `-0.167` to `0.208`
- **Verification**: Now matches text narrative and ground truth data (max_correlation_excluding_bug: 0.208)

**Table Before**:
```
| Verbalized Conf | -0.167 | 0.020 | 0.020 | 1.000 |
```

**Table After**:
```
| Verbalized Conf | 0.208 | 0.020 | 0.020 | 1.000 |
```

---

### MAJOR-CRED-001: Tone Overclaiming Relative to Pilot-Scale

**Problem**: Writing tone occasionally inflated significance beyond what pilot-scale (100 samples, single model) experiments support.

**Principle**: Calibrate language to match acknowledged experimental scope while preserving research contribution.

**Fixes Applied**:

#### 1. Introduction, Paragraph 1 - Hypothetical Example
**Location**: Line 17
**Before**: 
```
Consider a production system using self-consistency to detect knowledge gaps: 
it may achieve 0.55 AUROC while semantic entropy on the same task reaches 0.78—
a 13% relative improvement from simply choosing the right method.
```

**After**:
```
In our controlled experiments, semantic entropy achieves 0.78 AUROC on knowledge 
gap detection while the ensemble baseline reaches 0.69—a 13% relative improvement 
from semantic clustering alone, yet we lack understanding of whether such gains 
generalize across contexts.
```

**Rationale**: Replaced hypothetical example (0.55 vs 0.78) with actual experimental findings (0.69 vs 0.78). Added caveat about generalization uncertainty.

---

#### 2. Introduction, Final Paragraph - "Foundation" Language
**Location**: Line 39
**Before**: 
```
This work provides the foundation for that shift.
```

**After**:
```
This work demonstrates the feasibility of that shift.
```

**Rationale**: "Demonstrates feasibility" is more appropriate for pilot-scale work than "provides foundation."

---

#### 3. Introduction, Contributions Section - Actionable Guidance
**Location**: Line 35
**Before**: 
```
**Actionable guidance for practitioners and researchers.** For practitioners 
deploying uncertainty estimation on factual question answering, we provide 
validated evidence that semantic entropy with clustering outperforms simpler 
baselines.
```

**After**:
```
**Initial framework for practitioners and researchers.** For practitioners 
deploying uncertainty estimation on factual question answering in settings 
similar to our experimental setup, we demonstrate that semantic entropy with 
clustering outperforms simpler baselines.
```

**Rationale**: 
- "Initial framework" instead of "actionable guidance" 
- "demonstrate" instead of "provide validated evidence"
- Added scope qualifier "in settings similar to our experimental setup"

---

#### 4. Discussion Section 6.5 - Actionable Insights Header and Content
**Location**: Lines 389-394
**Before**: 
```
For **practitioners** deploying uncertainty estimation:
- Use semantic entropy with clustering for factual QA tasks (13% relative 
  improvement validated)
```

**After**:
```
For **practitioners** deploying uncertainty estimation in settings similar to 
our experimental setup (factual QA with Mistral-scale models):
- Semantic entropy with clustering demonstrates 13% relative improvement in 
  controlled experiments
```

**Rationale**: 
- Added scope qualifier to header
- Removed "validated" language
- Reframed as "demonstrates in controlled experiments"

---

#### 5. Discussion Section 6.5 - Path Forward
**Location**: Line 401
**Before**: 
```
Our mechanistic framework provides the foundation for this shift.
```

**After**:
```
Our mechanistic framework demonstrates the feasibility of this shift.
```

**Rationale**: Consistent with Introduction change - "demonstrates feasibility" vs "provides foundation."

---

#### 6. Conclusion, Opening Paragraph
**Location**: Line 406
**Before**: 
```
Our answer: semantic entropy for factual question answering, with a 13% 
relative improvement over simpler baselines.
```

**After**:
```
Our answer, based on controlled experiments with Mistral-7B on 100-sample 
factual QA tasks: semantic entropy demonstrates 13% relative improvement 
over simpler baselines.
```

**Rationale**: Added experimental scope context to temper the recommendation.

---

#### 7. Conclusion, Second Paragraph - Framework Language
**Location**: Lines 415-416
**Before**: 
```
For practitioners navigating the proliferation of uncertainty methods, our 
work provides validated guidance: semantic entropy with clustering outperforms 
simpler baselines...
```

**After**:
```
For practitioners navigating the proliferation of uncertainty methods, our 
pilot study provides initial evidence: semantic entropy with clustering 
outperforms simpler baselines in controlled settings...
```

**Rationale**: 
- "pilot study provides initial evidence" instead of "work provides validated guidance"
- Added "in controlled settings"

---

#### 8. Conclusion, Final Paragraph
**Location**: Line 418
**Before**: 
```
The mechanistic framework we establish provides a foundation for principled 
uncertainty estimation—essential as language models move into high-stakes 
applications where reliability is not optional but critical.
```

**After**:
```
The mechanistic framework we demonstrate provides an initial foundation for 
principled uncertainty estimation—essential as language models move into 
high-stakes applications where reliability is not optional but critical.
```

**Rationale**: "we demonstrate" + "initial foundation" instead of "we establish" + "foundation."

---

## Issues NOT Addressed

None. All FATAL and MAJOR issues were accepted and fixed.

**MINOR Issues**: 9 human review notes collected in separate file (`065_human_review_notes.md`) for human review during final polish, as per v2.0 protocol.

---

## Sections Modified

### Major Revisions:
- **Section 5.2 (Results - Method Independence)**: Corrected correlation matrix Table 1

### Tone Calibration Throughout:
- **Introduction**: 
  - Paragraph 1: Replaced hypothetical example with actual findings + generalization caveat
  - Final paragraph: "demonstrates feasibility" instead of "provides foundation"
  - Contributions section: Added scope qualifiers and softened language
- **Discussion Section 6.5**: 
  - Added experimental scope qualifiers to practitioner guidance
  - Softened "validated" to "demonstrates in controlled experiments"
  - Changed "framework provides foundation" to "demonstrates feasibility"
- **Conclusion**:
  - Opening: Added experimental scope context
  - Practitioner guidance: "pilot study provides initial evidence" with scope
  - Final paragraph: "we demonstrate" + "initial foundation"

---

## Word Count Changes

| Section | Before | After | Delta | Notes |
|---------|--------|-------|-------|-------|
| Abstract | 151 | 151 | 0 | No changes |
| Introduction | 1,048 | 1,057 | +9 | Added scope qualifiers |
| Related Work | 1,423 | 1,423 | 0 | No changes |
| Methodology | 1,518 | 1,518 | 0 | No changes |
| Experimental Setup | 1,234 | 1,234 | 0 | No changes |
| Results | 1,389 | 1,392 | +3 | Table correction + minor text |
| Discussion | 1,956 | 1,968 | +12 | Added scope qualifiers |
| Conclusion | 682 | 697 | +15 | Added scope context |
| **Total** | **9,401** | **9,440** | **+39** | Minimal increase for clarity |

---

## Verification Against Review Criteria

### MAJOR-ACC-001 (Correlation Matrix):
- ✅ Text now matches table (both show 0.208)
- ✅ Table matches ground truth (0.208 confirmed)
- ✅ Internal consistency restored

### MAJOR-CRED-001 (Tone Calibration):
- ✅ Introduction example uses actual data (0.69 vs 0.78), not hypothetical (0.55 vs 0.78)
- ✅ "Foundation" language replaced with "demonstrates feasibility" / "initial foundation"
- ✅ "Validated" replaced with "demonstrates in controlled experiments"
- ✅ Scope qualifiers added: "100-sample," "Mistral-7B," "in settings similar to experimental setup"
- ✅ Strong recommendations tempered: "pilot study provides initial evidence"
- ✅ Tone now matches acknowledged limitations (L1: pilot scale, L2: single model)

---

## Quality Assurance

### Cross-Reference Check:
- ✅ All table references remain valid
- ✅ All section references remain valid
- ✅ No new contradictions introduced
- ✅ Limitations section (6.2) remains unchanged and still acknowledges pilot scale

### Coherence Check:
- ✅ Introduction tone matches Conclusion tone
- ✅ Contributions claims match Results findings
- ✅ Discussion insights consistent with experimental scope
- ✅ No over-promising beyond 100-sample, single-model evidence

### Preservation Check:
- ✅ Core research findings unchanged (0.78 vs 0.69 AUROC, correlation 0.21, null result on h-m2)
- ✅ Mechanistic framework preserved
- ✅ Honest negative result handling unchanged
- ✅ Writing voice and style consistent

---

## Summary

**Issues Received**: 2 MAJOR (0 FATAL)
**Issues Addressed**: 2 MAJOR accepted and fixed
**Sections Modified**: 4 (Introduction, Results 5.2, Discussion 6.5, Conclusion)
**Word Count Delta**: +39 words (0.4% increase)
**Remaining Concerns**: None - all major issues resolved

**Key Improvements**:
1. Restored data consistency (correlation matrix now matches narrative)
2. Calibrated tone to match pilot-scale scope while preserving contribution
3. Added appropriate hedging and scope qualifiers throughout
4. Maintained research integrity and honest negative result handling

The revised paper addresses both major issues while preserving the paper's core contribution, mechanistic framework, and writing quality.
