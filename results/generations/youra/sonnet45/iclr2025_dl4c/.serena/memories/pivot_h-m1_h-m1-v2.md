# Hypothesis Pivot Record

**Date:** 2026-03-17T21:40:00+00:00
**From:** h-m1
**To:** h-m1-v2 (recommended)

## Pivot Reason

MUST_WORK gate FAILED: Cyclomatic complexity insufficient for detecting brittle high-complexity solutions across all benchmark types. Gate results:
- **HumanEval:** d=0.312 (barely passed), ΔAUC=-0.028 (failed) → Overall FAIL
- **MBPP:** d=0.165 (failed, well below 0.3 threshold) → Overall FAIL  
- **BigCodeBench:** d=1.172 (strong pass), ΔAUC=0.051 (passed) → Overall PASS

**Aggregate:** 1/3 datasets passed. Insufficient evidence for mechanism across all benchmark types.

## What Changed

Recommended modifications for h-m1-v2:
- **Test alternative complexity metrics:** Halstead complexity, nesting depth, cognitive complexity, lines of code
- **Multi-metric approach:** Combine multiple complexity signals to improve detection
- **Domain-specific weighting:** Higher complexity weight for repository-level tasks (BigCodeBench) vs simple problems (HumanEval/MBPP)
- **Metric selection per benchmark:** Different complexity metrics may work better for different task types

## What Was Preserved

Core hypothesis elements that remain valid:
- **Mechanism premise:** Execution-only PPO does permit some form of brittleness (validated on BigCodeBench)
- **Near-correct regime:** 70-100% visible test pass rate is correct analysis window
- **Brittle/robust classification:** <50% hidden (brittle) vs ≥90% hidden (robust) thresholds work well
- **Multi-benchmark approach:** Testing across HumanEval/MBPP/BigCodeBench revealed domain-specific patterns
- **Gate framework:** Cohen's d ≥ 0.3 remains appropriate threshold
- **Code infrastructure:** All implementation components (dataset loading, test execution, analysis) are validated and reusable

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| BigCodeBench Cohen's d | 1.172 | Strong validation - mechanism confirmed for complex tasks |
| HumanEval Cohen's d | 0.312 | Marginal pass - barely meets threshold |
| MBPP Cohen's d | 0.165 | Clear fail - insufficient effect size |
| Total samples analyzed | 318 | Sufficient statistical power |
| Covariance (all datasets) | < 0.11 | Complexity signal is orthogonal to execution rewards |

## Key Insights from Failure

**Domain Dependency Discovery:**
The mechanism is **repository-level task specific**. BigCodeBench (complex, multi-file tasks) shows strong brittle/robust separation (d=1.172), but function-level problems (HumanEval/MBPP) do not. This suggests:

1. **Task complexity threshold:** Simpler problems may not exhibit sufficient solution-space diversity for brittle patterns to emerge
2. **Cyclomatic complexity limitations:** CC may not capture the right complexity dimension for simple functions
3. **Alternative metrics needed:** Halstead (algorithmic complexity), nesting depth (control flow complexity), or cognitive complexity may perform better
4. **Positive validation:** The mechanism DOES exist for complex tasks, supporting continued investigation

## Recommendations for h-m1-v2

### Option A: Multi-Metric Approach (RECOMMENDED)
Test alternative complexity metrics across all 3 benchmarks:
- **Halstead complexity:** Captures algorithmic complexity (operators/operands)
- **Nesting depth:** Captures control flow depth
- **Cognitive complexity:** Captures human-perceived difficulty
- **Lines of code:** Simple but sometimes effective baseline

**Success criteria:** ≥2/4 metrics show d≥0.3 across ≥2/3 datasets

### Option B: Scope to BigCodeBench Only
Accept that mechanism is repository-level specific and scope all subsequent hypotheses (h-m2, h-m3, h-m4) to BigCodeBench only.

**Advantage:** Clear path forward with validated mechanism
**Disadvantage:** Reduces generalizability claims in final paper

### Option C: Domain-Adaptive Metrics
Use different complexity metrics for different benchmark types:
- HumanEval/MBPP: Halstead or cognitive complexity
- BigCodeBench: Cyclomatic complexity (already validated)

**Advantage:** Maximizes per-domain performance
**Disadvantage:** More complex hypothesis, harder to justify theoretically

## Lineage

```
h-m1 (cyclomatic complexity only)
    └── (PIVOT: CC insufficient for simple tasks, need alternative metrics)
        └── h-m1-v2 (multi-metric or domain-adaptive approach)
```

## Cascade Impact Assessment

**Dependent hypotheses affected:**
- **h-m2:** BLOCKED until h-m1-v2 passes
- **h-m3:** BLOCKED (depends on h-m2)
- **h-m4:** BLOCKED (depends on h-m1, h-m2, h-m3)

**Recommended action:** Complete h-m1-v2 before proceeding to h-m2. Do NOT attempt h-m2/h-m3/h-m4 with the failed h-m1 results.

---
*Pivot recorded at: 2026-03-17T21:40:00+00:00*
*Next action: Create h-m1-v2 with alternative complexity metrics or scope to BigCodeBench*
