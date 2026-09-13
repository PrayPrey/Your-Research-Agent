# Adversarial Review Changelog

**Paper:** When Reward Granularity Matters  
**Review Started:** 2026-08-31T09:00:00+00:00  
**Rounds Completed:** R1, R2 (in progress)

---

## Round 1 Changes (R1)

### FATAL Issues Fixed

**FATAL-001: max_new_tokens discrepancy (h-e1 used 256, paper reported 512 uniformly)**
- **Change 1:** Abstract — no change (512 refers to h-m1, which is correct)
- **Change 2:** §3.5 Table — added "(h-m1); 256 (h-e1 smoke test)¹" to max_new_tokens row
- **Change 3:** §5.3 — added footnote ¹ clarifying h-e1 smoke test used 256-token configuration
- **Files modified:** 06_paper_r1.md lines ~114, ~181

### MAJOR Issues Fixed

**MAJOR-ENG-001: "Every published paper" scope overclaim**
- **Change 4:** Abstract — "Every published paper" → "All major published papers on reinforcement learning with execution feedback (RLEF) for code LLMs use binary pass/fail reward" with inline citation list added to §1 sentence
- **Change 5:** §1 Introduction first line — "exclusive reward formulation in every published paper" → "reward formulation used by all major published papers" with explicit citations (CodeRL, PPOCoder, RLEF/Gehring, DAPO)
- **Change 6:** §1 Introduction second paragraph — "ubiquitous choice" → "widespread choice"
- **Change 7:** §7 Conclusion — "Every published RLEF paper" → "All major published RLEF papers (CodeRL, PPOCoder, RLEF/Gehring, DAPO)"

**MAJOR-ACC-001: Figure 2 reference misplaced in §5.2**
- **Change 8:** §5.2 — Changed "**Figure 2** (mean_reward.png) shows..." to italicized forward reference: "*(Figure 2, shown in Section 5.4) shows...*"

**MAJOR-ACC-002: Table 2 grad_norm row imprecise**
- **Change 9:** §5.4 Table 2 — "grad_norm (mean, steps 1–136) | ~10⁻³ | ~10⁻³" → "grad_norm diff (ratio−binary, steps 1–136) | mean: +0.000730; 95% CI: [−0.000253, +0.002561] | —"

**MAJOR-SKE-001: §6.3 stale "pending CI" limitation**
- **Change 10:** §6.3 — Removed "Real training gradient norm CI was pending at analysis time. The mechanistic proof served as primary evidence for h-e1; the numerical CI from the 150-step background run is supplementary." Replaced with: "Gradient norm analysis covers steps 1–136 of h-m1. The gradient norm 95% bootstrap CI on (ratio − binary) over steps 1–136 includes zero (mean = +0.000730, CI = [−0.000253, +0.002561]), consistent with both conditions receiving identical zero-reward signals. Longer training or correctly-powered conditions may exhibit different patterns."

---

---

## Round 2 Changes (R2)

R2 adversarial review (Accuracy Checker + Skeptical Expert) found **0 FATAL, 0 MAJOR** issues.

All R1 fixes verified correct. Mathematical derivations (M1–M4) independently verified. Omitted claims (O1–O4) confirmed absent from paper. No baseline fairness issues (no external baselines compared).

2 additional MINOR items added to human review notes (items 7–8).

**No paper text changes in R2.** 06_paper_r2.md = 06_paper_r1.md (unchanged).

---

---

## Final Summary

**Total Revisions Made:** 10 text changes across 8 sections  
**Sections Modified:** Abstract, §1 Introduction, §3.5, §5.2, §5.3, §5.4 Table 2, §6.3, §7 Conclusion  
**Word Count Change:** +~60 words (clarifications, footnote, qualification)  

**Review Process:**
- Started: 2026-08-31T09:00:00+00:00
- Completed: 2026-08-31T10:00:00+00:00
- Rounds: 2 (R1 + R2)
- Personas: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final reviewed paper)
- 065_review_summary.md (consolidated review)
- 065_human_review_notes.md (8 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md (Round 1 adversary report)
- 065_review_r2.md (Round 2 adversary report)
- 065_review_checkpoint.yaml (state tracking)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
