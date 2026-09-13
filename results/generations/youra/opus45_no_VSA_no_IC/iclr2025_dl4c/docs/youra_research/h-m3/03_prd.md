# Product Requirements Document: h-m3

**Hypothesis:** Unanimous scale agreement indicates ≥10% higher verdict reliability vs split verdicts
**Type:** MECHANISM
**Date:** 2026-08-24

---

## 1. Overview

### 1.1 Purpose
Validate whether unanimous agreement among LLM judges serves as a reliable confidence signal. When all judges agree on a verdict, we expect higher accuracy than when judges disagree.

### 1.2 Scope
- Analyze existing judge verdict data from h-e1/h-m2
- Compare accuracy: unanimous vs split verdicts
- Statistical significance testing (two-proportion z-test)

### 1.3 Success Criteria
- **Primary:** Unanimous accuracy exceeds split accuracy by ≥10%
- **Secondary:** p-value < 0.05 (statistically significant)
- **Falsification:** Improvement < 5%

---

## 2. Functional Requirements

### 2.1 Data Loading (FR-1)
- Load h-e1/code/outputs/results.csv
- Parse columns: problem_id, judge_model, verdict, ground_truth
- Validate 164 problems × 4 judges = 656 verdicts

### 2.2 Agreement Classification (FR-2)
- Group verdicts by problem_id
- Classify as unanimous (all 4 judges agree) or split (any disagreement)
- Track verdict distribution

### 2.3 Accuracy Computation (FR-3)
- For unanimous problems: compare consensus verdict to ground_truth
- For split problems: compare majority verdict to ground_truth
- Compute accuracy percentages for each group

### 2.4 Statistical Testing (FR-4)
- Two-proportion z-test (one-tailed, H1: unanimous > split)
- Report z-statistic, p-value
- 95% confidence intervals for each accuracy

### 2.5 Visualization (FR-5)
- Bar chart: unanimous vs split accuracy with error bars
- Pie chart: agreement distribution
- Save to h-m3/figures/

### 2.6 Results Output (FR-6)
- Generate 04_validation.md report
- JSON metrics output for gate evaluation

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Complete analysis in < 10 seconds (656 verdicts)

### 3.2 Reproducibility
- Fixed random seed where applicable
- Deterministic output

---

## 4. Data Requirements

### 4.1 Input Data
- **Source:** h-e1/code/outputs/results.csv
- **Format:** CSV with columns [problem_id, judge_model, verdict, ground_truth]
- **Size:** 164 problems × 4 judges

### 4.2 Output Data
- **Metrics:** unanimous_acc, split_acc, improvement, z_stat, p_value
- **Figures:** PNG files in h-m3/figures/
- **Report:** 04_validation.md

---

## 5. Dependencies

### 5.1 Data Dependencies
- h-e1 results.csv must exist and be valid

### 5.2 Software Dependencies
- Python 3.10+
- pandas, numpy, scipy, matplotlib

---

## 6. Gate Evaluation

### 6.1 Pass Condition
```
improvement >= 0.10 AND p_value < 0.05
```

### 6.2 Fail Condition
```
improvement < 0.05
```

### 6.3 Inconclusive
```
0.05 <= improvement < 0.10 OR p_value >= 0.05
```
