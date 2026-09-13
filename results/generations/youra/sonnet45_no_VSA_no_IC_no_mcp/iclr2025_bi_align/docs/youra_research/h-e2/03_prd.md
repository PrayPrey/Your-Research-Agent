# Product Requirements Document: h-e2

**Hypothesis:** AI response diversity correlates with query diversity (r > 0.4) in well-aligned conversations
**Type:** EXISTENCE
**Date:** 2026-08-25

---

## Executive Summary

Build observational analysis pipeline measuring correlation between user query diversity and AI response diversity in HH-RLHF dataset. Success: Pearson r > 0.4 with p < 0.05.

---

## Functional Requirements

### FR1: Dataset Loading & Parsing
- Load HH-RLHF from Hugging Face Datasets
- Parse multi-turn conversations splitting on "\n\nHuman:" and "\n\nAssistant:"
- Extract user queries and AI responses per conversation
- Compute helpfulness median and filter conversations with helpfulness > median

### FR2: Diversity Metrics
- Implement distinct-1 metric: unique unigrams / total unigrams
- Compute query diversity per conversation (aggregate all user turns)
- Compute response diversity per conversation (aggregate all AI turns)
- Handle edge cases: empty conversations, single-turn conversations

### FR3: Statistical Analysis
- Compute Pearson correlation between query diversity and response diversity
- Calculate p-value for significance testing
- Report 95% confidence interval for correlation coefficient
- Test success criterion: r > 0.4 AND p < 0.05

### FR4: Secondary Analyses
- Sensitivity: correlation across helpfulness quartiles (Q1-Q4)
- Robustness: correlation across r thresholds [0.3, 0.35, 0.4, 0.45, 0.5]
- Stratification: correlation by conversation length bins (2-3, 4-5, 6+ turns)

### FR5: Visualization
- **Mandatory:** Bar chart comparing target r (0.4) vs observed r with CI
- **Autonomous:** Scatter plot (query diversity vs response diversity) with regression line
- **Autonomous:** Distribution histograms (query diversity, response diversity)
- **Autonomous:** Sensitivity analysis line plot (r vs helpfulness percentile)
- **Autonomous:** Stratification bar chart (r by conversation length)

---

## Non-Functional Requirements

### Performance
- Dataset loading: < 5 minutes
- Full pipeline runtime: < 30 minutes
- Memory footprint: < 8GB RAM

### Reproducibility
- Random seed control (if any sampling)
- Deterministic preprocessing pipeline
- Version-pinned dependencies (datasets, scipy, numpy, matplotlib)

### Reliability
- Graceful handling of malformed conversations
- Validation: minimum 2 turns per conversation
- Warning if sample size < 100 conversations

---

## Data Requirements

**Source:** Anthropic/hh-rlhf (Hugging Face Datasets)
**Size:** 161k conversations (train + test combined)
**Filtering:** helpfulness > median, minimum 2 turns
**Expected sample:** ~80k conversations after filtering

---

## Success Metrics

**Primary:** r > 0.4 AND p < 0.05
**Secondary:** Sample size > 1000 conversations for reliable correlation

---

## Out of Scope

- Model training or fine-tuning
- New dataset collection
- Alternative diversity metrics beyond distinct-1
- Causal analysis (observational study only)

---

## Dependencies

- datasets (Hugging Face)
- scipy.stats (Pearson correlation)
- numpy (median, basic stats)
- matplotlib (visualization)

---

## Acceptance Criteria

1. Code executes without errors
2. Loads HH-RLHF and filters to well-aligned subset
3. Computes distinct-1 for queries and responses
4. Reports Pearson r and p-value
5. Generates mandatory gate metrics bar chart
6. Passes/fails based on r > 0.4 AND p < 0.05
