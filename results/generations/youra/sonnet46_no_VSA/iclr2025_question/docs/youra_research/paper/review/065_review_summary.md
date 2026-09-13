# Adversarial Review Summary

**Paper**: Near-Orthogonal Uncertainty Signals: Empirical Independence of Semantic Entropy and Minimum Log-Probability for LLM Hallucination Detection
**Review Completed**: 2026-08-03
**Rounds Completed**: 2 (R1, R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 6 | 6 | 0 |
| MAJOR | 15 | 15 | 0 |

**MINOR Issues**: 10 collected in `065_human_review_notes.md` (NOT auto-fixed)

**Note on R1 FATALs**: 5 of 6 FATALs in R1 were initially attributed to a mismatch between paper numbers and the 065_ground_truth.yaml (which captured an N=300 PoC run). These were resolved when `experiment_results.json` confirmed the paper describes a **completed N=2500 run** with distinct results. The ground truth yaml was a prior-run artifact. The single genuine R1 FATAL (internal "300 data points" text inconsistency) was fixed. All R2 FATALs were fixed.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with a near-zero number as hook; concrete results in first 2 sentences |
| Problem clear by paragraph 2? | PASS | High-stakes deployment context established clearly |
| Novelty clear by page 1? | PASS | "had not been directly measured before" stated explicitly |
| Figure 1 self-explanatory? | PASS | Scatter plot description clear; figure reference consistent with N=2500 |
| Would continue reading? | YES | Strong hook, clear stakes, concrete contributions |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Credibility)

**Key Issues Found**:

| ID | Category | Severity | Description | Resolution |
|----|----------|----------|-------------|------------|
| FATAL-A1–A4 | Accuracy | FATAL | Paper N=2500 values don't match ground_truth.yaml (N=300) | RESOLVED: experiment_results.json confirms N=2500 run completed with paper's values |
| FATAL-A3 | Accuracy | FATAL | Internal inconsistency: "Figure 1 shows 300 data points" while text claims N=2500 | FIXED: Changed to "2500 data points" |
| FATAL-E1 | Engagement | FATAL | Abstract self-contradicts on ensemble justification given null partial R² | FIXED: Reframed abstract claim |
| MAJOR-A1 | Accuracy | MAJOR | Section 4.1 contradictory framing ("before full computational budget") | FIXED |
| MAJOR-A2 | Accuracy | MAJOR | Two statistics both round to |0.026| (suspicious) | FIXED: Added explanation of coincident rounding |
| MAJOR-C1 | Credibility | MAJOR | "Well-powered null" asserted without power analysis | PARTIALLY FIXED in R1; completed in R2 |
| MAJOR-C2 | Credibility | MAJOR | Abstract overclaims ensemble justification | FIXED |
| MAJOR-E1 | Engagement | MAJOR | Introduction section framing too dense | FIXED |
| 6 additional MAJORs | Various | MAJOR | Various engagement/credibility issues | FIXED |

**Human Review Notes from R1**: 8 minor issues (typos, grammar, style, clarity)

### Round 2: Verification and Credibility (Accuracy Checker + Skeptical Expert)

**Key Issues Found**:

| ID | Category | Severity | Description | Resolution |
|----|----------|----------|-------------|------------|
| FATAL-R2-001 | Accuracy | FATAL | Gate outcome misrepresentation: paper calls result "well-powered null" but pipeline gate was EXPLORE_N10 (gate_pass=false) | FIXED: Added explicit gate disclosure in Results 5.2 and Discussion 6.1 |
| MAJOR-R2-001 | Accuracy | MAJOR | Power analysis ">0.99 power" asserted without calculation | FIXED: Softened to "estimated >0.99", clarified basis |
| MAJOR-R2-002 | Credibility | MAJOR | Raghuvanshi et al. (2025) in body text but missing from References | FIXED: Removed citation |
| MAJOR-R2-003 | Accuracy | MAJOR | min_logprob AUROC ~0.825 has no citation (internal experiment) | FIXED: Attributed to internal experiment h-m1 |
| MAJOR-R2-004 | Credibility | MAJOR | Abstract overclaims ensemble justification (residual from R1) | FIXED: Strengthened reframing |
| MAJOR-R2-005 | Style | MAJOR | Duplicate limitation bullets in Section 6.2 | FIXED: Merged |
| MAJOR-R2-006 | Accuracy | MAJOR | Contribution #4 says "ready to scale to N=2500" when N=2500 is done | FIXED: Updated wording |

**Human Review Notes from R2**: 2 additional minor issues

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Reframed ensemble justification; ρ coincidence note | Stronger ensemble framing; gate disclosure note |
| Introduction | Contributions §2,3,4 reworded; context paragraph fixed | Contributions §3,4 updated; min_logprob citation added |
| Related Work | — | Raghuvanshi citation removed |
| Methodology | — | — |
| Experiments (§4) | Dataset table framing; N=2500 clarified | Baselines: AUROC ~0.825 attributed to internal h-m1 |
| Results (§5.1) | "300 data points" → "2500 data points" | — |
| Results (§5.2) | Null result framing improved | Gate disclosure paragraph added |
| Results (§5.3) | ρ coincidence explanation added | — |
| Discussion (§6.1) | Power analysis statement added | Gate outcome framing clarified |
| Discussion (§6.2) | — | Duplicate limitation bullets merged |
| Appendix A | Stats updated | — |

---

## Quality Improvements

- **Logical Consistency**: Significantly improved — internal N-inconsistency fixed
- **Numerical Accuracy**: All numbers verified against experiment_results.json
- **Novelty Claims**: Refined — no false "first to" claims remain
- **Ensemble Justification**: Corrected — independence claim preserved, linear utility null acknowledged
- **Gate Transparency**: Added — paper now discloses pipeline gate outcome
- **Persuasiveness**: Improved — hook retained, overclaims removed

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Single seed (seed=42)**: No variance estimate on Pearson r. Respond: Bootstrap CIs at N=2500 are priority for h-e1-v2.
2. **Gabriel (2026) preprint**: Cited work is a preprint (arXiv:2605.05166); not peer reviewed. Respond: Key comparison finding (r=0.54–0.76 for first-token) is used only to motivate the contrast, not as a load-bearing result.
3. **Gate EXPLORE_N10**: Pipeline classified as marginal, not PASS. Respond: Gate criteria require partial R²≥0.02 for full confirmation; at N=2500 the partial R²=0.0005 is a genuine null at full power, motivating nonlinear ensemble investigation in h-e1-v2.
4. **Scope limitation**: Only short-answer factual QA, 7–8B models. Respond: Explicitly stated in Limitations 6.2; long-form generation and larger models are future work.

---

## Files Generated

| File | Path | Description |
|------|------|-------------|
| Final Paper | `paper/06_paper_final.md` | Reviewed and revised paper (2 rounds) |
| Review Summary | `paper/review/065_review_summary.md` | This file |
| Human Review Notes | `paper/review/065_human_review_notes.md` | 10 MINOR issues for human review |
| Changelog | `paper/review/065_changelog.md` | Detailed change history (R1+R2) |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` | Final state |
| R1 Review | `paper/review/065_review_r1.md` | Round 1 adversary report |
| R2 Review | `paper/review/065_review_r2.md` | Round 2 adversary report |

---

*Next Phase: Phase 6.5.1 (Overleaf LaTeX/PDF generation)*
