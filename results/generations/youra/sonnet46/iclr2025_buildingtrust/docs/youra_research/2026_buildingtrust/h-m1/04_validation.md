# H-M1 Validation Report

**Generated:** 2026-03-15 02:01:36 UTC
**Hypothesis:** H-M1 — Base Calibration Verification (ECE_base < 0.15)
**Gate Type:** MUST_WORK

---

## 1. Gate Result

**Gate Verdict:** ✅ PASS
**Threshold:** ECE_base < 0.15 for ALL 3 Pythia base sizes (1.4B, 2.8B, 6.9B)
**Execution Path:** Path A (regex parse h-e1/04_validation.md)

| Model | ECE_base | Gate Check |
|-------|----------|------------|
| Pythia-1.4B | 0.0849 | ✅ PASS |
| Pythia-2.8B | 0.0597 | ✅ PASS |
| Pythia-6.9B | 0.0792 | ✅ PASS |

---

## 2. Key Findings

1. MUST_WORK gate **PASSED**: all 3 Pythia base models show ECE < 0.15.
2. Pretraining without alignment produces well-calibrated logit distributions.
3. Lowest ECE: Pythia-2.8B (0.0597); Highest ECE: Pythia-1.4B (0.0849).
4. Base model calibration confirmed as causal baseline for H-M2/M3/M4 mechanism analysis (alignment-induced ECE shifts).

---

## 3. ECE Ordering (Base vs Aligned)

- Pythia-1.4B: ECE_base (0.0849) < aligned ECE ✅
- Pythia-2.8B: ECE_base (0.0597) < aligned ECE ✅
- Pythia-6.9B: ECE_base (0.0792) < aligned ECE ✅

*(Full aligned ECE values available in H-E1 04_validation.md)*

---

## 4. Figure Paths

- `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_01_ece_gate.png`
- `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_02_base_vs_aligned_ece.png`
- `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_03_calibration_curves.png`
- `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_04_ece_by_subject.png`
- `/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_05_brier_decomposition.png`

---

## 5. Execution Details

- **Execution Path:** Path A (regex parse h-e1/04_validation.md)
- **Gate Threshold:** 0.15
- **Base Sizes Evaluated:** ['1.4b', '2.8b', '6.9b']
- **N Calibration Bins:** 15
- **Timestamp:** 2026-03-15 02:01:36 UTC

---

## 6. Failure Analysis

No gate failure. H-M1 confirms causal baseline: pretraining yields ECE < 0.15.

---

## 7. Next Steps

- H-M1 gate PASSED. H-M2 (logit margin inflation mechanism) is now READY.
- Proceed with hypothesis loop: Phase 2C → 3 → 4 for H-M2.
