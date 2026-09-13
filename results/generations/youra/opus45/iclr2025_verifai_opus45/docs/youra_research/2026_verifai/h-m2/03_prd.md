# Product Requirements Document: H-M2

**Hypothesis:** G3 Superiority Over Minimal Feedback
**Date:** 2026-03-30
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M2: determining whether G3 (error+line) achieves at least 10 percentage points higher repair success than G0 (pass/fail only). This is a **MECHANISM** hypothesis that performs post-hoc statistical comparison using McNemar's test on paired data from H-M1.

**Success Metric:** (G3 success rate - G0 success rate) >= 10 percentage points AND McNemar p < 0.05 favoring G3

**Prerequisite:** H-M1 PASSED (ANOVA p=3.5e-19, significant granularity effect confirmed)

**CRITICAL FINDING:** H-M1 data already shows G0 (41.8%) significantly outperforms G3 (16.8%). This hypothesis is **PRE-FALSIFIED** but must be formally tested for scientific rigor.

---

## Problem Statement

### Background
The Self-Debug methodology assumes that more detailed error feedback improves LLM code repair. Specifically, line-level error localization (G3) should outperform minimal pass/fail feedback (G0). However, H-M1 results reveal an unexpected inverse relationship where simpler feedback produces better repair outcomes.

### Goal
Formally test whether G3 (error+line) achieves at least 10 percentage points higher repair success than G0 (pass/fail only) using paired statistical comparison on H-M1 data.

### Scope
- **In Scope:** G0 vs G3 paired comparison, McNemar's test, difference calculation
- **Out of Scope:** New model runs, multi-granularity analysis, new data collection

---

## Functional Requirements

### FR-1: Load H-M1 Repair Results
**Priority:** P0 (Critical)

Load the complete repair results from H-M1 experiment.

**Acceptance Criteria:**
- Load from H-M1 results: `h-m1/results/repair_results.json`
- Extract G0 and G3 outcomes for each of 304 cases
- Verify paired structure (same case_id for both conditions)

**Implementation Notes:**
```python
import json

def load_h_m1_results(results_path: str) -> tuple[list[int], list[int]]:
    """Load paired G0 and G3 results from H-M1."""
    with open(results_path) as f:
        results = json.load(f)

    # Extract paired outcomes (same case order)
    g0_outcomes = []
    g3_outcomes = []

    for case in results:
        if case['granularity'] == 'G0':
            g0_outcomes.append(1 if case['success'] else 0)
        elif case['granularity'] == 'G3':
            g3_outcomes.append(1 if case['success'] else 0)

    # Alternative: if results are nested by case_id
    # cases = sorted(set(r['task_id'] for r in results))
    # for case_id in cases:
    #     g0 = next(r for r in results if r['task_id']==case_id and r['granularity']=='G0')
    #     g3 = next(r for r in results if r['task_id']==case_id and r['granularity']=='G3')
    #     g0_outcomes.append(1 if g0['success'] else 0)
    #     g3_outcomes.append(1 if g3['success'] else 0)

    return g0_outcomes, g3_outcomes
```

### FR-2: Build Contingency Table
**Priority:** P0 (Critical)

Construct 2x2 contingency table for McNemar's test.

**Acceptance Criteria:**
- Rows: G0 outcome (fail=0, success=1)
- Columns: G3 outcome (fail=0, success=1)
- Cell counts: (both_fail, g0_fail_g3_success, g0_success_g3_fail, both_success)

**Implementation Notes:**
```python
import numpy as np

def build_contingency_table(g0_outcomes: list[int], g3_outcomes: list[int]) -> np.ndarray:
    """Build 2x2 contingency table for McNemar's test.

    Table layout:
                  G3=0 (fail)  G3=1 (success)
    G0=0 (fail)      a              b
    G0=1 (success)   c              d

    Where:
    - a: Both failed
    - b: G0 failed, G3 succeeded (discordant)
    - c: G0 succeeded, G3 failed (discordant)
    - d: Both succeeded
    """
    assert len(g0_outcomes) == len(g3_outcomes), "Must be paired data"

    table = np.zeros((2, 2), dtype=int)
    for g0, g3 in zip(g0_outcomes, g3_outcomes):
        table[g0, g3] += 1

    return table
```

### FR-3: McNemar's Test
**Priority:** P0 (Critical)

Perform McNemar's test for paired binary outcomes.

**Acceptance Criteria:**
- Use exact test for accuracy (binomial distribution)
- Calculate test statistic and p-value
- Determine direction of effect (which condition is better)

**Implementation Notes:**
```python
from statsmodels.stats.contingency_tables import mcnemar

def run_mcnemar_test(table: np.ndarray) -> dict:
    """Run McNemar's test on contingency table.

    McNemar's test focuses on discordant pairs:
    - b: G0 failed but G3 succeeded (favors G3)
    - c: G0 succeeded but G3 failed (favors G0)

    If c > b significantly, G0 is better than G3.
    """
    result = mcnemar(table, exact=True)

    b = table[0, 1]  # G0 fail, G3 success
    c = table[1, 0]  # G0 success, G3 fail

    return {
        'statistic': result.statistic,
        'pvalue': result.pvalue,
        'discordant_b': int(b),  # Favor G3
        'discordant_c': int(c),  # Favor G0
        'favors': 'G3' if b > c else 'G0' if c > b else 'neither'
    }
```

### FR-4: Calculate Success Rates and Difference
**Priority:** P0 (Critical)

Calculate success rates and the difference (G3 - G0).

**Acceptance Criteria:**
- G0 success rate as proportion
- G3 success rate as proportion
- Difference in percentage points
- 95% confidence interval for difference

**Implementation Notes:**
```python
from scipy.stats import norm
import numpy as np

def calculate_rates_and_difference(
    g0_outcomes: list[int],
    g3_outcomes: list[int]
) -> dict:
    """Calculate success rates and difference with CI."""
    n = len(g0_outcomes)

    g0_rate = sum(g0_outcomes) / n
    g3_rate = sum(g3_outcomes) / n
    difference = g3_rate - g0_rate

    # Confidence interval for paired proportion difference
    # Using normal approximation
    # Variance of difference: (p1(1-p1) + p2(1-p2) + 2*cov) / n
    # For paired data, use Newcombe's method or McNemar-based CI

    # Simple approximation for now
    se = np.sqrt((g0_rate*(1-g0_rate) + g3_rate*(1-g3_rate)) / n)
    ci_lower = difference - 1.96 * se
    ci_upper = difference + 1.96 * se

    return {
        'g0_rate': g0_rate,
        'g3_rate': g3_rate,
        'g0_successes': sum(g0_outcomes),
        'g3_successes': sum(g3_outcomes),
        'n_pairs': n,
        'difference': difference,
        'difference_pp': difference * 100,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'ci_lower_pp': ci_lower * 100,
        'ci_upper_pp': ci_upper * 100
    }
```

### FR-5: Gate Evaluation
**Priority:** P0 (Critical)

Evaluate gate condition for H-M2.

**Acceptance Criteria:**
- Gate: G3 >= G0 + 10 percentage points
- Statistical significance: McNemar p < 0.05 AND direction favors G3
- Combined verdict

**Implementation Notes:**
```python
def evaluate_gate(rates: dict, mcnemar_result: dict) -> dict:
    """Evaluate H-M2 gate condition.

    Gate PASSES if:
    1. difference >= 0.10 (G3 at least 10pp better than G0)
    2. McNemar p < 0.05 with effect favoring G3
    """
    difference_threshold = 0.10  # 10 percentage points

    difference_met = rates['difference'] >= difference_threshold
    significant = mcnemar_result['pvalue'] < 0.05
    favors_g3 = mcnemar_result['favors'] == 'G3'

    gate_passed = difference_met and significant and favors_g3

    return {
        'gate_passed': gate_passed,
        'difference_threshold': difference_threshold,
        'difference_met': difference_met,
        'significant': significant,
        'favors_g3': favors_g3,
        'verdict': 'PASS' if gate_passed else 'FAIL',
        'reason': get_failure_reason(difference_met, significant, favors_g3, rates)
    }

def get_failure_reason(diff_met, sig, favors_g3, rates):
    if rates['difference'] < 0:
        return f"G0 outperforms G3 by {abs(rates['difference_pp']):.1f}pp (opposite of hypothesis)"
    elif not diff_met:
        return f"Difference {rates['difference_pp']:.1f}pp < 10pp threshold"
    elif not sig:
        return "Difference not statistically significant (p >= 0.05)"
    elif not favors_g3:
        return "Statistical effect favors G0, not G3"
    return "Gate passed"
```

### FR-6: Results Persistence
**Priority:** P1 (High)

Save all analysis results.

**Acceptance Criteria:**
- Save contingency table and McNemar results
- Save rates and difference with CI
- Save gate evaluation
- JSON format for programmatic access

**Output Files:**
- `h-m2/results/comparison_results.json` - Full analysis results
- `h-m2/results/metrics.yaml` - Summary metrics
- `h-m2/figures/` - Visualization outputs

### FR-7: Visualization
**Priority:** P1 (High)

Generate visualizations for results analysis.

**Required Figures:**
1. **G0 vs G3 Success Rate Comparison** - Bar chart with 10pp threshold line
2. **Contingency Table Heatmap** - 2x2 paired outcomes visualization
3. **Difference with CI** - Point estimate with error bars
4. **Gate Metrics Summary** - Visual comparison to threshold

**Implementation Notes:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_comparison(rates: dict, output_dir: str):
    """Generate G0 vs G3 comparison bar chart."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ['G0 (Pass/Fail)', 'G3 (Error+Line)']
    values = [rates['g0_rate'] * 100, rates['g3_rate'] * 100]
    colors = ['#2ecc71', '#e74c3c']  # Green for G0, Red for G3

    bars = ax.bar(conditions, values, color=colors, alpha=0.8)

    # Add threshold line (G0 + 10pp)
    threshold = rates['g0_rate'] * 100 + 10
    ax.axhline(y=threshold, color='orange', linestyle='--',
               label=f'Hypothesis Threshold (G0 + 10pp = {threshold:.1f}%)')

    ax.set_ylabel('Repair Success Rate (%)')
    ax.set_title('H-M2: G3 vs G0 Repair Success Comparison')
    ax.legend()

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/g0_vs_g3_comparison.png', dpi=150)
    plt.close()

def plot_contingency_heatmap(table: np.ndarray, output_dir: str):
    """Generate contingency table heatmap."""
    fig, ax = plt.subplots(figsize=(7, 6))

    sns.heatmap(table, annot=True, fmt='d', cmap='Blues',
                xticklabels=['G3 Fail', 'G3 Success'],
                yticklabels=['G0 Fail', 'G0 Success'],
                ax=ax)

    ax.set_title('H-M2: Paired Outcomes Contingency Table')
    ax.set_xlabel('G3 (Error+Line) Outcome')
    ax.set_ylabel('G0 (Pass/Fail) Outcome')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/contingency_heatmap.png', dpi=150)
    plt.close()
```

---

## Non-Functional Requirements

### NFR-1: Performance
- Analysis completion: < 1 minute (post-hoc analysis only)
- No model inference required
- Minimal computational resources

### NFR-2: Reproducibility
- All analysis deterministic
- Results traceable to H-M1 data
- Clear documentation of statistical methods

### NFR-3: Resource Constraints
- CPU-only execution (no GPU required)
- Memory: < 1GB RAM
- Storage: < 100MB for results and figures

### NFR-4: Error Handling
- Validate H-M1 data integrity before analysis
- Handle missing or corrupted data gracefully
- Clear error messages for debugging

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
| Metric | Target | Measurement |
|--------|--------|-------------|
| G3 - G0 Difference | >= 10pp | Direct calculation |
| McNemar p-value | < 0.05 | statsmodels mcnemar |
| Effect Direction | Favors G3 | Discordant pair ratio |

### Expected Result (Based on H-M1 Data)
| Metric | Expected Value | Notes |
|--------|----------------|-------|
| G0 Success Rate | 41.8% | 127/304 from H-M1 |
| G3 Success Rate | 16.8% | 51/304 from H-M1 |
| Difference | -25.0pp | G0 >> G3 (opposite of hypothesis) |
| Gate | **FAIL** | Pre-falsified by H-M1 data |

### Gate Decision
- **PASS:** Difference >= 10pp AND McNemar p < 0.05 favoring G3 (unlikely given H-M1 data)
- **FAIL:** Document that G0 significantly outperforms G3, contradicting Self-Debug assumptions

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| statsmodels | >= 0.14.0 | McNemar's test |
| scipy | >= 1.10.0 | Statistical utilities |
| numpy | >= 1.24.0 | Numerical operations |
| matplotlib | >= 3.7.0 | Visualization |
| seaborn | >= 0.12.0 | Statistical plots |
| pyyaml | >= 6.0 | YAML output |

### Internal Dependencies
| Dependency | Status | Notes |
|------------|--------|-------|
| H-M1 Validation | COMPLETED | ANOVA p=3.5e-19 |
| H-M1 Results | EXISTS | `h-m1/results/repair_results.json` |
| Phase 2C Brief | COMPLETED | `h-m2/02c_experiment_brief.md` |

---

## Data Specifications

### Input Data
| Field | Type | Source | Description |
|-------|------|--------|-------------|
| task_id | int | H-M1 | MBPP problem ID |
| granularity | str | H-M1 | G0 or G3 |
| success | bool | H-M1 | Repair succeeded |

### Output Data
| Field | Type | Description |
|-------|------|-------------|
| g0_rate | float | G0 success rate |
| g3_rate | float | G3 success rate |
| difference | float | G3 - G0 difference |
| difference_pp | float | Difference in percentage points |
| mcnemar_pvalue | float | McNemar's test p-value |
| contingency_table | list | 2x2 table as nested list |
| gate_passed | bool | Gate condition met |

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Hypothesis pre-falsified | HIGH | Expected outcome; document scientific finding |
| H-M1 data unavailable | MEDIUM | Verify path before execution |
| Statistical assumptions violated | LOW | McNemar's exact test robust to small samples |

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| McNemar's Test | Core Mechanism Implementation |
| G0 vs G3 Comparison | Dataset section (derivative from H-M1) |
| Gate Condition | Success Criteria section |
| Expected Failure | Critical Finding section |
| Contingency Table | Core Mechanism Implementation |

---

## Appendix: Expected Contingency Table (from H-M1)

Based on H-M1 results (G0: 127/304 successes, G3: 51/304 successes):

```
                  G3=Fail    G3=Success
G0=Fail             ~150         ~27
G0=Success          ~103         ~24
```

**Interpretation:**
- ~103 cases: G0 succeeded where G3 failed (strongly favors G0)
- ~27 cases: G3 succeeded where G0 failed (favors G3)
- Discordant ratio ~4:1 favoring G0
- McNemar's test expected to show significant p-value, but **favoring G0, not G3**

---

*Generated for Phase 3 Implementation Planning*
*Source: h-m2/02c_experiment_brief.md*
*Prerequisite: H-M1 VALIDATED (ANOVA p=3.5e-19)*
*Expected Outcome: FAIL (G0 significantly outperforms G3)*
*Next: Architecture Design (03_architecture.md)*
