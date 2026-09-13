# Experiment Design: h-m1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Preprocessing entropy mediates ≥30% of the metadata→variance effect; preprocessing entropy differs across metadata quartiles while model hyperparameter entropy does not
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Mediation analysis for causal pathway validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (VALIDATED - 42.1% IQR reduction observed)
**Gate Status:** MUST_WORK (blocks h-c1, h-c2)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (satisfied)

### Gate Condition
MUST_WORK: If mediation effect <15% or p>0.10, pipeline BLOCKED.

---

## Continuation Context

Building on h-e1 validated findings:
- Relative IQR reduction: 42.1% (threshold: 20%)
- Absolute IQR reduction: 0.0197 (threshold: 0.01)
- 95% CI: [39.1%, 51.7%] excludes <10%
- p-value < 0.0001

### Previous Hypothesis Results (if applicable)
h-e1 established existence of metadata→variance relationship. h-m1 tests whether preprocessing entropy is the causal mediator.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Queries executed:**
1. "mediation analysis entropy preprocessing" - 4 results (low relevance: diffusion models)
2. "Sobel test bootstrap mediation Python" - 5 results (low relevance: diffusion schedulers)
3. "OpenML reproducibility variance metadata" - 5 results (low relevance: stable diffusion)

**Summary:** Archon KB does not contain directly relevant content for:
- Statistical mediation analysis
- OpenML flow/run analysis
- Preprocessing entropy computation
- Sobel test implementations

**Recommendation:** Rely on Exa GitHub search and established statistical packages (statsmodels, pingouin) for mediation analysis implementations.

### Archon Code Examples

**Queries executed:**
1. "mediation analysis statsmodels Python" - 5 results (irrelevant: diffusion pipelines)
2. "Shannon entropy preprocessing pipeline" - 5 results (irrelevant: image preprocessing)

**Summary:** No relevant code examples found for mediation analysis or entropy computation. Will source from established Python statistical libraries.

### Exa GitHub Implementations

**Query 1: Mediation Analysis Python**

**Repository 1**: pingouin (Official Documentation)
- **URL**: https://pingouin-stats.org/generated/pingouin.mediation_analysis.html
- **Relevance**: Direct mediation analysis with bootstrap CI and p-values
- **Key API**:
  ```python
  from pingouin import mediation_analysis
  stats = mediation_analysis(data=df, x="X", m="M", y="Y", 
                             alpha=0.05, n_boot=500, seed=42)
  # Returns: path, coef, se, pval, CI2.5, CI97.5, sig
  ```
- **Features**: Bootstrap CI, indirect effect (ACME), multiple mediators supported

**Repository 2**: statsmodels.stats.mediation
- **URL**: https://www.statsmodels.org/devel/generated/statsmodels.stats.mediation.Mediation.html
- **Relevance**: Full mediation framework with parametric/bootstrap methods
- **Key API**:
  ```python
  from statsmodels.stats.mediation import Mediation
  import statsmodels.api as sm
  outcome_model = sm.OLS.from_formula("Y ~ M + X + covars", data)
  mediator_model = sm.OLS.from_formula("M ~ X + covars", data)
  med = Mediation(outcome_model, mediator_model, "X", "M").fit(n_rep=1000)
  med.summary()  # ACME, ADE, Total effect with CIs
  ```

**Repository 3**: Experimental-Economics/textbook (Sobel test example)
- **URL**: https://github.com/Experimental-Economics/textbook/blob/main/Ch.%2008/Exhibit%208.1.3A/code/Exhibit_8.1.3A.py
- **Relevance**: Complete Sobel test implementation with variance formula
- **Key Code**:
  ```python
  # Sobel test for indirect effect
  indirect = coef_a * coef_b
  se_indirect = np.sqrt(coef_a**2 * var_b + coef_b**2 * var_a)
  z = indirect / se_indirect
  p = 2 * (1 - norm.cdf(abs(z)))
  ```

**Query 2: OpenML Python API**

**Repository 4**: openml-python (Official)
- **URL**: https://openml.github.io/openml-python/
- **Relevance**: Flow/run retrieval, evaluations listing
- **Key APIs**:
  ```python
  import openml
  # List evaluations with hyperparameters
  evals = openml.evaluations.list_evaluations_setups(
      function="predictive_accuracy", tasks=[task_id],
      flows=[flow_id], output_format="dataframe",
      parameters_in_separate_columns=True
  )
  # Get flow details
  flow = openml.flows.get_flow(flow_id)
  # Run model on task
  run = openml.runs.run_model_on_task(clf, task)
  ```

**Query 3: Shannon Entropy**

**Repository 5**: scipy.stats.entropy
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html
- **Relevance**: Shannon entropy computation for preprocessing distributions
- **Key API**:
  ```python
  from scipy.stats import entropy
  import numpy as np
  # Compute entropy of categorical distribution
  pk = np.array([0.3, 0.5, 0.2])  # probabilities
  H = entropy(pk, base=2)  # bits
  ```

**Serena Analysis Needed**: false (established libraries, clear APIs)

### 🎯 Implementation Priority Assessment

**CRITICAL: For mediation analysis, prioritize established statistical packages**

| Priority | Implementation | Justification |
|----------|----------------|---------------|
| 1 | pingouin.mediation_analysis | Simplest API, bootstrap CI, direct output |
| 2 | statsmodels.stats.mediation.Mediation | More flexible, moderated mediation support |
| 3 | Manual Sobel test | Educational, full control over calculation |

**Recommended Implementation Path:**
- Primary: pingouin.mediation_analysis (simplest, validated against R mediation package)
- Fallback: statsmodels.stats.mediation.Mediation (if complex model needed)
- Justification: Both packages tested against R mediation package; pingouin API is cleaner for standard mediation

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. Using established statistical packages (pingouin, statsmodels, scipy) with well-documented APIs.

---

## Experiment Specification

### Dataset

**Name:** OpenML Benchmark Datasets with Matched Runs
**Type:** programmatic-api (real data via OpenML REST API)
**Source:** OpenML.org (https://openml.org/)

**Selection Criteria:**
- Datasets with ≥10 matched runs (same flow, same hyperparameters)
- Time period: 2019-2024
- Must have metadata completeness score computable (5-field checklist)
- Must have reproducibility variance (IQR) computable

**Expected Sample Size:** ~200 datasets (from h-e1 validation)

**Variables Computed:**
1. **Metadata Completeness Score (M):** 5-field checklist (description, attribute info, version, license, creator)
2. **Preprocessing Entropy (H_prep):** Shannon entropy of preprocessing component distribution
3. **Model Hyperparameter Entropy (H_hyp):** Shannon entropy of hyperparameter distribution
4. **Reproducibility Variance (IQR):** Interquartile range of performance across matched runs

**Loading Information** (for Phase 4 download):
- Method: OpenML Python API (programmatic-api)
- Identifier: openml.datasets.list_datasets(), openml.flows.get_flow(), openml.runs.list_runs()
- Code:
  ```python
  import openml
  # List datasets meeting criteria
  datasets = openml.datasets.list_datasets(output_format='dataframe')
  # Get runs for a task
  runs = openml.runs.list_runs(task=[task_id], output_format='dataframe')
  # Get flow details for preprocessing
  flow = openml.flows.get_flow(flow_id)
  # Get evaluations
  evals = openml.evaluations.list_evaluations(function="predictive_accuracy", 
                                               tasks=[task_id], output_format='dataframe')
  ```

### Models

#### Baseline Model

**Architecture:** Linear Regression (Mediation Analysis Baseline)
**Type:** Statistical model (not neural network)
**Source:** statsmodels / pingouin

**Purpose:** This hypothesis tests a MECHANISM (mediation), not a model performance.
The "baseline" is the null model without mediation path.

**Mediation Model Specification:**
- **Outcome Model (Y):** Reproducibility Variance (IQR) ~ Metadata + Controls
- **Mediator Model (M):** Preprocessing Entropy ~ Metadata + Controls
- **Controls:** Intrinsic stability, popularity, algorithm family, infrastructure

**Loading Information** (for Phase 4 download):
- Method: pip install (pingouin, statsmodels)
- Identifier: pingouin==0.6.1, statsmodels>=0.14.1
- Code:
  ```python
  # Option 1: pingouin (simpler)
  from pingouin import mediation_analysis
  
  # Option 2: statsmodels (more control)
  from statsmodels.stats.mediation import Mediation
  import statsmodels.api as sm
  ```

#### Proposed Model

**Architecture:** Mediation Model (Metadata → Preprocessing Entropy → Variance)

**Causal Path:**
```
Metadata Completeness (X) → Preprocessing Entropy (M) → Reproducibility Variance (Y)
                         └──────────────────────────────────────────────────────────┘
                                          Direct Effect (c')
```

**Core Mechanism Implementation:**

```python
# Core Mechanism: Mediation Analysis for Preprocessing Entropy
# Based on: pingouin.mediation_analysis, statsmodels.stats.mediation

import pandas as pd
import numpy as np
from scipy.stats import entropy
from pingouin import mediation_analysis
import openml

def compute_preprocessing_entropy(flow_components: list) -> float:
    """Compute Shannon entropy of preprocessing component distribution."""
    if not flow_components:
        return 0.0
    from collections import Counter
    counts = Counter(flow_components)
    probs = np.array(list(counts.values())) / sum(counts.values())
    return entropy(probs, base=2)

def compute_hyperparameter_entropy(hyperparams: dict) -> float:
    """Compute entropy of hyperparameter value distribution."""
    values = list(hyperparams.values())
    if not values:
        return 0.0
    # Discretize continuous hyperparams into bins
    # ... binning logic
    return entropy(probs, base=2)

def run_mediation_analysis(df: pd.DataFrame) -> dict:
    """
    Run mediation analysis: M → H_prep → Variance
    
    Args:
        df: DataFrame with columns [metadata_score, prep_entropy, hyp_entropy, iqr, controls...]
    Returns:
        dict with indirect_effect, proportion_mediated, p_value, ci
    """
    result = mediation_analysis(
        data=df,
        x='metadata_score',      # IV: Metadata completeness
        m='prep_entropy',        # Mediator: Preprocessing entropy
        y='iqr',                 # DV: Reproducibility variance
        covar=['stability', 'popularity', 'algo_family'],
        alpha=0.05,
        n_boot=1000,
        seed=42
    )
    
    indirect = result.loc[result['path'] == 'Indirect', 'coef'].values[0]
    total = result.loc[result['path'] == 'Total', 'coef'].values[0]
    proportion_mediated = abs(indirect / total) if total != 0 else 0
    
    return {
        'indirect_effect': indirect,
        'total_effect': total,
        'proportion_mediated': proportion_mediated,
        'p_value': result.loc[result['path'] == 'Indirect', 'pval'].values[0],
        'ci_lower': result.loc[result['path'] == 'Indirect', 'CI2.5'].values[0],
        'ci_upper': result.loc[result['path'] == 'Indirect', 'CI97.5'].values[0]
    }
```

### Training Protocol

**Note:** This is a MECHANISM hypothesis (statistical analysis), not neural network training.

**Analysis Protocol:**
1. **Data Collection:**
   - Query OpenML API for datasets with ≥10 matched runs
   - Extract preprocessing components from flow descriptions
   - Compute metadata completeness scores (5-field checklist)
   
2. **Variable Computation:**
   - Preprocessing Entropy (H_prep): Shannon entropy of preprocessing component families
   - Hyperparameter Entropy (H_hyp): Shannon entropy of hyperparameter distributions
   - IQR: Interquartile range of performance across matched runs

3. **Mediation Analysis:**
   - Bootstrap iterations: n_boot=1000
   - Significance level: alpha=0.05
   - Random seed: 42 (fixed)
   - Method: Bias-corrected bootstrap CIs

4. **Sub-prediction Tests:**
   - P2a: Compare H_prep across metadata quartiles (t-test or ANOVA)
   - P2b: Compare H_hyp across metadata quartiles (should be NS)

### Evaluation

**Primary Metrics:**
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Proportion Mediated | indirect_effect / total_effect | ≥30% |
| Indirect Effect p-value | Bootstrap p-value | <0.05 |
| Sobel Z | indirect / SE_indirect | |Z| > 1.96 |

**Sub-prediction Metrics:**
| Sub-prediction | Test | Success Criterion |
|----------------|------|-------------------|
| P2a | H_prep(Q4) vs H_prep(Q1) | ≥30% reduction, p<0.05 |
| P2b | H_hyp(Q4) vs H_hyp(Q1) | NS (p>0.10) |

**Falsification Criteria:**
- Indirect effect <15% of total effect
- p-value >0.10

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical mediation analysis
- Library: pingouin, scipy.stats
- Code:
  ```python
  from pingouin import mediation_analysis
  from scipy.stats import entropy, ttest_ind
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Mediation Path Diagram**: Shows paths a, b, c' with effect sizes and CIs

#### Additional Figures (LLM Autonomous)

1. **Preprocessing Entropy by Metadata Quartile**: Box plot showing H_prep across Q1-Q4
2. **Hyperparameter Entropy by Metadata Quartile**: Box plot showing H_hyp across Q1-Q4 (expect no difference)
3. **Bootstrap Distribution**: Histogram of indirect effect from n_boot samples
4. **Mediation Proportion Bar Chart**: Proportion mediated vs direct effect

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Indirect effect (mediation) ≥30% of total effect
3. p-value (Sobel test) < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary:** Archon KB did not contain directly relevant content for mediation analysis or OpenML reproducibility research. Queries returned diffusion model documentation (low relevance).

- **Query 1:** "mediation analysis entropy preprocessing" → Diffusion models (irrelevant)
- **Query 2:** "Sobel test bootstrap mediation Python" → Diffusion schedulers (irrelevant)
- **Query 3:** "OpenML reproducibility variance metadata" → Stable diffusion (irrelevant)

**Used For:** N/A — relied on Exa GitHub search for relevant implementations.

### B. GitHub Implementations (Exa)

**Source B.1**: pingouin Documentation
- **URL**: https://pingouin-stats.org/generated/pingouin.mediation_analysis.html
- **Query Used**: "mediation analysis Python statsmodels pingouin Sobel test bootstrap"
- **Relevance**: Bootstrap-based mediation analysis with ACME computation
- **Used For**: Core mechanism implementation (mediation_analysis API)

**Source B.2**: statsmodels.stats.mediation
- **URL**: https://www.statsmodels.org/devel/generated/statsmodels.stats.mediation.Mediation.html
- **Query Used**: Same as B.1
- **Relevance**: Full mediation framework with moderated mediation support
- **Used For**: Fallback implementation, complex model support

**Source B.3**: Experimental-Economics/textbook
- **URL**: https://github.com/Experimental-Economics/textbook/blob/main/Ch.%2008/Exhibit%208.1.3A/code/Exhibit_8.1.3A.py
- **Query Used**: Same as B.1
- **Relevance**: Complete Sobel test implementation with variance formula
- **Used For**: Manual Sobel Z computation reference

**Source B.4**: openml-python
- **URL**: https://openml.github.io/openml-python/
- **Query Used**: "OpenML Python API flow run evaluation preprocessing"
- **Relevance**: Official OpenML API for flow/run/evaluation retrieval
- **Used For**: Dataset specification, data collection protocol

**Source B.5**: scipy.stats.entropy
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html
- **Query Used**: "Shannon entropy scipy.stats categorical distribution Python"
- **Relevance**: Shannon entropy computation for categorical distributions
- **Used For**: Preprocessing entropy and hyperparameter entropy computation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. Using established statistical packages (pingouin, statsmodels, scipy) with well-documented APIs.

### D. Previous Hypothesis Context

**Source**: h-e1 Validation Results (VALIDATED)
- **Key Findings Reused**:
  - Relative IQR reduction: 42.1% (threshold: 20%)
  - Absolute IQR reduction: 0.0197 (threshold: 0.01)
  - 95% CI: [39.1%, 51.7%] excludes <10%
  - p-value < 0.0001
- **Why Reused**: h-m1 tests MECHANISM of effect established by h-e1

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset selection | Phase 2B | 02b_verification_plan.md |
| Data loading | Exa GitHub | B.4 (openml-python) |
| Mediation analysis | Exa GitHub | B.1 (pingouin), B.2 (statsmodels) |
| Sobel test | Exa GitHub | B.3 (Experimental-Economics) |
| Entropy computation | Exa GitHub | B.5 (scipy.stats.entropy) |
| Pseudo-code | Exa GitHub | B.1 + B.5 combined |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md §2.2 |
| Success criteria | Phase 2B | h-m1 gate conditions |
| Previous context | Phase 4 | h-e1 validation results |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-09

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
