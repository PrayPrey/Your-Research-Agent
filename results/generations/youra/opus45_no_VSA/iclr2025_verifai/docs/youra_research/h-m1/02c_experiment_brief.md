# Experiment Design: H-M1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** ΔPass₁₂(cascade) > ΔPass₁₂(reverse) — larger early iteration gains in static-first condition (p<0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests WHY the effect exists by analyzing iteration trajectory signatures.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 VALIDATED (29.02% improvement, 95% CI LB 15.74%)
**Gate Status:** SHOULD_WORK (failure does not block pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (MUST_WORK, satisfied)

### Gate Condition
SHOULD_WORK: If ΔPass₁₂ analysis fails, the main existence effect (h-e1) still stands, but we lose mechanistic understanding of the scaffolding claim.

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
**Source:** h-e1/04_validation.md

| Metric | Result |
|--------|--------|
| Relative Improvement | 29.02% (target: ≥15%) |
| 95% CI Lower Bound | 15.74% (target: >10%) |
| McNemar p-value | 6.31×10⁻⁶ (significant) |
| pass@1 (static→exec) | 55.57% |
| pass@1 (exec→static) | 43.07% |

**Key Finding:** Static-first ordering significantly outperforms reverse ordering.

**Available Data:** h-e1 iteration logs at `h-e1/code/results/h-e1_iteration_logs.jsonl`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "iterative repair trajectory analysis LLM"**
- Limited direct matches (similarity 0.38)
- Related: diffusion trajectory analysis (TCD, arxiv:2402.19159)
- Key insight: Per-step analysis common in iterative refinement research

**Query 2: "per-iteration metrics code generation"**
- Found: FID metrics configuration for generation evaluation
- Pattern: Per-step metrics tracking in training loops

### Archon Code Examples

- FID metrics configuration showing per-step evaluation patterns
- Event tracking patterns for iteration-level logging

### Exa GitHub Implementations

**Repository 1**: FeedbackEval (arxiv:2504.06939)
- **URL**: https://doi.org/10.48550/arxiv.2504.06939
- **Relevance**: Defines Repair@k metric for iterative repair evaluation
- **Key Insight**: "Most LLMs exhibit sharp performance gains between repair@1 and repair@2"
- **Metric**: Repair@k measures pass rate after k iterations

**Repository 2**: "Is Three the Magic Number?" (arxiv:2607.05197)
- **URL**: https://arxiv.org/html/2607.05197
- **Relevance**: Per-iteration evaluation with full test suite at every step
- **Key Finding**: Mean relative improvement table shows step 1 has 266.7% gain, step 2 has 92.2%, step 3 drops to 11.5%
- **Direct Quote**: "the largest relative improvement occurs at step 1 and that by step 3 the marginal gains have dropped to single digit percentages"

**Repository 3**: Johin2/iterative-code-repair
- **URL**: https://github.com/Johin2/iterative-code-repair
- **Relevance**: Implementation of iterative self-repair with per-round tracking
- **Key Code**: `run_experiment.py`, `analyze_results.py` for trajectory analysis
- **Finding**: "Most gains come early. The first two repair rounds capture 76 to 95% of total improvement"

**Repository 4**: arxiv:2604.10508
- **URL**: https://arxiv.org/pdf/2604.10508
- **Metric**: "cumulative pass@1 at each round Ri" and "self-repair gain Δ"
- **Key**: Per-iteration tracking with greedy decoding

### 🎯 Implementation Priority Assessment

**CRITICAL: h-m1 is an ANALYSIS hypothesis — no new implementation needed**

This hypothesis analyzes existing h-e1 iteration logs, not a new training experiment.

**Recommended Implementation Path:**
- Primary: Post-hoc analysis of h-e1/code/results/h-e1_iteration_logs.jsonl
- Fallback: None needed (data already exists)
- Justification: h-m1 computes trajectory metrics from h-e1's repair iteration data

### Code Analysis (Serena MCP)

Not applicable — h-m1 is a statistical analysis of existing logs, not new model implementation.

---

## Experiment Specification

### Dataset

**Source:** Reuse h-e1 iteration logs (no new API calls needed)

**Dataset**: h-e1 Repair Iteration Logs
**Type**: programmatic-api (pre-computed from h-e1)
**Location**: `h-e1/code/results/h-e1_iteration_logs.jsonl`

**Statistics**:
- 664 problems (HumanEval 164 + MBPP 500)
- 2 conditions (static→exec, exec→static)
- 3 iterations per problem per condition
- Total: 664 × 2 × 3 = 3,984 iteration records

**Loading Information**:
- Method: JSONL file read
- Identifier: `h-e1_iteration_logs.jsonl`
- Code:
```python
import json
logs = [json.loads(line) for line in open("h-e1_iteration_logs.jsonl")]
```

### Models

#### Baseline Model

Not applicable — h-m1 analyzes logs, not models.

**Loading Information**:
- Method: N/A (analysis only)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical analysis pipeline

**Core Mechanism Implementation:**

```python
# Core Mechanism: ΔPass₁₂ Trajectory Analysis
# Based on: FeedbackEval (arxiv:2504.06939), "Is Three the Magic Number?" (arxiv:2607.05197)

def compute_delta_pass_12(logs: List[Dict], condition: str) -> Dict:
    """
    Compute pass@1 improvement from iteration 1 to iteration 2.
    
    Args:
        logs: List of {problem_id, condition, iteration, passed} records
        condition: "static_first" or "exec_first"
    
    Returns:
        {delta_pass_12, pass_at_iter_1, pass_at_iter_2, problem_ids}
    """
    condition_logs = [l for l in logs if l["condition"] == condition]
    problems = set(l["problem_id"] for l in condition_logs)
    
    # Count problems solved at each iteration
    solved_by_iter = {1: set(), 2: set(), 3: set()}
    for log in condition_logs:
        if log["passed"]:
            solved_by_iter[log["iteration"]].add(log["problem_id"])
    
    # Cumulative pass@1 at each iteration
    cumulative = {
        1: len(solved_by_iter[1]),
        2: len(solved_by_iter[1] | solved_by_iter[2]),
        3: len(solved_by_iter[1] | solved_by_iter[2] | solved_by_iter[3])
    }
    
    n = len(problems)
    pass_at_1 = cumulative[1] / n
    pass_at_2 = cumulative[2] / n
    
    # ΔPass₁₂ = improvement from iter 1 to iter 2
    delta_pass_12 = pass_at_2 - pass_at_1
    
    return {
        "delta_pass_12": delta_pass_12,
        "pass_at_iter_1": pass_at_1,
        "pass_at_iter_2": pass_at_2,
        "n_problems": n,
        "newly_solved_iter_2": solved_by_iter[2] - solved_by_iter[1]
    }

def compare_conditions(logs: List[Dict]) -> Dict:
    """Compare ΔPass₁₂ between static-first and exec-first conditions."""
    static_first = compute_delta_pass_12(logs, "static_first")
    exec_first = compute_delta_pass_12(logs, "exec_first")
    
    delta_diff = static_first["delta_pass_12"] - exec_first["delta_pass_12"]
    
    return {
        "static_first": static_first,
        "exec_first": exec_first,
        "delta_diff": delta_diff,
        "hypothesis_supported": delta_diff > 0
    }
```

### Training Protocol

**Not applicable** — h-m1 is post-hoc analysis of h-e1 logs.

**Analysis Protocol:**
1. Load h-e1 iteration logs
2. Compute ΔPass₁₂ for static→exec condition
3. Compute ΔPass₁₂ for exec→static condition
4. Compare using McNemar's test (paired, same problems)
5. Report p-value and effect size

**Rationale:** Reuses h-e1's controlled experiment data for mechanism analysis.

### Evaluation

**Primary Metric:** ΔPass₁₂ (delta between cumulative pass@1 at iteration 2 vs iteration 1)

**Success Criteria:**
- ΔPass₁₂(static-first) > ΔPass₁₂(exec-first)
- p < 0.05 (McNemar's test on newly solved problems at iter 2)

**Metrics Loading Information**:
- Task Type: binary classification (problem solved or not per iteration)
- Library: scipy.stats (McNemar's test)
- Code:
```python
from scipy.stats import chi2_contingency
import numpy as np

def mcnemar_test(static_newly_solved: set, exec_newly_solved: set, all_problems: set):
    """
    McNemar's test for paired binary outcomes.
    Tests whether static-first solves more NEW problems at iter 2.
    """
    # Contingency table: problems newly solved at iter 2
    # Rows: static-first (solved at iter2, not iter1)
    # Cols: exec-first (solved at iter2, not iter1)
    
    both = len(static_newly_solved & exec_newly_solved)
    static_only = len(static_newly_solved - exec_newly_solved)
    exec_only = len(exec_newly_solved - static_newly_solved)
    neither = len(all_problems - static_newly_solved - exec_newly_solved)
    
    table = [[both, static_only], [exec_only, neither]]
    
    # McNemar's test (exact for small counts)
    b, c = static_only, exec_only
    if b + c < 25:
        from scipy.stats import binom
        p_value = 2 * min(binom.cdf(min(b, c), b + c, 0.5), 1 - binom.cdf(max(b, c) - 1, b + c, 0.5))
    else:
        chi2 = (abs(b - c) - 1) ** 2 / (b + c)
        from scipy.stats import chi2 as chi2_dist
        p_value = 1 - chi2_dist.cdf(chi2, df=1)
    
    return {"p_value": p_value, "static_only": b, "exec_only": c}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: ΔPass₁₂ bar chart (static-first vs exec-first) with error bars

#### Additional Figures (LLM Autonomous)
1. **Iteration Trajectory Plot**: Cumulative pass@1 vs iteration number, separate lines per condition
2. **Problem-Level Heatmap**: Which problems were solved at which iteration, by condition
3. **Early vs Late Gains**: Stacked bar showing gains at iter 1, 2, 3 per condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: TRUE — ΔPass₁₂ metric is well-defined (cumulative pass difference)
- **mechanism_isolatable**: TRUE — comparing same problems under different orderings
- **baseline_measurable**: TRUE — exec-first condition serves as baseline

### Architecture Compatibility
- **Data Format**: JSONL with {problem_id, condition, iteration, passed}
- **Requirements**: h-e1 logs must contain per-iteration pass/fail status
- **Compatibility Check**: Verify logs contain iteration field (not just final result)

### Activation Indicators
- **Log Message**: "Computing ΔPass₁₂ for {condition}: iter1={pass_1}, iter2={pass_2}, delta={delta}"
- **Tensor Shape Change**: N/A (analysis, not neural network)
- **Metric Delta Expected**: ΔPass₁₂(static-first) > ΔPass₁₂(exec-first) by >0

### Mechanism Verification Code
```python
def verify_mechanism_data(logs):
    """Verify h-e1 logs support trajectory analysis."""
    required_fields = ["problem_id", "condition", "iteration", "passed"]
    for field in required_fields:
        assert all(field in log for log in logs), f"Missing field: {field}"
    
    conditions = set(log["condition"] for log in logs)
    assert "static_first" in conditions and "exec_first" in conditions
    
    iterations = set(log["iteration"] for log in logs)
    assert iterations == {1, 2, 3}, f"Expected iterations 1,2,3, got {iterations}"
    
    print("✓ Mechanism verification: logs compatible")
```

### Success Criteria
- **Hypothesis Support Threshold**: p < 0.05
- **Hypothesis Support Metric**: ΔPass₁₂(static-first) - ΔPass₁₂(exec-first) > 0

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ΔPass₁₂(static-first) > ΔPass₁₂(exec-first)
3. p < 0.05 (McNemar's test)

---

## Appendix: Reference Implementations

### Primary Sources

1. **FeedbackEval** (arxiv:2504.06939)
   - Repair@k metric definition
   - Per-iteration pass rate measurement
   - URL: https://doi.org/10.48550/arxiv.2504.06939

2. **"Is Three the Magic Number?"** (arxiv:2607.05197)
   - Mean relative improvement per repair step table
   - Finding: Step 1→2 gains are largest
   - URL: https://arxiv.org/html/2607.05197

3. **Johin2/iterative-code-repair**
   - Implementation of iterative self-repair tracking
   - analyze_results.py for trajectory visualization
   - URL: https://github.com/Johin2/iterative-code-repair

4. **Self-repair gain Δ metric** (arxiv:2604.10508)
   - Cumulative pass@1 at each round definition
   - URL: https://arxiv.org/pdf/2604.10508

### Related Work
- ReflexiCoder: Trajectory reward for iterative improvement
- CYCLE: Phase-III self-refinement as iterative programming
- CoCoGen/ProCoder: Iterative refinement with compiler feedback

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09T20:15:00+09:00

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- Prerequisite h-e1 validated (PASS)
- Experiment brief generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
