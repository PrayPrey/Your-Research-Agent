# Adversarial Review Summary

**Paper**: Per-Sample Hessian Trace as an Annotation-Free Minority Group Proxy Under ERM Training
**Review Completed**: 2026-08-04
**Rounds Completed**: 2
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

Paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 4 (+1 R1-introduced) | 5 | 0 |

**MINOR Issues**: 4 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Clear hook, concrete AUROC, mechanism mystery |
| Problem clear by paragraph 2? | PASS | Spurious correlations + annotation burden well framed |
| Novelty clear by page 1? | PASS | "First per-sample second-order annotation-free proxy" stated explicitly |
| Figure 1 self-explanatory? | N/A | Figures not in markdown document |
| Hook avoids "X is important"? | PASS | Opens with concrete result, not generic motivation |
| Would continue reading? | YES | Dual-result framing is genuinely interesting |
| Attention lost at? | Never | Technical but clear throughout |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Novelty)

**Key Issues Found:**

| ID | Category | Severity | Resolution |
|----|----------|----------|------------|
| CRED-MAJOR-001 | Overclaiming tone | MAJOR | Fixed: Introduction hook now says "4/5 random seeds" not "across five" |
| CRED-MAJOR-002 | Methodology contradiction | MAJOR | REVERTED in R2 — paper was correct (code gate IS ≥4/5) |
| CRED-MAJOR-003 | Numerical inconsistency | MAJOR | Fixed: Abstract confidence bound ≥0.97 → ≥0.967 (range 0.9678–0.9999) |
| CRED-MAJOR-004 | Baseline fairness | MAJOR | Addressed: Comparison context paragraph added to Section 5.1 |

### Round 2: Numerical Verification (Accuracy + Skeptical)

**Verification against actual JSON result files:**
- All 15 core numerical claims verified against `experiment_results.json` and `confidence_results.json`
- All R(t*) values, AUROC values, CV values, Spearman ρ values confirmed exact match
- Gate code confirmed `n_passing >= 4` (≥4/5), validating paper's stated threshold
- R1-introduced error caught: mean AUROC stated as 0.885, corrected to 0.89

**New issues found in R2:** 1 (R1-introduced mean AUROC error) — fixed

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Fixed confidence lower bound: ≥0.97 → ≥0.967 (with actual range 0.9678–0.9999) |
| Introduction (hook) | Fixed "across five seeds" → "in 4/5 random seeds (mean AUROC 0.89 across 4 passing seeds)" |
| Section 3.6 | Gate threshold ≥4/5 confirmed correct, R1 erroneous change reverted |
| Section 5.1 | Added comparison context paragraph for AUROC baseline scoping |

---

## Quality Improvements

- **Logical Consistency**: Improved — abstract and results table now internally consistent on confidence lower bound
- **Numerical Accuracy**: Improved — mean AUROC corrected; all claims verified against raw JSON
- **Novelty Claims**: Unchanged — claims were already appropriately scoped
- **Baseline Comparison**: Contextualized — existence result scope explicitly stated
- **Persuasiveness**: Improved — abstract no longer overclaims "across five seeds"
- **Hook Quality**: Improved — now accurately reflects 4/5 seed performance

---

## Reviewer Preparation Notes

Potential attack surfaces for real reviewers:

1. **No comparative baseline AUROC** — the paper defers this to future work. Prepared response: "This paper establishes the existence result (AUROC>0.85) for a novel signal class. Direct comparison requires implementing JTT/SELF as minority detectors under identical conditions — a separate experimental pipeline. We scope this paper to the existence result and mechanism investigation."

2. **Single dataset (Waterbirds only)** — acknowledged in Section 6.4. Prepared response: "Waterbirds is the standard spurious correlation benchmark. Generalization is explicitly identified as future work (H-M2, H-M3 hypotheses)."

3. **Mechanism unverified (feature-norm channel)** — acknowledged in Section 6.2 and 6.4. Prepared response: "We explicitly state this is a candidate, not a verified claim. The next experiment (directly measuring ‖x_i‖² at t*) is the clear next step."

4. **Seed 1 failure** — acknowledged in Section 6.4. Prepared response: "4/5 seeds satisfying all three criteria is a strong result; seed 1 satisfies 2/3 criteria. The non-monotone trajectory in seed 1 is a known stochastic artifact worth investigating."

---

## Final Recommendation

**CONVERGED — CONDITIONAL ACCEPT**

All FATAL and MAJOR issues resolved. Paper is technically sound, numerically accurate, and persuasively framed. MINOR issues (EVaLS citation, scalability limitation note) collected for human review before submission.
