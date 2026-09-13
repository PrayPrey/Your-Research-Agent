# Phase 2C Experiment Brief: H-E2

**Hypothesis**: CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05)  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Prerequisites**: H-E1 (COMPLETED)  
**Date**: 2026-08-10

---

## 1. Objective

Test whether the coefficient of variation of participation ratio (CV_PR) extracted in H-E1 correlates negatively with ImageNet top-1 accuracy across 100+ pretrained timm models.

**Success Criteria**:
- Pearson r < -0.3
- p-value < 0.05

**Falsification**:
- r >= 0 OR p >= 0.05

---

## 2. Data Sources

### 2.1 CV_PR Data (from H-E1)
- **Source**: `h-e1/h-e1/results/results.csv`
- **Format**: `model,model_cv_pr,time_sec,n_layers`
- **Sample size**: 100 models
- **CV_PR range**: [0.0014, 0.0326]

### 2.2 ImageNet Accuracy Data
- **Source**: timm results CSV from GitHub
- **URL**: `https://github.com/huggingface/pytorch-image-models/blob/main/results/results-imagenet.csv`
- **Format**: `model,img_size,top1,top1_err,top5,top5_err,param_count,...`
- **Type**: standard (official ImageNet-1k validation set, 50,000 images)

### 2.3 Data Merge Strategy
1. Download `results-imagenet.csv` from timm repo
2. Match model names between CV_PR results and accuracy data
3. Handle naming variations (e.g., `.in1k` suffixes)
4. Report unmatched models

---

## 3. Analysis Pipeline

### 3.1 Step 1: Data Loading
```python
cv_pr_df = pd.read_csv("h-e1/h-e1/results/results.csv")
accuracy_df = pd.read_csv("results-imagenet.csv")
```

### 3.2 Step 2: Model Name Matching
- Strip common suffixes for matching
- Log match rate (expect >90%)

### 3.3 Step 3: Correlation Analysis
```python
from scipy.stats import pearsonr, spearmanr

r_pearson, p_pearson = pearsonr(merged['model_cv_pr'], merged['top1'])
r_spearman, p_spearman = spearmanr(merged['model_cv_pr'], merged['top1'])
```

### 3.4 Step 4: Visualization
- Scatter plot: CV_PR vs top1 accuracy
- Regression line with 95% CI
- Annotate r and p values

### 3.5 Step 5: Robustness Checks
- Bootstrap 95% CI for correlation
- Outlier analysis (models >2σ from trend)
- Spearman rank correlation (non-parametric)

---

## 4. Expected Results

| Metric | Expected | Threshold |
|--------|----------|-----------|
| Pearson r | < -0.3 | < -0.3 |
| p-value | < 0.05 | < 0.05 |
| Sample size | ~100 | >= 80 after matching |

---

## 5. Failure Modes

| Mode | Detection | Mitigation |
|------|-----------|------------|
| Low match rate | <80% models matched | Manual name alignment |
| Weak correlation | -0.3 < r < 0 | Report as partial support |
| Non-significant | p >= 0.05 | Bootstrap CI analysis |
| Confounders | param_count drives effect | Partial correlation |

---

## 6. Deliverables

1. `h-e2/code/correlate.py` - Analysis script
2. `h-e2/results/correlation_results.json` - Statistics
3. `h-e2/figures/scatter_cv_pr_vs_accuracy.png` - Visualization
4. `h-e2/04_validation.md` - Phase 4 validation report

---

## 7. Timeline

| Task | Duration |
|------|----------|
| Data download & merge | 10 min |
| Correlation analysis | 5 min |
| Visualization | 5 min |
| Robustness checks | 10 min |
| **Total** | ~30 min |

---

## 8. Dependencies

```
scipy>=1.10
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
requests (for CSV download)
```

---

## 9. Code Skeleton

```python
#!/usr/bin/env python3
"""H-E2: CV_PR vs ImageNet Accuracy Correlation Analysis"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import requests

# Constants
CVPR_PATH = "h-e1/h-e1/results/results.csv"
ACCURACY_URL = "https://raw.githubusercontent.com/huggingface/pytorch-image-models/main/results/results-imagenet.csv"
THRESHOLD_R = -0.3
THRESHOLD_P = 0.05

def main():
    # 1. Load data
    cv_pr_df = pd.read_csv(CVPR_PATH)
    accuracy_df = pd.read_csv(ACCURACY_URL)
    
    # 2. Normalize model names
    cv_pr_df['model_norm'] = cv_pr_df['model'].str.lower()
    accuracy_df['model_norm'] = accuracy_df['model'].str.lower()
    
    # 3. Merge
    merged = cv_pr_df.merge(accuracy_df[['model_norm', 'top1']], on='model_norm')
    print(f"Matched {len(merged)}/{len(cv_pr_df)} models")
    
    # 4. Correlation
    r, p = pearsonr(merged['model_cv_pr'], merged['top1'])
    print(f"Pearson r={r:.4f}, p={p:.4e}")
    
    # 5. Verdict
    if r < THRESHOLD_R and p < THRESHOLD_P:
        print("PASS: H-E2 supported")
    else:
        print("FAIL: H-E2 not supported")
    
    return r, p

if __name__ == "__main__":
    main()
```

---

## 10. Archon References

- **H-E1 Validation**: Confirmed CV_PR extraction for 100 models
- **Phase 2B Plan**: Defined r < -0.3 threshold
- **Unterthiner 2020**: Baseline comparison for Phase 5
