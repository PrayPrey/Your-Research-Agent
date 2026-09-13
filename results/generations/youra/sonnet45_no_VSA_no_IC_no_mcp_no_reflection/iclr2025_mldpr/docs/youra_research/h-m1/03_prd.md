# Product Requirements Document: h-m1

**Date:** 2026-08-28
**Hypothesis:** h-m1 (MECHANISM)
**Author:** Anonymous

---

## Executive Summary

**Product Vision:** Implement score convergence detection system to validate that leaderboard top-5 score variance <0.5% for 6 months serves as measurable signal preceding community migration.

**Problem Statement:** Need to validate first causal step in saturation mechanism - whether score convergence is observable plateau visible before velocity decay. This builds foundation for dual-metric saturation detection (h-m2).

**Success Criteria:**
- Convergence detected (std <0.5%) for ≥2/3 benchmarks (ImageNet, GLUE, SQuAD)
- Detection aligns with expert consensus ±1 year
- Statistical significance validated (p<0.05)

---

## Functional Requirements

### FR-1: Data Preparation
**Priority:** P0 (Blocking)
**Description:** Load and validate PWC leaderboard data from h-e1.
**Acceptance Criteria:**
- Parse h-e1/data/pwc_leaderboards/{benchmark}_raw.jsonl
- Extract submission_date, score, benchmark fields
- Verify 100% timestamp coverage
- Group by month for rolling window analysis

**Data Sources:**
- ImageNet: 250 submissions (2015-2020)
- GLUE: 160 submissions (2018-2022)
- SQuAD: 180 submissions (2016-2020)

### FR-2: Rolling Window Statistics
**Priority:** P0 (Blocking)
**Description:** Compute 6-month rolling standard deviation of top-5 scores per benchmark.
**Acceptance Criteria:**
- Extract top-5 scores per month
- Apply rolling window (6 months, min_periods=3)
- Calculate std per window
- Detect first window where std <0.005 (0.5%)

**Algorithm:**
```python
def score_convergence_detection(df, window_months=6, threshold=0.005, top_k=5):
    df['month'] = pd.to_datetime(df['submission_date']).dt.to_period('M')
    for benchmark in df['benchmark'].unique():
        monthly_topk = df[df['benchmark']==benchmark].groupby('month')['score'].nlargest(top_k)
        monthly_std = monthly_topk.groupby(level=0).std()
        rolling_std = monthly_std.rolling(window=window_months, min_periods=3).mean()
        convergence_mask = rolling_std < threshold
        # Return first convergence date
```

### FR-3: Convergence Detection
**Priority:** P0 (Blocking)
**Description:** Identify first convergence month per benchmark.
**Acceptance Criteria:**
- Record first month where rolling std <0.5%
- Store convergence_date, final_std per benchmark
- Handle cases where no convergence detected

### FR-4: Statistical Validation
**Priority:** P1 (High)
**Description:** Validate convergence statistical significance.
**Acceptance Criteria:**
- Levene's test for variance homogeneity (pre vs post convergence)
- p-value <0.05 for significance
- Report test statistic and p-value per benchmark

**Method:**
```python
from scipy import stats
pre_scores = df[df['month'] < convergence_date]['score']
post_scores = df[df['month'] >= convergence_date]['score']
stat, pvalue = stats.levene(pre_scores, post_scores)
```

### FR-5: Visualization
**Priority:** P1 (High)
**Description:** Generate convergence timeline plots.
**Acceptance Criteria:**
- Rolling std over time per benchmark (line plot)
- Threshold line at 0.5%
- Convergence zone shading
- Save to figures/convergence_timeline_{benchmark}.png

### FR-6: Gate Metrics Comparison
**Priority:** P0 (Blocking)
**Description:** Compare convergence detection against success criteria.
**Acceptance Criteria:**
- Bar chart: target vs actual (convergence count, alignment accuracy)
- Save to figures/gate_metrics.png

---

## Non-Functional Requirements

### NFR-1: Performance
- Processing time: <5 seconds for 590 submissions
- Memory usage: <500MB

### NFR-2: Reproducibility
- Fixed random seed (not applicable - deterministic stats)
- Pandas version: >=1.3.0
- SciPy version: >=1.7.0

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings (Google style)
- Unit tests for rolling window logic

---

## Dependencies

### Data Dependencies
- h-e1 validated data: `docs/youra_research/h-e1/data/pwc_leaderboards/*.jsonl`
- No external API calls (offline analysis)

### Environment
- Python 3.8+
- pandas >=1.3.0
- numpy >=1.21.0
- scipy >=1.7.0
- matplotlib >=3.4.0

### Code Structure
```
docs/youra_research/h-m1/
├── code/
│   ├── data_loader.py          # FR-1
│   ├── convergence_detector.py # FR-2, FR-3
│   ├── statistical_validator.py # FR-4
│   ├── visualizer.py           # FR-5, FR-6
│   └── main_experiment.py      # Orchestration
├── data/                       # Symlink to h-e1/data
├── figures/                    # Generated plots
└── results/
    └── convergence_results.json
```

---

## Success Criteria & Validation

### MUST_WORK Gate Criteria
1. **Convergence Detected:** ≥2/3 benchmarks (2 out of 3: ImageNet, GLUE, SQuAD)
2. **Expert Alignment:** Convergence dates align with expert consensus ±1 year
3. **Statistical Significance:** p<0.05 for all detected convergences

### Validation Protocol
1. Load data from h-e1
2. Compute rolling std per benchmark
3. Detect first convergence per benchmark
4. Statistical validation (Levene's test)
5. Compare against expected dates:
   - ImageNet: 2017-2020 window (expected)
   - GLUE: 2020-2022 window (expected)
   - SQuAD: TBD (no prior expectation)

### Expected Baseline Performance
- ImageNet: Convergence expected 2017-2020 (6.7%→2.3%→1.8% historical pattern)
- GLUE: Convergence expected 2020-2022 (15pt/yr → <2pt/yr)
- Source: Phase 2B verification plan, h-e1 validation

---

## Out of Scope

- Velocity decay analysis (deferred to h-m2)
- Expert survey validation (deferred to h-m3)
- Multi-metric syndrome detection (h-m2 combines convergence + velocity)
- Real-time API scraping (using h-e1 static data)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 0.5% threshold may not generalize | High | Per-benchmark calibration in FR-2 |
| Expert consensus dates unavailable | Medium | Use historical literature as proxy |
| SQuAD shows no convergence | Medium | Acceptable if ImageNet + GLUE converge (2/3 threshold) |

---

## Appendix: Phase 2C Alignment

| Phase 2C Item | PRD Section |
|---------------|-------------|
| Dataset (PWC leaderboards) | FR-1 (Data Preparation) |
| Baseline model (rolling std) | FR-2 (Rolling Window Statistics) |
| Primary metric (convergence count) | FR-3 (Convergence Detection) |
| Statistical validation | FR-4 (Statistical Validation) |
| Visualization requirements | FR-5, FR-6 |
| Gate criteria (≥2/3 benchmarks) | Success Criteria |

---

**Frontmatter:**
```yaml
stepsCompleted: [1, 2, 3, 4, 5, 6]
hypothesis_id: h-m1
hypothesis_type: MECHANISM
task_budget: 30
prerequisites: [h-e1, h-e2]
```
