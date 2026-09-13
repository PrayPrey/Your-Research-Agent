# Experiment Design: h-m3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Citation velocity correlation with saturation detection yields >80% precision (detected saturation → actual paradigm shift) and >70% recall (actual shifts → detection within 6mo prior) on 15-20 benchmark cases
**Phase 2B Source:** 02b_context.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASS), h-m2 (PASS)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1, h-m2

### Gate Condition
**MUST_WORK**: Precision >80% AND Recall >70% on 15-20 benchmark cases

h-m3 validates whether citation velocity correlation adds predictive power beyond saturation detection (h-m1) and temporal precedence (h-m2) alone.

---

## Continuation Context

### Dependency Chain

```
h-e1 (PWC leaderboards) → h-m1 (saturation detector) → h-m2 (temporal validation) → h-m3 (citation correlation)
```

h-m1 established dual-metric saturation detection (score convergence + velocity decay).  
h-m2 validated temporal precedence (100% saturation→shift precedence, mean 48.1-month lead).  
h-m3 tests citation velocity as predictor of paradigm shifts correlated with saturation events.

### Previous Hypothesis Results (if applicable)

**From h-m1 (VALIDATED):**
- Score convergence detector: 3/3 benchmarks converged (ImageNet 2015-08, GLUE 2018-03, SQuAD 2018-05)
- Statistical significance: all p<0.05 (Levene's test)
- Code reuse: `data_loader.py`, `convergence_detector.py`, `statistical_validator.py`
- Data source: PWC leaderboards (h-e1 symlink)

**From h-m2 (VALIDATED):**
- Temporal precedence: 100% (3/3 pairs), mean lead 48.1 months
- Citation infrastructure: Semantic Scholar API integration (`citation_fetcher.py`)
- Mock data for PoC: Monthly citation time series with paradigm shift markers

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - synthesized from codebase analysis*

**Pattern: Citation Velocity Analysis**
- Common approach: Compute citation rate (Δcitations/Δtime) over rolling windows
- Libraries: pandas (time series), scipy.stats (statistical tests)
- Typical window: 3-6 months for velocity computation

**Pattern: Precision/Recall Validation**
- Binary classification metrics (detected vs ground truth)
- sklearn.metrics: `precision_score`, `recall_score`, `confusion_matrix`
- Threshold tuning: ROC curve analysis for optimal operating point

### Archon Code Examples

*MCP unavailable - inferred from h-m1/h-m2 implementations*

**Reusable Components:**
1. `h-m1/code/data_loader.py`: PWC leaderboard parser (monthly aggregation)
2. `h-m1/code/convergence_detector.py`: Rolling window statistics
3. `h-m2/code/citation_fetcher.py`: Semantic Scholar API integration
4. `h-m2/code/lead_time_analyzer.py`: Temporal precedence computation

### Exa GitHub Implementations

*MCP unavailable - architecture designed from common patterns*

**Citation Velocity Detection:**
- Standard approach: `df['velocity'] = df['citations'].diff() / df['time'].diff()`
- Smoothing: Rolling mean over 3-6 month windows to reduce noise
- Anomaly detection: Z-score thresholding for acceleration/deceleration events

**Precision/Recall Evaluation:**
- Ground truth: Binary labels (1 = paradigm shift within 6mo, 0 = no shift)
- Predictions: Binary detector output (1 = saturation detected, 0 = not detected)
- Metrics: `sklearn.metrics.classification_report`

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Codebase Analysis:**
- h-m1 provides saturation detection infrastructure (convergence_detector.py)
- h-m2 provides citation data infrastructure (citation_fetcher.py)
- h-m3 combines both: correlate saturation events with citation velocity

**Recommended Implementation Path:**
- Primary: Extend h-m2 citation analysis with h-m1 saturation detector integration
- Fallback: Standalone correlation detector with symlinked data
- Justification: Maximize code reuse from validated prerequisites (h-m1, h-m2)

### Code Analysis (Serena MCP)

*MCP unavailable - manual codebase review performed*

**h-m1 Convergence Detector (docs/youra_research/h-m1/code/convergence_detector.py):**
- Rolling window std computation
- Threshold-based detection
- Levene's test for statistical validation

**h-m2 Citation Fetcher (docs/youra_research/h-m2/code/citation_fetcher.py):**
- Semantic Scholar API integration
- Rate limiting (100 req/5min)
- Monthly citation aggregation
- Caching for reproducibility

**Integration Pattern:**
- Load saturation dates from h-m1 results
- Fetch citation velocity around saturation dates
- Correlate velocity changes with paradigm shift events

---

## Experiment Specification

### Dataset

**Name:** Papers with Code (PWC) Leaderboards + Semantic Scholar Citations  
**Type:** Custom (composite from h-m1 + h-m2)  
**Source:** 
- Leaderboards: `docs/youra_research/h-m1/data/pwc_leaderboards/` (symlink to h-e1)
- Citations: Semantic Scholar API (cached in `h-m3/data/citations/`)

**Benchmarks:** 15-20 cases with documented paradigm shifts (2015-2024)  
**Ground Truth:** Known paradigm shift adoption dates (GPT-3 2020-06, ViT 2021-02, LLaMA 2023-02, etc.)

**Preprocessing:**
1. Load saturation dates from h-m1 results (`h-m1/results/convergence_results.json`)
2. Fetch citation time series for each benchmark's top-cited papers
3. Compute monthly citation velocity: `Δcitations / Δtime`
4. Label events: 1 if paradigm shift within 6mo of saturation, 0 otherwise

**Loading Information** (for Phase 4 download):
- Method: Symlink + API
- Identifier: h-m1/data/pwc_leaderboards (existing), Semantic Scholar paper IDs
- Code:
```python
# Leaderboards (reuse h-m1)
leaderboard_path = Path("../h-m1/data/pwc_leaderboards")
saturation_results = json.load(open("../h-m1/results/convergence_results.json"))

# Citations (h-m2 infrastructure)
from citation_fetcher import CitationFetcher
fetcher = CitationFetcher(cache_dir="data/citations/")
citations_df = fetcher.fetch_citations(paper_id="<SS_ID>")
```

### Models

#### Baseline Model

**Name:** Saturation-Only Detector (h-m1)  
**Architecture:** Dual-metric threshold detector (score convergence + velocity decay)  
**Input:** Monthly leaderboard scores  
**Output:** Binary saturation detection (0/1)

**Performance (from h-m1):**
- Detection rate: 3/3 benchmarks (100%)
- False positive rate: Not measured (PoC validation only)

**Loading Information** (for Phase 4 download):
- Method: Code import
- Identifier: `../h-m1/code/convergence_detector.py`
- Code:
```python
import sys
sys.path.append("../h-m1/code")
from convergence_detector import ConvergenceDetector

detector = ConvergenceDetector(threshold=0.01, window=6)
saturation_date = detector.detect(leaderboard_df)
```

#### Proposed Model

**Architecture:** Saturation + Citation Velocity Correlation Detector

**Core Mechanism Implementation:**

```python
def citation_velocity_correlation_detector(
    saturation_dates: Dict[str, str],  # {benchmark: "YYYY-MM"}
    citations_df: pd.DataFrame,        # [benchmark, date, citations]
    paradigm_shifts: Dict[str, str],   # {benchmark: "YYYY-MM"}
    velocity_window: int = 3,          # months
    lead_time_threshold: int = 6       # months
) -> Tuple[float, float]:
    """
    Detect paradigm shifts using saturation + citation velocity correlation.
    
    Returns:
        (precision, recall) tuple
    """
    predictions = []
    ground_truth = []
    
    for benchmark in saturation_dates.keys():
        saturation = pd.to_datetime(saturation_dates[benchmark])
        
        # Compute citation velocity around saturation
        bench_citations = citations_df[citations_df['benchmark'] == benchmark]
        bench_citations['velocity'] = (
            bench_citations['citations']
            .rolling(window=velocity_window)
            .apply(lambda x: (x.iloc[-1] - x.iloc[0]) / velocity_window)
        )
        
        # Detect velocity spike within 6mo of saturation
        sat_window = bench_citations[
            (bench_citations['date'] >= saturation - pd.DateOffset(months=3)) &
            (bench_citations['date'] <= saturation + pd.DateOffset(months=lead_time_threshold))
        ]
        
        velocity_spike = sat_window['velocity'].max() > sat_window['velocity'].mean() + 2*sat_window['velocity'].std()
        predictions.append(int(velocity_spike))
        
        # Ground truth: paradigm shift within 6mo
        if benchmark in paradigm_shifts:
            shift_date = pd.to_datetime(paradigm_shifts[benchmark])
            actual_shift = abs((shift_date - saturation).days) <= lead_time_threshold * 30
            ground_truth.append(int(actual_shift))
        else:
            ground_truth.append(0)
    
    # Compute precision/recall
    from sklearn.metrics import precision_score, recall_score
    precision = precision_score(ground_truth, predictions, zero_division=0)
    recall = recall_score(ground_truth, predictions, zero_division=0)
    
    return precision, recall
```

**Key Innovation:** Correlates citation velocity changes around saturation dates with paradigm shift timing, adding predictive signal beyond saturation detection alone.

### Training Protocol

**No training required** (analytical detector, not learned model)

**Algorithm Steps:**
1. Load saturation dates from h-m1 results (3 benchmarks: ImageNet, GLUE, SQuAD)
2. Fetch citation time series for top-cited papers per benchmark (Semantic Scholar API)
3. Compute monthly citation velocity with 3-month rolling window
4. Detect velocity spikes (>2σ above mean) within 6-month window of saturation
5. Compare detections against ground truth paradigm shift dates
6. Compute precision/recall metrics

**Hyperparameters:**
- `velocity_window`: 3 months (citation rate smoothing)
- `lead_time_threshold`: 6 months (maximum lead time for correlation)
- `spike_threshold`: 2σ (z-score for velocity anomaly detection)

### Evaluation

**Metrics:**
1. **Precision**: TP / (TP + FP) — detected saturation → actual shift within 6mo
2. **Recall**: TP / (TP + FN) — actual shifts → saturation detected within 6mo prior
3. **F1-Score**: Harmonic mean of precision and recall

**Success Criteria:**
- Precision >80% (MUST_WORK gate)
- Recall >70% (MUST_WORK gate)
- Sample size: 15-20 benchmark cases (minimum statistical validity)

**Expected Baseline:**
- Random detector: ~33% precision/recall (chance)
- Saturation-only (h-m1): ~60% (hypothesized; h-m1 did not measure precision/recall)
- Saturation + citation velocity (h-m3): target >80%/70%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report

precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

print(classification_report(y_true, y_pred, target_names=['No Shift', 'Shift']))
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing target (80%/70%) vs actual precision/recall

#### Additional Figures (LLM Autonomous)

1. **Citation Velocity Timeline**: Line plot showing citation velocity over time for each benchmark, with saturation dates and paradigm shift dates marked
2. **Correlation Matrix**: Heatmap showing temporal correlation between saturation events and citation velocity spikes
3. **Confusion Matrix**: 2x2 heatmap showing TP/FP/TN/FN distribution
4. **Lead Time Distribution**: Histogram of lead times (saturation → shift) for true positives

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `precision > 0.80 AND recall > 0.70`

**Rationale:** MUST_WORK gate requires statistical validation (>80%/70%) on 15-20 cases. PoC validates existence of citation velocity correlation as predictive signal.

---

## Appendix: Reference Implementations

### Codebase Components (Reused from h-m1, h-m2)

**h-m1 Saturation Detector:**
- File: `docs/youra_research/h-m1/code/convergence_detector.py`
- Function: `ConvergenceDetector.detect(leaderboard_df)` → saturation date
- Validation: 3/3 benchmarks converged with p<0.05 significance

**h-m2 Citation Fetcher:**
- File: `docs/youra_research/h-m2/code/citation_fetcher.py`
- Function: `CitationFetcher.fetch_citations(paper_id)` → monthly citation DataFrame
- API: Semantic Scholar v1 graph API
- Rate limit: 100 requests per 5 minutes

**h-m2 Lead Time Analyzer:**
- File: `docs/youra_research/h-m2/code/lead_time_analyzer.py`
- Function: `LeadTimeAnalyzer.compute_lead_times(saturation, shifts)` → lead time distribution
- Validation: 100% temporal precedence (3/3 pairs)

### External References

**Citation Velocity Analysis Patterns:**
- Standard approach: Rolling window differentiation of cumulative citation counts
- Libraries: pandas (`df.diff()`, `df.rolling()`), scipy.stats (`zscore`)
- Threshold: 2σ above mean for anomaly detection

**Precision/Recall Validation:**
- Binary classification: sklearn.metrics (precision_score, recall_score, classification_report)
- Threshold tuning: ROC curve (sklearn.metrics.roc_curve, roc_auc_score)
- Confusion matrix: sklearn.metrics.confusion_matrix

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - state tracked in pipeline context)
**Date:** 2026-08-28T12:00:00Z

### Workflow History for This Hypothesis

h-m3 builds on validated prerequisites:
- h-m1: Saturation detection (VALIDATED, 2026-08-28)
- h-m2: Temporal precedence (VALIDATED, 2026-08-28)

No prior modification attempts. Version 1.

---

*MCP Tools Used: Archon (unavailable - synthesized), Exa (unavailable - synthesized), Serena (unavailable - manual codebase review)*
*All specifications grounded in prerequisite validation results and codebase analysis*
*Next Phase: Phase 3 - Implementation Planning*
