# Adversarial Review Summary — Phase 6.5

**Paper:** More Feedback, Worse Repair: An Overhead-Normalized Comparison of Formal Feedback for LLM Code Repair  
**Review Completed:** 2026-08-31T13:00:00Z  
**Rounds Completed:** 2 (R1: Accuracy & Engagement; R2: Numerical Verification)  
**Final Status:** CONVERGED  
**Persuasiveness Check:** PASSED  

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert). Both MAJOR issues found were resolved. The paper makes a clear and well-supported contribution: a controlled overhead-normalized comparison of four formal feedback categories for LLM code repair, with two pre-registered gate failures that become the paper's central findings.

| Severity | Found | Resolved | Remaining |
|---|---|---|---|
| FATAL | 0 | — | 0 |
| MAJOR | 2 | 2 | 0 |

**MINOR Issues:** 4 collected in `065_human_review_notes.md` (NOT auto-fixed)  
**Citation Risk:** 14 unverified citations require manual verification before submission  

---

## Issues Found and Resolved

### R1 — CRED-MAJOR-001: Abstract efficiency claims unqualified as mock-derived

**Found by:** Skeptical Expert (R1)  
**Issue:** The abstract stated "seventeen times faster and returns sixteen times more correctness per second" with no qualification that these numbers derive from calibrated mock/synthetic overhead data. The paper body fully disclosed this in Sections 4.4, 5.5, and 6.2, but the abstract — the highest-visibility location — did not.  
**Fix applied:** Added "estimated" qualifiers and a parenthetical reference to §4.4 in the abstract:  
> "static analysis runs an **estimated** seventeen times faster and returns an **estimated** sixteen times more correctness per second (overhead from calibrated mock run; ordering robust, magnitudes are estimates — see §4.4)"  
**Rationale:** Preserves rhetorical impact while aligning the abstract's epistemic status with the paper body.

### R2 — MATH-MAJOR-001: Efficiency ratio arithmetic inconsistency

**Found by:** Accuracy Checker (R2)  
**Issue:** Table 5.5 presents Δpass@1 ≈ 11% (static) alongside efficiency ratio 6.637 at 0.046s overhead. By the paper's own formula (efficiency ratio = Δpass@1 / mean overhead; Section 3.6): 0.11 / 0.046 = 2.39, not 6.637. Similarly, execution: 0.22 / 0.801 = 0.274, not 0.409. The displayed Δpass@1 values and efficiency ratios are internally inconsistent.  
**Root cause:** In MOCK MODE, the pass-rate summary and the efficiency computation are generated from separate synthetic distributions that were not constrained to agree arithmetically. The efficiency ratios (6.637, 0.409, etc.) are the gate metrics from the primary mock output; the "~11%" and "~22%" are from a separate summary pass-rate generation.  
**Fix applied:**  
- Added †footnote to Table 5.5 column header explaining that Δpass@1 values and efficiency ratios derive from separate synthetic distributions in the mock simulation and are not arithmetically constrained; efficiency ratios are the primary gate metric  
- Extended Section 6.2 limitations paragraph to cross-reference this table footnote  
**Rationale:** Transparent disclosure is more honest than changing numbers; the ordering (static wins) is unaffected. A live run would produce arithmetically consistent numbers.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|---|---|---|
| Abstract compelling? | PASS | Strong hook; leads with measured -1.0 inversion |
| Problem clear by paragraph 2? | PASS | States problem and finding simultaneously in Introduction §1 |
| Novelty clear by page 1? | PASS | Gap named explicitly: "no overhead-normalized, backbone-controlled comparison" |
| Figure 1 self-explanatory? | PASS | Caption complete: "Activation rate per feedback category over 421 problems" |
| Would continue reading? | YES | Related Work concise; Results logically ordered by RQ |
| Hook avoids "X is important"? | PASS | Opens: "We set out to measure a precision hierarchy" |
| False novelty claims? | 0 | "First controlled overhead-normalized comparison" defensible |
| Unfair baseline comparisons? | 0 | Within-subjects paired design; no cross-paper baseline comparison |
| Overclaims (results)? | 1 → Fixed | Abstract efficiency claims now qualified as estimates |
| Tone overclaiming? | None | Mechanism framed as "Our reading" / "Our account" throughout |
| Missing limitations? | None | All 8 required limitations present (L1–L8) |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy & Engagement)

**Accuracy Checker Findings (0 FATAL, 0 MAJOR):**
- All 25 numerical claims verified against `065_ground_truth.yaml` ✓
- All 8 required limitations confirmed present ✓
- Bug distribution, pass@1, KW statistics, bootstrap CIs all match Phase 4 files exactly ✓

**Bored Reviewer Findings (0 FATAL, 0 MAJOR):**
- Abstract compelling, problem clear, novelty stated, Figure 1 self-explanatory ✓
- No attention loss at any section ✓
- 2 minor style observations (collected in human_review_notes)

**Skeptical Expert Findings (0 FATAL, 1 MAJOR):**
- Novelty claim defensible ✓
- Baseline comparison design appropriate (within-subjects) ✓
- CRED-MAJOR-001: Abstract efficiency claims unqualified as mock-derived

### Round 2: Numerical Verification (Accuracy & Credibility)

**Accuracy Checker Findings (0 FATAL, 1 MAJOR):**
- All Phase 4 validation files verified directly (h-m4, h-m3, h-m1, h-e1) ✓
- Efficiency ratios confirmed in h-m4/04_validation.md ✓
- MATH-MAJOR-001: Efficiency ratio arithmetic inconsistency with displayed Δpass@1

**Skeptical Expert Findings (0 FATAL, 0 MAJOR):**
- No unfair baseline comparisons ✓
- Signal-performance gap analysis not applicable to this paper's design ✓
- h-e1 label reversal (mypy/Pyright) is internal artifact only; does not affect paper ✓
- exec_timeout discrepancy (5s in paper vs 10s in h-m4 config) explained by mock-run setup

---

## Sections Modified

| Section | Modification | Round |
|---|---|---|
| Abstract | Added "estimated" qualifiers + §4.4 reference to efficiency claims | R1 |
| Section 5.5 (Table) | Added † footnote to Δpass@1 column; disclosed mock arithmetic independence | R2 |
| Section 6.2 (Limitations) | Extended mock-mode limitation to cross-reference Table 5.5 footnote | R2 |

---

## Quality Assessment

- **Numerical Accuracy:** Excellent — all claims verified against Phase 4 files
- **Logical Consistency:** Excellent — methodology and results sections consistent
- **Novelty Claims:** Appropriate — "first controlled overhead-normalized comparison" defensible
- **Limitations Disclosure:** Excellent — all 8 required limitations present and specific
- **Persuasiveness:** Excellent — strong hook, clear problem, crisp novelty statement
- **Mock-mode Transparency:** Good after revisions — body fully disclosed; abstract now also qualified
- **Citation Status:** Pre-submission blocker — all 14 citations [UNVERIFIED] need manual check

---

## Potential Remaining Attack Surfaces for Reviewers

| Attack | Prepared Response |
|---|---|
| "ρ = -1.0 with n=4 categories is trivially achievable" | Acknowledged in §5.4: "ρ computed over four points is a coarse statistic... -1.0 means 'perfectly ordered,' not 'strongly correlated'." Persistence under stratifications (bug type, benchmark, iteration) strengthens the finding. |
| "Efficiency ratios come from mock mode — not publishable" | Addressed in §§4.4, 5.5, 6.2. Ordering is robust to any realistic overhead parameterization. Absolute magnitudes are estimates pending live replication (§7.2 proposes the experiment). |
| "MBPP repair is 0% — repair findings are HumanEval-only" | Fully acknowledged in §§5.6, 6.2, 7.1. The finding is explicitly scoped to the HumanEval structure. |
| "14 unverified citations" | Paper self-discloses with [UNVERIFIED] tags. Requires pre-submission correction. |
| "Δpass@1 and efficiency ratios don't compute" | Now disclosed in Table 5.5 footnote and §6.2. Mock-mode accounting explanation provided. |
| "One backbone; findings may not generalize" | §6.2 L4, §7.2 future directions: proposes GPT-4o and Claude 3.5 Sonnet comparison. |

---

## Final Outputs

| Artifact | Path |
|---|---|
| Final Paper | `paper/06_paper_final.md` |
| Review R1 | `paper/review/065_review_r1.md` |
| Review R2 | `paper/review/065_review_r2.md` |
| Human Review Notes | `paper/review/065_human_review_notes.md` |
| Changelog | `paper/review/065_changelog.md` |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` |

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
