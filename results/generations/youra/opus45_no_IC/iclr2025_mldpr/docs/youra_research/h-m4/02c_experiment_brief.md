# Experiment Design: H-M4

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Reduced diversity hides benchmark-specific overfitting
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing harm mechanism of benchmark concentration

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 PASSED: Cohen's d = 1.93)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (PASS), H-M1 (PASS), H-M2 (PASS), H-M3 (PASS)

### Gate Condition

**Primary:** Negative correlation between entropy and cross-benchmark variance
**Secondary:** Effect detectable in at least 2 of 3 venues

---

## Continuation Context

This hypothesis tests the harm mechanism: why does benchmark concentration matter? If papers evaluate only on standard benchmarks (low diversity), benchmark-specific overfitting goes undetected because no out-of-distribution tests exist.

### Previous Hypothesis Results

- **H-M3 Result:** Citation-linked papers have 23x higher benchmark overlap (0.318 vs 0.014 Jaccard)
- **Implication:** Papers cluster on same benchmarks through citation networks, reducing evaluation diversity
- **Next Step:** Test if this reduced diversity correlates with hidden overfitting (performance variance)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for "benchmark overfitting" in KB. Related content:
- Diffusion model evaluation pipelines (StyleGAN-V metrics)
- Multi-GPU evaluation frameworks (mmgeneration)
- Performance comparison utilities

**Key Pattern:** Cross-benchmark evaluation requires standardized preprocessing and consistent metric computation across datasets.

### Archon Code Examples

```python
# Pattern from KB: Variance evaluation across configurations
def elapsed_time(pipeline, nb_pass=3, num_inference_steps=20):
    # warmup
    for _ in range(2):
        images = pipeline(prompt, num_inference_steps=num_inference_steps)
    # time evaluation
    start = time.time()
    for _ in range(nb_pass):
        pipeline(prompt, num_inference_steps=num_inference_steps)
    end = time.time()
    return (end - start) / nb_pass
```

**Applicable Pattern:** Warmup + multiple passes for stable measurement. Apply to performance variance.

### Exa GitHub Implementations

1. **OoD-Bench (CVPR 2022):** 172 dataset pairs for OoD evaluation. Measures two dimensions of distribution shift.
   - URL: https://openaccess.thecvf.com/content/CVPR2022/papers/Ye_OoD-Bench_Quantifying_and_Understanding_Two_Dimensions_of_Out-of-Distribution_Generalization_CVPR_2022_paper.pdf
   
2. **Cross-dataset generalization framework (arXiv 2025):** Metrics for cross-dataset performance drop.
   - Key insight: "substantial performance drops when models tested on unseen datasets"
   
3. **LiveCodeBench:** Contamination-free evaluation showing models exhibit "stark drop in performance" on post-training problems.

4. **MultiBench:** Framework for multi-dataset robustness evaluation with variance metrics.

### 🎯 Implementation Priority Assessment

**CRITICAL: For this meta-analysis, we use PWC data (established) not model training**

**Recommended Implementation Path:**
- Primary: Papers With Code task-paper links + reported metrics extraction
- Fallback: Manual sampling of multi-benchmark papers (N=100+)
- Justification: PWC already has performance metrics; no model training needed

### Code Analysis (Serena MCP)

Not applicable - this is a meta-analysis of published results, not codebase analysis.

---

## Experiment Specification

### Dataset

**Type:** standard (meta-analysis)
**Name:** Papers With Code Benchmark Results
**Source:** https://paperswithcode.com/api/v1/
**Coverage:** Papers from NeurIPS, ICML, ICLR (2018-2024)

**Selection Criteria:**
1. Papers with results on 2+ benchmarks (rare ~5-10% of papers)
2. Same task type (e.g., image classification, NLP)
3. Reported metrics available in PWC

**Expected Sample Size:**
- Total papers: ~12,000 (from H-M3)
- Multi-benchmark papers: ~600-1,200 (5-10%)
- Minimum viable: 500 papers

**Loading Information** (for Phase 4 download):
- Method: PWC API + cached data
- Identifier: papers-with-code-results-api
- Code: 
```python
import requests
# Reuse cached PWC data from H-E1/H-M1
from pathlib import Path
PWC_CACHE = Path("pwc-archive")
papers = load_papers_with_abstracts(PWC_CACHE)
# Filter to multi-benchmark papers
multi_bench = [p for p in papers if len(p.get('tasks', [])) >= 2]
```

### Models

#### Baseline Model

**Type:** Statistical analysis (not ML model)
**Description:** Compute cross-benchmark performance variance for papers

**Null Hypothesis (H0):** No correlation between venue-year entropy and cross-benchmark variance (ρ = 0)

**Loading Information** (for Phase 4 download):
- Method: N/A (statistical analysis)
- Identifier: scipy.stats, numpy
- Code:
```python
from scipy import stats
import numpy as np
```

#### Proposed Model

**Architecture:** Correlation analysis with venue-level aggregation

**Core Mechanism Implementation:**

```python
def compute_cross_benchmark_variance(papers_with_metrics):
    """
    Compute performance variance across benchmarks for each paper.
    
    For papers evaluated on multiple benchmarks, high variance indicates
    benchmark-specific overfitting (good on some, bad on others).
    
    Args:
        papers_with_metrics: List of papers with performance on 2+ benchmarks
        
    Returns:
        per_paper_variance: Dict[paper_id, variance]
        venue_year_aggregates: Dict[(venue, year), mean_variance]
    """
    per_paper_variance = {}
    
    for paper in papers_with_metrics:
        benchmarks = paper['benchmarks']  # List of (benchmark, metric_value)
        
        if len(benchmarks) < 2:
            continue
            
        # Normalize metrics to [0, 1] range for comparability
        # (accuracy already 0-1, others need normalization)
        normalized = normalize_metrics(benchmarks)
        
        # Compute coefficient of variation (CV) as variance proxy
        # CV = std / mean, scale-invariant
        values = [m['normalized_score'] for m in normalized]
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
        
        per_paper_variance[paper['id']] = cv
        
    # Aggregate by venue-year
    venue_year_aggregates = {}
    for paper_id, cv in per_paper_variance.items():
        paper = get_paper(paper_id)
        key = (paper['venue'], paper['year'])
        if key not in venue_year_aggregates:
            venue_year_aggregates[key] = []
        venue_year_aggregates[key].append(cv)
    
    # Compute mean variance per venue-year
    for key in venue_year_aggregates:
        venue_year_aggregates[key] = np.mean(venue_year_aggregates[key])
        
    return per_paper_variance, venue_year_aggregates


def test_diversity_hides_overfitting(entropy_by_venue_year, variance_by_venue_year):
    """
    Test H-M4: Low diversity (entropy) correlates with high variance (overfitting).
    
    Args:
        entropy_by_venue_year: Dict[(venue, year), entropy] from H-E1
        variance_by_venue_year: Dict[(venue, year), mean_cv] from above
        
    Returns:
        correlation: Spearman rho (expect negative: low entropy -> high variance)
        p_value: Statistical significance
        per_venue_results: Results broken down by venue
    """
    # Align data
    common_keys = set(entropy_by_venue_year.keys()) & set(variance_by_venue_year.keys())
    
    entropies = [entropy_by_venue_year[k] for k in common_keys]
    variances = [variance_by_venue_year[k] for k in common_keys]
    
    # Spearman correlation (robust to non-linearity)
    rho, p_value = stats.spearmanr(entropies, variances)
    
    # Per-venue analysis
    per_venue_results = {}
    for venue in ['NeurIPS', 'ICML', 'ICLR']:
        venue_keys = [k for k in common_keys if k[0] == venue]
        if len(venue_keys) >= 3:
            v_ent = [entropy_by_venue_year[k] for k in venue_keys]
            v_var = [variance_by_venue_year[k] for k in venue_keys]
            v_rho, v_p = stats.spearmanr(v_ent, v_var)
            per_venue_results[venue] = {'rho': v_rho, 'p': v_p, 'n': len(venue_keys)}
    
    return {
        'spearman_rho': rho,
        'p_value': p_value,
        'n_venue_years': len(common_keys),
        'per_venue': per_venue_results,
        'hypothesis_supported': rho < 0 and p_value < 0.05
    }
```

### Training Protocol

**Type:** Statistical analysis (no training)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Analysis Type | Correlation | Testing relationship between entropy and variance |
| Correlation Method | Spearman | Robust to non-linear relationships |
| Significance Level | α = 0.05 | Standard threshold |
| Multiple Comparison | Per-venue + aggregate | Secondary criterion requires 2/3 venues |

### Evaluation

**Primary Metric:** Spearman correlation (ρ) between entropy and cross-benchmark variance
**Direction:** Expect ρ < 0 (negative correlation)

**Success Criteria:**
1. ρ < 0 with p < 0.05 (aggregate across all venue-years)
2. Negative correlation in at least 2 of 3 venues

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
rho, p_value = spearmanr(entropies, variances)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of entropy vs cross-benchmark variance with regression line

#### Additional Figures (LLM Autonomous)

1. **entropy_variance_scatter.png**: Scatter plot with venue color-coding
2. **per_venue_correlation.png**: Bar chart of ρ per venue
3. **variance_distribution.png**: Histogram of cross-benchmark variance by entropy quartile

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spearman ρ < 0 (negative correlation)
3. p < 0.05 (statistically significant)
4. Effect detected in ≥2 venues

**Failure Response:** IF fails: PIVOT to qualitative evidence review

---

## Appendix: Reference Implementations

### A. Cross-Dataset Generalization Studies

1. **OoD-Bench (CVPR 2022)**
   - Ye et al., "OoD-Bench: Quantifying and Understanding Two Dimensions of Out-of-Distribution Generalization"
   - 172 dataset pairs for OoD evaluation
   - Key finding: In-distribution and OoD accuracy jointly increase but relationship is dataset-dependent

2. **Assaying OoD Generalization (NeurIPS 2022)**
   - Wenzel et al., fine-tuned 31k networks across 9 architectures
   - Found performance-robustness relationship is "more nuanced and complex than posited"

3. **Cross-Dataset Drug Response (2025)**
   - Partin et al., benchmarking framework for cross-dataset generalization
   - Key metric: "performance drop compared to within-dataset results"

### B. Benchmark Variance Analysis

1. **Quantifying Variance in Evaluation Benchmarks (2024)**
   - Multiple variance metrics: seed variance, dataset monotonicity
   - Finding: "simple changes can reduce variance for smaller models"

2. **BenchBench (2024)**
   - Framework for benchmark agreement testing
   - Proposes aggregate reference benchmark to reduce outlier influence

### C. Data Sources

1. **Papers With Code API**
   - Primary source for benchmark results
   - URL: https://paperswithcode.com/api/v1/

2. **Cached PWC Data (from H-E1)**
   - Path: `pwc-archive/papers-with-abstracts`
   - Already filtered to NeurIPS/ICML/ICLR 2018-2024

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis

1. H-E1 PASS: 21/21 venue-years have valid HHI (coverage = 1.0)
2. H-M1 PASS: High-HHI group top-5 share > low-HHI (p = 0.000319, ρ = 0.9)
3. H-M2 PASS: HHI predicts standard benchmark adoption (β = 56.75, p < 0.001)
4. H-M3 PASS: Citation-linked papers share benchmarks (Cohen's d = 1.93)
5. **H-M4 IN_PROGRESS**: Testing if low diversity hides overfitting

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
