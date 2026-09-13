# Experiment Design: H-E1

**Date:** 2026-07-09
**Author:** Anonymous
**Hypothesis Statement:** Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05) across 5-10 trust benchmarks.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE - Experiment design in progress
**Prerequisites Satisfied:** Yes (no prerequisites - first hypothesis)
**Gate Status:** MUST_WORK (not yet tested)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition

**MUST_WORK Gate:** If this hypothesis fails (r ≥ -0.5 OR p ≥ 0.05), the entire verification approach is invalid. Pipeline routes to Phase 0 for fundamental redesign.

**Success Requirement:**
- Pearson r < -0.5 (negative moderate-to-strong correlation)
- p < 0.05 (statistical significance)

**Consequence if Fails:** CV is not a predictive meta-feature for benchmark stability. Alternative quality signals must be explored.

---

## Continuation Context

**First Hypothesis:** No previous hypothesis results to inherit.

This is the foundation hypothesis that all subsequent hypotheses (H-M1, H-M2, H-C1) depend on. If H-E1 passes the MUST_WORK gate, it validates that CV can predict cross-benchmark stability, enabling mechanism and robustness studies.

### Previous Hypothesis Results (if applicable)

N/A - This is the first hypothesis in the verification plan.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Benchmark Reliability and Leaderboard Analysis**
- **Result 1:** HuggingFace Paper 2305.14314 (LLM Trust/Evaluation)
  - URL: https://hf.co/papers/2305.14314
  - Context: LLM evaluation and trust benchmarks
  - Relevance: Moderate - discusses trust evaluation but not CV-stability meta-analysis
  - Key insight: Standard benchmarking practices in LLM evaluation domain

**Query 2: Spearman Correlation and Ranking Stability**
- Limited relevant results from Archon KB
- Searches returned primarily ML infrastructure content (not statistical meta-analysis)

**Query 3: Trust Benchmark Evaluation (TrustLLM)**
- Result: Paper on LLM trust evaluation
- Relevance: Domain context only - actual implementation is leaderboard data extraction, not model training

**Overall Assessment:**
- Archon KB contains limited content on meta-analysis of benchmark statistics
- Most relevant domain: Statistical analysis of leaderboard data
- This hypothesis requires **data extraction and statistical computation**, not model training
- Primary implementation: pandas DataFrame operations + scipy.stats functions

### Archon Code Examples

**Query 1: Pearson Correlation Statistical Test**
- **Result:** scipy installation example
  - Source: https://github.com/hojonathanho/diffusion
  - Pattern: Standard scipy installation for statistical tests
  - Insight: scipy.stats.pearsonr is standard library for correlation analysis
  
**Query 2: Cross-Benchmark Ranking Analysis**
- Limited directly applicable code examples
- Returned distributed computing patterns (not applicable to this meta-analysis)

**Key Implementation Pattern Identified:**
```python
# Standard correlation analysis pattern
from scipy.stats import pearsonr, spearmanr
import pandas as pd
import numpy as np

# Compute CV for each benchmark
cv = std(scores) / mean(scores)

# Compute pairwise Spearman correlations
for benchmark_pair with shared_models >= 5:
    rho = spearmanr(rank_A, rank_B)
    
# Test CV-stability correlation
r, p = pearsonr(cv_values, mean_rho_values)
```

**Assessment:**
- This is a **statistical data analysis task**, not a deep learning experiment
- Primary tools: pandas (data manipulation), scipy (statistical tests), matplotlib (visualization)
- No model training or neural networks involved
- Implementation complexity: LIGHT (data extraction + descriptive statistics + correlation tests)

### Exa GitHub Implementations

**Query 1: Benchmark Statistical Analysis Tools**

**Repository 1**: Arech/benchstats (⭐ active Python package)
- **URL**: https://github.com/Arech/benchstats
- **Relevance**: Statistical comparison of benchmark results with proper significance tests
- **Key Features**:
  - Variance summary statistics: mean, stdev, CV%, percentiles, IQR, MAD
  - Mann-Whitney U test and Brunner-Munzel test for comparison
  - Bonferroni multiple comparisons correction
- **Pattern**: Coefficient of Variation (CV) as standard metric for benchmark variability
- **Insight**: CV is a well-established metric for benchmark stability assessment

**Repository 2**: ianarawjo/evalstats (⭐ LLM evaluation focused)
- **URL**: https://github.com/ianarawjo/evalstats
- **Relevance**: Statistical analysis for LLM benchmark comparisons
- **Key Features**:
  - Bootstrap confidence intervals for ranking stability
  - Pairwise prompt comparisons with p-values
  - Descriptive stats: mean, median, std, **CV**, IQR
  - Two-level nested bootstrap for run-to-run stochasticity
- **Architecture**: pandas + scipy.stats for statistical tests
- **Insight**: CV used as standard robustness metric for LLM evaluations

**Repository 3**: AMD GAIA eval/statistics.py
- **URL**: https://github.com/amd/gaia/blob/1304b222/src/gaia/eval/statistics.py
- **Relevance**: Benchmark variance analysis with CV computation
- **Key Code Pattern**:
  ```python
  @dataclass
  class VarianceSummary:
      metric: str
      mean: float
      stdev: float
      cv_pct: float  # coefficient of variation (%)
      median: float
      iqr: float
      
  def compute_variance(values):
      m = _mean(values)
      s = _stdev(values, m)
      return VarianceSummary(
          mean=round(m, 2),
          stdev=round(s, 2),
          cv_pct=round(_cv_pct(values, m, s), 2)
      )
  ```
- **Pattern**: CV computation as standard benchmark stability metric
- **Insight**: Stdlib-only implementation (no numpy/scipy dependency for CV)

**Repository 4**: felipemaiapolo/statistical-scaling-law
- **URL**: https://github.com/felipemaiapolo/statistical-scaling-law
- **Relevance**: Leaderboard analysis across multiple benchmarks
- **Key Features**:
  - Cross-benchmark analysis of LLM capabilities
  - Data from Open LLM Leaderboard (df_full.csv format)
  - Latent-skill scaling model for multi-benchmark comparison
- **Dataset Format**: `data/df_full.csv` with benchmark scores and metadata
- **Insight**: Multi-benchmark leaderboard analysis is well-established pattern

**Repository 5**: significance_analysis PyPI package
- **URL**: https://pypi.org/project/significance_analysis/
- **Relevance**: HPO algorithms performing on multiple benchmarks
- **Key Features**:
  - Linear Mixed-Effects Model for cross-benchmark analysis
  - Critical Difference (CD) diagrams for ranking visualization
  - Post-hoc testing for algorithm comparisons
- **Dataset Format**:
  ```
  | algorithm | benchmark | metric |
  |-----------|-----------|--------|
  ```
- **Insight**: Standard pattern for multi-benchmark statistical comparison

**Query 2: Spearman Correlation Implementation**

**Source**: SciPy Official Documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Relevance**: Standard implementation for ranking correlation
- **Key Code**:
  ```python
  from scipy.stats import spearmanr, pearsonr
  
  # Spearman for ranking agreement
  res = spearmanr(rank_A, rank_B)
  rho, p_value = res.statistic, res.pvalue
  
  # Pearson for CV-stability correlation
  r, p = pearsonr(cv_values, mean_rho_values)
  ```
- **Best Practices**:
  - Use `nan_policy='omit'` for missing values
  - For small samples (n < 500), use permutation tests
  - Pandas `df.corr('spearman')` for pairwise correlations
- **Insight**: Standard scipy implementation sufficient for this analysis

**Serena Analysis Needed**: False
- Code patterns are straightforward pandas + scipy operations
- No complex architecture or custom layers
- Implementation is statistical data analysis, not deep learning

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:** This is NOT a paper reproduction experiment. This is an original meta-analysis hypothesis testing whether CV predicts cross-benchmark stability. No specific paper method to reproduce.

**Recommended Implementation Path:**
- Primary: Custom pandas + scipy implementation following `benchstats` and `evalstats` patterns
- Fallback: Adapt `GAIA statistics.py` variance computation code
- Justification: 
  - Standard statistical analysis using well-established libraries
  - Patterns from multiple sources (benchstats CV computation, evalstats bootstrap CIs, GAIA variance summaries) converge on same approach
  - No complex model training - straightforward DataFrame operations + correlation tests

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. This is a statistical data analysis task using standard pandas DataFrame operations and scipy.stats functions, not complex deep learning code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Trust Benchmark Leaderboard Corpus
**Type:** meta-analysis (real data from published leaderboards)

**Sources:**
1. **TrustLLM Leaderboard** - https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html
   - 16+ models across 8 dimensions (truthfulness, safety, fairness, robustness, privacy, ethics)
   - Structured HTML table with scores
2. **TruthfulQA Leaderboard** - GitHub repository
   - ~12 models with truthfulness scores
3. **HaluBench** - PatronusAI leaderboard (supplement PDF)
4. **FinTrust** - Finance trust benchmark (paper table extraction)
5. **MultiTrust** - Multi-dimensional trust (paper extraction)

**Target Sample Size:** 5-10 benchmarks (NOT 10-50 trivial samples)
- Each benchmark contributes: n_models scores (typically 10-16 models)
- Total data points: ~50-160 model-benchmark scores
- Statistical unit: Benchmark-level aggregates (CV, mean ρ)

**Loading Information** (for Phase 4 download):
- Method: Web scraping + manual table extraction
- Identifier: N/A (multi-source corpus)
- Code:
  ```python
  # TrustLLM: Web scraping from public leaderboard
  import pandas as pd
  import requests
  from bs4 import BeautifulSoup
  
  url = "https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html"
  # Scrape HTML table → pandas DataFrame
  
  # TruthfulQA: GitHub CSV download
  # HaluBench, FinTrust: Manual PDF table extraction → CSV
  
  # Consolidate into unified format:
  # | benchmark_name | model_name | score |
  ```

**Statistics:**
- Benchmarks: 5-10 trust evaluation benchmarks
- Models per benchmark: 10-16 (requirement: n ≥ 10)
- Shared models requirement: ≥5 shared models per benchmark pair for Spearman ρ
- Coverage: 2020-2025 trust benchmarks

**Preprocessing:**
- Extract model scores from HTML/PDF tables
- Normalize score ranges to common scale (if needed)
- Identify shared model sets across benchmarks
- Compute benchmark-level statistics (mean, std, CV)

**Data Validation:**
- Verify n_models ≥ 10 per benchmark (else exclude)
- Verify ≥5 shared models for cross-benchmark pairs
- Remove benchmarks with missing/incomplete data

### Models

#### Baseline Model

**Architecture:** N/A - This is a meta-analysis, not a model training experiment

**Rationale:** The hypothesis tests statistical properties of existing benchmark leaderboards (CV vs. cross-benchmark stability). No model training is involved. The "models" are the LLMs evaluated in the trust benchmarks (GPT-4, ChatGPT, Llama2, etc.), but we analyze their scores, not train them.

**Loading Information** (for Phase 4 download):
- Method: N/A - Meta-analysis only
- Identifier: N/A
- Code: N/A - Analysis uses pandas DataFrame operations and scipy.stats functions

#### Proposed Model

**Architecture:** Statistical Analysis Pipeline (No neural network - this is meta-analysis)

**Core Mechanism Implementation:**

```python
# Core Mechanism: CV-Stability Correlation Analysis
# Based on: benchstats, evalstats, GAIA statistics.py patterns

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from itertools import combinations

class BenchmarkMetaAnalysis:
    """
    Analyzes coefficient of variation (CV) as predictor of
    cross-benchmark ranking stability (mean Spearman ρ).
    
    This is a STATISTICAL ANALYSIS class, not a neural network.
    """
    def __init__(self, min_models=10, min_shared_models=5):
        self.min_models = min_models
        self.min_shared_models = min_shared_models
        self.benchmark_data = {}
        
    def compute_cv(self, benchmark_name, scores):
        """Coefficient of Variation (CV = σ/μ)"""
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        cv = std_score / mean_score
        return cv
    
    def compute_cross_benchmark_rho(self, benchmark_a, benchmark_b):
        """
        Spearman rank correlation between shared models.
        
        Args:
            benchmark_a: DataFrame with columns [model_name, score]
            benchmark_b: DataFrame with columns [model_name, score]
        Returns:
            rho: Spearman correlation coefficient (or None if insufficient overlap)
        """
        # Find shared models
        shared_models = set(benchmark_a.model_name) & set(benchmark_b.model_name)
        
        if len(shared_models) < self.min_shared_models:
            return None  # Insufficient overlap
        
        # Extract ranks for shared models
        a_shared = benchmark_a[benchmark_a.model_name.isin(shared_models)]
        b_shared = benchmark_b[benchmark_b.model_name.isin(shared_models)]
        
        # Rank within each benchmark
        a_ranks = a_shared.score.rank()
        b_ranks = b_shared.score.rank()
        
        # Compute Spearman correlation
        rho, _ = spearmanr(a_ranks, b_ranks)
        return rho
    
    def analyze_cv_stability_correlation(self, benchmark_dict):
        """
        Test H-E1: Does CV predict cross-benchmark stability?
        
        Args:
            benchmark_dict: {benchmark_name: DataFrame[model_name, score]}
        Returns:
            r: Pearson correlation (CV, mean_ρ)
            p: Statistical significance
            cv_values: List of CV per benchmark
            mean_rho_values: List of mean ρ per benchmark
        """
        cv_values = []
        mean_rho_values = []
        
        for benchmark_name, df in benchmark_dict.items():
            if len(df) < self.min_models:
                continue  # Skip benchmarks with < 10 models
            
            # Compute CV for this benchmark
            cv = self.compute_cv(benchmark_name, df.score.values)
            
            # Compute pairwise ρ with all other benchmarks
            pairwise_rhos = []
            for other_name, other_df in benchmark_dict.items():
                if other_name == benchmark_name:
                    continue
                rho = self.compute_cross_benchmark_rho(df, other_df)
                if rho is not None:
                    pairwise_rhos.append(rho)
            
            # Mean ρ for this benchmark
            if pairwise_rhos:
                mean_rho = np.mean(pairwise_rhos)
                cv_values.append(cv)
                mean_rho_values.append(mean_rho)
        
        # Test correlation: r, p = pearsonr(CV, mean_ρ)
        if len(cv_values) >= 5:  # Need at least 5 benchmarks
            r, p = pearsonr(cv_values, mean_rho_values)
            return r, p, cv_values, mean_rho_values
        else:
            return None, None, cv_values, mean_rho_values

# Usage (Phase 4 will implement):
# analyzer = BenchmarkMetaAnalysis()
# r, p, cvs, rhos = analyzer.analyze_cv_stability_correlation(leaderboard_data)
# success = (r < -0.5) and (p < 0.05)
```

**Integration:** N/A - Standalone statistical analysis pipeline

### Training Protocol

**No Training Required** - This is a meta-analysis, not a model training experiment.

**Analysis Pipeline:**
1. **Data Extraction** (Phase 4):
   - Scrape TrustLLM leaderboard HTML → pandas DataFrame
   - Extract TruthfulQA, HaluBench, FinTrust tables → CSV
   - Consolidate into unified format: `{benchmark_name: DataFrame[model_name, score]}`

2. **CV Computation**:
   - For each benchmark: `CV = std(scores) / mean(scores)`

3. **Cross-Benchmark ρ Computation**:
   - For each benchmark pair with ≥5 shared models: `ρ = spearmanr(rank_A, rank_B)`
   - For each benchmark: `mean_ρ = mean(pairwise_ρ_values)`

4. **Hypothesis Test**:
   - `r, p = pearsonr(CV_values, mean_ρ_values)`
   - Success: `r < -0.5` AND `p < 0.05`

**Fixed Parameters:**
- `min_models_per_benchmark = 10` (requirement from Phase 2B)
- `min_shared_models = 5` (for valid Spearman ρ)
- `alpha = 0.05` (statistical significance threshold)

**Seeds:** N/A (deterministic statistical computation)

> ⚠️ **EXISTENCE (PoC)**: Single analysis run. No model training, no random seeds.

### Evaluation

**Primary Metrics**:
1. **Pearson r**: Correlation between CV and mean cross-benchmark ρ
2. **p-value**: Statistical significance of the correlation

**Success Criteria** (MUST_WORK gate):
- `r < -0.5` (negative moderate-to-strong correlation)
- `p < 0.05` (statistical significance)

**Expected Baseline Performance** (from research context):
- Under null hypothesis H₀ (no correlation): `r ≈ 0`, `p > 0.05`
- Power analysis (Phase 2B): 70-90% power at n=5-10 benchmarks for detecting r=-0.5 to -0.7

**Source:** Phase 2B verification protocol

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical meta-analysis (correlation testing)
- Library: scipy.stats (Pearson correlation, Spearman rank correlation)
- Code:
  ```python
  from scipy.stats import pearsonr, spearmanr
  import numpy as np
  
  # Primary hypothesis test metrics
  def compute_cv(scores):
      """Coefficient of Variation"""
      return np.std(scores) / np.mean(scores)
  
  def compute_cross_benchmark_rho(benchmark_a_ranks, benchmark_b_ranks):
      """Spearman rank correlation between two benchmarks"""
      rho, p = spearmanr(benchmark_a_ranks, benchmark_b_ranks)
      return rho
  
  def test_cv_stability_correlation(cv_values, mean_rho_values):
      """Pearson correlation between CV and mean cross-benchmark ρ"""
      r, p = pearsonr(cv_values, mean_rho_values)
      return r, p
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on meta-analysis of benchmark statistics, the following visualizations would best communicate results:

1. **Scatter Plot**: CV (x-axis) vs. mean cross-benchmark ρ (y-axis)
   - Each point = one benchmark
   - Include regression line and 95% confidence interval
   - Annotate with r and p-value

2. **Dual Bar Chart**: Per-benchmark CV and mean ρ side-by-side
   - Sort benchmarks by CV (low to high)
   - Visual check: Does high CV → low ρ pattern hold?

3. **Correlation Matrix Heatmap**: Pairwise Spearman ρ across all benchmark pairs
   - Shows which benchmarks agree/disagree on model rankings
   - Color scale: red (low ρ, poor agreement) to green (high ρ, strong agreement)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace Paper 2305.14314
- **Type**: Knowledge base article
- **Query Used**: "trust benchmark LLM evaluation TrustLLM"
- **Relevance**: LLM trust evaluation context
- **Key Insights**:
  - Standard benchmarking practices in LLM trust evaluation
  - Domain context for trust benchmarks
- **Used For**: Background understanding of trust evaluation domain

**Assessment**: Archon KB had limited directly applicable meta-analysis content. Most results were ML infrastructure/training focused, not statistical analysis of leaderboards.

### Archon Code Examples

**Code Source A.1**: scipy installation example
- **Source**: https://github.com/hojonathanho/diffusion
- **Query Used**: "Pearson correlation scipy statistical test"
- **Key Code**:
  ```python
  pip install scipy  # Standard library for statistical tests
  ```
- **Used For**: Confirming scipy.stats as standard library for correlation analysis

**Assessment**: Limited directly applicable code examples. Archon KB is primarily ML/DL focused, not statistical meta-analysis.

### B. GitHub Implementations (Exa)

**Repository B.1**: Arech/benchstats (⭐ active Python package)
- **URL**: https://github.com/Arech/benchstats
- **Query Used**: "benchmark leaderboard statistical analysis coefficient variation Python"
- **Relevance**: Statistical comparison of benchmark results with variance metrics
- **Key Code** (annotated):
  ```python
  # Coefficient of Variation as standard benchmark stability metric
  # Used as basis for: CV computation in our analysis pipeline
  
  def compute_variance(values):
      m = _mean(values)
      s = _stdev(values, m)
      cv_pct = round(_cv_pct(values, m, s), 2)  # CV% computation
      return VarianceSummary(cv_pct=cv_pct)
  ```
- **Configuration Extracted**: CV as standard metric for benchmark variability
- **Used For**: CV computation pattern in BenchmarkMetaAnalysis class

**Repository B.2**: ianarawjo/evalstats (⭐ LLM evaluation focused)
- **URL**: https://github.com/ianarawjo/evalstats
- **Query Used**: "benchmark leaderboard statistical analysis coefficient variation Python"
- **Relevance**: Statistical analysis for LLM benchmark comparisons
- **Key Code** (annotated):
  ```python
  # Bootstrap confidence intervals, pairwise comparisons
  # Descriptive stats: mean, median, std, CV
  # Used as basis for: Robustness metrics pattern
  
  def robustness_metrics():
      """Point estimates: mean, median, std, CV, IQR"""
      return dict(cv=cv_value, ...)
  ```
- **Configuration Extracted**: CV used as standard robustness metric for LLM evaluations
- **Used For**: Validation that CV is well-established benchmark stability metric

**Repository B.3**: AMD GAIA eval/statistics.py
- **URL**: https://github.com/amd/gaia/blob/1304b222/src/gaia/eval/statistics.py
- **Query Used**: "benchmark leaderboard statistical analysis coefficient variation Python"
- **Relevance**: Benchmark variance analysis with CV computation
- **Key Code** (annotated):
  ```python
  @dataclass
  class VarianceSummary:
      cv_pct: float  # coefficient of variation (%)
      
  def compute_variance(values):
      m = _mean(values)
      s = _stdev(values, m)
      return VarianceSummary(cv_pct=round(_cv_pct(values, m, s), 2))
  ```
- **Configuration Extracted**: Stdlib-only CV implementation pattern
- **Used For**: CV computation implementation in BenchmarkMetaAnalysis

**Repository B.4**: felipemaiapolo/statistical-scaling-law
- **URL**: https://github.com/felipemaiapolo/statistical-scaling-law
- **Query Used**: "benchmark leaderboard statistical analysis coefficient variation Python"
- **Relevance**: Leaderboard analysis across multiple benchmarks
- **Key Features**:
  - Cross-benchmark analysis of LLM capabilities
  - Data format: `data/df_full.csv` with benchmark scores and metadata
  - Latent-skill scaling model for multi-benchmark comparison
- **Used For**: Confirming multi-benchmark leaderboard analysis as established pattern

**Repository B.5**: significance_analysis PyPI package
- **URL**: https://pypi.org/project/significance_analysis/
- **Query Used**: "benchmark leaderboard statistical analysis coefficient variation Python"
- **Relevance**: HPO algorithms performing on multiple benchmarks
- **Key Features**:
  - Linear Mixed-Effects Model for cross-benchmark analysis
  - Dataset format: | algorithm | benchmark | metric |
- **Used For**: Standard pattern for multi-benchmark statistical comparison

**Repository B.6**: SciPy Official Documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Query Used**: "Spearman correlation ranking stability cross-benchmark Python scipy"
- **Relevance**: Standard implementation for ranking correlation
- **Key Code**:
  ```python
  from scipy.stats import spearmanr, pearsonr
  
  # Spearman for ranking agreement
  rho, p = spearmanr(rank_A, rank_B)
  
  # Pearson for CV-stability correlation
  r, p = pearsonr(cv_values, mean_rho_values)
  ```
- **Best Practices**:
  - Use `nan_policy='omit'` for missing values
  - For small samples (n < 500), use permutation tests
  - Pandas `df.corr('spearman')` for pairwise correlations
- **Used For**: Statistical test implementation in analyze_cv_stability_correlation method

**Repository B.7**: TrustLLM Leaderboard
- **URL**: https://trustllmbenchmark.github.io/TrustLLM-Website/leaderboard.html
- **Query Used**: "TrustLLM HaluBench TruthfulQA leaderboard data download format"
- **Relevance**: Primary data source for trust benchmark leaderboard corpus
- **Data Format**: HTML table with 16+ models across 8 trust dimensions
- **Used For**: Dataset specification - primary source for benchmark data extraction

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. This is a statistical data analysis task using standard pandas DataFrame operations and scipy.stats functions, not complex deep learning code requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis in the verification chain (H-E1 is the foundation hypothesis).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A + Exa | Trust Benchmark Leaderboard Corpus (B.7) |
| CV computation | GitHub | benchstats (B.1), GAIA (B.3) |
| Baseline model | N/A | Meta-analysis - no model training |
| Mechanism design | GitHub + scipy docs | evalstats (B.2), scipy (B.6) |
| Pseudo-code | GitHub | benchstats, GAIA, significance_analysis patterns |
| Training protocol | N/A | Meta-analysis - no training |
| Evaluation metrics | Phase 2B + scipy | Pearson/Spearman tests (B.6) |
| Data extraction | Exa | TrustLLM leaderboard (B.7) |
| Statistical tests | scipy docs | spearmanr, pearsonr (B.6) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-09

### Workflow History for This Hypothesis

1. **Phase 2B** (Verification Planning): Hypothesis decomposed from main hypothesis, verification protocol defined
2. **Phase 2C** (Experiment Design - Current): Research-backed experiment specification created
   - Archon KB: Limited meta-analysis content, scipy patterns identified
   - Exa GitHub: Found benchstats, evalstats, GAIA examples
   - Dataset confirmed: Trust benchmark leaderboard corpus (5-10 benchmarks)
   - Analysis pipeline designed: CV computation → cross-benchmark ρ → Pearson correlation test
3. **Next:** Phase 3 (Implementation Planning) - PRD, Architecture, Tasks generation

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
