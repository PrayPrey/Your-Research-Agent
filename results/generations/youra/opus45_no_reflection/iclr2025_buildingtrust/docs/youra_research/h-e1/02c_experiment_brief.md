# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** A statistically significant positive correlation (r > 0.5, p < 0.05) exists between factuality error detection accuracy (TruthfulQA MC1) and adversarial robustness (1 - ASR on TextFooler) across 12+ open-weight LLMs.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - Foundation hypothesis

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation)

### Gate Condition
**MUST_WORK Gate**: If r < 0.3 after controlling for scale → ABANDON entire research direction. If 0.3 < r < 0.5 → PIVOT to investigate confounds.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct matches for TruthfulQA/TextFooler correlation studies in Archon KB. Related findings:
- Quantization techniques for LLM inference (bitsandbytes, optimum-quanto)
- LoRA adapter configurations for model fine-tuning
- General evaluation framework patterns

### Archon Code Examples

Limited relevant code examples. Primary implementation will rely on established frameworks:
- EleutherAI lm-evaluation-harness for TruthfulQA
- QData TextAttack for adversarial evaluation

### Exa GitHub Implementations

**TruthfulQA Evaluation:**
- Repository: `EleutherAI/lm-evaluation-harness` (12K+ stars)
- Task: `truthfulqa_mc1` - Multiple-choice single answer
- Dataset: 817 questions across 38 categories
- Metric: Accuracy (percentage of correct selections)
- Citation: Lin et al., 2022 (ACL)

**TextFooler Attack:**
- Repository: `QData/TextAttack` 
- Recipe: `textfooler` (Jin et al., 2019)
- Components: Word embedding swap, USE semantic similarity, POS checking
- Metric: Attack Success Rate (ASR)
- Command: `textattack attack --recipe textfooler --model <model> --num-examples 1000`

**ECE Calibration:**
- Standard implementation: 10 equal-frequency bins
- Reference: Guo et al., 2017 "On Calibration of Modern Neural Networks"
- Libraries: sklearn.calibration, custom implementations
- Key metric: ECE = E[|P(correct|confidence) - confidence|]

### Implementation Priority Assessment

**CRITICAL: For this correlation study, use official evaluation frameworks**

**Primary Implementation Path:**
- TruthfulQA: EleutherAI/lm-evaluation-harness (official benchmark backend)
- TextFooler: QData/TextAttack (reference implementation)
- ECE: Custom implementation following Guo et al. (2017)

**Recommended Implementation Path:**
- Primary: lm-evaluation-harness + TextAttack frameworks
- Fallback: HuggingFace datasets + custom evaluation scripts
- Justification: Official implementations ensure reproducibility and comparability with published baselines

### Code Analysis (Serena MCP)

*Skipped* - No local codebase to analyze. This is a new correlation study using external frameworks.

---

## Experiment Specification

### Dataset

**Dataset 1: TruthfulQA**
- **Name:** TruthfulQA (Lin et al., 2022)
- **Source:** HuggingFace Datasets (`truthful_qa`)
- **Type:** standard
- **Split:** validation (817 questions, full test set)
- **Task:** Multiple-choice single answer (MC1)
- **Categories:** 38 categories (health, law, finance, science, etc.)
- **Preprocessing:** None required (benchmark format)

**Dataset 2: SST-2**
- **Name:** Stanford Sentiment Treebank v2
- **Source:** HuggingFace Datasets (`glue`, `sst2`)
- **Type:** standard
- **Split:** validation (872 samples) + test subset for adversarial attack
- **Task:** Binary sentiment classification
- **Sample Size:** 1000+ samples per model for TextFooler attack
- **Preprocessing:** Standard tokenization

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `truthful_qa` (multiple_choice config), `glue/sst2`
- Code:
```python
from datasets import load_dataset

# TruthfulQA
truthfulqa = load_dataset("truthful_qa", "multiple_choice", split="validation")
# 817 questions total

# SST-2 for adversarial attack
sst2 = load_dataset("glue", "sst2", split="validation")
# Use full validation set (872 samples) + additional from train if needed
```

### Models

#### Baseline Model

**Model Pool (12+ Open-Weight LLMs):**

| Family | Models | Parameters |
|--------|--------|------------|
| Llama-2 | 7B, 13B, 70B | 7B, 13B, 70B |
| Llama-3 | 8B, 70B | 8B, 70B |
| Mistral | 7B-v0.1, 7B-Instruct | 7B |
| FLAN-T5 | base, large, xl | 250M, 780M, 3B |
| Phi | Phi-2, Phi-3-mini | 2.7B, 3.8B |

**Total:** 12 models across 5 families

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: See model_ids below
- Code:
```python
MODEL_IDS = [
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-70b-hf",
    "meta-llama/Meta-Llama-3-8B",
    "meta-llama/Meta-Llama-3-70B",
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "google/flan-t5-base",
    "google/flan-t5-large",
    "google/flan-t5-xl",
    "microsoft/phi-2",
    "microsoft/Phi-3-mini-4k-instruct",
]
```

#### Proposed Model

**Architecture:** Correlation analysis across model pool (no new model architecture)

**Core Mechanism Implementation:**

```python
# Pseudo-code: Factuality-Robustness Correlation Analysis (10-30 lines)

import numpy as np
from scipy import stats
from lm_eval import evaluator
from textattack import Attacker, AttackArgs
from textattack.attack_recipes import TextFoolerJin2019

def compute_correlation(models: list[str]) -> dict:
    """Compute correlation between TruthfulQA MC1 and adversarial robustness."""
    
    results = {"model": [], "mc1_acc": [], "robustness": [], "log_params": []}
    
    for model_id in models:
        # Step 1: TruthfulQA MC1 evaluation (lm-evaluation-harness)
        mc1_result = evaluator.simple_evaluate(
            model="hf",
            model_args=f"pretrained={model_id}",
            tasks=["truthfulqa_mc1"],
            batch_size=4
        )
        mc1_acc = mc1_result["results"]["truthfulqa_mc1"]["acc"]
        
        # Step 2: TextFooler attack on SST-2 (TextAttack)
        model_wrapper = load_model_for_attack(model_id)
        attack = TextFoolerJin2019.build(model_wrapper)
        attack_args = AttackArgs(num_examples=1000, disable_stdout=True)
        attacker = Attacker(attack, sst2_dataset, attack_args)
        attack_results = attacker.attack_dataset()
        asr = attack_results.attack_success_rate
        robustness = 1 - asr  # Higher is better
        
        # Store results
        results["model"].append(model_id)
        results["mc1_acc"].append(mc1_acc)
        results["robustness"].append(robustness)
        results["log_params"].append(np.log10(get_param_count(model_id)))
    
    # Step 3: Compute Pearson correlation
    r, p_value = stats.pearsonr(results["mc1_acc"], results["robustness"])
    
    # Step 4: Bootstrap 95% CI
    bootstrap_rs = []
    for _ in range(1000):
        idx = np.random.choice(len(models), len(models), replace=True)
        mc1_boot = [results["mc1_acc"][i] for i in idx]
        rob_boot = [results["robustness"][i] for i in idx]
        r_boot, _ = stats.pearsonr(mc1_boot, rob_boot)
        bootstrap_rs.append(r_boot)
    ci_lower, ci_upper = np.percentile(bootstrap_rs, [2.5, 97.5])
    
    # Step 5: Partial correlation controlling for scale
    partial_r = compute_partial_correlation(
        results["mc1_acc"], results["robustness"], results["log_params"]
    )
    
    return {
        "r": r, "p_value": p_value,
        "ci_95": (ci_lower, ci_upper),
        "partial_r": partial_r,
        "n_models": len(models)
    }
```

### Training Protocol

**No training required** - This is an evaluation/correlation study.

**Evaluation Protocol:**
1. **TruthfulQA MC1:** Run lm-evaluation-harness on all 12 models
   - Batch size: 4 (adjust for GPU memory)
   - Full test set: 817 questions
   - Metric: Accuracy (proportion correct)

2. **TextFooler Attack:** Run TextAttack on all 12 models
   - Dataset: SST-2 validation (1000+ samples)
   - Attack recipe: textfooler
   - Metric: Attack Success Rate (ASR)
   - Robustness: 1 - ASR

3. **Correlation Analysis:**
   - Pearson correlation with bootstrap CI
   - Partial correlation controlling for log(params)
   - Within-family correlation checks

### Evaluation

**Primary Metrics:**
| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| Pearson r | Correlation between MC1 and (1-ASR) | r > 0.5 |
| p-value | Statistical significance | p < 0.05 |
| Bootstrap 95% CI | Confidence interval for r | CI excludes 0.3 |

**Secondary Metrics:**
| Metric | Definition | Purpose |
|--------|------------|---------|
| Partial r | Correlation controlling for log(params) | Control for scale confound |
| Within-family r | Correlation within model families | Check consistency |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Correlation analysis
- Library: scipy.stats (pearsonr, spearmanr), numpy (bootstrap)
- Code:
```python
from scipy import stats
import numpy as np

def evaluate_hypothesis(mc1_scores, robustness_scores, log_params):
    # Primary: Pearson correlation
    r, p = stats.pearsonr(mc1_scores, robustness_scores)
    
    # Bootstrap CI
    bootstrap_rs = []
    n = len(mc1_scores)
    for _ in range(1000):
        idx = np.random.choice(n, n, replace=True)
        r_boot, _ = stats.pearsonr(
            [mc1_scores[i] for i in idx],
            [robustness_scores[i] for i in idx]
        )
        bootstrap_rs.append(r_boot)
    ci = np.percentile(bootstrap_rs, [2.5, 97.5])
    
    # Partial correlation (controlling for scale)
    # Using regression residuals method
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression()
    mc1_resid = mc1_scores - lr.fit([[p] for p in log_params], mc1_scores).predict([[p] for p in log_params])
    rob_resid = robustness_scores - lr.fit([[p] for p in log_params], robustness_scores).predict([[p] for p in log_params])
    partial_r, partial_p = stats.pearsonr(mc1_resid, rob_resid)
    
    return {
        "r": r, "p_value": p, "ci_95": ci,
        "partial_r": partial_r, "partial_p": partial_p,
        "pass": r > 0.5 and p < 0.05
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of MC1 accuracy vs (1-ASR) with:
  - Points colored by model family
  - Regression line with 95% CI band
  - r and p-value annotation
  - Threshold line at r = 0.5

#### Additional Figures (LLM Autonomous)

1. **Correlation Matrix Heatmap**: MC1, (1-ASR), log(params), ECE correlations
2. **Within-Family Scatter**: Separate panels for each model family
3. **Bootstrap Distribution**: Histogram of bootstrap r values with CI markers
4. **Partial Correlation Plot**: Residualized scatter after controlling for scale

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 12 models
2. Pearson r > 0.5 between MC1 accuracy and (1-ASR)
3. p-value < 0.05
4. Bootstrap 95% CI excludes r = 0.3

**Failure Response:**
- IF r < 0.3: ABANDON - hypothesis fundamentally wrong
- IF 0.3 < r < 0.5: PIVOT - weaker correlation, investigate confounds

---

## Appendix: Reference Implementations

### TruthfulQA Evaluation
- **Repository:** https://github.com/EleutherAI/lm-evaluation-harness
- **Task:** `truthfulqa_mc1`
- **Citation:** Lin et al., 2022. "TruthfulQA: Measuring How Models Mimic Human Falsehoods." ACL 2022.
- **Command:**
```bash
lm-eval --model hf --model_args pretrained=meta-llama/Llama-2-7b-hf \
        --tasks truthfulqa_mc1 --batch_size 4
```

### TextFooler Attack
- **Repository:** https://github.com/QData/TextAttack
- **Recipe:** `textfooler` (Jin et al., 2019)
- **Citation:** Jin et al., 2019. "Is BERT Really Robust? A Strong Baseline for Natural Language Attack on Text Classification and Entailment." arXiv:1907.11932.
- **Command:**
```bash
textattack attack --model-from-huggingface <model> \
                  --dataset-from-huggingface glue:sst2 \
                  --recipe textfooler --num-examples 1000
```

### ECE Calibration (for H-M1)
- **Reference:** Guo et al., 2017. "On Calibration of Modern Neural Networks." ICML 2017.
- **Implementation:** 10 equal-frequency bins, compute |accuracy - confidence| per bin

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T13:41:12+00:00

### Workflow History for This Hypothesis
- 2026-08-18: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-08-18: Phase 2C experiment design initiated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
