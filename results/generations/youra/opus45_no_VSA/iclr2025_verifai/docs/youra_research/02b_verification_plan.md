# Phase 2B: Verification Plan
## H-FeedbackOrder-v1: Feedback Ordering Effect in LLM Code Repair

**Generated**: 2026-08-09T19:56:00+09:00  
**Archon Project**: `a6171cdd-c4e1-4b7b-b2c8-42b319d21e38`

---

## Main Hypothesis

Under iterative repair (3 iterations) on HumanEval (164) + MBPP (500), if feedback is presented in static→execution order versus execution→static order (both with identical byte-matched content at 1000 tokens total), then the static-first condition achieves ≥15% relative pass@1 improvement, because early exposure to static analysis errors scaffolds the LLM's repair process toward surface-level fixes before tackling semantic issues.

---

## Sub-Hypotheses

| ID | Type | Gate | Statement | Prerequisites | Status |
|----|------|------|-----------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | Static→execution ordering achieves ≥15% relative pass@1 improvement over execution→static with 95% CI lower bound >10% | None | READY |
| h-m1 | MECHANISM | SHOULD_WORK | ΔPass₁₂(cascade) > ΔPass₁₂(reverse) — larger early iteration gains in static-first condition (p<0.05) | h-e1 | NOT_STARTED |
| h-m2 | MECHANISM | SHOULD_WORK | Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse) — fewer test regressions in static-first condition (p<0.05) | h-e1 | NOT_STARTED |

---

## Dependency Graph (DAG)

```
H-E1 (Existence) [MUST_WORK]
  ├── H-M1 (Trajectory Signature) [SHOULD_WORK]
  └── H-M2 (Regression Rate) [SHOULD_WORK]
```

H-M1 and H-M2 run in parallel after H-E1 completes — they analyze the same experiment logs with different metrics.

---

## Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| R1: Recency effects confound scaffolding interpretation | Medium | Monitor terminal position bias; compare with random ordering if needed |
| R2: Single model limitation (GPT-4o-mini only) | Low | Cross-model tests deferred to Phase 5 |
| R3: Token truncation degrades feedback quality | Low | Deterministic 500-token cap per feedback type |

---

## Timeline Estimate

| Phase | Hypothesis | Duration | Notes |
|-------|------------|----------|-------|
| Phase 2C | h-e1 | 1 hour | Experiment design |
| Phase 3 | h-e1 | 2 hours | Implementation planning |
| Phase 4 | h-e1 | 4-6 hours | 664 × 3 × 3 API calls |
| Analysis | h-m1, h-m2 | 1 hour | Computed from h-e1 logs |

**Total**: ~8-10 hours

---

## Dialectical Analysis

**Thesis**: Static-first ordering scaffolds coarse-to-fine repair — surface errors cleared before semantic debugging.

**Antithesis**: Recency effect (terminal position wins regardless of content type) — LLMs attend more to later tokens.

**Synthesis**: If trajectory signatures (ΔPass₁₂ gains, lower Regression Rate₁₂) match scaffolding predictions while reverse condition shows opposite patterns, recency alone cannot explain results. The matched-content design isolates ordering from information volume.

---

## Controlled Variables

- **Dataset**: HumanEval (164) + MBPP (500) = 664 problems
- **Model**: GPT-4o-mini
- **Token Budget**: 1000 total (500 static + 500 execution)
- **Iterations**: 3 repair iterations per problem
- **Truncation**: Deterministic, byte-identical across conditions

---

## Success Criteria

### H-E1 (Primary)
- Relative improvement ≥15%
- 95% CI lower bound >10%

### H-M1 (Secondary)
- ΔPass₁₂(cascade) > ΔPass₁₂(reverse)
- p < 0.05

### H-M2 (Secondary)
- Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
- p < 0.05

---

## Archon Task Mapping

| Hypothesis | Archon Task ID |
|------------|----------------|
| h-e1 | `f674a5be-7f71-4fa7-9615-bacf5212e684` |
| h-m1 | `f85ac1d2-a052-46aa-8c73-a363795e7e01` |
| h-m2 | `e8f525b4-588d-494c-87c0-b7bc4f08ce71` |

---

## Next Steps

1. Phase 2C: Design experiment for h-e1
2. Phase 3: Implementation planning
3. Phase 4: Execute and validate
4. Phase 5: Baseline comparison (DETERMINES_SUCCESS gate)
