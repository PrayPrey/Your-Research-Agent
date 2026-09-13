# Human Review Notes - Phase 6.5 Round 1

**Paper:** Architectural Fingerprinting of Deep Neural Networks via Weight Statistics  
**Generated:** 2026-04-21  
**Review Round:** R1  
**Purpose:** Minor polish items for human review (NOT fixed by Revision Agent per v2.0 protocol)

---

## Overview

This file contains MINOR issues identified in the adversarial review that require human judgment for polish. These are NOT critical for paper acceptance but improve readability and professionalism.

**Total MINOR Issues:** 9 items (5 from review, 4 additional identified)

**Protocol:** Revision Agent v2.0 does NOT fix MINOR issues automatically. These require human review because they involve style preferences, venue-specific conventions, or judgment calls.

---

## Category 1: Metadata and Placeholders

### 1. Author and Affiliation Placeholders
**Location:** Header (Lines 3-5)  
**Current:**
```
**Authors:** [Author names to be added]  
**Affiliation:** [Institution to be added]  
**Contact:** anonymous@anonymous.org
```

**Issue:** Placeholder text needs completion before submission  
**Action Required:** Fill in actual author names and institutional affiliation  
**Priority:** HIGH (required for submission)  
**Estimated Effort:** 5 minutes

---

### 2. Document Metadata Section
**Location:** End of paper (Lines 420-426 in original, similar in revised)  
**Current:**
```
**Document Metadata:**
- Paper ID: H-WeightDepthClassifier-v1-r1
- Research Folder: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl`
- Generated: 2026-04-21
- Pipeline Phase: Phase 6.5 (Adversarial Review Round 1 Revision)
- Target Venue: ICML 2025
- Word Count: ~9,000 words (approximate, within 8-page ICML limit with figures)
```

**Issue:** Internal pipeline metadata should be removed for external submission  
**Action Required:** Delete entire metadata section before submission to ICML  
**Priority:** MEDIUM (style/professionalism issue)  
**Estimated Effort:** 1 minute

---

### 3. References Section Incomplete
**Location:** Section References (Line 409 in original)  
**Current:**
```
# References

See `06_references.bib` for complete bibliography.
```

**Issue:** ICML submissions typically include formatted references inline or link to .bib file properly  
**Action Required:** 
- Option A: Include formatted references section with full citations
- Option B: Verify `06_references.bib` exists and is properly linked in LaTeX version
**Priority:** HIGH (required for submission)  
**Estimated Effort:** 2 hours (if creating bibliography from scratch)

---

## Category 2: Acknowledgments Section

### 4. Acknowledgments Content Review
**Location:** Acknowledgments section (Lines 412-417)  
**Current:**
```
This work was conducted as part of the YouRA (Your Research Assistant) pipeline Phase 6 paper writing process. Computational resources provided by NVIDIA H100 NVL infrastructure.
```

**Issue:** Mentions "YouRA pipeline" which may or may not be appropriate for venue  
**Questions for Human Review:**
- Should "YouRA pipeline" be mentioned in acknowledgments, or is this too informal?
- Is "Phase 6 paper writing process" appropriate, or should it just say "research process"?
- Is NVIDIA H100 NVL acknowledgment appropriate given paper claims "CPU-only would suffice" (line 178)?

**Action Required:** Revise acknowledgments for venue appropriateness  
**Priority:** LOW (acknowledgments are often venue-specific)  
**Estimated Effort:** 10 minutes

**Suggested Revision:**
```
This work was supported by [grant information if applicable]. Computational resources were provided by NVIDIA H100 NVL infrastructure. We thank [collaborators/reviewers] for valuable feedback.
```

---

## Category 3: Clarity and Style (From Adversarial Review)

### 5. GPU Usage Justification
**Location:** Section 4.5 Computational Cost (Line 178 in original)  
**Current:**
```
Hardware: NVIDIA H100 NVL (95GB), though CPU-only would suffice
```

**Issue:** If CPU-only would suffice, why use H100? Needs clarification  
**Suggested Clarification:**
- "Hardware: NVIDIA H100 NVL (95GB) available for experiments, though CPU-only implementation would suffice for feature extraction and logistic regression"
- Or: "Hardware: Experiments were run on NVIDIA H100 NVL (95GB) for convenience, though the lightweight feature extraction and logistic regression could run on CPU-only systems"

**Action Required:** Add brief explanation for why H100 was used if CPU suffices  
**Priority:** LOW (minor clarity improvement)  
**Estimated Effort:** 2 minutes

---

### 6. Design Rationale Subsection Placement
**Location:** Section 3.4 (Lines 89-98)  
**Current:** Section 3.4 "Design Rationale" in Methodology  
**Review Note:** "Consider moving design rationale to appendix for space"

**Issue:** Design rationale (Why binary? Why multiple features? etc.) is helpful but verbose  
**Trade-off:**
- **Keep in main text:** Improves understanding for readers unfamiliar with experimental design
- **Move to appendix:** Saves space in main paper for results/discussion

**Action Required:** Human judgment call based on page limit constraints  
**Priority:** LOW (space optimization)  
**Estimated Effort:** 5 minutes (if moving to appendix)

---

### 7. Redundant Analogy
**Location:** Section 3.4 (Line 98)  
**Review Note:** "Analogy 'skyscraper vs house' used twice (line 98 and line 84) - consolidate or remove one"

**Issue:** Same building analogy appears in two locations for explaining architectural fingerprinting  
**Current Locations:**
- Methodology Section 3.4 Design Rationale
- (Note: Reviewer may have misidentified second location, appears once in revised version)

**Action Required:** Verify analogy appears only once, or consolidate if repeated  
**Priority:** LOW (minor redundancy)  
**Estimated Effort:** 2 minutes

---

### 8. H-M3 Feature Importance Missing Coefficient
**Location:** Section 5.6 (Line 306 in original)  
**Current:**
```
**H-M3 Feature Importance:**
- BN layer count: (dominant, coefficient not shown but drives classification)
- Gamma mean/std: (weak contribution)
- Beta mean/std: (weak contribution)
```

**Issue:** Says "coefficient not shown" without explaining why  
**Suggested Fix:**
- Option A: Show the actual coefficient value for BN layer count
- Option B: Explain why coefficient is not shown (e.g., "coefficient not shown due to standardization artifacts")

**Action Required:** Either add coefficient or explain omission  
**Priority:** LOW (completeness)  
**Estimated Effort:** 5 minutes (if adding explanation) or 30 minutes (if computing coefficient)

---

### 9. Within-Family Model List Not Explicit
**Location:** Section 5.4 Table (Line 273 in original)  
**Current:**
```
| Family | Models | H-M2 Acc | H-M3 Acc | Threshold | Status |
|--------|--------|----------|----------|-----------|--------|
| **ResNet** | 9 (2 shallow, 7 deep) | **100%** | **100%** | ≥65% | ✓ PASS |
| **DenseNet** | 4 (1 shallow, 3 deep) | **100%** | **100%** | ≥65% | ✓ PASS |
```

**Issue:** Table shows "9 models" and "4 models" but doesn't list which specific models  
**Suggested Addition:** Add footnote or appendix listing:
- ResNet family: ResNet-18, ResNet-34, ResNet-50, ResNet-101, ResNet-152, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d
- DenseNet family: DenseNet-121, DenseNet-161, DenseNet-169, DenseNet-201

**Action Required:** Add model lists to appendix or footnote  
**Priority:** LOW (completeness for reproducibility)  
**Estimated Effort:** 3 minutes

---

## Category 4: LaTeX Conversion Considerations

### 10. Figure Placeholder Format
**Location:** Sections 5.1, 5.3, 5.4 (4 figure placeholders added in revision)  
**Current Format:** Markdown placeholder with bracketed text

**Issue:** When converting to LaTeX for ICML submission, placeholders need proper formatting  
**LaTeX Conversion Needed:**
```latex
\begin{figure}[t]
\centering
% [Placeholder for Figure 1: Weight Distribution Separation]
\caption{Weight norm distributions for shallow vs deep models...}
\label{fig:weight_distribution}
\end{figure}
```

**Action Required:** Convert markdown placeholders to LaTeX figure environments  
**Priority:** MEDIUM (required for LaTeX submission)  
**Estimated Effort:** 20 minutes (4 figures × 5 min each)

---

## Summary Statistics

| Category | Count | Total Effort |
|----------|-------|--------------|
| Metadata/Placeholders | 3 | ~2 hours |
| Acknowledgments | 1 | ~10 minutes |
| Clarity/Style | 5 | ~15 minutes |
| LaTeX Conversion | 1 | ~20 minutes |
| **TOTAL** | **10** | **~2.75 hours** |

---

## Priority Levels

### HIGH Priority (Required for Submission)
1. Author and affiliation placeholders (Item 1)
2. References section completion (Item 3)

### MEDIUM Priority (Professionalism)
1. Document metadata removal (Item 2)
2. Figure placeholder LaTeX conversion (Item 10)

### LOW Priority (Polish)
1. Acknowledgments review (Item 4)
2. GPU usage justification (Item 5)
3. Design rationale placement (Item 6)
4. Redundant analogy check (Item 7)
5. H-M3 coefficient explanation (Item 8)
6. Within-family model list (Item 9)

---

## Recommended Workflow

**Phase 1: Essential (Before Submission)**
1. Fill author/affiliation placeholders → 5 min
2. Complete references section → 2 hours
3. Remove internal metadata → 1 min
4. **Total:** ~2 hours

**Phase 2: Professional Polish (Before Final Submission)**
1. Review acknowledgments for venue appropriateness → 10 min
2. Convert figure placeholders to LaTeX → 20 min
3. Add GPU usage clarification → 2 min
4. **Total:** ~30 min

**Phase 3: Optional Completeness (If Page Budget Allows)**
1. Add H-M3 coefficient or explanation → 5-30 min
2. Add within-family model lists to appendix → 3 min
3. Check analogy redundancy → 2 min
4. Review design rationale placement → 5 min
5. **Total:** ~15-45 min

---

## Notes from Adversarial Review

The adversarial review (065_review_r1.md) identified these as "Human Review Notes" (Part 4, lines 198-210):

> Minor issues for human polish (NOT for Revision Agent)

Original review items:
1. Authors/Affiliation placeholders → **Item 1** above
2. References section incomplete → **Item 3** above
3. Document metadata removal → **Item 2** above
4. Acknowledgments YouRA mention → **Item 4** above
5. GPU H100 vs CPU clarification → **Item 5** above

Additional items identified during revision:
6. Design rationale placement → **Item 6** above
7. Redundant analogy → **Item 7** above
8. H-M3 coefficient missing → **Item 8** above
9. Within-family model list → **Item 9** above
10. LaTeX conversion → **Item 10** above

---

## Revision Agent Protocol Note

**Why Revision Agent Does NOT Fix MINOR Issues:**

Per v2.0 protocol, Revision Agent focuses on FATAL and MAJOR issues that impact:
- Factual accuracy
- Scientific credibility
- Core contribution clarity
- Reviewer acceptance likelihood

MINOR issues (style, typos, formatting, polish) require human judgment because:
- Venue-specific style conventions vary
- Subjective preferences differ
- Trade-offs need author input (e.g., space vs completeness)
- Metadata decisions are context-dependent

**Result:** MAJOR issues fixed in revised paper (06_paper_r1.md), MINOR issues collected here for human review.

---

**Generated By:** Revision Agent v2.0  
**Date:** 2026-04-21  
**Status:** Ready for human review  
**Next Step:** Author reviews and addresses items by priority level
