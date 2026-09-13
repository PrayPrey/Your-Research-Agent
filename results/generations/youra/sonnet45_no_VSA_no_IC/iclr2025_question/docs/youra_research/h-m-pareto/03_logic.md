# Logic Specification: h-m-pareto

**Date:** 2026-08-20  
**Author:** yoon303b@gmail.com  
**Hypothesis:** Pareto frontier analysis for UQ methods  
**Phase:** 3 - Implementation Planning

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New API design - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Applied Patterns

**Applied**: Standard sklearn AUROC computation, scipy statistical tests, PyTorch MC dropout

---

## Module 1: Calibration

### API Signatures

```python
def calibrate_temperature(
    model: torch.nn.Module,
    cal_loader: DataLoader,
    temperature_range: Tuple[float, float] = (0.5, 5.0),
    n_steps: int = 50
) -> float:
    """Grid search for optimal temperature. Returns T_opt."""
    ...

def calibrate_conformal(
    model: torch.nn.Module,
    cal_loader: DataLoader,
    alpha: float = 0.1
) -> float:
    """Compute conformal threshold. Returns tau for 90% coverage."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [N, C] | Raw model outputs, C=vocab_size |
| temperature | scalar | Grid search over [0.5, 5.0] |
| tau | scalar | Alpha-quantile threshold |

### Pseudo-code

```
calibrate_temperature:
1. For T in linspace(0.5, 5.0, 50):
   a. scaled_logits = logits / T  # [N, C]
   b. nll = -log(softmax(scaled_logits)[true_class])
   c. Store (T, mean(nll))
2. Return argmin(nll)

calibrate_conformal:
1. scores = 1 - max(softmax(logits))  # [N]
2. tau = quantile(scores, 1-alpha)  # 90th percentile
3. Return tau
```

---

## Module 2: UQ Methods

### API Signatures

```python
def apply_temp_scaling(
    model: torch.nn.Module,
    dataset: Dataset,
    temperature: float
) -> Tuple[Tensor, List[str]]:
    """
    Apply temperature scaling.
    Returns: (uncertainty_scores [N], predictions [N])
    """
    ...

def apply_conformal(
    model: torch.nn.Module,
    dataset: Dataset,
    tau: float
) -> Tuple[Tensor, List[str]]:
    """
    Apply conformal prediction.
    Returns: (uncertainty_scores [N], predictions [N])
    """
    ...

def apply_mc_dropout(
    model: torch.nn.Module,
    dataset: Dataset,
    n_passes: int,
    dropout_rate: float = 0.1
) -> Tuple[Tensor, List[str]]:
    """
    MC dropout with k passes.
    Returns: (uncertainty_scores [N], predictions [N])
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | [N, C] | Single forward pass |
| probs | [N, C] | softmax(logits / T) |
| mc_logits | [k, N, C] | k MC dropout passes |
| variance | [N, C] | var(mc_logits, dim=0) |
| uncertainty | [N] | 1 - max(probs) or mean(variance) |

### Pseudo-code

```
apply_temp_scaling:
1. logits = model(inputs)  # [N, C]
2. probs = softmax(logits / temperature)  # [N, C]
3. uncertainty = 1 - max(probs, dim=1)  # [N]
4. predictions = decode(argmax(logits))  # [N]
5. Return (uncertainty, predictions)

apply_mc_dropout:
1. Enable dropout: model.train() but freeze BatchNorm
2. For i in range(k):
   a. logits_i = model(inputs)  # [N, C]
   b. Store logits_i
3. mc_logits = stack(logits_i)  # [k, N, C]
4. uncertainty = mean(var(mc_logits, dim=0), dim=1)  # [N]
5. predictions = decode(argmax(mean(mc_logits, dim=0)))  # [N]
6. Return (uncertainty, predictions)
```

---

## Module 3: AUROC Computation

### API Signatures

```python
def evaluate_correctness(
    predictions: List[str],
    correct_answers: List[List[str]]
) -> Tensor:
    """
    Fuzzy match predictions against ground truth.
    Returns: binary correctness labels [N]
    """
    ...

def compute_auroc(
    uncertainty_scores: Tensor,
    correctness_labels: Tensor
) -> float:
    """
    AUROC for selective prediction.
    Returns: scalar in [0, 1]
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| uncertainty_scores | [N] | Higher = more uncertain |
| correctness_labels | [N] | Binary: 1=correct, 0=incorrect |
| auroc | scalar | roc_auc_score output |

### Pseudo-code

```
evaluate_correctness:
1. For each (pred, answer_list):
   a. If any(ans in pred.lower() for ans in answer_list):
      b. label = 1
   c. Else: label = 0
2. Return tensor(labels)  # [N]

compute_auroc:
1. from sklearn.metrics import roc_auc_score
2. Return roc_auc_score(correctness_labels, uncertainty_scores)
```

---

## Module 4: Pareto Frontier

### API Signatures

```python
def construct_pareto_frontier(
    results: Dict[str, Tuple[float, float, float]],
    alpha: float = 0.05,
    n_seeds: int = 3
) -> List[str]:
    """
    Args:
        results: {method: (cost, auroc_mean, auroc_std)}
        alpha: Significance level for paired t-test
        n_seeds: Number of random seeds
    Returns:
        pareto_set: List of non-dominated method names
    """
    ...

def dominance_check(
    method_i: Tuple[float, float, float],
    method_j: Tuple[float, float, float],
    alpha: float,
    n_seeds: int
) -> bool:
    """
    Check if j dominates i.
    Returns: True if cost_j <= cost_i AND auroc_j > auroc_i (p < alpha)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| costs | [6] | Per method |
| auroc_means | [6] | Per method |
| auroc_stds | [6] | Per method |
| auroc_samples | [n_seeds] | Generated from (mean, std) |

### Pseudo-code

```
dominance_check:
1. cost_i, auroc_i, std_i = method_i
2. cost_j, auroc_j, std_j = method_j
3. If cost_j > cost_i: return False  # Not cheaper
4. If auroc_j <= auroc_i: return False  # Not better
5. Generate samples:
   a. samples_i = [auroc_i + N(0, std_i) for _ in range(n_seeds)]
   b. samples_j = [auroc_j + N(0, std_j) for _ in range(n_seeds)]
6. t_stat, p_val = ttest_rel(samples_j, samples_i)
7. Return p_val < alpha

construct_pareto_frontier:
1. pareto_set = []
2. For each method_i in results:
   a. dominated = False
   b. For each method_j in results:
      i. If i == j: continue
      ii. If dominance_check(method_i, method_j, alpha, n_seeds):
          dominated = True
          break
   c. If not dominated:
      pareto_set.append(method_i)
3. Return pareto_set
```

---

## Module 5: Statistical Tests

### API Signatures

```python
def paired_t_test(
    samples_a: Tensor,
    samples_b: Tensor
) -> Tuple[float, float]:
    """
    Paired t-test for AUROC difference.
    Returns: (t_statistic, p_value)
    """
    ...

def spearman_correlation(
    uncertainty_scores: Tensor,
    correctness_labels: Tensor
) -> Tuple[float, float]:
    """
    Spearman rank correlation.
    Returns: (rho, p_value)
    """
    ...
```

### Pseudo-code

```
paired_t_test:
1. from scipy.stats import ttest_rel
2. Return ttest_rel(samples_a, samples_b)

spearman_correlation:
1. from scipy.stats import spearmanr
2. incorrectness = 1 - correctness_labels
3. Return spearmanr(uncertainty_scores, incorrectness)
```

---

## Module 6: Main Orchestration

### API Signatures

```python
def run_pareto_analysis(
    model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
    seeds: List[int] = [42, 123, 456],
    output_dir: str = "results"
) -> Dict[str, Any]:
    """
    Full pipeline: calibration -> UQ methods -> AUROC -> Pareto frontier.
    Returns: {pareto_set, results, figures}
    """
    ...
```

### Pseudo-code

```
run_pareto_analysis:
1. Load model, TruthfulQA, HaluEval
2. Calibration:
   a. T_opt = calibrate_temperature(model, HaluEval)
   b. tau = calibrate_conformal(model, HaluEval)
3. For each seed in [42, 123, 456]:
   a. For each method in [temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10]:
      i. uncertainty, preds = apply_method(model, TruthfulQA)
      ii. correctness = evaluate_correctness(preds, TruthfulQA.correct_answers)
      iii. auroc = compute_auroc(uncertainty, correctness)
      iv. Store (method, seed, auroc)
4. Aggregate:
   a. For each method:
      results[method] = (cost, mean(auroc), std(auroc))
5. pareto_set = construct_pareto_frontier(results)
6. Generate figures (scatter, bar chart, trade-off curves)
7. Save results, pareto_set, figures
8. Return {pareto_set, results, figures}
```

---

## Validation Checks

```python
# Verification code from 02c_experiment_brief.md
assert len(results) == 6, f"Expected 6 methods, got {len(results)}"
assert all(0 <= auroc <= 1.0 for _, auroc, _ in results.values()), "AUROC out of bounds"
assert len(pareto_set) >= 1, "Empty Pareto set - impossible"

# Cost ordering
costs = [results[m][0] for m in ["temperature_scaling", "mc_dropout_k1", "mc_dropout_k3", "mc_dropout_k5", "mc_dropout_k10"]]
assert costs == sorted(costs), "Cost values not increasing"

# H1 check
mc_k5_auroc = results["mc_dropout_k5"][1]
max_auroc = max(auroc for _, auroc, _ in results.values())
assert mc_k5_auroc >= max_auroc - 0.05, "H1 violation: MC k=5 not competitive"
```

---

## Dependencies

```python
# Core
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Metrics
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import spearmanr, ttest_rel

# Utils
import numpy as np
from typing import Tuple, List, Dict, Any
```

---

*Next: Phase 4 - Implementation based on these exact signatures*
