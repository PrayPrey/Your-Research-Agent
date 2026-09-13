# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-03-18T14:15:00+00:00
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** NEGATIVE_CORRELATION (difficulty confound)

## Summary

H-E1 hypothesized that AST structural diversity (TED-based) predicts pass@k across LLMs.
Experiment: Spearman correlation between mean TED diversity and pass@k on HumanEval+/MBPP+ (542 problems × 3 models).

## Performance Data

| Model | avg_rho | Gate Threshold | Pass? |
|-------|---------|----------------|-------|
| llama3_8b | -0.2166 | ≥ 0.15 | FAIL |
| codellama_7b | -0.1106 | ≥ 0.15 | FAIL |
| deepseek_6.7b | -0.1225 | ≥ 0.15 | FAIL |

Gate: MUST_WORK — avg_rho ≥ 0.15 AND min_p < 0.05 for all 3 models.
Result: ALL models show NEGATIVE correlation.

## Root Cause Analysis

- **Difficulty confound:** Hard problems have low pass@k AND low AST diversity (fewer solutions pass → less diversity). Easy problems have high pass@k AND high diversity. This creates a spurious negative correlation driven by problem difficulty, not the mechanism.
- The signal is the opposite of expected: TED diversity does not predict pass@k as a causal feature.
- AST diversity of passing solutions is a consequence of pass@k, not a predictor.

## Lessons Learned

1. Difficulty confound must be controlled before measuring AST diversity vs pass@k correlation.
2. Need to stratify by problem difficulty or use partial correlation controlling for difficulty.
3. AST diversity of passing solutions conflates two effects: (a) inherent solution space diversity and (b) pass rate filtering.
4. Future hypotheses should consider using diversity of ALL attempted solutions (not just passing), or control for difficulty explicitly.
5. The mechanism (structural diversity → pass@k) may have merit but requires a cleaner operationalization.

## Feedback for Next Phase (Phase 0)

### Suggested Modifications
- Control for problem difficulty (e.g., partial correlation with difficulty as covariate)
- Measure AST diversity of ALL generated solutions (not just passing ones)
- Use diversity of attempted solutions as predictor of pass@k
- Consider within-difficulty-tier analysis to remove confound

### What NOT To Do
- Do not use raw Spearman(TED_diversity_passing, pass@k) without difficulty control
- Do not assume correlation of passing-solution diversity with pass@k is causal

### What Showed Promise
- TED computation infrastructure works correctly
- Statistical pipeline (542 problems × 3 models) is sound
- The core intuition (structural diversity relates to problem-solving ability) may still be valid with proper confound control

## Routing Decision

reflection_outcome: ROUTED_TO_PHASE_0
Route: Phase 0 (hypothesis redesign required)

---
*For cross-phase reference*
*Written at: 2026-03-18T14:15:00+00:00*
