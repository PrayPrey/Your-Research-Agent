# Experiment Design: H-M3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under the quality-diversity tradeoff, an optimal balance point exists where quality and diversity are maximized, with measurable peak in dose-response curve
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Identifying optimal curation threshold via dose-response peak analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 completed with INCONCLUSIVE result)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2

### Gate Condition
SHOULD_WORK: Optimal peak should be identifiable within p20-p80 range (not at boundary). If fails: DOCUMENT (plateau may exist instead of peak).

---

## Continuation Context

H-M2 established deduplication mechanism but was INCONCLUSIVE due to lm-eval integration failure. H-M3 focuses on **perplexity filtering** threshold sweep to identify optimal balance point. This hypothesis uses EXISTING sweep data from H-E1/H-M2 plus additional targeted threshold analysis.

### Key Insight from H-M2
- Deduplication mechanism verified
- Training loss shows expected quality-diversity tradeoff pattern
- Benchmark evaluation requires proper lm-eval integration (fixed for H-M3)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Findings from established literature:

**Query 1: Optimal Threshold Identification**
- **DataComp (2023)**: CLIP filtering optima identified via systematic sweeps
- **Polynomial regression**: Quadratic/cubic model selection via AIC/BIC
- **Peak finding**: First derivative = 0, second derivative < 0
- **Confidence intervals**: Bootstrap resampling for threshold uncertainty

**Query 2: Dose-Response Curve Fitting**
- scipy.optimize.curve_fit for polynomial fitting
- numpy.polyfit for quick polynomial regression
- statsmodels for AIC/BIC model selection
- Standard approach: fit linear, quadratic, cubic; select best by information criterion

### Exa GitHub Implementations

**Repository 1**: [scipy/scipy](https://github.com/scipy/scipy)
- **URL**: https://github.com/scipy/scipy
- **Relevance**: optimize.curve_fit, find_peaks for threshold identification
- **Key Functions**: `scipy.signal.find_peaks`, `scipy.optimize.minimize_scalar`

**Repository 2**: [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels)
- **URL**: https://github.com/statsmodels/statsmodels
- **Relevance**: OLS regression with AIC/BIC model selection
- **Code**:
  ```python
  import statsmodels.api as sm
  model = sm.OLS(y, X).fit()
  print(model.aic, model.bic)
  ```

**Repository 3**: [EleutherAI/lm-evaluation-harness](https://github.com/eleutherai/lm-evaluation-harness)
- **URL**: https://github.com/eleutherai/lm-evaluation-harness
- **Relevance**: Benchmark evaluation for sweep points
- **Note**: v0.4+ requires `lm_eval.simple_evaluate()` API

---

## Experiment Specification

### Dataset

**Name:** RedPajama-v2 (subset)
**Type:** standard
**Source:** HuggingFace: togethercomputer/RedPajama-Data-v2

**Hypothesis Fit:**
- Pre-existing sweep data from H-E1/H-M2 available
- Full perplexity threshold sweep: none, p10, p20, ..., p90
- 10B tokens per configuration, 3 seeds

**Statistics:**
- Experiment subset: 10B tokens per configuration
- Sweep points: 10 perplexity thresholds
- Total training: 30 model runs (10 thresholds × 3 seeds)

**Loading Information:**
- Method: Reuse H-E1/H-M2 preprocessed data and checkpoints
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset(
      "togethercomputer/RedPajama-Data-v2",
      name="sample",
      split="train"
  )
  ```

### Models

#### Baseline Model

**Architecture:** GPT-2 125M (decoder-only transformer)
**Type:** Pretrained from scratch on filtered data
**Source:** HuggingFace Transformers

**Configuration:**
- Layers: 12
- Hidden size: 768
- Attention heads: 12
- Parameters: 125M
- Context length: 1024

**Loading Information:**
```python
from transformers import GPT2Config, GPT2LMHeadModel
config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12
)
model = GPT2LMHeadModel(config)
```

#### Proposed Model

**Architecture:** Same GPT-2 125M across all threshold configurations

**Core Mechanism Implementation:**

The mechanism is ANALYSIS of sweep data to identify optimal threshold. No new training required if H-E1 sweep data available.

```python
# Core Mechanism: Optimal Threshold Identification via Dose-Response Analysis
# Based on: scipy, statsmodels, numpy

import numpy as np
from scipy import optimize, signal
from scipy.stats import bootstrap
import statsmodels.api as sm
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class DoseResponseResult:
    """Results from dose-response curve fitting."""
    optimal_threshold: float
    optimal_score: float
    confidence_interval: Tuple[float, float]
    best_model: str  # 'linear', 'quadratic', 'cubic'
    aic_values: dict
    is_peak_internal: bool  # True if peak not at boundary

def fit_polynomial_models(
    thresholds: np.ndarray,  # e.g., [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    scores: np.ndarray,       # benchmark ensemble scores
    scores_std: np.ndarray    # std across seeds
) -> dict:
    """
    Fit linear, quadratic, cubic models and select best via AIC/BIC.
    
    Returns:
        Dict with model coefficients and information criteria
    """
    results = {}
    
    # Normalize thresholds to [0, 1] for numerical stability
    x = thresholds / 100.0
    y = scores
    
    for degree, name in [(1, 'linear'), (2, 'quadratic'), (3, 'cubic')]:
        X = np.vander(x, degree + 1)
        model = sm.OLS(y, X).fit()
        results[name] = {
            'coefficients': model.params,
            'aic': model.aic,
            'bic': model.bic,
            'rsquared': model.rsquared
        }
    
    return results

def find_optimal_threshold(
    thresholds: np.ndarray,
    scores: np.ndarray,
    model_coeffs: np.ndarray,
    degree: int
) -> Tuple[float, float, bool]:
    """
    Find peak via derivative analysis.
    
    Returns:
        (optimal_threshold, optimal_score, is_internal)
    """
    x = thresholds / 100.0
    
    if degree == 1:
        # Linear: no internal peak, return boundary
        idx = np.argmax(scores)
        return thresholds[idx], scores[idx], False
    
    # For quadratic: derivative = 2*a*x + b = 0 => x = -b/(2a)
    # For cubic: derivative = 3*a*x^2 + 2*b*x + c = 0
    poly = np.poly1d(model_coeffs)
    deriv = np.polyder(poly)
    
    # Find critical points
    critical = np.roots(deriv)
    critical = critical[np.isreal(critical)].real
    critical = critical[(critical >= 0) & (critical <= 1)]
    
    if len(critical) == 0:
        # No internal critical point, use boundary
        idx = np.argmax(scores)
        return thresholds[idx], scores[idx], False
    
    # Evaluate at critical points and boundaries
    candidates = np.concatenate([[0], critical, [1]])
    values = poly(candidates)
    best_idx = np.argmax(values)
    
    optimal_x = candidates[best_idx]
    optimal_threshold = optimal_x * 100
    optimal_score = values[best_idx]
    is_internal = (optimal_x > 0.05) and (optimal_x < 0.95)
    
    return optimal_threshold, optimal_score, is_internal

def compute_confidence_interval(
    thresholds: np.ndarray,
    scores_matrix: np.ndarray,  # shape: (n_thresholds, n_seeds)
    n_bootstrap: int = 1000
) -> Tuple[float, float]:
    """
    Bootstrap confidence interval for optimal threshold.
    
    Returns:
        (lower_bound, upper_bound) for 95% CI
    """
    n_thresholds, n_seeds = scores_matrix.shape
    optimal_thresholds = []
    
    for _ in range(n_bootstrap):
        # Resample seeds with replacement
        seed_indices = np.random.choice(n_seeds, n_seeds, replace=True)
        resampled = scores_matrix[:, seed_indices].mean(axis=1)
        
        # Find peak in resampled data
        idx = np.argmax(resampled)
        optimal_thresholds.append(thresholds[idx])
    
    lower = np.percentile(optimal_thresholds, 2.5)
    upper = np.percentile(optimal_thresholds, 97.5)
    
    return lower, upper

def analyze_dose_response(
    sweep_results: dict  # {threshold: {'scores': [s1, s2, s3], ...}}
) -> DoseResponseResult:
    """
    Full dose-response analysis pipeline.
    
    Args:
        sweep_results: Dict mapping threshold to seed scores
    
    Returns:
        DoseResponseResult with optimal threshold and analysis
    """
    thresholds = np.array(sorted(sweep_results.keys()))
    scores_matrix = np.array([
        sweep_results[t]['scores'] for t in thresholds
    ])
    
    mean_scores = scores_matrix.mean(axis=1)
    std_scores = scores_matrix.std(axis=1)
    
    # Fit models
    models = fit_polynomial_models(thresholds, mean_scores, std_scores)
    
    # Select best model by BIC (more conservative than AIC)
    best_model_name = min(models.keys(), key=lambda k: models[k]['bic'])
    best_model = models[best_model_name]
    
    # Find optimal threshold
    optimal_t, optimal_s, is_internal = find_optimal_threshold(
        thresholds, mean_scores,
        best_model['coefficients'],
        {'linear': 1, 'quadratic': 2, 'cubic': 3}[best_model_name]
    )
    
    # Confidence interval
    ci = compute_confidence_interval(thresholds, scores_matrix)
    
    return DoseResponseResult(
        optimal_threshold=optimal_t,
        optimal_score=optimal_s,
        confidence_interval=ci,
        best_model=best_model_name,
        aic_values={k: v['aic'] for k, v in models.items()},
        is_peak_internal=is_internal
    )
```

### Training Protocol

**Note:** H-M3 primarily analyzes existing sweep data from H-E1. If additional runs needed:

**Optimizer:** AdamW
- Parameters: β1=0.9, β2=0.95, weight_decay=0.1

**Learning Rate:** 6e-4

**Schedule:** Cosine decay with warmup
- Warmup steps: 2000

**Batch Size:** 512 sequences (512K tokens per batch)

**Epochs:** N/A (token-based)
- Total tokens: 10B per configuration

**Seeds:** 3 (for statistical robustness)

### Evaluation

**Primary Metrics:**
- Optimal threshold location (percentile)
- Benchmark Ensemble Score at optimum
- 95% CI width for optimal threshold
- Model selection (linear vs quadratic vs cubic)

**Success Criteria (MECHANISM hypothesis):**
- Primary: Peak identified within p20-p80 range (not at boundary)
- Secondary: 95% CI for peak spans ≤3 threshold levels (≤30 percentile points)

**Expected Findings:**
- Optimal threshold expected around p40-p60 based on DataComp analogy
- Quadratic or cubic model should outperform linear (AIC/BIC)

**Metrics Loading Information:**
```python
# Benchmark evaluation via lm-evaluation-harness
import lm_eval
results = lm_eval.simple_evaluate(
    model="hf",
    model_args="pretrained=./checkpoint",
    tasks=["hellaswag", "arc_easy", "piqa", "winogrande"],
    batch_size=16
)

# Ensemble score: PC1 or simple average
ensemble_score = np.mean([
    results['results'][task]['acc']
    for task in ['hellaswag', 'arc_easy', 'piqa', 'winogrande']
])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Dose-Response Curve**: Ensemble score (y) vs perplexity threshold (x), with fitted polynomial curve, optimal point marked, 95% CI shaded

#### Additional Figures (LLM Autonomous)

1. **Model Comparison**: AIC/BIC values for linear, quadratic, cubic fits
2. **Individual Benchmark Curves**: Per-benchmark dose-response curves
3. **Bootstrap Distribution**: Histogram of bootstrapped optimal thresholds
4. **Residual Plot**: Model fit quality assessment

> Phase 4 Coder MUST include figure generation logic.
> Figures saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: Yes - polynomial peak identification from dose-response data
- **mechanism_isolatable**: Yes - analysis is independent of model training
- **baseline_measurable**: Yes - linear model (no peak) is baseline

### Architecture Compatibility
Analysis-only hypothesis. Compatible with any sweep data format.

### Activation Indicators
- **Log message**: "Best model: {model_name}, Optimal threshold: {threshold}, CI: [{lower}, {upper}]"
- **Metric delta expected**: Internal peak (not at boundary) required for success

### Mechanism Verification Code
```python
def verify_optimal_balance_point(result: DoseResponseResult) -> bool:
    """
    Verify H-M3 success criteria.
    
    Success requires:
    1. Peak is internal (not at p0 or p90)
    2. Non-linear model selected (quadratic or cubic)
    3. CI width ≤ 30 percentile points
    """
    # Check 1: Internal peak
    if not result.is_peak_internal:
        print(f"FAIL: Peak at boundary ({result.optimal_threshold})")
        return False
    
    # Check 2: Non-linear model
    if result.best_model == 'linear':
        print("FAIL: Linear model selected (no dose-response curvature)")
        return False
    
    # Check 3: CI width
    ci_width = result.confidence_interval[1] - result.confidence_interval[0]
    if ci_width > 30:
        print(f"FAIL: CI too wide ({ci_width:.1f} > 30)")
        return False
    
    print(f"PASS: Optimal threshold = p{result.optimal_threshold:.0f}, "
          f"CI = [{result.confidence_interval[0]:.0f}, {result.confidence_interval[1]:.0f}], "
          f"Model = {result.best_model}")
    return True
```

### Success Threshold
- **hypothesis_support_threshold**: Peak within p20-p80, non-linear model selected, CI ≤ 30
- **hypothesis_support_metric**: is_peak_internal AND best_model != 'linear' AND ci_width <= 30

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Dose-response curve plotted with ≥5 threshold points
2. Polynomial regression completes for all three models
3. Optimal threshold identified (any location acceptable for PoC)
4. Verification: `analyze_dose_response(sweep_results)` returns valid result

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| scipy | https://github.com/scipy/scipy | Optimization, peak finding |
| statsmodels | https://github.com/statsmodels/statsmodels | AIC/BIC model selection |
| lm-evaluation-harness | https://github.com/eleutherai/lm-evaluation-harness | Benchmark evaluation |
| DataComp | https://arxiv.org/abs/2304.14108 | Precedent for curation optima |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design initiated
- Built on H-M2 deduplication sweep context
- Focus: perplexity threshold optimal point identification
- Core analysis: polynomial fitting + derivative-based peak finding

---

*MCP Tools Used: None (Archon/Exa unavailable)*
*Analysis-focused hypothesis using existing sweep data*
*Next Phase: Phase 3 - Implementation Planning*
