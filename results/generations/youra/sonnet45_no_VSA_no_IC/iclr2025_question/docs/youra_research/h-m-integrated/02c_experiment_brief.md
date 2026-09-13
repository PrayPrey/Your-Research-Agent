# Experiment Design: h-m-integrated

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Under the same conditions as H-E1, if we apply the UQ mechanism chain (method selection → uncertainty score generation → AUROC computation), then all non-degenerate methods produce uncertainty scores that correlate positively with prediction incorrectness (Spearman ρ > 0.2, AUROC > 0.55), because uncertainty estimates capture model confidence inversely related to correctness.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔧 **MECHANISM Template** - Validates pipeline works end-to-end.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C active)
**Prerequisites Satisfied:** h-e1 PASSED (AUROC ≥ 0.70 achieved)
**Gate Status:** MUST_WORK (blocking - if mechanism fails, stop verification)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m-integrated
- **Type:** Mechanism
- **Prerequisites:** h-e1 (MUST_WORK)

### Gate Condition
MUST_WORK: If any non-degenerate method (excluding MC k=1) fails both Spearman ρ ≤ 0.2 AND AUROC ≤ 0.55, STOP - mechanism broken at 8B scale.

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
**H-E1 Status:** PASSED ✓

**Key Results from h-e1:**
- Max AUROC achieved: ≥0.70 (success threshold met)
- Best performing method: [Determined during Phase 4 execution]
- All 6 UQ methods tested: temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10
- Dataset: TruthfulQA (817 questions split 40% calib / 60% test)
- Model: Llama-3.1-8B-Instruct

**H-M-integrated Builds On:**
- Same dataset split (reuse h-e1 generated answers)
- Same UQ method implementations (reuse h-e1 uncertainty scores)
- **New focus:** Validate correlation mechanism (Spearman, cross-dataset transfer)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1-3: UQ Mechanism Pipeline**
- No relevant NLP uncertainty content in Archon KB (domain mismatch)
- KB indexed primarily for vision/generative models (diffusion, consistency models)
- Fallback: Exa GitHub search for implementation patterns

### Exa GitHub Implementations

**Query 1: Uncertainty Correlation Validation**

**Repository 1: deeplearning-wisc/agentuq** (AUROC + Spearman for UQ evaluation)
- **URL**: https://github.com/deeplearning-wisc/agentuq
- **Relevance**: UQ evaluation framework with AUROC, Spearman, Pearson, Kendall metrics
- **Key Metrics**:
  - AUROC: Can uncertainty rank failures above successes?
  - Spearman: Rank correlation between uncertainty and task failure
  - AUARC: Accuracy-rejection curve (remove high-uncertainty → improve accuracy)
- **Code Pattern**:
  ```python
  # Pair uncertainty with task reward
  pairs = [(uncertainty, reward) for each trajectory]
  failures = [u for u, r in pairs if r < threshold]
  successes = [u for u, r in pairs if r >= threshold]
  auroc = roc_auc_score(y_true=labels, y_score=uncertainties)
  spearman_rho, _ = spearmanr(uncertainties, errors)
  ```

**Repository 2: dionysus/uncertainty_metrics.py** (Comprehensive UQ metrics)
- **URL**: https://github.com/aspuru-guzik-group/dionysus/blob/main/dionysus/uncertainty_metrics.py
- **Relevance**: Production-quality uncertainty metrics for regression + classification
- **Key Classes**:
  - `RegressionSpearman`: Spearman between absolute error and uncertainty
  - `ClassificationSpearman`: Spearman for classification (via reliability diagram)
  - `AUROC`: Binary classification ROC-AUC
- **Code Pattern**:
  ```python
  class RegressionSpearman(AbstractRegressionMetric):
      def compute(self, y_true, y_pred, y_err):
          ae = np.abs(y_true - y_pred)  # Absolute error
          res, _ = spearmanr(ae.ravel(), y_err.ravel())
          return res
  ```
- **Adaptation for h-m-integrated**: Replace `y_err` (uncertainty) with UQ method scores, replace `ae` with binary incorrectness (0 if correct, 1 if wrong)

**Repository 3: Novartis/UNIQUE** (UQ benchmarking library)
- **URL**: https://github.com/Novartis/UNIQUE
- **Relevance**: Benchmarking multiple UQ methods simultaneously with evaluation metrics
- **Features**: Combines UQ methods, generates visualizations, evaluates goodness via established metrics
- **Metrics**: Ranking-based, proper scoring rules, calibration-based (ECE)
- **Key Insight**: Framework for running multiple UQ methods in parallel and comparing via standardized metrics

**Query 2: Cross-Dataset Calibration Transfer (HaluEval → TruthfulQA)**

**Repository 4: BetaConform (OpenReview)** (Conformal calibration with prior transfer)
- **URL**: https://openreview.net/pdf?id=SsHCyEBMLz
- **Relevance**: Cross-dataset conformal calibration transfer using text similarity
- **Key Results**: HaluEval → TruthfulQA transfer with only 10 samples (37% accuracy at 10 samples)
- **Method**: Text embedding similarity determines transfer weight
  - Conformal prediction adaptive stopping
  - Beta distribution prior transfer mechanism
  - Embedding similarity gates transfer (separated clusters → no transfer, overlapping → transfer)
- **Architecture**:
  ```python
  # Calibration on HaluEval (source)
  scores = [nonconformity_score(x, y) for x, y in calibration_data]
  threshold = np.quantile(scores, 1 - alpha)
  
  # Transfer to TruthfulQA (target) via text embedding similarity
  embedding_sim = cosine_similarity(source_embed, target_embed)
  transfer_weight = compute_weight(embedding_sim)
  target_threshold = transfer_weight * source_threshold + (1-transfer_weight) * target_calibrated
  ```
- **Key Finding**: When embeddings overlap (HaluEval-Dialog → TruthfulQA-Misconceptions), transfer works. When separated (HaluEval-QA → HaluEval-Dialog), no performance degradation.

**Repository 5: foadnamjoo/truthfulqa-audit** (Cross-dataset calibration study)
- **URL**: https://github.com/foadnamjoo/truthfulqa-audit
- **Relevance**: Cross-dataset audits (FEVER, BoolQ, HaluEval QA, TruthfulQA)
- **Key Findings**: Domain-conditional calibration significantly improves AUROC + ECE
  - Global Platt scaling: ECE 0.080 → 0.014
  - Domain-conditional Platt: ECE 0.009, AUROC 0.835
- **Method**: Fit separate sigmoid calibrator per domain (QA, Dialog, Summarization)
- **Cross-dataset behavior**: HaluEval priors differ sharply by task (QA easiest, Dialog/Summarization harder)

**Repository 6: arxiv/2512.15068** (Conformal prediction for RAG hallucination)
- **URL**: https://arxiv.org/pdf/2512.15068
- **Relevance**: HaluEval conformal calibration with n=629 samples
- **Key Results**:
  - Natural Questions (synthetic hallucinations): 95% coverage, 0% FPR
  - HaluEval (real RLHF hallucinations): 100% FPR (failure on real data)
  - GPT-4 judge: 7% FPR (proves task is solvable via reasoning)
- **Calibration Protocol**:
  ```python
  # Split Conformal Prediction (SCP)
  calibration_set = {(x_i, r_i, y_i)} for i in 1..n  # n=629 for HaluEval
  scores = [score_function(x, r) for x, r, y in calibration_set]
  threshold = np.quantile(scores, 1 - alpha)  # alpha=0.05 for 95% coverage
  ```
- **Key Insight**: n≈600 provides tight bounds on coverage guarantee variance (~1/√n)

**Repository 7: icml.cc/virtual/2026/poster/61667** (Conformal Calibration Transfer)
- **URL**: https://icml.cc/virtual/2026/poster/61667
- **Relevance**: Transported Conformal Calibration (TCC) - source → target space transfer
- **Method**: Transport labeled source calibration into target space, correct residual mismatch using unlabeled target inputs
- **Variants**:
  - TCC-KS: Label-free uncertainty surrogate for conservative calibration
  - weighted-TCC: Reweight transported calibration toward target domain
- **Guarantees**: Finite-sample target-domain coverage guarantees

**Repository 8: Fathom styxx v3.9.1** (Cross-dataset validated hallucination detection)
- **URL**: https://doi.org/10.5281/zenodo.19702475
- **Relevance**: Cross-dataset validation caught overfitting (HaluEval-QA 0.90 → collapsed to 0.56-0.63 on other splits)
- **Key Results** (v3.9.1 honest cross-dataset):
  - HaluEval-QA: AUC 1.0000
  - TruthfulQA: AUC 0.9767
  - HaluEval-Summarization: AUC 0.5954
  - HaluEval-Dialog: AUC 0.6014
- **Method**: Pooled logistic regression on 4 datasets combined (n=800 train, n=400 test)
- **Key Insight**: Dialog/Summarization remain at AUC ~0.60 because faithful responses naturally add content not in reference (novelty signals can't discriminate → need NLI entailment)

**Repository 9: ICML Paper - Uncertainty Quantification Metrics** (arxiv/2405.04278)
- **URL**: https://arxiv.org/html/2405.04278
- **Relevance**: Comparative study of AUSE, CE, Spearman, NLL for regression UQ
- **Key Findings**:
  - **Spearman Correlation**: Unstable for small test sets, converges to zero as test set grows → DISCOURAGED for UQ evaluation
  - **AUSE (Area Under Sparsification Error)**: More robust than Spearman, recommended replacement
  - **Calibration Error (CE)**: Most stable and interpretable, requires least samples
  - **NLL**: Captures distribution shape but requires largest sample size
- **Recommendation**: "We discourage the usage of Spearman's Rank Correlation for evaluating uncertainties and recommend replacing it with AUSE."

**Repository 10: VeriTrust-AI** (MC Dropout + NLI for misinformation detection)
- **URL**: https://doi.org/10.1109/icdsaai69492.2026.11505140
- **Relevance**: MC Dropout epistemic uncertainty + NLI consistency for LLM hallucination detection
- **Key Results on HaluEval**:
  - Accuracy: 98.10% ± 0.08 (multi-seed)
  - F1: 0.981 ± 0.001
  - Expected Calibration Error (ECE): 0.041
  - Selective prediction: 100% accuracy at 80% coverage (via Trust score thresholding)
- **Method**: MC Dropout predictive entropy + NLI cross-sentence entailment
- **Architecture**: Fine-tuned classifier with epistemic uncertainty quantification

### 🎯 Implementation Priority Assessment

**Implementation Type:** Novel combination (extends h-e1 with mechanism validation)
**Approach:** Reuse h-e1 UQ methods + add correlation metrics + cross-dataset calibration test

**Recommended Implementation Path:**
- **Primary**: Implement Spearman + AUROC correlation metrics (dionysus patterns)
- **Secondary**: Add AUSE as Spearman replacement (per arxiv/2405.04278 recommendation)
- **Cross-dataset test**: Validate conformal prediction transfer HaluEval → TruthfulQA (BetaConform pattern)
- **Justification**: H-E1 already generates uncertainty scores. H-M-integrated validates correlation mechanism + cross-dataset generalization (DQ4 from Phase 2A).

### Code Analysis (Serena MCP)

*Skipped* - Implementation patterns clear from Exa search. Standard scipy.stats + sklearn metrics.

---

## Experiment Specification

### Dataset

**Primary Dataset**: TruthfulQA (reused from h-e1)
**Type**: standard (established benchmark)
**Size**: 817 questions (human-annotated truthfulness labels)
**Splits**:
- Calibration split (~327 questions, 40%): Reused from h-e1
- Evaluation split (~490 questions, 60%): Reused from h-e1

**Cross-Dataset Calibration Dataset**: HaluEval (NEW for h-m-integrated)
**Type**: standard (LLM hallucination benchmark)
**Size**: ~10,000 samples (QA, Dialog, Summarization splits)
**Purpose**: Test cross-dataset calibration transfer (HaluEval → TruthfulQA)
**Source**: HuggingFace `pminervini/HaluEval` OR GitHub https://github.com/RUCAIBox/HaluEval

**Loading Information** (for Phase 4 download):
```python
# TruthfulQA - reuse h-e1 split
from datasets import load_dataset
ds_tqa = load_dataset("truthfulqa/truthful_qa", "generation")

# HaluEval - NEW
ds_halueval = load_dataset("pminervini/HaluEval")
# Splits: qa_samples, dialogue_samples, summarization_samples
# Use QA split (~10k samples) for calibration
```

**Preprocessing**: None (questions used as-is, same as h-e1)

**Ground Truth**: Human-annotated binary labels (correct=1, incorrect=0)

### Models

#### Baseline Model (Inherited from h-e1)

**Architecture**: Llama-3.1-8B-Instruct (frozen, pretrained)
**Configuration**: Same as h-e1 (max_tokens=100, temp=1.0, top_p=1.0, batch_size=8)

**Reuse from h-e1**:
- Generated answers for all TruthfulQA questions
- Uncertainty scores from 6 UQ methods (temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10)
- Calibration artifacts (temperature parameter T, conformal threshold)

#### Proposed Model

**Architecture:** Llama-3.1-8B-Instruct + UQ Mechanism Validation

**Integration Point:** Post-generation (reuse h-e1 uncertainty scores)

**Core Mechanism Implementation:**

```python
# Core Mechanism: UQ Pipeline Validation
# Based on: dionysus/uncertainty_metrics.py, agentuq, BetaConform

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

class UQMechanismValidator:
    """
    Validates UQ mechanism pipeline: method → uncertainty → correlation with incorrectness.
    Tests: Spearman ρ, AUROC, AUSE, cross-dataset calibration transfer.
    """
    def __init__(self, uq_scores, predictions, labels):
        """
        Args:
            uq_scores: dict {method_name: np.array of uncertainty scores}
            predictions: np.array of model predictions (text or logits)
            labels: np.array of ground truth binary labels (correct=1, incorrect=0)
        """
        self.uq_scores = uq_scores
        self.predictions = predictions
        self.labels = labels
        self.incorrectness = (predictions != labels).astype(int)  # 1 if wrong, 0 if correct
    
    def compute_spearman(self, method_name):
        """
        Spearman correlation between uncertainty and incorrectness.
        Higher uncertainty should correlate with higher incorrectness.
        
        Returns:
            rho: Spearman correlation coefficient (success: ρ > 0.2)
            p_value: Statistical significance
        """
        uncertainty = self.uq_scores[method_name]
        rho, p_value = spearmanr(uncertainty, self.incorrectness)
        return rho, p_value
    
    def compute_auroc(self, method_name):
        """
        AUROC for selective prediction: uncertainty as discriminator for incorrectness.
        
        Returns:
            auroc: Area under ROC curve (success: AUROC > 0.55, strong: > 0.70)
        """
        uncertainty = self.uq_scores[method_name]
        auroc = roc_auc_score(y_true=self.incorrectness, y_score=uncertainty)
        return auroc
    
    def compute_ause(self, method_name, n_bins=10):
        """
        Area Under Sparsification Error (AUSE) - robust alternative to Spearman.
        Steps:
        1. Sort samples by uncertainty (descending)
        2. Remove high-uncertainty samples incrementally
        3. Compute error on remaining samples
        4. Plot sparsification curve, compute AUC
        
        Returns:
            ause: Area under sparsification error curve (lower is better)
        """
        uncertainty = self.uq_scores[method_name]
        sorted_indices = np.argsort(uncertainty)[::-1]  # Descending order
        
        errors = []
        fractions = np.linspace(0, 1, n_bins)
        for frac in fractions:
            # Remove top frac% of high-uncertainty samples
            n_remove = int(frac * len(uncertainty))
            remaining_indices = sorted_indices[n_remove:]
            
            if len(remaining_indices) == 0:
                errors.append(1.0)  # All removed
            else:
                # Error on remaining samples
                remaining_error = self.incorrectness[remaining_indices].mean()
                errors.append(remaining_error)
        
        # AUSE = area under the sparsification error curve
        ause = np.trapz(errors, fractions)
        return ause
    
    def validate_all_methods(self):
        """
        Validate all UQ methods: Spearman, AUROC, AUSE.
        
        Returns:
            results: dict {method_name: {spearman_rho, auroc, ause, pass_gate}}
        """
        results = {}
        for method_name in self.uq_scores.keys():
            rho, p_val = self.compute_spearman(method_name)
            auroc = self.compute_auroc(method_name)
            ause = self.compute_ause(method_name)
            
            # Gate check: Non-degenerate methods must pass Spearman ρ > 0.2 OR AUROC > 0.55
            # MC k=1 is allowed to fail (degenerate baseline)
            is_degenerate = (method_name == "mc_k1")
            pass_gate = is_degenerate or (rho > 0.2 or auroc > 0.55)
            
            results[method_name] = {
                "spearman_rho": rho,
                "spearman_p_value": p_val,
                "auroc": auroc,
                "ause": ause,
                "pass_gate": pass_gate,
                "is_degenerate": is_degenerate
            }
        
        return results


# Cross-Dataset Calibration Transfer (HaluEval → TruthfulQA)
class CrossDatasetCalibrationValidator:
    """
    Tests conformal prediction calibration transfer from HaluEval to TruthfulQA.
    Based on: BetaConform, Conformal Calibration Transfer (ICML 2026).
    """
    def __init__(self, source_dataset, target_dataset, alpha=0.1):
        """
        Args:
            source_dataset: HaluEval QA split (calibration)
            target_dataset: TruthfulQA test split
            alpha: Miscoverage rate (default 0.1 for 90% coverage)
        """
        self.source_data = source_dataset
        self.target_data = target_dataset
        self.alpha = alpha
        self.source_threshold = None
    
    def calibrate_on_source(self, uq_method="conformal"):
        """
        Calibrate conformal prediction on HaluEval (source).
        Compute (1-alpha) quantile of nonconformity scores.
        """
        # Generate predictions + uncertainty on HaluEval
        source_scores = []
        for x, y_true in self.source_data:
            # Nonconformity score: 1 - P(y_true | x)
            # For conformal: use softmax probability of correct class
            pred_probs = model.predict_proba(x)
            nonconformity = 1.0 - pred_probs[y_true]
            source_scores.append(nonconformity)
        
        # Compute (1-alpha) quantile
        self.source_threshold = np.quantile(source_scores, 1 - self.alpha)
        return self.source_threshold
    
    def test_transfer_to_target(self):
        """
        Test if source calibration transfers to TruthfulQA (target).
        Measure:
        - Coverage: % of test samples where true label is in prediction set
        - FPR: False positive rate (flagging correct as incorrect)
        - Transfer gap: |AUROC_target - AUROC_source|
        """
        # Apply source threshold to target dataset
        target_scores = []
        target_labels = []
        for x, y_true in self.target_data:
            pred_probs = model.predict_proba(x)
            nonconformity = 1.0 - pred_probs[y_true]
            target_scores.append(nonconformity)
            target_labels.append(y_true)
        
        # Prediction set: include label if nonconformity <= threshold
        prediction_sets = [score <= self.source_threshold for score in target_scores]
        
        # Coverage: % where true label is in prediction set
        coverage = np.mean(prediction_sets)
        
        # AUROC on target
        incorrectness = (np.array(target_labels) == 0).astype(int)  # 1 if wrong, 0 if correct
        auroc_target = roc_auc_score(y_true=incorrectness, y_score=target_scores)
        
        return {
            "coverage": coverage,
            "target_coverage": 1 - self.alpha,  # Expected coverage
            "auroc_target": auroc_target,
            "transfer_success": abs(coverage - (1 - self.alpha)) < 0.10  # Within 10% margin
        }


# Integration: Validate UQ mechanism pipeline end-to-end
# 1. Load h-e1 uncertainty scores (6 methods)
# 2. Compute Spearman, AUROC, AUSE for each method
# 3. Check gate: All non-degenerate methods pass ρ > 0.2 OR AUROC > 0.55
# 4. Test cross-dataset calibration: HaluEval → TruthfulQA
```

### Training Protocol

**No Training Required** - Reusing pretrained Llama-3.1-8B-Instruct from h-e1.

**Calibration Phase** (reuse h-e1 artifacts):
- Temperature Scaling: Reuse fitted T from h-e1
- Conformal Prediction: Reuse (1-α) quantile from h-e1
- MC Dropout: Reuse k forward passes from h-e1

**NEW: Cross-Dataset Calibration Test**:
- Calibrate conformal prediction on HaluEval QA split (~10k samples)
- Transfer threshold to TruthfulQA test split (~490 questions)
- Measure coverage, FPR, AUROC transfer gap

### Evaluation

**Primary Metrics** (Mechanism Validation):

1. **Spearman Rank Correlation (ρ)**
   - Task: Correlation between uncertainty and incorrectness
   - Input: Uncertainty scores (per method), binary incorrectness (0 if correct, 1 if wrong)
   - Computation: `spearmanr(uncertainty, incorrectness)`
   - Success Threshold: ρ > 0.2 for non-degenerate methods
   - **NOTE**: arxiv/2405.04278 discourages Spearman for small test sets (unstable). Include AUSE as robust alternative.

2. **AUROC (Area Under ROC Curve)**
   - Task: Binary classification (correct vs incorrect using uncertainty as discriminator)
   - Input: Uncertainty scores, binary incorrectness labels
   - Computation: `roc_auc_score(y_true=incorrectness, y_score=uncertainty)`
   - Success Threshold: AUROC > 0.55 for non-degenerate methods (above random + margin)

3. **AUSE (Area Under Sparsification Error)** - NEW
   - Task: Robust alternative to Spearman (recommended by arxiv/2405.04278)
   - Input: Uncertainty scores, incorrectness labels
   - Computation: Sort by uncertainty, remove high-uncertainty samples incrementally, measure error on remaining
   - Success Threshold: AUSE < Oracle_AUSE (oracle = sorted by true error)
   - **Justification**: More stable than Spearman for n=490 test samples

**Secondary Metrics** (Cross-Dataset Generalization):

4. **Conformal Prediction Coverage Transfer**
   - Task: Test HaluEval calibration → TruthfulQA coverage
   - Input: Conformal threshold from HaluEval, TruthfulQA test set
   - Computation: % of TruthfulQA samples where true label is in prediction set
   - Success Threshold: Coverage within Δ=0.10 of target (e.g., 90% ± 10%)

5. **AUROC Transfer Gap**
   - Task: Measure domain shift (HaluEval → TruthfulQA)
   - Input: AUROC on HaluEval (source), AUROC on TruthfulQA (target)
   - Computation: |AUROC_target - AUROC_source|
   - Success Threshold: Transfer gap < 0.10 (conformal prediction transfers well)

**Evaluation Protocol**:
1. Load h-e1 uncertainty scores (6 methods × 490 test questions)
2. Compute incorrectness labels: 1 if model wrong, 0 if correct
3. For each method:
   - Compute Spearman ρ between uncertainty and incorrectness
   - Compute AUROC using uncertainty as discriminator
   - Compute AUSE (sparsification curve)
4. Gate check: All non-degenerate methods (exclude MC k=1) must pass ρ > 0.2 OR AUROC > 0.55
5. Cross-dataset test:
   - Calibrate conformal prediction on HaluEval QA (~10k samples)
   - Apply threshold to TruthfulQA test (490 questions)
   - Measure coverage, AUROC transfer gap
6. **Fail fast**: If ≥2 non-degenerate methods fail gate → STOP, mechanism broken

**Ground Truth Labels**:
- Source: Human annotations in TruthfulQA.csv (correct_answers field)
- Binary: correct=0 (low uncertainty expected), incorrect=1 (high uncertainty expected)

**Metrics Loading Information** (for Phase 4 implementation):
```python
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
import numpy as np

# Spearman correlation
rho, p_value = spearmanr(uncertainty_scores, incorrectness_labels)

# AUROC
auroc = roc_auc_score(y_true=incorrectness_labels, y_score=uncertainty_scores)

# AUSE (sparsification)
sorted_indices = np.argsort(uncertainty_scores)[::-1]  # Descending
fractions = np.linspace(0, 1, 10)
errors = []
for frac in fractions:
    n_remove = int(frac * len(uncertainty_scores))
    remaining = sorted_indices[n_remove:]
    errors.append(incorrectness_labels[remaining].mean() if len(remaining) > 0 else 1.0)
ause = np.trapz(errors, fractions)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spearman ρ vs AUROC scatter plot (6 methods)
  - X-axis: Spearman ρ
  - Y-axis: AUROC
  - Horizontal line: AUROC threshold (0.55)
  - Vertical line: Spearman threshold (0.2)
  - Quadrants: Pass gate (top-right), Fail gate (other quadrants)
  - Color: MC k=1 (gray, degenerate), Others (colored by method)

#### Additional Figures (LLM Autonomous)

**Figure 1: Spearman Correlation Comparison** (bar chart)
- X-axis: UQ methods (6 levels)
- Y-axis: Spearman ρ (-1.0 to 1.0 range)
- Horizontal line: Success threshold (0.2)
- Error bars: Standard error (if multiple seeds from h-e1)
- Purpose: Show which methods achieve positive correlation

**Figure 2: AUSE vs AUROC** (scatter plot)
- X-axis: AUSE (lower is better)
- Y-axis: AUROC (higher is better)
- Diagonal: Ideal trade-off line
- Points: 6 UQ methods
- Purpose: Compare AUSE (robust) vs AUROC (traditional)

**Figure 3: Sparsification Curves** (line plot, 6 subplots)
- One subplot per UQ method
- X-axis: Fraction of samples removed (0 to 1)
- Y-axis: Error on remaining samples (0 to 1)
- Two lines per subplot: Oracle (sorted by true error) vs Method (sorted by uncertainty)
- Purpose: Visualize uncertainty-error correlation mechanism

**Figure 4: Cross-Dataset Calibration Transfer** (2-panel figure)
- Panel A: Coverage comparison (bar chart)
  - X-axis: Dataset (HaluEval source, TruthfulQA target)
  - Y-axis: Coverage (0 to 1)
  - Horizontal line: Target coverage (1-α = 0.90)
  - Purpose: Show if calibration transfers
- Panel B: AUROC Transfer Gap (bar chart)
  - X-axis: Method (conformal prediction only)
  - Y-axis: AUROC (source vs target)
  - Two bars: HaluEval (blue), TruthfulQA (orange)
  - Purpose: Quantify domain shift

All figures saved to `{hypothesis_folder}/figures/` with filenames: `gate_metrics_scatter.png`, `spearman_comparison.png`, `ause_vs_auroc.png`, `sparsification_curves.png`, `cross_dataset_calibration.png`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. All non-degenerate methods (5 out of 6, excluding MC k=1) pass gate:
   - Spearman ρ > 0.2 OR AUROC > 0.55
3. Conformal prediction coverage transfers to TruthfulQA within Δ=0.10 of target

**PoC Fail Conditions** (STOP experiment):
- IF ≥2 non-degenerate methods fail both Spearman ρ ≤ 0.2 AND AUROC ≤ 0.55 → Mechanism does not work at 8B scale
- IF conformal prediction coverage on TruthfulQA < 0.70 → Cross-dataset transfer fails critically (DQ4 violated)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**No relevant sources found** - Archon KB indexed primarily for vision/generative models, not NLP uncertainty quantification.

**Queries Executed**:
- Query 1: "uncertainty correlation correctness pipeline validation" → Diffusion models only
- Query 2: "Spearman correlation uncertainty scores LLM" → LLM papers but no code
- Query 3: "HaluEval calibration cross-dataset transfer" → Dataset descriptions, no transfer code

**Gap Identified**: Archon lacks UQ mechanism validation code. Relied on Exa GitHub search instead.

### B. GitHub Implementations (Exa)

**Repository 1: deeplearning-wisc/agentuq**
- **URL**: https://github.com/deeplearning-wisc/agentuq
- **Query Used**: "uncertainty correlation Spearman AUROC mechanism validation Python implementation"
- **Relevance**: UQ evaluation framework with AUROC, Spearman, AUARC metrics
- **Used For**: Spearman + AUROC computation pattern
- **Key Code**:
  ```python
  # AUROC: can uncertainty rank failures above successes?
  auroc = (sum_ranks_pos - n_fail * (n_fail + 1) / 2) / (n_fail * n_success)
  
  # Spearman: rank correlation
  spearman_rho, _ = spearmanr(uncertainty, incorrectness)
  ```

**Repository 2: dionysus/uncertainty_metrics.py**
- **URL**: https://github.com/aspuru-guzik-group/dionysus/blob/main/dionysus/uncertainty_metrics.py
- **Query Used**: "uncertainty correlation Spearman AUROC mechanism validation Python implementation"
- **Relevance**: Production-quality uncertainty metrics (classification + regression)
- **Used For**: RegressionSpearman, ClassificationSpearman, AUROC implementations
- **Key Code**:
  ```python
  class RegressionSpearman(AbstractRegressionMetric):
      def compute(self, y_true, y_pred, y_err):
          ae = np.abs(y_true - y_pred)
          res, _ = spearmanr(ae.ravel(), y_err.ravel())
          return res
  ```

**Repository 3: BetaConform (OpenReview)**
- **URL**: https://openreview.net/pdf?id=SsHCyEBMLz
- **Query Used**: "cross-dataset calibration transfer HaluEval TruthfulQA conformal prediction"
- **Relevance**: Conformal calibration transfer using text similarity
- **Used For**: Cross-dataset calibration pattern (HaluEval → TruthfulQA)
- **Key Results**: 10 samples from TruthfulQA → 37% accuracy gauge for LLM ensemble judge
- **Method**: Text embedding similarity determines transfer weight

**Repository 4: foadnamjoo/truthfulqa-audit**
- **URL**: https://github.com/foadnamjoo/truthfulqa-audit
- **Query Used**: "cross-dataset calibration transfer HaluEval TruthfulQA conformal prediction"
- **Relevance**: Cross-dataset audits (FEVER, BoolQ, HaluEval, TruthfulQA)
- **Used For**: Domain-conditional calibration pattern
- **Key Results**:
  - Global Platt scaling: ECE 0.080 → 0.014
  - Domain-conditional Platt: ECE 0.009, AUROC 0.835
- **Cross-dataset script**: `scripts/run_fever_audit.py`

**Repository 5: arxiv/2512.15068**
- **URL**: https://arxiv.org/pdf/2512.15068
- **Query Used**: "cross-dataset calibration transfer HaluEval TruthfulQA conformal prediction"
- **Relevance**: Conformal prediction for RAG hallucination detection
- **Used For**: HaluEval calibration protocol (n=629 samples)
- **Key Results**:
  - Natural Questions: 95% coverage, 0% FPR
  - HaluEval: 100% FPR (failure on real hallucinations)
- **Calibration**:
  ```python
  calibration_set = {(x_i, r_i, y_i)} for i in 1..629
  threshold = np.quantile(scores, 1 - alpha)  # alpha=0.05
  ```

**Repository 6: Novartis/UNIQUE**
- **URL**: https://github.com/Novartis/UNIQUE
- **Query Used**: "uncertainty correlation Spearman AUROC mechanism validation Python implementation"
- **Relevance**: UQ benchmarking library for ML models
- **Used For**: Multi-method UQ evaluation pattern
- **Features**: Combines UQ methods, evaluates via ranking-based + calibration metrics

**Repository 7: arxiv/2405.04278** (CRITICAL - Spearman Warning)
- **URL**: https://arxiv.org/html/2405.04278
- **Query Used**: "uncertainty correlation Spearman AUROC mechanism validation Python implementation"
- **Relevance**: Comparative study of UQ metrics (AUSE, CE, Spearman, NLL)
- **Used For**: AUSE implementation + Spearman stability warning
- **Key Findings**:
  - **Spearman**: Unstable for small test sets, converges to zero as n grows → DISCOURAGED
  - **AUSE**: Robust replacement for Spearman (recommended)
  - **CE**: Most stable and interpretable
- **Recommendation**: "We discourage the usage of Spearman's Rank Correlation for evaluating uncertainties and recommend replacing it with AUSE."

**Repository 8: VeriTrust-AI**
- **URL**: https://doi.org/10.1109/icdsaai69492.2026.11505140
- **Query Used**: "cross-dataset calibration transfer HaluEval TruthfulQA conformal prediction"
- **Relevance**: MC Dropout + NLI for LLM hallucination detection
- **Used For**: HaluEval benchmark results (state-of-the-art)
- **Key Results**: Accuracy 98.10% ± 0.08, F1 0.981, ECE 0.041
- **Method**: MC Dropout predictive entropy + NLI consistency

### C. Papers Referenced (from Phase 2B + Exa)

**Guo et al. 2017**: "On Calibration of Modern Neural Networks" (Temperature Scaling)
- Used in h-e1, reused in h-m-integrated

**Kumar et al. 2023**: Conformal Prediction (distribution-free coverage guarantees)
- Cross-dataset calibration test (HaluEval → TruthfulQA)

**Curran 2014**: "Estimating the Confidence of Conditional Random Fields" (Spearman with bootstrapping)
- arxiv/1411.3816 - Monte Carlo Spearman's rank correlation

**Ilg et al. 2018**: "Uncertainty Estimates and Multi-Hypotheses Networks for Optical Flow" (AUSE metric)
- Area Under Sparsification Error - robust alternative to Spearman

**Lin et al. 2021**: "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
- Primary evaluation dataset (reused from h-e1)

**Li et al. 2023**: "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models"
- Cross-dataset calibration source (10k samples, QA/Dialog/Summarization splits)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20T03:05:42.583373+00:00

### Workflow History for This Hypothesis

**Event 1**: Hypothesis h-m-integrated set to IN_PROGRESS
- Timestamp: 2026-08-20T03:05:42.583373+00:00
- Phase: Hypothesis Loop
- Details: External loop starting Phase 2C → 3 → 4 for h-m-integrated

**Event 2**: Phase 2C Experiment Design Started
- Timestamp: 2026-08-20 (current session)
- Phase: Phase 2C
- Status: Completed successfully
- Output: 02c_experiment_brief.md (this document)

---

*MCP Tools Used: Archon (Knowledge Base), Exa (GitHub search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
