# Experiment Design: h-m2

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse) — fewer test regressions in static-first condition (p<0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Analyzing WHY the primary effect (h-e1) occurs via regression rate analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (h-e1 VALIDATED)
**Gate Status:** SHOULD_WORK (null → pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (completed, PASS)

### Gate Condition
**SHOULD_WORK Gate:** If PASS, supports scaffolding mechanism theory. If FAIL, effect exists but mechanism explanation needs revision.

---

## Continuation Context

This is a **secondary analysis** of h-e1 experiment logs. No new API calls or experiments needed — only log analysis to compute regression metrics.

### Previous Hypothesis Results (h-e1)

| Metric | Result |
|--------|--------|
| Relative Improvement | 29.02% (target ≥15%) |
| 95% CI Lower Bound | 15.74% (target >10%) |
| McNemar p-value | 6.31e-06 |
| Verdict | **PASS** (MUST_WORK satisfied) |

**Data Source:** `h-e1/code/results/h-e1_iteration_logs.jsonl`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Test regression analysis code repair iteration**
- Results focused on diffusers/ControlNet (low relevance)
- No direct code repair regression analysis found

**Query 2: LLM iterative debugging metrics evaluation**
- Found paper reference (arXiv 2305.14314) on LLM debugging
- Evaluation metrics discussion available

**Key Insight:** Archon KB has limited code repair regression content. Primary sources from Exa.

### Archon Code Examples

**Query: pass@k metrics code evaluation Python**
- FID/PPL metric configuration examples (image generation focused)
- Model checkpoint loading patterns

**Key Insight:** General metric configuration patterns available; specific code repair metrics require custom implementation.

### Exa GitHub Implementations

**Repository 1**: [Johin2/iterative-code-repair](https://github.com/Johin2/iterative-code-repair)
- **Relevance**: Direct implementation of iterative self-repair on HumanEval/MBPP
- **Architecture**: Multi-round repair loop (R0→R4)
- **Key Finding**: "Most gains come early" — first two repair rounds capture 76-95% of total improvement
- **Data Structure**: Per-problem logs with iteration outcomes

**Repository 2**: [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels)
- **Relevance**: McNemar test implementation for paired comparisons
- **Code**: `statsmodels.stats.contingency_tables.mcnemar(table, exact=True)`
- **Key Insight**: Use exact=True for small samples, chi-squared for large

**Paper**: "How Many Tries Does It Take? Iterative Self-Repair in LLM Code Generation" (arXiv 2604.10508)
- **Protocol**: Feed execution errors back to model for correction
- **Metrics**: Cumulative pass@1 at each round, self-repair gain (Δ)
- **Relevance**: Validates iteration log structure for regression analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a LOG ANALYSIS experiment, not a new model training**

**Recommended Implementation Path:**
- Primary: Analyze h-e1 iteration logs (`h-e1_iteration_logs.jsonl`)
- Fallback: Re-run h-e1 experiment if logs incomplete
- Justification: h-m2 extracts secondary metrics from existing data

### Code Analysis (Serena MCP)

**Serena Analysis:** Not required — this is a statistical analysis task, not complex architecture implementation.

---

## Experiment Specification

### Dataset

**Dataset:** h-e1 Iteration Logs (derived from HumanEval + MBPP)
**Type:** `programmatic-api` (JSON log files)

**Statistics:**
- Total problems: 664 (HumanEval 164 + MBPP 500)
- Iterations per problem: 3
- Conditions: 2 (static→exec, exec→static)
- Total log entries: ~3,984 iteration outcomes

**Loading Information** (for Phase 4 download):
- Method: Local file
- Identifier: `h-e1/code/results/h-e1_iteration_logs.jsonl`
- Code:
```python
import json
with open("../h-e1/code/results/h-e1_iteration_logs.jsonl") as f:
    logs = [json.loads(line) for line in f]
```

### Models

#### Baseline Model

**This experiment has no model training** — it analyzes existing experiment logs.

**Loading Information** (for Phase 4 download):
- Method: N/A (log analysis only)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical analysis pipeline (not a neural network)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Regression Rate Computation
# Based on: Iterative code repair protocol (arXiv 2604.10508)

def compute_regression_rate(iteration_logs, condition):
    """
    Calculate Regression Rate₁₂ for a given feedback ordering condition.
    
    Regression Rate₁₂ = (# tests passed at iter 1 but failed at iter 2) / (# tests passed at iter 1)
    
    Args:
        iteration_logs: List[dict] - Per-problem iteration outcomes
        condition: str - "static_first" or "exec_first"
    
    Returns:
        float - Regression rate between 0 and 1
    """
    passed_at_1 = 0
    regressed_at_2 = 0
    
    for log in iteration_logs:
        if log["condition"] != condition:
            continue
        
        # Check iteration 1 outcome
        if log["iteration_1"]["passed"]:
            passed_at_1 += 1
            # Check if regressed at iteration 2
            if not log["iteration_2"]["passed"]:
                regressed_at_2 += 1
    
    if passed_at_1 == 0:
        return 0.0
    
    return regressed_at_2 / passed_at_1

# Statistical comparison using McNemar's test
from statsmodels.stats.contingency_tables import mcnemar

def compare_regression_rates(logs):
    """Compare regression rates between conditions using McNemar's test."""
    # Build 2x2 contingency table of regressions
    # Rows: cascade (static→exec), Columns: reverse (exec→static)
    table = build_regression_contingency_table(logs)
    result = mcnemar(table, exact=True)
    return result.statistic, result.pvalue
```

### Training Protocol

**Training:** Not applicable — this is a statistical analysis experiment.

**Analysis Protocol:**
1. Load h-e1 iteration logs
2. Filter by condition (static→exec vs exec→static)
3. Compute Regression Rate₁₂ for each condition
4. Build 2×2 contingency table (regressed vs not-regressed × condition)
5. Run McNemar's test for statistical significance

**Computational Requirements:**
- CPU only (no GPU needed)
- Runtime: <1 minute
- Memory: <1 GB

### Evaluation

**Primary Metric:** Regression Rate₁₂
- Definition: (# problems passed at iter 1 but failed at iter 2) / (# problems passed at iter 1)
- Lower is better (fewer regressions = more stable fixes)

**Statistical Test:** McNemar's Test
- Null hypothesis: No difference in regression rates between conditions
- Alternative: Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
- Use exact test (exact=True) if discordant pairs < 25

**Success Criteria:**
- Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
- p < 0.05

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical comparison
- Library: statsmodels
- Code:
```python
from statsmodels.stats.contingency_tables import mcnemar
result = mcnemar(table, exact=True)
print(f"p-value: {result.pvalue}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Regression Rate₁₂ for cascade vs reverse conditions (bar chart)

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (MECHANISM), recommended visualizations:
1. **Regression Rate Comparison Bar Chart**: Side-by-side bars for cascade vs reverse
2. **Per-Iteration Pass Rate Trajectory**: Line plot showing pass rates across iterations 0→1→2→3 for both conditions
3. **Contingency Table Heatmap**: Visual representation of the 2×2 McNemar table

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: YES — Regression analysis is computable from iteration logs
- `mechanism_isolatable`: YES — Each condition's regression rate computed independently
- `baseline_measurable`: YES — Both conditions use same log structure

### Architecture Compatibility
- `architecture_compatibility`: PASS — Log analysis only, no neural network constraints

### Activation Indicators
- `mechanism_log_message`: "Regression Rate₁₂ computed: cascade={x:.4f}, reverse={y:.4f}"
- `tensor_shape_change`: N/A (not a tensor operation)
- `metric_delta_expected`: Expect cascade regression rate < reverse regression rate

### Mechanism Verification Code
```python
def verify_mechanism_h_m2(cascade_rate, reverse_rate, p_value):
    """Verify h-m2 mechanism hypothesis."""
    print(f"[MECHANISM CHECK] Regression Rate₁₂ computed")
    print(f"  Cascade (static→exec): {cascade_rate:.4f}")
    print(f"  Reverse (exec→static): {reverse_rate:.4f}")
    print(f"  Difference: {reverse_rate - cascade_rate:.4f}")
    print(f"  McNemar p-value: {p_value:.6f}")
    
    mechanism_active = cascade_rate < reverse_rate
    statistically_significant = p_value < 0.05
    
    if mechanism_active and statistically_significant:
        print("[PASS] h-m2 MECHANISM hypothesis SUPPORTED")
        return "PASS"
    elif mechanism_active:
        print("[PARTIAL] Direction correct but not significant")
        return "PARTIAL"
    else:
        print("[FAIL] Cascade regression rate >= reverse")
        return "FAIL"
```

### Success Thresholds
- `hypothesis_support_threshold`: p < 0.05
- `hypothesis_support_metric`: Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Regression Rate₁₂(cascade) < Regression Rate₁₂(reverse)
3. McNemar p-value < 0.05

---

## Appendix: Reference Implementations

### Statistical Testing
- **statsmodels McNemar**: [statsmodels.stats.contingency_tables.mcnemar](https://www.statsmodels.org/devel/generated/statsmodels.stats.contingency_tables.mcnemar.html)
- **McNemar mid-p**: [kakumarabhishek/McNemar-mid-p](https://github.com/kakumarabhishek/McNemar-mid-p)

### Iterative Code Repair
- **Iterative Self-Repair**: [Johin2/iterative-code-repair](https://github.com/Johin2/iterative-code-repair)
- **Paper**: "How Many Tries Does It Take?" (arXiv 2604.10508)

### MBPP/HumanEval Evaluation
- **Inspect Evals MBPP**: [UKGovernmentBEIS/inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mbpp)
- **MGDebugger**: "From Code to Correctness" (arXiv 2410.01215v4)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- 2026-08-09: Phase 2C experiment design started
- Prerequisites: h-e1 PASS (MUST_WORK gate satisfied)
- Status: experiment_design IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
