# Phase 2B: Verification Plan — h-m-pareto

**Date:** 2026-08-20
**Hypothesis:** h-m-pareto (Pareto frontier exists with ≥2 optimal methods)
**Type:** Mechanism (SHOULD_WORK gate)

---

## Hypothesis Statement

Under the same conditions, if we construct the empirical Pareto frontier from (cost, AUROC) pairs for all 6 UQ methods, then at least 2 methods are Pareto-optimal (no method strictly dominates another with statistical significance p < 0.05), because different UQ mechanisms trade off calibration quality vs computational cost at different efficiency zones.

---

## Prerequisites

**Prerequisite Hypothesis:** h-m-integrated
**Status:** VALIDATED (PASSED)
**Dependency:** Assumes UQ pipeline produces valid uncertainty rankings (AUROC > 0.55, Spearman ρ > 0.2)

**Gate Status:** SHOULD_WORK (non-blocking)
- Negative result (|Pareto_set| = 1) is scientifically valuable
- Confirms universal dominance (MC k=10 beats all others)
- Both outcomes advance understanding of UQ cost-performance trade-offs

---

## Verification Protocol

### Step 1: Calibration (HaluEval)

**Dataset:** HaluEval (~10k samples)
**Methods:** Temperature scaling, conformal prediction only
**Procedure:**
1. Load HaluEval calibration set
2. Temperature scaling: Grid search T ∈ [0.5, 5.0] to minimize NLL
3. Conformal prediction: Compute α-quantile threshold (α=0.1)

**Expected Output:**
- Optimal temperature T_opt (typically 1.5-3.0)
- Conformal threshold τ (90% coverage target)

### Step 2: Inference (TruthfulQA)

**Dataset:** TruthfulQA (817 questions)
**Model:** Llama-3.1-8B-Instruct (frozen)
**Seeds:** 3 (42, 123, 456)

**Procedure for each method:**

1. **Temperature Scaling**:
   - Apply T_opt from Step 1
   - Compute softmax(logits / T_opt)
   - Uncertainty = 1 - max(softmax)
   - Cost = 1.0×

2. **Conformal Prediction**:
   - Apply threshold τ from Step 1
   - Compute prediction set size
   - Uncertainty = set size (larger = more uncertain)
   - Cost = 1.0×

3. **MC Dropout (k=1,3,5,10)**:
   - Enable dropout layers (model.eval() with dropout on)
   - Run k forward passes
   - Aggregate: mean prediction, variance as uncertainty
   - Cost = k × 1.0

**Expected Output:**
- 6 × 3 = 18 (method, seed) pairs
- Each pair: (predictions, uncertainty_scores, cost)

### Step 3: AUROC Computation

**Correctness Labels:**
```python
# For each TruthfulQA question
correctness = []
for question, prediction, correct_answers in zip(questions, predictions, ground_truth):
    # Check if prediction matches any correct answer (fuzzy match)
    is_correct = any(correct in prediction for correct in correct_answers)
    correctness.append(int(is_correct))
```

**AUROC Calculation:**
```python
from sklearn.metrics import roc_auc_score

for method, seed in product(methods, seeds):
    auroc = roc_auc_score(
        y_true=correctness,  # Binary labels
        y_score=uncertainty_scores[method][seed]  # Higher = more uncertain
    )
```

**Expected Range:** 0.60-0.80 (based on h-m-integrated baseline AUROC > 0.55)

### Step 4: Pareto Frontier Construction

**Algorithm:**
```python
def construct_pareto_frontier(results, alpha=0.05):
    """
    Args:
        results: Dict[method, (cost, auroc_mean, auroc_std)]
        alpha: Significance level for paired t-test
    Returns:
        pareto_set: List of Pareto-optimal method names
    """
    pareto_set = []
    for i, method_i in enumerate(methods):
        cost_i, auroc_i, std_i = results[method_i]
        dominated = False
        
        for j, method_j in enumerate(methods):
            if i == j:
                continue
            cost_j, auroc_j, std_j = results[method_j]
            
            # Dominance: cost_j <= cost_i AND auroc_j > auroc_i (significant)
            if cost_j <= cost_i:
                # Generate AUROC samples from (mean, std) for paired t-test
                auroc_samples_i = np.random.normal(auroc_i, std_i, size=100)
                auroc_samples_j = np.random.normal(auroc_j, std_j, size=100)
                
                t_stat, p_val = ttest_rel(auroc_samples_j, auroc_samples_i)
                
                if p_val < alpha and auroc_j > auroc_i:
                    dominated = True
                    break
        
        if not dominated:
            pareto_set.append(method_i)
    
    return pareto_set
```

**Expected Output:**
- Pareto set with ≥2 methods (h-m-pareto CONFIRMED)
- OR Pareto set with 1 method (h-m-pareto FAILED, universal dominance confirmed)

---

## Success Criteria

### Primary Criterion (H3)
**Metric:** |Pareto_set| ≥ 2
**Threshold:** At least 2 methods non-dominated
**Interpretation:** Cost-performance trade-off exists

### Secondary Criteria

**H1: MC dropout k=5 highest AUROC**
- Metric: AUROC_mc_k5 ≥ AUROC_method for all other methods
- Threshold: Statistical significance p < 0.05 (paired t-test)
- Expected: AUROC_mc_k5 ≥ 0.70

**H2: Temperature scaling competitive**
- Metric: |AUROC_temp_scaling - AUROC_mc_k5| ≤ 0.05
- Threshold: Absolute difference ≤ 0.05
- Expected: Temperature scaling in Pareto set despite low cost

**Validation Check (from h-m-integrated):**
- Spearman ρ > 0.2 for all methods (uncertainty correlates with incorrectness)

---

## Expected Results

### If h-m-pareto CONFIRMED (|Pareto_set| ≥ 2)

**Expected Pareto Set:**
1. Temperature scaling (1× cost, competitive AUROC)
2. MC dropout k=5 (5× cost, highest AUROC)

**Dominated Methods:**
- MC dropout k=1: Dominated by temperature scaling (same cost, lower AUROC)
- MC dropout k=3: Dominated by MC k=5 (lower cost, same AUROC)
- MC dropout k=10: Dominated by MC k=5 (higher cost, marginal AUROC gain)
- Conformal prediction: Dominated by temperature scaling (same cost, lower AUROC for point prediction task)

**Interpretation:**
- Trade-off exists: Low-cost calibration (temp scaling) vs high-cost averaging (MC k=5)
- Diminishing returns: MC k>5 not justified (marginal gains, 2× cost increase)

### If h-m-pareto FAILED (|Pareto_set| = 1)

**Expected Pareto Set:**
1. MC dropout k=10 only (highest cost, universally dominates)

**Interpretation:**
- UQ quality monotonic in computational cost
- Averaging is the only effective mechanism (post-hoc calibration insufficient)
- No efficiency zones exist (always worth spending more compute)

---

## Visualization Plan

**Figure 1: Pareto Frontier Scatter Plot**
- X-axis: Normalized cost (1× to 10×)
- Y-axis: AUROC (0.60-0.80 range)
- Points: 6 methods with error bars (n=3 seeds)
- Highlight: Pareto-optimal (green), dominated (red)

**Figure 2: AUROC Bar Chart**
- X-axis: 6 methods (ordered by cost)
- Y-axis: AUROC mean ± std
- Threshold line: AUROC ≥ 0.70
- Significance brackets: Paired t-test results

**Figure 3: Cost vs AUROC Trade-off**
- X-axis: Cost (1× to 10×)
- Y-axis: AUROC improvement over baseline
- Lines: MC dropout (k=1,3,5,10), temp scaling, conformal

---

## Statistical Analysis

**Paired t-test for dominance:**
- Null hypothesis: AUROC_method_j ≤ AUROC_method_i
- Alternative: AUROC_method_j > AUROC_method_i
- Significance: α = 0.05
- Sample size: n = 3 seeds (low power, conservative test)

**Power Analysis:**
- Effect size: Cohen's d ≥ 0.8 (large effect)
- Required n for 80% power: ~20 seeds
- **Limitation:** n=3 seeds → low statistical power
- **Mitigation:** Only claim dominance for large, obvious differences (AUROC gap > 0.10)

---

## Failure Modes

### False Negative (Pareto frontier exists, but |Pareto_set| = 1)
**Cause:** Low statistical power (n=3 seeds insufficient)
**Mitigation:** Report AUROC means and visual inspection of scatter plot
**Interpretation:** Conservative — real trade-offs may exist but not statistically significant

### False Positive (No real frontier, but |Pareto_set| ≥ 2)
**Cause:** High variance in AUROC estimates masks dominance
**Mitigation:** Report confidence intervals, require AUROC gap > 0.05 for practical significance
**Interpretation:** Liberal — claimed Pareto set may collapse with more seeds

---

## Data Collection Checklist

- [ ] Load TruthfulQA (817 questions) via HuggingFace
- [ ] Load HaluEval (~10k samples) for calibration
- [ ] Calibrate temperature scaling (T_opt)
- [ ] Calibrate conformal prediction (threshold τ)
- [ ] Run inference for 6 methods × 3 seeds = 18 runs
- [ ] Compute correctness labels (fuzzy match against correct_answers)
- [ ] Compute AUROC for all 18 runs
- [ ] Aggregate: (cost, AUROC_mean, AUROC_std) per method
- [ ] Construct Pareto frontier via dominance check
- [ ] Generate 3 visualization figures
- [ ] Save results to h-m-pareto/results/

---

*Next Phase: 02c_experiment_brief.md — Detailed implementation specifications for Phase 4*
