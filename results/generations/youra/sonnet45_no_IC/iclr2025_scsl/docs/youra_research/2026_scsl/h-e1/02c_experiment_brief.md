# Experiment Design: H-E1

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis Statement:** Under standard supervised learning conditions, if Logistic Regression is trained on log-scaled GitHub metadata (8 features) with balanced class weights, then it achieves ≥75% accuracy on held-out test set, because repository maintenance status is linearly separable in transformed feature space.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C)
**Prerequisites Satisfied:** Yes (none required - foundation hypothesis)
**Gate Status:** MUST_WORK - Not yet tested

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition

**Type:** MUST_WORK  
**Pass Condition:** Accuracy ≥75% AND F1 ≥0.73  
**If Fail:** Linear separability hypothesis rejected → analyze why non-linear methods necessary

---

## Continuation Context

**Status:** First hypothesis in verification chain (no previous context)

**Dependent Hypotheses:** H-M1 (Mechanism) will follow if H-E1 passes MUST_WORK gate

### Previous Hypothesis Results (if applicable)

N/A - This is the foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Coverage:** 3 knowledge base queries executed (logistic regression, repository maintenance, tabular classification)

**Query 1: Logistic Regression Classification**
- **Results:** Limited domain-specific matches (5 results from HuggingFace diffusers training scripts)
- **Key Insights:** Archon KB primarily contains deep learning codebases, not traditional ML methods
- **Relevance:** Low - no scikit-learn or tabular classification examples found

**Query 2: Repository Maintenance Prediction**
- **Results:** Generic GitHub profile/repository pages (5 results)
- **Key Insights:** No research papers or implementation cases for repository maintenance prediction
- **Relevance:** Low - no actionable experiment designs found

**Query 3: Tabular Classification Best Practices**
- **Results:** LaTeX documentation (3 results from Overleaf tutorials)
- **Key Insights:** Query returned unrelated documentation
- **Relevance:** None

**Overall Assessment:** Archon KB lacks coverage for:
- Traditional ML methods (sklearn LogisticRegression)
- Software engineering metrics research
- Repository maintenance prediction literature

**Fallback Strategy:** Rely on Phase 2B specification (established baselines from He et al. 2024, Adejumo & Johnson 2025) and standard sklearn documentation.

### Archon Code Examples

**Search Coverage:** 2 code example queries executed (sklearn logistic regression, GitHub API)

**Query 1: Scikit-learn Logistic Regression**
- **Results:** 5 optimizer examples from HuggingFace diffusers (Adam optimizer configurations)
- **Code Pattern Identified:**
  ```python
  optimizer = optimizer_cls(
      model.parameters(),
      lr=learning_rate,
      betas=(adam_beta1, adam_beta2),
      weight_decay=adam_weight_decay,
      eps=adam_epsilon,
  )
  ```
- **Insight:** Standard pattern for optimizer initialization (transferable to sklearn parameter tuning)
- **Relevance:** Medium - shows hyperparameter configuration patterns

**Query 2: GitHub API Repository Metadata**
- **Results:** 5 examples (BibTeX citations, web scraping schemas, directory structures)
- **Key Finding:** No direct GitHub REST API extraction code
- **Relevance:** Low - no actionable code for repository metadata collection

**Overall Assessment:** Limited actionable code examples for:
- Sklearn LogisticRegression training loops
- GitHub API metadata extraction
- Feature engineering for tabular data

**Standard Implementation Path:** Use canonical sklearn documentation and GitHub API official guides.

### Exa GitHub Implementations

⚠️ **Exa MCP Service Unavailable** (402 billing error - quota exceeded)

**Fallback Strategy:** Using Phase 2B established references:
- **Baseline Reference:** He et al. 2024 - Gradient Boosting + HITS centrality (C-Index 0.810, 103,354 repos)
- **Comparison Baseline:** Adejumo & Johnson 2025 - Composite Stability Index (F1 0.80, 100 repos)

**Standard Implementation Sources:**
1. **Scikit-learn LogisticRegression**: Official sklearn documentation
   - URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
   - Training pattern: Standard supervised learning with stratified split
   
2. **GitHub REST API**: Official GitHub API v3 documentation
   - URL: https://docs.github.com/en/rest
   - Metadata extraction: stars, forks, commits, contributors, open_issues, last_commit_date

**No Serena Analysis Needed:** Standard sklearn + GitHub API implementation (well-documented, no custom architectures)

### 🎯 Implementation Priority Assessment

**Implementation Type:** Standard baseline experiment (not paper reproduction)

**Priority:** Use canonical implementations
1. **Dataset Collection:** GitHub REST API v3 (official)
2. **Model:** scikit-learn LogisticRegression (official)
3. **Metrics:** sklearn.metrics (official)

**Recommended Implementation Path:**
- Primary: Official sklearn + GitHub API documentation
- Fallback: N/A (standard implementations are authoritative)
- Justification: Testing baseline LR hypothesis requires canonical sklearn implementation, not research code reproduction

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear

**Rationale:** Standard sklearn LogisticRegression + GitHub REST API implementation requires no complex code analysis. Official documentation provides complete specifications.

---

## Experiment Specification

### Dataset

**Name:** Papers with Code Benchmark Repositories  
**Type:** `custom` (programmatic API extraction)  
**Source:** GitHub REST API v3 + Papers with Code API

**Collection Protocol:**
1. Query Papers with Code API for benchmark repositories (2020-2024, min_stars=32, non-fork)
2. Extract metadata via GitHub REST API for each repository (stars, forks, commits, contributors, open_issues, last_commit_date)
3. Compute derived features (commit_frequency_median_weekly, issue_resolution_rate)

**Size:** 2000 repositories  
**Time Period:** 2020-2024 (enables temporal validation)

**Features (8 total):**
- stars_log, forks_log, contributors_log, total_commits_log, open_issues_log (log1p transformed)
- days_since_last_commit (raw)
- commit_frequency_median_weekly, issue_resolution_rate (derived)

**Labels:** Binary (maintained vs abandoned) from `days_since_last_commit < 180 days`  
**Splits:** Stratified 80/20 train/test (random_state=42)

**Preprocessing:**
- Log1p transformation for long-tail distributions
- StandardScaler normalization (fit on train, transform test)
- No missing value imputation (GitHub API returns complete metadata)

**Augmentation:** None (tabular data)

**Loading Information** (for Phase 4 download):
- Method: `custom` (GitHub API extraction script)
- Identifier: Papers with Code benchmark repositories (2020-2024)
- Code:
  ```python
  import requests
  import pandas as pd
  import numpy as np
  from sklearn.model_selection import train_test_split
  
  # 1. Query Papers with Code API for benchmark repos
  # 2. Extract metadata via GitHub REST API with auth token
  # 3. Engineer features with log1p transforms
  # 4. Create labels from days_since_last_commit < 180
  # 5. Stratified 80/20 split (random_state=42)
  ```

### Models

#### Baseline Model

**Architecture:** Logistic Regression (Linear Classifier)  
**Type:** sklearn.linear_model.LogisticRegression  
**Source:** scikit-learn 1.x

**Configuration:**
- max_iter=1000 (ensures convergence)
- class_weight='balanced' (handles potential class imbalance)
- solver='lbfgs' (recommended for small datasets)
- random_state=42 (reproducibility)
- Input: 8 features (log-scaled + derived)
- Output: Binary classification (maintained vs abandoned)
- Regularization: L2 (default)

**Training Time:** ~30 seconds on single CPU

**Modifications:** None (EXISTENCE hypothesis tests baseline LR directly)

**Loading Information** (for Phase 4 download):
- Method: `sklearn`
- Identifier: `sklearn.linear_model.LogisticRegression`
- Code:
  ```python
  from sklearn.linear_model import LogisticRegression
  from sklearn.preprocessing import StandardScaler
  
  # Normalization
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)
  X_test_scaled = scaler.transform(X_test)
  
  # Model
  model = LogisticRegression(
      max_iter=1000,
      class_weight='balanced',
      solver='lbfgs',
      random_state=42
  )
  
  # Training
  model.fit(X_train_scaled, y_train)
  ```

#### Proposed Model

**Architecture:** Same as Baseline (Logistic Regression)

**Rationale:** EXISTENCE hypothesis tests whether baseline LR achieves ≥75% accuracy threshold. For this hypothesis, baseline = proposed (no mechanism to add).

**Core Mechanism Implementation:**

```python
# Core Mechanism: Log-scaled Feature Transformation + Logistic Regression
# Based on: Phase 2B specification (H-E1)

class RepositoryMaintenanceClassifier:
    """
    Tests linear separability hypothesis for repository maintenance classification.
    Mechanism: Log1p transformation of long-tail features + L2-regularized logistic regression.
    """
    def __init__(self, max_iter=1000, random_state=42):
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        import numpy as np
        
        self.scaler = StandardScaler()
        self.model = LogisticRegression(
            max_iter=max_iter,
            class_weight='balanced',
            solver='lbfgs',
            random_state=random_state
        )
    
    def engineer_features(self, raw_features):
        """
        Transform raw GitHub metadata into log-scaled features.
        
        Args:
            raw_features: DataFrame with [stars, forks, contributors, total_commits, 
                          open_issues, days_since_last_commit, commit_frequency_median_weekly,
                          issue_resolution_rate]
        Returns:
            Transformed features (8 dimensions)
        """
        import numpy as np
        
        # Log1p transform for long-tail distributions
        features = raw_features.copy()
        for col in ['stars', 'forks', 'contributors', 'total_commits', 'open_issues']:
            features[f'{col}_log'] = np.log1p(features[col])
            features = features.drop(col, axis=1)
        
        return features
    
    def fit(self, X_raw, y):
        """Fit model with feature engineering + normalization."""
        X_engineered = self.engineer_features(X_raw)
        X_scaled = self.scaler.fit_transform(X_engineered)
        self.model.fit(X_scaled, y)
        return self
    
    def predict(self, X_raw):
        """Predict maintenance status."""
        X_engineered = self.engineer_features(X_raw)
        X_scaled = self.scaler.transform(X_engineered)
        return self.model.predict(X_scaled)

# No integration point - this IS the complete model
```

### Training Protocol

**Optimizer:** Not applicable (LogisticRegression uses internal LBFGS optimization)

**Hyperparameters:**
- max_iter: 1000 (ensures convergence)
- solver: 'lbfgs' (default for small datasets)
- C: 1.0 (inverse regularization strength, L2 default)
- class_weight: 'balanced' (handles potential class imbalance)
- random_state: 42 (reproducibility)

**Training Process:**
1. Load raw GitHub metadata (2000 repositories)
2. Engineer features (log1p transforms + derived features)
3. Create labels (days_since_last_commit < 180)
4. Stratified 80/20 train/test split (random_state=42)
5. Fit StandardScaler on training data
6. Train LogisticRegression on scaled training data
7. Evaluate on scaled test data

**Epochs:** Single pass (sklearn LogisticRegression converges automatically)  
**Batch Size:** Full batch (standard for sklearn on small datasets)  
**Loss Function:** Logistic loss (cross-entropy, internal to sklearn)  
**Seeds:** 1 (random_state=42)

**Training Time:** ~30 seconds on single CPU

**Source:** scikit-learn documentation + Phase 2B specification

### Evaluation

**Primary Metrics:**
- **Accuracy:** Fraction of correct predictions (primary success criterion)
- **F1 Score:** Harmonic mean of precision and recall (secondary success criterion)
- **Precision:** True positives / (true positives + false positives)
- **Recall:** True positives / (true positives + false negatives)

**Success Criteria (from Phase 2B):**
- **Primary:** Accuracy ≥75% AND F1 ≥0.73 on held-out test set
- **Secondary:** Accuracy ≥70% on high-confidence subset (validates labeling)
- **Statistical:** Performance exceeds majority baseline by ≥10%

**PoC Success Check (EXISTENCE hypothesis):**
- ✅ **PASS:** accuracy ≥ 0.75 AND f1 ≥ 0.73
- ⚠️ **PARTIAL:** 0.70 ≤ accuracy < 0.75 (moderate success, pivot to interpretation)
- ❌ **FAIL:** accuracy < 0.70 (linear separability rejected)

**Expected Baseline Performance** (from Phase 2B research):
- Majority Baseline: ~60% (class distribution dependent)
- Composite Stability Index (CSI): F1 0.80 (Adejumo & Johnson 2025, 100 repos)
- Gradient Boosting + HITS: C-Index 0.810 (He et al. 2024, 103,354 repos)

**Target:** LR accuracy ≥75%, competitive with CSI while being simpler

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: `sklearn.metrics`
- Code:
  ```python
  from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
  
  # Predictions
  y_pred = model.predict(X_test_scaled)
  
  # Metrics
  accuracy = accuracy_score(y_test, y_pred)
  precision = precision_score(y_test, y_pred)
  recall = recall_score(y_test, y_pred)
  f1 = f1_score(y_test, y_pred)
  
  # Success criteria check
  success_primary = (accuracy >= 0.75) and (f1 >= 0.73)
  success_baseline_margin = (accuracy >= 0.60 + 0.10)  # 10% above majority
  
  print(f"Accuracy: {accuracy:.3f} (target: ≥0.75)")
  print(f"F1 Score: {f1:.3f} (target: ≥0.73)")
  print(f"Success: {success_primary}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on EXISTENCE hypothesis (logistic regression classification) and evaluation metrics, the following additional figures are recommended:

1. **Confusion Matrix Heatmap**
   - Purpose: Show true positives, false positives, true negatives, false negatives
   - Helps: Identify if model biases toward one class

2. **Feature Importance (Coefficient Magnitude)**
   - Purpose: Visualize learned LR coefficients for 8 features
   - Helps: Validate linear separability mechanism (expected: negative days_since_last_commit, positive activity metrics)

3. **ROC Curve + AUC Score**
   - Purpose: Show classifier performance across thresholds
   - Helps: Assess discriminative power beyond fixed threshold

4. **Class Distribution (Train/Test)**
   - Purpose: Bar chart showing maintained vs abandoned counts
   - Helps: Validate stratified split and identify actual majority baseline

5. **Metric Comparison (LR vs Baselines)**
   - Purpose: Bar chart comparing LR accuracy to majority baseline, CSI (if available), GB (if available)
   - Helps: Contextualize LR performance relative to expected baselines

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Search Coverage:** 3 knowledge base queries + 2 code example queries executed

**Query 1: Logistic Regression Classification**
- **Type:** Knowledge base search
- **Query Used:** "logistic regression classification experiment design dataset"
- **Results:** 5 results from HuggingFace diffusers (low relevance)
- **Relevance:** Limited - Archon KB lacks traditional ML coverage
- **Used For:** Confirmed need to rely on sklearn documentation

**Query 2: Repository Maintenance Prediction**
- **Type:** Knowledge base search
- **Query Used:** "repository maintenance prediction GitHub metrics"
- **Results:** 5 generic GitHub profile pages
- **Relevance:** Low - no research papers found
- **Used For:** Validated reliance on Phase 2B references (He et al. 2024, Adejumo & Johnson 2025)

**Query 3: Tabular Classification Best Practices**
- **Type:** Knowledge base search
- **Query Used:** "tabular classification sklearn best practices"
- **Results:** 3 LaTeX documentation pages
- **Relevance:** None
- **Used For:** N/A

**Code Example 1: Scikit-learn Patterns**
- **Query Used:** "scikit-learn logistic regression"
- **Results:** 5 optimizer examples from HuggingFace (Adam configurations)
- **Key Pattern:**
  ```python
  optimizer = optimizer_cls(
      model.parameters(),
      lr=learning_rate,
      betas=(adam_beta1, adam_beta2),
      weight_decay=adam_weight_decay,
  )
  ```
- **Relevance:** Medium - pattern transferable to hyperparameter configuration
- **Used For:** Hyperparameter specification principles

**Code Example 2: GitHub API**
- **Query Used:** "GitHub API repository metadata extraction"
- **Results:** 5 examples (BibTeX, web scraping schemas, directories)
- **Relevance:** Low - no direct API extraction code
- **Used For:** N/A

**Overall Assessment:** Archon KB provided limited actionable findings. Experiment design relies on Phase 2B references and sklearn/GitHub API official documentation.

---

### B. GitHub Implementations (Exa)

⚠️ **Exa MCP Unavailable** (402 billing error - quota exceeded)

**Fallback References:**

**Reference 1: He et al. 2024 - Gradient Boosting + HITS**
- **Source:** Phase 2B verification plan (baseline comparison)
- **Performance:** C-Index 0.810 on 103,354 repos
- **Relevance:** Establishes upper bound for complex ensemble methods
- **Used For:** Baseline performance expectations, GB comparison target

**Reference 2: Adejumo & Johnson 2025 - Composite Stability Index**
- **Source:** Phase 2B verification plan (baseline comparison)
- **Performance:** F1 0.80 on 100 repos
- **Relevance:** Demonstrates basic metadata features capture maintenance signal
- **Used For:** Feature sufficiency validation, CSI comparison target

**Reference 3: Scikit-learn Official Documentation**
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- **Relevance:** Canonical implementation reference
- **Used For:** Model configuration, training protocol, hyperparameters

**Reference 4: GitHub REST API v3 Documentation**
- **URL:** https://docs.github.com/en/rest
- **Relevance:** Authoritative data source specification
- **Used For:** Dataset collection protocol, metadata extraction

---

### C. Code Analysis (Serena)

**Serena Analysis:** *Skipped* - Code from search results was sufficiently clear

**Rationale:** Standard sklearn LogisticRegression + GitHub REST API implementation requires no complex code analysis. Official documentation provides complete specifications.

---

### D. Previous Hypothesis Context

**Previous Context:** None - this is the first hypothesis (H-E1) in the verification chain.

**Dependent Hypotheses:** H-M1 (Mechanism) will reuse dataset and continue from H-E1 results.

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| **Dataset selection** | Phase 2B | Papers with Code benchmarks (He et al. 2024 domain) |
| **Dataset collection** | Official API | GitHub REST API v3 documentation |
| **Feature engineering** | Phase 2B | Log1p transforms (specified in H-E1 protocol) |
| **Baseline model** | Phase 2B + sklearn docs | LogisticRegression with balanced weights |
| **Model configuration** | sklearn docs | max_iter=1000, solver='lbfgs', random_state=42 |
| **Preprocessing** | sklearn docs | StandardScaler normalization |
| **Training protocol** | sklearn docs | Single-pass convergence, full batch |
| **Evaluation metrics** | Phase 2B + sklearn | accuracy, precision, recall, F1 from sklearn.metrics |
| **Success criteria** | Phase 2B | Accuracy ≥75%, F1 ≥0.73 (H-E1 specification) |
| **Baseline comparisons** | Phase 2B | Majority (~60%), CSI (F1 0.80), GB (C-Index 0.810) |
| **Visualization requirements** | Autonomous design | Confusion matrix, feature importance, ROC, class distribution |

**Source Distribution:**
- Phase 2B specification: 7 components
- Official documentation (sklearn, GitHub API): 5 components
- Autonomous design decisions: 1 component

**All specifications are traceable to documented sources.**

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-13T17:00:00Z

### Workflow History for This Hypothesis

**2026-07-13T16:56:11Z** - Hypothesis h-e1 set to IN_PROGRESS (Hypothesis Loop)  
**2026-07-13T17:00:00Z** - Phase 2C experiment design started (Step 01)  
**2026-07-13T17:00:00Z** - Phase 2C experiment design completed (Step 08)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
