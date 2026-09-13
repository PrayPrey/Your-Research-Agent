# Experiment Design: h-m1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Calibration moderates the truthfulness-robustness correlation: low-ECE (well-calibrated) models show significantly stronger correlation than high-ECE models (Fisher z-test p < 0.05).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests whether calibration explains h-e1 correlation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED with r=0.8028, p=0.000548)
**Gate Status:** SHOULD_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (PASSED)

### Gate Condition
1. Negative correlation: ECE vs TruthfulQA MC1 (r < -0.2)
2. Negative correlation: ECE vs AdvGLUE avg (r < -0.2)
3. Both p < 0.10

### Updated Statement (per verification_plan h-m2 scope)
This experiment also tests moderation: low-ECE tertile should show stronger TruthfulQA-AdvGLUE correlation than high-ECE tertile (Fisher z-test p < 0.05).

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
- **Partial correlation:** r = 0.8028
- **p-value:** 0.000548
- **95% CI:** [0.0816, ...]
- **Models evaluated:** 14 across 4 families (Pythia, Llama-2, Mistral, Falcon)
- **Reusable artifacts:**
  - `h-e1/code/analysis.py` - partial_corr(), bootstrap_ci()
  - `h-e1/code/config.py` - MODEL definitions, thresholds
  - `h-e1/code/results/` - cached TruthfulQA + AdvGLUE scores

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** No Archon MCP available.

Standard ECE (Expected Calibration Error) computation:
1. Bin predictions by confidence (15 bins standard)
2. For each bin: |average_confidence - accuracy|
3. Weight by bin population

### Exa GitHub Implementations

**[INFERRED]** No Exa MCP available.

Key references:
1. **torchmetrics.CalibrationError** - PyTorch implementation
2. **netcal** library - calibration metrics
3. **uncertainty-baselines** (Google) - ECE computation

### Code Reuse from h-e1

```python
# From h-e1/code/analysis.py - reuse directly
from analysis import partial_corr, bootstrap_ci, residualize

# From h-e1/code/config.py - extend with ECE config
MODELS, N_BOOTSTRAP, SEED = ...  # Already defined
```

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| **Name** | MMLU (for ECE) + h-e1 cached scores |
| **Type** | standard |
| **Source** | HuggingFace Hub via lm-evaluation-harness |
| **MMLU Version** | mmlu (full validation set) |
| **Preprocessing** | None - use raw logits for ECE |
| **Sample Size** | Full MMLU validation (~14k questions) |

**Loading Information:**
```python
# ECE requires model logits, not just accuracy
# Use lm-eval with --log_samples flag
lm_eval --model hf \
  --model_args pretrained=MODEL_NAME \
  --tasks mmlu \
  --log_samples \
  --output_path results/

# Or direct HuggingFace:
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all", split="validation")
```

### Models

| Property | Value |
|----------|-------|
| **Sample Size** | Same 14 models from h-e1 |
| **Families** | Pythia, Llama-2, Mistral, Falcon |
| **Requirement** | Must have cached h-e1 scores |

**Model List:** Reuse h-e1/code/config.py MODELS

### Core Mechanism Implementation

#### ECE Computation

```python
import numpy as np
from typing import List, Tuple

def compute_ece(
    confidences: np.ndarray,
    predictions: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15
) -> float:
    """
    Compute Expected Calibration Error (15-bin).
    
    Args:
        confidences: Model confidence for predicted class [N]
        predictions: Predicted class indices [N]
        labels: Ground truth labels [N]
        n_bins: Number of calibration bins
    
    Returns:
        ECE score (lower is better calibrated)
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total = len(labels)
    
    for i in range(n_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        in_bin = (confidences > low) & (confidences <= high)
        
        if in_bin.sum() == 0:
            continue
            
        bin_conf = confidences[in_bin].mean()
        bin_acc = (predictions[in_bin] == labels[in_bin]).mean()
        bin_weight = in_bin.sum() / total
        
        ece += bin_weight * abs(bin_acc - bin_conf)
    
    return ece


def get_model_ece(model_id: str, mmlu_results_path: str) -> float:
    """Extract ECE from logged lm-eval samples."""
    import json
    
    with open(mmlu_results_path) as f:
        data = json.load(f)
    
    # Parse logged samples for confidences and correctness
    confidences = []
    corrects = []
    
    for sample in data.get("samples", {}).get("mmlu", []):
        # lm-eval logs logprobs; convert to confidence
        logprobs = sample.get("logprobs", [])
        if logprobs:
            probs = np.exp(logprobs)
            probs = probs / probs.sum()
            conf = probs.max()
            pred = probs.argmax()
            label = sample.get("target", 0)
            
            confidences.append(conf)
            corrects.append(int(pred == label))
    
    confidences = np.array(confidences)
    corrects = np.array(corrects)
    
    return compute_ece(confidences, corrects, corrects, n_bins=15)
```

#### Correlation Analysis

```python
from scipy.stats import pearsonr, norm
import numpy as np

def correlate_ece_with_metrics(
    ece_scores: np.ndarray,
    truthfulqa_scores: np.ndarray,
    advglue_scores: np.ndarray,
    log_params: np.ndarray
) -> dict:
    """
    Test H-M1: ECE should negatively correlate with both metrics.
    
    Success: r < -0.2 and p < 0.10 for both correlations.
    """
    # Import reusable partial_corr from h-e1
    from analysis import partial_corr
    
    # ECE vs TruthfulQA (controlling for size)
    r_tqa, p_tqa = partial_corr(ece_scores, truthfulqa_scores, log_params)
    
    # ECE vs AdvGLUE (controlling for size)
    r_adv, p_adv = partial_corr(ece_scores, advglue_scores, log_params)
    
    return {
        "ece_vs_truthfulqa": {"r": r_tqa, "p": p_tqa, "passes": r_tqa < -0.2 and p_tqa < 0.10},
        "ece_vs_advglue": {"r": r_adv, "p": p_adv, "passes": r_adv < -0.2 and p_adv < 0.10},
        "gate_passed": (r_tqa < -0.2 and p_tqa < 0.10) and (r_adv < -0.2 and p_adv < 0.10)
    }
```

#### Tertile Stratification + Fisher z-test

```python
from scipy.stats import pearsonr, norm
import numpy as np

def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> Tuple[float, float]:
    """
    Fisher's z-test to compare two correlation coefficients.
    
    Returns:
        z_statistic, p_value (two-tailed)
    """
    # Fisher z-transform
    z1 = 0.5 * np.log((1 + r1) / (1 - r1))
    z2 = 0.5 * np.log((1 + r2) / (1 - r2))
    
    # Standard error
    se = np.sqrt(1/(n1 - 3) + 1/(n2 - 3))
    
    # z-statistic
    z_stat = (z1 - z2) / se
    
    # Two-tailed p-value
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    return z_stat, p_value


def tertile_moderation_test(
    ece_scores: np.ndarray,
    truthfulqa_scores: np.ndarray,
    advglue_scores: np.ndarray
) -> dict:
    """
    Test moderation: low-ECE group should show stronger
    TruthfulQA-AdvGLUE correlation than high-ECE group.
    
    Success: Fisher z-test p < 0.05, low_r > high_r.
    """
    n = len(ece_scores)
    
    # Sort by ECE, split into tertiles
    sorted_idx = np.argsort(ece_scores)
    tertile_size = n // 3
    
    low_ece_idx = sorted_idx[:tertile_size]   # Best calibrated
    high_ece_idx = sorted_idx[-tertile_size:]  # Worst calibrated
    
    # Within-group correlations
    r_low, _ = pearsonr(
        truthfulqa_scores[low_ece_idx],
        advglue_scores[low_ece_idx]
    )
    r_high, _ = pearsonr(
        truthfulqa_scores[high_ece_idx],
        advglue_scores[high_ece_idx]
    )
    
    # Fisher z-test
    z_stat, p_value = fisher_z_test(
        r_low, len(low_ece_idx),
        r_high, len(high_ece_idx)
    )
    
    return {
        "low_ece_correlation": r_low,
        "high_ece_correlation": r_high,
        "difference": r_low - r_high,
        "fisher_z": z_stat,
        "fisher_p": p_value,
        "moderation_detected": r_low > r_high and p_value < 0.05,
        "n_per_tertile": tertile_size
    }
```

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **ECE-TruthfulQA r** | Partial correlation | r < -0.2 |
| **ECE-AdvGLUE r** | Partial correlation | r < -0.2 |
| **Both p-values** | Statistical significance | p < 0.10 |
| **Fisher z p** | Moderation test | p < 0.05 |
| **Direction** | Low-ECE r > High-ECE r | Positive difference |

**Gate Condition:** 
- Primary (h-m1): Both ECE correlations meet thresholds
- Secondary (moderation): Fisher z-test significant with correct direction

### Visualization Requirements

#### Required Figure (Mandatory)
- **ECE vs Metrics Dual Scatter**: Two panels showing ECE vs TruthfulQA and ECE vs AdvGLUE
  - X-axis: ECE (15-bin)
  - Y-axis: Metric accuracy
  - Regression line with CI band
  - Annotate partial r, p values

#### Additional Figures

1. **Calibration curve comparison**: Low-ECE vs High-ECE model calibration curves
2. **Tertile correlation comparison**: Bar chart of within-tertile correlations
3. **Fisher z-test visualization**: Confidence intervals for r_low vs r_high

---

## 🔬 Success Check

**Gate Pass Conditions:**
1. ECE vs TruthfulQA: r < -0.2, p < 0.10
2. ECE vs AdvGLUE: r < -0.2, p < 0.10
3. Moderation: low_ECE_r > high_ECE_r, Fisher p < 0.05

**If Gate Fails:**
- Calibration does not explain correlation
- Seek alternative mechanism (training data overlap, model architecture)

---

## Appendix: Reference Implementations

### Primary References

1. **Guo et al. (2017)** "On Calibration of Modern Neural Networks"
   - Introduced ECE metric
   - 15-bin standard

2. **netcal library**
   - URL: https://github.com/EFS-OpenSource/calibration-framework
   - Comprehensive calibration metrics

3. **torchmetrics.CalibrationError**
   - URL: https://torchmetrics.readthedocs.io/
   - PyTorch-native ECE

### Statistical Methods

4. **Fisher z-transformation**
   - Standard method for comparing correlations
   - scipy.stats provides building blocks

### Code Reuse

From h-e1:
- `analysis.py`: partial_corr, bootstrap_ci, residualize
- `config.py`: MODELS, N_BOOTSTRAP, SEED
- `results/`: Cached TruthfulQA + AdvGLUE scores

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- h-e1 validated with r=0.8028, p=0.000548
- 2026-08-28: Phase 2C experiment design initiated for h-m1

---

*MCP Tools Used: None (MCP unavailable)*
*Specifications grounded in standard calibration evaluation practices*
*Next Phase: Phase 3 - Implementation Planning*
