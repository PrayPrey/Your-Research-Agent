# Experiment Design: h-c1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** The truthfulness-robustness correlation pattern holds separately for base models and instruction-tuned models, with potentially different effect sizes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **CONDITION (Stratified Analysis) Template** - Testing generality across model types.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASSED: r=0.8028, p=0.00055)
**Gate Status:** SHOULD_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1
- **Type:** CONDITION
- **Prerequisites:** h-e1 (PASSED)

### Gate Condition
Both base models and instruction-tuned models show positive TruthfulQA-AdvGLUE correlation (r > 0.2) with consistent sign. Pattern should hold across both subgroups.

---

## Continuation Context

Building on h-e1 which established strong overall correlation (r=0.8028, p<0.001) across 14 models from 4 families. This hypothesis tests whether the relationship is fundamental (holds for both model types) or an artifact of instruction tuning.

### Previous Hypothesis Results
**h-e1 Results:**
- Partial correlation r=0.8028 (threshold: >0.3)
- p-value=0.00055 (threshold: <0.05)
- 95% CI: [0.082, 0.969] (excludes 0)
- 14 models: Pythia (8), Llama-2 (3), Mistral (1), Falcon (2)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** No Archon MCP available.

Standard approach for stratified correlation analysis:
1. Label models by type (base vs instruction-tuned)
2. Compute within-group correlations
3. Compare effect sizes across groups

### Exa GitHub Implementations

**[INFERRED]** No Exa MCP available.

Key references:
1. **EleutherAI/lm-evaluation-harness** - Same evaluation framework as h-e1
2. Model cards on HuggingFace contain tuning type metadata

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| **Name** | TruthfulQA + AdvGLUE + Model Metadata (reuse h-e1 data + extend) |
| **Type** | standard |
| **Source** | HuggingFace Hub via lm-evaluation-harness |
| **Additional Metadata** | Model type (base/instruction-tuned) from HuggingFace model cards |
| **Preprocessing** | Label each model with tuning type |

**Loading Information:**
- Method: Extend h-e1 data collection with instruction-tuned variants
- Code:
```python
# Model type labeling
MODEL_TYPES = {
    # Base models (from h-e1)
    "EleutherAI/pythia-70m": "base",
    "EleutherAI/pythia-160m": "base",
    "EleutherAI/pythia-410m": "base",
    "EleutherAI/pythia-1b": "base",
    "EleutherAI/pythia-1.4b": "base",
    "EleutherAI/pythia-2.8b": "base",
    "EleutherAI/pythia-6.9b": "base",
    "EleutherAI/pythia-12b": "base",
    "meta-llama/Llama-2-7b-hf": "base",
    "meta-llama/Llama-2-13b-hf": "base",
    "meta-llama/Llama-2-70b-hf": "base",
    "mistralai/Mistral-7B-v0.1": "base",
    "tiiuae/falcon-7b": "base",
    "tiiuae/falcon-40b": "base",
    # Instruction-tuned variants (to add)
    "meta-llama/Llama-2-7b-chat-hf": "instruction-tuned",
    "meta-llama/Llama-2-13b-chat-hf": "instruction-tuned",
    "meta-llama/Llama-2-70b-chat-hf": "instruction-tuned",
    "mistralai/Mistral-7B-Instruct-v0.1": "instruction-tuned",
    "tiiuae/falcon-7b-instruct": "instruction-tuned",
    "tiiuae/falcon-40b-instruct": "instruction-tuned",
}
```

### Models

#### Model Sample

| Property | Value |
|----------|-------|
| **Total Sample Size** | 20+ models (14 from h-e1 + 6+ instruction-tuned) |
| **Base Models** | ~14 (all h-e1 models) |
| **Instruction-Tuned** | 6+ models |
| **Minimum per Group** | 6 models (for meaningful correlation) |

**Extended Model List:**

Base models (from h-e1):
- Pythia: 70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b
- Llama-2: 7b-hf, 13b-hf, 70b-hf
- Mistral: 7B-v0.1
- Falcon: 7b, 40b

Instruction-tuned models (new evaluations):
- Llama-2: 7b-chat-hf, 13b-chat-hf, 70b-chat-hf
- Mistral: 7B-Instruct-v0.1
- Falcon: 7b-instruct, 40b-instruct

### Core Implementation

```python
import numpy as np
from scipy import stats
from sklearn.utils import resample

def stratified_correlation_analysis(data):
    """
    Compute TruthfulQA-AdvGLUE correlation separately for base and 
    instruction-tuned models.
    
    Args:
        data: list of dicts with keys:
            - model: model name
            - truthfulqa_mc1: MC1 accuracy
            - advglue_avg: AdvGLUE average accuracy
            - log_params: log(parameter count)
            - model_type: "base" or "instruction-tuned"
    
    Returns:
        dict with results per group and comparison
    """
    # Split by model type
    base = [d for d in data if d['model_type'] == 'base']
    instruct = [d for d in data if d['model_type'] == 'instruction-tuned']
    
    def compute_group_correlation(group):
        if len(group) < 4:
            return {'r': np.nan, 'p': np.nan, 'n': len(group), 'error': 'insufficient_samples'}
        
        tqa = np.array([d['truthfulqa_mc1'] for d in group])
        adv = np.array([d['advglue_avg'] for d in group])
        log_p = np.array([d['log_params'] for d in group])
        
        # Partial correlation (control for size)
        resid_tqa = tqa - np.polyval(np.polyfit(log_p, tqa, 1), log_p)
        resid_adv = adv - np.polyval(np.polyfit(log_p, adv, 1), log_p)
        
        r, p = stats.pearsonr(resid_tqa, resid_adv)
        
        # Bootstrap CI
        n_boot = 1000
        boot_rs = []
        for _ in range(n_boot):
            idx = resample(range(len(group)), replace=True)
            tqa_b = tqa[idx]
            adv_b = adv[idx]
            log_p_b = log_p[idx]
            resid_tqa_b = tqa_b - np.polyval(np.polyfit(log_p_b, tqa_b, 1), log_p_b)
            resid_adv_b = adv_b - np.polyval(np.polyfit(log_p_b, adv_b, 1), log_p_b)
            r_b, _ = stats.pearsonr(resid_tqa_b, resid_adv_b)
            boot_rs.append(r_b)
        
        ci_lower = np.percentile(boot_rs, 2.5)
        ci_upper = np.percentile(boot_rs, 97.5)
        
        return {
            'r': r,
            'p': p,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'n': len(group),
            'gate_passed': r > 0.2  # Within-group threshold
        }
    
    base_results = compute_group_correlation(base)
    instruct_results = compute_group_correlation(instruct)
    
    # Overall gate: both groups r > 0.2 with same sign
    both_positive = (base_results.get('r', 0) > 0.2 and 
                     instruct_results.get('r', 0) > 0.2)
    same_sign = (np.sign(base_results.get('r', 0)) == 
                 np.sign(instruct_results.get('r', 0)))
    
    return {
        'base': base_results,
        'instruction_tuned': instruct_results,
        'pattern_consistent': both_positive and same_sign,
        'gate_passed': both_positive
    }
```

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **Base models r** | Within-group partial correlation | r > 0.2 |
| **Instruction-tuned r** | Within-group partial correlation | r > 0.2 |
| **Pattern consistency** | Same sign in both groups | Both positive |

**Gate Condition:** PASS if both groups show r > 0.2 with positive correlation.

### Visualization Requirements

#### Required Figure (Mandatory)
- **Stratified Scatter Plot**: Two-panel scatter plot
  - Left panel: Base models (TruthfulQA vs AdvGLUE)
  - Right panel: Instruction-tuned models
  - Regression lines with CI bands
  - Annotate r, p for each group

#### Additional Figures
1. **Effect size comparison**: Bar chart of r values per group with CI error bars
2. **Combined plot**: Single scatter with color coding by model type

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Base models: r > 0.2
3. Instruction-tuned models: r > 0.2
4. Both groups show positive correlation

**Partial Success:** One group passes, other inconclusive (small sample)

**Failure Interpretation:** Pattern may be instruction-tuning artifact

---

## Execution Plan

### Phase 4 Tasks

1. **Data Extension** (reuse h-e1 + add instruction-tuned):
   - Load h-e1 cached results
   - Run lm-eval-harness on 6 instruction-tuned models
   - Merge datasets with model type labels

2. **Stratified Analysis**:
   - Split by model_type
   - Compute within-group partial correlations
   - Bootstrap CIs for each group

3. **Visualization**:
   - Generate two-panel scatter plot
   - Generate effect size comparison bar chart

4. **Gate Evaluation**:
   - Check r > 0.2 for both groups
   - Report pattern consistency

---

## Appendix: Reference Implementations

### Primary References

1. **h-e1 Implementation**
   - Path: h-e1/code/
   - Reuse: Data loading, partial correlation functions

2. **lm-evaluation-harness**
   - URL: https://github.com/EleutherAI/lm-evaluation-harness
   - Same evaluation protocol as h-e1

### Statistical Methods

- Stratified partial correlation analysis
- Bootstrap CI per stratum
- No formal comparison test (pattern consistency check only)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated for h-c1
- Prerequisites: h-e1 PASSED (r=0.8028, p=0.00055)

---

*MCP Tools Used: None (MCP unavailable - used general knowledge)*
*All specifications grounded in h-e1 validated methodology*
*Next Phase: Phase 3 - Implementation Planning*
