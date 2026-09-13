# Adversarial Review Summary
**Paper:** Deduplication Produces a Contamination-Correction Benchmark Accuracy Signature
**Review Completed:** 2026-08-25T21:00:00+00:00
**Rounds Completed:** 2
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 3 | 3 | 0 |

**MINOR Issues:** 4 items collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with concrete puzzle, delivers clear resolution |
| Problem clear in 1 minute? | PASS | "What is happening?" paragraph lands immediately |
| Novelty clear in 2 minutes? | PASS | Contributions clearly enumerated in Introduction |
| Figure 1 self-explanatory? | CONDITIONAL PASS | Methodology figures appear before Results figures — numbering is internally consistent but unusual |
| Hook avoids "X is important"? | PASS | Opens with puzzle, not importance claim |
| Would continue reading? | YES | Strong, specific opening claim |
| Attention lost at? | Never (post-R1 fix) | Step 99K/128K ambiguity removed by footnote |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Numerical claim verification | 0 discrepancies |
| Methodology claim verification | 1 MAJOR (Pile step 99K/128K ambiguity) |

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| Figure numbering inconsistency | 1 MAJOR (fig_04 named Figure 3) |
| Engagement issues | None |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| n=16 statistical framing | 1 MAJOR (n=4 non-significance buried in Limitations) |
| Missing limitations | 1 MAJOR (no Phase 5 baseline comparison disclosed) |
| Novelty claims | No overclaims detected |
| Baseline fairness | Fair comparison methodology |

**Key Issues Addressed in R1:**
1. ACC-MAJOR-001: Added clarifying footnote about Pile step 99K (primary) vs 128K (H-M4 internal simulation)
2. ENG-MAJOR-001: Fixed `fig_04_bias_decomposition.png` → `fig_03_bias_decomposition.png` in 2 locations
3. SKP-MAJOR-001: Added n=4 non-significance disclosure to Methodology (r=0.776, p=0.224)
4. SKP-MAJOR-002: Added Limitation L6 (no formal Phase 5 baseline comparison)

### Round 2: Numerical Verification

All 12+ numerical claims systematically verified against Phase 4 validation files:
- h-e1/04_validation.md: MMLU t/p/Δ, all benchmarks ✅
- h-m3/04_validation.md: r, ρ, CI, per-size correlations, n=4 ablation ✅
- h-m4/04_validation.md: Δr, bias_delta, checkpoint mapping ✅
- h-m2/04_validation.md: direction reversal, all deltas ✅
- h-m1/04_validation.md: 2/4 benchmarks, Spearman ρ=1.0 ✅

**No numerical discrepancies found.** 1 new minor issue (per-size p-values not reported).

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | None |
| Introduction | None |
| Related Work | None |
| Methodology (Sec 3) | Token-Count Matching (footnote + figure filename fix); Correlation Analysis (n=4 disclosure added) |
| Experiments (Sec 4) | None |
| Results (Sec 5) | Section 5.2 (per-size non-significance parenthetical) |
| Discussion (Sec 6) | Limitations: Added L6 (no Phase 5 baseline) |
| Conclusion | None |
| Figure Reference Summary | fig_03 filename corrected |

---

## Quality Improvements

- **Logical Consistency:** Improved (step 99K footnote clarifies apparent discrepancy)
- **Numerical Accuracy:** Unchanged (all claims already correct)
- **Statistical Framing:** Improved (n=4 non-significance now disclosed in Methodology)
- **Limitations Coverage:** Improved (L6 added)
- **Persuasiveness:** Unchanged (already strong)
- **Figure Numbering:** Improved (filename/number inconsistency fixed)

---

## Reviewer Preparation Notes

**Potential remaining attack surfaces for real reviewers:**

1. **n=16 effective sample size** — Now pre-empted in Methodology with n=4 disclosure. Prepared response: "Our primary n=16 analysis treats model-size replications as independent observations; per-size correlations all exceed r=0.5, supporting this. At n=4 (benchmark mean), r=0.776 does not reach significance — we report this prominently in Section 3."

2. **H-M4 analytical simulation** — Disclosed in paper (both Methodology and Results). Prepared response: "The direction of the result is theoretically constrained by the volume confound model. The H-M3 primary result (r=0.632, real GPU inference) is unaffected."

3. **Proxy contamination estimates** — Disclosed as L2. Prepared response: "We use established literature estimates (Lee et al. 2022, GPT-4 TR); H-M1 freshly computed estimates are pending and will be incorporated in camera-ready."

4. **Single model family** — Disclosed as L5. Future work section mentions OLMo/Dolma extension.

5. **H-M1 dry-run only** — Clearly disclosed in all mentions. Full experiment pending.

---

## Files Generated

| Artifact | Path |
|----------|------|
| Final Paper | `paper/06_paper_final.md` |
| Review Summary | `paper/review/065_review_summary.md` |
| Human Review Notes | `paper/review/065_human_review_notes.md` |
| Changelog | `paper/review/065_changelog.md` |
| R1 Review | `paper/review/065_review_r1.md` |
| R2 Review | `paper/review/065_review_r2.md` |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` |
| Paper R1 | `paper/06_paper_r1.md` |
| Paper R2 | `paper/06_paper_r2.md` |

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
