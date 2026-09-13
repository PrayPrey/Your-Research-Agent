# Product Requirements Document: h-m1 Benchmark Distinctiveness Analysis

**Hypothesis:** h-m1 (MECHANISM)  
**Date:** 2026-04-15  
**Author:** Phase 3 Implementation Planning  
**Type:** Statistical Analysis - Benchmark Comparison  

---

## 1. Executive Summary

### 1.1 Problem Statement
Analyze execution trace data from 20+ code generation models to determine if different benchmarks (HumanEval, MBPP, APPS) produce distinctive evaluation signatures. This validates whether benchmark design creates meaningful differences in how models are measured, which is critical for understanding what evaluation dimensions exist in code generation assessment.

### 1.2 Success Criteria
- **Primary:** At least one benchmark pair shows ρ (Spearman correlation) < 0.8 AND KL divergence > 0.1
- **Secondary:** Feature distributions show visually distinct patterns across benchmarks
- **Gate:** SHOULD_WORK - Provides evidence for dimensional analysis, but failure leads to pivot

### 1.3 Scope
**In Scope:**
- Statistical analysis of execution trace data from h-e1
- Spearman correlation analysis of model rankings across benchmarks
- KL divergence computation for feature distributions
- Visualization of benchmark distinctiveness patterns
- Cross-benchmark comparison of evaluation signatures

**Out of Scope:**
- New model evaluation or data collection (reuse h-e1 data)
- Model training or fine-tuning
- Deep learning model development
- Manual benchmark annotation

---

## 2. Functional Requirements

### FR-1: Load Execution Trace Data
**Priority:** HIGH  
**Description:** Load and validate execution trace features from h-e1 hypothesis

**Acceptance Criteria:**
- Load complete feature dataset from h-e1 output
- Verify minimum 20 models across 3 benchmarks
- Validate feature completeness (all required features present)
- Data structure: DataFrame with columns [model, benchmark, pass@1, pass@10, pass@100, runtime_q25, runtime_q50, runtime_q75, syntax_errors, logic_errors, resource_errors]

**Implementation Notes:**
```python
import pandas as pd

# Load from h-e1 output
execution_traces = pd.read_csv('../h-e1/execution_traces.csv')
# OR
execution_traces = pd.read_pickle('../h-e1/execution_traces.pkl')

# Validate minimum requirements
assert len(execution_traces['model'].unique()) >= 20
assert set(execution_traces['benchmark'].unique()) >= {'HumanEval', 'MBPP', 'APPS'}
```

### FR-2: Compute Model Ranking Correlations
**Priority:** HIGH  
**Description:** Calculate Spearman correlation between model rankings on different benchmarks

**Acceptance Criteria:**
- Pairwise correlations for all benchmark combinations:
  - HumanEval vs MBPP
  - HumanEval vs APPS
  - MBPP vs APPS
- Statistical significance (p-value) reported for each correlation
- Results stored in correlation matrix format

**Implementation Requirements:**
```python
from scipy.stats import spearmanr

def compute_ranking_correlation(bench1_scores, bench2_scores):
    """
    Compute Spearman correlation between model rankings
    
    Args:
        bench1_scores: Model scores on benchmark 1
        bench2_scores: Model scores on benchmark 2
        
    Returns:
        rho: Spearman correlation coefficient
        p_value: Statistical significance
    """
    # Align models across benchmarks
    common_models = bench1_scores.index.intersection(bench2_scores.index)
    rho, p_value = spearmanr(
        bench1_scores[common_models], 
        bench2_scores[common_models]
    )
    return rho, p_value
```

### FR-3: Compute Feature Distribution Divergence
**Priority:** HIGH  
**Description:** Calculate KL divergence between feature distributions across benchmarks

**Acceptance Criteria:**
- KL divergence computed for each benchmark pair
- Primary feature: pass@1 distribution
- Secondary features: runtime quartiles, error distributions
- Divergence values > 0.1 flagged as "distinctive"

**Implementation Requirements:**
```python
from scipy.stats import entropy
import numpy as np

def compute_kl_divergence(bench1_features, bench2_features):
    """
    Compute KL divergence between feature distributions
    
    Args:
        bench1_features: Feature values from benchmark 1
        bench2_features: Feature values from benchmark 2
        
    Returns:
        kl_div: KL divergence value
    """
    # Normalize to probability distributions
    hist1, bins = np.histogram(bench1_features, bins=20, density=True)
    hist2, _ = np.histogram(bench2_features, bins=bins, density=True)
    
    # Add small epsilon to avoid log(0)
    hist1 = hist1 + 1e-10
    hist2 = hist2 + 1e-10
    
    # Normalize
    hist1 = hist1 / hist1.sum()
    hist2 = hist2 / hist2.sum()
    
    kl_div = entropy(pk=hist1, qk=hist2)
    return kl_div
```

### FR-4: Gate Condition Evaluation
**Priority:** HIGH  
**Description:** Evaluate whether gate condition is satisfied

**Acceptance Criteria:**
- Check: At least one benchmark pair with ρ < 0.8
- Check: At least one benchmark pair with KL divergence > 0.1
- Both conditions must be true for PASS
- Clear logging of which benchmark pair(s) satisfy conditions

**Gate Logic:**
```python
def evaluate_gate(correlations, kl_divergences):
    """
    Evaluate SHOULD_WORK gate condition
    
    Returns:
        pass_gate: Boolean indicating gate satisfaction
        reasons: List of supporting evidence
    """
    has_low_correlation = any(v['rho'] < 0.8 for v in correlations.values())
    has_high_divergence = any(v > 0.1 for v in kl_divergences.values())
    
    pass_gate = has_low_correlation and has_high_divergence
    
    reasons = []
    if has_low_correlation:
        low_corr_pairs = [k for k, v in correlations.items() if v['rho'] < 0.8]
        reasons.append(f"Low correlation pairs: {low_corr_pairs}")
    if has_high_divergence:
        high_div_pairs = [k for k, v in kl_divergences.items() if v > 0.1]
        reasons.append(f"High divergence pairs: {high_div_pairs}")
    
    return pass_gate, reasons
```

### FR-5: Visualization Generation
**Priority:** MEDIUM  
**Description:** Generate visualizations showing benchmark distinctiveness

**Acceptance Criteria:**
- Correlation heatmap (3×3 matrix)
- KL divergence bar chart
- Model ranking scatter plots (pairwise)
- Feature distribution overlays
- All figures saved to h-m1/figures/

**Required Figures:**
1. **Correlation Matrix Heatmap** (MANDATORY - gate metric)
   - 3×3 heatmap with benchmark pairs
   - Color scale: 0.0 (distinctive) to 1.0 (identical)
   - Threshold line at ρ = 0.8
   - Annotations showing exact ρ values

2. **KL Divergence Comparison**
   - Bar chart comparing divergence across benchmark pairs
   - Threshold line at KL = 0.1
   - Error bars if computed over multiple features

3. **Model Ranking Scatter Plots**
   - 3 subplots: HumanEval-MBPP, HumanEval-APPS, MBPP-APPS
   - X-axis: Ranking on benchmark 1
   - Y-axis: Ranking on benchmark 2
   - Diagonal line for perfect agreement
   - ρ value annotated

4. **Feature Distribution Overlays**
   - Overlaid histograms for pass@1 distributions
   - Separate curves for each benchmark
   - KL divergence values annotated

---

## 3. Non-Functional Requirements

### NFR-1: Statistical Rigor
- Use standard scipy.stats implementations
- Report p-values with correlations (significance threshold: p < 0.05)
- Handle missing data appropriately (exclude incomplete pairs)
- Document any statistical assumptions

### NFR-2: Computational Resources
- No GPU required (pure statistical analysis)
- Runtime: < 5 minutes on standard CPU
- Memory: < 4GB (data fits in memory)
- Storage: < 100MB for output figures

### NFR-3: Reproducibility
- Fixed random seed for any stochastic operations
- Exact scipy/numpy/pandas versions specified
- Analysis script can be re-run deterministically
- Results documented in validation report

### NFR-4: Code Quality
- Type hints for all functions
- Docstrings for statistical methods
- Unit tests for core calculations
- Clear variable naming (avoid abbreviations)

---

## 4. Data Specifications

### 4.1 Input Data

**Dataset: h-e1 Execution Traces**
- Source: `../h-e1/execution_traces.csv` or `../h-e1/execution_traces.pkl`
- Size: 60+ rows (20 models × 3 benchmarks)
- Format: Pandas DataFrame
- Required columns:
  - `model`: str (model identifier)
  - `benchmark`: str ("HumanEval" | "MBPP" | "APPS")
  - `pass@1`: float (0.0-1.0)
  - `pass@10`: float (0.0-1.0)
  - `pass@100`: float (0.0-1.0)
  - `runtime_q25`: float (milliseconds)
  - `runtime_q50`: float (milliseconds)
  - `runtime_q75`: float (milliseconds)
  - `error_syntax`: float (percentage, 0.0-100.0)
  - `error_runtime`: float (percentage)
  - `error_timeout`: float (percentage)

**Preprocessing:**
- Log-transform runtime values (handle zeros)
- Percentage-transform pass rates (already in 0-1 range)
- Normalize error distributions to sum to 100%

### 4.2 Output Data Schema

**Analysis Results:**
```python
{
    "correlations": {
        "HumanEval-MBPP": {"rho": float, "p_value": float},
        "HumanEval-APPS": {"rho": float, "p_value": float},
        "MBPP-APPS": {"rho": float, "p_value": float}
    },
    "kl_divergence": {
        "HumanEval-MBPP": float,
        "HumanEval-APPS": float,
        "MBPP-APPS": float
    },
    "gate_satisfied": bool,
    "supporting_evidence": [str]
}
```

**Output Format:** JSON file saved to `h-m1/analysis_results.json`

---

## 5. Evaluation Metrics

### 5.1 Primary Metric: Gate Condition
**Formula:**
```
PASS = (∃ pair: ρ < 0.8) AND (∃ pair: KL > 0.1)
```

**Expected Results (from Phase 2B):**
- HumanEval-MBPP: ρ ~ 0.7-0.8, KL ~ 0.1-0.2
- HumanEval-APPS: ρ ~ 0.5-0.7, KL ~ 0.2-0.3
- MBPP-APPS: ρ ~ 0.5-0.7, KL ~ 0.2-0.3

### 5.2 Secondary Metrics

**Correlation Strength Interpretation:**
- ρ ≥ 0.9: Very high agreement (benchmarks measure same thing)
- 0.7 ≤ ρ < 0.9: High agreement (similar but not identical)
- 0.5 ≤ ρ < 0.7: Moderate agreement (some distinctiveness)
- ρ < 0.5: Low agreement (highly distinctive)

**KL Divergence Interpretation:**
- KL < 0.05: Nearly identical distributions
- 0.05 ≤ KL < 0.1: Small differences
- 0.1 ≤ KL < 0.5: Moderate differences (distinctive)
- KL ≥ 0.5: Large differences (very distinctive)

---

## 6. Visualization Requirements

### 6.1 Required Figure (Gate Metric)
**Correlation Heatmap**
- Dimensions: 3×3 symmetric matrix
- Color map: coolwarm (blue = low correlation, red = high)
- Threshold annotation: horizontal/vertical lines at ρ = 0.8
- Title: "Benchmark Ranking Correlation Matrix"
- Save as: `h-m1/figures/correlation_heatmap.png`

### 6.2 Additional Figures
All figures auto-generated by Phase 4 implementation:

1. **KL Divergence Bar Chart**
   - X-axis: Benchmark pairs
   - Y-axis: KL divergence
   - Threshold line at 0.1
   - Save as: `h-m1/figures/kl_divergence.png`

2. **Ranking Scatter Plots**
   - 3 subplots in single figure
   - Diagonal reference line
   - Save as: `h-m1/figures/ranking_scatters.png`

3. **Distribution Overlays**
   - Overlaid histograms for pass@1
   - Separate colors per benchmark
   - Save as: `h-m1/figures/feature_distributions.png`

4. **Ranking Agreement Diagram** (optional)
   - Alluvial/Sankey showing rank changes
   - Save as: `h-m1/figures/ranking_flow.png`

**Output Location:** All figures saved to `h-m1/figures/` (auto-created)

---

## 7. Dependencies

### 7.1 Python Packages
```
scipy>=1.10.0          # Statistical functions
numpy>=1.24.0          # Numerical operations
pandas>=2.0.0          # Data manipulation
matplotlib>=3.7.0      # Plotting
seaborn>=0.12.0        # Statistical visualizations
```

### 7.2 Data Dependencies
- h-e1 execution trace data (prerequisite hypothesis)
- Minimum 20 models evaluated across 3 benchmarks
- Feature completeness ≥ 95% (from h-e1 validation)

### 7.3 Reference Papers
- Spearman correlation: Standard statistical method
- KL divergence: Kullback-Leibler (1951)
- Benchmark papers (for context):
  - HumanEval: Chen et al. (2021)
  - MBPP: Austin et al. (2021)
  - APPS: Hendrycks et al. (2021)

---

## 8. Risks and Mitigations

### Risk 1: High Correlation Across All Benchmarks
**Impact:** Gate condition fails (ρ ≥ 0.8 for all pairs)  
**Likelihood:** MEDIUM  
**Mitigation:** Pivot to analyzing why benchmarks are more similar than expected; investigate whether difficulty confounds dominate

### Risk 2: Low Statistical Power
**Impact:** Correlations unstable due to small sample size  
**Likelihood:** LOW (20+ models sufficient)  
**Mitigation:** Report confidence intervals; focus on effect sizes not just significance

### Risk 3: Missing Data from h-e1
**Impact:** Incomplete benchmark coverage reduces comparability  
**Likelihood:** LOW (h-e1 validated ≥95% completeness)  
**Mitigation:** Use pairwise complete observations; document any exclusions

### Risk 4: Confounding by Difficulty
**Impact:** Correlations reflect task difficulty not evaluation philosophy  
**Likelihood:** MEDIUM  
**Mitigation:** Secondary analysis controlling for difficulty (out of scope for PoC, noted for interpretation)

---

## 9. Acceptance Criteria Summary

**Phase 3 → Phase 4 Handoff:**
- [x] h-e1 execution trace data accessible
- [x] Statistical methods specified (Spearman correlation, KL divergence)
- [x] Gate condition clearly defined (ρ < 0.8 AND KL > 0.1)
- [x] Visualization requirements documented
- [x] Analysis output schema defined

**Phase 4 Implementation Complete:**
- [ ] All pairwise correlations computed
- [ ] All KL divergences computed
- [ ] Gate condition evaluated
- [ ] All required figures generated
- [ ] Results saved to analysis_results.json
- [ ] Validation report documents findings

---

## 10. Appendix

### A. Analysis Workflow Pseudo-code
```python
class BenchmarkDistinctivenessAnalyzer:
    """Analyzes whether benchmarks create distinctive evaluation signatures"""
    
    def __init__(self, execution_traces_df):
        self.data = execution_traces_df
        self.benchmarks = ['HumanEval', 'MBPP', 'APPS']
        
    def compute_ranking_correlation(self, bench1, bench2):
        """Compute Spearman ρ between model rankings"""
        scores1 = self.data[self.data['benchmark'] == bench1].set_index('model')['pass@1']
        scores2 = self.data[self.data['benchmark'] == bench2].set_index('model')['pass@1']
        common_models = scores1.index.intersection(scores2.index)
        rho, p_value = spearmanr(scores1[common_models], scores2[common_models])
        return rho, p_value
    
    def compute_kl_divergence(self, bench1, bench2, feature='pass@1'):
        """Compute KL divergence between feature distributions"""
        dist1 = self.data[self.data['benchmark'] == bench1][feature].values
        dist2 = self.data[self.data['benchmark'] == bench2][feature].values
        
        # Normalize to probability distributions
        hist1, bins = np.histogram(dist1, bins=20, density=True)
        hist2, _ = np.histogram(dist2, bins=bins, density=True)
        hist1 = (hist1 + 1e-10) / (hist1 + 1e-10).sum()
        hist2 = (hist2 + 1e-10) / (hist2 + 1e-10).sum()
        
        kl_div = entropy(pk=hist1, qk=hist2)
        return kl_div
    
    def analyze_distinctiveness(self):
        """Main analysis: Test if benchmarks show distinctive signatures"""
        results = {
            'correlations': {},
            'kl_divergence': {},
            'gate_satisfied': False,
            'supporting_evidence': []
        }
        
        # Pairwise analysis
        for i, bench1 in enumerate(self.benchmarks):
            for bench2 in self.benchmarks[i+1:]:
                pair_name = f'{bench1}-{bench2}'
                
                # Correlation
                rho, p = self.compute_ranking_correlation(bench1, bench2)
                results['correlations'][pair_name] = {'rho': rho, 'p_value': p}
                
                # KL divergence
                kl = self.compute_kl_divergence(bench1, bench2)
                results['kl_divergence'][pair_name] = kl
        
        # Gate evaluation
        has_low_corr = any(v['rho'] < 0.8 for v in results['correlations'].values())
        has_high_div = any(v > 0.1 for v in results['kl_divergence'].values())
        results['gate_satisfied'] = has_low_corr and has_high_div
        
        return results
```

### B. Expected Computation Time
- Data loading: < 1 second
- Correlation computation: < 5 seconds (3 pairs)
- KL divergence computation: < 10 seconds (3 pairs × multiple features)
- Visualization: < 30 seconds (4 figures)
- **Total:** < 1 minute

### C. Output File Structure
```
h-m1/
├── 02c_experiment_brief.md  (input from Phase 2C)
├── 03_prd.md                (this document)
├── 03_architecture.md       (next: Phase 3)
├── 03_logic.md              (next: Phase 3)
├── 03_config.md             (next: Phase 3)
├── analysis_results.json    (output from Phase 4)
├── 04_validation.md         (output from Phase 4)
└── figures/
    ├── correlation_heatmap.png
    ├── kl_divergence.png
    ├── ranking_scatters.png
    └── feature_distributions.png
```

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)  
**Prerequisite:** h-e1 execution trace data (COMPLETED)
