# Human Review Notes - MINOR Issues
**Paper:** Retrieval-Specific Corpus Curation: Empirical Validation and Mechanism Falsification  
**Review Round:** 1  
**Date:** 2026-07-12  
**Purpose:** Polish items for human reviewer (typos, grammar, formatting, minor clarity improvements)

---

## Overview

This document collects MINOR issues identified in Round 1 adversarial review that were NOT fixed by automated revision. These are polish items (typos, grammar, formatting, minor wording) that require human judgment or are not critical for acceptance.

**Total MINOR Issues:** 12  
**Categories:** Accuracy (4), Engagement (3), Credibility (2), Typos/Grammar (3)

---

## MINOR Issues - Accuracy

### ACC-004: Citation Verification Incomplete
**Location:** Section "Paper Statistics" line 401  
**Issue:** Paper reports 81.8% citation verification rate (9/11 verified), but doesn't identify which 2 citations are unverified.

**Recommendation:** Add list of unverified citations:
```markdown
**Citations verified:** 9 of 11 (81.8%)
**Unverified citations:** [Author Year], [Author Year] - [reason: not found in Semantic Scholar / conflicting metadata / etc]
```

---

### ACC-005: Figure Content Not Validated
**Location:** Figures section  
**Issue:** Review cannot verify that Figure 1 actually shows "ratio=0.973" as claimed. Similarly for other figures.

**Recommendation:** 
- Open `figures/fig_1_entity_density.png` and verify ratio value is displayed
- Check that Figure 2-4 match their captions
- If figures are missing or incorrect, regenerate from h-m1, h-m2 validation reports

---

### ACC-006: Corpus Size Inconsistency (PARTIALLY FIXED)
**Location:** Multiple sections  
**Issue:** Methodology Section 3.5 originally said "50K documents" but experiments used 5K/10K. Automated revision changed most instances to "5,000 for proof-of-concept" but may have missed some.

**Recommendation:** Global search for "50K", "50,000", "10K", "10,000", "5K", "5,000" and verify consistency:
- Proof-of-concept experiments: 10,000 total (5,000 baseline + 5,000 retrieval)
- Full-scale recommendation: 50K-1M documents

**Grep command for verification:**
```bash
grep -n "50K\|50,000\|10K\|10,000\|5K\|5,000" 06_paper_r1.md
```

---

### ACC-007: Gate Threshold Notation Inconsistent
**Location:** Multiple sections  
**Issue:** Some sections use "+0.03" (absolute), others "≥3pp" (percentage points), others "+3pp" (mixed).

**Recommendation:** Standardize on one notation:
- **Option A:** Always use "+0.03" (absolute difference)
- **Option B:** Always use "+3pp" or "≥3pp" (percentage points with explicit "pp")
- **Suggested:** Use "+3pp" for readability, with note "All thresholds reported as percentage point differences"

**Instances to check:**
- Abstract: "target ≥0.03"
- Section 3.1: "≥3pp"
- Section 4.1: "≥3pp improvement"
- Section 5.1: "+0.03 gate threshold"

---

## MINOR Issues - Engagement

### ENG-003: Related Work Section Too Long, Lacks Roadmap
**Location:** Section 2 (lines 42-84)  
**Issue:** 44 paragraphs without clear signposting. Reader loses thread between subsections.

**Recommendation:** Add roadmap sentence at start of Section 2:
```markdown
# 2. Related Work

We review three research threads that inform our approach: pretraining corpus filtering methods (Section 2.1), retrieval benchmarks and evaluation protocols (Section 2.2), and quality metrics for text data (Section 2.3). We position our contribution as extending data-centric machine learning from pretraining to the retrieval domain.

## 2.1 Pretraining Corpus Filtering
[existing content...]
```

**Alternative:** Add transition sentences between subsections:
- After 2.1: "While pretraining corpus filtering has matured, retrieval benchmarks have focused on model evaluation rather than corpus quality."
- After 2.2: "Both pretraining filters and retrieval benchmarks rely on quality metrics, which we review next."

---

### ENG-004: Figure References Feel Mechanical
**Location:** Multiple sections  
**Issue:** Phrases like "Figure 4 (query_split_distribution.png) illustrates..." and "Figure 1 shows..." feel like afterthoughts.

**Recommendation:** Integrate figures with motivation:

**Before:**
> "Figure 4 (query_split_distribution.png) illustrates the query classification results."

**After:**
> "As shown in Figure 4, our query classification revealed an extreme imbalance: 99.9% semantic queries versus 0.1% lexical—far from the expected 60/40 split and indicating a corpus sampling issue."

**Instances to improve:**
- Section 4.4: Figure 4 reference
- Section 5.2: Figure 1 reference ("Figure 1 shows the entity density comparison")
- Section 5.3: Figure 2 and Figure 3 references

---

### ENG-005: Methodology Section Front-Loads Formalism
**Location:** Section 3.1 (lines 95-102)  
**Issue:** Opens with formal hypothesis statements ("H-E1 (Existence). Retrieval-quality filtered corpora achieve ≥3pp...") before explaining WHY these hypotheses matter.

**Recommendation:** Add intuition paragraph before formal hypotheses:

```markdown
## 3.1 Research Questions and Experimental Design

Our investigation tests whether retrieval-quality signals diverge from pretraining quality by decomposing the question into three parts: (1) does retrieval-specific filtering improve performance at all? (2) does it work by learning factual density? (3) does density help semantic queries more than lexical queries? This decomposition allows us to separate existence claims from mechanistic claims—we can validate that something works while refuting specific theories of *why* it works.

We formalize these questions as three testable hypotheses:

**H-E1 (Existence).** Retrieval-quality filtered corpora achieve ≥3pp higher Recall@10...
[existing content...]
```

---

## MINOR Issues - Credibility

### CRED-007: "Longer-Term Vision" Language Feels Aspirational
**Location:** Discussion Section 6.5  
**Issue:** Phrase "The longer-term vision: develop a retrieval-quality theory independent of pretraining paradigms" feels aspirational, especially combined with earlier overclaiming issues.

**Recommendation:** Change to:
```markdown
**Before:** "The longer-term vision: develop a retrieval-quality theory independent of pretraining paradigms."

**After:** "A key direction for future work is developing a retrieval-quality theory independent of pretraining paradigms."
```

---

### CRED-008: No Acknowledgment of Concurrent Work
**Location:** Related Work Section 2  
**Issue:** Doesn't mention if anyone else is working on retrieval-specific corpus filtering. Could be oversight.

**Recommendation:** Add caveat in Related Work or Introduction:
```markdown
"To our knowledge, no prior work has systematically tested retrieval-specific corpus filtering using BEIR annotations as training signals. We acknowledge the possibility of concurrent work in this emerging area and focus our review on published methods as of January 2025."
```

---

## MINOR Issues - Typos & Grammar

### TYPO-001: Inconsistent Hyphenation
**Location:** Throughout paper  
**Issue:** "retrieval-quality" (hyphenated) vs "retrieval quality" (no hyphen) used inconsistently.

**Rule:** Hyphenate when used as compound adjective before noun:
- ✓ "retrieval-quality corpus" (compound adjective)
- ✓ "quality of retrieval" (no hyphen, not compound)
- ✓ "retrieval-quality signals"

**Recommendation:** Global search for "retrieval quality" and verify each instance follows hyphenation rule.

**Instances found (examples):**
- Line 32: "retrieval-quality corpora" ✓
- Line 93: "retrieval quality" (check context)
- Line 259: "retrieval-quality corpus" ✓

---

### TYPO-002: Missing Comma After Transition
**Location:** Related Work Section 2.1 (line 54)  
**Issue:** "However these gains came with tradeoffs" missing comma after "However"

**Fix:**
```markdown
**Before:** "However these gains came with tradeoffs:"
**After:** "However, these gains came with tradeoffs:"
```

---

### TYPO-003: Comma Splice in Conclusion
**Location:** Conclusion Section 7 (line 366)  
**Issue:** "The field has focused on pretraining data quality for years, producing frameworks..." is a comma splice (two independent clauses).

**Fix Options:**
```markdown
**Option A (semicolon):** "The field has focused on pretraining data quality for years; producing frameworks like DataComp-LM..."

**Option B (conjunction):** "The field has focused on pretraining data quality for years, and has produced frameworks like DataComp-LM..."

**Option C (period):** "The field has focused on pretraining data quality for years. Frameworks like DataComp-LM..."
```

**Recommendation:** Option A (semicolon) for flow.

---

## MINOR Issues - Clarity & Formatting

### CLARITY-001: Jargon Overload in Abstract
**Location:** Abstract line 17  
**Issue:** "using stratified sampling to enforce independence from educational quality" - WHY stratification matters is unclear without reading methodology.

**Recommendation:** Add brief parenthetical:
```markdown
**Before:** "using stratified sampling to enforce independence from educational quality"

**After:** "using stratified sampling (oversampling documents with low educational quality but high retrieval success) to enforce independence from educational quality"
```

---

### CLARITY-002: Figure Captions Too Brief
**Location:** Figures section (end of paper)  
**Issue:** Captions don't explain what the figure IS (bar chart? line plot? scatter?).

**Current:**
> "**Figure 1:** Entity density comparison showing negative result (ratio=0.973). Located at: `figures/fig_1_entity_density.png`"

**Recommended:**
> "**Figure 1:** Bar chart comparing entity density (entities per 100 tokens) between retrieval-selected corpus (10.38) and perplexity baseline (10.66), showing negative result (ratio=0.973 < 1.15 threshold). Located at: `figures/fig_1_entity_density.png`"

**Apply to all 4 figures.**

---

### FORMAT-001: Section 4.4 Too Long, Needs Subsections
**Location:** Section 4.4 Implementation Details  
**Issue:** 18 paragraphs covering multiple topics without clear structure.

**Recommendation:** Break into subsections:
```markdown
## 4.4 Implementation Details

### 4.4.1 Stratified Classifier Training
[FastText training content]

### 4.4.2 Entity Density Measurement (RQ2)
[spaCy NER content]

### 4.4.3 Query Splitting for Differential Evaluation (RQ3)
[BM25 query split content, including CAVEAT box]

### 4.4.4 Retrieval Model and Computational Setup
[DPR encoders, corpus sizes content]
```

---

### FORMAT-002: Figure Placement Markers Missing
**Location:** Throughout paper  
**Issue:** ICML format expects "[Figure X about here]" markers where figures should be inserted.

**Recommendation:** Add markers after first reference to each figure:
```markdown
[First reference to Figure 1 in Section 5.2]
"Figure 1 shows the entity density comparison."

[Add marker:]
[Figure 1 about here]
```

**Add for all 4 figures.**

---

### FORMAT-003: Conclusion Too Long for ICML Format
**Location:** Section 7 (17 paragraphs)  
**Issue:** ICML conclusions typically 1-2 paragraphs. Current conclusion includes future directions, broader impact, methodological reflections.

**Recommendation:** Move content:
- **Future directions (3 paragraphs)** → Move to Discussion Section 6.5
- **Methodological challenges (2 paragraphs)** → Already in Discussion 6.2
- **Keep in Conclusion:** Main contributions recap (1 para), significance (1 para), closing vision (1 para)

**Trimmed conclusion would be ~400 words (currently ~800).**

---

## Polish Checklist for Human Reviewer

### Accuracy Polish
- [ ] Identify 2 unverified citations (ACC-004)
- [ ] Verify figure content matches captions (ACC-005)
- [ ] Check corpus size consistency (ACC-006)
- [ ] Standardize gate threshold notation (ACC-007)

### Engagement Polish
- [ ] Add roadmap sentence to Related Work (ENG-003)
- [ ] Integrate figure references naturally (ENG-004)
- [ ] Add intuition before formalism in Section 3.1 (ENG-005)

### Credibility Polish
- [ ] Soften "longer-term vision" language (CRED-007)
- [ ] Add concurrent work acknowledgment (CRED-008)

### Typos & Grammar
- [ ] Fix inconsistent hyphenation (TYPO-001)
- [ ] Add comma after "However" (TYPO-002)
- [ ] Fix comma splice in Conclusion (TYPO-003)

### Clarity & Formatting
- [ ] Expand jargon in abstract (CLARITY-001)
- [ ] Enhance figure captions (CLARITY-002)
- [ ] Add subsections to Section 4.4 (FORMAT-001)
- [ ] Add figure placement markers (FORMAT-002)
- [ ] Trim Conclusion section (FORMAT-003)

---

## Estimated Human Review Time

- **Quick pass (typos, grammar only):** 30-45 minutes
- **Full polish (all MINOR issues):** 2-3 hours
- **Priority items (if time limited):** ACC-007 (notation), ENG-003 (roadmap), TYPO-002/003 (grammar), CLARITY-002 (figure captions)

---

## Notes

These MINOR issues do NOT affect the paper's acceptance prospects—all FATAL and MAJOR issues were addressed in automated revision. This is purely polish to improve readability and professionalism.

Human reviewer should use judgment on which issues to fix based on:
1. Time constraints
2. Venue expectations (ICML is competitive, polish matters)
3. Personal writing style preferences

**Do NOT re-introduce overclaiming language** while fixing these polish items—the automated revision was intentionally conservative about scope claims.
