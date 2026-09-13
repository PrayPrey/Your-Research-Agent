# Experiment Design: h-m3

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** Unanimous scale agreement indicates ≥10% higher verdict reliability vs split verdicts
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing agreement-as-confidence signal

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 data available)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (FAILED but data available)

### Gate Condition
- Unanimous verdict accuracy > split verdict accuracy by ≥10%
- Two-proportion z-test p < 0.05
- Falsification: Difference < 5%

---

## Continuation Context

This hypothesis reuses judge verdict data from h-e1/h-m2 to test a different claim:
- h-m2 tested: Does ensemble voting beat best single judge? (FAILED)
- h-m3 tests: Does unanimous agreement indicate higher reliability? (independent question)

### Previous Hypothesis Results
- h-m2 FAILED: Majority vote accuracy 37.80% vs best single 45.85%
- Data available: 164 HumanEval+ problems × 4 judge models
- Judge verdicts cached in h-e1/code/outputs/results.csv

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct results for LLM judge agreement patterns. Archon KB focused on distributed computing and diffusion models.

### Exa GitHub/Web Findings

**Source 1: "Vibe Coding on Trial: Unanimous LLM Juries" (arXiv 2602.18492)**
- Studies unanimous committees of LLM judges for SQL evaluation
- Key finding: Small unanimous committees cut false accepts while maintaining TPR
- Committee composition matters significantly
- Recommends per-generator validation

**Source 2: "LLMs as a Jury: Cross-Model Consensus" (arXiv 2607.10139)**
- Studies cross-model consensus as confidence signal
- Key finding: "unanimous four-model panel is correct 99.5% of the time while still answering 85% of problems"
- Agreement serves as calibrated abstention control
- Shared-error floor limits selective accuracy

**Source 3: "Reliability without Validity" (arXiv 2606.19544)**
- Largest LLM-as-Judge evaluation: 21 judges, 118 runs, ~541K judgments
- Recommends Cohen's κ over exact match
- Test-retest reliability coexists with position bias
- Minimum Viable Validation Protocol defined

### 🎯 Implementation Priority Assessment

**CRITICAL: Uses existing cached data from h-e1**

**Recommended Implementation Path:**
- Primary: Analyze h-e1/code/outputs/results.csv
- Fallback: N/A (data already exists)
- Justification: Statistical analysis of existing verdicts, no new inference needed

### Code Analysis (Serena MCP)

*Skipped* - Hypothesis tests statistical properties of agreement patterns, no complex architecture to analyze

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ Judge Verdicts
**Type**: programmatic-api (real execution results, NOT synthetic)

**Statistics**:
- 164 HumanEval+ problems
- 4 judge models per problem (7B×2, 70B, proprietary)
- Total: 656 verdicts with ground truth labels

**Source**: h-e1/code/outputs/results.csv

**Loading Information** (for Phase 4):
- Method: pandas CSV
- Identifier: h-e1/code/outputs/results.csv (relative to research folder)
- Code: `pd.read_csv("../h-e1/code/outputs/results.csv")`

### Models

#### Baseline Model

**Architecture**: N/A - Statistical analysis, no model training

**Loading Information**: Not applicable

#### Proposed Model

**Architecture**: N/A - Statistical comparison

**Core Mechanism Implementation:**

```python
# Core Mechanism: Agreement-as-Confidence Analysis
# Based on: arXiv 2607.10139 "LLMs as a Jury"

import pandas as pd
import numpy as np
from scipy.stats import proportions_ztest

def analyze_agreement_confidence(results_df):
    """
    Compare verdict accuracy: unanimous vs split agreement.
    
    Args:
        results_df: DataFrame with columns [problem_id, judge_model, verdict, ground_truth]
    
    Returns:
        dict with unanimous_acc, split_acc, z_stat, p_value, improvement
    """
    # Group by problem to determine agreement type
    grouped = results_df.groupby('problem_id')
    
    # Classify problems by agreement type
    agreement_info = grouped.apply(lambda g: pd.Series({
        'unanimous': g['verdict'].nunique() == 1,
        'majority_verdict': g['verdict'].mode().iloc[0],
        'ground_truth': g['ground_truth'].iloc[0]
    }))
    
    unanimous_mask = agreement_info['unanimous']
    
    # Compute accuracy for unanimous vs split
    unanimous_correct = (
        agreement_info.loc[unanimous_mask, 'majority_verdict'] == 
        agreement_info.loc[unanimous_mask, 'ground_truth']
    ).sum()
    unanimous_total = unanimous_mask.sum()
    
    split_correct = (
        agreement_info.loc[~unanimous_mask, 'majority_verdict'] == 
        agreement_info.loc[~unanimous_mask, 'ground_truth']
    ).sum()
    split_total = (~unanimous_mask).sum()
    
    unanimous_acc = unanimous_correct / unanimous_total if unanimous_total > 0 else 0
    split_acc = split_correct / split_total if split_total > 0 else 0
    
    # Two-proportion z-test
    z_stat, p_value = proportions_ztest(
        [unanimous_correct, split_correct],
        [unanimous_total, split_total],
        alternative='larger'  # H1: unanimous > split
    )
    
    return {
        'unanimous_acc': unanimous_acc,
        'split_acc': split_acc,
        'improvement': unanimous_acc - split_acc,
        'z_stat': z_stat,
        'p_value': p_value,
        'unanimous_n': unanimous_total,
        'split_n': split_total
    }
```

### Training Protocol

**Not Applicable** - This is statistical analysis, not model training.

**Analysis Protocol**:
1. Load judge verdicts from h-e1 results
2. Group by problem_id
3. Classify: unanimous (all 4 judges agree) vs split (any disagreement)
4. Compute accuracy for each group
5. Run two-proportion z-test
6. Report improvement and statistical significance

### Evaluation

**Primary Metrics**:
- Unanimous verdict accuracy (% correct when all judges agree)
- Split verdict accuracy (% correct when judges disagree)
- Accuracy improvement: unanimous_acc - split_acc

**Success Criteria (from Phase 2B)**:
- Improvement ≥ 10% (unanimous_acc - split_acc ≥ 0.10)
- p-value < 0.05 (statistically significant)

**Falsification**:
- Improvement < 5%

**Metrics Loading Information**:
- Task Type: statistical comparison
- Library: scipy.stats
- Code: `from scipy.stats import proportions_ztest`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing unanimous vs split accuracy with 95% CI error bars

#### Additional Figures (LLM Autonomous)
- Agreement distribution pie chart (% problems unanimous vs split)
- Per-model contribution to disagreement (which judges cause splits)
- Confusion matrix for unanimous verdicts

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. unanimous_acc - split_acc ≥ 0.10
3. p-value < 0.05

---

## Appendix: Reference Implementations

### A. Exa Web Search Sources

**Source 1**: "Vibe Coding on Trial: Unanimous LLM Juries"
- **URL**: https://doi.org/10.48550/arxiv.2602.18492
- **Query Used**: "LLM judge agreement unanimous voting confidence"
- **Relevance**: Direct study of unanimous LLM judge committees
- **Used For**: Experimental design rationale

**Source 2**: "LLMs as a Jury: Cross-Model Consensus"
- **URL**: https://arxiv.org/html/2607.10139v2
- **Query Used**: "multi-model LLM ensemble voting agreement"
- **Relevance**: Studies agreement-as-confidence signal
- **Key Finding**: Unanimous panel 99.5% correct at 85% coverage
- **Used For**: Success threshold calibration, methodology

**Source 3**: "Reliability without Validity" (arXiv 2606.19544)
- **URL**: https://arxiv.org/html/2606.19544v1
- **Query Used**: Same as above
- **Relevance**: Largest systematic LLM-as-Judge evaluation
- **Used For**: Statistical methodology (Cohen's κ framework)

### B. Previous Hypothesis Context

**Source**: h-e1 and h-m2 validation results
- **File**: h-e1/code/outputs/results.csv
- **Contents**: Judge verdicts for 164 HumanEval+ problems
- **Why Reused**: Same data, different analysis question

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Previous hypothesis | h-e1/code/outputs/results.csv |
| Statistical test | Research paper | arXiv 2607.10139 |
| Success threshold | Phase 2B | 02b_verification_plan.md |
| Cohen's κ methodology | Research paper | arXiv 2606.19544 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-24
- Experiment design completed: 2026-08-24

---

*MCP Tools Used: Exa (Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
