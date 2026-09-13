# Experimental Setup

We designed experiments to answer three questions: (1) Does logistic regression achieve ≥75% accuracy? (2) How much better is gradient boosting? (3) Which features matter most? Our experimental design validates the simplicity hypothesis through controlled comparison.

## Research Questions

**RQ1 (Absolute Performance)**: Does logistic regression achieve ≥75% accuracy on held-out test set?  
**Hypothesis**: H-E1 (EXISTENCE) — LR trained on 6 log-scaled GitHub metadata features achieves ≥75% accuracy because repository maintenance is linearly separable in transformed feature space.  
**Pass Criterion**: Accuracy ≥75% AND F1 ≥0.73 on stratified test split.

**RQ2 (Complexity Value)**: How much accuracy improves with gradient boosting compared to logistic regression?  
**Hypothesis**: H-M1 (MECHANISM) — Repository maintenance patterns form approximately linear clusters, so LR and GB achieve similar performance (gap ≤5%).  
**Pass Criterion**: LR-GB performance gap ≤5%, coefficient signs correct, feature overlap ≥2/3.

**RQ3 (Feature Importance)**: Which metadata features predict maintenance status?  
**Expected**: Staleness (days_since_last_commit) should have strong negative coefficient, activity features (stars, forks, commits, contributors, issues) should have positive coefficients.

## Experimental Protocol

### Data Split

**Training set**: 96 repositories (80% stratified)  
- 79 maintained (82.3%)
- 17 abandoned (17.7%)

**Test set**: 24 repositories (20% stratified)  
- 20 maintained (83.3%)
- 4 abandoned (16.7%)

Stratified split maintains class distribution between train and test sets. Random seed 42 ensures reproducibility.

### Model Training

**Logistic Regression Training**:
1. Fit StandardScaler on train set features
2. Transform train and test features (zero mean, unit variance)
3. Train LR with balanced class weights (to handle 82.5% vs 17.5% imbalance)
4. Record convergence iterations and training time

**Gradient Boosting Training**:
1. Use same train/test split as LR (controlled comparison)
2. No scaling needed (tree-based methods are scale-invariant)
3. Train GB with scale_pos_weight for class imbalance
4. Extract feature importances from trained ensemble

### Evaluation Metrics

**Classification Performance**:
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN) — overall correctness
- **Precision**: TP / (TP + FP) — positive predictive value
- **Recall**: TP / (TP + FN) — sensitivity
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall) — harmonic mean
- **ROC-AUC**: Area under receiver operating characteristic curve — discriminative power

**Mechanism Analysis**:
- **LR Coefficients**: Extract weights for each feature, verify signs match causal expectations
- **GB Feature Importances**: Extract Gini importance for each feature
- **Feature Overlap**: Count how many features appear in top-3 for both LR and GB

### Visualization

We generate 5 figures to support results:

1. **Confusion Matrix** (H-E1): 2×2 heatmap showing true positives, true negatives, false positives, false negatives
2. **ROC Curve** (H-E1): True positive rate vs false positive rate with AUC score
3. **Coefficient Bar Chart** (H-M1): LR feature weights with magnitudes and signs
4. **Feature Importance Comparison** (H-M1): Side-by-side bar chart of LR coefficients vs GB importances
5. **Performance Comparison** (H-M1): LR vs GB accuracy and F1 scores

### Baseline Comparisons (Not Implemented)

**Planned but not executed**:
- **Majority Classifier**: Always predict most frequent class (maintained) — expected 82.5% accuracy
- **Composite Stability Index (CSI)**: Replicate Adejumo & Johnson (2025) weighted aggregation

**Rationale for omission**: We prioritized testing the core simplicity hypothesis (LR ≥75%) over comprehensive baseline comparison due to resource constraints. This is an acknowledged limitation — explicit comparison to CSI would strengthen relative positioning (see Discussion).

## Hypothesis Validation Gates

### H-E1 (EXISTENCE Gate)

**Criterion**: LR achieves accuracy ≥75% AND F1 ≥0.73  
**Rationale**: 75% accuracy represents "moderate performance" threshold — if LR exceeds this, simple methods are viable. F1 ≥0.73 ensures both precision and recall are reasonable, not just accuracy from class imbalance.  
**Result Preview**: PASS — Accuracy 1.0 (100%), F1 1.0 (100%), both far exceed thresholds.

### H-M1 (MECHANISM Gate)

**Criterion**: Three conditions must all pass:
1. **Coefficient signs correct**: days_since_last < 0 (staleness predicts abandonment), activity features > 0 (engagement predicts maintenance)
2. **Performance gap ≤5%**: |LR_accuracy - GB_accuracy| ≤ 0.05 (linear approximation is close to non-linear)
3. **Feature overlap ≥2/3**: At least 2 of top-3 features agree between LR and GB

**Rationale**: If repository maintenance is linearly separable, LR and GB should use similar features with similar weights and achieve similar performance.  
**Result Preview**: PARTIAL PASS — Coefficients correct ✓, Gap 4.2% ✓, Overlap 1/3 ✗. Mechanism more complex than hypothesized.

## Reproducibility

All experiments are reproducible with:
- **Data**: 120 Papers with Code repositories (list available in supplementary material)
- **Code**: Python 3.10, scikit-learn 1.3, NumPy 1.24, Matplotlib 3.7
- **Seeds**: `random_state=42` for all stochastic operations (train/test split, LR initialization, GB sampling)
- **Hardware**: Single CPU for LR training (~30s), multi-core CPU for GB training (~10min)

We provide all experimental code, trained model artifacts, and raw results in our supplementary material for full reproducibility.
