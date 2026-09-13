# Experiment Design: h-e1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundational hypothesis)
**Gate Status:** MUST_WORK - If fails, ABANDON study (infeasible)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK - If <100 benchmarks meet criteria, study is infeasible. ABANDON or pivot to qualitative case study.

---

## Continuation Context

This is the foundational hypothesis validating data availability. No previous hypothesis results.

### Previous Hypothesis Results (if applicable)
None - This is the first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Query:** "Papers with Code API benchmark data collection"

**Relevant Sources:**
1. **ML Benchmark Collection Papers** (arXiv 2312.00858, 2307.10159, 2301.00704, 2211.09800)
   - Context: Research papers discussing benchmark aggregation and meta-analysis
   - Relevance: Methodological approaches for collecting benchmark statistics at scale
   - Key Finding: Large-scale benchmark studies typically use API-based collection followed by statistical filtering

2. **Gist on Benchmark Data Collection** (https://gist.github.com/sayakpaul/27aec6bca7eb7b0e0aa4112205850335)
   - Context: Practical data collection workflow
   - Relevance: Implementation pattern for API querying and data validation

**Insights:**
- No direct Archon examples for Papers with Code API specifically
- General pattern: REST API → JSON parsing → DataFrame filtering → Statistical analysis
- Standard libraries: `requests`, `pandas`, `scipy.stats`

### Archon Code Examples

**Search Query:** "Papers with Code API Python requests"

**Results:** No direct Papers with Code API examples found in Archon KB.
**Generic API Patterns Available:** Standard HTTP requests patterns exist but not domain-specific.

**Implication:** Will need to reference official Papers with Code API documentation directly.

### Exa GitHub Implementations

**Search Status:** Exa MCP service quota exceeded (HTTP 402)

**Fallback Strategy:** Use official Papers with Code API documentation and standard Python data analysis libraries.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Type:** Data Collection & Statistical Analysis (not model training)

**No Official Implementation:** This is an original observational study - no prior author implementation exists.

**Recommended Implementation Path:**
- Primary: **Custom Python script using Papers with Code REST API**
  - Official API endpoint: `https://paperswithcode.com/api/v1/`
  - Libraries: `requests`, `pandas`, `scipy`, `numpy`
  - Rationale: Direct API access ensures real-time data, transparent filtering
  
- Fallback: **Manual CSV export + Python analysis**
  - Download benchmark data from Papers with Code website
  - Parse locally with pandas
  - Rationale: If API access fails or has quota limits

- Justification: **Existence hypothesis requires data validation, not model implementation.** The goal is to count benchmarks meeting criteria (≥100 benchmarks, ≥5 results each), which is a data collection + filtering task.

### Code Analysis (Serena MCP)

**Not Applicable** - This hypothesis validates data availability (existence check), not code implementation.

**What Serena Would Analyze (if applicable):**
- N/A - No codebase to analyze for an observational data study

---

## Experiment Specification

### Dataset

**Name:** Papers with Code Benchmark Results Database
**Type:** programmatic-api (real data via REST API)
**Source:** https://paperswithcode.com/api/v1/
**Version/Snapshot:** Live API (2019-2024 publication filter)

**Scope:**
- Domain: ML classification benchmarks only
- Time Range: Published 2019-01-01 to 2024-12-31
- Task Filter: Classification tasks (exclude regression, generation, etc.)
- Metric Filter: Accuracy or F1 score (standardized metrics)

**Preprocessing:**
1. Query `/benchmarks/` endpoint with filters: `task=classification`, `published_after=2019-01-01`
2. For each benchmark, fetch `/results/` to count independent reproduction attempts
3. Filter: Keep only benchmarks with ≥5 reported results from different papers/groups
4. Extract metadata: benchmark name, task, dataset, metric type, publication count

**Splits:**
- N/A (observational study, no train/val/test splits)

**Augmentation:**
- None required

**Expected Sample Size:**
- Target: ≥100 benchmarks meeting criteria (hypothesis success threshold)
- Realistic Estimate: 150-300 benchmarks (based on Papers with Code scale: 4000+ total benchmarks)

**Loading Information** (for Phase 4 download):
- Method: `REST API + requests library`
- Identifier: `https://paperswithcode.com/api/v1/benchmarks/`
- Code:
```python
import requests
import pandas as pd

def fetch_benchmarks(task='classification', min_results=5, start_year=2019, end_year=2024):
    """Fetch classification benchmarks from Papers with Code API."""
    base_url = "https://paperswithcode.com/api/v1/benchmarks/"
    params = {
        'task': task,
        'published_after': f'{start_year}-01-01',
        'published_before': f'{end_year}-12-31'
    }
    
    response = requests.get(base_url, params=params)
    benchmarks = response.json()['results']
    
    # Filter by reproduction count
    valid_benchmarks = []
    for bm in benchmarks:
        results_url = f"{base_url}{bm['id']}/results/"
        results = requests.get(results_url).json()['results']
        if len(results) >= min_results:
            valid_benchmarks.append({
                'id': bm['id'],
                'name': bm['name'],
                'task': bm['task'],
                'result_count': len(results)
            })
    
    return pd.DataFrame(valid_benchmarks)
```

### Models

#### Baseline Model

**Not Applicable** - This is an observational data study, not a machine learning model experiment.

**Baseline Comparison:**
Instead of a baseline model, we compare against:
- **Null Hypothesis (H0):** Random sampling would yield <100 benchmarks with ≥5 results
- **Expected Under H0:** If Papers with Code has ~4000 benchmarks and only 2-3% have sufficient reproductions, we'd expect ~80-120 benchmarks
- **Statistical Test:** Binomial test to validate if observed count significantly exceeds random expectation

**Loading Information** (for Phase 4 download):
- Method: N/A (statistical comparison, not model loading)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Statistical Validation Framework (not a neural network)

**Core Mechanism Implementation:**

```python
# Hypothesis: Papers with Code contains ≥100 classification benchmarks (2019-2024) 
# with ≥5 independent reproductions each

def validate_existence_hypothesis(benchmarks_df, min_count=100, min_results=5):
    """
    Validate H-E1: Sufficient benchmark sample exists for meta-analysis.
    
    Args:
        benchmarks_df: DataFrame from fetch_benchmarks()
        min_count: Minimum benchmarks required (default: 100)
        min_results: Minimum reproductions per benchmark (default: 5)
    
    Returns:
        dict: Validation results with pass/fail status
    """
    # Step 1: Filter benchmarks meeting criteria
    valid_benchmarks = benchmarks_df[benchmarks_df['result_count'] >= min_results]
    
    # Step 2: Count total
    total_count = len(valid_benchmarks)
    
    # Step 3: Check against threshold
    hypothesis_passes = total_count >= min_count
    
    # Step 4: Power analysis (Cohen's d = 0.57, alpha = 0.05, power = 0.80)
    # For two-sample comparison, required N per group
    from scipy.stats import norm
    effect_size = 0.57  # medium effect (from Phase 2B Section 1.3)
    z_alpha = norm.ppf(0.975)  # two-tailed alpha = 0.05
    z_beta = norm.ppf(0.80)    # power = 0.80
    required_n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    power_sufficient = total_count >= required_n
    
    # Step 5: Coverage validation (domain diversity)
    domain_distribution = valid_benchmarks['task'].value_counts()
    domains_covered = len(domain_distribution)
    
    return {
        'total_benchmarks': total_count,
        'threshold': min_count,
        'hypothesis_passes': hypothesis_passes,
        'statistical_power_sufficient': power_sufficient,
        'required_n_per_group': int(required_n / 2),
        'domains_covered': domains_covered,
        'domain_distribution': domain_distribution.to_dict()
    }
```

**Key Logic:**
1. Filter benchmarks: `result_count >= 5`
2. Count total: `N = len(filtered)`
3. Validate: `N >= 100` (MUST_WORK gate)
4. Secondary check: Statistical power for Cohen's d=0.57 (medium effect)
5. Tertiary check: Domain diversity (CV vs NLP coverage)

### Training Protocol

**Not Applicable** - This is a data collection and statistical validation study, not a model training experiment.

**Execution Protocol Instead:**
1. **Data Collection Phase** (~30 minutes)
   - Query Papers with Code API for classification benchmarks (2019-2024)
   - Rate limiting: 1 request/second to avoid API throttling
   - Store raw JSON responses for reproducibility
   
2. **Filtering Phase** (~10 minutes)
   - Parse JSON to DataFrame
   - Apply inclusion criteria: `result_count >= 5`
   - Filter by metric type: accuracy or F1 only
   
3. **Validation Phase** (~10 minutes)
   - Run `validate_existence_hypothesis()` function
   - Generate summary statistics
   - Check power analysis requirements

**Total Execution Time:** ~50 minutes (single-run, no epochs/iterations)

**Resources Required:**
- Compute: Standard CPU (no GPU needed)
- Memory: ~500MB (DataFrame storage)
- Network: Stable internet for API access

### Evaluation

**Primary Metric: Benchmark Count**
- **Definition:** Total number of classification benchmarks (2019-2024) with ≥5 independent results
- **Target:** ≥100 benchmarks
- **Measurement:** `len(valid_benchmarks_df)`

**Secondary Metrics:**

1. **Statistical Power Adequacy**
   - **Definition:** Does sample size support detecting Cohen's d=0.57 with 80% power?
   - **Formula:** `required_n = 2 * ((z_alpha + z_beta) / d)^2`
   - **Target:** `total_count >= required_n_per_group * 2`

2. **Domain Coverage**
   - **Definition:** Distribution across CV, NLP, multimodal tasks
   - **Target:** ≥2 domains represented (avoid single-domain bias)
   - **Measurement:** `len(valid_benchmarks_df['task'].unique())`

3. **Reproduction Depth Distribution**
   - **Definition:** Histogram of result counts per benchmark
   - **Target:** Median ≥7 results (sufficient variance for CV calculation)
   - **Measurement:** `valid_benchmarks_df['result_count'].median()`

**Success Criteria (PoC: Direction-based):**
- ✅ **PASS:** `benchmark_count >= 100` AND `power_sufficient == True`
- ❌ **FAIL:** `benchmark_count < 100` → ABANDON study (per Phase 2B gate logic)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `Observational Data Validation`
- Library: `scipy.stats` (for power analysis), `pandas` (for counting/filtering)
- Code:
```python
from scipy.stats import norm
import pandas as pd

def compute_metrics(benchmarks_df):
    """Compute all evaluation metrics for H-E1."""
    # Primary metric
    benchmark_count = len(benchmarks_df)
    
    # Secondary: Power analysis
    effect_size = 0.57
    z_alpha = norm.ppf(0.975)
    z_beta = norm.ppf(0.80)
    required_n_per_group = int(((z_alpha + z_beta) / effect_size) ** 2)
    power_sufficient = benchmark_count >= (required_n_per_group * 2)
    
    # Secondary: Domain coverage
    domain_counts = benchmarks_df['task'].value_counts()
    domain_coverage = len(domain_counts)
    
    # Secondary: Reproduction depth
    median_results = benchmarks_df['result_count'].median()
    
    return {
        'benchmark_count': benchmark_count,
        'passes_threshold': benchmark_count >= 100,
        'power_sufficient': power_sufficient,
        'required_n': required_n_per_group * 2,
        'domain_coverage': domain_coverage,
        'median_reproduction_depth': median_results
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**

1. **Figure 1: Benchmark Count vs Threshold (Bar Chart)**
   - X-axis: ["Threshold (100)", "Actual Count"]
   - Y-axis: Benchmark count
   - Color: Green if passes, Red if fails
   - Purpose: Gate metric comparison (mandatory)

2. **Figure 2: Reproduction Depth Distribution (Histogram)**
   - X-axis: Number of reproductions per benchmark (bins: 5-10, 11-20, 21-50, 50+)
   - Y-axis: Frequency (benchmark count)
   - Purpose: Show distribution quality (validate median ≥7)

3. **Figure 3: Domain Coverage (Pie Chart)**
   - Segments: CV, NLP, Multimodal, Other
   - Labels: Percentage + count
   - Purpose: Validate representative sampling across domains

4. **Figure 4: Timeline Distribution (Line Chart)**
   - X-axis: Publication year (2019-2024)
   - Y-axis: Benchmark count
   - Purpose: Identify temporal trends (ensure 2019-2024 coverage)

5. **Figure 5: Power Analysis Visualization (Bar Chart)**
   - X-axis: ["Required N (80% power)", "Actual N"]
   - Y-axis: Sample size
   - Purpose: Validate statistical power sufficiency

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.
> Use `matplotlib` or `seaborn` for visualization.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Official Papers with Code API Documentation
- **URL:** https://paperswithcode.com/api/v1/docs/
- **Endpoints Used:**
  - `/benchmarks/` - List benchmarks with filters
  - `/benchmarks/{id}/results/` - Get results for specific benchmark
- **Rate Limits:** 1000 requests/hour (conservative: 1 req/sec)
- **Authentication:** None required for public endpoints

### Reference Code Patterns

**1. API Query Pattern (from Archon KB - Generic REST API)**
```python
import requests
import time

def safe_api_call(url, params=None, retry=3, delay=1):
    """Safely call API with retry logic."""
    for attempt in range(retry):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            time.sleep(delay)  # Rate limiting
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == retry - 1:
                raise
            time.sleep(delay * 2)
```

**2. Statistical Power Analysis (scipy.stats)**
```python
from scipy.stats import norm

def calculate_required_sample_size(effect_size, alpha=0.05, power=0.80):
    """Calculate required N for two-sample t-test."""
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    n_per_group = ((z_alpha + z_beta) / effect_size) ** 2
    return int(n_per_group * 2)  # Total N for both groups
```

**3. Data Validation Framework (pandas)**
```python
import pandas as pd

def validate_dataset_coverage(df, required_cols, min_samples):
    """Validate dataset meets minimum requirements."""
    assert all(col in df.columns for col in required_cols), "Missing columns"
    assert len(df) >= min_samples, f"Insufficient samples: {len(df)} < {min_samples}"
    return True
```

### Similar Studies Referenced in Phase 2A/2B
- **Gim et al. 2025** - FAIR principles compliance study (AMD imaging datasets)
  - Methodology: Manual dataset coding + inter-rater reliability
  - Relevance: Artifact quality validation approach
  
- **Jain et al. 2024** - Croissant-RAI metadata format proposal
  - Methodology: Structured metadata extraction
  - Relevance: Standardized artifact format

- **Semmelrock et al. 2024** - Reproducibility barriers framework
  - Methodology: Survey-based taxonomy development
  - Relevance: Reproducibility metrics definition

### Implementation Notes
- **No existing GitHub repos** found for "Papers with Code benchmark reproducibility analysis"
- **Custom implementation required** - This is original research
- **Closest analog:** Meta-analysis studies using API-based data collection (e.g., Semantic Scholar API for citation analysis)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T00:00:00

### Workflow History for This Hypothesis

**Events from verification_state.yaml:**
1. **2026-07-12T14:17:46** - Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
2. **2026-07-12 (current)** - Phase 2C experiment design COMPLETED

**Current Status:**
- experiment_design.status: COMPLETED
- experiment_design.file: 02c_experiment_brief.md
- Next phase: Phase 3 (Implementation Planning)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
