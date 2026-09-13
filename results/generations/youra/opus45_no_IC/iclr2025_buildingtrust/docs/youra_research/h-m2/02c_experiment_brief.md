# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Different confidence distributions require different temperature parameters for optimal calibration
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing whether optimal T varies across clusters

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASS, h-m1 PASS)
**Gate Status:** SHOULD_WORK - CV(optimal T) > 0.1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (PASS - 17/21 cluster pairs significantly different)

### Gate Condition
- **Type:** SHOULD_WORK
- **Condition:** Coefficient of variation of optimal T > 0.1, Range of T > 0.3
- **Fail Action:** EXPLORE (check regularization strength)

---

## Continuation Context

H-M1 confirmed that LLMs produce category-specific confidence distributions on TruthfulQA. 17/21 cluster pairs showed significantly different distributions (KS p<0.05). This establishes the premise for H-M2: if distributions differ, optimal temperature scaling parameters should also differ.

### Previous Hypothesis Results
- **H-E1:** PASS - ANOVA p=0.00012 confirms category-dependent ECE variation
- **H-M1:** PASS - KS test 17/21 pairs significant confirms different confidence distributions

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for temperature scaling calibration in KB. General resources on PyTorch optimization and CUDA numerics found but not directly applicable.

### Archon Code Examples

No calibration-specific code examples in KB. Diffusion-related guidance scale examples found but not applicable to temperature scaling calibration.

### Exa GitHub Implementations

**Primary Reference: gpleiss/temperature_scaling (canonical implementation)**
- URL: https://github.com/gpleiss/temperature_scaling
- Method: LBFGS optimizer minimizing NLL
- Key code pattern:
```python
class ModelWithTemperature(nn.Module):
    def __init__(self, model):
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
    
    def temperature_scale(self, logits):
        return logits / self.temperature
    
    def set_temperature(self, valid_loader):
        # Collect logits and labels
        optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=200)
        nll_criterion = nn.CrossEntropyLoss()
        optimizer.step(lambda: nll_criterion(self.temperature_scale(logits), labels))
```

**Secondary: TorchUncertainty TemperatureScaler**
- URL: https://torch-uncertainty.github.io/
- Includes VectorScaler (per-class temperature) and MatrixScaler
- Clean API: `scaled_model = TemperatureScaler(model); scaled_model.fit(dataloader)`

**Academic Reference: Class-based Temperature Scaling (Frenkel & Goldberger, EUSIPCO 2021)**
- URL: https://www.eurasip.org/Proceedings/Eusipco/Eusipco2021/pdfs/0001486.pdf
- Key insight: "Calibration error differs across classes, propose to calibrate each class separately"
- Validates our cluster-specific approach

### 🎯 Implementation Priority Assessment

**CRITICAL: Per-cluster temperature optimization requires:**
1. Cluster assignment from H-M1 results (7 clusters)
2. Per-cluster logit collection
3. Independent T optimization per cluster
4. Coefficient of variation calculation across optimal T values

**Recommended Implementation Path:**
- Primary: Adapt gpleiss/temperature_scaling for per-cluster optimization
- Fallback: scipy.optimize.minimize with NLL loss per cluster
- Justification: gpleiss implementation is canonical, well-tested, uses LBFGS which converges reliably

### Code Analysis (Serena MCP)

Not applicable - no existing codebase for this experiment.

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | TruthfulQA |
| **Type** | standard |
| **Source** | https://github.com/sylinrl/TruthfulQA |
| **Size** | 817 questions |
| **Clusters** | 7 semantic clusters (from 38 categories) |
| **Samples per cluster** | ~100-150 per cluster |
| **Split** | 5-fold CV (80/20 per cluster) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets or direct CSV
- Identifier: `truthful_qa` or `TruthfulQA.csv`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
# OR direct CSV
import pandas as pd
df = pd.read_csv("TruthfulQA.csv")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Architecture** | Llama-2-7B |
| **Source** | HuggingFace Hub |
| **Identifier** | meta-llama/Llama-2-7b-hf |
| **Purpose** | Extract logits for temperature scaling |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Per-cluster temperature scaling optimization

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax

def optimize_temperature_per_cluster(logits_by_cluster, labels_by_cluster):
    """
    Optimize temperature T for each cluster independently.
    
    Args:
        logits_by_cluster: dict {cluster_id: np.array [n_samples, n_classes]}
        labels_by_cluster: dict {cluster_id: np.array [n_samples]}
    
    Returns:
        optimal_temps: dict {cluster_id: float}
    """
    optimal_temps = {}
    
    for cluster_id in logits_by_cluster:
        logits = logits_by_cluster[cluster_id]
        labels = labels_by_cluster[cluster_id]
        
        def nll_loss(T):
            # Temperature scale logits
            scaled_logits = logits / T[0]
            probs = softmax(scaled_logits, axis=1)
            # Negative log likelihood
            nll = -np.mean(np.log(probs[np.arange(len(labels)), labels] + 1e-10))
            return nll
        
        # Optimize T using L-BFGS-B with bounds [0.1, 10]
        result = minimize(nll_loss, x0=[1.0], method='L-BFGS-B', 
                         bounds=[(0.1, 10.0)])
        optimal_temps[cluster_id] = result.x[0]
    
    return optimal_temps

def compute_temperature_variation(optimal_temps):
    """
    Compute coefficient of variation and range of optimal temperatures.
    
    Returns:
        cv: coefficient of variation (std/mean)
        t_range: max(T) - min(T)
    """
    temps = list(optimal_temps.values())
    mean_t = np.mean(temps)
    std_t = np.std(temps)
    cv = std_t / mean_t
    t_range = max(temps) - min(temps)
    return cv, t_range

# Gate condition check
def check_gate(optimal_temps):
    cv, t_range = compute_temperature_variation(optimal_temps)
    primary_pass = cv > 0.1
    secondary_pass = t_range > 0.3
    return primary_pass, secondary_pass, cv, t_range
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Optimization** | L-BFGS-B | Standard for temperature scaling (Guo et al., 2017) |
| **Loss** | Negative Log Likelihood | Minimizes miscalibration |
| **T bounds** | [0.1, 10.0] | Prevents degenerate solutions |
| **Initial T** | 1.0 | Neutral starting point |
| **CV folds** | 5 | Standard cross-validation |
| **Validation split** | 80/20 per cluster | Ensures per-cluster evaluation |

**Cross-Validation Protocol:**
1. For each of 5 folds:
   - Split each cluster 80/20 (train/val)
   - Optimize T per cluster on train fold
   - Record optimal T values
2. Aggregate T values across folds
3. Compute CV and range with confidence intervals

### Evaluation

| Metric | Definition | Gate Threshold |
|--------|------------|----------------|
| **CV(T)** | std(T)/mean(T) across clusters | > 0.1 (primary) |
| **Range(T)** | max(T) - min(T) | > 0.3 (secondary) |
| **Bootstrap CI** | 95% CI for CV and range | Report width |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Calibration parameter optimization
- Library: scipy.optimize, numpy
- Code:
```python
from scipy.optimize import minimize
import numpy as np

# CV calculation
cv = np.std(temps) / np.mean(temps)
t_range = np.max(temps) - np.min(temps)

# Bootstrap CI
from scipy.stats import bootstrap
ci = bootstrap((temps,), np.std, n_resamples=1000)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of optimal T per cluster with error bars

#### Additional Figures (LLM Autonomous)

1. **Temperature Distribution**: Box plot of optimal T across 5 CV folds for each cluster
2. **T vs Cluster**: Line plot showing optimal T variation across clusters
3. **CV Distribution**: Histogram of CV values across bootstrap samples

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. CV(optimal T) > 0.1 across clusters
3. Range(optimal T) > 0.3

**Expected Outcome:**
Given H-M1 showed 17/21 cluster pairs have significantly different confidence distributions, we expect optimal temperatures to differ meaningfully. If distributions differ, the confidence-accuracy relationship differs, requiring different scaling.

---

## Appendix: Reference Implementations

### Primary Reference
- **Repository:** gpleiss/temperature_scaling
- **URL:** https://github.com/gpleiss/temperature_scaling
- **Key pattern:** LBFGS optimization of single T parameter
- **Adaptation needed:** Loop over clusters, store per-cluster T

### Secondary Reference
- **Library:** TorchUncertainty
- **URL:** https://torch-uncertainty.github.io/
- **Feature:** VectorScaler provides per-class T (can adapt for per-cluster)

### Academic Reference
- **Paper:** "Network Calibration by Class-based Temperature Scaling"
- **Authors:** Frenkel & Goldberger (EUSIPCO 2021)
- **URL:** https://www.eurasip.org/Proceedings/Eusipco/Eusipco2021/pdfs/0001486.pdf
- **Relevance:** Validates that class/cluster-specific T improves calibration

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T18:30:00+00:00

### Workflow History for This Hypothesis
- H-E1: PASS - ANOVA p=0.00012 < 0.05
- H-M1: PASS - KS test 17/21 pairs significant
- H-M2: IN_PROGRESS - Experiment design complete

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
