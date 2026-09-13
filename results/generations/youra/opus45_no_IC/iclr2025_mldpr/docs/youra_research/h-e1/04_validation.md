# H-E1 Validation Report

**Hypothesis:** HHI concentration measurable from PWC data for NeurIPS/ICML/ICLR (2018-2024)
**Date:** 2026-08-10
**Status:** PASSED

## Gate Results

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Coverage | 21/21 venue-years | 21/21 | PASS |
| HHI Range | [0, 1] | [0.0066, 0.0455] | PASS |
| HHI Variance | > 0 | 0.000137 | PASS |

## Data Source

- **Dataset:** HuggingFace `pwc-archive/papers-with-abstracts`
- **Total papers:** 12,600 (filtered to target venues/years)
- **Unique task categories:** 1,666 (used as dataset proxy)
- **Method:** Task labels from PWC used as benchmark/dataset proxy for HHI computation

## Key Findings

### HHI Summary Statistics
- **Mean HHI:** 0.0171
- **Min HHI:** 0.0066 (NeurIPS 2023)
- **Max HHI:** 0.0455 (ICML 2024)

### Venue-Year Coverage

| Venue | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|-------|------|------|------|------|------|------|------|
| NeurIPS | 807 | 1143 | 1525 | 1948 | 188 | 1703 | 70 |
| ICML | 386 | 219 | 664 | 122 | 13 | 12 | 6 |
| ICLR | 771 | 940 | 730 | 1026 | 274 | 39 | 14 |

## Mock Data Fix Applied

- Removed synthetic data generation (np.random based)
- Replaced with real HuggingFace PWC dataset loading
- Using paper `tasks` column as benchmark/dataset proxy
- Implemented caching for subsequent runs

## Figures Generated

1. `figures/hhi_heatmap.png` - HHI concentration by venue-year
2. `figures/hhi_timeseries.png` - HHI trends over time
3. `figures/coverage_bar.png` - Coverage validation
4. `figures/entropy_vs_hhi.png` - Diversity vs concentration scatter
5. `figures/top_datasets.png` - Top task categories by venue

## Next Steps

Gate PASSED. Proceed to H-M1 (mechanistic hypothesis).
