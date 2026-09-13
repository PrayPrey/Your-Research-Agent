# Methodology

We decompose the meta-method selection hypothesis into three testable sub-hypotheses, each addressing one component of the causal mechanism. This staged design allows us to isolate failure modes: if data collection succeeds but correlation fails, the issue is feature-method relationships (not data availability); if correlation succeeds but training fails, the issue is sample size (not feature informativeness).

## Hypothesis Decomposition Strategy

The core hypothesis claims that a meta-classifier trained on 50-60 benchmarks using fast-to-compute features will predict method families achieving top-30% ranking with >50% success rate. This statement embeds four assumptions:

- **A1 (Data Availability):** Published benchmarks aggregate ≥50 training examples
- **A2 (Feature Sufficiency):** Fast features (<1 min computation) capture dataset characteristics that differentiate method performance
- **A3 (Learnable Patterns):** Random Forest extracts generalizable relationships (not domain folklore)
- **A4 (Prediction Quality):** Predicted methods achieve competitive performance on held-out datasets

We test these sequentially through three sub-hypotheses:

**H-E1 (Existence):** At least 50 benchmarks with complete baseline comparisons are collectible from literature (OGB, FedML, LEAF, pFL-Bench, Champneys, Zhou suites), validating A1.

**H-M1 (Mechanism - Correlation):** Dataset characteristics (sample size, dimensionality, class imbalance, signal properties) show significant correlations (ρ > 0.3, p < 0.05) with method family rankings, validating A2 and testing the first causal link.

**H-M2 (Mechanism - Training):** Meta-classifier trained on aggregated benchmarks achieves ≥30% accuracy on held-out datasets via leave-5-out cross-validation, validating A3 and A4.

This decomposition is **falsifiable at each stage**: if h-e1 collects <30 benchmarks, A1 fails and we stop (insufficient training data). If h-m1 finds zero correlations, A2 fails (features non-informative). If h-m2 achieves <30% accuracy, A3 or A4 fails (no learning or poor generalization). The staged design prevents misattribution: we can distinguish "not enough data" from "data exists but is uninformative" from "features are informative but classifier doesn't learn."

---

## H-E1: Benchmark Data Collection

**Objective:** Verify that ≥50 benchmarks with complete method comparisons are accessible from published sources, providing sufficient training data for meta-learning.

### Data Sources

We target six benchmark suites identified in prior literature:

1. **OGB (Open Graph Benchmark)** [8]: 15 graph datasets (ogbn-arxiv, ogbn-products, ogbn-papers100M, etc.) with documented baseline results for GCN, GraphSAINT, ClusterGCN, GraphSAGE families. Accessible via Python library (`pip install ogb`).

2. **FedML** [9]: 6 federated learning datasets (CIFAR-10/100, CINIC-10, Shakespeare, StackOverflow) with FedAvg, FedProx, FedOpt baseline comparisons. Accessible via GitHub repository.

3. **LEAF (Federated Settings)** [10]: 5 datasets (FEMNIST, Sent140, Reddit, CelebA, Shakespeare) with heterogeneity statistics and baseline results. Available via GitHub.

4. **pFL-Bench** [14]: 8 personalized federated learning benchmarks. Accessible via Papers with Code or direct repository links.

5. **Champneys et al. NLSI** [2]: 5 nonlinear system identification tasks (Silverbox, Bouc-Wen, W-H saturation, etc.) with NARX, LSTM, Polynomial baseline comparisons. Results reported in paper tables.

6. **Zhou et al. Medical FL** [1]: 9 medical imaging datasets (BloodMNIST, PathMNIST, DermaMNIST, etc.) with FedAvg, SCAFFOLD, FedDyn, augmentation method results. Reported in paper.

### Collection Protocol

For each source:

1. **API/Library Access:** Load datasets via official libraries (OGB, FedML) to verify accessibility and extract metadata from loaded objects.

2. **GitHub Repository:** Clone or fetch README files documenting dataset statistics and baseline results.

3. **Paper Table Extraction:** For Champneys and Zhou, manually extract benchmark names, dataset characteristics (if reported), and method rankings from paper tables into structured CSV format.

4. **Metadata Fields:** For each benchmark, collect:
   - **Tier 1 Features (Universal, <1 sec):** sample_size (n), dimensionality (d), num_classes (classification), class_imbalance (Gini coefficient of class distribution)
   - **Tier 2 Features (Domain-specific, <1 min):** autocorrelation_lag1 (time-series), edge_density (graphs), feature_correlation_rank (tabular)
   - **Method Rankings:** Percentile ranking (0-100%) for representative methods from each family (Linear, Polynomial, RNN/LSTM, Augmentation)

### Success Criteria

- **PASS:** ≥50 benchmarks collected with ≥80% of Tier 1 features populated (sample_size, dimensionality, class_imbalance available for ≥40 benchmarks).
- **PARTIAL:** 30-49 benchmarks collected, or <80% feature completeness. Indicates data availability challenges.
- **FAIL:** <30 benchmarks collected. Insufficient training data for meta-classifier; hypothesis untestable.

### Collected Benchmark Diversity

To ensure generalization, collected benchmarks should span:
- **Domains:** Vision (image classification), NLP/Text, Tabular, Time-Series, Graph
- **Scales:** Small (n < 1K), Medium (1K ≤ n < 10K), Large (n ≥ 10K)
- **Task Types:** Classification, Regression
- **Structural Properties:** Balanced vs. imbalanced classes, low-dim vs. high-dim features

We visualize domain distribution (Figure 1) and data source breakdown (Figure 2) to document diversity and identify coverage gaps.

---

## H-M1: Feature-Method Correlation Analysis

**Objective:** Test whether dataset characteristics correlate with method family performance, validating that fast-to-compute features capture information relevant for method selection.

### Feature Tiers

We compute features in two tiers based on computational cost:

**Tier 1 (Universal, <1 sec):** Computable from basic dataset statistics without domain knowledge.
- `sample_size`: Total number of training samples
- `dimensionality`: Number of input features
- `num_classes`: Number of output classes (classification tasks)
- `class_imbalance`: Gini coefficient of class distribution (0 = balanced, 1 = single class dominates)
- `signal_noise_ratio`: Variance of features divided by variance of residuals (regression)

**Tier 2 (Domain-specific, 5-15 sec):** Requires domain-aware computation but remains fast.
- `autocorrelation_lag1`: First-order autocorrelation (time-series)
- `edge_density`: Average degree / max degree (graphs)
- `feature_correlation_rank`: Rank of feature correlation matrix (tabular)

Tier 1 features should be available for all benchmarks (universal). Tier 2 features are computed conditionally based on domain.

### Method Family Representatives

We map diverse methods to four broad families based on inductive bias:

- **Linear:** ARX, Ridge Regression, Linear SVM
- **Polynomial:** NARX-Poly, Polynomial Regression, Kernel SVM with polynomial kernel
- **RNN:** LSTM, GRU, vanilla RNN
- **Augmentation:** Data augmentation techniques (DDPM+LS, MixUp, CutMix)

For each benchmark, we extract the ranking percentile (0-100%) of the best-performing method in each family. If multiple representatives exist (e.g., LSTM and GRU), we use the maximum ranking within the family.

### Correlation Protocol

For each (feature, method_family) pair:

1. **Data Preparation:** Filter benchmarks to those with non-missing values for both feature and method ranking.
2. **Correlation Test:** Compute Spearman's rank correlation ρ (robust to outliers and nonlinear monotonic relationships).
3. **Significance Test:** Report p-value; threshold at p < 0.05 for significance.
4. **Practical Significance:** Require |ρ| > 0.3 for "meaningful" correlation (weak correlations uninformative for prediction).

We test all combinations: 7 features (5 Tier 1 + 2 domain-conditional Tier 2) × 4 method families = 28 tests. Bonferroni correction would require p < 0.05/28 ≈ 0.0018, but we report uncorrected p-values (exploratory analysis, not confirmatory hypothesis testing).

### Expected Patterns (From Literature)

Based on Zhou [1] and Champneys [2], we hypothesize:
- **sample_size ↔ Augmentation:** Negative correlation (small datasets benefit more from augmentation)
- **dimensionality ↔ Linear:** Positive correlation (high-dim favors regularized linear models)
- **autocorrelation_lag1 ↔ RNN:** Positive correlation (temporal structure favors recurrent models)
- **class_imbalance ↔ Augmentation:** Positive correlation (imbalanced datasets benefit from synthetic samples)

### Success Criteria

- **PASS:** ≥5 significant correlations (ρ > 0.3, p < 0.05) spanning at least 3 method families. Evidence that features capture method-relevant information.
- **PARTIAL:** 3-4 significant correlations, or correlations confined to single family. Suggests feature insufficiency.
- **FAIL:** <3 significant correlations. Features non-informative; either need Tier 3 (expensive probing) or dataset characteristics don't predict method performance.

We visualize results as a heatmap (Figure 5) with correlation coefficients and significance markers, and scatter plots (Figure 6) for top correlations.

---

## H-M2: Meta-Classifier Training and Evaluation

**Objective:** Test whether a Random Forest trained on collected benchmarks can predict method family rankings on held-out datasets with ≥30% top-30% success rate.

### Model Architecture

We use **Random Forest** (scikit-learn `RandomForestClassifier`) for interpretability and robustness:
- **Input:** 7-dimensional feature vector (Tier 1 + Tier 2 features, domain-conditional)
- **Output:** 4-class prediction (Linear, Polynomial, RNN, Augmentation)
- **Hyperparameters:**
  - `n_estimators=100` (ensemble size, standard default)
  - `max_depth=10` (prevent overfitting on small training set)
  - `min_samples_split=5` (require ≥5 samples to split node)

Random Forest is interpretable via SHAP feature importance, handles missing values (NaN indicators), and is robust to small sample sizes (validated on datasets with n=50-100 in prior work).

### Training Protocol

**Target Variable:** For each benchmark, the target is the best-performing method family (highest ranking percentile among the four families). This converts regression (predicting exact ranking) to 4-class classification (predicting family).

**Cross-Validation:** Leave-5-out CV with 10 folds (if 50 benchmarks collected, each fold trains on 45 and tests on 5). Stratified by domain if possible (ensure each fold has vision/NLP/tabular/time-series representation).

**Evaluation Metrics:**
- **Primary:** Top-30% success rate — percentage of held-out benchmarks where predicted family achieves ≤30th percentile ranking (top 30%)
- **Secondary:** Confusion matrix, per-domain accuracy, feature importance (SHAP)

### Baseline Comparisons

- **Random Selection:** Uniform random choice from {Linear, Polynomial, RNN, Augmentation}. Expected 30% top-30% success rate (by definition of top-30%).
- **Majority Class:** Always predict most frequent winner in training set. Expected 30-40% success rate (degeneracy check).
- **Domain Folklore:** Predict based on domain only (vision→RNN [pre-Transformer era assumption], time-series→RNN, tabular→Linear). Expected 40-50% success rate per Phase 2A estimates.

### Success Criteria

- **PASS:** ≥35% top-30% success rate, significantly better than random (Chi-square test p < 0.05).
- **PARTIAL:** 30-35% success rate, marginally better than random. Suggests weak but present signal; investigate feature sufficiency or increase training data.
- **FAIL:** <30% success rate (no better than random) or worse than majority-class baseline. Indicates no learning; either features insufficient, sample size too small, or method rankings too chaotic.

We visualize confusion matrix (Figure 8), per-domain accuracy (Figure 9), and feature importance (Figure 10) to diagnose failure modes.

---

## Mock Data Elimination Protocol

To ensure reported results use real data (not hard-coded defaults), we implement verification:

1. **Coverage Reporting:** For each feature, report fraction of benchmarks with real (non-NaN) values. If coverage is 0%, feature was not extracted.
2. **Variance Check:** For each feature, report standard deviation. Zero variance indicates all values identical (likely mock data artifact).
3. **External Review:** Phase 4 validation includes manual inspection of feature arrays to verify diversity.

This transparency allows readers to assess whether negative results stem from data quality issues versus hypothesis failure.

---

## Summary: Why This Design?

The three-stage decomposition (h-e1 → h-m1 → h-m2) isolates components of the causal chain. If stage 1 fails, we learn that benchmark data is inaccessible (infrastructure problem). If stage 1 passes but stage 2 fails, we learn that dataset characteristics don't correlate with method rankings (hypothesis problem). If stages 1-2 pass but stage 3 fails, we learn that correlations exist but aren't strong enough for prediction (sample size or feature richness problem).

This design allows us to distinguish between:
- **Data collection bottleneck** (our actual finding: h-e1 collected only 29 benchmarks with 14% feature coverage)
- **Weak feature-method relationships** (untested due to insufficient data)
- **Meta-classifier learning failure** (occurred but attributable to degenerate input, not algorithm)

The next two sections present experimental protocols in detail (Section 4) and results demonstrating the data collection bottleneck (Section 5).

---

**Figures for Methodology:**
- Figure 1: Domain distribution of collected benchmarks (bar chart: vision, tabular, time-series, graph)
- Figure 2: Data source breakdown (pie chart: OGB, GitHub, Manual CSVs)
- Figure 4: Method family taxonomy (diagram: Linear/Polynomial/RNN/Augmentation with example methods)
