# Phase 4.5 Synthesis Results
Date: 2026-08-03
Research: H-Diversity-v1 — Community breadth diversity and benchmark displacement timing (Papers With Code)

## Key Outcomes
- Predictions supported: 0/3 (P1 REFUTED, P2 REFUTED, P3 INCONCLUSIVE)
- Refined core statement: Community-breadth diversity at benchmark introduction year does NOT predict plurality displacement hazard (well-powered null: HR=1.006, p=0.9495, CI [0.846,1.196])
- Main theoretical contribution: First well-powered, pre-validated null ruling out breadth-class predictors; 5-gate FAIL FAST methodology is a reusable contribution
- Critical limitation: Time-fixed predictor cannot test accumulation dynamics (CoxTimeVaryingFitter excluded due to 34.1% coverage ceiling)

## Lessons for Future Pipelines
- FAIL FAST pre-validation (G0-G4 gates) is essential: confirmed predictor is real/well-measured, making null attributable to hypothesis not data quality
- Underpowered directional HR=0.871 (22 events) from prior run was sampling noise; 10x power (EPV≈86) gives decisive null HR=1.006
- NaN drop from 345→258 rows should be investigated early in panel construction (match fuzzy join hits to row-level NaN pattern)
- lifelines check_assumptions() can raise string-conversion error on categorical task names — exclude categorical covariates from PH check
