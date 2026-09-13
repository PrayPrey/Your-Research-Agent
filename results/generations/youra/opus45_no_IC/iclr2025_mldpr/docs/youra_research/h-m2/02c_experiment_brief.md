# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Convergence creates implicit evaluation standards
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal mechanism in epistemic lock-in chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASSED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (High HHI indicates community convergence)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass Condition:** Higher HHI predicts higher standard-benchmark adoption (β > 0, p < 0.05)
- **Fail Action:** Document as limitation, explore direct norm measurement

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

From `h-m1/04_validation.md`:
- **Gate Status:** PASSED
- **Mann-Whitney U:** 104.0, p = 0.000319
- **Spearman ρ:** 0.90, p = 2.79e-08
- **High-HHI mean top-5 share:** 0.226
- **Low-HHI mean top-5 share:** 0.147

**Proven:** HHI correctly indicates benchmark concentration. High HHI = few datasets dominate.

**Reuse for H-M2:** 
- Same PWC dataset (venue-year aggregated data)
- Same HHI computation pipeline
- Add: new paper benchmark choice analysis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query:** "benchmark adoption implicit standards evaluation norms"

Limited direct matches. Relevant conceptual frameworks:
- Benchmark performativity literature (MacKenzie framework)
- Evaluation standard emergence in ML communities
- OpenReview paper M3Y74vmsMcY on evaluation practices

### Archon Code Examples

No direct code examples for benchmark adoption prediction. Training/prediction code patterns available for general ML pipelines.

### Exa GitHub Implementations

**Key Repositories Found:**

1. **elliottower/benchmarks-engines** (MIT License)
   - Explores how benchmarks shape ML research
   - Covers benchmark adoption dynamics over time
   - Topics: benchmarks, machine-learning, performativity, sociology-of-science

2. **nandomp/AI_Research_Dynamics** (10 stars)
   - "Research Community Dynamics behind Popular AI Benchmarks"
   - Analysis of 25 PWC benchmarks, ~2000 result entries
   - Methodology for exploring competition/collaboration dynamics
   - Published: Nature Machine Intelligence 2021

3. **paperswithcode/paperswithcode-data** (934 stars)
   - Full PWC dataset archive (frozen as of July 2025)
   - Contains paper-dataset links for historical analysis

### Implementation Priority Assessment

**CRITICAL: For bibliometric/metascience experiments, prioritize established datasets**

**Recommended Implementation Path:**
- Primary: Papers With Code archived data (paperswithcode-data)
- Fallback: Semantic Scholar API for paper metadata enrichment
- Justification: PWC provides direct paper-dataset links; frozen archive ensures reproducibility

### Code Analysis (Serena MCP)

Not applicable - this is a statistical/econometric analysis, not code modification experiment.

---

## Experiment Specification

### Dataset

**Dataset:** Papers With Code Paper-Dataset Links (PWC Archive)
**Type:** standard (frozen archive)
**Source:** https://github.com/paperswithcode/paperswithcode-data

**Statistics:**
- Papers: ~80,000+ with dataset tags
- Venues: NeurIPS, ICML, ICLR (2018-2024)
- Venue-years: 21 combinations
- Expected papers per venue-year: ~1,000-3,000

**Loading Information** (for Phase 4 download):
- Method: GitHub archive + CSV/JSON parsing
- Identifier: `paperswithcode/paperswithcode-data`
- Code:
```python
# Clone or download PWC archive
# git clone https://github.com/paperswithcode/paperswithcode-data.git
import pandas as pd
papers_df = pd.read_json("paperswithcode-data/papers-with-abstracts.json")
datasets_df = pd.read_json("paperswithcode-data/datasets.json")
# Filter to target venues and years
```

**Preprocessing:**
1. Filter papers to NeurIPS/ICML/ICLR (2018-2024)
2. Extract dataset tags per paper
3. Identify "standard" datasets (top-5 by usage in prior year per venue)
4. Label each paper's benchmark choice: standard (1) vs novel (0)

### Models

#### Baseline Model

**Architecture:** Logistic Regression (Standard Benchmark Adoption Prediction)
**Type:** statistical
**Configuration:**
- DV: Binary (standard_benchmark_used: 0/1)
- IV: Prior-year venue HHI (continuous)
- No covariates (baseline)

**Loading Information** (for Phase 4):
- Method: sklearn
- Identifier: `sklearn.linear_model.LogisticRegression`
- Code:
```python
from sklearn.linear_model import LogisticRegression
baseline_model = LogisticRegression(random_state=42)
```

#### Proposed Model

**Architecture:** Logistic Regression with Controls

**Core Mechanism Implementation:**

```python
# Core Mechanism: Standard Benchmark Adoption Prediction
# Based on: H-M2 hypothesis - HHI predicts benchmark conformity

import pandas as pd
import statsmodels.api as sm
from scipy import stats

class BenchmarkAdoptionAnalyzer:
    """
    Tests if higher venue HHI predicts higher standard-benchmark adoption.
    IV: Prior-year HHI (lagged)
    DV: Binary standard_benchmark_used
    """
    def __init__(self, papers_df, hhi_df):
        self.papers = papers_df  # paper_id, venue, year, datasets_used
        self.hhi = hhi_df        # venue, year, hhi_score

    def compute_standard_datasets(self, venue, year):
        """Top-5 datasets by usage in prior year = 'standard'"""
        prior_year = year - 1
        prior_papers = self.papers[
            (self.papers['venue'] == venue) & 
            (self.papers['year'] == prior_year)
        ]
        # Explode dataset lists, count, get top-5
        dataset_counts = prior_papers['datasets_used'].explode().value_counts()
        return set(dataset_counts.head(5).index)

    def label_papers(self):
        """Label each paper: uses standard benchmark (1) or novel (0)"""
        results = []
        for _, paper in self.papers.iterrows():
            standards = self.compute_standard_datasets(paper['venue'], paper['year'])
            uses_standard = any(d in standards for d in paper['datasets_used'])
            prior_hhi = self.hhi[
                (self.hhi['venue'] == paper['venue']) & 
                (self.hhi['year'] == paper['year'] - 1)
            ]['hhi_score'].values
            if len(prior_hhi) > 0:
                results.append({
                    'paper_id': paper['paper_id'],
                    'venue': paper['venue'],
                    'year': paper['year'],
                    'standard_benchmark': int(uses_standard),
                    'prior_hhi': prior_hhi[0]
                })
        return pd.DataFrame(results)

    def fit_model(self, df, add_controls=False):
        """Logistic regression: P(standard) ~ prior_HHI"""
        X = df[['prior_hhi']]
        if add_controls:
            # Add venue dummies (topic proxy)
            X = pd.concat([X, pd.get_dummies(df['venue'], prefix='venue')], axis=1)
        X = sm.add_constant(X)
        y = df['standard_benchmark']
        model = sm.Logit(y, X).fit(disp=0)
        return model
```

### Training Protocol

**Analysis Type:** Cross-sectional logistic regression (not iterative training)

**Procedure:**
1. Load PWC archive data
2. Filter to target venues (NeurIPS, ICML, ICLR) and years (2019-2024, need 2018 for lag)
3. Compute prior-year standard datasets per venue
4. Label papers as standard/novel benchmark users
5. Merge with HHI data from H-E1 output
6. Fit logistic regression: P(standard) ~ prior_HHI

**Model Specifications:**
- Model 1 (Baseline): P(standard) ~ prior_HHI
- Model 2 (With Controls): P(standard) ~ prior_HHI + venue_dummies

**Seeds:** 1 (fixed at 42 for reproducibility)

**No hyperparameter tuning required** - standard logistic regression.

### Evaluation

**Primary Metrics:**
- β(prior_HHI): Coefficient for HHI effect on standard adoption
- p-value: Statistical significance of β
- Odds Ratio: exp(β) interpretation

**Success Criteria:**
- **Gate Pass:** β > 0 AND p < 0.05
- **Interpretation:** Higher prior-year HHI increases probability of using standard benchmarks

**Expected Baseline Performance:**
- Based on H-M1 results (strong HHI-concentration correlation), expect moderate positive effect
- Expected β range: 0.5 - 2.0 (log-odds scale)
- Expected OR range: 1.6 - 7.4

**Metrics Loading Information:**
- Task Type: binary_classification / logistic_regression
- Library: statsmodels
- Code:
```python
import statsmodels.api as sm
model = sm.Logit(y, X).fit()
print(f"β(HHI) = {model.params['prior_hhi']:.4f}")
print(f"p-value = {model.pvalues['prior_hhi']:.4f}")
print(f"OR = {np.exp(model.params['prior_hhi']):.4f}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: β coefficient with 95% CI, p-value annotation

#### Additional Figures (LLM Autonomous)
- HHI vs adoption rate scatter plot by venue
- Predicted probability curve across HHI range
- Model comparison table (baseline vs with controls)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - Standard/novel classification computable from PWC data
- **mechanism_isolatable:** True - Prior-year HHI is exogenous to current paper choices
- **baseline_measurable:** True - Logistic regression without HHI provides null baseline

### Architecture Compatibility
- **Compatible:** Yes - Statistical analysis on tabular data, no architecture constraints

### Activation Indicators
- **mechanism_log_message:** "Computing standard benchmark adoption rates..."
- **tensor_shape_change:** N/A (tabular data)
- **metric_delta_expected:** β(HHI) should be > 0 if mechanism active

### Verification Code
```python
def verify_mechanism_activation(model_results):
    """Check that HHI effect is in expected direction"""
    beta_hhi = model_results.params.get('prior_hhi', 0)
    p_value = model_results.pvalues.get('prior_hhi', 1.0)
    
    activation_checks = {
        'coefficient_positive': beta_hhi > 0,
        'statistically_significant': p_value < 0.05,
        'effect_meaningful': abs(beta_hhi) > 0.1  # non-trivial effect
    }
    
    mechanism_activated = all(activation_checks.values())
    return mechanism_activated, activation_checks
```

### Success Thresholds
- **hypothesis_support_threshold:** β > 0, p < 0.05
- **hypothesis_support_metric:** Logistic regression coefficient and p-value

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. β(prior_HHI) > 0 (positive effect direction)
3. p < 0.05 (statistically significant)

---

## Appendix: Reference Implementations

### Primary References

1. **Martinez-Plumed et al. (2021)** - "Research Community Dynamics behind Popular AI Benchmarks"
   - Nature Machine Intelligence
   - GitHub: nandomp/AI_Research_Dynamics
   - Methodology for analyzing PWC benchmark dynamics

2. **Papers With Code Data Archive**
   - GitHub: paperswithcode/paperswithcode-data
   - Frozen dataset for reproducible analysis

3. **MacKenzie Framework (Performativity)**
   - Theoretical basis for benchmark-as-engine hypothesis
   - Referenced in elliottower/benchmarks-engines

### Code Snippets

**PWC Data Loading (from Exa search):**
```python
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()
# Or use archived JSON directly
papers = pd.read_json("papers-with-abstracts.json")
```

**Logistic Regression (statsmodels):**
```python
import statsmodels.api as sm
X = sm.add_constant(df[['prior_hhi']])
model = sm.Logit(df['standard_benchmark'], X).fit()
print(model.summary())
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T12:30:00Z

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS: 2026-08-10T12:13:13Z
- Phase 2C experiment design: IN_PROGRESS

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
