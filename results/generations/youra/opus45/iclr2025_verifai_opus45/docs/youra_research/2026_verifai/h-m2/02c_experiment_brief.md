# Experiment Design: h-m2

**Date:** 2026-03-30
**Author:** Anonymous
**Hypothesis Statement:** G3 (error+line) achieves at least 10 percentage points higher repair success than G0 (pass/fail only)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Post-hoc comparison using h-m1 data

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** Yes (h-m1 PASSED: ANOVA p=3.5e-19)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (COMPLETED, PASSED)

### Gate Condition
G3 achieves at least 10 percentage points higher repair success than G0 (pass/fail only).

**CRITICAL FINDING FROM h-m1:**
The prerequisite h-m1 experiment ALREADY demonstrated the **OPPOSITE** result:
- G0 (pass/fail): **41.8%** success rate
- G3 (error+line): **16.8%** success rate
- Difference: G0 outperforms G3 by **25.0 percentage points**

This hypothesis is **PRE-FALSIFIED** by h-m1 data but must still be formally tested for scientific rigor.

---

## Continuation Context

### Previous Hypothesis Results (h-m1)

**Experiment:** H-M1 Granularity Effect on Repair Success
**Result:** PASS (ANOVA p=3.5e-19, significant effect exists)
**Key Finding:** Simpler feedback (G0, G1) significantly outperforms detailed feedback (G2-G4)

| Granularity | Success Rate | Successes/Total |
|-------------|--------------|-----------------|
| G0 | 41.8% | 127/304 |
| G1 | 40.8% | 124/304 |
| G2 | 18.4% | 56/304 |
| G3 | 16.8% | 51/304 |
| G4 | 22.7% | 69/304 |

**Implication for h-m2:** The data already shows G0 > G3 by ~25pp. h-m2 hypothesis predicts the opposite (G3 > G0 + 10pp), which is already contradicted.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LLM code repair error feedback granularity experiment**
- Limited direct results in Archon KB for this specific research area
- Self-Debug (Chen et al., 2023) is a relatively new approach
- No prior granularity comparison studies found in KB

**Query 2: Self-debug code repair implementation challenges**
- General code repair patterns found
- PyTorch evaluation and error handling patterns available

**Query 3: MBPP benchmark code generation evaluation**
- Standard evaluation methodologies documented
- pass@k metrics commonly used

### Archon Code Examples

Limited direct code examples for LLM code repair granularity comparison.
Relying on Exa GitHub findings for implementation details.

### Exa GitHub Implementations

**Repository 1**: theoxo/self-repair (⭐ 15) - ICLR 2024
- **URL**: https://github.com/theoxo/self-repair
- **Relevance**: "Is Self-Repair a Silver Bullet for Code Generation?" - directly relevant study
- **Key Finding**: Self-repair effectiveness varies significantly by model and task
- **Implementation**: Python-based evaluation framework for HumanEval/APPS

**Repository 2**: TnTWoW/RePair (⭐ 7) - ACL 2024
- **URL**: https://github.com/TnTWoW/RePair
- **Relevance**: Automated Program Repair with Process-based Feedback
- **Dataset**: CodeNet4Repair (HuggingFace: TnT/Multi_CodeNet4Repair)

**Repository 3**: iSEngLab/AwesomeLLM4APR - TOSEM 2026 Survey
- **URL**: https://github.com/iSEngLab/AwesomeLLM4APR
- **Relevance**: Comprehensive survey of LLM for Automated Program Repair
- **References**: Teaching Large Language Models to Self-Debug (Chen et al., 2024 ICLR)

**Original Paper**: Teaching Large Language Models to Self-Debug
- **Authors**: Xinyun Chen, Maxwell Lin, Nathanael Schärli, Denny Zhou
- **Venue**: ICLR 2024
- **URL**: https://openreview.net/forum?id=KuPixIqPiq
- **Benchmarks**: Spider (text-to-SQL), TransCoder (C++-to-Python), MBPP (text-to-Python)

### Implementation Priority Assessment

**CRITICAL: This experiment uses POST-HOC analysis of h-m1 data**

**Recommended Implementation Path:**
- Primary: Extract G3 and G0 results from h-m1 experiment (already collected)
- Fallback: N/A - data already exists
- Justification: Controlled comparison using identical experimental conditions

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. This is a statistical analysis, not a new implementation.

---

## Experiment Specification

### Dataset

**Name:** MBPP Runtime Error Cases (from h-m1)
**Type:** standard (derivative)
**Source:** h-m1 experiment output
**Size:** 304 runtime error cases

**Loading Information** (for Phase 4):
- Method: Load from h-m1 results
- Identifier: `h-m1/results/repair_results.json`
- Code:
```python
import json
with open('h-m1/results/repair_results.json', 'r') as f:
    results = json.load(f)
g0_results = [r for r in results if r['granularity'] == 'G0']
g3_results = [r for r in results if r['granularity'] == 'G3']
```

### Models

#### Baseline Model

**Already Executed in h-m1**
- **Architecture:** CodeLlama-7B-Instruct
- **Source:** meta-llama/CodeLlama-7b-Instruct-hf
- **Configuration:** temperature=0, max_tokens=512

**Loading Information** (for Phase 4 - reference only):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/CodeLlama-7b-Instruct-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
```

#### Proposed Model

**Architecture:** N/A - This is a post-hoc comparison, not a new model

**Core Mechanism Implementation:**

This hypothesis tests a **statistical comparison** between two feedback granularity levels:

```python
# Core Mechanism: G3 vs G0 Paired Comparison (McNemar's Test)
# Based on: statsmodels.stats.contingency_tables.mcnemar

import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

def compare_g3_vs_g0(g0_results: list, g3_results: list) -> dict:
    """
    McNemar's test for paired binary outcomes.

    Args:
        g0_results: List of binary outcomes (0/1) for G0 feedback
        g3_results: List of binary outcomes (0/1) for G3 feedback
    Returns:
        dict with test statistic, p-value, and effect size
    """
    assert len(g0_results) == len(g3_results), "Must be paired"
    n = len(g0_results)

    # Build 2x2 contingency table
    # Rows: G0 (fail=0, success=1), Cols: G3 (fail=0, success=1)
    table = np.zeros((2, 2), dtype=int)
    for g0, g3 in zip(g0_results, g3_results):
        table[g0, g3] += 1

    # McNemar's test (exact for small samples)
    result = mcnemar(table, exact=True)

    # Calculate rates
    g0_rate = sum(g0_results) / n
    g3_rate = sum(g3_results) / n
    difference = g3_rate - g0_rate

    return {
        'g0_rate': g0_rate,
        'g3_rate': g3_rate,
        'difference': difference,  # G3 - G0
        'difference_pp': difference * 100,  # percentage points
        'mcnemar_statistic': result.statistic,
        'mcnemar_pvalue': result.pvalue,
        'n_pairs': n,
        'contingency_table': table.tolist(),
        'gate_passed': difference >= 0.10  # G3 >= G0 + 10pp
    }
```

### Training Protocol

**N/A - Post-hoc Analysis**

This experiment does not require training. It performs statistical analysis on data already collected in h-m1.

**Analysis Protocol:**
1. Load repair results from h-m1/results/repair_results.json
2. Extract paired outcomes for G0 and G3 conditions
3. Apply McNemar's test for paired binary data
4. Calculate difference and confidence interval
5. Evaluate gate condition (G3 - G0 >= 10pp)

### Evaluation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Paired binary comparison
- Library: statsmodels, scipy
- Code:
```python
from statsmodels.stats.contingency_tables import mcnemar
from scipy.stats import chi2
# McNemar's test for paired nominal data
```

**Primary Metrics:**
- G0 success rate (from h-m1: 41.8%)
- G3 success rate (from h-m1: 16.8%)
- Difference (G3 - G0) in percentage points
- McNemar's test p-value

**Success Criteria (Gate: SHOULD_WORK):**
- Primary: (G3 - G0) >= 10 percentage points
- Statistical: McNemar p < 0.05 with G3 > G0

**Expected Result (based on h-m1):**
- G3 - G0 = 16.8% - 41.8% = **-25.0 percentage points**
- **HYPOTHESIS EXPECTED TO FAIL** (G0 significantly outperforms G3)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: G0 vs G3 success rate bar chart with 10pp threshold line

#### Additional Figures (LLM Autonomous)
- Contingency table heatmap showing paired outcomes
- Error bar plot with confidence intervals
- Comparison to h-m1 overall granularity curve

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes - Statistical comparison of G3 vs G0
- **mechanism_isolatable:** Yes - Direct paired comparison from h-m1 data
- **baseline_measurable:** Yes - G0 results from h-m1 serve as baseline

### Architecture Compatibility
- **Compatible:** Yes - Post-hoc analysis using existing data
- **Data Format:** JSON with binary success outcomes per case

### Activation Indicators
- **mechanism_log_message:** "Comparing G3 vs G0 across {n} paired samples"
- **tensor_shape_change:** N/A (statistical analysis)
- **metric_delta_expected:** G3 - G0 (expecting negative based on h-m1)

### Verification Code
```python
def verify_mechanism_activation(results: dict) -> bool:
    """Verify that comparison was performed correctly."""
    checks = [
        results['n_pairs'] == 304,  # All h-m1 cases
        results['g0_rate'] > 0,     # G0 has successes
        results['g3_rate'] > 0,     # G3 has successes
        'mcnemar_pvalue' in results # Statistical test ran
    ]
    return all(checks)
```

### Success Threshold
- **hypothesis_support_threshold:** difference >= 0.10 (10pp)
- **hypothesis_support_metric:** (G3 success rate) - (G0 success rate)

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. McNemar's test produces valid p-value
3. Difference calculated correctly

**Gate Pass Condition (SHOULD_WORK):**
- (G3 - G0) >= 10 percentage points AND McNemar p < 0.05 favoring G3

**EXPECTED GATE RESULT: FAIL**
Based on h-m1 data: G3 (16.8%) - G0 (41.8%) = -25.0pp
G0 significantly outperforms G3, contradicting the hypothesis.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: General PyTorch evaluation patterns
- **Type**: Knowledge base article
- **Query Used**: "LLM code repair error feedback granularity experiment"
- **Relevance**: Limited direct results for this specific topic
- **Used For**: Background context

### B. GitHub Implementations (Exa)

**Repository 1**: theoxo/self-repair (⭐ 15)
- **URL**: https://github.com/theoxo/self-repair
- **Query Used**: "Self-Debug Chen LLM code repair official implementation GitHub"
- **Relevance**: ICLR 2024 paper on self-repair effectiveness
- **Used For**: Understanding self-repair methodology

**Repository 2**: TnTWoW/RePair (⭐ 7)
- **URL**: https://github.com/TnTWoW/RePair
- **Relevance**: ACL 2024 automated program repair
- **Used For**: Reference implementation patterns

### C. Statistical Method Sources (Exa)

**McNemar's Test Implementation**:
- statsmodels: `from statsmodels.stats.contingency_tables import mcnemar`
- Sources: GeeksforGeeks, Towards Data Science, AskPython tutorials
- **Used For**: Core statistical test implementation

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: 304 MBPP runtime error cases
  - Results: All G0-G4 repair outcomes
  - Model: CodeLlama-7B-Instruct configuration
- **Why Reused**: Post-hoc analysis of existing experimental data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Previous Experiment | h-m1/results/repair_results.json |
| G0/G3 definitions | Phase 2B | 02b_verification_plan.md |
| Statistical test | Exa Search | statsmodels McNemar documentation |
| Success criteria | Phase 2B | Gate condition from verification plan |
| Expected baseline | h-m1 Results | 04_validation.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-30T10:35:00Z

### Workflow History for This Hypothesis
- Phase 2B: Hypothesis defined with SHOULD_WORK gate
- Phase 2C Step 1: Initialized, loaded h-m1 prerequisite results
- Phase 2C Step 2-7: Research and synthesis complete
- Phase 2C Step 8: Validation and completion

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web), McNemar Test Research*
*All specifications grounded in h-m1 experimental data*
*Next Phase: Phase 3 - Implementation Planning*
