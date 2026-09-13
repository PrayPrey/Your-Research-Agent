# Adversarial Review Changelog
# Phase 6.5 — All rounds

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

**Date:** 2026-08-03  
**Issues Addressed:** 1 FATAL, 3 MAJOR

### FATAL-001 — Measurement Count Corrected (1,760 → 1,920)

**Locations changed:**
- Abstract: removed "1,760" (not present in original abstract — count only in intro/conclusion)
- Introduction para 4: "1,760 attention matrix measurements" → "1,920 attention matrix measurements"
- Introduction Contribution 1: "1,760 measurements" → "1,920 measurements"
- Conclusion: "1,760 measurements" → "1,920 measurements"

**Rationale:** Per-N table shows n=1600, 160, 160 → total 1,920. The "1,760" was an arithmetic error with no correspondence to the experimental design (50+5+5=60 samples × 32 layers = 1,920).

### MAJOR-001 — "Conclusive" → "Unambiguous"

**Location:** Introduction, bold paragraph header
- Before: "**The mechanism gate result is conclusive.**"
- After: "**The mechanism gate result is unambiguous.**"

**Rationale:** "Conclusive" implied full causal resolution (approximation definitively not AND bounded-state definitively is the cause). "Unambiguous" correctly describes what was measured: the approximation gate result is clear-cut, without overclaiming the bounded-state attribution.

### MAJOR-002 — Causal Attribution Softened in Abstract

**Location:** Abstract, sentence 5
- Before: "This rules out approximation failure as the mechanism for retrieval degradation, attributing it instead to the SSM state update's exponential forgetting of early token positions"
- After: "This rules out approximation failure as the mechanism for retrieval degradation, narrowing the causal attribution toward the SSM state update's exponential forgetting of early token positions"

**Rationale:** H-E1 behavioral confirmation pending. "Attributing it instead to" asserted bounded-state as confirmed cause. "Narrowing the causal attribution toward" accurately reflects: one mechanism ruled out, bounded-state implicated but behaviorally unconfirmed.

### MAJOR-003 — Optimization Budget Limitation Added

**Location:** Section 6.3 Limitations (new paragraph after "N ≤ 2048")
- Added: "**Optimization budget:** The SSD fitting used 500 Adam steps per layer (vs MOHAWK's reported 10,000 steps). The gate passes with large margin (β=-0.368 vs threshold 0.5), suggesting the result is robust to optimization budget; fully-converged fits would be expected to yield equal or better approximation quality."

**Rationale:** The 500-step budget vs MOHAWK's 10,000-step budget is a methodological choice that reviewers would notice. The gate's large margin makes it defensible, but acknowledging it prevents a "gotcha" reviewer comment.

### Section 2.3 — Hybrid Architectures Trimmed (MINOR-003 partial)

**Location:** Section 2.3
- Before: Referenced both Falcon-H1 and Apriel-H1 with individual sentences
- After: Combined into single sentence referencing Falcon-H1 only as the representative example; Apriel-H1 removed from main text (still in references)

**Rationale:** Apriel-H1 adds no information beyond Falcon-H1 for this paper's purposes. Trimming reduces Section 2.3 padding.

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

**Date:** 2026-08-03  
**Issues Addressed:** 0 FATAL, 0 MAJOR (R2 numerical verification found no new issues)

R2 Serena-pattern verification confirmed all paper numerical claims against source files (h-m1/04_validation.md, h-e1/04_validation.md, h-m2/04_validation.md). No changes to paper content required.

Paper metadata updated: added `r2_status` field confirming numerical verification passed.

---

## Final Summary

**Total Revisions Made:** 4 (all in R1)  
**Sections Modified:** Abstract, Introduction, Section 6.3 (Limitations), Section 2.3 (minor trim)  
**Word Count Change:** ~5273 → ~5310 (+37, from added limitation sentence)

**Review Process:**
- Started: 2026-08-03
- Completed: 2026-08-03
- Rounds: 2 (R1: structural fixes; R2: numerical verification)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Convergence:** CONVERGED after R2 (FATAL=0, MAJOR=0, persuasiveness PASSED)

**Files Generated:**
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_r1.md, 065_review_r2.md (per-round reviews)
- 065_review_checkpoint.yaml (state tracking)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
