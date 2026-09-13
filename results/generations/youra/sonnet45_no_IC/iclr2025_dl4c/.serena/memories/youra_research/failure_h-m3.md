# Phase 4 Failure: h-m3 (XGBoost Gradient Boosting)

**Date:** 2026-07-12  
**Hypothesis:** h-m3 - XGBoost Classifier Achieves Target Performance  
**Gate Type:** DETERMINES_SUCCESS  
**Gate Result:** FAIL (3/5 conditions failed)

## Failure Summary

XGBoost gradient boosting failed to meet DETERMINES_SUCCESS gate criteria due to severe overfitting on a small dataset (340 samples, 238 training).

### Failed Gate Conditions

1. **Test Precision < 0.80** (Actual: 0.7391)
   - 6 false positives out of 31 negatives
   - Model incorrectly flags accepted code as needing revision

2. **Generalization Gap > 10%** (Actual: 20.10%)
   - Train F1: 0.9896
   - Test F1: 0.7907
   - Severe overfitting despite regularization (subsample=0.8, colsample_bytree=0.8)

3. **Bootstrap CI Lower < 0.70** (Actual: 0.6364)
   - Wide confidence interval: [0.6364, 0.9201]
   - High variance across bootstrap resamples
   - Small test set (51 samples) contributes to instability

### Passed Gate Conditions

- ✅ Test F1 ≥ 0.74 (Actual: 0.7907)
- ✅ Test Recall ≥ 0.70 (Actual: 0.8500)

## Root Cause Analysis

### 1. Dataset Size Insufficient
- **Total samples:** 340 (238 train, 51 val, 51 test)
- **Problem:** XGBoost with 100 trees easily memorizes 238 training samples
- **Evidence:** Train F1 = 0.9896 vs Test F1 = 0.7907

### 2. Model Complexity Too High
- **Configuration:** max_depth=5, n_estimators=100
- **Problem:** 100 decision trees with depth 5 can model extremely complex patterns
- **Evidence:** Perfect training performance but poor generalization

### 3. Regularization Ineffective
- **Applied:** subsample=0.8, colsample_bytree=0.8
- **Problem:** These regularization techniques insufficient for such small data
- **Evidence:** 20% generalization gap persists

## Comparison to Baseline (h-m2)

| Metric | h-m2 (LogReg) | h-m3 (XGBoost) | Delta |
|--------|---------------|----------------|-------|
| Test F1 | 0.7500 | 0.7907 | +0.0407 |
| Test AUC | 0.8677 | 0.9274 | +0.0597 |
| Test Precision | 0.7500 | 0.7391 | -0.0109 |
| Gen Gap | ~5% | 20.10% | +15% |

**Insight:** XGBoost achieves higher F1 and AUC but at the cost of severe overfitting and lower precision.

## Lessons Learned

### What NOT to Do

1. **Don't use XGBoost on datasets < 1000 samples**
   - Decision tree ensembles require substantial data to avoid overfitting
   - Linear models (logistic regression) more appropriate for small datasets

2. **Don't ignore generalization gap in gate criteria**
   - High test metrics alone insufficient - must also check train/test gap
   - 20% gap indicates model won't generalize to real-world code

3. **Don't trust bootstrap CI with small test sets**
   - 51 test samples too small for stable confidence intervals
   - Wide CI [0.64, 0.92] indicates high uncertainty

### What TO Do Next

1. **Increase Dataset Size**
   - Collect more samples (target: 1000+ for XGBoost, 500+ for linear models)
   - Current 340 samples insufficient for complex models

2. **Try Simpler Models First**
   - h-m2 logistic regression already achieves F1=0.75 without overfitting
   - Consider regularized linear models (Ridge, Elastic Net) before trees

3. **Feature Engineering Over Model Complexity**
   - Combine execution + static features (h-integrated hypothesis)
   - Better features > more complex models on small data

4. **Stricter Cross-Validation**
   - Use nested CV for hyperparameter tuning
   - Monitor train/val/test gaps during tuning

## Routing Decision

**Action:** Route to Phase 2A (Hypothesis Redesign)

**Rationale:**
- Fundamental issue: dataset size insufficient for XGBoost
- Not a code bug - architectural limitation of approach
- Need to redesign hypothesis (larger dataset OR simpler model OR better features)

**Blocked Hypotheses:**
- h-integrated may face similar overfitting issues (also uses XGBoost on same small dataset)
- Should consider linear model for h-integrated OR dataset expansion first

## References

- Experiment results: `docs/youra_research/h-m3/code/outputs/experiment_results.json`
- Validation report: `docs/youra_research/h-m3/04_validation.md`
- Prerequisite: `mem:youra_research/failure_h-m2` (passed)

## Related Hypotheses

- h-m2: Linear baseline (PASSED with F1=0.75, no overfitting)
- h-integrated: Planned XGBoost on combined features (SHOULD RECONSIDER approach)

## Tags

#phase4 #failure #overfitting #xgboost #small-dataset #determines-success #generalization-gap #precision-fail
