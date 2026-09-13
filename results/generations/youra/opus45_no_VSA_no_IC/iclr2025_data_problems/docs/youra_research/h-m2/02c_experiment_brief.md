# Experiment Design: h-m2

**Date:** 2026-08-24
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** Mode profiles exhibit dissociation: inter-method variance > intra-method variance (F-ratio > 4.0, Cohen's d > 0.5)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing whether attribution methods produce statistically distinguishable mode profiles using ANOVA F-ratio and Cohen's d effect size metrics.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (validated - different methods create different mode sensitivities)

### Gate Condition
MUST_WORK: If this fails (inter-method variance not significantly greater than intra-method variance), the core claim of method fingerprinting cannot be supported.

---

## Continuation Context

**Builds on h-m1 validated infrastructure:**
- 3 attribution methods (TRAK, TracIn, Kronfluence) successfully integrated
- 3 mode types (memorization, feature transfer, spurious) with probe pairs
- CIFAR-10 + ResNet-18 baseline established
- Mode sensitivity scores computed per method

### Previous Hypothesis Results (h-m1)
- All 3 attribution methods correctly integrated and produce non-trivial scores
- Mode sensitivity patterns differ observably across methods
- Probe construction validated (1000 pairs per mode)
- Runtime experiment confirmed code executes successfully

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query: "F-ratio Cohen d variance statistical dissociation"**
- Limited direct results for attribution method variance analysis
- General statistical methods well-documented in scipy/statsmodels

### Archon Code Examples

Limited direct matches for influence function comparison code.

### Exa GitHub Implementations

**Key Finding 1: scipy.stats.f_oneway**
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
- **Purpose**: One-way ANOVA computing F-statistic for group mean comparison
- **API**: `F, p = scipy.stats.f_oneway(group1, group2, group3)`
- **Returns**: F-statistic and p-value

**Key Finding 2: statsmodels.stats.oneway.effectsize_oneway**
- **URL**: https://www.statsmodels.org/devel/generated/statsmodels.stats.oneway.effectsize_oneway.html
- **Purpose**: Cohen's f (convertible to Cohen's d) for ANOVA effect size
- **API**: `f2 = effectsize_oneway(means, vars_, nobs, use_var="unequal")`

**Key Finding 3: TRAK Paper Benchmarking**
- **URL**: https://proceedings.mlr.press/v202/park23c.html
- **Method**: Linear Datamodeling Score (LDS) for attribution method comparison
- **Insight**: TRAK significantly outperforms TracIn (0.42 vs 0.09 MRR on fact tracing)
- **Implication**: Methods DO show measurable differences in behavior

**Key Finding 4: quanda Benchmark Framework**
- **URL**: https://quanda.readthedocs.io/
- **Purpose**: Standardized metrics for training data attribution evaluation
- **Includes**: Multiple evaluation metrics for comparing TDA methods

### 🎯 Implementation Priority Assessment

**h-m2 extends h-m1 with statistical dissociation analysis**

| Component | Source | Status |
|-----------|--------|--------|
| Attribution methods (TRAK, TracIn, Kronfluence) | h-m1 validated | Reuse |
| Mode probes (mem, transfer, spurious) | h-m1 validated | Reuse |
| F-ratio computation | scipy.stats.f_oneway | Standard |
| Cohen's d computation | Manual or pingouin | Standard |
| Variance decomposition | numpy/scipy | Standard |

**Recommended Implementation Path:**
- Primary: Extend h-m1 code with variance analysis module
- Fallback: N/A - scipy/numpy are stable
- Justification: Statistical tests are well-established; focus is on correct variance decomposition

### Code Analysis (Serena MCP)

Not performed - statistical methods from scipy/statsmodels are well-documented. h-m1 code provides the attribution score infrastructure.

---

## Experiment Specification

### Dataset

**Name:** CIFAR-10 (reused from h-m1)
**Type:** standard
**Source:** torchvision.datasets.CIFAR10
**Statistics:** 50,000 train / 10,000 test images, 10 classes, 32x32 RGB

**Contrastive Probes:** 1000 pairs per mode × 3 modes × 10 random seeds = 30,000 total probe evaluations
- **Memorization probes:** Near-duplicate train-test pairs (high pixel similarity)
- **Feature transfer probes:** Same-class pairs with different visual features
- **Spurious probes:** Pairs sharing spurious correlation (e.g., background color)

**Rationale for 10 seeds:** Intra-method variance requires multiple independent runs per method

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.datasets.CIFAR10`
- Code:
  ```python
  from torchvision.datasets import CIFAR10
  from torchvision import transforms
  
  transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
  ])
  train_dataset = CIFAR10(root='./data', train=True, download=True, transform=transform)
  test_dataset = CIFAR10(root='./data', train=False, download=True, transform=transform)
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-18 (reused from h-m1)
**Configuration:** 
- Output classes: 10
- Pretrained on ImageNet, fine-tuned on CIFAR-10
- 10 independent training runs with different seeds (for intra-method variance)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `torchvision.models.resnet18`
- Code:
  ```python
  import torch
  import torchvision.models as models
  
  def create_model(seed):
      torch.manual_seed(seed)
      model = models.resnet18(pretrained=True)
      model.fc = torch.nn.Linear(model.fc.in_features, 10)
      return model
  ```

#### Proposed Model

**Architecture:** Baseline + Variance Decomposition Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Dissociation Analysis via ANOVA
# Test whether inter-method variance > intra-method variance

import numpy as np
from scipy import stats
from typing import Dict, List

def compute_mode_profile(method_scores: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute normalized mode profile vector from raw influence scores.
    
    Args:
        method_scores: Dict mapping mode_name -> influence_scores array
    
    Returns:
        Normalized profile vector [mem_sensitivity, transfer_sensitivity, spurious_sensitivity]
    """
    profile = np.array([
        np.mean(method_scores['memorization']),
        np.mean(method_scores['feature_transfer']),
        np.mean(method_scores['spurious'])
    ])
    # Normalize to unit vector for fair comparison
    return profile / (np.linalg.norm(profile) + 1e-8)

def compute_dissociation_metrics(
    all_profiles: Dict[str, List[np.ndarray]],  # method -> list of profiles (one per seed)
    num_seeds: int = 10
) -> Dict[str, float]:
    """
    Compute F-ratio and Cohen's d for method dissociation.
    
    Args:
        all_profiles: {method_name: [profile_seed1, profile_seed2, ...]}
        num_seeds: Number of independent runs per method
    
    Returns:
        Dict with F_ratio, p_value, cohens_d, dissociation_confirmed
    """
    methods = list(all_profiles.keys())  # ['trak', 'tracin', 'kronfluence']
    
    # Stack all profiles for ANOVA: shape (3 methods × num_seeds, 3 modes)
    profiles_by_method = [np.array(all_profiles[m]) for m in methods]
    
    # Compute inter-method variance (between-group)
    method_means = [np.mean(profiles, axis=0) for profiles in profiles_by_method]
    grand_mean = np.mean(np.vstack(profiles_by_method), axis=0)
    ss_between = sum(
        len(profiles) * np.sum((mean - grand_mean)**2)
        for profiles, mean in zip(profiles_by_method, method_means)
    )
    df_between = len(methods) - 1  # 2
    
    # Compute intra-method variance (within-group)
    ss_within = sum(
        np.sum((profiles - mean)**2)
        for profiles, mean in zip(profiles_by_method, method_means)
    )
    df_within = sum(len(p) - 1 for p in profiles_by_method)  # 3 * (10-1) = 27
    
    # F-ratio
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    F_ratio = ms_between / (ms_within + 1e-8)
    
    # P-value from F-distribution
    p_value = 1 - stats.f.cdf(F_ratio, df_between, df_within)
    
    # Cohen's d: effect size for largest pairwise difference
    cohens_d_values = []
    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            if i < j:
                profiles1 = np.array(all_profiles[m1])
                profiles2 = np.array(all_profiles[m2])
                # Pool for each mode dimension, take max
                for mode_idx in range(3):
                    mean_diff = abs(np.mean(profiles1[:, mode_idx]) - np.mean(profiles2[:, mode_idx]))
                    pooled_std = np.sqrt(
                        (np.var(profiles1[:, mode_idx]) + np.var(profiles2[:, mode_idx])) / 2
                    )
                    if pooled_std > 0:
                        cohens_d_values.append(mean_diff / pooled_std)
    
    cohens_d = max(cohens_d_values) if cohens_d_values else 0.0
    
    return {
        'F_ratio': F_ratio,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'ss_between': ss_between,
        'ss_within': ss_within,
        'dissociation_confirmed': (F_ratio > 4.0) and (cohens_d > 0.5)
    }

# Integration: Run after collecting profiles from multiple seeds per method
```

### Training Protocol

**Model Training (10 seeds per method):**
- **Optimizer:** SGD (momentum=0.9, weight_decay=5e-4)
- **Learning Rate:** 0.1 with cosine annealing
- **Batch Size:** 128
- **Epochs:** 200
- **Loss:** CrossEntropyLoss
- **Seeds:** [42, 123, 456, 789, 1000, 1111, 2222, 3333, 4444, 5555]

**Attribution Computation (per seed):**
- Compute influence for 1000 probes per mode (3 modes = 3000 probes)
- Run all 3 methods on same probes
- Compute mode profile vector per method per seed
- Total: 3 methods × 10 seeds × 3000 probes = 90,000 influence computations

**Variance Analysis:**
- Collect 10 mode profiles per method (30 total profiles)
- Run ANOVA to compute F-ratio
- Compute pairwise Cohen's d for all method pairs

**Sources:** scipy.stats.f_oneway documentation, TRAK paper benchmarking methodology

### Evaluation

**Primary Metrics:**
- **F-ratio:** Inter-method variance / intra-method variance (target: > 4.0)
- **Cohen's d:** Effect size for maximum pairwise method difference (target: > 0.5)
- **p-value:** Statistical significance of F-ratio (target: < 0.05)

**Success Criteria (MECHANISM hypothesis - h-m2):**
- F-ratio > 4.0: Methods differ more than random variation
- Cohen's d > 0.5: Medium-to-large practical effect size
- p-value < 0.05: Statistically significant at conventional threshold

**Expected Baseline Performance:**
- Random attribution: F-ratio ≈ 1.0 (no systematic difference)
- Methods should cluster by method identity, not by random seed

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: variance analysis / ANOVA
- Library: scipy.stats, numpy
- Code:
  ```python
  from scipy import stats
  import numpy as np
  
  # One-way ANOVA across methods
  F, p = stats.f_oneway(trak_profiles, tracin_profiles, kron_profiles)
  
  # Cohen's d (manual computation)
  def cohens_d(group1, group2):
      n1, n2 = len(group1), len(group2)
      pooled_std = np.sqrt(((n1-1)*np.var(group1) + (n2-1)*np.var(group2)) / (n1+n2-2))
      return (np.mean(group1) - np.mean(group2)) / pooled_std
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing F-ratio vs 4.0 threshold and Cohen's d vs 0.5 threshold

#### Additional Figures (LLM Autonomous)
- Mode profile scatter plot (3D: mem × transfer × spurious) with method clustering
- Intra-method vs inter-method variance box plot
- Pairwise Cohen's d heatmap (3×3 method comparison)
- Profile distribution per method (violin plots)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions:**
- mechanism_exists: True (h-m1 proved different sensitivities exist)
- mechanism_isolatable: True (each method runs independently with controlled seeds)
- baseline_measurable: True (F-ratio ≈ 1.0 for random/identical methods)

**Architecture Compatibility:**
- All methods from h-m1 remain compatible
- Multiple seeds require multiple training runs (parallelizable)
- Variance computation is standard numpy/scipy

**Activation Indicators:**
- mechanism_log_message: "Dissociation analysis: F={F_ratio:.2f}, d={cohens_d:.2f}"
- tensor_shape_change: Profile arrays shape = (num_methods, num_seeds, 3)
- metric_delta_expected: F-ratio >> 1.0 if methods truly dissociate

**Verification Code:**
```python
def verify_dissociation(results: dict) -> bool:
    """Verify h-m2 gate conditions are met."""
    # Gate 1: F-ratio > 4.0
    f_pass = results['F_ratio'] > 4.0
    
    # Gate 2: Cohen's d > 0.5
    d_pass = results['cohens_d'] > 0.5
    
    # Gate 3: Statistical significance
    p_pass = results['p_value'] < 0.05
    
    print(f"F-ratio: {results['F_ratio']:.2f} ({'PASS' if f_pass else 'FAIL'})")
    print(f"Cohen's d: {results['cohens_d']:.2f} ({'PASS' if d_pass else 'FAIL'})")
    print(f"p-value: {results['p_value']:.4f} ({'PASS' if p_pass else 'FAIL'})")
    
    return f_pass and d_pass
```

**Hypothesis Support:**
- threshold: F-ratio > 4.0 AND Cohen's d > 0.5
- metric: Variance ratio (between/within) and effect size

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 3 methods × 10 seeds
2. F-ratio > 4.0 (inter-method variance dominates)
3. Cohen's d > 0.5 (medium-to-large effect size)

---

## Appendix: Reference Implementations

### A. Statistical Methods

**scipy.stats.f_oneway**
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
- **Used For**: One-way ANOVA F-statistic computation

**statsmodels.stats.oneway.effectsize_oneway**
- **URL**: https://www.statsmodels.org/devel/generated/statsmodels.stats.oneway.effectsize_oneway.html
- **Used For**: Cohen's f effect size (convertible to d)

### B. Attribution Method Comparison Precedent

**TRAK Paper (Park et al., 2023)**
- **URL**: https://proceedings.mlr.press/v202/park23c.html
- **Finding**: TRAK significantly outperforms TracIn on benchmarks
- **Implication**: Methods DO produce measurably different results

### C. GitHub Implementations (from h-m1)

**Repository 1**: MadryLab/trak
- **URL**: https://github.com/MadryLab/trak
- **Used For**: TRAK attribution scores

**Repository 2**: pomonam/kronfluence
- **URL**: https://github.com/pomonam/kronfluence
- **Used For**: Kronfluence attribution scores

**Repository 3**: KuchikiRenji/Empirical-Influence-Function
- **URL**: https://github.com/KuchikiRenji/Empirical-Influence-Function
- **Used For**: TracIn attribution scores

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| ANOVA F-ratio | Standard | scipy.stats.f_oneway |
| Cohen's d | Standard | Manual computation / pingouin |
| Attribution methods | h-m1 validated | TRAK, TracIn, Kronfluence |
| Dataset | h-m1 validated | CIFAR-10 |
| Model | h-m1 validated | ResNet-18 |
| Multiple seeds design | Research | Standard variance estimation |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design started for h-m2
- 2026-08-24: Loaded continuation context from h-m1 (VALIDATED)
- 2026-08-24: MCP research completed (scipy ANOVA, statsmodels effect size)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
