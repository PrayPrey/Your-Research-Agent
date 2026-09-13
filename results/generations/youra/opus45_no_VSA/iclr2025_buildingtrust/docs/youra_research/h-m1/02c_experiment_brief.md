# Experiment Design: H-M1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** PC1,residual correlates positively with Behavioral Stability Index (BSI) computed on independent datasets (ρ > 0, p < 0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests causal relationship between latent factor and behavioral measure.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED: λ₁=2.277 exceeds 95th percentile, p=0.001)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (PC1,residual must exist)

### Gate Condition
PC1,residual correlates positively with BSI (ρ > 0, p < 0.05). If fails, entire GRC theory is undermined—latent factor exists but doesn't predict behavioral stability.

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **PC1 validated:** λ₁=2.277, explaining 60% of residual variance
- **Factor loadings:** All 6 benchmarks load positively (0.35-0.44) on PC1
- **KMO:** 0.83 (meritorious factor structure)
- **Models evaluated:** ~100 LLMs with trustworthiness benchmark scores

**Reuse from H-E1:**
- Same model set (~100 LLMs)
- Same PC1,residual scores computed in H-E1
- Same confound controls (log(params), release date)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Behavioral stability LLM paraphrase**
- Limited direct matches in KB
- Found: Consistency models (diffusion), BERT fine-tuning patterns

**Query 2: LLM trustworthiness evaluation PCA**
- Paper: "Evaluating Large Language Models" (hf.co/papers/2305.14314)
- OpenReview discussions on LLM evaluation methodology

### Archon Code Examples

Limited direct code for BSI computation. Primary patterns found:
- BERT paraphrase detection fine-tuning
- Consistency model implementations (different domain)

### Exa GitHub Implementations

**Repository 1**: google-research-datasets/paws (Official)
- **URL**: https://github.com/google-research-datasets/paws
- **Relevance**: PAWS = Paraphrase Adversaries from Word Scrambling—exactly what BSI measures
- **Dataset Stats**: 108,463 human-labeled pairs, high lexical overlap
- **Key Insight**: Models fail <40% accuracy without PAWS training, tests structural understanding

**Repository 2**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Standard LLM evaluation framework, includes PAWS-X task
- **Architecture**: Modular task system, standardized evaluation

**Repository 3**: GLUE Benchmark (nyu-mll/glue)
- **URL**: HuggingFace datasets
- **Relevance**: QQP (Quora Question Pairs) included as GLUE task
- **Dataset Stats**: 400k+ question pairs

### 🎯 Implementation Priority Assessment

**CRITICAL: BSI computation requires paraphrase consistency evaluation**

**Recommended Implementation Path:**
- Primary: Use PAWS-Wiki test set + QQP test set via HuggingFace datasets
- Fallback: EleutherAI lm-eval-harness PAWS-X task
- Justification: PAWS specifically designed to test behavioral stability (same words, different meaning)

### Code Analysis (Serena MCP)

*Skipped* - Code patterns clear from Exa search. BSI = accuracy consistency across paraphrase pairs.

---

## Experiment Specification

### Dataset

**Dataset 1: PAWS-Wiki (Primary BSI Dataset)**
- **Name**: google-research-datasets/paws (labeled_final)
- **Type**: standard (HuggingFace datasets)
- **Source**: https://huggingface.co/datasets/google-research-datasets/paws
- **Purpose**: Test behavioral stability on adversarial paraphrases
- **Size**: 8,000 test pairs (labeled_final)
- **Task**: Binary classification (paraphrase: 1, non-paraphrase: 0)
- **Why BSI-relevant**: High lexical overlap pairs test structural understanding, not bag-of-words matching

**Dataset 2: QQP (Secondary BSI Dataset)**
- **Name**: nyu-mll/glue (qqp config)
- **Type**: standard (HuggingFace GLUE)
- **Source**: https://huggingface.co/datasets/nyu-mll/glue
- **Purpose**: Complement PAWS with standard paraphrase task
- **Size**: 40,430 validation pairs (test labels hidden)
- **Task**: Binary classification (duplicate: 1, not duplicate: 0)
- **Why BSI-relevant**: Real-world paraphrase detection, different distribution from PAWS

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `google-research-datasets/paws` (config: `labeled_final`) + `nyu-mll/glue` (config: `qqp`)
- Code:
```python
from datasets import load_dataset

# PAWS-Wiki
paws = load_dataset("google-research-datasets/paws", "labeled_final", split="test")
# Columns: id, sentence1, sentence2, label

# QQP from GLUE
qqp = load_dataset("nyu-mll/glue", "qqp", split="validation")
# Columns: question1, question2, label, idx
```

### Models

#### Baseline Model

**Architecture**: ~100 LLMs from H-E1 analysis
**Type**: Pre-existing benchmark scores (no training needed)
**Source**: H-E1 validation results (PC1,residual scores)

**Model Selection**: Same set as H-E1 to ensure PC1 scores are valid
- Includes: Llama-2 family, Mistral family, GPT variants, etc.
- Parameter range: 1B to 70B+

**Loading Information** (for Phase 4 download):
- Method: No model download needed—use pre-computed PC1 scores from H-E1
- Identifier: `../h-e1/04_validation.md` (PC1 scores)
- Code:
```python
# Load PC1 scores from H-E1
import pandas as pd
pc1_scores = pd.read_csv("../h-e1/results/pc1_scores.csv")
# Columns: model_name, pc1_score, log_params, release_date
```

#### Proposed Model

**Architecture**: N/A (correlation analysis, not model modification)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Behavioral Stability Index (BSI) Computation
# Based on: PAWS methodology (Zhang et al., NAACL 2019)

import numpy as np
from scipy import stats

def compute_bsi(model_predictions_paws, model_predictions_qqp, 
                paws_labels, qqp_labels):
    """
    Compute Behavioral Stability Index for a single model.
    
    BSI = average consistency across paraphrase evaluation tasks
    
    Args:
        model_predictions_paws: (N_paws,) model predictions on PAWS
        model_predictions_qqp: (N_qqp,) model predictions on QQP
        paws_labels: (N_paws,) ground truth labels
        qqp_labels: (N_qqp,) ground truth labels
    
    Returns:
        bsi_score: float, behavioral stability index
    """
    # Accuracy on each dataset
    paws_acc = np.mean(model_predictions_paws == paws_labels)
    qqp_acc = np.mean(model_predictions_qqp == qqp_labels)
    
    # BSI = geometric mean of accuracies (penalizes imbalance)
    bsi_score = np.sqrt(paws_acc * qqp_acc)
    
    return bsi_score

def compute_bsi_correlation(pc1_scores, bsi_scores):
    """
    Test H-M1: PC1,residual correlates with BSI.
    
    Args:
        pc1_scores: (M,) PC1 scores for M models
        bsi_scores: (M,) BSI scores for M models
    
    Returns:
        rho: Pearson correlation coefficient
        p_value: two-tailed p-value
    """
    rho, p_value = stats.pearsonr(pc1_scores, bsi_scores)
    return rho, p_value

# Integration: Run after H-E1 PC1 computation
```

### Training Protocol

**No training required** — This is a correlation analysis experiment.

**Protocol:**
1. Load PC1,residual scores from H-E1 results
2. For each model, compute BSI on PAWS + QQP (if predictions available)
   - If predictions not available: Run inference on test sets
3. Compute Pearson correlation between PC1 and BSI
4. Report ρ, p-value, 95% CI

**Inference Settings (if needed):**
- Batch size: 32
- Max sequence length: 256
- Prompt format: "[CLS] sentence1 [SEP] sentence2 [SEP]" or model-specific

**Seeds**: 1 (deterministic inference)

### Evaluation

**Primary Metrics:**
- **ρ (Pearson correlation)**: PC1,residual vs BSI
- **p-value**: Statistical significance of correlation
- **95% CI**: Confidence interval for ρ

**Success Criteria:**
- ρ > 0 (positive correlation)
- p < 0.05 (statistically significant)

**Expected Baseline Performance** (from research):
- PAWS accuracy: ~85% for strong models (with PAWS training)
- PAWS accuracy: <40% for naive models (BERT on QQP only)
- QQP accuracy: ~90% for BERT-class models
- **Source**: Zhang et al., NAACL 2019; GLUE leaderboard

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import pearsonr, spearmanr
import numpy as np

# Pearson correlation
rho, p_value = pearsonr(pc1_scores, bsi_scores)

# 95% CI via Fisher z-transform
n = len(pc1_scores)
z = np.arctanh(rho)
se = 1 / np.sqrt(n - 3)
ci_lower = np.tanh(z - 1.96 * se)
ci_upper = np.tanh(z + 1.96 * se)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **PC1 vs BSI Scatter Plot**: X-axis = PC1,residual, Y-axis = BSI
  - Include regression line
  - Show ρ and p-value in annotation
  - Color points by model family (if available)

#### Additional Figures (LLM Autonomous)
- Correlation matrix: PC1 vs individual dataset accuracies (PAWS, QQP)
- Distribution plots: PC1 distribution, BSI distribution
- Residual plot: Check correlation linearity assumptions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: TRUE — BSI is a computable metric (accuracy aggregation)
- `mechanism_isolatable`: TRUE — BSI computed independently of PC1
- `baseline_measurable`: TRUE — Individual dataset accuracies measurable

### Architecture Compatibility
- No architecture modification needed
- Uses existing model predictions on standard NLP tasks
- PC1 scores from H-E1 already validated

### Activation Indicators
- `mechanism_log_message`: "BSI computed for model {model_name}: PAWS_acc={paws_acc:.3f}, QQP_acc={qqp_acc:.3f}, BSI={bsi:.3f}"
- `tensor_shape_change`: N/A (not a neural component)
- `metric_delta_expected`: ρ should be positive (PC1 ↑ → BSI ↑)

### Mechanism Verification Code
```python
def verify_bsi_mechanism(pc1_scores, bsi_scores, min_samples=30):
    """
    Verify H-M1 mechanism is testable.
    
    Returns:
        verification_passed: bool
        reason: str
    """
    # Check 1: Sufficient samples
    if len(pc1_scores) < min_samples:
        return False, f"Insufficient samples: {len(pc1_scores)} < {min_samples}"
    
    # Check 2: Variance in both variables
    if np.std(pc1_scores) < 1e-6:
        return False, "No variance in PC1 scores"
    if np.std(bsi_scores) < 1e-6:
        return False, "No variance in BSI scores"
    
    # Check 3: No NaN/Inf
    if np.any(~np.isfinite(pc1_scores)) or np.any(~np.isfinite(bsi_scores)):
        return False, "NaN or Inf values detected"
    
    return True, "Mechanism verification passed"
```

### Success Criteria
- `hypothesis_support_metric`: Pearson ρ
- `hypothesis_support_threshold`: ρ > 0 AND p < 0.05

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Correlation computed successfully
3. ρ > 0 (positive direction)
4. p < 0.05 (significant)

**If ρ ≤ 0 or p ≥ 0.05:** H-M1 fails, GRC mechanism unsupported

---

## Appendix: Reference Implementations

### Primary References

1. **PAWS Dataset** (Zhang et al., NAACL 2019)
   - URL: https://github.com/google-research-datasets/paws
   - Paper: https://aclanthology.org/N19-1131/
   - Key: Adversarial paraphrase pairs with high lexical overlap

2. **QQP / GLUE Benchmark**
   - URL: https://huggingface.co/datasets/nyu-mll/glue
   - Paper: Wang et al., 2019
   - Key: Standard paraphrase detection benchmark

3. **lm-evaluation-harness** (EleutherAI)
   - URL: https://github.com/EleutherAI/lm-evaluation-harness
   - Key: PAWS-X task implementation for LLM evaluation

### Code Snippets Used

**PAWS Loading (HuggingFace)**:
```python
from datasets import load_dataset
paws = load_dataset("google-research-datasets/paws", "labeled_final", split="test")
```

**QQP Loading (GLUE)**:
```python
from datasets import load_dataset
qqp = load_dataset("nyu-mll/glue", "qqp", split="validation")
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-08T10:00:00Z

### Workflow History for This Hypothesis
- 2026-08-08: Phase 2C experiment design initiated
- Prerequisites: H-E1 VALIDATED (PC1 exists, λ₁=2.277)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), HuggingFace datasets docs*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
