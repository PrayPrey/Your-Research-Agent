# H-M1 Analysis Report: Error Traces Contain Counterfactual Information

## Summary

- **Total samples**: 1095
- **Mean CF score**: 0.439
- **Median CF score**: 0.400
- **Samples with CF_score >= 0.4**: 928 (84.7%)

## Success Criteria Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| CF_score >= 0.4 rate | >70% | 84.7% | PASS |
| Mean CF_score | >0.5 | 0.439 | FAIL |
| Root cause accuracy | >60% | 51.8% | FAIL |

## Gate Verdict

**PASS**: 84.7% of traces have CF_score >= 0.4

## CF Score Distribution

- Mean: 0.439
- Median: 0.400
- Std: 0.249
- 70th percentile: 0.400
- Min: 0.000
- Max: 0.800

## Hypothesis Test

H0: mean CF_score <= 0.4
H1: mean CF_score > 0.4

- t-statistic: 5.253
- p-value (one-sided): 0.0000
- **Result**: Reject H0

## CF Score by Bug Type (ANOVA)

- F-statistic: 89.251
- p-value: 0.0000
- Significant difference: Yes

| Bug Type | Mean CF Score |
|----------|---------------|
| logic | 0.583 |
| off_by_one | 0.265 |
| syntax | 0.400 |
| type | 0.665 |

## Root Cause Identification

- Overall accuracy: 51.8%

| Bug Type | Accuracy |
|----------|----------|
| logic | 0.4% |
| off_by_one | 5.3% |
| syntax | 83.5% |
| type | 16.9% |

## Feature Presence

| Feature | Present Rate |
|---------|--------------|
| has_line | 84.7% |
| has_expected | 24.8% |
| has_actual | 24.8% |
| has_type_info | 85.3% |
| has_variable_state | 0.0% |
