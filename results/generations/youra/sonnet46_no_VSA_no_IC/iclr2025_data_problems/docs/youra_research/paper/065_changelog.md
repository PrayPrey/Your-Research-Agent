# Phase 6.5 Adversarial Review Changelog

**Review Date:** 2026-08-20  
**Rounds:** 2 (R1 + R2)  
**Final status:** CONVERGED — 06_paper_final.md produced

---

## R1 Changes (MAJOR fixes)

### MAJOR-01 — Contribution #1 claim qualified
**File:** `paper/sections/01_introduction.md`, `paper/06_paper_final.md`  
**What changed:** Contribution #1 text changed from "We provide the first direct demonstration..." to "We provide what is, to our knowledge, the first quantitative measurement... (Analysis conducted on domain-representative generated text; η² values represent upper bounds relative to real Pile documents; see Section 6.2 L3.)"  
**Why:** Claiming "first direct demonstration" for results based on synthetic rather than real Pile documents oversells the contribution. Qualifier added without undermining the core finding.

### MAJOR-02 — Baselines section clarified
**File:** `paper/sections/04_experiments.md`, `paper/06_paper_final.md`  
**What changed:** Added explicit note to Section 4.4 (Baselines) stating: "Due to the data limitations documented in Section 5.4 (Books3 zero-exposure, insufficient evaluation cache), none of these baselines could be executed in the current study."  
**Why:** Original text described baselines as if they were used in the study. They are part of the validated-but-unexecuted h-m3 pipeline. Readers would assume execution without this clarification.

### MAJOR-03 — Results 5.1 inline synthetic text caveat added
**File:** `paper/sections/05_results.md`, `paper/06_paper_final.md`  
**What changed:** Added note at top of Section 5.1: "Note on text source: These measurements were conducted on domain-representative generated texts (200 documents per domain) rather than actual Pile documents; η² values are therefore upper bounds."  
**Why:** Without this caveat, readers of the Results section see η²=0.9915 and may assume it was measured on real Pile documents. The caveat is already in Discussion L3 but needs to be at the point of presentation.

---

## R2 Changes (FATAL numerical fix)

### FATAL-01 — Per-domain std table corrected (Section 5.2)
**File:** `paper/sections/05_results.md`, `paper/06_paper.md`, `paper/06_paper_final.md`  
**What changed:** The entire per-domain std table in Section 5.2 was incorrect. All 8 of 10 domain std values were wrong (only Pile-CC and Wikipedia were approximately correct). Table corrected to match h-e1/04_validation.md ground truth values exactly. Domain ordering corrected to descending std.

Specific corrections:
| Domain | Old (wrong) | New (correct) |
|--------|------------|---------------|
| StackExchange | 0.0068 | 0.01496 |
| PubMed Abstracts | 0.0017 | 0.01485 |
| Wikipedia (en) | 0.0086 | 0.00858 |
| USPTO Backgrounds | 0.0163 | 0.00578 |
| PubMed Central | 0.0092 | 0.00288 |
| FreeLaw | 0.0157 | 0.00256 |
| NIH ExPorter | 0.0114 | 0.00130 |
| ArXiv | 0.0121 | 0.00128 |
| DM Mathematics | 0.0187 | 0.00102 |

Also fixed in `06_paper.md` inline text: "Wikipedia (0.0086)" → "Wikipedia (0.00858)"; "Pile-CC (0.0266)" → "Pile-CC (0.02657)".

**Why:** These numbers are central claims in RQ2 results. Wrong values would cause factual errors in the published paper and could mislead readers comparing to Table values.

---

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `paper/06_paper_final.md` | CREATED | Final reviewed paper with all R1+R2 fixes applied |
| `paper/065_review_summary.md` | CREATED | Review outcome summary with numerical verification table |
| `paper/065_changelog.md` | CREATED | This file |
| `paper/065_human_review_notes.md` | CREATED | 4 MINOR issues for human review |
| `paper/sections/01_introduction.md` | MODIFIED | Contribution #1 text qualified |
| `paper/sections/04_experiments.md` | MODIFIED | Baselines section note added |
| `paper/sections/05_results.md` | MODIFIED | Results 5.1 caveat + 5.2 table corrected |
| `paper/06_paper.md` | MODIFIED | Pile-CC and Wikipedia std corrected in Section 5.2 |
