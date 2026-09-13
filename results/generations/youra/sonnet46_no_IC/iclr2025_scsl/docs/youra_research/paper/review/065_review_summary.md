# Adversarial Review Summary — Phase 6.5

**Paper**: Where Does WGA Improvement Come From? Backbone vs. Head Robustification in ResNet-50 on Waterbirds  
**Review Completed**: 2026-08-05  
**Rounds Completed**: 2 (R1 + R2)  
**Final Status**: CONVERGED  
**Persuasiveness Check**: PASSED  
**Final Recommendation**: CONDITIONAL_ACCEPT  

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 3     | 3        | 0         |

**MINOR Issues**: 7 total collected in `065_human_review_notes.md` (NOT auto-fixed)

All quantitative claims verified against Phase 4 source files in R2. Cohen's d=6.4759 independently confirmed by manual calculation. Zero numerical discrepancies found.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with structural paradox; concrete numerics (p=0.0039, d=6.48) |
| Problem clear by paragraph 2? | PASS | DFR paradox framed clearly; diagnostic approach stated |
| Novelty clear by page 1? | PASS | Pre-registered linear probe framework is concrete and specific |
| Figure 1 self-explanatory? | CANNOT ASSESS | Caption not in paper source — flagged in HRN-1 |
| Hook avoids "X is important"? | PASS | Opens with "The best-performing method does not change the backbone at all" |
| Would continue reading? | YES | Strong paradox hook; busy reviewer would continue |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| Claim-Evidence Mismatch | 0 |
| Numerical Inconsistency | 0 |
| Baseline Comparison Fairness | 0 |

All 16 quantitative claims checked against ground truth — zero numerical errors.

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Hook Quality | PASS |
| Clarity Issues | 2 MINOR (hypothesis table density, contribution framing) |
| Engagement Problems | 0 |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| Novelty Questions | 0 |
| Methodology Concerns | 2 MAJOR (causal language, citation qualification) |
| Missing Limitations | 0 |
| Qualitative vs Statistical | 1 MAJOR (gradient norm) |

**Key Issues Addressed in R1**:
1. M-1: "verified causal chain" → "mechanistic chain/pathway" throughout paper; intervention-studies disclaimer added to Discussion 6.2
2. M-2: Raymond 2026 citation qualified as "(preprint)" in Related Work, Discussion, and References
3. M-3: Gradient norm comparison (ERM=1.152 vs GroupDRO=0.230) labeled "(qualitative illustration; representative single-seed values, not a pre-registered gate)"

### Round 2: Numerical Verification

All 29 numerical values in the paper verified against Phase 4 source files:

| File | Claims Verified | Result |
|------|-----------------|--------|
| h-m3/04_validation.md | 10 values (per-seed probe acc, p-value, Cohen's d, SAM) | ALL MATCH |
| h-p0/04_validation.md | 6 values (cosine sim per seed, variance per seed) | ALL MATCH |
| h-m2/04_validation.md | 7 values (L2 ratios, DFR control, gradient norms) | ALL MATCH |
| h-m1/04_validation.md | 2 values (minority fraction, group counts) | ALL MATCH |
| h-p2/04_validation.md | 4 values (r full, p full, r n=6, p n=6; CI bounds) | ALL MATCH |

Mathematical validity checks:
- Cohen's d=6.4759 independently verified by manual paired-difference calculation ✓
- d is large because N=5,794 test-set probe accuracy estimates are very precise (SD_paired≈0.00476) ✓
- Bootstrap CI width [-0.925, +0.084] is expected at n=9 with method-level WGA collinearity ✓
- Cosine similarity variance ~1e-14 is consistent with float64 computation on float32 weights ✓

**Key fix in R2**:
- Section header "3.8 Causal Chain Structure" → "3.8 Mechanistic Chain Structure" (residual from R1)

---

## Sections Modified

| Section | Round | Modifications |
|---------|-------|---------------|
| Abstract | R1 | "three-step verified causal chain" → "three-step mechanistic chain" |
| Introduction (para 3) | R1 | "three-step verified causal chain" → "three-step mechanistic chain" |
| Introduction (Contribution #3) | R1 | "Verified causal chain" → "Mechanistic chain" |
| Section 3.1 | R1 | "causal chain" → "mechanistic pathway" |
| Section 3.8 (header) | R2 | "Causal Chain Structure" → "Mechanistic Chain Structure" |
| Section 3.8 (body) | R1 | "verified causal chain" → "verified mechanistic chain" |
| Section 5.2 | R1 | Added "(qualitative illustration; representative single-seed values, not a pre-registered gate)" after gradient norm comparison |
| Section 5.5 | R1 | "The causal chain is verified." → "The mechanistic chain is verified." |
| Section 6.1 (Discussion) | R1 | Raymond 2026 → Raymond 2026 preprint; independence note added |
| Section 6.2 (Discussion) | R1 | Added: "Establishing causality would require intervention studies..." |
| Section 7 (Conclusion) | R1 | "three-step causal chain" → "three-step mechanistic chain" |
| Related Work 2.3 | R1 | Raymond 2026 → Raymond 2026 preprint; independence note added |
| References | R1 | Raymond 2026 venue → "*arXiv preprint*" |

---

## Quality Improvements

- **Logical Consistency**: Improved — causal overclaim removed; terminology unified
- **Numerical Accuracy**: Verified — all 29 values match source files exactly
- **Novelty Claims**: Unchanged — scope is appropriate and defensible
- **Baseline Comparison**: Unchanged — Izmailov 2022 WGA values correctly attributed
- **Persuasiveness**: Maintained — hook is strong; narrative coherent
- **Citation Quality**: Improved — Raymond 2026 preprint qualifier prevents expert rejection

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **n=3 seeds**: Well-defended by d=6.48 (only n=2 needed for 80% power at alpha=0.05 one-sided). Discussion L1 explicitly addresses this.
2. **Single dataset/architecture**: Acknowledged in L2. Waterbirds is canonical; future work directions named.
3. **H-P2 SUGGESTIVE at n=9**: Correctly reported. Root cause (method-level WGA constants) explained in L3. ERM+GroupDRO ablation CONFIRMED.
4. **Causality claim**: M-1 fix deployed. "Mechanistic chain" + Discussion disclaimer ("not causal necessity") is robust.
5. **Raymond 2026 preprint**: M-2 fix deployed. Finding is independently supported by paper's own pre-registered evidence.
6. **Large d=6.48**: Pre-empted in Results 5.3 ("reflects high stability of probe accuracy estimates with N=5,794 test samples").

Suggested responses if raised:
- n=3: "Cohen's d=6.48 requires only n=2 for 80% power at alpha=0.05, one-sided. Power is not a concern for this effect size."
- H-P2: "Correctly reported as SUGGESTIVE. The ERM+GroupDRO ablation (r=-0.755, p=0.041) is CONFIRMED. Limitation L3 acknowledged."
- Causality: "We claim mechanistic co-occurrence (measured), not causal necessity (which requires intervention). Discussion explicitly acknowledges this."

---

## Files Generated

| Artifact | Path |
|----------|------|
| Final Paper | `paper/06_paper_final.md` |
| Review Round 1 | `paper/review/065_review_r1.md` |
| Review Round 2 | `paper/review/065_review_r2.md` |
| Review Summary | `paper/review/065_review_summary.md` |
| Human Review Notes | `paper/review/065_human_review_notes.md` |
| Changelog | `paper/review/065_changelog.md` |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` |

---

## Next Phase

Phase 6.5.1 (Overleaf LaTeX/PDF generation) — run `/phase651-overleaf`
