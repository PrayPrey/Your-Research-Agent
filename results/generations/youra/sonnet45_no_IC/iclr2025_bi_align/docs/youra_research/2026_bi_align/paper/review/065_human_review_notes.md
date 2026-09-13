# Phase 6.5 Human Review Notes - Round 1

**Generated:** 2026-07-13  
**Source:** Adversary Review R1 - MINOR Issues (9 total)  
**Status:** NOT automatically fixed - requires human review during final polish

---

## Overview

These are minor formatting, clarity, and consistency issues identified by the Adversary Agent that DO NOT rise to FATAL/MAJOR severity but should be addressed during final paper polish before submission.

**CRITICAL:** All quantitative claims are ground-truth accurate. Do NOT change any numbers.

---

## MINOR Issues for Human Review

### Formatting Issues (3)

**MINOR-1: Figure numbering inconsistency**
- **Location:** Methods L273, Results Section 5.5
- **Issue:** Methods L273 refers to "Figure 1 (architecture diagram)" but Results section starts numbering at Figure 3. Figures 1-2 are missing from the sequence.
- **Fix:** Either insert Figures 1-2 (architecture diagram, loss curves overview) OR renumber all figures to start from Figure 1 in Results section.

**MINOR-2: Missing figure captions**
- **Location:** Results L278-289
- **Issue:** Results Section 5.5 references Figures 3-7 (gradient distribution, probing curves, gate metrics, CKA heatmap, t-SNE) but no figure files are embedded in markdown.
- **Fix:** Include actual figure files with captions OR add note "Figures available in supplementary materials."

**MINOR-3: Citation format incompleteness**
- **Location:** Related Work L53, multiple sections
- **Issue:** Citations like "Navon et al., 2022" lack full venue/journal information (e.g., "Navon et al., 2022, NeurIPS").
- **Fix:** Add full citation format for all references. Verify citation accuracy against ground truth (e.g., Navon 2022 has 271 citations per GT).

### Clarity Issues (3)

**MINOR-4: Jargon density**
- **Location:** Methods Section 3.2, L77-91
- **Issue:** 8 mathematical symbols (π_θ, π_ref, β, σ, L_DPO, L_attr, α, f_attr) introduced in 15 lines without notation table.
- **Fix:** Add notation table at beginning of Methods section OR simplify mathematical exposition.

**MINOR-5: Acronym overload**
- **Location:** Results L232, multiple sections
- **Issue:** "PoC" used without re-definition in Results section (defined in Methods L123). Readers who skip sections may be confused.
- **Fix:** Either define acronyms per major section OR use "proof-of-concept" consistently instead of "PoC."

**MINOR-6: Passive voice**
- **Location:** Discussion L329
- **Issue:** "All experiments were conducted at approximately 1%..." uses passive voice.
- **Fix:** Make more direct: "We conducted all experiments at approximately 1%..."

### Consistency Issues (3)

**MINOR-7: Percentage formatting inconsistency**
- **Location:** Abstract L5 vs Intro L19
- **Issue:** Abstract uses "54.07%" (two decimals) but Intro uses "54%" (rounded). Inconsistent precision.
- **Fix:** Choose one format - either always show two decimals (54.07%) OR always round to integer (54%) throughout paper.

**MINOR-8: Dataset name inconsistency**
- **Location:** Methods L111 vs Experiments L173
- **Issue:** Methods uses "HH-RLHF" but Experiments uses "Anthropic Helpful-Harmless from RLHF dataset."
- **Fix:** Use "HH-RLHF" consistently OR always use full name "Anthropic Helpful-Harmless from RLHF (HH-RLHF)" on first mention per section.

**MINOR-9: Threshold terminology inconsistency**
- **Location:** Results L232 vs Discussion L331
- **Issue:** Results says "PoC threshold (≥50%)" but Discussion says "feasibility threshold" for same concept.
- **Fix:** Use consistent terminology - either "PoC threshold" OR "feasibility threshold" throughout.

---

## Typos/Grammar

**NONE DETECTED** - The paper is exceptionally well-written grammatically.

---

## What NOT to Change

Per Adversary Review Section 5:

- **Do NOT alter any quantitative claims** - all numbers (78.5°, 54.07%, 65.14%, -5.8%, -21.3%, 100%) are ground-truth accurate
- **Do NOT remove PoC limitations** - they are appropriately disclosed throughout
- **Do NOT strengthen performance claims** - "feasibility demonstration" framing is correct
- **Do NOT hide negative results** - h-m1 FAIL (R²=-1.324) reporting is exemplary transparency

---

## Estimated Fix Time

**Total polish time:** 1 hour
- Formatting fixes: 20 min
- Clarity improvements: 20 min
- Consistency cleanup: 20 min

---

**END OF HUMAN REVIEW NOTES**
