# Phase 6.5 Adversarial Review Summary

**Date:** 2026-08-02
**Hypothesis:** h-e1
**Rounds completed:** 2 (R1 + R2)
**Final status:** CONVERGED

## Convergence Criteria Met

- FATAL issues after R2: 0
- MAJOR issues after R2: 0
- Rounds: 2 (≥2 required)
- Persuasiveness check: PASS (abstract compelling, LOMO framed correctly, all required limitations present)

---

## Round 1 (R1) Findings

### Persona 1: Accuracy Checker
| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| A1 | FATAL | Per-category p-values in Table 1 used fabricated approximations (~0.12, ~0.12, ~0.15, ~0.20) inconsistent with actual values from stats_results.json (0.265, 0.295, 0.360, 0.695) | FIXED |

### Persona 2: Bored Reviewer
| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| B1 | MINOR | Introduction paragraph 3 dense; mechanism described before reader buy-in | Deferred to human review |
| B2 | MINOR | Zhang et al. (2026) citation timing suspicious for a 2026-08-02 paper | Deferred to human review |
| B3 | MAJOR | Approximate p-values in results table unprofessional (same root as A1) | FIXED (merged with A1) |

### Persona 3: Skeptical Expert
| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| S1 | FATAL | "Pillai's trace (≡ η² in three-group case)" — incorrect equivalence claim | FIXED |
| S2 | MAJOR | encoder×adv_mnli p=0.014 mixed-effects result missing from paper | FIXED (added Section 5.2b with degeneracy caveat) |
| S3 | MAJOR | CheckList absence unexplained in Datasets section | FIXED |
| S4 | MINOR | MANOVA rank-deficiency note absent | Deferred to human review |
| S5 | MINOR | Mixed-effects sensitivity check results absent from results section | FIXED (covered by S2 fix) |

---

## Round 2 (R2) Findings — Numerical Verification

R2 verified all numerical claims against `h-e1/results/stats_results.json`:

| Claim | JSON value | Paper value | Match |
|-------|-----------|-------------|-------|
| η²=0.293 | 0.29313 | 0.293 | ✓ |
| adv_rte η²=0.592 | 0.5923 | 0.592 | ✓ |
| adv_qqp η²=0.354 | 0.3537 | 0.354 | ✓ |
| adv_qnli η²=0.350 | 0.3496 | 0.350 | ✓ |
| adv_sst2 η²=0.274 | 0.2742 | 0.274 | ✓ |
| adv_mnli η²=0.189 | 0.1890 | 0.189 | ✓ |
| anli_r3 η²=0.000 | 0.0 | 0.000 | ✓ |
| p-values (all 6) | [0.36, 0.695, 0.265, 0.295, 0.075, 1.0] | [0.360, 0.695, 0.265, 0.295, 0.075, 1.000] | ✓ |
| LOMO=0.333 (3/9) | 0.3333 | 0.333 | ✓ |
| LOMO confusion | [[0,3,0],[1,1,0],[0,2,2]] | described | ✓ |
| gate_eta_fraction | 0.8333 | 83% (5/6) | ✓ |

| R2 New Finding | Severity | Status |
|---------------|----------|--------|
| R2-1: mixed-effects model degenerate (most p≈1.0 or NaN at N=9); encoder×adv_mnli p=0.014 in pathological model; Section 5.2b overstated | MAJOR | FIXED — hedged to report degeneracy explicitly |

---

## Changes Applied

1. **Table 1 p-values** corrected from approximations to exact permutation values (R1-A1/B3)
2. **Pillai's trace ≡ η² claim** corrected to accurate description in Section 3.5 (R1-S1)
3. **Section 5.2b added** with mixed-effects result and degeneracy caveat (R1-S2; revised in R2)
4. **CheckList note added** to Section 4.1 Datasets (R1-S3)
5. **Section 03_methodology.md** Pillai's trace description corrected
6. **Section 04_experiments.md** CheckList note added
7. **Section 05_results.md** Table 1 p-values corrected; Section 5.2b (mixed-effects) added
8. **06_paper.md** all above changes mirrored
9. **06_paper_final.md** generated with all fixes applied

---

## Files Modified

- `paper/06_paper.md` — all fixes applied
- `paper/sections/03_methodology.md` — Pillai's trace fix
- `paper/sections/04_experiments.md` — CheckList note
- `paper/sections/05_results.md` — p-values corrected, Section 5.2b added

## Files Generated

- `paper/06_paper_final.md` — final paper with all fixes
- `paper/065_review_summary.md` — this file
- `paper/065_changelog.md` — diff-style changelog
- `paper/065_human_review_notes.md` — minor issues for human review
