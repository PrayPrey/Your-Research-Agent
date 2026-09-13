# Human Review Notes - Round 1

**Date:** 2026-08-28  
**Source:** Adversary R1 Review (Section: Part 4 - Minor Issues)  
**Status:** Deferred for human copyediting pass  
**Priority:** LOW (polish-level fixes, non-blocking for publication)

---

## Typos

### 1. Company Name
- **Location:** Section 3.4, Line 149 (revised: Section 3.6)
- **Current:** "HuggingFace"
- **Correction:** "Hugging Face" (two words, company standard)
- **Context:** "HuggingFace `datasets` library" → "Hugging Face `datasets` library"

---

## Grammar & Clarity

### 2. Entropy Value Precision
- **Location:** Section 5.2, Line 409 (revised paper)
- **Current:** "Mean entropy: 0.6931 nats"
- **Suggestion:** "Mean entropy: 0.6931 nats (exactly ln(2))"
- **Rationale:** Add clarification for readers unfamiliar with binary maximum entropy constant

### 3. Feasibility Statement Format
- **Location:** Section 6.3, Proxy 1
- **Current:** "Feasibility: High — 2 weeks implementation"
- **Suggestion:** "Feasibility: High (2-week implementation)"
- **Rationale:** Consistent formatting with other sections (parenthetical instead of em-dash)

### 4. Training Steps Ambiguity
- **Location:** Section 3.1, Line 89 (revised paper)
- **Current:** "Extended RLHF (10K-20K steps)"
- **Suggestion:** "Extended RLHF (10K-20K training steps)" or "Extended RLHF (10K-20K gradient updates)"
- **Rationale:** Clarify whether "steps" means training iterations or preference examples (assume training steps, but ambiguous to some readers)

---

## Formatting

### 5. Table 1 Symbols
- **Location:** Section 5.1, Table 1
- **Current:** Checkmark/X symbols (✓/✗) used in Status column
- **Issue:** May not render correctly in all PDF viewers (LaTeX compatibility)
- **Suggestion:** Replace with "PASS" / "FAIL" text or use LaTeX-safe symbols (`\checkmark` / `\times`)
- **Context:** Table 1 (H-E1 Gate Evaluation Summary)

### 6. Figure Paths
- **Location:** Section 5.2, Figure 1 and Figure 2
- **Current:** `![Entropy Scatter Plot](h-e1/figures/entropy_scatter.png)`
- **Issue:** Paths point to `h-e1/figures/` subdirectory
- **Action Required:** Verify figures copied to paper directory or update paths for final submission
- **Files:** `entropy_scatter.png`, `entropy_histogram.png`

---

## Citation Style

### 7. In-Text Citation Inconsistency
- **Issue:** Mixed citation styles throughout paper
- **Examples:**
  - Format A: "(Ouyang et al., 2022)" — parenthetical, end of sentence
  - Format B: "Ouyang et al. (2022)" — narrative, mid-sentence
- **Location:** Sections 2.1, 2.2, 2.4, 6.1
- **Suggestion:** Standardize to one format (recommend Format A for APA style, Format B for ACL style)
- **Scope:** ~20-30 citations throughout paper

---

## References Section

### 8. References List Missing
- **Location:** Section "References" (end of paper)
- **Current:** "See `06_references.bib` for BibTeX citations."
- **Issue:** Final submission should include formatted reference list, not pointer to .bib file
- **Action Required:** Generate formatted references from BibTeX (APA, ACL, or target venue style)
- **Estimated items:** ~15-20 citations (Shannon 1948, Ouyang 2022, Bai 2022, Stiennon 2020, Nakano 2021, Amershi 2019, Skalse 2022, Nguyen 2014, etc.)

---

## Summary for Human Reviewer

**Issue Count:** 8 minor items
- Typos: 1
- Grammar/Clarity: 3
- Formatting: 2
- Citation/References: 2

**Estimated Fix Time:** 30-60 minutes (batch copyediting)

**Priority Order:**
1. **HIGH:** References list (item 8) — required for final submission
2. **MEDIUM:** Citation style consistency (item 7) — affects professionalism
3. **LOW:** Typos, formatting, clarity tweaks (items 1-6) — nice-to-have polish

**Notes:**
- All issues are cosmetic (no impact on scientific content or credibility)
- No changes to quantitative results or claims needed
- Paper is publication-ready after these polish fixes
- Consider using automated citation formatter (e.g., Zotero, Mendeley) for item 7-8

---

**Round 1 Human Review Notes Complete:** 8 items deferred to final copyediting pass. These do not block Round 2 adversarial review or publication decision.
