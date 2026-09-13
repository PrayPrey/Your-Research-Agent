# Adversarial Review Summary — Phase 6.5

**Paper:** The Coordinate System, Not the Symmetry Group: Graph-Based SSL for Cross-Architecture Weight Space Transfer
**Review Completed:** 2026-08-05
**Rounds Completed:** 2 (R1 + R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED
**Recommendation:** CONDITIONAL_ACCEPT

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 1 | 1 | 0 |
| MAJOR | 11 | 11 | 0 |

**MINOR Issues:** Collected in `065_human_review_notes.md` (NOT auto-fixed)

All critical issues resolved. Paper is ready for final human polish before submission.

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong hook sentence; concrete result stated upfront |
| Problem clear by paragraph 2? | PASS | Failure mode of SANE is clearly described |
| Novelty clear by page 1? | PASS | Graph schema as coordinate system is crisp |
| Figure 1 self-explanatory? | PASS (assumed) | Figures referenced but not inline in markdown |
| Hook avoids "X is important"? | PASS | Starts with concrete claim |

---

## Round-by-Round Summary

### Round 1 (R1): Three-Persona Review

**Focus:** Structural issues, accuracy, engagement, credibility

**Accuracy Checker Findings (0 FATAL, 3 MAJOR):**
| Issue | Finding |
|-------|---------|
| ACC-MAJOR-001 | EquiSSL R² differs between Table 1 (0.210, h-m1) and Table 2 (0.185, h-m2) — different runs, not explained |
| ACC-MAJOR-002 | +221% vs 219.5% arithmetic — paper's 221% is correct rounding of 220.8% (verified, minor consistency fix) |
| ACC-MAJOR-003 | [Anonymous2025LayerNorm] arXiv:2510.08300 cited in body as established theory but marked [UNVERIFIED] |

**Bored Reviewer Findings (0 FATAL, 1 MAJOR):**
| Issue | Finding |
|-------|---------|
| ENG-MAJOR-001 | Abstract stated "3x R² improvement" without giving SANE's base R²=0.072 |

**Skeptical Expert Findings (0 FATAL, 4 MAJOR):**
| Issue | Finding |
|-------|---------|
| CRED-MAJOR-001 | "R²=0.231–0.327" range in Contribution (3) spanned two independent runs, not a seed range |
| CRED-MAJOR-002 | SANE described as SOTA without noting R²=0.72 in its intended same-architecture setting |
| CRED-MAJOR-003 | "Establishing a new baseline" overclaim for n=53, single-seed proof-of-concept |
| CRED-MAJOR-004 | Unverified citation does structural load-bearing work in LayerNorm argument |

**R1 Key Issues Resolved:**
- Abstract now states R²=0.231 vs SANE's R²=0.072 (3× improvement)
- All occurrences of [Anonymous2025LayerNorm] hedged as "empirically motivated conjecture, not proven mechanism"
- SANE's R²=0.72 within-architecture performance now stated throughout
- "Establishing a new baseline" → "providing initial proof-of-concept evidence"
- h-m1 vs h-m2 independent run distinction made explicit in both table captions

### Round 2 (R2): Numerical Verification with Serena MCP

**Focus:** Mathematical validity, baseline fairness, numerical verification

**FATAL Issues (1 found, 1 resolved):**
| Issue | Finding | Resolution |
|-------|---------|------------|
| FATAL-R2-001 | Table 3 mixed two incompatible MMD definitions: SANE=0.849 and EquiSSL=2.348 from h-e1 (CNN→ViT cross-arch MMD), but EquiSSL-perm=0.203 from h-m2 (within-ViT subpopulation MMD — different quantity) | EquiSSL-perm row removed from Table 3; explicit note added that cross-arch MMD not computed for EquiSSL-perm; Limitations section updated |

**MAJOR Issues (3 found, 3 resolved):**
| Issue | Finding | Resolution |
|-------|---------|------------|
| MAJOR-R2-001 | Symmetry group ablation (Table 2) uses EquiSSL from h-e1 (50 epochs) vs EquiSSL-perm from h-m1 (100 epochs) — 2× training discrepancy | Disclosed in Table 2 caption and new Limitations bullet; Table 1's ΔR²=+0.021 cited as more controlled evidence |
| MAJOR-R2-002 | "+221%" still in 4 places; consistent with rounded values but inconsistent with ground truth's 219.5% | Changed to "~220%" with explicit computation parenthetical |
| MAJOR-R2-003 | h-m2 described as "fresh training run from scratch" but actually applies fresh RidgeCV evaluation to pre-existing checkpoints | All descriptions corrected; epoch discrepancy properly attributed |

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Added SANE R²=0.072 baseline | Changed "221%" to "~220%" |
| Introduction | SANE context, hedged citation, removed range notation, Contribution (2) softened | Epoch discrepancy note for Contribution (3) |
| Related Work 2.4 | LayerNorm framed as hypothesis | — |
| Section 3.5 | Retitled; fully reframed as conjecture | — |
| Section 3.6 | SANE within-arch R²=0.72 context added | — |
| Section 5.1 | Table 1 caption, ~220% | ~220% consistency |
| Section 5.2 | Table 2 caption, h-m1/h-m2 independent run disclosure | Epoch discrepancy in caption |
| Section 5.4 | — | Table 3 EquiSSL-perm row removed; Limitations note |
| Section 6 Discussion | Finding 2 updated | MMD limitation, ~220% |
| Section 6 Limitations | — | New "Ablation fairness" and "MMD comparability" bullets |
| Section 7 Conclusion | Softened baseline claim | ~220%, ablation caveat |
| Appendix A | — | MMD figure description updated |
| Appendix B | — | Epoch note |

---

## Quality Improvements

- **Logical Consistency:** Improved — h-m1/h-m2 distinction made explicit; Table 3 MMD confound fixed
- **Numerical Accuracy:** Improved — ~220% consistently; epoch discrepancy disclosed
- **Novelty Claims:** Refined — "proof-of-concept evidence" not "new baseline"; citation hedged
- **Baseline Comparison:** Contextualized — SANE's within-arch R²=0.72 stated; MMD confound removed
- **Persuasiveness:** Improved — SANE base R² in abstract; cleaner narrative
- **Statistical Honesty:** Preserved — single seed, n=53 caveats maintained throughout

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Single seed, n=53**: Core limitation. Prepared response: "Results are preliminary but directionally consistent with theoretical predictions. Full multi-seed, 250-model evaluation is the stated future work (Section 7)."

2. **Ablation confound (50 vs 100 epochs)**: Now disclosed. Response: "We acknowledge the epoch discrepancy in Table 2. Table 1 provides a more controlled comparison showing ΔR²=+0.021 for EquiSSL-perm vs EquiSSL under comparable conditions."

3. **Unverified citation [Anonymous2025LayerNorm]**: Now hedged. Response: "The citation is noted as unverified. Our empirical finding (scale equivariance hurts ViT SSL) stands independently; the LayerNorm argument provides theoretical motivation, not justification."

4. **No cross-arch MMD for EquiSSL-perm**: Now acknowledged. Response: "MMD was not computed for EquiSSL-perm in cross-architecture setting. Table 3 correctly shows only the two available measurements. R² is the primary evaluation metric."

5. **SANE out-of-distribution testing**: Now addressed. Response: "SANE's R²=0.72 in its intended setting is explicitly acknowledged. We study the cross-architecture distribution shift failure mode — this is the research question, not a flaw in our evaluation."

---

## Human Review Notes

See `065_human_review_notes.md` for collected minor issues (typos, grammar, style, formatting). Total: ~12 notes across R1 and R2. None block acceptance.

---

## Files Generated

| File | Path |
|------|------|
| Final Paper | `paper/06_paper_final.md` |
| Review R1 | `paper/review/065_review_r1.md` |
| Review R2 | `paper/review/065_review_r2.md` |
| Review Summary | `paper/review/065_review_summary.md` |
| Human Review Notes | `paper/review/065_human_review_notes.md` |
| Changelog | `paper/review/065_changelog.md` |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` |

**Next Phase:** Phase 6.5.1 — Overleaf LaTeX/PDF generation
