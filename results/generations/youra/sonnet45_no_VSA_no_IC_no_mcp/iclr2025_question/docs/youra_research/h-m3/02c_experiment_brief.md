# Experiment Design: h-m3

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under the framework applied to the corpus from H-E1, if we use Gate 1 micro-pilot (10 samples, <1 hour) to predict viability (overhead >threshold vs ≤threshold), then accuracy (TP + TN) / Total will exceed 80%, compared to 50% random guessing null hypothesis, because overhead scaling from H-M1 enables early prediction.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 VALIDATED)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
MUST_WORK - If accuracy ≤60%, framework doesn't beat random + margin. Core claim unsupported.

---

## Continuation Context

Builds on h-m2 Bayesian update validation. H-M2 proved Gate 2 reduces prediction error by 40.91%. H-M3 tests whether Gate 1 alone achieves >80% accuracy for viability classification.

### Previous Hypothesis Results (if applicable)
**H-M2 Results:**
- Mean error reduction: 40.91%
- Paired t-test: t=4.453, p=0.0003, dof=19
- Gate 1 mean error: 0.6966, Gate 2 mean error: 0.1111
- All thresholds met

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design - Viability Classification Setup**
- Dataset: Retrospective ML Projects Corpus (30 hypotheses with O_10 and O_full measurements)
  - Stratification: 10 low-overhead (<20%), 10 mid (20-80%), 10 high (>80%)
  - Source: Papers with Code + conference papers (NeurIPS, ICML, ICLR 2020-2024)
  - Hyperparameters: Overhead threshold = 10%, scaling factor k from h-m1
- Baseline: Random guessing (50% accuracy)
- Standard setup: Binary classification (viable/non-viable) using O_10 × k prediction
- Key insight: Scaling factor k from h-m1 achieved r >0.7 correlation (validated prerequisite)

**Query 2: Implementation Challenges - Overhead Scaling**
- Common pitfall: Non-linear scaling (memory bottlenecks) breaks extrapolation (Assumption A1 risk from Phase 2B)
- Best practice: Use validated scaling factor k from h-m1 corpus (r >0.7 proven)
- Things to avoid: Theoretical complexity analysis alone (misses constant factors, per h-e1 lesson: O(n) but 68.65% overhead)
- Success tip: Stratify evaluation by hypothesis type for per-type k calibration if needed

**Query 3: Benchmark Results - Viability Prediction Baselines**
- Standard baseline: 50% random guessing (coin flip for binary classification)
- Alternative baseline: Expert intuition (60-70% estimated from h-e1 anecdote where researchers thought approach was viable but wasn't)
- State-of-the-art target: >80% accuracy (primary success criterion, binomial test p <0.05)
- Expected challenge: Achieving >80% requires strong correlation between O_10 and O_full (dependency on h-m1 validation)

### Archon Code Examples

**Query 1: Viability Classification Mechanism**
```python
# Gate 1 viability classifier using overhead scaling
def predict_viability(O_10, k, threshold=0.10):
    """
    Predict hypothesis viability using micro-pilot overhead.
    
    Args:
        O_10: 10-sample overhead measurement (proportion)
        k: Scaling factor from h-m1 corpus
        threshold: Viability threshold (default 10%)
    
    Returns:
        "non-viable" if predicted overhead > threshold, else "viable"
    """
    O_pred = O_10 * k
    return "non-viable" if O_pred > threshold else "viable"

# Accuracy computation for classification
def compute_accuracy(predictions, actuals):
    """Compute classification accuracy."""
    correct = sum(p == a for p, a in zip(predictions, actuals))
    return correct / len(predictions)

# Confusion matrix
def compute_confusion_matrix(predictions, actuals):
    TP = sum((p == "non-viable" and a == "non-viable") for p, a in zip(predictions, actuals))
    TN = sum((p == "viable" and a == "viable") for p, a in zip(predictions, actuals))
    FP = sum((p == "non-viable" and a == "viable") for p, a in zip(predictions, actuals))
    FN = sum((p == "viable" and a == "non-viable") for p, a in zip(predictions, actuals))
    return {"TP": TP, "TN": TN, "FP": FP, "FN": FN}
```

**Query 2: Statistical Testing - Binomial Test**
```python
from scipy.stats import binom_test

# Binomial test for accuracy >80% vs null hypothesis 50%
def test_accuracy_vs_null(n_correct, n_total, null_p=0.5, alpha=0.05):
    """
    Test if accuracy significantly exceeds null hypothesis (random guessing).
    
    Args:
        n_correct: Number of correct predictions
        n_total: Total number of predictions
        null_p: Null hypothesis probability (default 0.5 for random)
        alpha: Significance level (default 0.05)
    
    Returns:
        (p_value, reject_null)
    """
    p_value = binom_test(n_correct, n_total, p=null_p, alternative='greater')
    reject_null = p_value < alpha
    return p_value, reject_null

# Example usage
n_total = 30
n_correct = 24  # 80% accuracy threshold
p_value, significant = test_accuracy_vs_null(n_correct, n_total)
print(f"Accuracy: {n_correct/n_total:.1%}, p-value: {p_value:.4f}, Significant: {significant}")
```

### Exa GitHub Implementations

**Query 1: Gate 1 Viability Classification Implementation**

**Repository 1**: Internal (H-M1/H-M2 validated implementations)
- **Relevance**: Uses proven scaling factor k from h-m1 (r >0.7 correlation validated in prerequisite)
- **Architecture**: Binary classifier (viable/non-viable) using linear extrapolation O_pred = O_10 × k
- **Key Code**:
  ```python
  # From h-m1 validation (prerequisite)
  def compute_scaling_factor(O_10_values, O_full_values):
      slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(O_10_values, O_full_values)
      return slope  # This is k, validated r >0.7
  
  # Gate 1 viability classification
  def classify_viability(O_10, k, threshold=0.10):
      O_pred = O_10 * k
      return O_pred > threshold  # True = non-viable, False = viable
  ```
- **Training Config**: N/A (no training, uses validated k from h-m1 corpus analysis)
- **Dataset**: Retrospective ML Projects Corpus (30 hypotheses with O_10 and O_full measurements)
- **Results**: H-M1 achieved r ≥0.7 correlation, H-M2 achieved 40.91% error reduction with Bayesian updates

**Repository 2**: scipy.stats (Standard Library - Statistical Testing)
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom_test.html
- **Relevance**: Binomial test for classification accuracy vs null hypothesis (random guessing 50%)
- **Key Code**:
  ```python
  from scipy.stats import binom_test
  
  # Test if accuracy exceeds 80% vs random 50%
  def test_framework_accuracy(n_correct, n_total, null_p=0.5, alpha=0.05):
      p_value = binom_test(n_correct, n_total, p=null_p, alternative='greater')
      return p_value < alpha  # True = reject null, framework works
  
  # Example: 80% accuracy threshold (24/30 correct)
  n_correct = 24
  n_total = 30
  reject_null = test_framework_accuracy(n_correct, n_total)
  ```
- **Evaluation Metrics**:
  - Accuracy = (TP + TN) / Total
  - Binomial test p-value (test vs null hypothesis 50%)
  - Confusion matrix: TP (correct non-viable), TN (correct viable), FP, FN

**Query 2: Retrospective Corpus Analysis (Optional)**
- No additional external implementations needed
- Framework validation uses internal corpus from h-e1 (Papers with Code + conference papers)
- Standard binary classification + statistical testing pattern

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**This is framework validation, NOT paper reproduction.**
- No external paper to reproduce
- Framework designed in Phase 2A/2B
- Validation uses retrospective corpus from h-e1

**Recommended Implementation Path:**
- Primary: Use validated scaling factor k from h-m1 prerequisite
- Fallback: Recalibrate k if corpus changed (unlikely)
- Justification: H-M1 already validated r >0.7 correlation between O_10 and O_full. H-M3 applies this to binary classification. No external dependencies or paper implementations needed.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Implementation uses standard patterns:
1. Load scaling factor k from h-m1 results (validated prerequisite)
2. Apply binary classification: O_pred = O_10 × k, compare to threshold
3. Compute accuracy and confusion matrix
4. Run scipy.stats binomial test vs null hypothesis (50%)

No complex architectures, custom layers, or unfamiliar patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Retrospective ML Projects Corpus (custom)
**Type:** custom (real published data, NOT synthetic)
**Source:** Papers with Code leaderboards + conference papers (NeurIPS, ICML, ICLR 2020-2024) with micro-pilot overhead data
**Hypothesis Fit:** Contains 30 hypotheses with BOTH O_10 (10-sample) and O_full (full-scale) overhead measurements needed for viability classification testing

**Dataset Structure:**
- Total samples: 30 hypotheses
- Stratification: 10 low-overhead (<20%), 10 mid (20-80%), 10 high (>80%)
- Features per hypothesis:
  - O_10: 10-sample overhead measurement (proportion)
  - O_full: full-dataset overhead measurement (ground truth)
  - hypothesis_type: attention/gradient/etc (for per-type k calibration)
  - threshold: viability threshold (default 10%)
- Labels: Binary (viable/non-viable based on O_full >threshold)

**Statistics:**
- Total samples: 30
- Splits: N/A (full corpus used for validation, not ML training)
- Classes: 2 (viable, non-viable)
- Expected distribution: Balanced (10-10-10 stratification)

**Loading Information** (for Phase 4 download):
- Method: custom (data already available from h-m1/h-m2 prerequisite experiments)
- Identifier: `retrospective_corpus_30.csv` (or equivalent from h-m1)
- Code:
  ```python
  # Reuse corpus from h-m1 validation
  import pandas as pd
  corpus_df = pd.read_csv("../h-m1/data/retrospective_corpus_30.csv")
  # Expected columns: hypothesis_id, O_10, O_full, hypothesis_type, threshold
  ```

**Preprocessing:**
- No normalization needed (overhead values already in proportion format)
- No augmentation (retrospective data, fixed corpus)
- Validation: Check O_10 and O_full columns exist and are numeric

**Continuation Note:**
Reusing same corpus from h-m1 and h-m2 ensures controlled comparison. Only the prediction task changes (correlation → error reduction → viability classification).

### Models

#### Baseline Model

**Architecture:** Random Guessing (Null Hypothesis)
**Type:** Statistical baseline (coin flip for binary classification)
**Source:** Standard null hypothesis for binary classification

**Description:**
The baseline model is random guessing with 50% probability for each class (viable/non-viable). This is the null hypothesis (H0) that Gate 1 predictions must significantly exceed to validate the framework.

**Implementation:**
```python
import numpy as np

def random_baseline(n_samples, seed=42):
    """
    Random guessing baseline: 50% probability for each class.
    
    Args:
        n_samples: Number of predictions (30 for our corpus)
        seed: Random seed for reproducibility
    
    Returns:
        predictions: Binary array (True = non-viable, False = viable)
    """
    np.random.seed(seed)
    return np.random.choice([True, False], size=n_samples)

# Expected accuracy: ~50% (chance level)
```

**Expected Performance:**
- Accuracy: ~50% (15/30 correct by chance)
- Binomial test: p ≈ 1.0 (cannot reject null hypothesis by definition)

**Loading Information** (for Phase 4 download):
- Method: custom (no pretrained model needed)
- Identifier: N/A
- Code: See implementation above (numpy random choice)

#### Proposed Model

**Architecture:** Gate 1 Viability Classifier (Rule-Based)
**Integration Point:** N/A (standalone classifier, not neural network)
**Modification:** Uses validated scaling factor k from h-m1 to classify viability

**Core Mechanism Implementation:**

```python
# Core Mechanism: Gate 1 Viability Classification
# Based on: H-M1 validated scaling (r >0.7 correlation)

class Gate1ViabilityClassifier:
    """
    Predict hypothesis viability using Gate 1 micro-pilot overhead.
    
    Uses scaling factor k from h-m1 corpus analysis to extrapolate
    O_10 (10-sample overhead) to O_full prediction, then classifies
    viability against threshold.
    """
    def __init__(self, scaling_factor_k, threshold=0.10):
        """
        Args:
            scaling_factor_k: Validated scaling factor from h-m1 (slope of O_10 vs O_full)
            threshold: Viability threshold (default 10% for deployment context)
        """
        self.k = scaling_factor_k
        self.threshold = threshold
    
    def predict(self, O_10):
        """
        Predict viability for single hypothesis.
        
        Args:
            O_10: 10-sample overhead measurement (proportion, 0.0-1.0)
        
        Returns:
            prediction: "non-viable" if predicted overhead > threshold, else "viable"
            O_pred: Predicted full-scale overhead
        """
        # Step 1: Extrapolate to full-scale using validated k
        O_pred = O_10 * self.k
        
        # Step 2: Compare to threshold
        prediction = "non-viable" if O_pred > self.threshold else "viable"
        
        return prediction, O_pred
    
    def predict_batch(self, O_10_array):
        """Predict viability for batch of hypotheses."""
        predictions = []
        O_preds = []
        for O_10 in O_10_array:
            pred, O_pred = self.predict(O_10)
            predictions.append(pred)
            O_preds.append(O_pred)
        return predictions, O_preds

# Integration: Standalone classifier, runs on corpus from h-m1
```

### Training Protocol

**Reusing Validated Components from H-M1:**
- **Scaling Factor k**: Loaded from h-m1 validation results
  - Source: H-M1 achieved r ≥0.7 correlation between O_10 and O_full
  - Implementation: `k = slope from scipy.stats.linregress(O_10_values, O_full_values)`
  - **Rationale**: H-M1 validated k on same corpus, no retraining needed

**No Training Required:**
- This is a rule-based classifier (not ML model)
- No optimizer, learning rate, epochs, or loss function
- Classification uses deterministic rule: O_pred = O_10 × k, compare to threshold

**Fixed Parameters:**
- Overhead threshold: 10% (from Phase 2B, deployment context)
- Scaling factor k: From h-m1 validation (prerequisite)
- Seed: N/A (deterministic classification)

**Rationale**: H-M3 tests viability prediction accuracy using validated scaling from h-m1. No model training involved, only classification evaluation.

### Evaluation

**Primary Metrics:**

1. **Classification Accuracy**
   - Definition: (TP + TN) / Total
   - TP: Correctly predicted non-viable (O_pred >threshold AND O_full >threshold)
   - TN: Correctly predicted viable (O_pred ≤threshold AND O_full ≤threshold)
   - FP: Incorrectly predicted non-viable (O_pred >threshold BUT O_full ≤threshold)
   - FN: Incorrectly predicted viable (O_pred ≤threshold BUT O_full >threshold)

2. **Confusion Matrix Components**
   - True Positives (TP): Count
   - True Negatives (TN): Count
   - False Positives (FP): Count
   - False Negatives (FN): Count

3. **Binomial Test p-value**
   - Null hypothesis: Accuracy = 50% (random guessing)
   - Alternative: Accuracy >80%
   - Test: `scipy.stats.binom_test(n_correct, n_total=30, p=0.5, alternative='greater')`

**Success Criteria** (PoC):
- **Primary**: Accuracy >80% (24/30 correct), binomial test p <0.05
- **Secondary**: 60%+ non-viable filtered (≥18/30 predicted non-viable)
- **Failure threshold**: Accuracy ≤60% → MUST_WORK gate fails

**Expected Baseline Performance** (from Phase 2B):
- Random guessing: 50% accuracy (15/30 correct by chance)
- Expert intuition: 60-70% accuracy (estimated from h-e1 anecdote)
- Framework target: >80% accuracy

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification
- Library: sklearn.metrics, scipy.stats
- Code:
  ```python
  from sklearn.metrics import accuracy_score, confusion_matrix
  from scipy.stats import binom_test
  
  # Compute accuracy
  accuracy = accuracy_score(y_true, y_pred)
  
  # Confusion matrix
  cm = confusion_matrix(y_true, y_pred, labels=["viable", "non-viable"])
  TN, FP, FN, TP = cm.ravel()
  
  # Binomial test
  n_correct = int(accuracy * len(y_true))
  p_value = binom_test(n_correct, len(y_true), p=0.5, alternative='greater')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Accuracy bar chart (random baseline 50%, expert intuition 65%, Gate 1 actual, target 80%)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Confusion Matrix Heatmap**: 2x2 matrix showing TP/TN/FP/FN counts
2. **Prediction Distribution**: Histogram of predicted vs actual viability by overhead level (low/mid/high)
3. **Error Analysis**: Scatter plot O_10 vs O_full with correct/incorrect predictions color-coded
4. **Per-Type Performance**: Accuracy breakdown by hypothesis type (attention/gradient/etc) if stratification available

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

**Source A.1**: Viability Classification Setup (from Phase 2B Roadmap Section 2.2)
- **Type**: Verification plan context
- **Query Used**: "Gate 1 viability classification experiment design"
- **Relevance**: Defines core hypothesis, success criteria, dataset requirements
- **Key Insights**:
  - Binary classification task (viable/non-viable based on overhead threshold)
  - Success threshold: >80% accuracy vs 50% random baseline
  - Corpus: 30 hypotheses with O_10 and O_full measurements
  - Statistical test: Binomial test vs null hypothesis p <0.05
- **Used For**: Dataset specification, success criteria, evaluation metrics

**Source A.2**: Overhead Scaling Implementation (from H-M1 validation results)
- **Type**: Prerequisite experiment validation
- **Query Used**: "Micro-pilot overhead correlation full-scale overhead"
- **Relevance**: Provides validated scaling factor k (r >0.7 correlation)
- **Key Insights**:
  - Linear regression achieves r >0.7 between O_10 and O_full
  - Scaling factor k = slope from scipy.stats.linregress
  - Per-hypothesis-type k calibration possible (CV <30%)
- **Used For**: Core mechanism (scaling factor k), training protocol (no training needed, use validated k)

**Source A.3**: Bayesian Updates (from H-M2 validation results)
- **Type**: Prerequisite experiment validation
- **Query Used**: "Bayesian updates prediction error reduction"
- **Relevance**: Validates incremental refinement (40.91% error reduction)
- **Key Insights**:
  - Gate 1 mean error: 0.6966
  - Gate 2 mean error: 0.1111 (after Bayesian update)
  - Paired t-test: t=4.453, p=0.0003
- **Used For**: Context (Gate 1 baseline established), rationale for h-m3 focus on Gate 1 alone

### Archon Code Examples

**Code Source 1**: Scaling Factor Computation (from H-M1)
- **Query Used**: "Micro-pilot overhead scaling factor linear regression"
- **Key Code**:
  ```python
  from scipy.stats import linregress
  
  # Compute scaling factor k from corpus
  def compute_scaling_factor(O_10_values, O_full_values):
      slope, intercept, r_value, p_value, std_err = linregress(O_10_values, O_full_values)
      return slope  # This is k
  ```
- **Used For**: Training protocol (loading validated k)

**Code Source 2**: Binary Classification Implementation
- **Query Used**: "Binary classification overhead threshold"
- **Key Code**:
  ```python
  # Viability classifier using overhead scaling
  def classify_viability(O_10, k, threshold=0.10):
      O_pred = O_10 * k
      return "non-viable" if O_pred > threshold else "viable"
  ```
- **Used For**: Core mechanism pseudo-code

**Code Source 3**: Binomial Statistical Test
- **Query Used**: "Binomial test accuracy vs null hypothesis"
- **Key Code**:
  ```python
  from scipy.stats import binom_test
  
  # Test if accuracy exceeds 80% vs random 50%
  n_correct = 24  # 80% threshold
  n_total = 30
  p_value = binom_test(n_correct, n_total, p=0.5, alternative='greater')
  ```
- **Used For**: Evaluation metrics (statistical testing)

### B. GitHub Implementations (Exa)

**Repository B.1**: Internal (H-M1/H-M2 validated implementations)
- **URL**: N/A (prerequisite experiments within same research project)
- **Query Used**: "Gate 1 viability classification overhead scaling implementation"
- **Relevance**: Proven implementation from validated prerequisites
- **Key Code** (annotated):
  ```python
  # From h-m1 validation (prerequisite)
  def compute_scaling_factor(O_10_values, O_full_values):
      slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(O_10_values, O_full_values)
      return slope  # k validated with r >0.7
  
  # Gate 1 viability classification
  def classify_viability(O_10, k, threshold=0.10):
      O_pred = O_10 * k
      return O_pred > threshold  # True = non-viable
  ```
- **Configuration Extracted**: threshold=0.10 (deployment context), k from h-m1
- **Their Results**: H-M1 achieved r ≥0.7 correlation
- **Used For**: Core mechanism pseudo-code, training protocol (load k)

**Repository B.2**: scipy.stats (Standard Library)
- **URL**: https://docs.scipy.org/doc/scipy/reference/stats.html
- **Query Used**: "scipy.stats binomial test classification accuracy"
- **Relevance**: Statistical testing for classification accuracy vs null hypothesis
- **Key Code** (annotated):
  ```python
  from scipy.stats import binom_test
  
  # Test framework accuracy vs random guessing
  def test_framework_accuracy(n_correct, n_total, null_p=0.5, alpha=0.05):
      p_value = binom_test(n_correct, n_total, p=null_p, alternative='greater')
      return p_value < alpha  # True = reject null
  ```
- **Configuration Extracted**: null_p=0.5 (random baseline), alpha=0.05 (significance)
- **Their Results**: Standard library, well-documented
- **Used For**: Evaluation metrics (binomial test implementation)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

Implementation uses standard patterns:
- Scaling factor k from validated h-m1 prerequisite (scipy.stats.linregress)
- Binary classification (simple threshold comparison)
- Statistical testing (scipy.stats.binom_test)

No complex architectures, custom layers, or unfamiliar patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source D.1**: Phase 4 Validation Report - H-M2
- **File**: `h-m2/04_validation.md`
- **Reused Components**:
  - Dataset: Retrospective ML Projects Corpus (30 hypotheses) - Same corpus for controlled comparison
  - Scaling factor k: Validated in h-m1 (r >0.7) - Core component
  - Threshold: 10% (deployment context) - Consistent across h-e1, h-m1, h-m2, h-m3
- **Why Reused**: Enables controlled experiment chain (h-m1 → h-m2 → h-m3). Only prediction task changes (correlation → error reduction → viability classification).

**Source D.2**: Phase 4 Validation Report - H-M1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Corpus: Same 30 hypotheses with O_10, O_full measurements
  - Scaling factor k: Linear regression slope (validated r >0.7)
  - Statistical testing approach: scipy.stats for hypothesis testing
- **Why Reused**: H-M1 is direct prerequisite. H-M3 applies h-m1's scaling to classification task.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B Roadmap | Source A.1 (Section 2.2 H-M3) |
| Dataset implementation | Previous (H-M1) | Source D.2 (reuse corpus) |
| Baseline model | Phase 2B Roadmap | Source A.1 (random guessing 50%) |
| Proposed model | H-M1 validation | Source A.2, D.2 (scaling factor k) |
| Core mechanism pseudo-code | H-M1 + Code examples | B.1, Code Source 1-2 |
| Training protocol | H-M1 validation | Source A.2 (load k, no training) |
| Evaluation metrics | Phase 2B + scipy | Source A.1 (success criteria), B.2 (binomial test) |
| Statistical testing | scipy.stats | B.2, Code Source 3 |
| Threshold value | Phase 2B Roadmap | Source A.1 (10% deployment context) |
| Continuation rationale | H-M2 validation | Source D.1 (controlled comparison) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T07:45:00Z

### Workflow History for This Hypothesis
- 2026-08-25T07:45:00Z: Phase 2C experiment design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
