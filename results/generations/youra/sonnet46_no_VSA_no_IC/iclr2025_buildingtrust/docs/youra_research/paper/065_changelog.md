# Phase 6.5 Changelog

**Generated:** 2026-08-20  
**Phase:** 6.5 Adversarial Review  
**Base file:** paper/06_paper.md  
**Final file:** paper/06_paper_final.md

---

## Changes Applied

### 06_paper.md (assembled paper)

| Change | Type | Location |
|---|---|---|
| Table 1 row "OOD" → "OOD Robustness" (label clarification) | FATAL fix | Section 5.5, Table 1 |
| Added rationale sentence for RQ1→RQ3→RQ2 ordering in Section 5.3 | FATAL fix | Section 5.3 |
| Added Gevers & Daelemans caveat "(preprint; independently verified as plausible but not confirmed via library access at submission time)" | MAJOR fix | Section 2.4 |
| Table 1 footnote: added explicit Δρ computation basis — ρ_fairness(N=13)=0.967 used; Meng et al. same-sample assumption met | MAJOR fix | Section 5.5 Table 1 footnote |
| Limitation 2: added paragraph clarifying ρ_fairness re-estimation on N=13 for Fisher z validity | MAJOR fix | Section 6.2 |

### paper/sections/03_methodology.md

| Change | Type | Location |
|---|---|---|
| Table row: "GLUE† / AdvGLUE†" → "In-distribution NLU / OOD robustness (TrustLLM Micro F1)" | FATAL fix | Section 3.2 benchmark pairs table |
| Footnote updated: removed GLUE-X claim as primary source, clarified TrustLLM OOD robustness Micro F1 | FATAL fix | Section 3.2 |

### paper/sections/05_results.md

| Change | Type | Location |
|---|---|---|
| "ρ_AdvGLUE ≈ 0.984" → "ρ_OOD ≈ 0.984" in Section 5.1 prose | FATAL fix | Section 5.1 |
| Table in Section 5.3: "GLUE → AdvGLUE" row → "OOD Robustness" | FATAL fix | Section 5.3 |
| "ρ_AdvGLUE = 0.868" → "ρ_OOD = 0.868" in prose | FATAL fix | Section 5.3 |
| Table 1 footnote: added Δρ computation basis and Meng et al. same-sample clarification | MAJOR fix | Section 5.5 |

### paper/sections/06_discussion.md

| Change | Type | Location |
|---|---|---|
| Limitation 2: expanded to include Fisher z N-mismatch explanation and Δρ=0.967−0.776=0.192 basis | MAJOR fix | Section 6.2 |

---

## Files NOT changed

- paper/sections/00_abstract.md (numbers correct, wording acceptable)
- paper/sections/01_introduction.md (numbers correct)
- paper/sections/02_related_work.md (Gevers caveat added in assembled paper only — section file consistent)
- paper/sections/04_experiments.md (no issues)
- paper/sections/07_conclusion.md (numbers correct)
- paper/06_references.bib (citation tags preserved as-is)

---

## MINOR issues deferred to human review

See `065_human_review_notes.md`.
