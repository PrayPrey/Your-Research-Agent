# Experiment Design: h-c1

**Date:** 2026-08-24
**Author:** PrayPrey
**Hypothesis Statement:** Mode profiles are stable within methods: split-half reliability Cronbach's alpha > 0.8
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASS)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1
- **Type:** CONDITION
- **Prerequisites:** h-m1 (validated)

### Gate Condition
SHOULD_WORK - Failure indicates limitation but does not block workflow. If mode profiles are not stable, findings need qualification.

---

## Continuation Context

Building on h-m1 which validated that different mathematical operations create systematically different sensitivities to influence modes. h-c1 tests whether those mode profiles are stable within each method.

### Previous Hypothesis Results (if applicable)
h-m1 PASS: All 3 attribution methods (TRAK, TracIn, Kronfluence) correctly integrated. Probe pairs cover 3 modes: memorization, feature transfer, spurious. Mechanism is testable.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB specialized in diffusion/generative models. No direct hits for:
- Cronbach's alpha / split-half reliability
- Attribution method stability measurement
- Psychometric reliability analysis

**Conclusion:** Standard psychometrics literature and established libraries (pingouin) are authoritative sources for this hypothesis.

### Archon Code Examples

No relevant code examples found. Archon KB does not contain attribution method or psychometric implementations.

### Exa GitHub Implementations

**Query 1: Cronbach's Alpha Implementation**

**Repository 1**: raphaelvallat/pingouin (⭐ 1.5k+)
- **URL**: https://github.com/raphaelvallat/pingouin
- **Relevance**: Standard statistical library with Cronbach's alpha implementation
- **Key Code**:
  ```python
  import pingouin as pg
  # Wide format: each column is an item (mode), each row is a subject (probe pair)
  alpha, ci = pg.cronbach_alpha(data=mode_scores_df)
  # Returns: (alpha_value, [lower_ci, upper_ci])
  ```
- **Features**:
  - Supports wide and long format data
  - Pairwise or listwise deletion for missing values
  - 95% confidence intervals via Feldt's method
  - Tested against R's psych package

**Repository 2**: cronbach (standalone package)
- **URL**: https://pypi.org/project/cronbach/
- **Relevance**: Fork of pingouin's cronbach_alpha with fewer dependencies
- **Key Code**:
  ```python
  from cronbach import alpha
  alpha_val, ci = alpha(df)
  ```

**Query 2: Attribution Methods (TRAK, TracIn)**

**Repository 3**: MadryLab/trak (⭐ official)
- **URL**: https://github.com/MadryLab/trak
- **Relevance**: Official TRAK implementation for data attribution
- **Key Code**:
  ```python
  from trak import TRAKer
  traker = TRAKer(model=model, task='image_classification', train_set_size=N)
  traker.featurize(batch=batch, ...)
  scores = traker.finalize_scores(exp_name='test')
  ```

**Repository 4**: rollovd/TracIn-PyTorch
- **URL**: https://github.com/rollovd/TracIn-PyTorch
- **Relevance**: TracIn implementation with batch processing
- **Key Code**:
  ```python
  from src.tracin import vectorized_calculate_tracin_score
  matrix = vectorized_calculate_tracin_score(model, criterion, weights, ...)
  ```

**Repository 5**: Captum (TracInCP)
- **URL**: https://captum.ai/tutorials/TracInCP_Tutorial
- **Relevance**: Official PyTorch interpretability library with TracIn
- **Key Code**:
  ```python
  from captum.influence import TracInCPFast
  tracin = TracInCPFast(model, train_dataset, checkpoints, loss_fn)
  influences = tracin.influence(test_examples)
  ```

### 🎯 Implementation Priority Assessment

**For reliability measurement (Cronbach's alpha):**
1. pingouin library (HIGHEST) - established, tested against R
2. Manual numpy implementation (FALLBACK) - for custom modifications

**For attribution scores (reuse from h-m1):**
1. TRAK: MadryLab/trak (official)
2. TracIn: Captum TracInCPFast
3. Kronfluence: existing h-m1 implementation

**Recommended Implementation Path:**
- Primary: pingouin.cronbach_alpha() for reliability measurement
- Fallback: Manual implementation using numpy correlation formula
- Justification: pingouin is the standard Python library for psychometric analysis, tested against R's psych package, provides confidence intervals

### Code Analysis (Serena MCP)

*Skipped* - Code patterns are clear. Standard library functions (pingouin) and established attribution implementations (TRAK, TracIn, Captum) require no additional semantic analysis.

---

## Experiment Specification

### Dataset

**Name**: h-m1 Attribution Scores (reuse from prerequisite)
**Type**: programmatic-api (computed from h-m1 validation)
**Description**: Attribution influence scores computed by TRAK, TracIn, and Kronfluence from h-m1 experiment

**Data Structure**:
- 3 attribution methods × 3 influence modes × N probe pairs
- Each cell: influence score (float) for probe pair on mode
- Total: 9 "items" per probe pair (for Cronbach's alpha calculation)

**Sample Size**: 1000 contrastive probe pairs per mode (from 02b_verification_plan.md)
- Full dataset: 1000 pairs × 3 modes = 3000 probe pairs total
- Per-method reliability: 1000 samples (statistically meaningful)

**Loading Information** (for Phase 4):
- Method: File I/O (reuse h-m1 outputs)
- Identifier: `h-m1/outputs/attribution_scores.npz`
- Code:
  ```python
  import numpy as np
  scores = np.load("../h-m1/outputs/attribution_scores.npz")
  # scores["trak_memorization"], scores["trak_feature_transfer"], etc.
  ```

### Models

#### Baseline Model

**N/A** - This is a statistical analysis hypothesis, not model training.

h-c1 analyzes existing attribution scores from h-m1. No neural network training required.

**Loading Information** (for Phase 4):
- Method: N/A
- Identifier: N/A
- Code: N/A (statistical analysis only)

#### Analysis Method

**Method**: Split-half reliability with Cronbach's alpha
**Library**: pingouin (https://github.com/raphaelvallat/pingouin)

**Core Mechanism Implementation:**

```python
import numpy as np
import pandas as pd
import pingouin as pg

def compute_mode_profile_reliability(attribution_scores: dict) -> dict:
    """
    Compute Cronbach's alpha for each attribution method's mode profile.
    
    Args:
        attribution_scores: Dict with keys like "trak_memorization", "tracin_feature_transfer", etc.
                           Each value is array of shape (n_probes,)
    
    Returns:
        Dict mapping method_name -> (alpha, [ci_lower, ci_upper])
    """
    methods = ["trak", "tracin", "kronfluence"]
    modes = ["memorization", "feature_transfer", "spurious"]
    results = {}
    
    for method in methods:
        # Build DataFrame: rows = probe pairs, cols = modes (items)
        mode_scores = pd.DataFrame({
            mode: attribution_scores[f"{method}_{mode}"]
            for mode in modes
        })
        
        # Cronbach's alpha treats modes as "items" measuring same construct
        # (the method's overall sensitivity profile)
        alpha, ci = pg.cronbach_alpha(data=mode_scores)
        results[method] = {"alpha": alpha, "ci_lower": ci[0], "ci_upper": ci[1]}
    
    return results

# Success: alpha > 0.8 for each method
```

### Training Protocol

**N/A** - No model training. This is a statistical analysis experiment.

**Analysis Protocol**:
1. Load attribution scores from h-m1 outputs
2. For each method (TRAK, TracIn, Kronfluence):
   a. Construct mode profile matrix (probes × modes)
   b. Compute Cronbach's alpha using pingouin
   c. Record alpha value and 95% CI
3. Check if all alphas > 0.8

**Seeds**: 1 (fixed) - Cronbach's alpha is deterministic given data

### Evaluation

**Primary Metric**: Cronbach's alpha (internal consistency reliability)

**Success Criteria** (from 02b_verification_plan.md):
- Cronbach's alpha > 0.8 for each method's mode profile
- This is the P2 success criterion

**Interpretation**:
| Alpha Range | Interpretation |
|-------------|----------------|
| α ≥ 0.9 | Excellent reliability |
| 0.8 ≤ α < 0.9 | Good reliability |
| 0.7 ≤ α < 0.8 | Acceptable |
| α < 0.7 | Poor (hypothesis fails) |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: reliability_analysis
- Library: pingouin
- Code:
  ```python
  import pingouin as pg
  alpha, ci = pg.cronbach_alpha(data=mode_scores_df)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing Cronbach's alpha for each method with 95% CI error bars, threshold line at 0.8

#### Additional Figures (LLM Autonomous)
- **Reliability Heatmap**: Mode × Method matrix showing item-total correlations
- **Alpha-if-dropped**: For each method, show how alpha changes if each mode is dropped (identifies problematic modes)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Cronbach's alpha > 0.8 for each method's mode profile

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB**: No relevant sources found. Knowledge base focused on diffusion/generative models, not psychometrics or attribution methods.

### B. GitHub Implementations (Exa)

**Repository 1**: raphaelvallat/pingouin (⭐ 1.5k+)
- **URL**: https://github.com/raphaelvallat/pingouin
- **Query Used**: "Cronbach alpha split-half reliability Python scipy pingouin"
- **Relevance**: Standard Python library for statistical analysis, Cronbach's alpha implementation
- **Key Code**:
  ```python
  import pingouin as pg
  alpha, ci = pg.cronbach_alpha(data=mode_scores_df)
  # Returns: (alpha_value, array([ci_lower, ci_upper]))
  ```
- **Used For**: Core reliability measurement implementation

**Repository 2**: MadryLab/trak (⭐ official)
- **URL**: https://github.com/MadryLab/trak
- **Query Used**: "TRAK TracIn influence function stability measurement"
- **Relevance**: Official TRAK implementation (attribution scores from h-m1)
- **Used For**: Understanding attribution score format for h-m1 dependency

**Repository 3**: Captum TracInCPFast
- **URL**: https://captum.ai/tutorials/TracInCP_Tutorial
- **Relevance**: PyTorch influence function library (TracIn from h-m1)
- **Used For**: Understanding TracIn score format

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - pingouin API is well-documented and straightforward.

### D. Previous Hypothesis Context

**Source**: h-m1 (prerequisite)
- **Status**: VALIDATED (PASS)
- **Reused Components**:
  - Attribution scores: TRAK, TracIn, Kronfluence outputs
  - Probe pairs: 1000 per mode × 3 modes
  - Mode definitions: memorization, feature_transfer, spurious
- **Why Reused**: h-c1 tests reliability of h-m1's mode profiles; same data enables controlled analysis

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Cronbach's alpha formula | Exa GitHub | pingouin documentation |
| Confidence intervals | Exa GitHub | Feldt's method (pingouin) |
| Attribution scores | h-m1 | MadryLab/trak, Captum |
| Success threshold (0.8) | Phase 2B | 02b_verification_plan.md |
| Sample size (1000) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- 2026-08-24: Phase 2C experiment design started
- 2026-08-24: MCP searches completed (Archon: 4 queries, Exa: 2 queries)
- 2026-08-24: Experiment specification synthesized
- 2026-08-24: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
