# Experiment Design: H-M4

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Under the SSI formulation (SSI = 1/variance), if confidence variance correlates with contamination, then SSI will serve as a valid contamination metric, because the inverse transform amplifies differences in variance into a usable signal.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Validates SSI metric formulation as contamination signal

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m3 PASS: r=-0.517, d=0.58)
**Gate Status:** SHOULD_WORK (not yet triggered)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** h-m3

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** AUC > 0.7 for SSI-based classification; r > 0.6 between contamination % and mean SSI
- **Fail Action:** EXPLORE alternative metric (entropy-based)

---

## Continuation Context

This experiment builds on validated H-M3 results showing correlation between representation invariance and confidence uniformity (r=-0.517). H-M4 validates that SSI = 1/variance transforms this into a usable contamination detection metric.

### Previous Hypothesis Results

| Hypothesis | Result | Key Metric |
|------------|--------|------------|
| H-E1 | PASS | Asymmetry ratio 5.07x |
| H-M1 | PASS | Effect size 31.1% at 50% contamination |
| H-M2 | PASS | MPS difference 0.065, d=0.52 |
| H-M3 | PASS | r=-0.517, d=0.58 |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable. Using roadmap knowledge.*

SSI metric based on inverse variance transform:
- SSI = 1 / variance(confidence_scores)
- Higher SSI indicates more uniform confidence across paraphrases
- Contaminated items expected to show higher SSI

### Archon Code Examples

*MCP unavailable.*

Standard implementation pattern:
```python
def compute_ssi(confidence_scores: np.ndarray) -> float:
    """SSI = 1 / variance with numerical stability."""
    variance = np.var(confidence_scores)
    return 1.0 / (variance + 1e-8)  # epsilon for stability
```

### Exa GitHub Implementations

*MCP unavailable.*

Relevant patterns from contamination detection literature:
- sklearn.metrics.roc_auc_score for AUC computation
- scipy.stats.pearsonr for correlation analysis
- numpy variance computation with ddof=0 or ddof=1

### Implementation Priority Assessment

**Primary:** Custom SSI computation using numpy + sklearn metrics
**Fallback:** N/A (simple metric, no external dependencies)
**Justification:** SSI is novel metric defined in this work, no prior implementations to reference

### Code Analysis (Serena MCP)

*MCP unavailable. Serena analysis skipped.*

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | MMLU |
| Version | Standard test set |
| Size | 14,042 items |
| Type | standard |
| Source | https://github.com/hendrycks/test |
| Splits | Full test set for evaluation |
| Preprocessing | None (use raw questions) |
| Augmentation | K=20 paraphrases per item (from H-E1/H-M1) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`, `all`, split=`test`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("cais/mmlu", "all", split="test")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| Architecture | Mistral-7B-v0.1 |
| Source | huggingface.co/mistralai/Mistral-7B-v0.1 |
| Contamination Levels | 0%, 5%, 10%, 20%, 50% |
| Note | Reuse checkpoints from H-M1/H-M2/H-M3 |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `mistralai/Mistral-7B-v0.1`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

#### Proposed Model

**Architecture:** SSI metric computation on top of confidence extraction pipeline

**Core Mechanism Implementation:**

```python
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import pearsonr

def compute_ssi(confidence_scores: np.ndarray, epsilon: float = 1e-8) -> float:
    """
    Compute Semantic Saturation Index for a single item.
    
    Args:
        confidence_scores: Array of shape (K,) with confidence for K paraphrases
        epsilon: Numerical stability constant
    
    Returns:
        SSI value (higher = more uniform confidence = more contaminated)
    """
    variance = np.var(confidence_scores, ddof=0)
    ssi = 1.0 / (variance + epsilon)
    return ssi

def compute_ssi_batch(confidence_matrix: np.ndarray) -> np.ndarray:
    """
    Compute SSI for batch of items.
    
    Args:
        confidence_matrix: Shape (N_items, K_paraphrases)
    
    Returns:
        SSI values for each item, shape (N_items,)
    """
    variances = np.var(confidence_matrix, axis=1, ddof=0)
    ssi_values = 1.0 / (variances + 1e-8)
    return ssi_values

def evaluate_ssi_discrimination(
    ssi_clean: np.ndarray,
    ssi_contaminated: np.ndarray,
    contamination_levels: np.ndarray,
    mean_ssi_per_level: np.ndarray
) -> dict:
    """
    Evaluate SSI as contamination metric.
    
    Returns:
        dict with AUC and Pearson r
    """
    # Binary classification: clean (0) vs contaminated (1)
    y_true = np.concatenate([np.zeros(len(ssi_clean)), np.ones(len(ssi_contaminated))])
    y_scores = np.concatenate([ssi_clean, ssi_contaminated])
    auc = roc_auc_score(y_true, y_scores)
    
    # Correlation between contamination level and mean SSI
    r, p_value = pearsonr(contamination_levels, mean_ssi_per_level)
    
    return {
        "auc": auc,
        "pearson_r": r,
        "p_value": p_value,
        "primary_pass": auc > 0.7,
        "secondary_pass": r > 0.6
    }
```

### Training Protocol

**No training required for H-M4.** This experiment uses checkpoints from H-M1/H-M2/H-M3.

| Aspect | Value |
|--------|-------|
| Training | None (inference only) |
| Checkpoints | Reuse from H-M1 (5 contamination levels) |
| Paraphrases | Reuse from H-E1 (K=20 per item) |
| Confidence extraction | Extract from checkpoints on paraphrased items |

### Evaluation

| Metric | Purpose | Success Threshold |
|--------|---------|-------------------|
| AUC (ROC) | SSI discriminates contaminated from clean | > 0.7 |
| Pearson r | Contamination level correlates with mean SSI | > 0.6 |
| Effect Size (Cohen's d) | Practical significance | > 0.5 |
| Monotonicity | SSI increases with contamination | Yes |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification, correlation
- Library: sklearn.metrics, scipy.stats
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import pearsonr, ttest_ind
import numpy as np

# AUC computation
auc = roc_auc_score(y_true, ssi_scores)

# Pearson correlation
r, p = pearsonr(contamination_levels, mean_ssi_values)

# Effect size
d = (np.mean(ssi_contaminated) - np.mean(ssi_clean)) / np.sqrt(
    (np.var(ssi_contaminated) + np.var(ssi_clean)) / 2
)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: AUC and Pearson r vs thresholds bar chart

#### Additional Figures (LLM Autonomous)

1. **SSI Distribution Plot**: Violin/box plot of SSI by contamination level
2. **ROC Curve**: SSI-based classification ROC with AUC annotation
3. **Correlation Scatter**: Mean SSI vs contamination % with regression line
4. **SSI Heatmap**: Item-wise SSI across contamination levels

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. AUC > 0.7 for SSI-based contamination classification
3. Pearson r > 0.6 between contamination % and mean SSI

**Gate Logic:**
- PASS: Both primary (AUC > 0.7) and secondary (r > 0.6) met
- PARTIAL: Primary met, secondary not met (proceed with caution)
- FAIL: Primary not met → EXPLORE alternative metric formulation

---

## Appendix: Reference Implementations

### SSI Computation
```python
# From roadmap specification
ssi = 1.0 / (variance + epsilon)
```

### AUC Evaluation Pattern
```python
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(labels, scores)
```

### Correlation Analysis Pattern
```python
from scipy.stats import pearsonr
r, p = pearsonr(x, y)
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M4 set to IN_PROGRESS (external loop)
- Prerequisites: H-M3 PASS (r=-0.517, d=0.58)
- Next: Phase 3 implementation planning

---

*MCP Tools Used: None (MCP unavailable in this session)*
*All specifications grounded in Phase 2B roadmap and prior hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*
