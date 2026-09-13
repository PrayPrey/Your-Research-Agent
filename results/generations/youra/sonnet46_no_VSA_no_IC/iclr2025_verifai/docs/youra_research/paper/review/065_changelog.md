# Changelog — Phase 6.5 Adversarial Review

## Round 1 Revisions (2026-08-22)

### FATAL Issues Fixed

- **F1 (venue mismatch / no executed experiments):** Applied Option C — explicit pre-registration framing throughout. Abstract revised to explicitly label this a "Stage 1 infrastructure and pre-registration report." Introduction added a paragraph acknowledging the paper as a complete contribution in the infrastructure-and-preregistration tradition (citing Nosek et al., 2018). Conclusion revised: "What remains is execution" expanded to acknowledge that the pre-registered infrastructure and design are independent scholarly contributions to reproducibility and transparency. Nosek et al. 2018 added to References.

### MAJOR Issues Fixed

- **M1 ("68-84%" rounding error):** Changed "68-84%" to "67-84%" in Section 3.1 opening sentence. Consistent with Table 2 (Section 5.2) which correctly states 67.6% (23/34). The abstract phrasing "minimum information needed" was also updated to "structured information needed" (see M2 below).

- **M2 ("minimal sufficient oracle" overclaim):** Replaced all instances of "minimal sufficient oracle" with "structured, jointly motivated oracle" or "structured oracle" throughout. Specific changes:
  - Abstract: "giving it the minimum information needed" → "giving it the structured information needed"
  - Introduction paragraph 3: "The triple is a minimal sufficient oracle for semantic repair" → "The triple is a structured, jointly motivated oracle for semantic repair"
  - Section 3.1: "minimum information necessary for targeted algorithmic repair" → "structured information necessary for targeted algorithmic repair"
  - Section 6.1: "minimum viable oracle for this failure population" → "structured oracle designed for this failure population"

- **M3 (Clarke 2003 CEGIS citation — unverified, missing from References):** Removed all CEGIS attributions. Specific changes:
  - Introduction paragraph 3: "a CEGIS-style counterexample specifying exactly where..." → "a counterexample that specifies exactly where..."
  - Section 3.2 Step 2: "a CEGIS-style counterexample that specifies exactly..." → "a counterexample that specifies exactly..."
  - No fake citation added. CEGIS concept retained without attribution.

- **M4 ("first explicit verification" novelty overclaim):** Narrowed the novelty claim in three locations:
  - Section 1 contribution bullet: "This is the first explicit verification that EvalPlus semantic failures are reproducibly recoverable from archive" → "We verify and document the data infrastructure for this specific failure set, providing a reusable template for pre-experiment reproducibility checks in LLM repair research"
  - Section 2.4: "first controlled verification of the EvalPlus failure set" → "an explicit verification of the EvalPlus failure set"
  - Section 6.3 (Broader Impact): expanded to explicitly name the infrastructure and pre-registration as independently valuable scholarly contributions

### Issues NOT Fixed (Deferred to Human Review)

- MINOR issues M-minor-1 through M-minor-7: collected in `065_human_review_notes.md`. No auto-fixes applied.
  - M-minor-1: Abstract "4/4 conditions, 5/5 tests" relationship unclear
  - M-minor-2: "convergent motivation" jargon
  - M-minor-3: Table 3.3 "0 API calls" for Condition A unclear
  - M-minor-4: Section 5.5 power analysis derivation not shown
  - M-minor-5: Figure 1 not described inline in Section 4.1
  - M-minor-6: "changes almost nothing" passive voice (partially addressed via rephrasing in Introduction)
  - M-minor-7: Appendix YAML block unconventional for ICML format

---

## Round 2 Revisions (2026-08-22)

### MAJOR Issues Fixed

- R2-M1: Condition B baseline description clarified — no longer called "Self-Refine style"; now "Fixed reprompt prompt (Self-Refine [Madaan et al., 2023] motivation)" in Section 4.2 baselines table. Clarifying sentence added in Section 2.1: "Condition B simplifies Self-Refine's iterative self-feedback to a single fixed reprompt string, isolating re-exposure from self-generated feedback."

### Issues NOT fixed (deferred to human review)

- R2-minor-1, R2-minor-2, R2-minor-3: collected in 065_human_review_notes.md

---

## Final Summary

**Total Revisions Made**: 6 (1 FATAL, 5 MAJOR)  
**Sections Modified**: Abstract, Introduction, Section 2.1, Section 2.4, Section 3.1, Section 3.2, Section 4.2, Section 6.1, Section 6.2, Section 6.3, Section 7, References  
**Word Count Change**: ~4800 → ~4950 (additions from pre-registration framing and clarifications)

**Review Process:**
- Started: 2026-08-22T20:00:00+00:00
- Completed: 2026-08-22T21:00:00+00:00
- Rounds: 2 (R1, R2)
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert
- Convergence: CONVERGED after R2

**Files Generated:**
- `paper/06_paper_final.md` — final reviewed paper
- `paper/review/065_review_summary.md` — consolidated review summary
- `paper/review/065_human_review_notes.md` — MINOR issues for human review
- `paper/review/065_changelog.md` — this file
- `paper/review/065_review_r1.md` — R1 adversary report
- `paper/review/065_review_r2.md` — R2 adversary report
- `paper/06_paper_r1.md` — R1 revised paper
- `paper/06_paper_r2.md` — R2 revised paper

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
