# Validation Report: H-C1 (CONDITION)

**Hypothesis**: Mode 3 proportion is higher for subjective prompts (creative writing) than objective prompts (math/coding) with ratio > 1.5

**Gate Type**: SHOULD_WORK

## Execution Summary

| Step | Status |
|------|--------|
| Environment Setup (S-1) | DONE |
| Config + keyword lists (C-1) | DONE |
| Prompt categorization (C-2) | DONE |
| Category filtering (C-3) | DONE |
| Mode 3 stratified counts (C-4) | DONE |
| Two-proportion z-test (C-5) | DONE |
| Ratio CI + effect size (C-6) | DONE |
| Result classification (C-7) | DONE |
| Pipeline integration (C-8) | DONE |

## Results

### Category Distribution
- Subjective: 9,839 battles
- Objective: 4,349 battles
- Ambiguous (excluded): 43,289 battles

### Mode 3 Counts
| Category | Mode 3 | Total | Proportion |
|----------|--------|-------|------------|
| Subjective | 2,184 | 9,839 | 22.20% |
| Objective | 901 | 4,349 | 20.72% |

### Statistical Analysis
| Metric | Value |
|--------|-------|
| Ratio (p_subj / p_obj) | 1.0714 |
| 95% CI | [1.0001, 1.1479] |
| z-statistic | 1.9703 |
| p-value (one-sided) | 0.0244 |
| Cohen's h | 0.0361 |

### Classification
**INCONCLUSIVE**

The ratio is 1.07, which is:
- Greater than 1.0 (not falsified)
- Less than 1.5 (not confirmed per hypothesis threshold)
- Statistically significant (p < 0.05) but effect size is negligible (h = 0.036)

## Gate Verdict

**GATE NOT SATISFIED**

The hypothesis required ratio > 1.5. Observed ratio = 1.07. While subjective prompts show slightly higher Mode 3 proportion, the difference is far below the predicted threshold.

## Artifacts
- `code/outputs/category_mode_distribution.json`
- `code/outputs/ratio_analysis.json`
- `code/outputs/prompt_categories.parquet`
