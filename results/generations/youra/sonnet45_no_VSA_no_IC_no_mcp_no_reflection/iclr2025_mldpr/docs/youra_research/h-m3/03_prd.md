# Product Requirements Document (PRD)

**Date:** 2026-08-28  
**Author:** Anonymous  
**Hypothesis:** h-m3  
**Type:** MECHANISM  
**Gate:** MUST_WORK

---

## Executive Summary

Implement citation velocity correlation detector that combines saturation detection (h-m1) with citation velocity analysis to predict paradigm shifts in ML benchmarks. Target: >80% precision, >70% recall on 15-20 benchmark cases.

**Core Innovation:** Correlate citation velocity changes around detected saturation dates with paradigm shift timing, adding predictive signal beyond saturation detection alone.

---

## Problem Statement

### Context
h-m1 validated saturation detection (score convergence + velocity decay).  
h-m2 validated temporal precedence (100% saturation precedes shifts by mean 48.1 months).  
h-m3 tests whether citation velocity correlation improves paradigm shift prediction accuracy.

### Gap
Current saturation detector (h-m1) has unknown precision/recall for paradigm shift prediction. Citation velocity may provide additional predictive signal.

### Objective
Validate that citation velocity correlation achieves >80% precision and >70% recall on 15-20 benchmark cases with documented paradigm shifts (2015-2024).

---

## Functional Requirements

### FR-1: Data Integration
**Priority:** P0  
**Description:** Integrate PWC leaderboards (h-e1 symlink) with Semantic Scholar citation data

**Acceptance Criteria:**
- Load saturation dates from h-m1 results (convergence_results.json)
- Fetch citation time series for top-cited papers per benchmark
- Monthly citation resolution with caching for reproducibility
- Handle 15-20 benchmark cases

**Dependencies:** h-m1 (saturation dates), h-m2 (citation infrastructure)

### FR-2: Citation Velocity Computation
**Priority:** P0  
**Description:** Compute monthly citation velocity with rolling window smoothing

**Acceptance Criteria:**
- Calculate: `velocity = Δcitations / Δtime`
- 3-month rolling window for noise reduction
- Store velocity time series per benchmark

**Algorithm:**
```python
citations_df['velocity'] = (
    citations_df['citations']
    .rolling(window=3)
    .apply(lambda x: (x.iloc[-1] - x.iloc[0]) / 3)
)
```

### FR-3: Velocity Spike Detection
**Priority:** P0  
**Description:** Detect citation velocity anomalies around saturation dates

**Acceptance Criteria:**
- Search window: saturation_date ± 3 months to +6 months
- Spike threshold: >2σ above mean velocity
- Binary detection: 1 if spike detected, 0 otherwise

**Formula:**
```python
spike = max(velocity) > mean(velocity) + 2*std(velocity)
```

### FR-4: Baseline Model - Saturation-Only Detector
**Priority:** P0  
**Description:** Implement baseline using h-m1 saturation detection without citation velocity

**Acceptance Criteria:**
- Reuse h-m1 ConvergenceDetector
- Binary prediction: 1 if saturation detected, 0 otherwise
- No citation data integration

**Code Reuse:**
```python
from h-m1.code.convergence_detector import ConvergenceDetector
detector = ConvergenceDetector(threshold=0.01, window=6)
```

### FR-5: Proposed Model - Saturation + Citation Velocity
**Priority:** P0  
**Description:** Implement combined detector using both saturation and citation velocity

**Acceptance Criteria:**
- Detect saturation (h-m1)
- Detect citation velocity spike (FR-3)
- Combined prediction: 1 if both detected, 0 otherwise
- Temporal alignment: velocity spike within 6mo of saturation

### FR-6: Ground Truth Labeling
**Priority:** P0  
**Description:** Label benchmark cases with paradigm shift events

**Acceptance Criteria:**
- Binary labels: 1 = paradigm shift within 6mo of saturation, 0 = no shift
- Ground truth dates: GPT-3 (2020-06), ViT (2021-02), LLaMA (2023-02), etc.
- 15-20 total cases with documented shift dates

### FR-7: Precision/Recall Evaluation
**Priority:** P0  
**Description:** Compute binary classification metrics

**Acceptance Criteria:**
- Precision: TP / (TP + FP) — detected saturation → actual shift
- Recall: TP / (TP + FN) — actual shifts → detected within 6mo
- F1-Score: harmonic mean
- Statistical significance testing (if sample size permits)

**Implementation:**
```python
from sklearn.metrics import precision_score, recall_score, classification_report
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
```

### FR-8: Visualization - Gate Metrics Comparison
**Priority:** P0  
**Description:** Mandatory figure showing target vs actual precision/recall

**Acceptance Criteria:**
- Bar chart: [Target, Baseline, Proposed] × [Precision, Recall]
- Target line: 80% precision, 70% recall
- Save to: docs/youra_research/h-m3/figures/gate_metrics.png

### FR-9: Visualization - Citation Velocity Timeline
**Priority:** P1  
**Description:** Line plot showing citation velocity evolution

**Acceptance Criteria:**
- X-axis: time (months)
- Y-axis: citation velocity
- Markers: saturation dates, paradigm shift dates
- One subplot per benchmark

### FR-10: Visualization - Confusion Matrix
**Priority:** P1  
**Description:** Heatmap showing TP/FP/TN/FN distribution

**Acceptance Criteria:**
- 2×2 heatmap with counts
- Annotations with percentages
- Color scale: diverging (blue-red)

---

## Non-Functional Requirements

### NFR-1: Code Reusability
Reuse h-m1 and h-m2 components:
- `h-m1/code/data_loader.py`
- `h-m1/code/convergence_detector.py`
- `h-m2/code/citation_fetcher.py`
- `h-m2/code/lead_time_analyzer.py`

### NFR-2: Reproducibility
- Cache all API responses (Semantic Scholar)
- Save random seeds (if applicable)
- Document all hyperparameters in config file

### NFR-3: Execution Time
- Total runtime: <30 minutes for 15-20 cases
- API rate limit compliance: 100 req/5min (Semantic Scholar)

### NFR-4: Error Handling
- Graceful API failure handling
- Missing data fallback (use h-m2 mock data if API fails)
- Validation error reporting

---

## Data Specifications

### Input Data

**PWC Leaderboards:**
- Source: h-e1 symlink (docs/youra_research/h-m1/data/pwc_leaderboards/)
- Format: JSONL with monthly scores
- Preprocessing: None (reuse h-m1)

**Citation Data:**
- Source: Semantic Scholar API
- Cache: docs/youra_research/h-m3/data/citations/
- Format: JSONL with monthly citation counts
- Papers: Top-cited per benchmark (identified via h-m2)

**Ground Truth:**
- Paradigm shift dates: Manual annotation file
- Format: JSON {benchmark: shift_date}
- Examples: ImageNet→ResNet (2015-12), GLUE→BERT (2018-10)

### Output Data

**Predictions:**
- Format: CSV [benchmark, saturation_date, velocity_spike, prediction, ground_truth]
- Save to: docs/youra_research/h-m3/results/predictions.csv

**Metrics:**
- Format: JSON {precision, recall, f1, confusion_matrix}
- Save to: docs/youra_research/h-m3/results/metrics.json

**Figures:**
- Gate metrics: gate_metrics.png
- Timeline: citation_velocity_timeline.png
- Confusion matrix: confusion_matrix.png
- All saved to: docs/youra_research/h-m3/figures/

---

## Success Criteria

### Gate Condition (MUST_WORK)
1. **Precision >80%**: Detected saturation events → actual paradigm shifts
2. **Recall >70%**: Actual paradigm shifts → detected within 6mo prior
3. **Sample Size**: 15-20 benchmark cases

### Code Execution
- All scripts run without error
- Figures generated and saved
- Results reproducible from cached data

### Validation Report
- 04_validation.md contains:
  - Precision/recall values
  - Confusion matrix
  - Gate pass/fail decision
  - Key findings

---

## Dependencies

### Prerequisites
- h-m1 (VALIDATED): Saturation detection, convergence_detector.py
- h-m2 (VALIDATED): Citation infrastructure, citation_fetcher.py

### External Libraries
- pandas: Time series manipulation
- numpy: Numerical computation
- scikit-learn: Metrics (precision_score, recall_score)
- matplotlib/seaborn: Visualization
- requests: Semantic Scholar API

### Data Dependencies
- PWC Leaderboards: h-e1 (via h-m1 symlink)
- Semantic Scholar API: Citation time series
- Paradigm shift dates: Manual annotation

---

## Risks and Mitigation

### Risk 1: API Rate Limits
**Impact:** Failed citation data fetch  
**Mitigation:** Use cached h-m2 mock data as fallback

### Risk 2: Small Sample Size (<15 cases)
**Impact:** Low statistical power  
**Mitigation:** Report confidence intervals, acknowledge limitation

### Risk 3: Threshold Sensitivity
**Impact:** Precision/recall depends on spike threshold (2σ)  
**Mitigation:** Document threshold, perform sensitivity analysis if time permits

---

## Out of Scope

- Multi-threshold optimization (ROC curve analysis)
- Cross-validation splits
- Feature engineering beyond velocity spike
- Deployment infrastructure
- Real-time citation monitoring

---

## Appendix: Hypothesis Lineage

```
h-e1 (PWC leaderboards)
  ↓
h-m1 (saturation detector)  → Validated: 3/3 convergence, p<0.05
  ↓
h-m2 (temporal validation)  → Validated: 100% precedence, 48.1mo lead
  ↓
h-m3 (citation correlation) → Target: >80% precision, >70% recall
```

**Code Reuse Strategy:**
- h-m1: Data loading, convergence detection, statistical validation
- h-m2: Citation fetching, lead time analysis, mock data generation
- h-m3: Integration + velocity correlation (new)
