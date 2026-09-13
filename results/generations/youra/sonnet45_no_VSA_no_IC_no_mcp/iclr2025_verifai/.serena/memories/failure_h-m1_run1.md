# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-25T02:45:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_INEFFECTIVE

## Performance Gap

| Metric | Ours (Constrained) | Baseline (Vanilla) | Gap |
|--------|-------------------|-------------------|-----|
| Type Error Rate | 88.0% | 84.0% | +4.76% (WORSE) |

## Root Cause Analysis

- **Mechanism mismatch:** Type constraint weighting targets type consistency, but syntax errors dominate HumanEval failures (64-68%, vs 20% type errors)
- **Penalty too weak:** penalty_weight=-2.0 modulates token probabilities but doesn't strongly suppress type violations
- **Limited type checker scope:** h-e1 stub checks return/assignment types, misses function call mismatches, attribute errors, binary operation type errors
- **Partial code ambiguity:** Many intermediate tokens (e.g., `return a +`) cannot be type-checked until expression complete

## Lessons Learned

1. **Failure mode assumption violated** - Hypothesis assumed type errors would dominate generation failures, but syntax errors are 3× more frequent in CodeLlama-7B HumanEval samples
2. **Mechanism implementation ≠ hypothesis validation** - Type constraint logits processor implemented correctly and actively penalizing violations (5.3% token penalty rate), but effect is opposite of expected (error rate INCREASED)
3. **Small-scale validation prevented waste** - 5-problem PoC run detected gate failure early, avoiding expensive full 60-problem run (which was already blocked by CUDA OOM)
4. **Type-only constraints insufficient** - Need multi-modal constraints (syntax + type + semantics) to address dominant failure mode
5. **Soft penalties may be too weak** - Probabilistic logit modulation vs hard token rejection tradeoff needs further investigation

## Feedback for Next Phase

### Suggested Modifications

- Combine type constraints with syntax validity checking (e.g., CFG masking for complete expressions)
- Strengthen penalty weight: ablation study with [-5.0, -10.0, -20.0, hard-rejection]
- Expand type checker coverage: function call argument types, binary operation type compatibility, attribute access validation
- Target dominant failure mode: syntax+type constraint weighting (h-m1-v2) with ≥30% total error reduction threshold

### What NOT To Do

- Do NOT rely solely on type constraints without addressing syntax errors
- Do NOT assume soft penalties (-2.0) are sufficient - test stronger penalties first
- Do NOT run full-scale experiments before small-scale gate validation

### What Showed Promise

- Type checker integration functional: h-e1 stub extracts constraints from AST, detects violations via confidence scoring
- Constraint application working: 5.3% average penalty rate, up to 14% on highly-typed problems
- Mypy evaluation pipeline robust: subprocess wrapper, error taxonomy classification, statistical tests all validated

---
*For cross-phase reference*
*Written at: 2026-08-25T02:45:00Z*
