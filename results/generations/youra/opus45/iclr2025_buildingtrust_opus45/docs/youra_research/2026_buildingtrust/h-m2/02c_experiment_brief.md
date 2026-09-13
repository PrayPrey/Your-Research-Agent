# Experiment Design: h-m2

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2x2 prompt controls.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing the percentile-normalized monotonicity attenuation mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (PASS - margin inflation confirmed)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (COMPLETED)

### Gate Condition
β_percentile_instruct < β_percentile_base with p < 0.05 under 2x2 prompt design controls (zero-shot/few-shot × base/instruct).

---

## Continuation Context

**Building on H-M1 Results:**
- H-M1 confirmed margin inflation for incorrect predictions (Qwen 3.06x, Mistral 16.79x)
- Both families show statistically significant inflation (p < 0.001)
- This margin inflation should manifest as reduced percentile-normalized monotonicity

### Previous Hypothesis Results (if applicable)
| Family | Base E[m|inc] | Inst E[m|inc] | Inflation Ratio | Cohen's d |
|--------|---------------|---------------|-----------------|-----------|
| Qwen | 0.9597 | 2.9327 | 3.06x | 1.009 |
| Mistral | 0.4682 | 7.8606 | 16.79x | 1.848 |

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "logistic regression confidence calibration LLM"**
- Limited direct matches in knowledge base
- Related paper: QLoRA (2305.14314) - discusses LLM finetuning but not calibration analysis

**Query 2: "percentile normalization calibration monotonicity"**
- No direct matches for percentile-normalized calibration methods
- General pattern: Normalization techniques are common in diffusion models but not in calibration literature in KB

**Query 3: "MMLU AUROC discriminative quality"**
- OpenReview paper (M3Y74vmsMcY) - large calibration-related discussion
- Key insight: AUROC is a standard metric for discriminative quality evaluation

**Query 4: "RLHF alignment preference optimization"**
- PEFT/LoRA documentation discusses preference-based training
- Related hyperparameters: LR 1e-4 to 2e-4, batch size scaling with model size

**Summary of Archon Knowledge Base Findings:**
- The hypothesis mechanism (percentile-normalized logistic regression for LLM calibration) is **novel** with limited prior art in KB
- Standard approach: Use `scipy.stats.zscore()` for normalization, `sklearn.linear_model.LogisticRegression` for slope estimation
- Bootstrap confidence intervals standard for statistical inference
- MMLU is well-established benchmark for MCQ evaluation

### Archon Code Examples

**Query 1: "logistic regression sklearn statsmodels"**
- No direct sklearn logistic regression examples found
- Diffusers/HuggingFace pipeline examples dominant in KB

**Query 2: "scipy z-score normalization"**
- torchmetrics examples for FID/CLIP score computation
- Image normalization patterns: `(x / 127.5) - 1.0` for [-1, 1] range

**Relevant Code Pattern (inferred from KB patterns):**
```python
from scipy.stats import zscore
from sklearn.linear_model import LogisticRegression
import numpy as np

# Z-score normalize margins
margins_normalized = zscore(margins)

# Fit logistic regression: Pr(correct) = σ(α + β·z-score(margin))
lr = LogisticRegression(solver='lbfgs')
lr.fit(margins_normalized.reshape(-1, 1), correctness)
beta_percentile = lr.coef_[0][0]
```

**Note:** Limited direct code examples for this specific methodology. Implementation will rely on standard sklearn/scipy patterns.

### Exa GitHub Implementations

**Query 1: "LLM confidence calibration logistic regression AUROC GitHub implementation"**

**Repository 1**: [activatedgeek/calibration-tuning](https://github.com/activatedgeek/calibration-tuning) (⭐ 53)
- **URL**: https://github.com/activatedgeek/calibration-tuning
- **Relevance**: Direct calibration of LLMs with base vs instruct comparison
- **Key Features**:
  - Fine-tuned models for calibration (Llama 2, Mistral)
  - Base vs Chat/Instruct model comparison
  - Multiple-choice QA evaluation
- **Models Available**: Llama 2 7B/13B (base + chat), Mistral 7B (base + instruct)
- **Dataset**: Custom 20K generation dataset labeled for correctness

**Repository 2**: [shuoli90/Rank-Calibration](https://github.com/shuoli90/Rank-Calibration) (⭐ 13)
- **URL**: https://github.com/shuoli90/Rank-Calibration
- **Relevance**: Rank-based calibration assessment framework
- **Key Insight**: "Higher uncertainty should imply lower generation quality"
- **Metrics**: Rank-calibration quantifies deviations from ideal confidence-correctness relationship
- **Code Pattern**: Python metrics implementation for calibration assessment

**Repository 3**: [prateekchhikara/llms-calibration](https://github.com/prateekchhikara/llms-calibration) (⭐ 19)
- **URL**: https://github.com/prateekchhikara/llms-calibration
- **Relevance**: ECE (Expected Calibration Error) analysis for LLMs
- **Paper**: "Mind the Confidence Gap" (TMLR published)
- **Key Insight**: Models can be overconfident in incorrect answers
- **Datasets**: Uses standard benchmarks including TruthfulQA

**Repository 4**: [appier-research/llm-calibration](https://github.com/appier-research/llm-calibration) (⭐ 4)
- **URL**: https://github.com/appier-research/llm-calibration
- **Relevance**: "On Calibration of LLMs: From Response To Capability"
- **Datasets**: MMLU, GPQA, GSM8K, Math-500
- **Setup**: Uses `uv` package manager, supports repeated sampling for accuracy estimation

**Query 2: Bootstrap Confidence Intervals for Logistic Regression**

**Key Code Patterns Found:**

```python
# Bootstrap for Logistic Regression Coefficients
from sklearn.utils import resample
from sklearn.linear_model import LogisticRegression
import numpy as np

n_iterations = 1000
betas = []
for i in range(n_iterations):
    sample_idx = np.random.choice(len(X), len(X), replace=True)
    X_boot, y_boot = X[sample_idx], y[sample_idx]
    lr = LogisticRegression(solver='lbfgs')
    lr.fit(X_boot, y_boot)
    betas.append(lr.coef_[0][0])

# 95% Confidence Interval
ci_lower = np.percentile(betas, 2.5)
ci_upper = np.percentile(betas, 97.5)
```

**Statsmodels Alternative (with built-in CI):**
```python
import statsmodels.api as sm
model = sm.Logit(y, sm.add_constant(X)).fit()
conf_interval = model.conf_int(alpha=0.05)  # 95% CI
```

**MMLU Evaluation Framework:**
- DeepEval library: `from deepeval.benchmarks import MMLU`
- EleutherAI lm-evaluation-harness: Standard MMLU evaluation
- Key insight: MMLU scoring is accuracy-based (proportion of correct letter answers)

**Serena Analysis Needed**: false (Code patterns are clear - standard sklearn/statsmodels)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a **novel methodology** (percentile-normalized logistic regression for LLM calibration analysis). No direct author implementation exists. Implementation will use standard statistical libraries.

**Recommended Implementation Path:**
- Primary: sklearn LogisticRegression + scipy.stats.zscore + bootstrap CI
- Fallback: statsmodels Logit with built-in conf_int()
- Justification: Standard statistical packages, well-documented APIs, reproducible

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard sklearn/statsmodels patterns for logistic regression with bootstrap confidence intervals are well-documented and do not require semantic code analysis.

**Key Implementation Patterns Identified:**
1. `scipy.stats.zscore()` for percentile normalization
2. `sklearn.linear_model.LogisticRegression` for β coefficient estimation
3. Bootstrap resampling (1000 iterations) for confidence interval estimation
4. `statsmodels.Logit.fit().conf_int()` as alternative with built-in CI

---

## Experiment Specification

### Dataset

**Dataset**: MMLU (Massive Multitask Language Understanding)
**Type**: standard (real benchmark dataset)
**Source**: HuggingFace Hub

| Field | Value |
|-------|-------|
| **Identifier** | cais/mmlu |
| **Split** | test |
| **Sample Count** | 14,042 |
| **Format** | Multiple-choice (4 options) |
| **Domains** | 57 subjects (humanities, social sciences, STEM, other) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`
- Code:
```python
from datasets import load_dataset

# Load MMLU test set (all 57 subjects)
mmlu = load_dataset("cais/mmlu", "all", split="test")
# Total: 14,042 samples

# Structure per sample:
# - question: str
# - choices: List[str] (4 options)
# - answer: str ('A', 'B', 'C', or 'D')
```

**Note: Continuation Experiment - Data Reuse**

This hypothesis does NOT require new model inference. H-M2 reuses cached inference results from H-E1:
- **Cache Location**: `h-e1/cache/` (JSON files with logit margins, correctness labels)
- **Data Available**: Logit margins for all 14,042 MMLU test samples per model
- **Rationale**: Enables controlled comparison - same inference data, different statistical analysis

### Models

#### Baseline Model

**Architecture**: Qwen2.5-7B, Mistral-7B (base + instruct pairs)
**Type**: Causal LLM
**Pretrained**: Yes (HuggingFace Hub)

| Model Family | Base Model | Instruct Model |
|--------------|------------|----------------|
| Qwen | Qwen/Qwen2.5-7B | Qwen/Qwen2.5-7B-Instruct |
| Mistral | mistralai/Mistral-7B-v0.1 | mistralai/Mistral-7B-Instruct-v0.1 |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (NOT NEEDED - reusing H-E1 cache)
- Identifier: See table above
- Code:
```python
# NOT NEEDED FOR H-M2 - Using cached inference from H-E1
# Cache format: {"sample_id": ..., "margins": [...], "correct": bool, ...}

import json
from pathlib import Path

def load_cached_results(model_name: str, hypothesis_folder: str = "../h-e1"):
    """Load cached inference results from H-E1."""
    cache_path = Path(hypothesis_folder) / "cache" / f"{model_name}_results.json"
    with open(cache_path) as f:
        return json.load(f)
```

**Modifications for Hypothesis**: None (analysis only, no model modifications)

#### Proposed Model

**Architecture:** Statistical Reanalysis of H-E1 Cached Data with Percentile Normalization

**Core Mechanism Implementation:**

```python
# Core Mechanism: Percentile-Normalized Monotonicity Analysis
# Based on: sklearn LogisticRegression + scipy zscore + bootstrap CI
# Source: Phase 2B verification protocol

import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample

def compute_beta_percentile(margins: np.ndarray, correctness: np.ndarray) -> float:
    """
    Compute β coefficient from logistic regression on z-score normalized margins.

    Args:
        margins: (N,) logit margin values (max_logit - second_max_logit)
        correctness: (N,) binary correctness labels (0 or 1)
    Returns:
        beta_percentile: slope coefficient from Pr(correct) = σ(α + β·z(margin))
    """
    # Step 1: Z-score normalize margins within model
    margins_normalized = zscore(margins)

    # Step 2: Fit logistic regression
    lr = LogisticRegression(solver='lbfgs', max_iter=1000)
    lr.fit(margins_normalized.reshape(-1, 1), correctness)

    # Step 3: Extract β coefficient
    beta_percentile = lr.coef_[0][0]
    return beta_percentile

def bootstrap_ci(margins: np.ndarray, correctness: np.ndarray,
                 n_iterations: int = 1000, alpha: float = 0.05) -> tuple:
    """
    Bootstrap 95% CI for β_percentile coefficient.

    Returns:
        (beta_mean, ci_lower, ci_upper)
    """
    betas = []
    for i in range(n_iterations):
        idx = resample(np.arange(len(margins)), replace=True)
        beta = compute_beta_percentile(margins[idx], correctness[idx])
        betas.append(beta)

    beta_mean = np.mean(betas)
    ci_lower = np.percentile(betas, 100 * alpha / 2)
    ci_upper = np.percentile(betas, 100 * (1 - alpha / 2))
    return beta_mean, ci_lower, ci_upper
```

### Training Protocol

**Type**: Statistical Reanalysis (No Training Required)

This is a statistical reanalysis hypothesis - no model training or fine-tuning is performed.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Data Source** | H-E1 cached inference results | Enables controlled comparison |
| **Sample Size** | 14,042 per model | Full MMLU test set |
| **Bootstrap Iterations** | 1,000 | Standard for CI estimation |
| **Random Seed** | 42 | Reproducibility |

**2×2 Factorial Design**:
- Factor 1: Model Type (base vs. instruct)
- Factor 2: Prompt Format (zero-shot vs. few-shot) [if available in H-E1 cache]

### Evaluation

**Primary Metrics**:

| Metric | Definition | Gate Criterion |
|--------|------------|----------------|
| **β_percentile** | Slope from Pr(correct) = σ(α + β·z(margin)) | β_instruct < β_base |
| **p-value** | Bootstrap-based two-sample test | p < 0.05 |
| **Effect Size** | Δβ = β_base - β_instruct | Report magnitude |

**Statistical Test**:
- Bootstrap difference test: Compute β_base - β_instruct across bootstrap samples
- p-value: Proportion of bootstrap samples where Δβ ≤ 0
- 95% CI for Δβ via percentile method

**Success Criteria** (MUST_WORK Gate):
1. **Primary**: β_percentile_instruct < β_percentile_base (direction)
2. **Primary**: p < 0.05 (statistical significance)
3. **Secondary**: Effect persists across 2×2 prompt conditions

**Expected Results** (from H-M1 findings):
- H-M1 showed 3-17x margin inflation for incorrect predictions
- Expect β_instruct < β_base due to reduced discriminability

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (correct/incorrect)
- Library: sklearn.linear_model, scipy.stats, sklearn.utils
- Code:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from scipy.stats import zscore
from sklearn.utils import resample
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: β_percentile comparison bar chart with 95% CIs

#### Additional Figures (LLM Autonomous)

1. **β_percentile Comparison Bar Chart**: Base vs Instruct for each model family with error bars
2. **Bootstrap Distribution Plot**: Histograms of β_base and β_instruct from bootstrap samples
3. **Logistic Regression Curves**: Pr(correct) vs z-score(margin) for each condition
4. **2×2 Factorial Heatmap**: β values across prompt format × model type conditions
5. **Forest Plot**: Effect sizes (Δβ) with CIs across model families

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. β_percentile_instruct < β_percentile_base with p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: LLM Calibration Research
- **Type**: Knowledge base article
- **Query Used**: "logistic regression confidence calibration LLM"
- **Relevance**: Limited direct matches - confirms novelty of percentile normalization approach
- **Key Insights**:
  - QLoRA paper (2305.14314) discusses LLM finetuning hyperparameters
  - Standard calibration methods (ECE) well-documented but not percentile-normalized slope
- **Used For**: Confirming methodological novelty

**Source 2**: Bootstrap Confidence Intervals
- **Type**: Knowledge base article
- **Query Used**: "bootstrap confidence interval statistical test"
- **Relevance**: Standard statistical methodology for CI estimation
- **Key Insights**:
  - 1000 bootstrap iterations is standard
  - Percentile method for CI bounds (2.5%, 97.5%)
- **Used For**: Training protocol and evaluation specification

### B. GitHub Implementations (Exa)

**Repository 1**: [activatedgeek/calibration-tuning](https://github.com/activatedgeek/calibration-tuning) (⭐ 53)
- **URL**: https://github.com/activatedgeek/calibration-tuning
- **Query Used**: "LLM confidence calibration logistic regression AUROC GitHub implementation"
- **Relevance**: Direct calibration work on base vs instruct models
- **Key Code**: Fine-tuned Llama 2, Mistral models for calibration
- **Used For**: Model selection validation (same families used)

**Repository 2**: [shuoli90/Rank-Calibration](https://github.com/shuoli90/Rank-Calibration) (⭐ 13)
- **URL**: https://github.com/shuoli90/Rank-Calibration
- **Query Used**: Same as above
- **Relevance**: Rank-based calibration assessment framework
- **Key Insight**: "Higher uncertainty should imply lower generation quality"
- **Used For**: Conceptual framework for monotonicity analysis

**Repository 3**: [prateekchhikara/llms-calibration](https://github.com/prateekchhikara/llms-calibration) (⭐ 19)
- **URL**: https://github.com/prateekchhikara/llms-calibration
- **Query Used**: Same as above
- **Relevance**: ECE analysis for LLMs (TMLR published)
- **Used For**: Related work context

**Code Source 1**: Bootstrap CI for Logistic Regression
- **URL**: https://stats.stackexchange.com/questions/183230/
- **Query Used**: "sklearn LogisticRegression bootstrap confidence interval scipy zscore"
- **Key Code**:
```python
from sklearn.utils import resample
from sklearn.linear_model import LogisticRegression

betas = []
for i in range(1000):
    idx = resample(np.arange(len(X)), replace=True)
    lr = LogisticRegression(solver='lbfgs')
    lr.fit(X[idx], y[idx])
    betas.append(lr.coef_[0][0])

ci_lower = np.percentile(betas, 2.5)
ci_upper = np.percentile(betas, 97.5)
```
- **Used For**: Core mechanism pseudo-code generation

**Code Source 2**: MMLU Dataset Loading
- **URL**: https://huggingface.co/datasets/cais/mmlu
- **Query Used**: "MMLU dataset huggingface load_dataset cais/mmlu python"
- **Key Code**:
```python
from datasets import load_dataset
mmlu = load_dataset("cais/mmlu", "all", split="test")  # 14,042 samples
```
- **Used For**: Dataset specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.
Standard sklearn/statsmodels/scipy patterns do not require semantic code analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports - h-e1, h-m1
- **Files**: `h-e1/04_validation.md`, `h-m1/04_validation.md`
- **Reused Components**:
  - **Dataset**: MMLU test set (14,042 samples) - cached inference results
  - **Models**: Qwen2.5-7B, Mistral-7B (base + instruct) - cached logit margins
  - **Correctness Labels**: From H-E1 evaluation
- **Why Reused**: Enables controlled experiment (same data, different analysis)

**H-M1 Key Findings** (prerequisite):
| Family | Base E[m|inc] | Inst E[m|inc] | Inflation Ratio | p-value |
|--------|---------------|---------------|-----------------|---------|
| Qwen | 0.9597 | 2.9327 | 3.06x | <0.001 |
| Mistral | 0.4682 | 7.8606 | 16.79x | <0.001 |

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MMLU) | HuggingFace | Code Source 2 |
| Models (Qwen, Mistral) | Previous Context | h-e1, h-m1 |
| Cached Inference Data | Previous Context | h-e1/cache/ |
| β_percentile Methodology | Custom (Novel) | Phase 2B Protocol |
| Bootstrap CI | GitHub/StackOverflow | Code Source 1 |
| LogisticRegression | sklearn | Standard library |
| Z-score Normalization | scipy.stats | Standard library |
| Statistical Test | Bootstrap Difference | Derived from Code Source 1 |
| Success Criteria | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24T17:14:17Z

### Workflow History for This Hypothesis
- 2026-03-24T17:14:17Z: h-m2 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
