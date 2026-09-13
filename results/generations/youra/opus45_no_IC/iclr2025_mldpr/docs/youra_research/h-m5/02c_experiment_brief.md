# Experiment Design: H-M5

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Concentration-diversity cycle reinforces itself via positive feedback loop
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal feedback loop via lagged panel regression.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M4 PASSED)
**Gate Status:** SHOULD_WORK (pending verification)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M5
- **Type:** MECHANISM
- **Prerequisites:** H-M4 (COMPLETED)

### Gate Condition
- **Type:** SHOULD_WORK
- **Primary:** β(HHI_{t-1}) < 0 with p < 0.05
- **Secondary:** HHI Granger-causes entropy (not reverse)
- **If Fail:** Report as correlation only, abandon causal claim

---

## Continuation Context

Building on H-M4 validation showing strong negative correlation (ρ=-0.958) between entropy and cross-benchmark variance, H-M5 tests the temporal-causal mechanism: does concentration PRECEDE diversity decline?

### Previous Hypothesis Results (if applicable)
- **H-E1:** 21/21 venue-years have valid HHI (mean=0.23, range 0.16-0.28)
- **H-M1:** High-HHI group has higher top-5 share (p<0.001, ρ=0.9)
- **H-M2:** Higher HHI predicts standard benchmark adoption (β=56.75, p<0.001)
- **H-M3:** Citing pairs have higher dataset overlap (Cohen's d=1.93)
- **H-M4:** Negative correlation between entropy and variance (ρ=-0.958)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB lacks panel regression/econometrics examples (ML-focused). No relevant results for "panel regression fixed effects Granger causality".

### Archon Code Examples

No relevant code examples found. Archon KB contains primarily ML/DL pipeline code (diffusers, stable diffusion), not econometric analysis code.

### Exa GitHub Implementations

**Primary Finding: linearmodels.PanelOLS**
- Source: https://bashtage.github.io/linearmodels/panel/introduction.html
- Repository: https://github.com/bashtage/linearmodels (1054 stars)
- Features: Entity effects, time effects, two-way fixed effects
- Formula interface: `PanelOLS.from_formula('y ~ x + EntityEffects + TimeEffects', data)`

**Secondary Finding: statsmodels.grangercausalitytests**
- Source: https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html
- Four tests: params_ftest, ssr_ftest, ssr_chi2test, lrtest
- Null hypothesis: x2 does NOT Granger-cause x1
- Usage: `grangercausalitytests(data[['x1', 'x2']], maxlag=2)`

### 🎯 Implementation Priority Assessment

**CRITICAL: For panel regression with fixed effects, use established econometrics libraries**

1. **linearmodels.PanelOLS** - Gold standard for panel fixed effects in Python
2. **statsmodels.grangercausalitytests** - Standard implementation for Granger causality
3. Both libraries well-maintained, documented, widely used in academic research

**Recommended Implementation Path:**
- Primary: linearmodels.PanelOLS with entity_effects=True, time_effects=True
- Fallback: statsmodels OLS with manual dummy variables (slower but equivalent)
- Justification: linearmodels designed specifically for panel data; avoids dummy variable explosion

### Code Analysis (Serena MCP)

*Skipped* - No local codebase for statistical analysis. This is a new econometric pipeline using external libraries.

---

## Experiment Specification

### Dataset

**Name:** H-E1 Panel Dataset (derived from Papers With Code)
**Type:** standard (reuse from H-E1)
**Source:** PWC API cached data from H-E1 validation
**Format:** Panel data with 21 venue-year observations

| Field | Description |
|-------|-------------|
| venue | NeurIPS, ICML, ICLR |
| year | 2018-2024 |
| hhi | Herfindahl-Hirschman Index (0-1) |
| entropy | Normalized Shannon entropy (0-1) |
| paper_count | Number of papers per venue-year |
| hhi_lag1 | HHI from previous year |
| delta_hhi | Year-over-year HHI change |
| delta_entropy | Year-over-year entropy change |

**Sample Size:** 21 venue-years (3 venues × 7 years)
**Note:** Small N panel; statistical power limited. Report confidence intervals.

**Loading Information** (for Phase 4 download):
- Method: Load from H-E1 cache
- Identifier: `docs/youra_research/h-e1/data/venue_year_metrics.csv`
- Code:
```python
import pandas as pd
df = pd.read_csv('docs/youra_research/h-e1/data/venue_year_metrics.csv')
df = df.set_index(['venue', 'year'])  # MultiIndex for panel
```

### Models

#### Baseline Model

**Model:** Pooled OLS (no fixed effects)
**Specification:** Entropy_t ~ HHI_{t-1}
**Purpose:** Naive correlation baseline without controlling for venue/time heterogeneity

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `linearmodels>=7.0`
- Code:
```python
from linearmodels.panel import PooledOLS
import statsmodels.api as sm

exog = sm.add_constant(df[['hhi_lag1', 'paper_count']])
baseline = PooledOLS(df['entropy'], exog)
baseline_res = baseline.fit()
```

#### Proposed Model

**Architecture:** Lagged Panel Regression with Two-Way Fixed Effects

**Model Specification:**
```
Entropy_{it} = α_i + γ_t + β₁·HHI_{i,t-1} + β₂·PaperCount_{it} + ε_{it}
```

Where:
- α_i = venue fixed effects (absorb time-invariant venue characteristics)
- γ_t = year fixed effects (absorb common temporal shocks)
- β₁ = coefficient of interest (expected < 0)
- β₂ = control for venue size

**Core Mechanism Implementation:**

```python
# H-M5: Lagged Panel Regression with Fixed Effects
# Tests: Does HHI_{t-1} predict Entropy_t?

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
from statsmodels.tsa.stattools import grangercausalitytests
import statsmodels.api as sm

def run_h_m5_analysis(df: pd.DataFrame) -> dict:
    """
    Run H-M5 lagged panel regression and Granger causality tests.
    
    Args:
        df: Panel data with columns [venue, year, hhi, entropy, paper_count]
            Index: MultiIndex (venue, year)
    
    Returns:
        dict with beta, p_value, granger_results, gate_passed
    """
    # 1. Create lagged variables
    df = df.sort_index()
    df['hhi_lag1'] = df.groupby('venue')['hhi'].shift(1)
    df['entropy_lag1'] = df.groupby('venue')['entropy'].shift(1)
    df = df.dropna()  # Drop first year per venue (no lag)
    
    # 2. Run Panel OLS with entity + time effects
    exog = sm.add_constant(df[['hhi_lag1', 'paper_count']])
    model = PanelOLS(
        dependent=df['entropy'],
        exog=exog,
        entity_effects=True,  # Venue FE
        time_effects=True     # Year FE
    )
    results = model.fit(cov_type='clustered', cluster_entity=True)
    
    beta_hhi = results.params['hhi_lag1']
    p_value = results.pvalues['hhi_lag1']
    conf_int = results.conf_int().loc['hhi_lag1']
    
    # 3. Granger causality test (per venue, then aggregate)
    granger_results = {}
    for venue in df.index.get_level_values('venue').unique():
        venue_data = df.loc[venue][['entropy', 'hhi']].values
        if len(venue_data) >= 4:  # Need enough lags
            gc = grangercausalitytests(venue_data, maxlag=2, verbose=False)
            granger_results[venue] = {
                lag: gc[lag][0]['ssr_ftest'][1]  # p-value
                for lag in gc.keys()
            }
    
    # 4. Reverse Granger test (entropy -> hhi)
    reverse_granger = {}
    for venue in df.index.get_level_values('venue').unique():
        venue_data = df.loc[venue][['hhi', 'entropy']].values
        if len(venue_data) >= 4:
            gc = grangercausalitytests(venue_data, maxlag=2, verbose=False)
            reverse_granger[venue] = {
                lag: gc[lag][0]['ssr_ftest'][1]
                for lag in gc.keys()
            }
    
    # 5. Gate evaluation
    gate_passed = (beta_hhi < 0) and (p_value < 0.05)
    
    return {
        'beta_hhi_lag1': beta_hhi,
        'p_value': p_value,
        'conf_int_lower': conf_int[0],
        'conf_int_upper': conf_int[1],
        'r_squared': results.rsquared,
        'granger_hhi_to_entropy': granger_results,
        'granger_entropy_to_hhi': reverse_granger,
        'gate_passed': gate_passed,
        'n_observations': len(df),
        'full_results': results
    }
```

### Training Protocol

**N/A** - This is a statistical analysis, not ML training.

**Analysis Protocol:**
1. Load panel data from H-E1 cache
2. Create lagged variables (HHI_{t-1})
3. Drop first year per venue (no lag available)
4. Fit PanelOLS with entity + time fixed effects
5. Extract β(HHI_{t-1}) and p-value
6. Run Granger causality tests (both directions)
7. Evaluate gate condition

**Robustness Checks:**
- Alternative lag structure (2-year lag)
- Without time fixed effects
- Using ΔHHI instead of level HHI_{t-1}

### Evaluation

**Primary Metric:** β(HHI_{t-1}) coefficient sign and significance
- **Pass:** β < 0 AND p < 0.05
- **Fail:** β ≥ 0 OR p ≥ 0.05

**Secondary Metric:** Granger causality direction
- **Strong Pass:** HHI Granger-causes entropy (p < 0.05) AND entropy does NOT Granger-cause HHI (p > 0.05)
- **Weak Pass:** HHI Granger-causes entropy only
- **Fail:** No Granger causality or bidirectional

**Effect Size:** Report 95% confidence interval for β

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical hypothesis testing
- Library: linearmodels, statsmodels
- Code:
```python
from linearmodels.panel import PanelOLS
from statsmodels.tsa.stattools import grangercausalitytests
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: β coefficient with 95% CI, significance threshold line

#### Additional Figures (LLM Autonomous)
1. **Scatter plot**: HHI_{t-1} vs Entropy_t with regression line, colored by venue
2. **Time series**: HHI and entropy trends per venue (line plot, dual y-axis)
3. **Granger causality heatmap**: p-values for both directions across lags
4. **Residual diagnostic**: QQ plot and residuals vs fitted

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m5/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. β(HHI_{t-1}) < 0 with p < 0.05
3. Granger causality: HHI → entropy (p < 0.05 for at least 1 lag)

**PoC Interpretation:**
- If PASS: Concentration temporally precedes diversity decline, supporting causal mechanism
- If FAIL (β≥0 or p≥0.05): Report as correlation only, no causal claim

---

## Appendix: Reference Implementations

### linearmodels PanelOLS
- Documentation: https://bashtage.github.io/linearmodels/panel/introduction.html
- GitHub: https://github.com/bashtage/linearmodels
- Key example:
```python
from linearmodels.panel import PanelOLS
mod = PanelOLS.from_formula(
    'y ~ 1 + x + EntityEffects + TimeEffects', 
    data=data.set_index(['entity', 'time'])
)
res = mod.fit(cov_type='clustered', cluster_entity=True)
```

### statsmodels Granger Causality
- Documentation: https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html
- Key example:
```python
from statsmodels.tsa.stattools import grangercausalitytests
# Column order matters: [effect, cause]
gc_res = grangercausalitytests(data[['entropy', 'hhi']], maxlag=2)
# Null: hhi does NOT Granger-cause entropy
# Reject null if p < 0.05
```

### Dependencies
```
linearmodels>=7.0
statsmodels>=0.14
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-M5 set to IN_PROGRESS (Phase 2C start)
- 2026-08-10: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
