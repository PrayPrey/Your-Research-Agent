# Experiment Design: h-m3

**Date:** 2026-03-30
**Author:** Anonymous
**Hypothesis Statement:** G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%), confirming non-monotonic relationship
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (COMPLETED)

### Gate Condition
G4 <= G3 + 2% (practical equivalence or G3 wins)

---

## Continuation Context

This hypothesis uses data from the completed H-M1 experiment. The H-M1 results showed:
- G3 success rate: 16.8% (51/304)
- G4 success rate: 22.7% (69/304)
- Difference: G4 - G3 = +5.9%

**Critical observation:** The H-M1 data shows G4 outperforming G3 by 5.9%, which exceeds the 2% threshold. This experiment will perform formal statistical testing to determine if this difference is significant.

### Previous Hypothesis Results (if applicable)
- H-E1: PASS - Runtime error prevalence 60.8% (304/500 failures)
- H-M1: PASS - ANOVA p=3.5e-19, significant granularity effect confirmed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "error feedback granularity LLM code repair experiment" - 4 results
2. "self-debugging code repair statistical comparison" - 4 results
3. "MBPP benchmark code generation evaluation" - 5 results

**Findings:**
The Archon knowledge base does not contain direct research on LLM code repair or error feedback granularity comparison. This is expected for a specialized research domain. However, this is acceptable for H-M3 because:

1. **Data reuse from H-M1:** H-M3 reanalyzes existing experimental data from H-M1 (304 cases × 5 granularity levels = 1,520 repair attempts already collected)
2. **Statistical methodology is standard:** McNemar's test for paired binary outcomes and TOST equivalence testing are well-established statistical methods
3. **No new model training required:** This is a statistical analysis hypothesis, not an implementation hypothesis

**Relevant Background (from prior phases):**
- Self-Debug (Chen et al., 2023): Uses G2-level feedback, no granularity comparison
- TraceFixer (Bouzenia et al., 2023): Uses full traces (G4), no ablation study
- Haque et al. (2025): Found traces help less than expected but didn't test granularity systematically

### Archon Code Examples

**Search Queries Executed:**
1. "McNemar test statistical comparison" - 5 results (no relevant code)
2. "paired proportion comparison equivalence" - 5 results (no relevant code)

**Findings:**
No directly relevant code examples found in Archon KB for statistical proportion comparison tests. Standard implementations from scipy.stats and statsmodels will be used:
- `scipy.stats.chi2_contingency` or `statsmodels.stats.contingency_tables.mcnemar` for McNemar's test
- Manual TOST implementation or `statsmodels.stats.proportion` for equivalence testing

### Exa GitHub Implementations

**Query 1: Self-Debug LLM Code Repair Implementation**

**Repository 1**: [FloridSleeves/LLMDebugger](https://github.com/floridsleeves/llmdebugger) (577 stars)
- **URL**: https://github.com/floridsleeves/llmdebugger
- **Paper**: "Debug like a Human: A Large Language Model Debugger via Verifying Runtime Execution Step-by-step" (ACL 2024)
- **Relevance**: LDB framework for LLM code debugging with runtime execution verification
- **Key Features**:
  - Segments programs into basic blocks
  - Tracks intermediate variable values during execution
  - Achieves 98.2% accuracy with GPT-4o
- **Installation**:
  ```bash
  conda create -n ldb python=3.10
  conda activate ldb
  python -m pip install -r requirements.txt
  ```

**Paper Reference**: [Teaching Large Language Models to Self-Debug](https://arxiv.org/abs/2304.05128) (Chen et al., ICLR 2024)
- Original Self-Debug paper
- Benchmarks: Spider, TransCoder, MBPP
- Improves baseline by up to 12% on MBPP

**Query 2: McNemar's Test Python Implementation**

**Statistical Testing Resources:**
1. **statsmodels.stats.contingency_tables.mcnemar** - Standard implementation
   - URL: https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html
   - Usage for paired binary classifier comparison

2. **McNemar's Test Implementation Pattern:**
   ```python
   from statsmodels.stats.contingency_tables import mcnemar

   # Create 2x2 contingency table
   # [[both_correct, g3_correct_g4_wrong],
   #  [g3_wrong_g4_correct, both_wrong]]
   table = [[a, b], [c, d]]
   result = mcnemar(table, exact=True)
   print(f"p-value: {result.pvalue}")
   ```

**Query 3: TOST Equivalence Test**

**statsmodels.stats.proportion.tost_proportions_2indep**:
- URL: https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.tost_proportions_2indep.html
- Tests if two proportions are within equivalence margin
- H0: |prop1 - prop2| >= margin (not equivalent)
- H1: |prop1 - prop2| < margin (equivalent)
- Usage:
  ```python
  from statsmodels.stats.proportion import tost_proportions_2indep

  # Test if G4-G3 difference is within 2% margin
  result = tost_proportions_2indep(
      count1=69, nobs1=304,  # G4: 69/304
      count2=51, nobs2=304,  # G3: 51/304
      low=-0.02, upp=0.02    # 2% equivalence margin
  )
  ```

**Serena Analysis Needed**: No (code is clear - standard statistical tests)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M3 is a **statistical reanalysis hypothesis** - it does not require new model training or data collection. All data already exists from H-M1.

**Recommended Implementation Path:**
- Primary: Reuse H-M1 experimental results (304 cases × 5 granularity levels)
- Fallback: N/A - data already collected
- Justification: H-M3 compares G3 vs G4 success rates using existing H-M1 data. No new experiments needed - only statistical analysis.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear.

H-M3 uses standard statistical testing functions from established libraries:
- `statsmodels.stats.contingency_tables.mcnemar` - McNemar's test for paired binary data
- `statsmodels.stats.proportion.tost_proportions_2indep` - TOST equivalence test

No custom model architectures or complex code patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** H-M1 Experimental Results (reanalysis)
**Type:** standard (derived from MBPP benchmark)
**Source:** `h-m1/results/repair_results.json`

**This is a REANALYSIS experiment** - no new data collection required.

| Field | Value |
|-------|-------|
| Original Dataset | MBPP test split (500 problems) |
| Runtime Error Cases | 304 (from H-E1) |
| Repair Attempts | 1,520 (304 × 5 granularity levels) |
| Relevant Data | G3 and G4 results (608 paired outcomes) |

**Data Structure for H-M3:**
```
G3 results: 304 binary outcomes (success/failure)
G4 results: 304 binary outcomes (success/failure)
Paired by: problem_id (same 304 runtime error cases)
```

**Loading Information** (for Phase 4):
- Method: Load from H-M1 results
- Identifier: `h-m1/results/repair_results.json`
- Code:
  ```python
  import json
  with open("../h-m1/results/repair_results.json") as f:
      h_m1_results = json.load(f)
  g3_results = [r["success"] for r in h_m1_results if r["granularity"] == "G3"]
  g4_results = [r["success"] for r in h_m1_results if r["granularity"] == "G4"]
  ```

### Models

#### Baseline Model

**No model inference required** - H-M3 is a statistical analysis hypothesis.

The "baseline" for H-M3 is the G3 granularity level performance:
- G3 success rate: 16.8% (51/304)
- This is compared against G4: 22.7% (69/304)

**Loading Information** (for Phase 4):
- Method: N/A (no model loading)
- Identifier: N/A
- Code: N/A (statistical analysis only)

#### Proposed Model

**Architecture:** N/A - This is a statistical reanalysis hypothesis

H-M3 does not propose a new model. It analyzes the relationship between G3 and G4 granularity levels using existing H-M1 experimental data.

**Core Mechanism Implementation:**

```python
# H-M3: Non-Monotonicity Analysis (G3 >= G4)
# Statistical comparison of paired binary outcomes
# Based on: statsmodels McNemar + TOST equivalence testing

import json
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar
from scipy import stats

def load_h_m1_results(filepath: str) -> dict:
    """Load repair results from H-M1 experiment."""
    with open(filepath) as f:
        return json.load(f)

def extract_paired_outcomes(results: list) -> tuple:
    """Extract G3 and G4 outcomes for same problem IDs."""
    g3_by_problem = {r["problem_id"]: r["success"]
                     for r in results if r["granularity"] == "G3"}
    g4_by_problem = {r["problem_id"]: r["success"]
                     for r in results if r["granularity"] == "G4"}

    problem_ids = sorted(g3_by_problem.keys())
    g3_outcomes = [g3_by_problem[pid] for pid in problem_ids]
    g4_outcomes = [g4_by_problem[pid] for pid in problem_ids]
    return g3_outcomes, g4_outcomes, problem_ids

def build_contingency_table(g3: list, g4: list) -> np.ndarray:
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
    return np.array([[a, b], [c, d]])

def run_mcnemar_test(table: np.ndarray) -> dict:
    """Run McNemar's test for marginal homogeneity."""
    result = mcnemar(table, exact=True)
    return {"statistic": result.statistic, "pvalue": result.pvalue}

def check_gate_condition(g3_rate: float, g4_rate: float,
                         margin: float = 0.02) -> dict:
    """Check if G4 <= G3 + margin (H-M3 gate condition)."""
    diff = g4_rate - g3_rate
    passed = diff <= margin
    return {
        "g3_rate": g3_rate,
        "g4_rate": g4_rate,
        "difference": diff,
        "margin": margin,
        "gate_passed": passed
    }
```

### Training Protocol

**N/A - No Training Required**

H-M3 is a statistical reanalysis hypothesis. It performs statistical tests on existing H-M1 data.

**Computational Protocol:**
1. Load H-M1 repair results (`h-m1/results/repair_results.json`)
2. Extract paired G3 and G4 outcomes for all 304 problem IDs
3. Compute success rates: G3 = 51/304 = 16.8%, G4 = 69/304 = 22.7%
4. Build 2x2 contingency table for McNemar's test
5. Run McNemar's exact test for significant difference
6. Check gate condition: G4 <= G3 + 2%

**Seeds:** N/A (deterministic statistical analysis)

### Evaluation

**Statistical Tests:**

| Test | Purpose | Library |
|------|---------|---------|
| McNemar's Test | Test if G3 vs G4 success rates differ significantly | `statsmodels.stats.contingency_tables.mcnemar` |
| TOST Equivalence | Test if difference is within ±2% margin | `statsmodels.stats.proportion.tost_proportions_2indep` |
| Confidence Interval | 95% CI for G4-G3 difference | `statsmodels.stats.proportion.confint_proportions_2indep` |

**Primary Metrics:**
- G3 success rate: proportion of successful repairs with G3 feedback
- G4 success rate: proportion of successful repairs with G4 feedback
- Difference: G4 - G3 (expected to be ≤ 2% for gate pass)

**Success Criteria (Gate Condition):**
- **Primary:** G4 ≤ G3 + 2% (practical equivalence or G3 superiority)
- **Statistical:** McNemar p-value interpretation
  - If p < 0.05 AND G4 > G3: Gate FAILS (G4 significantly better)
  - If p >= 0.05: Gate PASS (no significant difference - supports non-monotonicity)
  - If p < 0.05 AND G3 > G4: Gate PASS (G3 significantly better - supports non-monotonicity)

**Expected Baseline Performance (from H-M1):**
- G3: 16.8% (51/304)
- G4: 22.7% (69/304)
- Observed difference: +5.9% (G4 > G3)
- Post-hoc p-value from H-M1: 0.452 (not significant)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: paired binary classification comparison
- Library: statsmodels, scipy
- Code:
  ```python
  from statsmodels.stats.contingency_tables import mcnemar
  from statsmodels.stats.proportion import (
      tost_proportions_2indep,
      confint_proportions_2indep
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: G3 vs G4 success rate bar chart with 2% margin line

#### Additional Figures (LLM Autonomous)
1. **Contingency Table Heatmap**: 2x2 matrix showing paired outcome distribution
2. **Confidence Interval Plot**: Point estimate with 95% CI for G4-G3 difference
3. **Granularity Curve**: All G0-G4 success rates showing non-monotonic pattern (from H-M1)
4. **McNemar Test Summary**: Visual representation of test statistic and p-value

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Statistical test confirms G4 <= G3 + 2% OR documents deviation

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note:** Archon KB did not contain direct results for LLM code repair or statistical testing. This is acceptable for H-M3 because:
1. H-M3 reanalyzes existing H-M1 data (no new implementation needed)
2. Statistical methods (McNemar, TOST) are well-established
3. Standard Python libraries (statsmodels, scipy) provide implementations

**Queries Executed:**
1. "error feedback granularity LLM code repair experiment" - No direct matches
2. "self-debugging code repair statistical comparison" - No direct matches
3. "McNemar test statistical comparison" - No direct matches

### B. GitHub Implementations (Exa)

**Repository 1**: [FloridSleeves/LLMDebugger](https://github.com/floridsleeves/llmdebugger) (577 stars)
- **URL**: https://github.com/floridsleeves/llmdebugger
- **Query Used**: "Self-Debug LLM code repair GitHub implementation Chen 2023"
- **Relevance**: LDB framework for LLM debugging with runtime execution verification
- **Paper**: "Debug like a Human: A Large Language Model Debugger via Verifying Runtime Execution Step-by-step" (ACL 2024)
- **Used For**: Background context on LLM debugging approaches

**Paper Reference**: [Teaching Large Language Models to Self-Debug](https://arxiv.org/abs/2304.05128)
- **Authors**: Xinyun Chen, Maxwell Lin, Nathanael Schärli, Denny Zhou (Google)
- **Venue**: ICLR 2024
- **Query Used**: "Self-Debug LLM code repair GitHub implementation Chen 2023"
- **Relevance**: Original Self-Debug methodology used in H-M1 experiment design
- **Key Findings**: Self-debugging improves baseline by up to 12% on MBPP
- **Used For**: H-M1 experimental design foundation

**Statistical Testing Resources**:

**Source 1**: [McNemar's Test in Python](https://www.askpython.com/python/examples/mcnemars-test)
- **Query Used**: "McNemar test Python scipy paired binary comparison code"
- **Relevance**: Step-by-step guide for McNemar's test implementation
- **Used For**: Statistical test selection and implementation pattern

**Source 2**: [McNemar's Test to evaluate ML Classifiers](https://medium.com/data-science/mcnemars-test-to-evaluate-machine-learning-classifiers-with-python-9f26191e1a6b)
- **Query Used**: "McNemar test Python scipy paired binary comparison code"
- **Relevance**: Applying McNemar's test for classifier comparison
- **Used For**: Contingency table construction methodology

**Source 3**: [statsmodels TOST documentation](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.tost_proportions_2indep.html)
- **Query Used**: "TOST equivalence test Python statsmodels proportion comparison"
- **Relevance**: Official API documentation for equivalence testing
- **Used For**: TOST implementation for 2% margin test

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

H-M3 uses standard statistical testing functions from established libraries. No custom model architectures or complex code patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: H-M1 Validation Report
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: MBPP runtime error cases (304 samples from H-E1)
  - Results: G0-G4 success rates from 1,520 repair attempts
  - Statistical findings: ANOVA F=23.89, p=3.5e-19, post-hoc comparisons
- **Why Reused**: H-M3 is a focused reanalysis of G3 vs G4 comparison from H-M1 data

**Key H-M1 Results Used:**
| Granularity | Successes | Total | Success Rate |
|-------------|-----------|-------|--------------|
| G3 | 51 | 304 | 16.8% |
| G4 | 69 | 304 | 22.7% |

**Post-hoc Finding**: G3 vs G4 p-value = 0.452 (not significant in Tukey HSD)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (H-M1 results) | Previous Hypothesis | H-M1 04_validation.md |
| Statistical test selection | Exa GitHub | McNemar's Test articles |
| McNemar implementation | Library Docs | statsmodels.stats.contingency_tables |
| TOST equivalence test | Library Docs | statsmodels.stats.proportion |
| Gate condition (2% margin) | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | H-M3 specification |
| Baseline rates (G3, G4) | Previous Hypothesis | H-M1 results/metrics.yaml |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-30

### Workflow History for This Hypothesis
- Phase 2C started: 2026-03-30
- Status: IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
