# Human Review Notes - Round 1 Minor Issues

**Date:** 2026-04-19  
**Source:** 065_review_r1.md (Adversarial Review)  
**Paper Version:** 06_paper_r1.md  
**Status:** Collected for manual review

---

## Overview

This file collects **11 minor issues** identified in the adversarial review that require human judgment. Per v2.0 protocol, the revision agent does NOT auto-fix these—they involve formatting preferences, style choices, and journal-specific requirements best handled by human authors.

**Issue Breakdown:**
- **Formatting:** 5 issues (hypothesis naming, table symbols, abstract length, bold text, list formatting)
- **Style:** 3 issues (redundant phrasing, section overlap, conclusion length)
- **Content:** 2 issues (figure placement, baseline suggestions)
- **Missing:** 1 issue (acknowledgments)

---

## FORMATTING ISSUES (Priority: MEDIUM-HIGH)

### HUMAN_REVIEW_NOTE_008: Hypothesis Naming Inconsistency

**Location:** Throughout paper  
**Issue:** Inconsistent hypothesis naming: "h-e1" (lowercase) vs "H-E1" (uppercase)

**Examples:**
- Line 64: "H-E1" (uppercase)
- Line 76: "h-e1" (lowercase)
- Line 94: "h-m1" (lowercase)
- Section headings use "H-E1, H-M1, H-M2"
- Body text mixes both styles

**Recommendation:** Standardize to uppercase "H-E1, H-M1, H-M2" throughout for formality and consistency with section headings.

**Priority:** MEDIUM - affects professional appearance

---

### HUMAN_REVIEW_NOTE_009: Table 1 Unicode Symbols

**Location:** Section 5.2, Table 1 (Results)  
**Issue:** Table 1 uses Unicode arrows (↔) for annotator pairs. Some journal LaTeX templates may not render Unicode symbols correctly.

**Current:**
```
| Annotator Pair | Cohen's κ | Agreement Rate |
|----------------|-----------|----------------|
| A1 ↔ A2 | 0.700 | 82.3% |
| A1 ↔ A3 | 0.720 | 84.7% |
| A2 ↔ A3 | 0.753 | 83.7% |
```

**Alternative notation:**
```
| Annotator Pair | Cohen's κ | Agreement Rate |
|----------------|-----------|----------------|
| A1-A2 | 0.700 | 82.3% |
| A1-A3 | 0.720 | 84.7% |
| A2-A3 | 0.753 | 83.7% |
```

**Recommendation:** Test with target journal template. If arrows don't render, use dash notation "A1-A2".

**Priority:** LOW - only matters if template breaks

---

### HUMAN_REVIEW_NOTE_010: Abstract Length Exceeds Limit

**Location:** Abstract  
**Issue:** Abstract is ~220 words, likely exceeds ICML 150-word limit (and many other conferences)

**Current length:** 220 words (estimated)  
**Target length:** 150 words (ICML standard)  
**Reduction needed:** ~70 words (32%)

**Suggested trimming strategy:**
1. Sentence 1: Keep (the hook - essential)
2. Sentence 2: Trim "enabling reusable alignment benchmarks without per-model reward training" (implied by context)
3. Sentence 3: Condense findings (1), (2), (3) - remove some CI details, consolidate
4. Sentence 4: Keep (negative result interpretation - essential)
5. Sentence 5: Trim to one phrase (semantic diversity example)
6. Sentence 6: Condense implications to one sentence

**Example condensed structure (150 words):**
> "Despite 160,000+ human judgments showing substantial consistency in identifying safety violations (κ=0.724), standard language model embeddings reveal no geometric structure separating safe from unsafe responses (d=0.034, statistically indistinguishable from random). Analyzing Anthropic's HH-RLHF dataset through systematic validation, we find genuine violations exist (45.6% base-rate) with consistent human detection (κ=0.724), yet pretrained RoBERTa embeddings show no meaningful clustering (93% below target effect size, >0.99 power). This reveals a fundamental disconnect: human-detectable alignment structure does not imply embedding-space structure with standard encoders. Alignment violations are semantically diverse and occupy overlapping embedding regions despite human-detectable differences. Our findings establish that embedding-based alignment evaluation requires safety-specialized representations, while contributing a reusable base-rate validation protocol and systematic hypothesis decomposition that pinpoints failure at representation level."

**Recommendation:** Review target journal word limits and trim accordingly.

**Priority:** HIGH - submission requirement

---

### HUMAN_REVIEW_NOTE_012: Bold Formatting Non-Standard

**Location:** Introduction, Line 14  
**Issue:** "**The key insight:**" with bold formatting is non-standard for academic papers

**Current:**
> "**The key insight:** Human-detectable alignment structure does not imply embedding-space structure."

**Alternatives:**
1. Remove bold: "The key insight: Human-detectable alignment structure..."
2. Rephrase: "Our key insight is that human-detectable alignment structure does not imply embedding-space structure."
3. Integrate into flow: "We demonstrate a key insight—human-detectable alignment structure does not imply embedding-space structure."

**Recommendation:** Choose based on journal style. Most academic venues avoid bold in body text except for emphasis in specific contexts.

**Priority:** LOW - style preference

---

### HUMAN_REVIEW_NOTE_014: Numbered List Embedded in Prose

**Location:** Section 3.4 (Methodology, Embedding Extraction Details)  
**Issue:** Numbered list (1-4 steps) embedded in paragraph prose. Hard to scan quickly.

**Current:**
> "We use the Hugging Face Transformers library [Wolf et al., 2020] with RoBERTa-base checkpoint. For each response text: 1. **Tokenization:** RoBERTa tokenizer with max length 512 tokens (truncation for longer responses) 2. **Encoding:** Forward pass through RoBERTa encoder 3. **Pooling:** Extract CLS token representation (768 dimensions) 4. **Normalization:** L2 normalize embeddings for distance metric consistency"

**Recommended formatting:**
> "We use the Hugging Face Transformers library [Wolf et al., 2020] with RoBERTa-base checkpoint. For each response text:
> 
> 1. **Tokenization:** RoBERTa tokenizer with max length 512 tokens (truncation for longer responses)
> 2. **Encoding:** Forward pass through RoBERTa encoder  
> 3. **Pooling:** Extract CLS token representation (768 dimensions)  
> 4. **Normalization:** L2 normalize embeddings for distance metric consistency"

**Recommendation:** Use proper numbered list formatting for readability.

**Priority:** LOW - readability improvement

---

## STYLE ISSUES (Priority: LOW-MEDIUM)

### HUMAN_REVIEW_NOTE_002: Section 3-4 Overlap

**Location:** Sections 3 (Methodology) and 4 (Experimental Setup)  
**Issue:** Significant content overlap between sections. Both describe H-E1/H-M1/H-M2 protocols, embedding extraction, and metrics.

**Overlap areas:**
- H-E1/H-M1/H-M2 protocols described in both Section 3.2-3.4 and Section 4.2
- Embedding extraction described in both Section 3.4 and Section 4.3
- Metrics listed in both Section 3.5 and Section 4.4

**Potential confusion:** Readers may wonder if they're seeing duplicate information or missing distinctions.

**Recommendation:**
- **Option 1:** Merge sections - "Methodology and Experimental Setup" as single section
- **Option 2:** Clear differentiation - Section 3 = high-level rationale/design principles, Section 4 = implementation details
- **Option 3:** Reorganize - Section 3 = protocol design, Section 4 = datasets and resources only

**Rationale from review:** "Feels repetitive with Section 3. Lots of overlap in protocol descriptions... risks boring readers with repetition."

**Priority:** MEDIUM - affects readability for skimmers

---

### HUMAN_REVIEW_NOTE_005: Limitation Repetition

**Location:** Multiple sections  
**Issue:** L2 limitation (untrained annotators) mentioned 3 times across different sections

**Instances:**
1. Methodology Section 3.2 (H-M1 protocol): "Implementation note" paragraph
2. Results Section 5.2 (H-M1 findings): "Limitation note" paragraph
3. Discussion Section 6.2 (Limitations): "L2: Annotation consistency used untrained data"

**Observation:** This is appropriate transparency, but slightly repetitive. Some readers may feel it's over-emphasized.

**Recommendation:**
- **Option 1:** Keep all three (maximum transparency for different reader paths)
- **Option 2:** Consolidate - detailed disclosure in Methodology, brief mention in Results, skip in Discussion
- **Option 3:** Footnote - first mention with footnote, reference footnote in subsequent mentions

**Priority:** LOW - this is cautious disclosure, not a major issue

---

### HUMAN_REVIEW_NOTE_013: Redundant Phrasing in Introduction

**Location:** Introduction, Line 18  
**Issue:** "Building on this insight, we make the following contributions:" is slightly redundant (the insight was just stated)

**Current:**
> "**The key insight:** Human-detectable alignment structure does not imply embedding-space structure. [...paragraph...] This negative finding is scientifically valuable. [...paragraph...] **Contributions.** Building on this insight, we make the following contributions:"

**Recommendation:** Simplify to "We make the following contributions:" (the connection is already clear from context)

**Priority:** LOW - minor wordiness

---

## CONTENT SUGGESTIONS (Priority: LOW-MEDIUM)

### HUMAN_REVIEW_NOTE_001: Figure 1 Placement Critical

**Location:** Figures (mentioned but not shown in text-only draft)  
**Issue:** Figure 1 (three-hypothesis cascade showing where chain breaks) is critical for engagement but placement not specified

**Review comment:** "Figure 1 (3-hypothesis cascade) is critical for engagement. Visual showing H-E1 PASS → H-M1 PASS → H-M2 FAIL with color coding would make the story instantly graspable. Ensure this is prominent (ideally page 1 or 2 of final paper)."

**Recommendation:**
- Place Figure 1 in Introduction (after hypothesis description) or early in Methodology
- Use color coding: green checkmarks for PASS gates, red X for FAIL gate
- Include visual flow: Dataset → H-E1 (base-rate ✓) → H-M1 (consistency ✓) → H-M2 (clustering ✗)

**Priority:** MEDIUM - improves first impression

---

### HUMAN_REVIEW_NOTE_004: Multi-Encoder Sanity Check

**Location:** Discussion, Baselines  
**Issue:** Could strengthen "pretrained encoders fail" claim with multi-encoder sanity check

**Suggestion:** Compare RoBERTa to other pretrained encoders (BERT-base, GPT-2 embeddings) as sanity check. If all show d~0.03, strengthens "pretrained encoders fail" claim more robustly than single-encoder result.

**Rationale:** Not required (RoBERTa is representative baseline), but would bolster conclusions. Could be appendix material or future work.

**Review comment:** "Not required (you tested RoBERTa as representative), but would bolster conclusions. Consider as appendix material or future work."

**Priority:** LOW - enhancement, not requirement

---

### HUMAN_REVIEW_NOTE_015: Section 5.6 Placement

**Location:** Results Section 5.6 ("The Human-Embedding Disconnect")  
**Issue:** This subsection is excellent but appears AFTER all RQ results. Could be more impactful as overview.

**Current structure:**
- 5.1: RQ1 (H-E1)
- 5.2: RQ2 (H-M1)
- 5.3: RQ3 (H-M2)
- 5.6: The Human-Embedding Disconnect (synthesis)
- 5.7: Summary

**Alternative structure:**
- 5.1: The Human-Embedding Disconnect (punchline overview)
- 5.2: RQ1 (H-E1)
- 5.3: RQ2 (H-M1)
- 5.4: RQ3 (H-M2)
- 5.5: Summary

**Rationale:** Busy readers benefit from seeing the punchline (disconnect) before diving into each hypothesis. Currently structured for suspense (reveal at end), but could prioritize clarity over narrative tension.

**Priority:** LOW - narrative choice, both work

---

## TONE ADJUSTMENTS (Priority: LOW)

### HUMAN_REVIEW_NOTE_006: "Dead End" Needs Qualifier

**Location:** Introduction, Line 16  
**Issue:** "dead end for alignment evaluation" is strong language for single-encoder test

**Current:**
> "This negative finding is scientifically valuable. It establishes that embedding-space clustering approaches using standard pretrained models are a dead end for alignment evaluation, redirecting research toward safety-specialized representations..."

**Observation:** The phrase "dead end" is strong. More accurate: "dead end for alignment evaluation using standard pretrained encoders" (with encoder qualifier).

**Recommended edit:** Add "using standard pretrained encoders" qualifier to avoid overclaiming from single-encoder result.

**Priority:** MEDIUM - precision in claims

---

### HUMAN_REVIEW_NOTE_007: "Reshape Understanding" Overstates

**Location:** Discussion, Line 346  
**Issue:** "reshape understanding of alignment structure" overstates single-encoder finding

**Current:**
> "Our experiments reveal three critical findings that reshape understanding of alignment structure in RLHF data:"

**Observation:** "Reshape understanding" is slightly strong for demonstrating that one pretrained encoder (RoBERTa) doesn't cluster alignment failures.

**Recommended edit:** Soften to "clarify limitations of pretrained encoders for alignment structure detection" or "advance understanding of representation requirements for alignment evaluation"

**Priority:** LOW - tone calibration

---

## MISSING ELEMENTS (Priority: LOW)

### HUMAN_REVIEW_NOTE_018: Acknowledgments Section Missing

**Location:** End of paper  
**Issue:** Standard academic practice to acknowledge funding, compute resources, annotators. Section not present in current draft.

**Suggested acknowledgments:**
1. Human annotators who participated in H-E1/H-M1 studies
2. GPU compute resources (A100 access)
3. Any funding sources supporting the research
4. Dataset providers (Anthropic for HH-RLHF release)
5. Code/infrastructure contributors if applicable

**Recommendation:** Add acknowledgments section before references.

**Priority:** LOW - standard practice, not critical

---

## REFERENCE VERIFICATION (Priority: MEDIUM)

### HUMAN_REVIEW_NOTE_017: Bibliography Completeness Check

**Location:** References section (not shown in text-only draft)  
**Issue:** Ensure all cited works appear in bibliography with correct formatting

**Citations mentioned in paper:**
- Christiano et al., 2017
- Bai et al., 2022
- Ouyang et al., 2022
- Hendrycks et al., 2020
- Lin et al., 2022 (TruthfulQA)
- Liu et al., 2019 (RoBERTa)
- Wolf et al., 2020 (Transformers)
- Hewitt & Manning, 2019
- Petroni et al., 2019
- Bolukbasi et al., 2016
- Ziegler et al., 2019

**Recommendation:** Verify all 11+ citations appear in bibliography with complete metadata (venue, pages, DOI if applicable).

**Priority:** MEDIUM - submission requirement

---

## OPTIONAL ADDITIONS (Priority: LOW)

### HUMAN_REVIEW_NOTE_003: Related Work Enhancement

**Location:** Related Work, Section 2  
**Issue:** Related Work is comprehensive and fair. One optional addition suggested.

**Suggestion:** Consider adding Kadavath et al. 2022 ("Language Models (Mostly) Know What They Know") - relevant to human-model alignment consistency questions, though not directly about preference learning.

**Rationale:** Explores calibration and self-knowledge in LMs, tangentially related to whether models internalize human judgment structure.

**Priority:** LOW - optional enhancement

---

## SUMMARY FOR HUMAN REVIEW

**Total minor issues:** 11

**By priority:**
- **HIGH:** 1 issue (abstract length - submission requirement)
- **MEDIUM:** 4 issues (hypothesis naming, figure placement, tone qualifiers, references)
- **LOW:** 6 issues (table symbols, style choices, optional enhancements)

**Recommended action sequence:**
1. **Immediate:** Trim abstract to 150 words (ICML requirement)
2. **Before submission:** Standardize hypothesis naming (H-E1 throughout), add acknowledgments, verify references
3. **Optional polish:** Consider section restructuring (3-4 overlap), tone adjustments ("dead end", "reshape")
4. **If time permits:** Multi-encoder sanity check (appendix), figure placement optimization

**Time estimate:** 1-2 hours for all minor issues

---

**Notes collected by:** Revision Agent v2.0  
**Date:** 2026-04-19  
**Status:** Ready for human review  
**Next step:** Author decision on which minor issues to address before submission
