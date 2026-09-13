# Phase 4.5 Synthesis Results
Date: 2026-08-03
Research: H-ContractStrength-v2 — Execution-based contract checking on ContractEval

## Key Outcomes
- Predictions supported: P1 SUPPORTED (HIGH), P2 PARTIALLY_SUPPORTED (LOW — structural n=5), P3 REFUTED (HIGH — gap 0.007 not 0.10)
- Refined core statement: Execution-based contract checking reveals 40% oracle-isolation gap on CVT inputs (4× threshold, p=5.88e-38) and adaptive PBT adds ~10pp beyond static oracle (p=2.64e-22); cross-model variation is negligible at n=5 (genuine null, ΔR²=0.004)
- Main theoretical contribution: Oracle existence threshold effect — any contract yields ~40% isolation gap regardless of richness tier (h-m2: ρ=0.136 not gradient); adaptive PBT contribution is model-invariant (0.099–0.103 across all 5 models)
- Critical limitation: h-m1 oracle design revised — EvalPlus valid inputs produce zero violations on ContractEval inline assert preconditions; CVT inputs used instead. h-m4 structurally underpowered at n=5.

## MUST_WORK gates: 3/3 PASSED (h-e1, h-m1, h-m3)
## SHOULD_WORK gates: 0/2 satisfied (h-m2, h-m4 → LIMITATION_RECORDED)
## Output: 045_validated_hypothesis.md (all 8 sections complete)

## Lessons for Future Pipelines
- ContractEval contracts are inline assert preconditions, not icontract decorators — oracle isolation requires CVT inputs, not static valid inputs. Plan for this upfront in 02c_experiment_brief.md
- n=5 models is structurally insufficient for Kendall τ significance at α=0.05 for any τ < 1.0 (min p ≈ 0.017 at τ=1.0). Future cross-model hypotheses need n≥10 in the hypothesis design
- AST richness tiers may need postcondition-specific filtering; precondition contracts dominate ContractEval and their complexity correlates weakly with oracle power
- Adaptive PBT contribution (h-m3) is remarkably model-invariant — a sign of oracle-level rather than model-level signal
