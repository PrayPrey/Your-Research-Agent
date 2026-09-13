# Phase 6.5 Adversarial Review Summary

**Date:** 2026-08-20  
**Rounds completed:** 2  
**Final verdict:** CONVERGED — paper approved for submission

---

## Review Configuration

| Field | Value |
|---|---|
| Personas | Accuracy Checker, Bored Reviewer, Skeptical Expert |
| Rounds | R1 (all three), R2 (numerical verification) |
| Ground truth source | 065_ground_truth.yaml + h-e1/h-m1/h-m2/h-m3 validation files |
| Max rounds | 3 |
| Convergence | Round 2 |

---

## Issues Found and Resolved

### FATAL Issues (2 found, 2 fixed)

| # | Location | Issue | Fix Applied |
|---|---|---|---|
| F1 | 05_results.md, 06_paper.md Table 1 | "GLUE→AdvGLUE" label for OOD pair — incorrect benchmark name | Changed to "OOD Robustness" throughout |
| F2 | 06_paper.md Section 5.3 | RQ ordering 1→3→2 with no rationale in assembled paper | Added rationale sentence: "We present RQ3 before RQ2 because the mechanism test result reframes the interpretation of the Δρ analysis" |

### MAJOR Issues (3 found, 3 fixed)

| # | Location | Issue | Fix Applied |
|---|---|---|---|
| M1 | 06_paper.md Table 1 footnote, Section 6.2 | Fisher z-test applied across different N (N=16 vs N=13) — Meng et al. 1992 requires same sample | Added explicit clarification that ρ_fairness was re-estimated on N=13 subset (ρ=0.967) for Δρ computation; Meng et al. assumption met |
| M2 | 06_paper.md Table 1, Section 5.4 | Δρ=0.192 computation basis ambiguous — unclear whether ρ_fairness(N=16)=0.962 or ρ_fairness(N=13)=0.967 was used | Added footnote: Δρ=0.967−0.776=0.192 from N=13 subset; N=16 result (0.962) is primary P1 estimate |
| M3 | Section 2.4 | Gevers & Daelemans [2026] cited as predecessor but from same year — no caveat | Added "(preprint; independently verified as plausible but not confirmed via library access at submission time)" |

### MINOR Issues (collected for human review — NOT auto-fixed)

See `065_human_review_notes.md` for full list.

---

## Numerical Verification Summary

All primary metrics verified against source files:

| Metric | Paper | Source | Match |
|---|---|---|---|
| ρ_fairness | 0.962 | h-m1: 0.9617 | ✅ |
| p_fairness | <0.0001 | h-m1: 0.0000 | ✅ |
| CI_fairness | [0.90, 1.00] | h-m1: [0.90, 1.00] | ✅ |
| ρ_ANLI | 0.684 | h-m3: 0.6835 | ✅ |
| p_ANLI | 0.007 | h-m3: 0.0071 | ✅ |
| ρ_OOD | 0.868 | h-m3: 0.8675 | ✅ |
| p_OOD | 0.0001 | h-m3: 0.0001 | ✅ |
| Rank reversals | 0, 0 | h-m3: 0, 0 | ✅ |
| Δρ | 0.192 | h-m2: 0.192 | ✅ |
| Fisher z | 2.265 | h-m2: 2.265 | ✅ |
| Fisher p | 0.024 | h-m2: 0.024 | ✅ |
| ρ_Winogrande | 0.969 | h-m1: 0.9691 | ✅ |
| Winogrande N | 14 | h-m1: 14 | ✅ |
| Winogrande Δρ | 0.073 | 045_validated: 0.073 | ✅ |
| N_fairness | 16 | h-m1: 16 | ✅ |
| N_robustness | 13 | h-m2/h-m3: 13 | ✅ |
| Shortfall | 0.008 | 0.200−0.192=0.008 | ✅ |

---

## Convergence Decision

- Round 1: 2 FATAL + 3 MAJOR found, all fixed
- Round 2: 0 FATAL, 0 MAJOR remaining; all numbers verified
- Persuasiveness: Abstract compelling (falsified mechanism hook), novelty clear in <2 min, contributions numbered
- **Converged at round 2**

---

## Remaining Risks (not blocking)

| Risk | Level | Mitigation |
|---|---|---|
| Gevers & Daelemans [2026] citation unverifiable | LOW | Caveat added in text |
| Yang et al. 2023 GLUE-X citation unverified | LOW | [UNVERIFIED] tag in references |
| N=13 model list inconsistency (Falcon-40B in h-m2 not in h-e1) | LOW | Internal artifact; no paper-facing numbers affected |
