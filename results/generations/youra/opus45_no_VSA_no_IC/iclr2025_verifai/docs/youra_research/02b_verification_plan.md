# Phase 2B: Verification Plan
**Generated:** 2026-08-24
**Main Hypothesis:** h-sa-correlation-001

## Main Hypothesis

**Statement:** Static analysis metrics (pylint score, mypy error count, radon cyclomatic complexity) exhibit moderate positive correlation (point-biserial r ≥ 0.35) with functional correctness (pass@1) on HumanEval/MBPP for LLM-generated code, after controlling for code length as a confounding variable.

**Success Criterion:** r ≥ 0.35, p < 0.05 (partial correlation controlling for LOC)

## Sub-Hypotheses

### H-E1: SA Metrics Measurable on LLM Code (EXISTENCE)
- **Type:** EXISTENCE
- **Gate:** MUST_WORK
- **Statement:** Pylint, mypy, and radon produce valid numeric outputs on ≥95% of LLM-generated code samples without crashing or null values.
- **Prerequisites:** None
- **Status:** READY
- **Success Criterion:** ≥95% valid output rate across all SA tools

### H-M1: Single SA Metric Correlation (MECHANISM)
- **Type:** MECHANISM
- **Gate:** MUST_WORK
- **Statement:** At least one SA metric (pylint score OR mypy error count OR radon CC) shows point-biserial correlation r ≥ 0.35 with pass@1, controlling for code length, on combined HumanEval+MBPP dataset.
- **Prerequisites:** H-E1
- **Status:** NOT_STARTED
- **Success Criterion:** max(r_pylint, r_mypy, r_radon) ≥ 0.35 with p < 0.05

### H-M2: Ensemble SA Correlation (MECHANISM)
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Statement:** A weighted ensemble of SA metrics achieves higher correlation with pass@1 than any single metric (r_ensemble > max(r_individual)).
- **Prerequisites:** H-M1
- **Status:** NOT_STARTED
- **Success Criterion:** r_ensemble > max(r_individual)

### H-C1: Cross-Model Generalization (CONDITION)
- **Type:** CONDITION
- **Gate:** SHOULD_WORK
- **Statement:** SA-correctness correlation generalizes across 3+ LLMs with variance std(r) < 0.15, demonstrating model-agnostic predictive signal.
- **Prerequisites:** H-M1
- **Status:** NOT_STARTED
- **Success Criterion:** std(r_per_model) < 0.15 across GPT-4, Claude-3, Llama-70B, Codestral

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK)
  │
  └──► H-M1 (MUST_WORK)
         │
         ├──► H-M2 (SHOULD_WORK)  [parallel]
         │
         └──► H-C1 (SHOULD_WORK)  [parallel]
```

## Risk Analysis

| Risk | Level | Mitigation |
|------|-------|------------|
| SA tools crash on malformed LLM code | Low | Wrapper with timeout/exception handling |
| Effect size r < 0.35 | Medium | Negative result publishable as debunking assumption |
| Cross-model variance > 0.15 | Medium | Report per-model results regardless |
| Code length confound dominates | Low | Partial correlation already planned |

## Timeline Estimate

| Phase | Hypothesis | Duration | Dependencies |
|-------|------------|----------|--------------|
| Week 1 | H-E1 | 3 days | None |
| Week 1-2 | H-M1 | 7 days | H-E1 |
| Week 2-3 | H-M2, H-C1 | 5 days each (parallel) | H-M1 |
| Week 3 | Synthesis | 3 days | All |

## Archon Project

- **Project ID:** 191dbfef-5512-4e14-aef1-0a28b718627f
- **Task Mapping:**
  - H-E1: 1a308df6-40e9-4b1e-b356-aa062d769cfc
  - H-M1: f1b5dd2d-a614-401b-ad62-6c185b40f6ec
  - H-M2: 55daed85-487f-4e24-9696-460fe1038fdf
  - H-C1: 884dfd64-c8fc-415d-abc8-9568027c3484

## Next Steps

1. Begin Phase 2C with H-E1 (first READY hypothesis)
2. Design experiment for SA tool coverage measurement
3. Generate implementation plan in Phase 3
