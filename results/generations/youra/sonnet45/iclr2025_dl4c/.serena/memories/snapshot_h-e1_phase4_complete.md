# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-18T16:28:49Z
**Hypothesis:** h-e1
**Type:** EXISTENCE
**Final Status:** FAILED
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Statement

> Under EvalPlus HumanEval evaluation conditions, if static structural features (12-dim vector: cyclomatic complexity, branch density, nesting depth, AST entropy, etc.) are extracted from LLM-generated code solutions, then these features will explain at least 50% of test coverage residual variance (median residual variance ratio ≥ 0.5 across ≥70% of tasks) after controlling for semantic equivalence clusters and task difficulty.

## Results

- **Validation:** COMPLETED
- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL (0/4 checks passed)
- **Experiment Status:** COMPLETED with real data
- **Routing Decision:** ROUTED_TO_PHASE_0

### Performance Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Proposed R² | 0.2938 | N/A | ❌ Below baseline |
| Baseline R² | 0.5582 | N/A | Reference |
| Improvement | -0.2644 (-47.4%) | Positive | ❌ FAIL |
| Median Ratio | NaN | ≥ 0.5 | ❌ FAIL |
| Task Coverage >0.4 | 0.0% | ≥ 70% | ❌ FAIL |
| Delta R² | 0.0000 | ≥ 0.10 | ❌ FAIL |
| Max VIF | 29.20 | ≤ 5.0 | ❌ FAIL |

## Root Cause

**Dataset Mismatch:** CoverageEval provides one canonical solution per task, hypothesis requires diverse CODE solutions. Coverage variation comes from different TESTS (not different CODE implementations), making structural features constant within each task.

## Reflection Summary

- **Triggered:** Yes (automatic for MUST_WORK FAIL)
- **Outcome:** ROUTED_TO_PHASE_0
- **Meaningful Findings:** Fundamental hypothesis-dataset incompatibility
- **Modification Attempts:** 0

### Lessons Learned

1. **Always verify dataset structure matches hypothesis requirements** - CoverageEval's single-solution design is incompatible with code diversity hypothesis
2. **Coverage variation source matters** - Test-level variation ≠ code-level variation
3. **Structural features need variation** - Constant features across task cannot explain variance
4. **Dataset selection is critical** - Experiment brief specified LLM solution generation but wasn't executed
5. **Early PoC validation** - Real data experiment confirmed mismatch before extensive development

### Alternative Approaches

1. Generate diverse LLM solutions (CodeLlama/StarCoder/DeepSeek) - 5-10 solutions per task
2. Use different dataset with multiple human/LLM solutions per task
3. Reformulate hypothesis to focus on test-level variation (compatible with CoverageEval)

## Cascade Effects

4 dependent hypotheses marked CASCADE_FAILED:
- h-m1: MECHANISM (defensive programming patterns)
- h-m2: MECHANISM (test suite shallowness)
- h-m3: MECHANISM (complexity-coverage correlation)
- h-m4: MECHANISM (coverage predictor stability)

## Files Generated

- `04_validation.md` - Comprehensive validation report
- `reflection_report.md` - Step 6b reflection analysis
- `code/` - 7 Python modules (2,327 lines)
- Serena Memory: `failure_h-e1_run4.md`

## Next Steps

**Phase 0 Entry:**
1. Load Serena Memory: `failure_h-e1_run4.md`
2. Brainstorm alternative formulations or datasets
3. Refine research question (code diversity vs test diversity)
4. Design validation: ensure dataset matches hypothesis requirements

---

*Per-hypothesis snapshot for Phase 2A reference*
*Phase 4 completed: 2026-03-18T16:28:49Z*
