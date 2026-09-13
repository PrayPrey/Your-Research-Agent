# H-M3 Summary: ΔECE Calibration Under Adversarial Perturbation

**Gate result:** EXPLORE
**Gate pass rate:** 0.20 (1/5 cells with ΔECE > 0.05)
**Mean ΔECE:** 0.0023
**t-stat:** 0.1122  **p-value:** 0.4580
**Mean ECE(clean):** 0.2359  **Mean ECE(adv):** 0.2381

## Per-cell results
| Task | ECE(clean) | ECE(adv) | ΔECE | Pass |
|------|-----------|---------|------|------|
| advglue_mnli | 0.2792 | 0.3497 | 0.0705 | PASS |
| advglue_qqp | 0.0623 | 0.0329 | -0.0294 | FAIL |
| anli_r1 | 0.2792 | 0.2387 | -0.0405 | FAIL |
| anli_r2 | 0.2792 | 0.2656 | -0.0136 | FAIL |
| anli_r3 | 0.2792 | 0.3036 | 0.0243 | FAIL |

## Top-3 cells by ΔECE
  advglue_mnli: ΔECE=0.0705
  anli_r3: ΔECE=0.0243
  anli_r2: ΔECE=-0.0136

## ANLI difficulty gradient
anli_r1: ΔECE=-0.0405
anli_r2: ΔECE=-0.0136
anli_r3: ΔECE=0.0243

## Threshold sensitivity (ablation)
  threshold=0.03: gate_pass_rate=0.20
  threshold=0.05: gate_pass_rate=0.20
  threshold=0.1: gate_pass_rate=0.00

## Notes
- Single-model scope: Llama-2-7b-hf (inherited from H-E1/H-M2)
- Kadavath 2022 expected ECE(clean): 0.05–0.15; observed mean: 0.2359
- Gate type: SHOULD_WORK — EXPLORE result allows pipeline continuation
