# Adversarial Review Changelog
**Paper:** When Does Semantic Entropy Win?  
**Phase 6.5 Adversarial Review**  
**Started:** 2026-08-25T22:00:00+00:00

---

## Round 1 Revisions (R1)

### R1-FIX-001 [FATAL → FIXED] — CI Non-Overlap Claim Corrected

**Issue:** ACC-FATAL-001 — Paper claimed "non-overlapping 95% CIs" but SE CI lower bound (0.608) < TE CI upper bound (0.671), meaning CIs overlap by 0.063.

**Changes:**
- Abstract: Added "(95% bootstrap CI on the gap excludes zero; CIs marginally overlap at 0.063)"
- Section 1 Introduction: Changed "non-overlapping 95% CIs" → "bootstrap CI on the gap excludes zero"
- Section 4.3 Gate criteria: Changed "non-overlapping 95% CIs" → "bootstrap CI on gap excludes zero"  
- Section 5.1: Replaced "non-overlapping confidence intervals" with accurate description of marginal overlap + gap CI significance criterion
- Summary table (Section 5.6): Added "(gap CI excludes zero)" annotation

**Sections modified:** Abstract, Introduction, Section 4.3, Section 5.1, Section 5.6

### R1-FIX-002 [MAJOR → FIXED] — Abstract Hook Rewritten

**Issue:** BORED-MAJOR-001 — Abstract opened generically; narrative blueprint specified counterintuitive_finding hook.

**Change:** Prepended three sentences to Abstract opening with the reversal finding: "Semantic entropy outperforms token entropy by 0.155 AUROC on TriviaQA — then loses by 0.066 AUROC on TruthfulQA. Same model, opposite orderings. This reversal is not noise: it exposes a task-structure condition..."

**Sections modified:** Abstract

### R1-FIX-003 [MAJOR → FIXED] — SCG-SE Delta Now Reports Both Raw and Corrected

**Issue:** ACC-MAJOR-001 — Paper reported only corrected delta (0.336) without explaining raw delta (0.092).

**Change:** Section 5.4 now reports: raw delta = 0.092 (3× gate) AND corrected delta = 0.336 (11× gate), with explanation that both exceed the gate. Sign convention explanation clarified.

**Sections modified:** Section 5.4 (RQ4)

### R1-FIX-004 [MAJOR → FIXED] — H-M3 vs H-E1 SE Discrepancy Explained

**Issue:** SKEP-MAJOR-002 — Paper said 0.714 ≈ 0.717 without explaining the 0.003 gap.

**Change:** Section 5.4 note now states: "the 0.003 difference reflects bootstrap sampling variation across overlapping but not identical sample subsets, not a pipeline discrepancy."

**Sections modified:** Section 5.4 note on SE orientation

### R1-FIX-005 [MAJOR → FIXED] — TruthfulQA Subset Justification Added

**Issue:** SKEP-MAJOR-003 — TruthfulQA yes/no subset (17% of full set) not justified.

**Change:** Section 3.1 now includes: "We use the yes/no prefix subset (N=141 of 817 total)... This subset preserves TruthfulQA's core adversarial-misconception structure while allowing automated correctness labeling; evaluation on the full set would require GPT-4 or human judges, which we leave for future work."

**Sections modified:** Section 3.1

---

## Round 2 Revisions (R2)

### R2-FIX-001 [MINOR → FIXED] — Table 3 SCG "(inverted)" Annotation Removed

**Issue:** R2-MINOR-002 — Table 3 SCG row had misleading "(inverted)" tag. Inversion was on SE pipeline (H-M3), not on SCG.

**Change:** Replaced with "SCG | 0.378† |..." and added paragraph footnote: "†TriviaQA SCG AUROC = 0.378 from H-M3 pipeline... SE AUROC from H-M3 is 0.286 uninverted; corrected = 0.714. See Section 5.4."

**Sections modified:** Section 5.3, Table 3

---

## Final Summary

**Total Revisions Made:** 6 (5 FATAL/MAJOR + 1 MINOR fix)  
**Sections Modified:** Abstract, Sections 1, 3.1, 4.3, 5.1, 5.3, 5.4, 5.6  
**Word Count Change:** ~+120 words (justifications and clarifications added)

**Review Process:**
- Started: 2026-08-25T22:00:00+00:00
- Completed: 2026-08-25T22:30:00+00:00
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- `06_paper_r1.md` (R1 revised)
- `06_paper_r2.md` (R2 revised — includes all fixes)
- `06_paper_final.md` (final paper = copy of R2 with review metadata)
- `paper/review/065_review_r1.md` (R1 adversary report)
- `paper/review/065_review_r2.md` (R2 adversary report)
- `paper/review/065_review_summary.md` (consolidated summary)
- `paper/review/065_human_review_notes.md` (6 MINOR issues for human review)
- `paper/review/065_changelog.md` (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
