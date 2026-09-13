# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-25T19:00:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate soft-failed (EXPLORE result). The quantitative thresholds for the confidence-accuracy decoupling mechanism (ΔAcc ≤ −0.10 AND conf_wrong_adv ≥ 0.70 in ≥60% of cells) were not met with available single-model data. The mechanism partially exists (ANLI difficulty gradient confirmed, consistent with H-M1) but magnitude is smaller than the gate requires.

## Failed Checks

- ΔAcc threshold (≤ -0.10) not met — mean ΔAcc = -0.0105 (only advglue_mnli: -0.0675 and anli_r3: -0.0550 approach threshold)
- conf_wrong_adv threshold (≥ 0.70) not met — mean = 0.6162 (range 0.59–0.65 across all cells)
- gate_pass_rate = 0.0000 (< 0.60 required; 0/5 cells pass both criteria simultaneously)

## Partial Results

| Metric | Value |
|--------|-------|
| gate_pass_rate | 0.0000 |
| gate_pass_count | 0 / 5 |
| mean_delta_acc | -0.0105 |
| mean_conf_wrong_adv | 0.6162 |
| total_cells | 5 |
| anli_gradient_confirmed | True (R3 ≤ R1, consistent with H-M1) |

## Experiment Summary

Post-hoc analysis on H-E1 JSONL outputs (Llama-2-7b-hf only, 5 task cells). AdvGLUE MNLI shows closest accuracy drop (-0.0675) and ANLI R3 shows -0.0550, but neither exceeds the -0.10 threshold. All 5 cells show confidence on wrong adversarial predictions below 0.70 (range 0.59–0.65). The 4-model grid from the PRD (which motivated the 60% pass-rate threshold) was not available — H-E1 contains only Llama-2-7b-hf.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Extending H-E1 with additional models (Mistral-7b, Llama-2-13b, Falcon-7b) to properly evaluate the 4-model × 5-task grid
2. Whether the confidence threshold of 0.70 is appropriate for 7B parameter models (which may be calibrated differently than larger models)
3. Whether AdvGLUE/ANLI adversarial perturbations are sufficiently in-distribution for Llama-2-7b-hf to produce the expected overconfidence pattern

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL), this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-25T19:00:00+00:00*
*For cross-phase reference*
