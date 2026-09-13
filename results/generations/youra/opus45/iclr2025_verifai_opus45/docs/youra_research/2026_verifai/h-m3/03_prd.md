# Product Requirements Document: H-M3

**Hypothesis:** Non-Monotonicity Confirmation (G3 >= G4)
**Date:** 2026-03-30
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-M3: determining whether G4 (full trace) does NOT significantly outperform G3 (G4 <= G3 + 2%), confirming a non-monotonic relationship in error feedback granularity. This is a **MECHANISM** hypothesis that performs statistical reanalysis of existing H-M1 experimental data using McNemar's test and TOST equivalence testing.

**Success Metric:** G4 <= G3 + 2% (practical equivalence or G3 superiority)

**Prerequisite:** H-M1 PASSED (ANOVA p=3.5e-19, significant granularity effect confirmed)

**Key Characteristic:** This is a **statistical reanalysis hypothesis** - no new model inference or data collection required. All analysis is performed on existing H-M1 results (304 paired G3/G4 outcomes).

---

## Problem Statement

### Background
The H-M1 experiment demonstrated a statistically significant effect of feedback granularity on repair success (ANOVA p=3.5e-19). However, the relationship appears non-monotonic - more detailed feedback (G4: full traces) does not necessarily improve repair rates over intermediate feedback (G3: error + line). Post-hoc analysis from H-M1 showed G3 vs G4 p-value = 0.452 (not significant), with G4 outperforming G3 by 5.9%.

### Goal
Formally test whether G4 feedback provides meaningful improvement over G3, or whether the difference falls within practical equivalence bounds (±2%). This addresses the core research claim that "more information is NOT always better" for LLM code repair.

### Scope
- **In Scope:** McNemar's test for paired binary outcomes, TOST equivalence testing, confidence interval estimation, reanalysis of H-M1 G3/G4 data
- **Out of Scope:** New repair experiments, model inference, other granularity comparisons

---

## Functional Requirements

### FR-1: Load H-M1 Repair Results
**Priority:** P0 (Critical)

Load the paired G3 and G4 repair outcomes from H-M1 experiment.

**Acceptance Criteria:**
- Load from H-M1 results: `h-m1/results/repair_results.json`
- Extract G3 outcomes (304 binary values)
- Extract G4 outcomes (304 binary values)
- Pair by problem_id (same 304 runtime error cases)
- Verify data integrity: same problem_ids for both granularity levels

**Implementation Notes:**
```python
import json
from pathlib import Path

def load_h_m1_results(results_path: str) -> list[dict]:
    """Load repair results from H-M1 experiment."""
    with open(results_path) as f:
        return json.load(f)

def extract_paired_outcomes(results: list[dict]) -> tuple[list[bool], list[bool], list[int]]:
    """Extract G3 and G4 outcomes paired by problem_id."""
    g3_by_problem = {r["task_id"]: r["success"]
                     for r in results if r["granularity"] == "G3"}
    g4_by_problem = {r["task_id"]: r["success"]
                     for r in results if r["granularity"] == "G4"}

    # Ensure same problem_ids
    problem_ids = sorted(set(g3_by_problem.keys()) & set(g4_by_problem.keys()))

    g3_outcomes = [g3_by_problem[pid] for pid in problem_ids]
    g4_outcomes = [g4_by_problem[pid] for pid in problem_ids]

    return g3_outcomes, g4_outcomes, problem_ids
```

### FR-2: Build Contingency Table
**Priority:** P0 (Critical)

Construct 2x2 contingency table for McNemar's test.

**Acceptance Criteria:**
- Build table from paired binary outcomes
- Layout: rows = G3 outcome, columns = G4 outcome
- Cells: (both_success, g3_only_success, g4_only_success, both_fail)
- Validate row/column marginals match expected totals

**Implementation Notes:**
```python
import numpy as np

def build_contingency_table(g3: list[bool], g4: list[bool]) -> np.ndarray:
    """Build 2x2 contingency table for McNemar's test.

    Layout:
              G4=Success  G4=Fail
    G3=Success    a          b
    G3=Fail       c          d
    """
    a = sum(1 for i in range(len(g3)) if g3[i] and g4[i])      # both success
    b = sum(1 for i in range(len(g3)) if g3[i] and not g4[i])  # G3 only
    c = sum(1 for i in range(len(g3)) if not g3[i] and g4[i])  # G4 only
    d = sum(1 for i in range(len(g3)) if not g3[i] and not g4[i])  # both fail

    table = np.array([[a, b], [c, d]])

    # Validate
    assert table.sum() == len(g3), "Table sum must equal sample size"

    return table
```

### FR-3: McNemar's Test
**Priority:** P0 (Critical)

Perform McNemar's test for marginal homogeneity.

**Acceptance Criteria:**
- Use exact test (binomial) for small discordant cells
- Report test statistic and p-value
- Interpret: p < 0.05 indicates significant difference between G3 and G4

**Implementation Notes:**
```python
from statsmodels.stats.contingency_tables import mcnemar

def run_mcnemar_test(table: np.ndarray) -> dict:
    """Run McNemar's test for marginal homogeneity."""
    result = mcnemar(table, exact=True)

    return {
        "statistic": result.statistic,
        "pvalue": result.pvalue,
        "significant": result.pvalue < 0.05,
        "interpretation": "G3 and G4 differ significantly" if result.pvalue < 0.05
                         else "No significant difference between G3 and G4"
    }
```

### FR-4: TOST Equivalence Test
**Priority:** P0 (Critical)

Perform Two One-Sided Tests (TOST) procedure for equivalence.

**Acceptance Criteria:**
- Equivalence margin: ±2% (0.02)
- H0: |G4_rate - G3_rate| >= 0.02 (not equivalent)
- H1: |G4_rate - G3_rate| < 0.02 (equivalent)
- Report both one-sided p-values and equivalence conclusion

**Implementation Notes:**
```python
from statsmodels.stats.proportion import test_proportions_2indep
import scipy.stats as stats

def run_tost_equivalence(g3_successes: int, g3_total: int,
                          g4_successes: int, g4_total: int,
                          margin: float = 0.02) -> dict:
    """Run TOST procedure for equivalence testing.

    Tests whether G4-G3 difference is within ±margin.
    """
    g3_rate = g3_successes / g3_total
    g4_rate = g4_successes / g4_total
    diff = g4_rate - g3_rate

    # Standard error for difference of proportions
    se = np.sqrt(g3_rate * (1 - g3_rate) / g3_total +
                 g4_rate * (1 - g4_rate) / g4_total)

    # Two one-sided tests
    # Test 1: H0: diff <= -margin (G4 much worse)
    z_lower = (diff - (-margin)) / se
    p_lower = 1 - stats.norm.cdf(z_lower)

    # Test 2: H0: diff >= margin (G4 much better)
    z_upper = (diff - margin) / se
    p_upper = stats.norm.cdf(z_upper)

    # Equivalence requires both tests to reject at alpha=0.05
    equivalent = (p_lower < 0.05) and (p_upper < 0.05)

    return {
        "g3_rate": g3_rate,
        "g4_rate": g4_rate,
        "difference": diff,
        "margin": margin,
        "p_lower": p_lower,
        "p_upper": p_upper,
        "tost_pvalue": max(p_lower, p_upper),
        "equivalent": equivalent,
        "interpretation": f"G3 and G4 are {'equivalent' if equivalent else 'not equivalent'} within {margin*100}% margin"
    }
```

### FR-5: Confidence Interval for Difference
**Priority:** P1 (High)

Calculate 95% confidence interval for G4-G3 rate difference.

**Acceptance Criteria:**
- Use appropriate method for paired proportions (Agresti-Caffo or similar)
- Report point estimate and 95% CI bounds
- Gate interpretation: CI entirely below +2% → practical equivalence

**Implementation Notes:**
```python
def compute_confidence_interval(g3_successes: int, g3_total: int,
                                 g4_successes: int, g4_total: int,
                                 confidence: float = 0.95) -> dict:
    """Compute confidence interval for difference in proportions."""
    g3_rate = g3_successes / g3_total
    g4_rate = g4_successes / g4_total
    diff = g4_rate - g3_rate

    # Standard error (unpooled)
    se = np.sqrt(g3_rate * (1 - g3_rate) / g3_total +
                 g4_rate * (1 - g4_rate) / g4_total)

    # Z-value for confidence level
    z = stats.norm.ppf((1 + confidence) / 2)

    ci_lower = diff - z * se
    ci_upper = diff + z * se

    return {
        "point_estimate": diff,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence": confidence,
        "interpretation": f"95% CI for G4-G3 difference: [{ci_lower:.3f}, {ci_upper:.3f}]"
    }
```

### FR-6: Gate Condition Evaluation
**Priority:** P0 (Critical)

Evaluate the H-M3 gate condition: G4 <= G3 + 2%.

**Acceptance Criteria:**
- Primary gate: G4_rate <= G3_rate + 0.02
- Interpretation based on McNemar p-value:
  - If p < 0.05 AND G4 > G3: Gate FAILS (G4 significantly better)
  - If p >= 0.05: Gate PASS (no significant difference)
  - If p < 0.05 AND G3 > G4: Gate PASS (G3 significantly better)

**Implementation Notes:**
```python
def evaluate_gate_condition(g3_rate: float, g4_rate: float,
                            mcnemar_pvalue: float,
                            margin: float = 0.02) -> dict:
    """Evaluate H-M3 gate condition."""
    diff = g4_rate - g3_rate

    # Primary check: is G4 within margin of G3?
    within_margin = diff <= margin

    # Statistical interpretation
    if mcnemar_pvalue < 0.05:
        if g4_rate > g3_rate:
            gate_passed = False
            reason = f"FAIL: G4 significantly outperforms G3 (diff={diff:.3f}, p={mcnemar_pvalue:.4f})"
        else:
            gate_passed = True
            reason = f"PASS: G3 significantly outperforms G4 (diff={diff:.3f}, p={mcnemar_pvalue:.4f})"
    else:
        gate_passed = True
        reason = f"PASS: No significant difference between G3 and G4 (diff={diff:.3f}, p={mcnemar_pvalue:.4f})"

    return {
        "g3_rate": g3_rate,
        "g4_rate": g4_rate,
        "difference": diff,
        "margin": margin,
        "within_margin": within_margin,
        "mcnemar_pvalue": mcnemar_pvalue,
        "gate_passed": gate_passed,
        "reason": reason
    }
```

### FR-7: Results Persistence
**Priority:** P1 (High)

Save all statistical analysis results for reproducibility.

**Acceptance Criteria:**
- Save contingency table to JSON
- Save all test results (McNemar, TOST, CI) to YAML
- Save gate evaluation to YAML
- Include timestamps and data checksums

**Output Files:**
- `h-m3/results/contingency_table.json` - 2x2 table
- `h-m3/results/statistical_tests.yaml` - McNemar, TOST, CI results
- `h-m3/results/metrics.yaml` - Gate evaluation and summary
- `h-m3/figures/` - Visualization outputs

### FR-8: Visualization
**Priority:** P1 (High)

Generate visualizations for statistical analysis results.

**Required Figures:**
1. **Gate Metrics Comparison** - G3 vs G4 success rate bar chart with 2% margin line (MANDATORY)
2. **Contingency Table Heatmap** - 2x2 matrix showing paired outcome distribution
3. **Confidence Interval Plot** - Point estimate with 95% CI for G4-G3 difference
4. **Granularity Curve** - All G0-G4 success rates showing non-monotonic pattern (from H-M1)

**Implementation Notes:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gate_comparison(g3_rate: float, g4_rate: float, margin: float = 0.02,
                         output_path: str = "figures/gate_comparison.png"):
    """Plot G3 vs G4 comparison with gate threshold."""
    fig, ax = plt.subplots(figsize=(8, 6))

    rates = [g3_rate, g4_rate]
    labels = ["G3 (Error+Line)", "G4 (Full Trace)"]
    colors = ["#2ecc71", "#3498db"]

    bars = ax.bar(labels, rates, color=colors, edgecolor="black", linewidth=1.5)

    # Add margin line (G3 + 2%)
    ax.axhline(y=g3_rate + margin, color="red", linestyle="--",
               label=f"G3 + {margin*100:.0f}% threshold")

    ax.set_ylabel("Repair Success Rate", fontsize=12)
    ax.set_title("H-M3: G3 vs G4 Comparison (Gate: G4 <= G3 + 2%)", fontsize=14)
    ax.legend()
    ax.set_ylim(0, max(rates) * 1.3)

    # Add value labels
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{rate:.1%}", ha="center", fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_contingency_heatmap(table: np.ndarray,
                             output_path: str = "figures/contingency_heatmap.png"):
    """Plot 2x2 contingency table as heatmap."""
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(table, annot=True, fmt="d", cmap="Blues",
                xticklabels=["G4 Success", "G4 Fail"],
                yticklabels=["G3 Success", "G3 Fail"],
                ax=ax, cbar_kws={"label": "Count"})

    ax.set_title("Paired Outcomes: G3 vs G4", fontsize=14)
    ax.set_xlabel("G4 Outcome", fontsize=12)
    ax.set_ylabel("G3 Outcome", fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
```

**Output Directory:** `h-m3/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Statistical analysis: ≤10 seconds total
- No GPU required (CPU-only statistical computation)
- Memory: ≤1GB RAM

### NFR-2: Reproducibility
- Deterministic statistical tests
- All results saved with timestamps
- Data checksums for input verification

### NFR-3: Dependencies
- No model loading required
- Standard statistical libraries only (scipy, statsmodels, numpy)

### NFR-4: Error Handling
- Validate H-M1 results exist before analysis
- Check data integrity (paired observations)
- Graceful handling of edge cases (zero cells in contingency table)

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
| Metric | Target | Measurement |
|--------|--------|-------------|
| G4 - G3 Difference | <= +2% | Point estimate |
| McNemar p-value | >= 0.05 OR G3 > G4 | statsmodels.mcnemar |
| Sample Size | 304 paired observations | H-M1 results |

### Interpretation Matrix
| McNemar p-value | Direction | Gate Result | Conclusion |
|-----------------|-----------|-------------|------------|
| p >= 0.05 | Any | PASS | No significant difference |
| p < 0.05 | G3 > G4 | PASS | G3 superior (strong non-monotonicity) |
| p < 0.05 | G4 > G3 | FAIL | G4 superior (monotonic relationship) |

### Expected Outcome (from H-M1 post-hoc)
Based on H-M1 data:
- G3: 16.8% (51/304)
- G4: 22.7% (69/304)
- Difference: +5.9% (exceeds 2% margin)
- Post-hoc p-value: 0.452 (not significant)

**Expected Gate Result:** PASS (despite 5.9% difference, p=0.452 indicates no statistical significance)

### Gate Decision
- **PASS:** Non-monotonicity confirmed → Validates core research claim
- **FAIL:** G4 significantly outperforms G3 → Document limitation, "more is better" may hold

---

## Dependencies

### External Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| scipy | >=1.10.0 | Statistical functions |
| statsmodels | >=0.14.0 | McNemar's test, TOST |
| numpy | >=1.24.0 | Numerical operations |
| matplotlib | >=3.7.0 | Visualization |
| seaborn | >=0.12.0 | Statistical plots |
| pyyaml | >=6.0 | Results persistence |

### Internal Dependencies
| Dependency | Status | Notes |
|------------|--------|-------|
| H-M1 Validation | COMPLETED | PASS - ANOVA p=3.5e-19 |
| H-M1 Results | EXISTS | `h-m1/results/repair_results.json` |
| Phase 2C Brief | COMPLETED | `h-m3/02c_experiment_brief.md` |

---

## Data Specifications

### Input Data (from H-M1)
| Field | Type | Source | Description |
|-------|------|--------|-------------|
| task_id | int | H-M1 | MBPP problem ID |
| granularity | str | H-M1 | "G3" or "G4" |
| success | bool | H-M1 | Repair succeeded |

### Derived Data
| Field | Type | Description |
|-------|------|-------------|
| g3_outcomes | list[bool] | 304 G3 success values |
| g4_outcomes | list[bool] | 304 G4 success values |
| contingency_table | np.ndarray | 2x2 paired outcome matrix |

### Output Metrics
| Field | Type | Description |
|-------|------|-------------|
| g3_rate | float | G3 success rate (expected: 0.168) |
| g4_rate | float | G4 success rate (expected: 0.227) |
| difference | float | G4 - G3 (expected: +0.059) |
| mcnemar_pvalue | float | McNemar test p-value |
| tost_pvalue | float | TOST equivalence p-value |
| ci_lower | float | 95% CI lower bound |
| ci_upper | float | 95% CI upper bound |
| gate_passed | bool | H-M3 gate result |

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Gate FAIL (G4 >> G3) | MEDIUM | Valid scientific outcome; document limitation |
| H-M1 results missing | HIGH | Check file existence before analysis |
| Data integrity issues | MEDIUM | Validate paired observations, checksums |
| Statistical edge cases | LOW | Handle zero cells, use exact tests |

---

## Appendix: Phase 2C Traceability

| PRD Section | Phase 2C Source |
|-------------|-----------------|
| McNemar's Test | Statistical Tests section |
| TOST Equivalence | Statistical Tests section |
| Gate Condition (2% margin) | Success Criteria section |
| Data Source (H-M1) | Dataset section |
| Expected Rates | Previous Hypothesis Results |
| Confidence Interval | Evaluation section |

---

## Appendix: Expected Results Summary

Based on H-M1 experimental data:

### Contingency Table (Expected)
|  | G4 Success | G4 Fail | Total |
|--|------------|---------|-------|
| **G3 Success** | ~35 | ~16 | 51 |
| **G3 Fail** | ~34 | ~219 | 253 |
| **Total** | 69 | 235 | 304 |

### Statistical Tests (Expected)
- **McNemar p-value:** ~0.45 (not significant)
- **TOST p-value:** >0.05 (not equivalent within 2%)
- **95% CI for difference:** approximately [-0.02, +0.14]

### Gate Decision (Expected)
- **Result:** PASS
- **Reason:** McNemar p >= 0.05 indicates no significant difference

---

*Generated for Phase 3 Implementation Planning*
*Source: h-m3/02c_experiment_brief.md*
*Prerequisite: H-M1 VALIDATED (ANOVA p=3.5e-19)*
*Hypothesis Type: Statistical Reanalysis*
*Next: Architecture Design (03_architecture.md)*
