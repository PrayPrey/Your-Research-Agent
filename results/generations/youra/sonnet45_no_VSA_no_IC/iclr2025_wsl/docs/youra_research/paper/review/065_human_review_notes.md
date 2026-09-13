# Human Review Notes - Phase 6.5 Round 1

**Generated:** 2026-08-20  
**Revision Round:** Round 1 (Post-Adversarial Review)  
**Count:** 11 minor issues  
**Status:** NOT FIXED by Revision Agent (requires human author final polish)

---

## Purpose

This document collects MINOR issues identified by Adversary Agent v2 that were NOT addressed by the automated Revision Agent. These issues require human judgment for final manuscript polish before submission. All FATAL and MAJOR issues have been addressed in the revised paper (06_paper_r1.md) — see 065_changelog_r1.md for details.

---

## Typos

*None identified.*

---

## Grammar

### GRAMMAR-001: Subject-verb agreement

**Location:** Original line 124 (Section 3.1)  
**Issue:** "Models trained on same task cluster tightly regardless of architecture" — missing verb conjugation ("cluster" should be "clusters" for singular subject "model" or sentence needs restructuring for plural)  
**Current Text:** "Task-based clustering: Models trained on the same task cluster tightly regardless of architecture"  
**Suggested Fix:** "Task-based clustering: Models trained on the same task cluster together tightly regardless of architecture" OR "Task-based clustering: Same-task models cluster tightly regardless of architecture"  
**Priority:** Low (meaning clear, but grammatically imprecise)

---

## Style

### STYLE-001: Acronyms not spelled out in abstract

**Location:** Abstract line 3  
**Issue:** "NFN, UNF, task arithmetic" — acronyms used without expansion on first use, even in abstract. ICML style guide recommends spelling out on first use.  
**Current Text:** "Existing weight space learning methods (NFN, UNF, task arithmetic) demonstrate..."  
**Suggested Fix:** "Existing weight space learning methods (Neural Functional Networks, Universal Neural Functionals, task arithmetic) demonstrate..." OR move acronym introduction to Introduction Section 1 and use descriptive phrase in abstract ("existing equivariant architectures and model editing methods")  
**Priority:** Low (common in ML abstracts to use acronyms without expansion for space constraints, but journal-dependent)

### STYLE-002: Informal limitation header

**Location:** Section 6.3.1 L1 header  
**Issue:** "L1: Mock Dataset (CRITICAL — Blocks Publication)" — informal tone with em-dash and "Blocks Publication" warning, inconsistent with academic style  
**Current Text:** "**L1: Synthetic Dataset (CRITICAL — Blocks Publication)**"  
**Suggested Fix:** "**L1: Synthetic Dataset (Critical Limitation)**" with severity discussion in body text rather than header  
**Priority:** Low (tone slightly informal but common in technical reports; adjust for target venue norms)

### STYLE-003: Passive constructions reduce clarity

**Location:** Various (7 instances)  
**Issue:** Passive voice reduces readability in methodology descriptions  
**Examples:**  
- Section 3.2.1: "NFN layers are implemented via..." → "We implement NFN layers via..."
- Section 4.1.1: "Metadata is extracted from state_dicts" → "We extract metadata from state_dicts"
- Section 5.3: "Reconstruction loss is decreased" → "Reconstruction loss decreased"  
**Suggested Fix:** Replace passive constructions with active voice where agent is known  
**Priority:** Low (passive voice common in methods sections, but active improves clarity)

### STYLE-004: Abbreviate "proof-of-concept" after first use

**Location:** Throughout document (83 instances)  
**Issue:** "proof-of-concept" spelled out fully every time, adds word count without clarity gain  
**Suggested Fix:** Introduce abbreviation in abstract: "proof-of-concept (PoC)" then use "PoC" consistently  
**Impact:** Saves ~300 words (83 instances × ~3.6 words savings each)  
**Priority:** Low (minor conciseness improvement, useful if approaching page limit)

### STYLE-005: Marketing language in conclusion

**Location:** Original Section 7.5 closing (REMOVED in revision)  
**Issue:** "The future of model zoo curation is weight-based, not metadata-based." — marketing tone, not scientific conclusion  
**Status:** **FIXED** — Removed in 06_paper_r1.md revision  
**No action needed.**

---

## Clarity

### CLARITY-001: Missing citation for metadata corruption claim

**Location:** Abstract line 1, Introduction line 11  
**Issue:** "30-40% of checkpoints have corrupted task labels" — specific statistic without citation  
**Current Text:** "yet 30-40% have corrupted metadata... [citation needed: HF data quality study]"  
**Suggested Fix:**  
- **Option A:** Cite source if available (e.g., "Hugging Face Data Quality Report 2025" or empirical study)  
- **Option B:** Soften to "many checkpoints have corrupted metadata" if no source exists  
- **Option C:** Conduct small-scale audit (sample 100 Hugging Face models, manually verify metadata) and cite as "internal audit"  
**Priority:** Medium (quantitative claim in abstract requires support for Tier 1 venues)

### CLARITY-002: Jargon in introduction

**Location:** Introduction line 17  
**Issue:** "equivariance vs expressivity" — technical jargon without plain-English translation for non-specialist readers  
**Current Text:** "This limitation reflects a fundamental tension in weight space learning: **equivariance vs expressivity**."  
**Suggested Fix:** "This limitation reflects a fundamental tension: **preserving local symmetries (equivariance) vs enabling global generalization (expressivity)**."  
**Priority:** Low (jargon acceptable for technical ML audience, but plain-English version improves accessibility)

### CLARITY-003: Speculative extrapolation without evidence

**Location:** Section 6.2.3, original line 888 (Discussion)  
**Issue:** "Extrapolating: 200 epochs → reconstruction loss ~0.10-0.20" — linear extrapolation assumption unsupported  
**Current Text:** "Full 200-epoch training expected to reach 0.10-0.20 reconstruction loss, improving accuracy."  
**Suggested Fix:** Add uncertainty qualifier: "Full 200-epoch training may improve reconstruction loss to 0.10-0.20 (assuming continued linear descent, though loss plateaus possible)"  
**Priority:** Low (speculation is hedged with "expected" but could be more explicit about uncertainty)

### CLARITY-004: Section length balance

**Location:** Section 6 (Discussion)  
**Issue:** Discussion is 35% of total paper length (7,400 words of 21,070 total), potentially unbalanced  
**Analysis:**  
- Section 6.1 (Mechanism Validation): 1,850 words  
- Section 6.2 (Unexpected Findings): 2,100 words  
- Section 6.3 (Limitations): 1,750 words  
- Section 6.4 (Future Work): 1,700 words  
**Suggested Fix:**  
- **Option A:** Split Section 6 into separate sections (e.g., "6. Mechanism Validation", "7. Limitations and Future Work", "8. Conclusion")  
- **Option B:** Move Section 6.4 (Future Work) to appendix or supplementary material  
- **Option C:** Condense Section 6.2 competing explanations (currently 2,100 words for 3 findings, could trim to 1,200 words by removing redundant evidence)  
**Priority:** Low (thorough discussion valuable for PoC paper, but some venues have discussion length norms)

---

## Missing Content

### MISSING-001: Figure 1 not embedded

**Location:** Section 5.1 line 573  
**Issue:** "Figure 1 visualizes the coverage matrix as a heatmap" — reference present but image not embedded  
**Current Text:** "Figure 1 visualizes the coverage matrix as a heatmap (model counts per architecture-task cell, color-coded: red <30 models, yellow 30-99, green ≥100)."  
**File Reference:** Validation file h-e1 line 195 mentions "coverage_heatmap.png (194KB)" exists  
**Required Action:**  
1. Locate coverage_heatmap.png in validation artifacts  
2. Embed in Section 5.1 (after Table 1) using LaTeX figure environment or Markdown image syntax  
3. Verify caption matches content (color scheme: red <30, yellow 30-99, green ≥100)  
**Priority:** High (figure referenced in text but missing, breaks manuscript completeness for submission)

### MISSING-002: Figures 2-7 descriptions without images

**Location:** Sections 5.2-5.6  
**Issue:** Text references Figures 2-7 (CKA similarity matrix, training curves, violin plots, per-task breakdown, architecture pair heatmap, confusion matrix) but images not embedded  
**Current References:**  
- Figure 2 (Section 5.2): CKA similarity matrix 50×50 heatmap  
- Figure 3 (Section 5.3): Training curves (4 subplots: total loss, reconstruction, KL, contrastive)  
- Figure 4 (Section 5.4): Violin plots (same-task vs random WCSS distributions)  
- Figure 5 (Section 5.4.3): Per-task WCSS ratio bar chart  
- Figure 6 (Section 5.4.4): Architecture pair WCSS heatmap  
- Figure 7 (Section 5.5): Task classification confusion matrix  
**Required Action:**  
- Generate figures from validation data or locate in artifacts directory  
- Embed all 7 figures in corresponding sections  
- Verify captions accurately describe content  
**Priority:** High (figures essential for results interpretation, missing images prevent review)

---

## Structural

### STRUCTURE-001: Methodology intuition paragraphs could use subheadings

**Location:** Section 3.1, 3.2.2  
**Issue:** Added intuition paragraphs (per MAJOR-ENG-002 fix) improve clarity but lack visual hierarchy — bolded "Intuition:" and "Motivation:" labels inline rather than subheadings  
**Current Format:**  
```markdown
### 3.2.2 Level 2: Permutation-Invariant Hierarchical Pooling

**Motivation:** NFN outputs are architecture-specific...
```  
**Suggested Fix:**  
```markdown
### 3.2.2 Level 2: Permutation-Invariant Hierarchical Pooling

#### Motivation
NFN outputs are architecture-specific...

#### Pooling Operation
For each layer...
```  
**Priority:** Low (formatting preference, current structure readable)

---

## Numerical Precision

### PRECISION-001: Inconsistent rounding for CKA values

**Location:** Abstract, Section 5.2  
**Issue:** CKA same-task reported as 0.82 (abstract) and 0.8184 (Section 5.2 table), inconsistent precision  
**Analysis:**  
- Abstract: "CKA similarity 0.82 for same-task pairs"  
- Section 5.2 Table 2: "Median CKA: **0.8184**"  
**Suggested Fix:**  
- **Option A:** Use 0.82 consistently (2 significant figures) for readability  
- **Option B:** Use 0.82 in abstract (concise), 0.8184 in results table (precise)  
- **Current approach (Option B) is acceptable** — abstract uses rounded values, tables use precise measurements  
**Priority:** Low (no action needed, current approach standard)

---

## Summary

**Total MINOR issues:** 11  
- **Grammar:** 1  
- **Style:** 4 (1 fixed)  
- **Clarity:** 4  
- **Missing Content:** 2 (HIGH priority)  
- **Structural:** 1  
- **Numerical Precision:** 1 (no action needed)

**High Priority (Required for Submission):**  
1. MISSING-001: Embed Figure 1 (coverage heatmap)  
2. MISSING-002: Embed Figures 2-7 (CKA matrix, training curves, WCSS plots, confusion matrix)  
3. CLARITY-001: Cite source for "30-40% corrupted metadata" claim OR soften wording  

**Medium Priority (Improves Quality):**  
- None

**Low Priority (Final Polish):**  
- GRAMMAR-001: Fix "cluster tightly" verb agreement  
- STYLE-001: Spell out acronyms in abstract  
- STYLE-002: Formalize limitation headers  
- STYLE-003: Replace passive voice with active (7 instances)  
- CLARITY-002: Translate "equivariance vs expressivity" jargon  
- CLARITY-003: Add uncertainty to extrapolation claim  

**Recommended Timeline for Human Review:**  
- **High Priority items:** 2-4 hours (locate and embed 7 figures, verify metadata claim citation)  
- **Low Priority items:** 1-2 hours (grammar fixes, style polish)  
- **Total:** 3-6 hours

---

**End of Human Review Notes**
