# Experiment Brief: h-e1 Correlation Existence

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Significant positive partial correlation (r > 0.3, p < 0.05) exists between TruthfulQA MC1 accuracy and AdvGLUE average accuracy after controlling for log(model_params) across 15+ LLMs.

## 2. Research Design

### 2.1 Variables

| Variable | Type | Measurement |
|----------|------|-------------|
| TruthfulQA MC1 | DV | Accuracy score (0-1) via lm-eval-harness |
| AdvGLUE Average | DV | Mean accuracy across 5 subtasks |
| log(params) | CV | Log-transformed parameter count |
| Model Identity | IV | Categorical (15-20 models) |

### 2.2 Model Selection

**Target:** 15-20 decoder-only LLMs across 4+ families

| Family | Models | Size Range |
|--------|--------|------------|
| Pythia | 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B | 70M-12B |
| Llama-2 | 7B, 13B | 7B-13B |
| Mistral | 7B | 7B |
| Falcon | 7B | 7B |
| OPT | 125M, 350M, 1.3B, 2.7B, 6.7B | 125M-6.7B |

**Total:** ~18 models spanning 70M-13B parameters

## 3. Datasets

### 3.1 TruthfulQA

- **Source:** HuggingFace `truthful_qa`
- **Task:** MC1 (single correct answer)
- **Samples:** 817 questions (full test set)
- **Type:** standard
- **Evaluation:** lm-eval-harness with `truthfulqa_mc1`

### 3.2 AdvGLUE

- **Source:** HuggingFace `AI-Secure/adv_glue`
- **Tasks:** SST-2, QQP, MNLI, RTE, QNLI (adversarial versions)
- **Samples:** ~5,000 total across subtasks
- **Type:** standard
- **Evaluation:** Custom evaluation script using dev.json

### 3.3 MMLU (for ECE baseline in h-m1)

- **Source:** HuggingFace `cais/mmlu`
- **Samples:** Full validation set (~1,500 questions)
- **Type:** standard
- **Purpose:** Neutral ECE calculation for mechanism hypothesis

## 4. Implementation Plan

### 4.1 Phase 1: Data Collection

```python
# lm-eval-harness commands
lm_eval --model hf \
    --model_args pretrained=EleutherAI/pythia-70m \
    --tasks truthfulqa_mc1 \
    --output_path results/pythia-70m/

# Repeat for all 18 models
```

### 4.2 Phase 2: AdvGLUE Evaluation

```python
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

advglue = load_dataset("AI-Secure/adv_glue")

# Evaluate each model on 5 AdvGLUE subtasks
# Compute mean accuracy as AdvGLUE_avg
```

### 4.3 Phase 3: Partial Correlation Analysis

```python
import numpy as np
from scipy import stats
import pandas as pd

def partial_correlation(x, y, z):
    """Compute partial correlation r(x,y|z)"""
    # Regress x on z
    slope_xz, intercept_xz, _, _, _ = stats.linregress(z, x)
    resid_x = x - (slope_xz * z + intercept_xz)
    
    # Regress y on z
    slope_yz, intercept_yz, _, _, _ = stats.linregress(z, y)
    resid_y = y - (slope_yz * z + intercept_yz)
    
    # Correlate residuals
    r, p = stats.pearsonr(resid_x, resid_y)
    return r, p

def bootstrap_ci(x, y, z, n_iterations=1000, alpha=0.05):
    """Bootstrap 95% CI for partial correlation"""
    n = len(x)
    r_samples = []
    for _ in range(n_iterations):
        idx = np.random.choice(n, n, replace=True)
        r, _ = partial_correlation(x[idx], y[idx], z[idx])
        r_samples.append(r)
    lower = np.percentile(r_samples, 100 * alpha / 2)
    upper = np.percentile(r_samples, 100 * (1 - alpha / 2))
    return lower, upper

# Apply to collected data
df = pd.read_csv("results/benchmark_scores.csv")
x = df['truthfulqa_mc1'].values
y = df['advglue_avg'].values
z = np.log(df['params'].values)

r, p = partial_correlation(x, y, z)
ci_low, ci_high = bootstrap_ci(x, y, z)

print(f"Partial r = {r:.3f}, p = {p:.4f}")
print(f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")
```

## 5. Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Partial r | > 0.3 | Pearson partial correlation |
| p-value | < 0.05 | Two-tailed significance |
| Bootstrap CI | Excludes 0 | 1000-iteration bootstrap |

## 6. Validation Protocol

1. **Data Quality Check:** Verify all 18 models produce valid scores
2. **Normality Check:** Test residuals for normality (Shapiro-Wilk)
3. **Sensitivity Analysis:** 
   - Spearman rank correlation as robustness check
   - Leave-one-family-out analysis
4. **Visualization:** Scatter plot of TruthfulQA vs AdvGLUE with regression line

## 7. Expected Timeline

| Step | Duration | Output |
|------|----------|--------|
| Model evaluation (TruthfulQA) | 6-8 hours | CSV with MC1 scores |
| Model evaluation (AdvGLUE) | 8-10 hours | CSV with subtask scores |
| Statistical analysis | 1-2 hours | Correlation results |
| Report generation | 1 hour | 04_validation.md |

**Total:** 2-3 days

## 8. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Insufficient sample size (N=18) | Bootstrap CI; add more model variants if needed |
| Model family clustering | Weight families equally; leave-one-family-out |
| Evaluation inconsistency | Use identical lm-eval-harness settings |
| AdvGLUE format mismatch | Pre-test on 2-3 models before full run |

## 9. Output Artifacts

1. `results/benchmark_scores.csv` - All model scores
2. `results/correlation_analysis.json` - Statistical results
3. `docs/youra_research/04_validation.md` - Final validation report
4. `figures/truthfulqa_advglue_scatter.png` - Visualization

## 10. Code Dependencies

```
lm-eval>=0.4.0
transformers>=4.40.0
datasets>=2.19.0
scipy>=1.12.0
numpy>=1.26.0
pandas>=2.2.0
matplotlib>=3.8.0
```

---

## Research Sources

- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [AdvGLUE Benchmark](https://adversarialglue.github.io/)
- [AdvGLUE Dataset](https://huggingface.co/datasets/AI-Secure/adv_glue)
- [BenchScope: Benchmark Correlation Analysis](https://arxiv.org/pdf/2603.29357)
- [ECE Implementation Guide](https://towardsdatascience.com/expected-calibration-error-ece-a-step-by-step-visual-explanation-with-python-code-c3e9aa12937d/)

---

*Generated by Phase 2C Experiment Design*
*Next: Phase 3 Implementation Planning*
