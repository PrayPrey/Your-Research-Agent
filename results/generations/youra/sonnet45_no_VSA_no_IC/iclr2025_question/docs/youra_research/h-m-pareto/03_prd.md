# Product Requirements Document: h-m-pareto

**Date:** 2026-08-20  
**Author:** yoon303b@gmail.com  
**Hypothesis:** h-m-pareto (Pareto frontier analysis for UQ methods)  
**Phase:** 3 - Implementation Planning

---

## Executive Summary

Construct empirical Pareto frontier from (cost, AUROC) pairs across 6 UQ methods to test whether cost-performance trade-offs exist in selective prediction. Success: ≥2 Pareto-optimal methods (no universal dominance).

---

## Problem Statement

### Research Context
- **Prerequisite:** h-m-integrated validated that all UQ methods produce valid uncertainty rankings (AUROC > 0.55, Spearman ρ > 0.2)
- **Open Question:** Do different UQ mechanisms operate in distinct efficiency zones, or does one method universally dominate?
- **Scientific Value:** Both outcomes advance understanding:
  - |Pareto_set| ≥ 2: Trade-offs exist → practitioners can choose based on budget
  - |Pareto_set| = 1: Universal dominance → always use highest-cost method

### Hypothesis Statement
Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then at least 2 methods are Pareto-optimal (no method strictly dominates another with p < 0.05), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones.

**Gate:** SHOULD_WORK (non-blocking - negative result is scientifically valuable)

---

## Success Criteria

### Primary Metrics
1. **Pareto Set Size:** |Pareto_set| ≥ 2 (H3: trade-off exists)
2. **AUROC Threshold:** All methods AUROC ≥ 0.55 (validation check from h-m-integrated)
3. **Statistical Rigor:** Dominance determined via paired t-test (α=0.05, n=3 seeds)

### Secondary Metrics
1. **H1:** MC dropout k=5 achieves highest AUROC (≥ 0.70)
2. **H2:** Temperature scaling competitive (|AUROC_temp - AUROC_mc_k5| ≤ 0.05)
3. **Spearman ρ:** All methods > 0.2 (uncertainty correlates with incorrectness)

### Failure Modes
- **False Negative:** Low power (n=3 seeds) masks real trade-offs → report visual inspection
- **False Positive:** High variance obscures dominance → require AUROC gap > 0.05 for practical significance

---

## Technical Requirements

### Core Components

#### 1. Calibration Module
**Purpose:** Optimize temperature scaling and conformal prediction hyperparameters on HaluEval

**Inputs:**
- HaluEval calibration set (~10k samples)
- Llama-3.1-8B-Instruct model outputs (logits)

**Outputs:**
- Optimal temperature T_opt (expected range: 1.5-3.0)
- Conformal threshold τ (90% coverage @ α=0.1)

**Implementation:**
```python
def calibrate_temperature(model, cal_dataset):
    """Grid search T ∈ [0.5, 5.0] to minimize NLL"""
    pass

def calibrate_conformal(model, cal_dataset, alpha=0.1):
    """Compute α-quantile threshold for 90% coverage"""
    pass
```

#### 2. UQ Methods Module
**Purpose:** Generate uncertainty scores for 6 methods on TruthfulQA

**Methods:**
1. Temperature Scaling: 1× cost (post-hoc)
2. Conformal Prediction: 1× cost (post-hoc)
3. MC Dropout k=1,3,5,10: k× cost (k forward passes)

**Outputs:**
- Uncertainty scores (higher = more uncertain)
- Predictions (text strings)
- Cost multiplier (relative to 1× baseline)

**Implementation Pattern:**
```python
def apply_temp_scaling(model, dataset, temperature):
    """Apply T_opt to softmax, uncertainty = 1 - max(softmax)"""
    pass

def apply_mc_dropout(model, dataset, n_passes):
    """Enable dropout, run k passes, uncertainty = variance"""
    pass
```

#### 3. AUROC Computation Module
**Purpose:** Evaluate uncertainty quality via selective prediction AUROC

**Inputs:**
- Uncertainty scores (6 methods × 3 seeds × 817 questions)
- Correctness labels (fuzzy match against TruthfulQA correct_answers)

**Outputs:**
- AUROC per (method, seed) pair
- Aggregated: (AUROC_mean, AUROC_std) per method

**Implementation:**
```python
from sklearn.metrics import roc_auc_score

def compute_auroc(uncertainty_scores, correctness_labels):
    """Binary classification: correct vs incorrect predictions"""
    return roc_auc_score(y_true=correctness_labels, y_score=uncertainty_scores)
```

#### 4. Pareto Frontier Module
**Purpose:** Identify non-dominated methods via dominance check

**Algorithm:**
- For each method i:
  - Check if any method j satisfies: cost_j ≤ cost_i AND auroc_j > auroc_i (p < 0.05)
  - If no j dominates i, add i to Pareto set

**Statistical Test:**
- Paired t-test on AUROC samples (generated from mean/std)
- Conservative: n=3 seeds → low power → only detect large differences

**Implementation:**
```python
def construct_pareto_frontier(results, alpha=0.05):
    """
    Args:
        results: Dict[method, (cost, auroc_mean, auroc_std)]
    Returns:
        pareto_set: List of Pareto-optimal method names
    """
    pass
```

---

## Data Requirements

### Datasets

**TruthfulQA (Test Set):**
- Source: HuggingFace `truthfulqa/truthful_qa`
- Config: `generation` (not multiple_choice)
- Split: `validation` (817 examples)
- Fields: question, best_answer, correct_answers, incorrect_answers, category

**HaluEval (Calibration Set):**
- Source: HuggingFace (hallucination evaluation benchmark)
- Size: ~10k samples
- Purpose: Calibration only (temperature/conformal hyperparameters)

### Model

**Llama-3.1-8B-Instruct:**
- Source: HuggingFace `meta-llama/Llama-3.1-8B-Instruct`
- Access: Requires Meta license + HF token
- Precision: bfloat16
- Device: auto (GPU if available)

**Modifications:**
- Enable dropout for MC dropout: `model.config.use_cache = False`, dropout layers active
- No architecture changes (frozen baseline)

---

## Deliverables

### Code Artifacts
1. `calibration.py`: Temperature scaling + conformal prediction calibration
2. `uq_methods.py`: All 6 UQ method implementations
3. `pareto_analysis.py`: Frontier construction + dominance check
4. `evaluation.py`: AUROC computation + correctness labeling
5. `main.py`: Orchestration script (calibration → inference → analysis)

### Data Artifacts
1. `results/calibration.json`: T_opt, τ values
2. `results/auroc_scores.json`: (method, seed) AUROC pairs
3. `results/pareto_frontier.json`: Pareto set + dominated methods

### Visualizations (in `figures/`)
1. `pareto_frontier.png`: (cost, AUROC) scatter with Pareto-optimal highlighted
2. `auroc_bar_chart.png`: AUROC mean ± std with significance brackets
3. `cost_vs_auroc_tradeoff.png`: Trade-off curves per method
4. `spearman_heatmap.png`: Correlation validation (all methods > 0.2)

### Documentation
1. `04_validation.md`: Results, interpretation, next steps
2. `04_checkpoint.yaml`: Updated state with validation.result

---

## Implementation Constraints

### Budget
- **Computational:** MC dropout k=10 most expensive (10× baseline × 817 questions × 3 seeds)
- **Time:** Estimated 2-4 hours for full pipeline (calibration + inference + analysis)
- **Memory:** 8B model requires ~16GB VRAM (bfloat16)

### Dependencies
- PyTorch, transformers (Llama model)
- sklearn (AUROC, metrics)
- scipy (paired t-test, Spearman)
- HuggingFace datasets (TruthfulQA, HaluEval)

### Reproducibility
- Fixed seeds: 42, 123, 456
- Deterministic: `torch.manual_seed(seed)`, `torch.backends.cudnn.deterministic = True`
- Cache model outputs for efficiency (avoid recomputing base predictions)

---

## Risks & Mitigation

### Risk 1: Low Statistical Power
**Issue:** n=3 seeds insufficient for paired t-test (requires n~20 for 80% power)  
**Mitigation:** Report visual inspection of scatter plot, require AUROC gap > 0.10 for claims  
**Impact:** Conservative results (real trade-offs may exist but not statistically significant)

### Risk 2: Correctness Labeling Noise
**Issue:** Fuzzy matching against `correct_answers` may introduce false positives/negatives  
**Mitigation:** Use strict substring matching, manual inspection of edge cases  
**Impact:** AUROC estimates noisier → wider confidence intervals

### Risk 3: HaluEval Calibration Mismatch
**Issue:** HaluEval domain differs from TruthfulQA → calibration may not transfer  
**Mitigation:** Report calibration vs test AUROC gap, consider TruthfulQA subset for calibration  
**Impact:** Temperature scaling / conformal may underperform

---

## Acceptance Criteria

### Minimum Viable Implementation
1. All 6 UQ methods produce uncertainty scores on TruthfulQA (817 questions × 3 seeds)
2. AUROC computed for all 18 (method, seed) pairs
3. Pareto frontier constructed with statistical dominance check
4. Primary figure (Pareto scatter plot) generated

### Full Implementation
1. Calibration on HaluEval completes (T_opt, τ validated)
2. Spearman ρ > 0.2 for all methods (validation check)
3. All 4 visualizations generated with publication-quality labels
4. 04_validation.md documents results + interpretation
5. State updated: `validation.result = PASSED/FAILED`, `completed = true`

---

## Appendix: Reference Implementations

### Primary Libraries
1. **TorchCP:** Conformal prediction (LAC, APS, RAPS, temperature scaling)
2. **sklearn.metrics:** AUROC computation
3. **scipy.stats:** Paired t-test, Spearman correlation

### Benchmarks
1. **retinal-selective-prediction:** MC dropout T=30 → AURC 0.0756 (best), temp scaling → ECE 0.146→0.055
2. **TS4CP:** Temperature scaling + conformal trade-off analysis (ICML paper)

### Implementation Priority
1. **Library** (TorchCP) for conformal prediction
2. **Manual** for MC dropout (enable model dropout layers)
3. **sklearn** for AUROC (standard, validated)

---

*Next Step: 03_architecture.md — System design and component integration*
