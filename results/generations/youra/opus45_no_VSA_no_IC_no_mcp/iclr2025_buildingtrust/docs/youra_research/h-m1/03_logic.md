# Logic Document: H-M1

**Hypothesis:** Calibration moderates truthfulness-robustness correlation
**Date:** 2026-08-28

---

## 1. Core Algorithms

### 1.1 ECE Computation

```python
def compute_ece(
    confidences: np.ndarray,  # [N] float in [0,1]
    predictions: np.ndarray,  # [N] int class indices
    labels: np.ndarray,       # [N] int ground truth
    n_bins: int = 15
) -> float:
    """
    Expected Calibration Error (15-bin).
    
    Returns:
        ECE in [0, 1], lower = better calibrated
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
        if in_bin.sum() == 0:
            continue
        bin_acc = (predictions[in_bin] == labels[in_bin]).mean()
        bin_conf = confidences[in_bin].mean()
        ece += (in_bin.sum() / len(labels)) * abs(bin_acc - bin_conf)
    
    return ece
```

**Tensor shapes:**
- Input: confidences [N], predictions [N], labels [N]
- Output: scalar float

### 1.2 Fisher Z-Test

```python
def fisher_z_test(
    r1: float,  # Correlation 1
    n1: int,    # Sample size 1
    r2: float,  # Correlation 2
    n2: int     # Sample size 2
) -> tuple[float, float]:
    """
    Compare two Pearson correlations.
    
    Returns:
        (z_statistic, p_value_two_tailed)
    """
    # Fisher z-transform
    z1 = 0.5 * np.log((1 + r1) / (1 - r1))
    z2 = 0.5 * np.log((1 + r2) / (1 - r2))
    
    # Standard error
    se = np.sqrt(1/(n1-3) + 1/(n2-3))
    
    # Test statistic
    z_stat = (z1 - z2) / se
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    return z_stat, p_value
```

### 1.3 Tertile Moderation

```python
def tertile_moderation_test(
    ece_scores: np.ndarray,       # [M] ECE per model
    truthfulqa_scores: np.ndarray, # [M] TruthfulQA acc
    advglue_scores: np.ndarray     # [M] AdvGLUE acc
) -> dict:
    """
    Test if calibration moderates TruthfulQA-AdvGLUE correlation.
    
    Returns:
        {
            "low_ece_r": float,
            "high_ece_r": float,
            "fisher_z": float,
            "fisher_p": float,
            "moderation_detected": bool
        }
    """
    n = len(ece_scores)
    sorted_idx = np.argsort(ece_scores)
    tertile_size = n // 3
    
    low_idx = sorted_idx[:tertile_size]
    high_idx = sorted_idx[-tertile_size:]
    
    r_low, _ = pearsonr(truthfulqa_scores[low_idx], advglue_scores[low_idx])
    r_high, _ = pearsonr(truthfulqa_scores[high_idx], advglue_scores[high_idx])
    
    z, p = fisher_z_test(r_low, len(low_idx), r_high, len(high_idx))
    
    return {
        "low_ece_r": r_low,
        "high_ece_r": r_high,
        "fisher_z": z,
        "fisher_p": p,
        "moderation_detected": (r_low > r_high) and (p < 0.05)
    }
```

### 1.4 ECE-Metric Correlations

```python
def correlate_ece_with_metrics(
    ece_scores: np.ndarray,
    truthfulqa_scores: np.ndarray,
    advglue_scores: np.ndarray,
    log_params: np.ndarray
) -> dict:
    """
    Partial correlations controlling for model size.
    
    Gate conditions:
        - r < -0.2 for both
        - p < 0.10 for both
    """
    r_tqa, p_tqa = partial_corr(ece_scores, truthfulqa_scores, log_params)
    r_adv, p_adv = partial_corr(ece_scores, advglue_scores, log_params)
    
    return {
        "ece_vs_truthfulqa": {"r": r_tqa, "p": p_tqa},
        "ece_vs_advglue": {"r": r_adv, "p": p_adv},
        "gate_1_pass": r_tqa < -0.2 and p_tqa < 0.10,
        "gate_2_pass": r_adv < -0.2 and p_adv < 0.10
    }
```

## 2. API Signatures

| Function | Input Types | Output Type |
|----------|-------------|-------------|
| `compute_ece` | ndarray[N], ndarray[N], ndarray[N], int | float |
| `fisher_z_test` | float, int, float, int | tuple[float, float] |
| `tertile_moderation_test` | ndarray[M], ndarray[M], ndarray[M] | dict |
| `correlate_ece_with_metrics` | ndarray[M], ndarray[M], ndarray[M], ndarray[M] | dict |
| `partial_corr` | ndarray[M], ndarray[M], ndarray[M] | tuple[float, float] |

## 3. Reuse from H-E1

```python
# Import directly from h-e1
import sys
sys.path.insert(0, "../h-e1/code")
from analysis import partial_corr, bootstrap_ci, residualize
from config import MODELS, SEED
```

## 4. Edge Cases

| Case | Handling |
|------|----------|
| Empty bin in ECE | Skip, weight = 0 |
| r = ±1 in Fisher z | Clip to ±0.999 |
| Tertile size < 3 | Warning, low statistical power |
| Missing model data | Exclude from analysis |

---

*Logic spec for MECHANISM hypothesis implementation*
