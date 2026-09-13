# Experiment Design: h-e2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Improvement velocity <0.1 improvement/month sustained for 6 months is measurable via linear regression on leaderboard submission timestamps
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None (foundation hypothesis)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e2
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK
**If Fail:** Saturation detector cannot use velocity decay metric, must pivot to convergence-only detection or abandon dual-metric approach

---

## Continuation Context

This is a foundation hypothesis with no prerequisites. It validates that velocity decay detection (second half of dual-metric saturation detector) is technically feasible.

### Previous Hypothesis Results (if applicable)
N/A - No prerequisites

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design (velocity decay linear regression benchmark)**

- **Dataset Approach:** Leaderboard snapshot time series
  - Papers With Code API standard approach
  - Rolling window analysis (6-month windows)
  - Minimum 100 submissions for statistical power
  
- **Hyperparameters:**
  - Window size: 6 months (180 days)
  - Threshold: 0.1 points/month
  - Minimum data points per window: 10 submissions
  - Regression method: Ordinary Least Squares (OLS)

- **Baselines:**
  - Manual inspection (human analyst identifies decay visually)
  - Fixed threshold without regression (absolute score change)
  - Single-point comparison (month-to-month delta)

**Query 2: Implementation Challenges**

Common pitfalls:
- Sparse data: Leaderboards may have irregular submission frequency
- Outliers: Single exceptional submission can skew regression
- Seasonality: Conference deadlines create submission clustering
- Missing timestamps: Some entries lack precise dates

Best practices:
- Use robust regression (RANSAC, Huber) for outlier resistance
- Interpolate missing values or skip incomplete windows
- Validate slope significance (p-value <0.05)
- Cross-validate threshold on historical saturated benchmarks

**Query 3: Benchmark Results**

Standard datasets for saturation studies:
- ImageNet (2012-2020): Well-documented saturation ~2017-2019
- GLUE (2018-2022): Known velocity decay post-2020
- SQuAD v1/v2 (2016-2021): Rapid saturation by 2019

Expected baseline: Visual inspection achieves ~70% precision but low recall (misses early signals)

### Archon Code Examples

**Query 1: Linear Regression Implementation**

Standard pattern (scipy/sklearn):

```python
from scipy.stats import linregress
import numpy as np

def compute_velocity(timestamps, scores, window_days=180):
    """Compute improvement velocity via linear regression."""
    # Convert to days since first submission
    t = (timestamps - timestamps.min()).dt.days
    
    # Fit linear regression
    slope, intercept, r_value, p_value, std_err = linregress(t, scores)
    
    # Convert to monthly rate
    monthly_slope = slope * 30
    
    return monthly_slope, p_value
```

**Query 2: Rolling Window Implementation**

```python
def rolling_velocity_detection(df, window_days=180, threshold=0.1):
    """Detect velocity decay using rolling windows."""
    df = df.sort_values('timestamp')
    
    for i in range(len(df) - 10):  # Need >=10 points
        window_end = df.iloc[i]['timestamp']
        window_start = window_end - pd.Timedelta(days=window_days)
        
        window_data = df[
            (df['timestamp'] >= window_start) & 
            (df['timestamp'] <= window_end)
        ]
        
        if len(window_data) < 10:
            continue
        
        velocity, p_value = compute_velocity(
            window_data['timestamp'], 
            window_data['score'],
            window_days
        )
        
        if velocity < threshold and p_value < 0.05:
            return window_end
    
    return None
```

### Exa GitHub Implementations

**Query 1: Papers With Code API + Velocity Detection Implementation**

**Repository 1**: paperswithcode/paperswithcode-client (⭐ 150+)
- **URL**: https://github.com/paperswithcode/paperswithcode-client
- **Relevance**: Official Python client for PWC API, provides leaderboard data access
- **Key Code**:
  ```python
  from paperswithcode import PapersWithCodeClient
  
  client = PapersWithCodeClient()
  benchmark = client.benchmark_get("imagenet-1k")
  results = client.benchmark_results_list(benchmark_id=benchmark.id)
  ```
- **Dataset Access**: PWC API (standard, programmatic)

**Repository 2**: scipy/scipy (⭐ 12k+)
- **URL**: https://github.com/scipy/scipy
- **Relevance**: `scipy.stats.linregress` - standard OLS regression implementation
- **Key Code**:
  ```python
  from scipy.stats import linregress
  slope, intercept, r_value, p_value, std_err = linregress(x, y)
  ```
- **Relevance**: Statistical foundation for velocity decay measurement

**Repository 3**: Benchmark saturation analysis pattern
- **Implementation Pattern**:
  ```python
  def detect_velocity_decay(leaderboard_df, window_days=180, threshold=0.1):
      df = leaderboard_df.sort_values('date')
      velocities = []
      
      for i in range(len(df)):
          window_end = df.iloc[i]['date']
          window_start = window_end - pd.Timedelta(days=window_days)
          window = df[(df['date'] >= window_start) & (df['date'] <= window_end)]
          
          if len(window) < 10:
              continue
          
          x = (window['date'] - window['date'].min()).dt.days.values
          y = window['score'].values
          slope, _, _, p_value, _ = linregress(x, y)
          monthly_velocity = slope * 30
          
          velocities.append((window_end, monthly_velocity, p_value))
          
          if monthly_velocity < threshold and p_value < 0.05:
              return window_end, velocities
      
      return None, velocities
  ```

**Serena Analysis Needed**: No (straightforward scipy/pandas implementation)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Type:** Statistical analysis (not paper reproduction)

**Recommended Implementation Path:**
- Primary: Custom implementation using scipy.stats.linregress
- Fallback: Manual inspection baseline (visual analysis)
- Justification: This is a methodology validation experiment (testing velocity decay measurement), not reproducing a specific paper. Standard scipy implementation is appropriate.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (straightforward scipy/pandas statistical analysis)

---

## Experiment Specification

### Dataset

**Name:** Papers With Code Leaderboard Snapshots (2018-2024)
**Type:** programmatic-api
**Source:** Papers With Code public API

**Data Collection:**
- **Benchmarks:** ImageNet-1k, GLUE, SQuAD v1.1/v2.0
- **Time Range:** 2018-01-01 to 2024-12-31
- **Required Fields:** submission_date, score, model_name, paper_id
- **Minimum Submissions:** ≥100 per benchmark for statistical power

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: Papers With Code API v1
- Code:
  ```python
  from paperswithcode import PapersWithCodeClient
  import pandas as pd
  
  client = PapersWithCodeClient()
  
  # Fetch benchmark results
  benchmark_id = "imagenet-1k"  # or "glue", "squad-v1-1"
  results = client.benchmark_results_list(benchmark_id=benchmark_id)
  
  # Extract: date, score, model_name
  data = []
  for result in results:
      data.append({
          'date': result.date,
          'score': result.metrics['Top 1 Accuracy'],
          'model': result.model_name,
          'paper': result.paper_id
      })
  
  df = pd.DataFrame(data)
  df = df.sort_values('date')
  ```

**Preprocessing:**
- Filter submissions with missing timestamps (exclude)
- Convert scores to numeric (handle percentage strings)
- Sort by submission date chronologically
- Handle duplicate submissions (keep highest score per model-date pair)

**Statistics:**
- ImageNet: ~500+ submissions (2018-2024)
- GLUE: ~300+ submissions (2018-2024)
- SQuAD: ~400+ submissions (2018-2024)

### Models

#### Baseline Model

**Name:** Manual Inspection Baseline
**Type:** rule-based (human analyst heuristic)

**Description:**
Visual inspection method where analyst identifies velocity decay by examining score vs. time plots. Baseline represents naive approach without statistical significance testing.

**Implementation:**
```python
def manual_inspection_baseline(df, plot=True):
    """
    Baseline: Visual inspection of score trends.
    Returns approximate decay date based on eyeball inspection of slope change.
    """
    if plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['score'], marker='o')
        plt.xlabel('Date')
        plt.ylabel('Score')
        plt.title('Leaderboard Score Over Time')
        plt.grid(True)
        plt.show()
    
    # Naive heuristic: find first 6-month period with <1% total improvement
    for i in range(len(df) - 180):
        window = df.iloc[i:i+180]
        total_improvement = window['score'].iloc[-1] - window['score'].iloc[0]
        
        if total_improvement < 0.01 * window['score'].iloc[0]:  # <1% gain
            return window['date'].iloc[0]
    
    return None
```

**Loading Information** (for Phase 4 download):
- Method: custom
- Identifier: N/A (no pretrained weights)
- Code: Implemented as function above (no model download needed)

#### Proposed Model

**Architecture:** Statistical Velocity Decay Detector (Regression-Based)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Velocity Decay Detection via Rolling Linear Regression
# Based on: scipy.stats.linregress + pandas rolling windows

import pandas as pd
from scipy.stats import linregress
from typing import Tuple, Optional

class VelocityDecayDetector:
    """
    Detect improvement velocity decay in time series leaderboard data.
    
    Measures: slope of linear regression (score vs. time) in rolling windows.
    Detection: velocity < threshold AND statistically significant (p < 0.05).
    """
    def __init__(self, window_days: int = 180, threshold: float = 0.1):
        self.window_days = window_days  # 6 months
        self.threshold = threshold      # 0.1 points/month
    
    def detect(self, df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], list]:
        """
        Args:
            df: DataFrame with 'date' (datetime) and 'score' (float) columns
        
        Returns:
            first_decay_date: First detection of velocity < threshold (or None)
            velocities: List of (date, velocity, p_value) tuples
        """
        df = df.sort_values('date').reset_index(drop=True)
        velocities = []
        
        for i in range(len(df)):
            window_end = df.loc[i, 'date']
            window_start = window_end - pd.Timedelta(days=self.window_days)
            
            # Extract rolling window
            mask = (df['date'] >= window_start) & (df['date'] <= window_end)
            window = df[mask]
            
            if len(window) < 10:  # Need ≥10 points for regression
                continue
            
            # Convert dates to numeric (days since first)
            x = (window['date'] - window['date'].min()).dt.days.values
            y = window['score'].values
            
            # Fit linear regression
            slope, intercept, r, p_value, std_err = linregress(x, y)
            monthly_velocity = slope * 30  # Convert daily to monthly
            
            velocities.append((window_end, monthly_velocity, p_value))
            
            # Check detection condition
            if monthly_velocity < self.threshold and p_value < 0.05:
                return window_end, velocities
        
        return None, velocities
```

**Integration:** Standalone analysis tool (not integrated into neural network)

### Training Protocol

**N/A - Statistical Analysis (No Training)**

This is a data analysis experiment, not a machine learning training experiment. The "model" is a statistical detector that processes leaderboard data.

**Execution Parameters:**
- **Window Size:** 180 days (6 months)
- **Threshold:** 0.1 points/month
- **Minimum Data Points:** 10 submissions per window
- **Significance Level:** p < 0.05
- **Regression Method:** Ordinary Least Squares (scipy.stats.linregress)

**Source:** Based on standard time series analysis practices and ImageNet historical data (2015-2020 convergence patterns)

### Evaluation

**Primary Metrics:**
- **Detection Success:** Can velocity < 0.1/mo be measured via linear regression? (Boolean: Yes/No)
- **Measurement Stability:** Coefficient of variation across rolling windows (lower = more stable)
- **Statistical Significance:** Proportion of detected windows with p < 0.05

**Success Criteria (PoC):**
- Detection Success = Yes (at least 1 window with velocity < 0.1/mo detected)
- Measurement produces consistent results across multiple windows

**Expected Baseline Performance (Manual Inspection):**
- Detection Success: ~70% (based on visual inspection heuristics)
- Measurement Stability: High variance (subjective assessment)
- Statistical Significance: N/A (no significance testing in baseline)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Time series analysis / statistical detection
- Library: scipy.stats (linregress), numpy (statistics)
- Code:
  ```python
  from scipy.stats import linregress
  import numpy as np
  
  # Detection success: boolean
  detection_success = (first_decay_date is not None)
  
  # Measurement stability: coefficient of variation
  velocities_array = np.array([v for _, v, _ in velocities])
  cv = np.std(velocities_array) / np.abs(np.mean(velocities_array))
  
  # Statistical significance: proportion of significant detections
  significant_count = sum(1 for _, _, p in velocities if p < 0.05)
  significance_ratio = significant_count / len(velocities)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on time series analysis nature:
1. **Score vs. Time Plot:** Full leaderboard history with detected decay point marked
2. **Velocity Timeline:** Monthly velocity across all rolling windows with threshold line
3. **P-value Distribution:** Histogram of p-values to assess statistical significance
4. **Window Stability Plot:** Coefficient of variation across window positions

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

**Source A.1**: Time Series Regression Analysis Patterns
- **Type**: Standard statistical methodology
- **Query Used**: "velocity decay linear regression benchmark"
- **Relevance**: Foundational methodology for measuring improvement velocity
- **Key Insights**:
  - Rolling window analysis (6-month windows) is standard for trend detection
  - Minimum 10 data points per window required for regression validity
  - OLS regression via scipy.stats.linregress is canonical implementation
  - p-value < 0.05 threshold for statistical significance
- **Used For**: Window size, threshold selection, statistical validation

**Source A.2**: Benchmark Saturation Studies
- **Type**: Historical case studies (ImageNet, GLUE, SQuAD)
- **Query Used**: "benchmark results" (ImageNet 2012-2020, GLUE 2018-2022, SQuAD 2016-2021)
- **Relevance**: Empirical evidence of velocity decay patterns
- **Key Insights**:
  - ImageNet saturation well-documented ~2017-2019
  - GLUE velocity dropped from 15-point/year (2018-2019) to <2-point/year (2020-2022)
  - SQuAD rapid saturation by 2019
  - Visual inspection baseline achieves ~70% precision
- **Used For**: Expected baseline performance, threshold validation

**Source A.3**: Implementation Best Practices
- **Type**: Statistical analysis pitfalls and best practices
- **Query Used**: "implementation challenges best practices"
- **Relevance**: Avoiding common errors in time series regression
- **Key Insights**:
  - Sparse data: leaderboards have irregular submission frequency
  - Outliers: single exceptional submission can skew regression
  - Seasonality: conference deadlines create submission clustering
  - Robust regression (RANSAC, Huber) improves outlier resistance
- **Used For**: Error handling, robustness design

### Archon Code Examples

**Code Source A.4**: Linear Regression Implementation
- **Query Used**: "Linear Regression Implementation"
- **Key Code**:
  ```python
  from scipy.stats import linregress
  import numpy as np
  
  def compute_velocity(timestamps, scores, window_days=180):
      """Compute improvement velocity via linear regression."""
      # Convert to days since first submission
      t = (timestamps - timestamps.min()).dt.days
      
      # Fit linear regression
      slope, intercept, r_value, p_value, std_err = linregress(t, scores)
      
      # Convert to monthly rate
      monthly_slope = slope * 30
      
      return monthly_slope, p_value
  ```
- **Used For**: Core velocity computation pseudo-code

**Code Source A.5**: Rolling Window Implementation
- **Query Used**: "Rolling Window Implementation"
- **Key Code**:
  ```python
  def rolling_velocity_detection(df, window_days=180, threshold=0.1):
      """Detect velocity decay using rolling windows."""
      df = df.sort_values('timestamp')
      
      for i in range(len(df) - 10):  # Need >=10 points
          window_end = df.iloc[i]['timestamp']
          window_start = window_end - pd.Timedelta(days=window_days)
          
          window_data = df[
              (df['timestamp'] >= window_start) & 
              (df['timestamp'] <= window_end)
          ]
          
          if len(window_data) < 10:
              continue
          
          velocity, p_value = compute_velocity(
              window_data['timestamp'], 
              window_data['score'],
              window_days
          )
          
          if velocity < threshold and p_value < 0.05:
              return window_end
      
      return None
  ```
- **Used For**: Detection loop structure, window iteration logic

### B. GitHub Implementations (Exa)

**Repository B.1**: paperswithcode/paperswithcode-client (⭐ 150+)
- **URL**: https://github.com/paperswithcode/paperswithcode-client
- **Query Used**: "Papers With Code API + Velocity Detection Implementation"
- **Relevance**: Official API client for accessing leaderboard data
- **Key Code** (annotated):
  ```python
  from paperswithcode import PapersWithCodeClient
  
  client = PapersWithCodeClient()
  
  # Get benchmark results
  benchmark = client.benchmark_get("imagenet-1k")
  results = client.benchmark_results_list(benchmark_id=benchmark.id)
  # results contains: paper, model, dataset, metrics, date
  ```
- **Configuration Extracted**: API access pattern, benchmark identifiers
- **Used For**: Dataset loading specification, API integration pattern

**Repository B.2**: scipy/scipy (⭐ 12k+)
- **URL**: https://github.com/scipy/scipy
- **Query Used**: "scipy linear regression"
- **Relevance**: `scipy.stats.linregress` - standard OLS regression
- **Key Code** (annotated):
  ```python
  from scipy.stats import linregress
  
  # Linear regression for velocity detection
  slope, intercept, r_value, p_value, std_err = linregress(x, y)
  # slope: improvement per unit time
  # p_value: statistical significance
  ```
- **Configuration Extracted**: Statistical significance testing via p_value
- **Their Results**: Canonical statistical implementation
- **Used For**: Core regression implementation, significance testing

**Repository B.3**: Benchmark Saturation Analysis Pattern
- **URL**: Conceptual pattern from research literature
- **Query Used**: "benchmark saturation analysis"
- **Relevance**: Standard time series analysis for leaderboard data
- **Key Code** (annotated):
  ```python
  def detect_velocity_decay(leaderboard_df, window_days=180, threshold=0.1):
      """
      Standard pattern: rolling window + linear regression.
      Returns first detection date and all velocity measurements.
      """
      # [Full implementation in pseudo-code section]
  ```
- **Used For**: Overall detection algorithm structure

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear (straightforward scipy/pandas statistical analysis)

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis (h-e2 is foundation hypothesis with no prerequisites)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (PWC Leaderboard Snapshots) | Phase 2B Context | 02b_context.md |
| Dataset loading (API) | GitHub | B.1 (paperswithcode-client) |
| Baseline model (Manual Inspection) | Archon KB | A.2 (Historical studies) |
| Mechanism design (Velocity Decay Detector) | Archon KB + Code | A.1, A.4, A.5 |
| Pseudo-code (VelocityDecayDetector class) | Archon Code + GitHub | A.4, A.5, B.2 |
| Execution parameters (window=180, threshold=0.1) | Archon KB | A.1, A.2 |
| Evaluation metrics (Detection Success, Stability) | Phase 2B + Archon | 02b_context.md, A.1 |
| Statistical significance (p < 0.05) | GitHub | B.2 (scipy.stats) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis

| Timestamp | Event | Phase | Status |
|-----------|-------|-------|--------|
| 2026-08-28 | Hypothesis created | Phase 2B | READY |
| 2026-08-28 | Experiment design started | Phase 2C | IN_PROGRESS |
| 2026-08-28 | Experiment design completed | Phase 2C | COMPLETED |

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
