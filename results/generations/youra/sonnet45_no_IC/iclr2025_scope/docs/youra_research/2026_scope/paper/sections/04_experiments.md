# Experimental Setup

This section details the experimental protocols for the three sub-hypotheses, including datasets, evaluation metrics, and success criteria. Our design follows the decomposition strategy (Section 3): test data collection (h-e1), then correlation (h-m1), then training (h-m2) sequentially, with each stage building on the prior.

## H-E1: Benchmark Data Collection Experiment

**Research Question:** Can we collect ≥50 benchmarks with complete method comparisons from published sources?

### Data Collection Sources

We implement four collection mechanisms:

**1. OGB Collector (API-based)**
```python
from ogb.nodeproppred import PygNodePropPredDataset
# Load datasets: ogbn-arxiv, ogbn-products, ogbn-papers100M, ogbl-collab
# Extract: n_samples, n_features, n_classes from dataset.meta_info
```
Target: 15 graph datasets from OGB library with documented GCN/GraphSAINT/ClusterGCN baselines.

**2. GitHub Collector (Repository scraping)**
```python
# Fetch README.md from FedML and LEAF repositories
# Parse markdown tables for dataset statistics
```
Target: 11 federated learning datasets (FedML: 6, LEAF: 5) with FedAvg/FedProx baseline results.

**3. Papers with Code Collector (Leaderboard API, optional)**
```python
# Requires authentication; planned but not attempted in POC
```
Target: 10+ additional benchmarks from leaderboard data.

**4. Manual Collector (Paper table extraction)**
```python
# Extract from Champneys et al. Table and Zhou et al. Table V
# Store as CSV: benchmark_name, domain, sample_size, method_rankings
```
Target: 14 benchmarks (Champneys: 5 NLSI tasks, Zhou: 9 medical datasets).

### Feature Extraction Protocol

For each collected benchmark, attempt to extract:

**Tier 1 Features (Required for all benchmarks):**
- `sample_size`: From OGB `meta_info`, README, or paper reported n
- `dimensionality`: Input feature count (image: height×width×channels, tabular: number of columns)
- `num_classes`: From task definition (classification)
- `class_imbalance`: Compute Gini coefficient if class distribution available

**Tier 2 Features (Conditional on domain):**
- `autocorrelation_lag1`: If time-series data accessible
- `edge_density`: If graph structure available (OGB datasets)
- `feature_correlation_rank`: If tabular data accessible

**Method Rankings:** Extract ranking percentile (0-100%) for representatives of each method family from paper tables or official leaderboards. If multiple methods per family, use best ranking.

### Evaluation Metrics

- **Primary:** Total benchmarks collected with at least one complete method comparison
- **Coverage Metrics:**
  - Fraction of benchmarks with `sample_size` populated
  - Fraction with `dimensionality` populated
  - Fraction with `class_imbalance` populated
  - Average completeness across Tier 1 features
- **Diversity Metrics:**
  - Domain distribution (vision / NLP / tabular / time-series / graph)
  - Scale distribution (small < 1K, medium 1K-10K, large > 10K samples)
  - Data source distribution (OGB / GitHub / Manual / Papers with Code)

### Success Thresholds

- **PASS:** ≥50 benchmarks collected, ≥80% Tier 1 feature completeness
- **PARTIAL:** 30-49 benchmarks, or 60-80% completeness
- **FAIL:** <30 benchmarks, or <60% completeness (insufficient for meta-learning)

### Expected Outcomes (From Phase 2A)

We hypothesized collecting 50-60 benchmarks from the six identified sources (OGB: 15, FedML: 6, LEAF: 5, pFL-Bench: 8, Champneys: 5, Zhou: 9, Papers with Code: 10+ = 58-68 total). Tier 1 features should be "trivial to compute" (<1 sec per dataset), achievable from API metadata or README documentation.

---

## H-M1: Correlation Analysis Experiment

**Research Question:** Do dataset characteristics correlate with method family performance?

### Input Data

Use benchmarks collected in h-e1 with complete feature-ranking pairs. For each benchmark i:
- **Features:** x_i = [sample_size, dimensionality, num_classes, class_imbalance, ...]
- **Method Rankings:** y_i = [Linear_ranking, Poly_ranking, RNN_ranking, Aug_ranking]

### Statistical Test Protocol

For each (feature, method_family) pair:

**1. Data Filtering:**
```python
# Remove benchmarks with NaN values for this feature or ranking
valid_data = data.dropna(subset=['feature', 'method_ranking'])
```

**2. Spearman Correlation:**
```python
from scipy.stats import spearmanr
rho, p_value = spearmanr(valid_data['feature'], valid_data['method_ranking'])
```
Use Spearman (not Pearson) because: (1) robust to outliers, (2) captures monotonic nonlinear relationships, (3) works with ranking data.

**3. Significance Test:**
- **Statistical significance:** p < 0.05 (uncorrected; exploratory analysis)
- **Practical significance:** |ρ| > 0.3 (weak correlations below 0.3 not actionable)

**4. Visualization:**
- Heatmap (Figure 5): All 28 tests (7 features × 4 families), color-coded by ρ, markers for p < 0.05
- Scatter plots (Figure 6): Top 5 correlations with linear fit and confidence interval

### Expected Correlations (Hypothesis-Driven)

Based on Zhou [1] and Champneys [2]:
- `sample_size` ↔ `Aug_ranking`: ρ ≈ -0.5 (smaller datasets benefit more from augmentation)
- `dimensionality` ↔ `Linear_ranking`: ρ ≈ +0.4 (high-dim favors regularized linear models)
- `autocorrelation_lag1` ↔ `RNN_ranking`: ρ ≈ +0.5 (temporal structure favors RNNs)

We test these directional hypotheses but report all 28 correlations for transparency.

### Success Criteria

- **PASS:** ≥5 significant correlations (|ρ| > 0.3, p < 0.05) across ≥3 method families
- **PARTIAL:** 3-4 significant correlations, or confined to 1-2 families (suggests feature insufficiency)
- **FAIL:** <3 significant correlations (features non-informative; need Tier 3 or hypothesis invalid)

### Mock Data Check

To verify real data usage:
- Report feature variance (σ² > 0 indicates diversity)
- Report coverage (fraction non-NaN)
- If any feature has σ² = 0, flag as mock data artifact

---

## H-M2: Meta-Classifier Training Experiment

**Research Question:** Can a Random Forest trained on collected benchmarks predict method families achieving top-30% ranking on held-out datasets?

### Model Configuration

**Architecture:**
```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(
    n_estimators=100,      # Standard ensemble size
    max_depth=10,          # Prevent overfitting on small n
    min_samples_split=5,   # Require ≥5 samples per split
    random_state=42        # Reproducibility
)
```

**Input:** X = [sample_size, dimensionality, num_classes, class_imbalance, domain_specific_features]
**Target:** y = argmax(Linear_ranking, Poly_ranking, RNN_ranking, Aug_ranking) for each benchmark

### Cross-Validation Protocol

**Leave-5-out CV:**
- If n=50 benchmarks → 10 folds (each fold: train on 45, test on 5)
- If n=29 benchmarks (actual) → 6 folds (train on 24, test on 5)

**Stratification:** Attempt to balance domains across folds (each fold has vision/NLP/tabular/time-series representation) if sufficient samples per domain.

**Training:**
```python
for fold_idx, (train_idx, test_idx) in enumerate(cv_splits):
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Evaluate: does predicted family achieve top-30% on test benchmarks?
    for i, pred_family in enumerate(y_pred):
        actual_ranking = test_rankings[i, pred_family]  # Get ranking of predicted family
        if actual_ranking <= 30:  # Top 30% threshold
            successes += 1
```

### Evaluation Metrics

**Primary Metric: Top-30% Success Rate**
- For each held-out benchmark, check if predicted family's ranking ≤ 30th percentile
- Aggregate across all folds: `success_rate = successes / total_test_samples`

**Secondary Metrics:**
- **Confusion Matrix:** Actual family (ground truth) vs. Predicted family
- **Per-Domain Accuracy:** Success rate broken down by vision/NLP/tabular/time-series
- **Feature Importance:** SHAP values to identify which features drive predictions

### Baseline Comparisons

Train three baseline models:

**1. Random Baseline:**
```python
y_pred_random = np.random.choice(['Linear', 'Poly', 'RNN', 'Aug'], size=len(y_test))
# Expected success rate: 30% (by definition of top-30%)
```

**2. Majority Class Baseline:**
```python
most_frequent_family = Counter(y_train).most_common(1)[0][0]
y_pred_majority = [most_frequent_family] * len(y_test)
# Expected success rate: 30-40% (if one family wins ~40% of benchmarks)
```

**3. Domain Folklore Baseline:**
```python
# Map domain → family: vision→RNN, time-series→RNN, tabular→Linear
y_pred_folklore = [domain_to_family[benchmark_domain] for benchmark in test_set]
# Expected success rate: 40-50% (per Phase 2A estimates)
```

### Success Criteria

- **PASS:** ≥35% success rate, Chi-square test p < 0.05 vs. random baseline
- **PARTIAL:** 30-35% success rate (marginally better than random), investigate feature sufficiency
- **FAIL:** <30% success rate or worse than majority baseline (no learning signal)

### Hyperparameter Sensitivity (If Time Permits)

Test alternative configurations:
- `max_depth` ∈ {5, 10, 15, 20} (underfitting vs. overfitting trade-off)
- `n_estimators` ∈ {50, 100, 200} (ensemble size)
- `min_samples_split` ∈ {2, 5, 10} (regularization strength)

Report best configuration and sensitivity analysis in appendix.

---

## Experimental Workflow Summary

**Stage 1 (h-e1):** Collect benchmarks → Visualize diversity → Compute coverage metrics → Check Tier 1 completeness

**Stage 2 (h-m1):** Filter to complete feature-ranking pairs → Compute 28 Spearman correlations → Visualize heatmap and scatter plots → Report significant correlations

**Stage 3 (h-m2):** Prepare X (features) and y (best family) → Leave-5-out CV → Train Random Forest → Evaluate top-30% success rate → Compare to baselines → Visualize confusion matrix and feature importance

**Dependency:** h-m1 requires h-e1 to succeed (need data). h-m2 requires h-m1 to partially succeed (need at least some informative features). If h-e1 fails (< 30 benchmarks), we stop. If h-m1 fails (zero correlations), we document why (insufficient features vs. no relationships) before attempting h-m2.

---

**Figures for Experiments:**
- Figure 3: Feature completeness heatmap (benchmarks × features, color-coded by NaN/real)
- Figure 5: Correlation heatmap (features × method families, ρ values with significance markers)
- Figure 6: Scatter plots for top correlations
- Figure 7: Significance p-values (bar chart for 28 tests)
- Figure 8: Confusion matrix (h-m2 predicted vs. actual family)
- Figure 9: Per-domain accuracy (h-m2 success rate by domain)
- Figure 10: Feature importance (SHAP values for Random Forest)
