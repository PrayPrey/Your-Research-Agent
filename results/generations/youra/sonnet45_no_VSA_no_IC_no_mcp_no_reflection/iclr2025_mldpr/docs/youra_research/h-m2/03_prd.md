# Product Requirements Document: h-m2 Temporal Lead Time Validation

## Executive Summary

**Hypothesis:** h-m2 (MECHANISM)  
**Gate:** SHOULD_WORK  
**Objective:** Validate that saturation dates precede paradigm shifts by >6 months in ≥60% of cases

This PRD defines requirements for implementing temporal lead time analysis to validate whether benchmark saturation detection (from h-m1) acts as a leading indicator of paradigm shift adoption events.

## Problem Statement

**Research Question:** Do detected saturation dates consistently precede major paradigm shifts (GPT-3, ViT, LLaMA) by sufficient lead time to serve as predictive signals?

**Validation Approach:** Temporal alignment analysis comparing h-m1 saturation dates against citation-derived paradigm shift adoption dates.

## Functional Requirements

### FR1: Citation Data Collection
- **Input:** Paradigm shift papers (GPT-3, ViT, LLaMA)
- **Source:** Semantic Scholar API
- **Output:** Monthly citation time series (2015-2024)
- **Validation:** Coverage check, missing month interpolation (<10% gaps)

### FR2: Adoption Date Detection
- **Algorithm:** Rolling average citation threshold detection
- **Parameters:** 
  - Threshold: 50 citations/month
  - Window: 3 months sustained
- **Output:** Adoption date per paradigm shift paper
- **Validation:** Community consensus alignment check

### FR3: Lead Time Computation
- **Input:** h-m1 saturation dates + adoption dates
- **Processing:** Temporal offset calculation (adoption_date - saturation_date)
- **Output:** Lead time in months per (benchmark, shift) pair
- **Metrics:** Precede fraction, mean lead time

### FR4: Statistical Validation
- **Tests:** McNemar test, permutation baseline
- **Null Hypothesis:** Lead times random (50% precede/lag)
- **Significance:** p < 0.05
- **Output:** p-values, effect sizes

### FR5: Visualization
- **Timeline Plot:** Saturation dates vs adoption dates
- **Histogram:** Lead time distribution with 6-month threshold
- **Output:** PNG figures in h-m2/figures/

### FR6: Gate Evaluation
- **Primary (P1):** Precede fraction ≥0.6 AND mean lead >6 months
- **Secondary (S1-S3):** Mean lead >6mo, no post-shift lags, p<0.05
- **Output:** PASS/FAIL decision + validation report

## Data Requirements

### Datasets

| Dataset | Type | Source | Sample Size |
|---------|------|--------|-------------|
| **Citation Time Series** | Custom (real) | Semantic Scholar API | 3 papers × ~100-500 monthly records |
| **h-m1 Saturation Dates** | Derived | h-m1/results/convergence_results.json | 3 benchmarks (ImageNet, GLUE, SQuAD) |

### Benchmark-Shift Mapping

| Benchmark | Paradigm Shift | Expected Lead Time |
|-----------|----------------|-------------------|
| ImageNet | ViT (2021) | 2015-08 → 2021-Q4 (~6.3 years) |
| GLUE | GPT-3 (2020) | 2018-03 → 2020-Q3 (~2.4 years) |
| SQuAD | GPT-3 (2020) | 2018-05 → 2020-Q3 (~2.3 years) |

### Data Access

- **Semantic Scholar API:** Free tier, 100 req/5min
- **Rate Limiting:** Implemented in citation_fetcher.py
- **Caching:** h-m2/data/citations/{paper_id}.json

## Baseline Methods

| Baseline | Purpose | Implementation |
|----------|---------|----------------|
| **Random Timing** | Chance-level comparison | Shuffle saturation dates 1000× |
| **Score-Only** | Future dual-metric validation | Use h-m1 convergence dates (current) |

## Evaluation Metrics

| Metric | Type | Target | Formula |
|--------|------|--------|---------|
| **Precede Fraction** | Primary (P1) | ≥60% | `sum(lead_time > 6) / n_pairs` |
| **Mean Lead Time** | Secondary (S1) | >6 months | `mean(lead_times)` |
| **Post-Shift Lag Rate** | Secondary (S2) | 0% | `sum(lead_time < -3) / n_pairs` |
| **Statistical Significance** | Secondary (S3) | p<0.05 | McNemar test p-value |

## Success Criteria

### Gate PASS Conditions

1. ✅ Precede fraction ≥60% (P1)
2. ✅ Mean lead time >6 months (S1)
3. ✅ Statistical significance p<0.05 (S3)

### Gate FAIL Response

IF <60% precede OR mean lead <3 months → **ABANDON** temporal claim per SHOULD_WORK gate

## Non-Functional Requirements

### NFR1: Performance
- Total runtime: <30 minutes (API calls rate-limited)
- Citation fetch: <10 min (3 papers, cached)

### NFR2: Reproducibility
- Random seed: 42 for permutation tests
- Cache all API responses (no re-fetch on re-run)

### NFR3: Dependencies
- Python 3.10+
- Libraries: pandas, numpy, scipy, matplotlib, requests
- Network: Internet access for Semantic Scholar API

### NFR4: Output Quality
- All figures: 300 DPI PNG
- Validation report: Markdown with tables
- Results: JSON with full precision

## Code Structure

```
h-m2/
├── code/
│   ├── citation_fetcher.py         # Semantic Scholar API client
│   ├── adoption_detector.py        # Rolling avg threshold detection
│   ├── lead_time_analyzer.py       # Temporal alignment computation
│   ├── statistical_validator.py    # McNemar test, permutation baseline
│   ├── visualizer.py               # Timeline + histogram plots
│   └── main_experiment.py          # Pipeline orchestration
├── data/
│   ├── citations/                  # Citation time series JSON
│   └── shift_adoption_dates.json   # Detected adoption dates
├── figures/                        # Visualizations
└── results/
    ├── lead_times.json             # Per-pair results
    └── statistical_validation.json # p-values
```

## Dependencies

**Python Packages:**
- pandas (time series)
- numpy (numerical)
- scipy (McNemar test)
- matplotlib (visualization)
- requests (API calls)

**Data Dependencies:**
- h-m1/results/convergence_results.json (saturation dates)
- Semantic Scholar API (citation data)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **R1: Citation data gaps** | Accept quarterly granularity, document gaps |
| **R2: Adoption date ambiguity** | 3-month sustained window, consensus validation |
| **R3: Small sample size** | Fisher exact test, report effect size |
| **R4: Synthetic data contamination** | Document provenance, test temporal mechanism independence |

## Timeline & Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Data Prep | 1h | Citation time series cached |
| Adoption Detection | 1h | shift_adoption_dates.json |
| Lead Time Computation | 30min | lead_times.json |
| Statistical Validation | 30min | statistical_validation.json |
| Visualization | 30min | Figures (timeline, histogram) |
| Gate Evaluation | 15min | 04_validation.md |
| **Total** | **3.5h** | |

## Acceptance Criteria

- [ ] Citation data for 3 paradigm shift papers cached
- [ ] Adoption dates detected and validated against consensus
- [ ] Lead times computed for ≥9 (benchmark, shift) pairs
- [ ] Statistical tests executed (McNemar + permutation)
- [ ] Visualizations generated (timeline + histogram)
- [ ] Gate evaluation complete with PASS/FAIL decision
- [ ] 04_validation.md report generated

## Out of Scope

- Citation-based saturation detection (deferred to h-m3)
- Dual-metric (convergence + velocity) comparison (awaits h-e2)
- Expansion to >3 benchmarks (future work)
- Real PWC data integration (h-m1 uses synthetic, h-m2 tests temporal mechanism independence)
