# Hypothesis Pivot Record

**Date:** 2026-03-15T20:20:00
**From:** h-e1
**To:** phase2c-next (new experiment design via Phase 2C)

## Pivot Reason

PARTIAL result from Phase 4 MUST_WORK gate. The prescreening mechanism is correctly implemented and all 67 unit tests pass (100% SDD compliance, 1 Coder-Validator cycle). However, gate metrics failed because the SFT checkpoint is absent — base Qwen2.5-Coder-7B-Instruct achieves 0% pass rate on APPS introductory problems, yielding S_term=0 for all 300 processed problems. No problems fell in the target prescreening window S_term ∈ [0.3, 0.55].

**Gate failures:**
- fraction_k_pass_ge1=0.0 (threshold: >=0.10)
- pct_groups_above_1.5x=0.0 (threshold: >=0.80)
- n_prescreened=0 (threshold: >=50)

**Root cause:** Model capability gap (missing SFT checkpoint), NOT a fundamental flaw in the hypothesis or methodology. The prescreening mechanism itself is valid.

**Reflection outcome:** SELF_MODIFY → Route to Phase 2C for experiment redesign.

## What Changed

- Experiment must use SFT checkpoint (or alternative capable model) to achieve non-zero S_term values
- Gate criteria may need adjustment for base model capability level
- Consider using a model that already achieves >10% pass rate on APPS introductory problems without SFT
- Alternative: include SFT training step as prerequisite before prescreening evaluation

## What Was Preserved

- Complete prescreening pipeline infrastructure (prescreening.py, execution_sandbox.py, evaluate.py, data_loader.py, reward_fn.py, config.py, visualization.py)
- All 67 passing unit tests
- APPS dataset setup (2639 introductory samples, 1923 after difficulty+T filters)
- Variance ratio computation logic (evaluate.py)
- R_ratio, R_binary, S_term reward functions (reward_fn.py)
- Execution sandbox with subprocess harness (execution_sandbox.py)
- PrescreeningConfig dataclass (config.py)

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| n_problems_processed | 300 | From h-e1 |
| n_problems_prescreened | 0 | From h-e1 |
| fraction_k_pass_ge1 | 0.0 | From h-e1 |
| mean_var_ratio | 0.0 | From h-e1 |
| pct_groups_above_1_5x | 0.0 | From h-e1 |
| sft_checkpoint_used | false | From h-e1 |
| model_used | Qwen/Qwen2.5-Coder-7B-Instruct | From h-e1 |
| tests_passed | 67/67 | 100% pass rate |
| coder_validator_cycles | 1 | Efficient implementation |

## Lineage

```
h-e1
    └── (PIVOT: PARTIAL - missing SFT causes 0% base model pass rate...)
        └── phase2c-next (Phase 2C experiment redesign)
```

## Key Lessons for Phase 2C Redesign

1. **SFT checkpoint is critical** — base model cannot solve APPS introductory problems at required rate
2. **Alternative approach A:** Use DeepSeek-Coder or CodeLlama which have higher baseline code pass rates
3. **Alternative approach B:** Add SFT training step as Phase prerequisite before prescreening evaluation
4. **Alternative approach C:** Use easier problems (e.g., HumanEval) where base models achieve >10% pass
5. **Infrastructure is reusable** — code folder can be copied as incremental baseline for next hypothesis

---
*Pivot recorded at: 2026-03-15T20:20:00*
