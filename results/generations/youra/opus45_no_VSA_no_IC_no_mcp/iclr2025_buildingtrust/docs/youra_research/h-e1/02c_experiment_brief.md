# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Significant positive partial correlation (r > 0.3, p < 0.05) exists between TruthfulQA MC1 accuracy and AdvGLUE average accuracy after controlling for log(model_params) across 15+ LLMs.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
Partial correlation r > 0.3, p < 0.05 between TruthfulQA MC1 and AdvGLUE avg controlling for log(params). Bootstrap 95% CI must exclude 0.

---

## Continuation Context

First hypothesis in verification chain. No prior results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - This is the entry gate hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** No Archon MCP available in this session.

Standard approach for cross-benchmark correlation:
1. Use lm-evaluation-harness for consistent evaluation
2. Collect benchmark scores and model metadata
3. Apply partial correlation with statsmodels or scipy

### Archon Code Examples

**[INFERRED]** Pattern: Partial correlation analysis

```python
from scipy import stats
import numpy as np

def partial_correlation(x, y, covariate):
    """Compute partial Pearson correlation controlling for covariate."""
    # Residualize x on covariate
    slope_x, intercept_x, _, _, _ = stats.linregress(covariate, x)
    residual_x = x - (slope_x * covariate + intercept_x)
    
    # Residualize y on covariate
    slope_y, intercept_y, _, _, _ = stats.linregress(covariate, y)
    residual_y = y - (slope_y * covariate + intercept_y)
    
    # Correlation of residuals
    r, p = stats.pearsonr(residual_x, residual_y)
    return r, p
```

### Exa GitHub Implementations

**[INFERRED]** No Exa MCP available in this session.

Key reference implementations:
1. **EleutherAI/lm-evaluation-harness** - Standard evaluation framework
   - URL: https://github.com/EleutherAI/lm-evaluation-harness
   - Supports TruthfulQA MC1 task
   - Language: Python

2. **adversarial-glue/AdvGLUE** - Adversarial robustness benchmark
   - URL: https://github.com/adversarial-glue/AdvGLUE (via HuggingFace datasets)
   - Integrated into lm-eval-harness

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a correlation study, not paper reproduction. Priority is standard benchmark evaluation tools.

**Recommended Implementation Path:**
- Primary: lm-evaluation-harness for all evaluations
- Fallback: Direct HuggingFace datasets + custom evaluation loop
- Justification: lm-eval-harness ensures consistent evaluation across models

### Code Analysis (Serena MCP)

**[INFERRED]** No Serena MCP available.

Standard correlation analysis pattern requires:
- Data collection: benchmark scores per model
- Statistical analysis: partial correlation, bootstrap CI
- Visualization: scatter plot with regression line

---

## Experiment Specification

### Dataset

| Property | Value |
|----------|-------|
| **Name** | TruthfulQA + AdvGLUE + Model Metadata |
| **Type** | standard |
| **Source** | HuggingFace Hub via lm-evaluation-harness |
| **TruthfulQA Version** | truthful_qa (mc1 task) |
| **AdvGLUE Version** | adversarial_glue (all subtasks) |
| **Preprocessing** | None - use raw benchmark scores |
| **Augmentation** | N/A - correlation study |

**Loading Information** (for Phase 4 download):
- Method: lm-evaluation-harness CLI or Python API
- Identifier: `truthful_qa`, `adversarial_glue`
- Code:
```python
# Via lm-eval CLI
# lm_eval --model hf --model_args pretrained=MODEL_NAME --tasks truthful_qa_mc1,adversarial_glue --batch_size auto

# Via HuggingFace datasets (fallback)
from datasets import load_dataset
truthfulqa = load_dataset("truthful_qa", "multiple_choice")
advglue = load_dataset("adv_glue", "adv_sst2")  # Example subtask
```

### Models

#### Baseline Model

| Property | Value |
|----------|-------|
| **Sample Size** | 15-20 models |
| **Families** | Pythia (70M-12B), Llama-2 (7B-70B), Mistral (7B), Falcon (7B-40B) |
| **Type** | Decoder-only autoregressive |
| **Selection Criteria** | Multiple sizes per family for correlation range |

**Model List (Target):**
1. EleutherAI/pythia-70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b
2. meta-llama/Llama-2-7b-hf, 13b-hf, 70b-hf
3. mistralai/Mistral-7B-v0.1
4. tiiuae/falcon-7b, 40b

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers via lm-eval-harness
- Identifier: HuggingFace model IDs (listed above)
- Code:
```python
# lm-eval-harness handles loading
# lm_eval --model hf --model_args pretrained=EleutherAI/pythia-1b --tasks truthful_qa_mc1
```

#### Proposed Model

**Architecture:** N/A - Correlation analysis, not model training

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy import stats
from sklearn.utils import resample

def run_correlation_analysis(truthfulqa_scores, advglue_scores, log_params):
    """
    Compute partial correlation between TruthfulQA MC1 and AdvGLUE avg
    controlling for log(model_params).
    
    Args:
        truthfulqa_scores: array of MC1 accuracy per model
        advglue_scores: array of AdvGLUE avg accuracy per model
        log_params: array of log(param_count) per model
    
    Returns:
        dict with r, p, ci_lower, ci_upper
    """
    n = len(truthfulqa_scores)
    
    # Partial correlation via residualization
    def partial_corr(x, y, z):
        # Regress out z from x and y
        _, _, rx, _, _ = stats.linregress(z, x)
        _, _, ry, _, _ = stats.linregress(z, y)
        resid_x = x - np.polyval(np.polyfit(z, x, 1), z)
        resid_y = y - np.polyval(np.polyfit(z, y, 1), z)
        return stats.pearsonr(resid_x, resid_y)
    
    r, p = partial_corr(truthfulqa_scores, advglue_scores, log_params)
    
    # Bootstrap 95% CI
    n_bootstrap = 1000
    bootstrap_rs = []
    for _ in range(n_bootstrap):
        idx = resample(range(n), replace=True)
        r_boot, _ = partial_corr(
            truthfulqa_scores[idx], 
            advglue_scores[idx], 
            log_params[idx]
        )
        bootstrap_rs.append(r_boot)
    
    ci_lower = np.percentile(bootstrap_rs, 2.5)
    ci_upper = np.percentile(bootstrap_rs, 97.5)
    
    return {
        'r': r,
        'p': p,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'n_models': n,
        'gate_passed': r > 0.3 and p < 0.05 and ci_lower > 0
    }
```

### Training Protocol

N/A - This is a correlation analysis study, not a training experiment.

**Evaluation-only protocol:**
1. Run lm-eval-harness on each model for TruthfulQA MC1
2. Run lm-eval-harness on each model for AdvGLUE (all subtasks)
3. Collect model parameter counts from model configs
4. Compute partial correlation with bootstrap CI

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **Partial r** | Pearson correlation controlling for log(params) | r > 0.3 |
| **p-value** | Statistical significance | p < 0.05 |
| **Bootstrap CI** | 95% confidence interval | Lower bound > 0 |

**Gate Condition:** All three criteria must be met for PASS.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats, sklearn.utils (for bootstrap)
- Code:
```python
from scipy import stats
from sklearn.utils import resample
import numpy as np

# Pearson correlation
r, p = stats.pearsonr(x, y)

# Bootstrap
bootstrap_samples = [resample(data) for _ in range(1000)]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of TruthfulQA MC1 vs AdvGLUE avg
  - X-axis: TruthfulQA MC1 accuracy
  - Y-axis: AdvGLUE average accuracy
  - Point size: proportional to log(params)
  - Regression line with CI band
  - Annotate r, p values

#### Additional Figures (LLM Autonomous)

1. **Partial correlation visualization**: Residual plot after controlling for model size
2. **Bootstrap distribution**: Histogram of bootstrap r values with CI bounds
3. **Model family comparison**: Grouped bar chart of scores by family

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Partial r > 0.3, p < 0.05, CI excludes 0

---

## Appendix: Reference Implementations

### Primary References

1. **lm-evaluation-harness**
   - URL: https://github.com/EleutherAI/lm-evaluation-harness
   - Purpose: Standardized LLM evaluation
   - Tasks: truthful_qa_mc1, adversarial_glue

2. **TruthfulQA Paper**
   - Lin et al. (2022) "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
   - Dataset: HuggingFace truthful_qa

3. **AdvGLUE Paper**
   - Wang et al. (2022) "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation"
   - Dataset: HuggingFace adv_glue

### Statistical Methods

4. **Partial Correlation**
   - Scipy stats.pearsonr for base correlation
   - Residualization method for partial correlation
   - Bootstrap resampling for confidence intervals

### Code Snippets

**lm-eval-harness usage:**
```bash
# Install
pip install lm-eval

# Run evaluation
lm_eval --model hf \
  --model_args pretrained=EleutherAI/pythia-1b \
  --tasks truthful_qa_mc1 \
  --batch_size auto \
  --output_path results/
```

**Collecting results:**
```python
import json
import os

def collect_results(results_dir):
    """Parse lm-eval-harness JSON outputs."""
    scores = []
    for model_dir in os.listdir(results_dir):
        result_file = os.path.join(results_dir, model_dir, 'results.json')
        if os.path.exists(result_file):
            with open(result_file) as f:
                data = json.load(f)
            scores.append({
                'model': model_dir,
                'truthfulqa_mc1': data['results']['truthful_qa_mc1']['acc'],
                'advglue_avg': np.mean([
                    data['results'][task]['acc'] 
                    for task in data['results'] 
                    if 'adv' in task
                ])
            })
    return scores
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated for h-e1

---

*MCP Tools Used: None (MCP unavailable - used general knowledge)*
*All specifications grounded in standard benchmark evaluation practices*
*Next Phase: Phase 3 - Implementation Planning*
