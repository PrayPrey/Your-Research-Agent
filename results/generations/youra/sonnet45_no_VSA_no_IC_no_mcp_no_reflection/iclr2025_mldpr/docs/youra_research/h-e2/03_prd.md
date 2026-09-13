# Product Requirements Document: Velocity Decay Detection via Linear Regression

**Date:** 2026-08-28  
**Author:** Anonymous  
**Hypothesis:** h-e2  
**Type:** EXISTENCE (Proof-of-Concept)  
**Gate:** MUST_WORK  

---

## Executive Summary

This PRD specifies implementation of a velocity decay detector that measures improvement rates in benchmark leaderboard submissions via linear regression. The system validates whether velocity <0.1 improvement/month sustained for 6 months is measurable, enabling dual-metric saturation detection (convergence + velocity decay).

**Core Deliverable:** Statistical analysis tool that processes timestamped leaderboard data and detects velocity decay patterns.

**Success Criteria:** Detect velocity <0.1/mo on ≥1 benchmark with stable, reproducible measurements across rolling windows.

---

## Problem Statement

Current benchmark saturation detection lacks quantitative velocity metrics. Manual inspection achieves ~70% precision but misses early signals. This experiment validates that linear regression can measure improvement velocity decay, providing the second half of a dual-metric saturation detector.

**If this fails:** Saturation detection must use convergence-only metrics or abandon dual-metric approach entirely.

---

## Functional Requirements

### FR-1: Data Collection
**Priority:** P0  
**Description:** Fetch timestamped benchmark submissions from Papers With Code API.

**Acceptance Criteria:**
- Collect submissions for ImageNet-1k, GLUE, SQuAD v1.1/v2.0
- Time range: 2018-01-01 to 2024-12-31
- Required fields: submission_date, score, model_name, paper_id
- Minimum 100 submissions per benchmark
- Handle missing timestamps (exclude incomplete entries)
- Convert percentage strings to numeric scores

**Data Schema:**
```python
{
    'date': datetime,
    'score': float,
    'model': str,
    'paper': str
}
```

### FR-2: Data Preprocessing
**Priority:** P0  
**Description:** Clean and prepare leaderboard data for regression analysis.

**Acceptance Criteria:**
- Sort submissions chronologically by date
- Filter entries with missing timestamps
- Handle duplicate submissions (keep highest score per model-date pair)
- Validate numeric score conversion
- Output sorted DataFrame with date/score columns

### FR-3: Velocity Computation (Core Mechanism)
**Priority:** P0  
**Description:** Compute improvement velocity via linear regression on rolling windows.

**Acceptance Criteria:**
- Window size: 180 days (6 months)
- Minimum 10 data points per window
- Use scipy.stats.linregress for OLS regression
- Extract slope (daily improvement rate)
- Convert to monthly rate (slope × 30)
- Return p-value for significance testing

**Implementation:**
```python
from scipy.stats import linregress

def compute_velocity(timestamps, scores):
    # Convert to days since first submission
    x = (timestamps - timestamps.min()).dt.days.values
    y = scores.values
    
    slope, intercept, r, p_value, std_err = linregress(x, y)
    monthly_velocity = slope * 30
    
    return monthly_velocity, p_value
```

### FR-4: Rolling Window Detection
**Priority:** P0  
**Description:** Apply velocity computation across rolling 6-month windows.

**Acceptance Criteria:**
- Iterate through all possible 180-day windows
- Skip windows with <10 submissions
- Detect first window where velocity <0.1/mo AND p <0.05
- Record all velocity measurements for stability analysis
- Return first detection date + full velocity timeline

### FR-5: Baseline Comparison (Manual Inspection)
**Priority:** P0  
**Description:** Implement naive baseline for comparison.

**Acceptance Criteria:**
- Baseline method: visual inspection heuristic
- Detection rule: first 6-month period with <1% total improvement
- No statistical significance testing
- Return approximate decay date

**Implementation:**
```python
def manual_inspection_baseline(df):
    for i in range(len(df) - 180):
        window = df.iloc[i:i+180]
        total_improvement = window['score'].iloc[-1] - window['score'].iloc[0]
        
        if total_improvement < 0.01 * window['score'].iloc[0]:
            return window['date'].iloc[0]
    
    return None
```

### FR-6: Evaluation Metrics
**Priority:** P0  
**Description:** Compute PoC success metrics.

**Acceptance Criteria:**
- **Detection Success:** Boolean (first_decay_date is not None)
- **Measurement Stability:** Coefficient of variation across velocities
- **Statistical Significance:** Proportion of windows with p <0.05

**Formulas:**
```python
detection_success = (first_decay_date is not None)
cv = np.std(velocities) / np.abs(np.mean(velocities))
significance_ratio = sum(1 for p in p_values if p < 0.05) / len(p_values)
```

### FR-7: Visualization
**Priority:** P1  
**Description:** Generate diagnostic plots for analysis.

**Required Figures:**
1. Score vs. Time (full leaderboard history + detected decay point)
2. Velocity Timeline (monthly velocity across windows + threshold line)
3. P-value Distribution (histogram)
4. Gate Metrics Comparison (target vs. actual bar chart)

**Output:** Save all figures to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Use standard scipy.stats.linregress (no custom regression)
- p-value threshold: 0.05 for significance
- Minimum sample size: 10 points per window

### NFR-2: Reproducibility
- Fixed random seed (not applicable - deterministic analysis)
- Save all velocity measurements for verification
- Log detection parameters (window=180, threshold=0.1)

### NFR-3: Performance
- Target: Process 500-submission benchmark in <30 seconds
- No optimization required (PoC scope)

### NFR-4: Code Quality
- Type hints for all functions
- Docstrings for core detector class
- Single-file implementation acceptable (LIGHT tier)

---

## Data Requirements

### Input Data
**Source:** Papers With Code API v1  
**Access Method:** programmatic-api  
**Identifier:** `paperswithcode-client` library  

**Benchmarks:**
- ImageNet-1k (2018-2024, ~500+ submissions)
- GLUE (2018-2024, ~300+ submissions)
- SQuAD v1.1/v2.0 (2018-2024, ~400+ submissions)

**API Example:**
```python
from paperswithcode import PapersWithCodeClient

client = PapersWithCodeClient()
benchmark = client.benchmark_get("imagenet-1k")
results = client.benchmark_results_list(benchmark_id=benchmark.id)
```

### Output Data
**Format:** Markdown report + figures (PNG/SVG)  
**Location:** `{hypothesis_folder}/04_validation.md` and `{hypothesis_folder}/figures/`  

---

## Success Criteria

### Primary (Gate: MUST_WORK)
- **Detection Success = True:** At least 1 window with velocity <0.1/mo detected
- **Measurement Stability:** Coefficient of variation <50% (stable measurements)
- **Statistical Significance:** ≥50% of detected windows have p <0.05

### Secondary
- Outperform manual inspection baseline in detection consistency
- Generate all 4 required visualizations
- Code runs without errors on all 3 benchmarks

**PoC Pass Condition:** Primary criteria met on ≥1 benchmark.

---

## Dependencies

### External Libraries
- `scipy` (linregress)
- `numpy` (statistics)
- `pandas` (data manipulation)
- `matplotlib` (visualization)
- `paperswithcode` (optional, API access)

### Prerequisites
- None (foundation hypothesis)

### Assumptions
- Papers With Code API remains accessible
- Leaderboard data has sufficient timestamp density
- 6-month windows contain ≥10 submissions

---

## Out of Scope

- Real-time leaderboard monitoring
- Multi-benchmark aggregation (analyze each independently)
- Robust regression methods (RANSAC, Huber) - defer to future work
- Automated threshold tuning (use fixed 0.1/mo)
- Integration with saturation detection pipeline (Phase 4+ work)

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sparse submission data (<10 points/window) | HIGH | Skip incomplete windows, validate on multiple benchmarks |
| API rate limiting | MEDIUM | Cache responses, implement retry logic |
| Outlier submissions skew regression | MEDIUM | Document in limitations, defer robust regression to future |
| Seasonality (conference deadlines) | LOW | Accept as real signal, not noise |

---

## Acceptance Criteria Summary

**This implementation is COMPLETE when:**
1. ✅ All 7 functional requirements implemented
2. ✅ Code runs on ImageNet/GLUE/SQuAD without error
3. ✅ Detection Success = True on ≥1 benchmark
4. ✅ Measurement Stability CV <50%
5. ✅ All 4 visualizations generated
6. ✅ Validation report written to 04_validation.md

---

## Appendix: Reference Implementation

### Core Detector Class
```python
class VelocityDecayDetector:
    def __init__(self, window_days=180, threshold=0.1):
        self.window_days = window_days
        self.threshold = threshold
    
    def detect(self, df: pd.DataFrame) -> Tuple[Optional[pd.Timestamp], list]:
        df = df.sort_values('date').reset_index(drop=True)
        velocities = []
        
        for i in range(len(df)):
            window_end = df.loc[i, 'date']
            window_start = window_end - pd.Timedelta(days=self.window_days)
            
            mask = (df['date'] >= window_start) & (df['date'] <= window_end)
            window = df[mask]
            
            if len(window) < 10:
                continue
            
            x = (window['date'] - window['date'].min()).dt.days.values
            y = window['score'].values
            
            slope, _, _, p_value, _ = linregress(x, y)
            monthly_velocity = slope * 30
            
            velocities.append((window_end, monthly_velocity, p_value))
            
            if monthly_velocity < self.threshold and p_value < 0.05:
                return window_end, velocities
        
        return None, velocities
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-28  
**Next Phase:** Architecture Design (Step 3)
