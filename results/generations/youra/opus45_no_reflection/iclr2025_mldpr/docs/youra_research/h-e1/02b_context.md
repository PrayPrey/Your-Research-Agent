# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

## Hypothesis Statement

Under the condition of analyzing Papers With Code data (2018-2024), if foundation model emergence represents a structural break, then PELT change-point detection will identify a statistically significant change point in aggregate Gini coefficient time series within the 2019-2022 window at α=0.05.

## Rationale

This establishes whether a detectable phase transition signal exists in the data before testing the causal mechanism. Without confirming existence, mechanism testing is premature.

## Variables

- **IV:** Time period (pre-2020 vs post-2021)
- **DV:** Gini coefficient of benchmark usage distribution [0,1]
- **CV:** Publication volume (normalized by monthly paper count)

## Success Criteria (PoC: Direction-based)

- **Primary:** Change point detected within 2019-2022 at α=0.05
- **Secondary:** Segmented model fits better than single monotonic trend (BIC comparison)

## Verification Protocol

1. Download PWC historical dumps and parse task-dataset-metric triplets (2018-2024)
2. Compute monthly aggregate Gini coefficient time series
3. Apply PELT algorithm with α=0.05 significance threshold
4. Test if change point falls within 2019-2022 window

## Failure Response

- IF fails: PIVOT to quarterly aggregation or alternative change-point method (Bai-Perron)

## Dataset

- **Source:** Papers With Code Historical Data (standard)
- **URL:** https://github.com/paperswithcode/paperswithcode-data
- **Path:** PWC daily dumps (2018-2024)
- **Unit:** Task-dataset-metric triplets with paper associations

## Model/Method

- **Type:** Statistical Analysis Pipeline
- **Components:** ruptures (PELT), scipy (stats), custom Gini implementation
- **Baseline:** Koch et al. (2021) concentration metrics

## Baseline Reference

| Method | Performance | Dataset |
|--------|-------------|---------|
| Koch et al. (2021) | Gini ~0.6-0.7 for 2015-2020 | Papers With Code + Semantic Scholar |

## Dependencies

None (first hypothesis in chain)

## Gate Condition

MUST_WORK gate - if this fails, entire verification stops and hypothesis needs reassessment.

## Risks Affecting This Hypothesis

| Risk | Severity | Mitigation |
|------|----------|------------|
| R1: PWC data incomplete | High | Semantic Scholar supplementation |
| R2: Triplet unit miscalibrated | Medium | Paper-dataset pair robustness check |
| R4: Temporal resolution insufficient | High | Quarterly sensitivity analysis |
| R5: Volume confound inseparable | High | Dual reporting (raw + normalized) |
