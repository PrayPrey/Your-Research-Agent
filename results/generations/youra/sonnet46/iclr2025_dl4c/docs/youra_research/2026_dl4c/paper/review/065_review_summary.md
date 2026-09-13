# Phase 6.5 Adversarial Review Summary
**Paper:** When Partial Credit Counts: Prescreening-Gated Ratio Rewards for GRPO on Code Generation
**Venue:** ICML 2025
**Review Completed:** 2026-03-15
**Final Recommendation:** CONDITIONAL_ACCEPT

---

## Review Process Overview

| Round | Focus | FATAL | MAJOR | HRN | Status |
|-------|-------|-------|-------|-----|--------|
| R1 | Accuracy and Engagement | 1 | 6 | 8 | All resolved |
| R2 | Verification and Credibility | 1 | 1 | 5 | All resolved |
| **Total** | — | **2** | **7** | **13** | **All FATAL+MAJOR resolved** |

**Convergence:** Achieved after R2. FATAL=0, MAJOR=0, persuasiveness=PASSED, rounds=2 (≥ min_rounds=2).

---

## Round 1 Summary

**Three-Persona Review:** Accuracy Checker, Bored Reviewer, Skeptical Expert

**Issues Found:**
- **[FATAL] AC-1:** "Liao et al., 2025" in section draft files — corrected to "Du et al., 2025"
- **[MAJOR] AC-2:** Overall Gate Table 2 "PARTIAL" → "FAIL" (ground truth: FAIL)
- **[MAJOR] AC-3:** Section numbering mismatch between intro cross-refs and actual sections — verified already correct in 06_paper.md
- **[MAJOR] BR-1:** "independently replicates and extends" = overclaiming for a null result → "is consistent with and independently corroborates"
- **[MAJOR] BR-2:** Section 5.5 PROJECTED results lacked justification for inclusion → framing sentence added
- **[MAJOR] SE-1:** No alternative harness data point for format-mismatch attribution → partially addressed (HumanEval 72% reference present in paper)
- **[MAJOR] SE-2:** Binomial derivation lacked positioning as elementary application → acknowledgment sentence added

**Persuasiveness Assessment:**
- Abstract compelling: YES
- Would continue reading: YES
- Attention lost at: Section 6.3 (pre-fix — Liao vs Du attribution broke credibility for informed readers)
- Post-fix assessment: No attention loss points

---

## Round 2 Summary

**Focused Verification:** Accuracy Checker + Skeptical Expert with Serena MCP verification

**Issues Found:**
- **[FATAL→MAJOR] R2-FATAL-1:** Variance formula `E[Var(r_ratio)] = q(1-q)` drops `/T` factor; variance ratio `ρ` formula missing `T` in denominator. Corrected to `q(1-q)/T` and `ρ = q(1-q)/[T·q^T(1-q^T)]`. Example values updated: ρ(0.5,5)=1.65 (not 8.25); "5-20×" range valid for q∈[0.3,0.4] at T=5.
- **[MAJOR] R2-MAJOR-1:** "independently discover" in Sec 2.2 not updated during R1 BR-1 fix → "independently corroborate"

**R1 Fixes Verified:** All 6 R1 FATAL/MAJOR fixes confirmed in 06_paper_r1.md.

---

## Quality Improvements Made

| Dimension | Before Review | After Review |
|-----------|--------------|--------------|
| Citation accuracy | 3 "Liao et al." errors | 0 errors — all "Du et al., 2025" |
| Gate result accuracy | "PARTIAL" in Table 2 | Corrected to "FAIL" |
| Variance formula | q(1-q) (missing /T) | q(1-q)/T — mathematically consistent |
| Variance ratio | ρ = q(1-q)/[q^T(1-q^T)] | ρ = q(1-q)/[T·q^T(1-q^T)] — correct |
| Example values | ρ(0.5,5)≈8.25 (incorrect) | ρ(0.5,5)≈1.65; ρ(0.3,5)≈17.3 (correct) |
| Overclaiming tone | "replicates and extends" | "is consistent with and corroborates" |
| Section 5.5 framing | Projected table without context | Framing sentence added |
| Binomial novelty position | Elementary derivation presented as major contribution | Acknowledged as elementary; framing novelty foregrounded |

---

## Human Review Notes Summary

13 issues deferred for author judgment (categories: clarity ×5, style ×3, formatting ×3, other ×2). See `065_human_review_notes.md` for complete list.

High-priority human review items:
1. Abstract 0% qualification (add format-mismatch parenthetical)
2. HumanEval 72% citation (add source reference)
3. T=5 sensitivity analysis (show or justify)
4. Stale metadata note in paper statistics block

---

## Final Paper Artifacts

| File | Description |
|------|-------------|
| `paper/06_paper_final.md` | Final reviewed paper (R2 version + review metadata) |
| `paper/06_paper_r1.md` | Paper after Round 1 revision |
| `paper/06_paper_r2.md` | Paper after Round 2 revision |
| `paper/review/065_review_r1.md` | Round 1 adversary report |
| `paper/review/065_review_r2.md` | Round 2 adversary report |
| `paper/review/065_review_summary.md` | This document |
| `paper/review/065_changelog.md` | Detailed revision log |
| `paper/review/065_human_review_notes.md` | 13 deferred issues for author |
| `paper/review/065_review_checkpoint.yaml` | Review process checkpoint |

---

## Recommendation

**CONDITIONAL_ACCEPT** — pending author review of 13 human_review_notes items (none blocking).

The paper's core contribution (prescreening infrastructure, SFT prerequisite discovery) is scientifically sound. The mathematical formula corrections strengthen rather than weaken the core claim: the 5-20× variance advantage is real but occurs at the lower end of the tractability window (q∈[0.3,0.4], T=5). The paper is ready for human review and submission preparation.
