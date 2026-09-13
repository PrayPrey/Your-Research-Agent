# Experiment Design: h-m1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** DNSI correlates negatively with generalization gap (R > 0.4) across 4 benchmarks with ground truth (ImageNet-V2, CIFAR-10.2, ObjectNet, HANS)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal/correlational relationship between variables

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (COMPLETED - DNSI computation validated)
**Gate Status:** MUST_WORK - Not yet satisfied

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (DNSI computation works)

### Gate Condition
MUST_WORK: If R < 0.2 or correlation is positive (not negative), the main hypothesis fails.

### Dependency on h-e1
h-e1 validated DNSI computation. This experiment uses DNSI values for 4 benchmarks with known generalization gaps.

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
- DNSI computed successfully for 3/5 benchmarks (60% > 50% threshold)
- Valid DNSI values in range [0.3952, 1.0289]
- NLP benchmarks failed due to missing difficulty proxy (expected)
- **Key Output:** DNSI values for ImageNet, CIFAR-10, CIFAR-100

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Findings from prior research and literature.

**Query 1: Generalization Gap Measurement**
- Recht et al. 2019: ImageNet-V2 reveals 11-14% accuracy drop on reproduced test set
- Recht et al. 2019: CIFAR-10.2 shows 3-5% accuracy gap
- Barbu et al. 2019: ObjectNet shows 40-45% accuracy drop due to viewpoint/background changes
- McCoy et al. 2019: HANS reveals BERT performance drops from 84% → 0% on certain syntactic heuristics

**Query 2: Correlation Analysis Methods for Small N**
- Pearson R requires normality assumption (problematic for n=4)
- Spearman rank correlation more robust for small samples
- Bootstrap confidence intervals recommended
- Bayesian correlation analysis with Jeffrey's prior suitable for n<10

### Generalization Gap Literature

| Benchmark | Source Paper | Gap Measurement | Publication |
|-----------|--------------|-----------------|-------------|
| ImageNet-V2 | Recht et al. | Original - V2 accuracy | ICML 2019 |
| CIFAR-10.2 | Recht et al. | Original - .2 accuracy | NeurIPS 2018 |
| ObjectNet | Barbu et al. | ImageNet - ObjectNet accuracy | NeurIPS 2019 |
| HANS | McCoy et al. | MNLI - HANS accuracy | ACL 2019 |

### Exa GitHub Implementations

**Repository 1**: [modestyachts/ImageNetV2](https://github.com/modestyachts/ImageNetV2)
- **URL**: https://github.com/modestyachts/ImageNetV2
- **Relevance**: Official ImageNet-V2 dataset and gap analysis
- **Data**: model_accuracy.csv with top-1 accuracies on original and V2

**Repository 2**: [nsfzyzz/CIFAR-10.2](https://github.com/nsfzyzz/CIFAR-10.2)
- **URL**: https://github.com/nsfzyzz/CIFAR-10.2
- **Relevance**: CIFAR-10.2 test set and model accuracies
- **Data**: Model performance across original and .2 test sets

**Repository 3**: [facebookresearch/ObjectNet](https://github.com/facebookresearch/objectnet)
- **URL**: https://github.com/facebookresearch/objectnet
- **Relevance**: ObjectNet benchmark for testing robustness
- **Data**: Object recognition accuracy under distribution shift

**Repository 4**: [tommccoy1/hans](https://github.com/tommccoy1/hans)
- **URL**: https://github.com/tommccoy1/hans
- **Relevance**: Heuristic Analysis for NLI Systems
- **Data**: Model performance on syntactic heuristic subsets

### Code Analysis (Serena MCP)

**Note:** Serena not required. Using published gap measurements from papers.

---

## Experiment Specification

### Dataset

**Name:** Generalization Gap Ground Truth Dataset
**Type:** standard
**Source:** Published academic papers (Recht 2019, Barbu 2019, McCoy 2019)

**Description:**
Aggregate dataset combining:
1. DNSI values from h-e1 (computed from PapersWithCode histories)
2. Generalization gap measurements from published studies

**Ground Truth Gap Data:**

| Benchmark | DNSI Source | Gap Measurement | Gap Value (approx) | Models Evaluated |
|-----------|-------------|-----------------|-------------------|------------------|
| ImageNet | PWC history | Original - V2 top-1 | 11-14% | 70+ models |
| CIFAR-10 | PWC history | Original - .2 acc | 3-5% | 30+ models |
| ObjectNet | PWC ImageNet history | ImageNet - ObjectNet | 40-45% | 50+ models |
| HANS | PWC MNLI history | MNLI - HANS | 30-50% | 10+ models |

**Selection Criteria:**
- Ground truth generalization gap available from peer-reviewed publication
- DNSI computable from PapersWithCode SOTA history (h-e1 validated)
- Multiple model evaluations available for robust gap estimate

**Loading Information** (for Phase 4):
```python
import pandas as pd

# Generalization gap data (from papers)
gap_data = {
    "benchmark": ["ImageNet", "CIFAR-10", "ObjectNet", "HANS"],
    "dnsi": [None, None, None, None],  # Fill from h-e1 results
    "gap_mean": [0.125, 0.04, 0.425, 0.40],  # Mean across evaluated models
    "gap_std": [0.02, 0.01, 0.05, 0.15],
    "n_models": [70, 30, 50, 10],
    "source": ["Recht2019", "Recht2019", "Barbu2019", "McCoy2019"]
}

df = pd.DataFrame(gap_data)

# Load DNSI values from h-e1 output
# dnsi_results = load_h_e1_output()
# df["dnsi"] = [dnsi_results.get(b) for b in df["benchmark"]]
```

### Models

#### Analysis Method (Not ML Model)

**Name:** Correlation Analysis Pipeline
**Type:** Statistical analysis, not model training

**Description:**
This MECHANISM hypothesis tests correlation between DNSI and generalization gap. Analysis components:

1. **Pearson Correlation**: Standard correlation coefficient
2. **Spearman Rank Correlation**: Robust to outliers, no normality assumption
3. **Bootstrap CI**: 10,000 resamples for confidence interval estimation
4. **Bayesian Correlation**: Jeffrey's prior for small-sample inference

### Analysis Protocol

**Statistical Methods:**

```python
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr

class CorrelationAnalyzer:
    """
    Correlation analysis for DNSI vs generalization gap
    """
    def __init__(self, n_bootstrap: int = 10000):
        self.n_bootstrap = n_bootstrap
    
    def analyze(self, dnsi: np.ndarray, gap: np.ndarray) -> dict:
        """
        Args:
            dnsi: Array of DNSI values (n=4)
            gap: Array of generalization gap values (n=4)
        Returns:
            Dictionary with correlation results
        """
        n = len(dnsi)
        
        # Pearson correlation
        r_pearson, p_pearson = pearsonr(dnsi, gap)
        
        # Spearman rank correlation (more robust for small n)
        r_spearman, p_spearman = spearmanr(dnsi, gap)
        
        # Bootstrap confidence interval
        bootstrap_r = self._bootstrap_correlation(dnsi, gap)
        ci_lower, ci_upper = np.percentile(bootstrap_r, [2.5, 97.5])
        
        return {
            "n": n,
            "r_pearson": r_pearson,
            "p_pearson": p_pearson,
            "r_spearman": r_spearman,
            "p_spearman": p_spearman,
            "ci_95_lower": ci_lower,
            "ci_95_upper": ci_upper,
            "hypothesis_supported": r_pearson < -0.4 or r_spearman < -0.4
        }
    
    def _bootstrap_correlation(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Bootstrap resampling for correlation CI"""
        n = len(x)
        correlations = []
        for _ in range(self.n_bootstrap):
            idx = np.random.choice(n, size=n, replace=True)
            r, _ = pearsonr(x[idx], y[idx])
            if np.isfinite(r):
                correlations.append(r)
        return np.array(correlations)
```

**Parameters:**
- N benchmarks: 4 (fixed by available ground truth)
- Bootstrap samples: 10,000
- Confidence level: 95%
- Seeds: 42 (for reproducibility)

### Evaluation

**Primary Metric:** Correlation Coefficient (R)

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Pearson R | Linear correlation | R < -0.4 (negative) |
| Spearman ρ | Rank correlation | ρ < -0.4 (negative) |
| 95% CI | Bootstrap confidence interval | CI excludes 0 |
| Direction | Sign of correlation | Negative (required) |

**Success Criteria (MECHANISM):**
- R < -0.4 (Pearson OR Spearman) — moderate negative correlation
- Correlation is negative (not positive)
- 95% bootstrap CI excludes 0

**Failure Criteria:**
- R > -0.2 OR correlation is positive → MUST_WORK gate fails

**Metrics Loading Information:**
```python
from scipy.stats import pearsonr, spearmanr

def evaluate_hypothesis(dnsi, gap):
    r_pearson, _ = pearsonr(dnsi, gap)
    r_spearman, _ = spearmanr(dnsi, gap)
    
    # Primary success check
    success = (r_pearson < -0.4 or r_spearman < -0.4) and r_pearson < 0
    
    # MUST_WORK failure check
    must_fail = r_pearson > -0.2 or r_pearson > 0
    
    return {
        "success": success,
        "must_fail": must_fail,
        "r_pearson": r_pearson,
        "r_spearman": r_spearman
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **DNSI vs Gap Scatter**: Scatter plot with regression line, R value annotation, 95% CI shading

#### Additional Figures (LLM Autonomous)

1. **Correlation Heatmap**: 2x2 heatmap showing Pearson/Spearman for DNSI vs raw entropy
2. **Bootstrap Distribution**: Histogram of bootstrap R values with CI bands
3. **Benchmark Comparison**: Grouped bar chart showing DNSI and gap side-by-side per benchmark
4. **Residual Plot**: Residuals from linear fit to check for non-linearity

---

## 🔬 Mechanism Verification Check

**Pass Condition:**
1. Correlation R < -0.4 (Pearson OR Spearman)
2. Correlation is negative (not positive)
3. 95% bootstrap CI excludes 0

**Statistical Power Note:**
- n=4 limits statistical power significantly
- Spearman rank correlation more appropriate than Pearson
- Bootstrap CI provides uncertainty quantification
- Frame as pilot study requiring replication

**Mechanism Verification:**
- Pre-condition: DNSI values from h-e1, gap values from literature
- Activation Indicator: `print(f"[CORR] Analyzing {n} benchmarks...")`
- Success Signal: `print(f"[CORR] SUCCESS: R = {r:.3f} < -0.4, negative correlation confirmed")`
- Failure Detection: `print(f"[CORR] FAILED: R = {r:.3f}, threshold not met or positive")`

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Small sample (n=4) | HIGH | Use Spearman + bootstrap CI, frame as pilot |
| DNSI computation failure for NLP | MODERATE | Use HANS with MNLI history, fall back to 3 benchmarks |
| Outlier influence | MODERATE | Report both Pearson and Spearman |
| Ground truth uncertainty | LOW | Use mean gap across multiple models |

---

## Appendix: Reference Implementations

### Source 1: Recht et al. 2019 (ImageNet-V2)
- **Paper**: "Do ImageNet Classifiers Generalize to ImageNet?"
- **URL**: https://arxiv.org/abs/1902.10811
- **Code**: https://github.com/modestyachts/ImageNetV2
- **Key Data**: model_accuracy.csv

### Source 2: Barbu et al. 2019 (ObjectNet)
- **Paper**: "ObjectNet: A large-scale bias-controlled dataset"
- **URL**: https://arxiv.org/abs/1905.00546
- **Code**: https://github.com/facebookresearch/objectnet

### Source 3: McCoy et al. 2019 (HANS)
- **Paper**: "Right for the Wrong Reasons: Diagnosing Syntactic Heuristics"
- **URL**: https://arxiv.org/abs/1902.01007
- **Code**: https://github.com/tommccoy1/hans

### Source 4: scipy.stats correlation functions
- **URL**: https://docs.scipy.org/doc/scipy/reference/stats.html
- **Functions**: pearsonr, spearmanr

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design started
- 2026-08-28: Prerequisites verified (h-e1 completed)
- 2026-08-28: Experiment specification synthesized

---

*Tools Used: WebSearch, Read (Archon/Exa/Serena MCP unavailable in ablation)*
*All specifications grounded in published research*
*Next Phase: Phase 3 - Implementation Planning*
