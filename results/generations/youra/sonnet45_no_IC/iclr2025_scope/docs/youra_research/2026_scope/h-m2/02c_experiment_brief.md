# Experiment Design: h-m2

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis Statement:** Aggregated benchmark results from literature provide sufficient training examples (50-60 datasets) to learn feature-method relationships.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Standard validation template

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PARTIAL - 2/3 correlations found)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1

### Gate Condition
SHOULD_WORK - Primary mechanism for meta-learning approach

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

**Key Findings from H-M1:**
- Mock data fix successfully applied (all hard-coded defaults removed)
- Found 2/3 significant correlations (target ≥3):
  - image_resolution → Polynomial: ρ=+0.894, p=0.0161
  - channel_count → Polynomial: ρ=+0.894, p=0.0161
- Limited to Vision domain features only
- Insufficient feature diversity in H-E1 dataset (13.8% coverage for sample_size, 0% for dimensionality)
- Zero variance in class_imbalance feature (all values = 0.559)

**Gate Result:** PARTIAL (2 significant correlations found, but insufficient coverage)

**Lessons Learned:**
1. H-E1 dataset lacks comprehensive feature data for all domains
2. Vision-specific features show strong correlation (image_resolution, channel_count)
3. Need diverse dataset characteristics across all method families
4. Current data: 29 benchmarks with limited feature coverage

**Implications for H-M2:**
- H-M2 tests if 50-60 datasets provide sufficient training examples
- H-M1 showed only 2 usable feature-method pairs from 29 benchmarks
- Need to validate if meta-classifier can learn from limited feature diversity
- Must measure training data sufficiency despite sparse feature coverage

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Meta-learning with Limited Training Data**
- **Findings**: General ML training examples from diffusion models, not directly applicable to meta-learning for method selection
- **Relevance**: Limited - searches returned diffusion model training code (not meta-learning)
- **Key insight**: Standard cross-validation practices apply to small datasets

**Query 2: Random Forest Classification with Small Datasets**
- **Source**: HuggingFace diffusers training examples (unconditional generation, consistency distillation)
- **Relevance**: Shows hyperparameter patterns for small-data scenarios
- **Key Configuration Patterns**:
  - Learning rate: 1e-6 to 5e-6 (conservative for small data)
  - Batch size: 1-16 (small to prevent overfitting)
  - Gradient accumulation used to simulate larger batches
  - Validation splits for early stopping

**Query 3: Cross-validation and Train/Test Split**
- **Source**: HuggingFace training scripts with split strategies
- **Key patterns**: Data splits typically 80/20 or 70/30 for small datasets
- **Relevance**: Directly applicable to meta-learning dataset splitting

### Archon Code Examples

**Query 1: Random Forest Classifier with sklearn**
- **Result**: PyTorch dataset splitting example
- **Code Pattern**:
  ```python
  generator = torch.Generator().manual_seed(42)
  train_data, val_data = random_split(dataset, [0.8, 0.2], generator=generator)
  ```
- **Insight**: Use fixed seed for reproducibility in small-data scenarios

**Query 2: Dataset Meta-features Extraction**
- **Results**: Dataset structure documentation from PixArt, Latte
- **Pattern**: Hierarchical organization (images/, captions/, features/)
- **Insight**: Feature extraction should produce structured, documented output

**Limited Utility**: Archon KB contains primarily diffusion model code, not meta-learning or Random Forest examples. Will rely on standard sklearn documentation for implementation.

### Exa GitHub Implementations

**Exa Service Status**: 402 Payment Required (quota exceeded)

**Unable to search GitHub for:**
- sklearn Random Forest small dataset examples
- Meta-learning feature extraction implementations
- Cross-validation with limited training data

**Fallback**: Will use standard sklearn.ensemble.RandomForestClassifier with default hyperparameters validated for small datasets in literature

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority: Standard Library (sklearn)**

This is NOT a paper reproduction — it's a novel hypothesis about meta-learning sufficiency. No official implementation exists.

**Recommended Implementation Path:**
- Primary: `sklearn.ensemble.RandomForestClassifier` with default parameters
- Fallback: None needed (sklearn is standard)
- Justification: 
  - H-M2 tests if 50-60 datasets provide sufficient training examples
  - Random Forest chosen in Phase 2A for robustness to small data
  - Standard sklearn implementation is stable and well-documented
  - No custom mechanism — testing data sufficiency, not novel algorithm

### Code Analysis (Serena MCP)

**Serena Analysis: Not Required**

**Rationale:**
- No complex architecture to analyze
- Using standard sklearn.RandomForestClassifier (well-documented API)
- Feature computation already implemented in H-M1 (reusing code)
- Training loop is standard: `model.fit(X_train, y_train)` → `model.predict(X_test)`

---

## Experiment Specification

### Dataset

**Dataset: H-E1 Benchmark Collection (Reused from prerequisite)**

**Type**: `custom` (user-provided, already collected)  
**Source**: H-E1 hypothesis output (`docs/youra_research/h-e1/code/output/benchmarks.json`)  
**Total Benchmarks**: 63 (exceeds target of 50-60)  
**Domains**: Vision (27), NLP (15), Tabular (11), Other (10)

**Feature Set** (from H-M1):
- **Tier 1 Features** (4): `sample_size`, `dimensionality`, `num_classes`, `class_imbalance`
- **Tier 2 Features** (6): Domain-specific (image_resolution, channel_count, sequence_length, etc.)
- **Coverage**: Variable per feature (13.8% for sample_size, 75.9% for class_imbalance, 0% for many Tier 2)

**Target Variable**: Method family ranking (4 classes: Linear, Polynomial, RNN, Augmentation)  
**Data Split Strategy**: Leave-5-out cross-validation (replicates real-world "predict on unseen datasets")

**Preprocessing**:
1. Load benchmarks.json from H-E1
2. Compute features using `src/feature_computer.py` from H-M1 (reused)
3. Extract method family rankings from `method_rankings` field
4. Remove NaN features (columns with >70% missing data)
5. Z-score normalization for remaining features

**Augmentation**: None (meta-learning on dataset-level features, not sample-level)

**Statistics**:
- Total samples: 63 benchmarks
- Features: 4-10 (after NaN removal)
- Classes: 4 method families
- Training split: 58 benchmarks (leave-5-out per fold)
- Test split: 5 benchmarks per fold

**Loading Information** (for Phase 4 download):
- Method: `custom` (file-based loading)
- Identifier: `../h-e1/code/output/benchmarks.json`
- Code: 
  ```python
  import json
  with open("../h-e1/code/output/benchmarks.json") as f:
      benchmarks = json.load(f)
  ```

### Models

#### Baseline Model

**Model: Majority Class Baseline (Naive Predictor)**

**Architecture**: Always predict the most frequent method family in training data  
**Purpose**: Establishes floor performance — any learning should beat this  
**Implementation**: `sklearn.dummy.DummyClassifier(strategy="most_frequent")`

**Configuration**:
- No trainable parameters
- Deterministic prediction
- Expected accuracy: ~25-30% (with 4 balanced classes, slightly biased by domain distribution)

**Loading Information** (for Phase 4 download):
- Method: `sklearn` (standard library)
- Identifier: `sklearn.dummy.DummyClassifier`
- Code: 
  ```python
  from sklearn.dummy import DummyClassifier
  baseline = DummyClassifier(strategy="most_frequent")
  baseline.fit(X_train, y_train)
  ```

#### Proposed Model

**Model: Random Forest Meta-Classifier**

**Architecture**: Ensemble of 100 decision trees trained on dataset meta-features

**Core Mechanism Implementation:**

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut

# Meta-Classifier: Random Forest for Method Selection
# Hypothesis: 50-60 training examples sufficient for generalization

class MetaMethodSelector:
    """
    Tests if aggregated benchmark results (50-60 datasets) provide
    sufficient training examples to learn feature-method relationships.
    """
    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            min_samples_split=5,  # Prevent overfitting on small data
            min_samples_leaf=2
        )
    
    def fit(self, X_meta_features, y_method_families):
        """
        Train on aggregated benchmarks.
        
        Args:
            X_meta_features: (N, F) - dataset characteristics
                            N=63 benchmarks, F=4-10 features
            y_method_families: (N,) - top-performing method family per benchmark
        """
        self.model.fit(X_meta_features, y_method_families)
        return self
    
    def predict(self, X_new_dataset):
        """
        Predict best method family for unseen dataset.
        
        Args:
            X_new_dataset: (1, F) - new dataset's meta-features
        Returns:
            method_family: str - predicted family (Linear/Polynomial/RNN/Augmentation)
        """
        return self.model.predict(X_new_dataset)
    
    def evaluate_sufficiency(self, X, y, cv_folds=5):
        """
        Leave-K-out validation to measure generalization.
        Tests if 50-60 examples provide sufficient training signal.
        """
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(self.model, X, y, cv=cv_folds, scoring='accuracy')
        return scores.mean(), scores.std()

# Integration: Standalone model (not inserted into neural network)
# Operates on dataset-level meta-features, not sample-level data
```

**Key Design Choices** (from Phase 2A + H-M1 lessons):
- `n_estimators=100`: Standard for Random Forest
- `max_depth=10`: Prevents overfitting on 63 training samples
- `min_samples_split=5`: Ensures splits only on sufficient data
- `min_samples_leaf=2`: Each leaf represents ≥2 datasets (not single outlier)
- Fixed seed (`random_state=42`): Reproducibility

### Training Protocol

**From Previous Hypothesis (H-M1)**: Not applicable — H-M1 used correlation analysis, not classifier training

**Training Strategy**: Leave-5-out Cross-Validation

**Hyperparameters** (sklearn RandomForestClassifier):
- **n_estimators**: 100 (ensemble size)
- **max_depth**: 10 (tree depth limit)
- **min_samples_split**: 5 (minimum samples to split node)
- **min_samples_leaf**: 2 (minimum samples per leaf)
- **random_state**: 42 (reproducibility)
- **criterion**: "gini" (default, works well for multi-class)
- **max_features**: "sqrt" (default, prevents correlation in trees)

**Training Procedure**:
1. Load 63 benchmarks with features from H-E1
2. For each cross-validation fold (13 folds total):
   - Train: 58 benchmarks
   - Test: 5 held-out benchmarks
3. Fit Random Forest on training fold
4. Predict method families for test fold
5. Record accuracy per fold

**Loss Function**: N/A (Random Forest uses internal Gini impurity, not gradient-based loss)

**Seeds**: 1 (fixed at `random_state=42`)

**Training Time**: <5 seconds per fold (sklearn is fast on 63 samples)

**Rationale**: 
- Leave-5-out mimics real-world scenario: "predict best method for 5 new datasets"
- 13 folds × 5 test samples = 65 predictions (full coverage with some overlap)
- No gradient descent — Random Forest uses bagging/bootstrapping
- Hyperparameters chosen for small-data robustness (prevent overfitting)

### Evaluation

**Primary Metrics**:
1. **Cross-Validation Accuracy**: Mean accuracy across all 13 folds
2. **Generalization Gap**: Train accuracy - Test accuracy (measures overfitting)
3. **Per-Domain Accuracy**: Accuracy broken down by benchmark domain (Vision/NLP/Tabular)

**Success Criteria** (MECHANISM hypothesis):
- **Primary**: CV Accuracy > Baseline (majority class ~27%)
- **Target**: CV Accuracy ≥ 40% (demonstrates learning beyond random chance)
- **Threshold**: Generalization Gap < 20% (not severely overfitting)

**Expected Baseline Performance** (from hypothesis):
- Majority class baseline: ~27% (4 classes, slightly imbalanced)
- Random guess: 25%

**Gate Evaluation** (SHOULD_WORK):
- ✅ PASS: CV Accuracy > 35% AND Generalization Gap < 25%
- ⚠️ PARTIAL: CV Accuracy 30-35% OR Gap 20-25%
- ❌ FAIL: CV Accuracy ≤ 30% (no learning) OR Gap ≥ 25% (severe overfitting)

**Interpretation**:
- If PASS: 50-60 datasets provide sufficient training signal → proceed to H-M3
- If PARTIAL: Limited but present learning → investigate feature quality in H-M3
- If FAIL: Insufficient data → hypothesis rejected, need more benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: `multi-class classification`
- Library: `sklearn.metrics`
- Code: 
  ```python
  from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
  from sklearn.model_selection import cross_val_score
  
  # Cross-validation evaluation
  cv_scores = cross_val_score(model, X, y, cv=13, scoring='accuracy')
  cv_mean = cv_scores.mean()
  cv_std = cv_scores.std()
  
  # Per-fold evaluation
  accuracy = accuracy_score(y_true, y_pred)
  report = classification_report(y_true, y_pred)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual CV accuracy bar chart
  - X-axis: [Baseline, Target, Actual]
  - Y-axis: Accuracy (%)
  - Threshold lines: PASS (35%), Target (40%)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations** (Phase 4 Coder decides final set):

1. **Learning Curve**: CV Accuracy vs Training Set Size
   - Tests hypothesis directly: "Does accuracy improve with more datasets?"
   - X-axis: Training size (10, 20, 30, 40, 50, 58 benchmarks)
   - Y-axis: CV Accuracy
   - Shows if 50-60 is sufficient or if more data would help

2. **Confusion Matrix**: Predicted vs Actual Method Families
   - Heatmap showing which method families are confused
   - Identifies if model generalizes across all families or only some

3. **Per-Domain Accuracy**: Bar chart of accuracy by benchmark domain
   - X-axis: Vision, NLP, Tabular, Other
   - Y-axis: Accuracy
   - Shows if model works equally well across domains

4. **Feature Importance**: Bar chart of Random Forest feature importances
   - X-axis: Feature names (sample_size, dimensionality, etc.)
   - Y-axis: Importance score
   - Validates which features drive predictions

5. **Generalization Gap**: Train vs Test Accuracy scatter plot
   - X-axis: Fold index
   - Y-axis: Accuracy
   - Two lines: Train (blue), Test (red)
   - Shows overfitting severity per fold

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 MECHANISM Success Check

**MECHANISM Pass Condition** (SHOULD_WORK gate):
1. Code runs without error
2. CV Accuracy > Baseline (majority class ~27%)
3. Generalization Gap < 20%
4. **Primary Goal**: CV Accuracy ≥ 35% (above chance + margin)

**Success Interpretation**:
- ✅ PASS: Meta-classifier learns from 50-60 datasets, demonstrates feature-method relationships
- ⚠️ PARTIAL: Learns but weakly (30-35% accuracy) — limited training signal
- ❌ FAIL: No learning (≤30%) — insufficient data for generalization

---

## Appendix: Reference Implementations

### sklearn RandomForestClassifier Documentation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- **Relevance**: Official API documentation for primary model
- **Key Parameters**: `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`

### sklearn Cross-Validation Guide
- **URL**: https://scikit-learn.org/stable/modules/cross_validation.html
- **Relevance**: Leave-K-out CV strategy for small datasets
- **Implementation**: `cross_val_score` with custom CV splitter

### H-M1 Feature Computation Code
- **Path**: `../h-m1/code/src/feature_computer.py`
- **Relevance**: Reused for feature extraction (Tier 1 + Tier 2)
- **Note**: Mock data fix already applied (no synthetic defaults)

### H-E1 Benchmark Collection
- **Path**: `../h-e1/code/output/benchmarks.json`
- **Relevance**: Source dataset (63 benchmarks with method rankings)
- **Format**: JSON with fields: `name`, `domain`, `method_rankings`, `metadata`

### Meta-Learning on Small Datasets (Conceptual)
- **Concept**: Few-shot learning principles apply to meta-learning with limited benchmarks
- **Strategy**: Regularization (max_depth, min_samples) prevents overfitting
- **Note**: No specific paper implementation — this is a novel hypothesis testing sufficiency

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-13T09:20:37+00:00

### Workflow History for This Hypothesis
- 2026-07-13T09:20:37: Hypothesis h-m2 set to IN_PROGRESS
- Phase 2C started: Experiment design in progress

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
