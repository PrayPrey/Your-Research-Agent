# Product Requirements Document: H-M4
# Hedging-Confidence Correlation Analysis

**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Date:** 2026-08-19
**Base Hypothesis:** H-M3

---

## 1. Executive Summary

H-M4 tests whether LLMs incorporate uncertainty signals (hedging markers) into their confidence judgments. This is validated by computing Spearman correlation between hedging marker count and verbalized confidence scores from H-M2 cached outputs.

**Key Insight:** This is a statistical analysis hypothesis, not a model training experiment. All data comes from H-M2's 817 processed TruthfulQA outputs.

---

## 2. Problem Statement

### 2.1 Research Question
Do hedging markers in CoT reasoning negatively correlate with verbalized confidence, indicating the model incorporates uncertainty signals?

### 2.2 Hypothesis Statement
Under CoT+confidence conditions, if hedging markers are present in reasoning, then verbalized confidence correlates negatively with marker count, because the model incorporates uncertainty signals into its confidence judgment.

### 2.3 Gate Condition
- **Primary:** Spearman r < -0.2 (moderate negative correlation)
- **Secondary:** p-value < 0.05 (statistically significant)

---

## 3. Functional Requirements

### FR-1: Data Loading (Priority: Critical)
Load H-M2 cached results containing hedging counts and confidence scores.
- **Input:** `../h-m2/code/results/h-m2_results.json`
- **Output:** Paired arrays of (hedging_count, confidence_score)
- **Validation:** n >= 500 valid data points

### FR-2: Correlation Analysis (Priority: Critical)
Compute Spearman rank correlation between hedging count and confidence.
- **Method:** scipy.stats.spearmanr
- **Output:** correlation coefficient (r) and p-value
- **Gate Check:** r < -0.2 AND p < 0.05

### FR-3: Statistical Validation (Priority: High)
Validate correlation results with additional statistical measures.
- Compute 95% confidence interval for correlation
- Verify sample size adequacy
- Check for outliers that might skew results

### FR-4: Visualization Generation (Priority: High)
Generate required figures for analysis.
- Scatter plot with regression line (hedging vs confidence)
- Box plot by hedging bucket (0, 1-2, 3-5, 6+)
- Bar chart comparing threshold vs actual r value

### FR-5: Results Export (Priority: Medium)
Save analysis results in standard format.
- JSON results file with all metrics
- PNG figures for paper inclusion
- Markdown summary for validation report

---

## 4. Data Specification

### 4.1 Primary Dataset

**Source:** H-M2 Cached Outputs
- **Path:** `../h-m2/code/results/h-m2_results.json`
- **Size:** 817 items (full TruthfulQA test set)
- **Format:** JSON with hedging_count, confidence, output_text fields
- **Download Required:** NO (cached from H-M2)

### 4.2 Data Schema

```python
@dataclass
class H_M2_Output:
    question_id: str
    output_text: str
    hedging_count: int       # Count of hedging markers
    confidence: float        # Verbalized confidence 0-100
    hedging_markers: List[str]  # Actual markers found
    is_correct: bool         # Answer correctness
```

### 4.3 Auto-Download Datasets
- None required - all data from H-M2 cache

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Analysis completion in < 10 seconds
- Memory usage < 500MB

### NFR-2: Reproducibility
- Fixed random seed for any sampling
- Deterministic correlation computation

### NFR-3: Compatibility
- Python 3.8+
- scipy >= 1.7.0

---

## 6. Success Criteria

### 6.1 Gate Metrics (MUST_WORK)

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Spearman r | < -0.2 | Moderate negative correlation |
| p-value | < 0.05 | Statistical significance |
| n_samples | >= 500 | Adequate sample size |

### 6.2 Expected Values (Literature)
- Correlation strength: -0.2 to -0.5 (moderate negative)
- Based on Lin et al. 2022 uncertainty-language correlations

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.7.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
```

### 7.2 Internal Dependencies
- H-M2 results file must exist
- H-M2 validation must have passed

### 7.3 External Repositories
- None required (pure statistical analysis)

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| H-M2 data missing | Critical | Verify file exists at startup |
| Weak correlation | Gate failure | Report actual r for analysis |
| Non-linear relationship | Misleading results | Include scatter plot for visual inspection |

---

## 9. Out of Scope

- New LLM API calls (using cached data)
- Model training or fine-tuning
- Additional dataset collection
- Causal inference (correlation only)

---

## 10. References

1. Xiong et al. 2023 - "Can LLMs Express Their Uncertainty?"
2. Tian et al. 2023 - "Just Ask for Calibration"
3. Lin et al. 2022 - "Teaching Models to Express Their Uncertainty"
4. scipy.stats.spearmanr documentation

---

*Phase 3 PRD for H-M4 Hedging-Confidence Correlation Analysis*
