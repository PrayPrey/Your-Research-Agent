# Evaluation Protocol: H-M3
# Random Mathlib Tactic Sampling Baseline

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Type:** MECHANISM (corpus contribution test)  
**Gate:** SHOULD_WORK  

---

## Overview

Test whether random tactic sampling from Mathlib corpus distribution achieves 18-25% success on miniF2F (Δ=3-10 percentage points above lean-auto 15.6%), attributable to human tactic frequency patterns alone.

---

## Dataset

**Name:** miniF2F Lean 4 Test Set  
**Size:** 244 problems  
**Source:** google-deepmind/miniF2F (AlphaProof evaluation version)  
**Preprocessing:** Reuse H-E1 infrastructure (no additional setup)

---

## Prover Configuration

### Random Mathlib Tactic Sampler

**Core Algorithm:**
```lean
def randomMathlibProver (goal: Goal, budget: Nat, seed: Nat) : Option Proof :=
  let rng := mkStdGen seed
  for i in 1..budget do
    let (tactic, rng') := sampleWeighted(tacticDistribution, rng)
    match tryApply(tactic, goal) with
    | Success [] => return some proof  -- No subgoals = solved
    | Success (g::gs) => 
        goal := pickRandom(g::gs, rng')  -- Random goal selection
        rng := rng'
    | Failure => continue
  return none  -- Budget exhausted
```

**Tactic Distribution (Weighted Sampling):**
| Tactic | Weight | Cumulative |
|--------|--------|------------|
| simp | 0.35 | 0.35 |
| rfl | 0.15 | 0.50 |
| intro | 0.08 | 0.58 |
| apply | 0.07 | 0.65 |
| cases | 0.06 | 0.71 |
| intros | 0.04 | 0.75 |
| ring | 0.04 | 0.79 |
| induction | 0.04 | 0.83 |
| exact | 0.04 | 0.87 |
| norm_num | 0.03 | 0.90 |
| constructor | 0.03 | 0.93 |
| linarith | 0.02 | 0.95 |
| omega | 0.02 | 0.97 |
| have | 0.02 | 0.99 |
| calc | 0.01 | 1.00 |

**Parameters:**
- **Tactic budget:** 15 evaluations per problem
- **Goal selection:** Random (when tactic creates multiple subgoals)
- **Timeout:** 300s per problem
- **RNG seeding:** Deterministic (problem_index → seed for reproducibility)

---

## Metrics

### Primary Metrics

**1. Success Rate**
- **Definition:** `problems_solved / 244`
- **Target:** [0.18, 0.25] (predicted: 0.20)
- **Confidence Interval:** 95% Wilson score interval

**2. Δ vs lean-auto**
- **Definition:** `success_rate_h_m3 - success_rate_h_e1`
- **Target:** [0.03, 0.10] percentage points
- **H-E1 baseline:** 15.6% [11.5%, 20.3%]

### Secondary Metrics

**3. Tactic Consumption**
- **Definition:** Average evaluations per solved problem
- **Expected:** ~10 (within 15 budget)

**4. Failure Modes**
- **budget_exhausted:** ~60% of failures
- **timeout:** ~35% of failures
- **error:** <5% of failures

**5. Solve Time**
- **Definition:** Wall-clock seconds to proof
- **Range:** [0, 300]s
- **Expected mean:** ~120s (random sampling less efficient than lean-auto)

---

## Statistical Analysis

### Hypothesis Test

**Null Hypothesis (H₀):** Random success rate = lean-auto success rate (15.6%)  
**Alternative Hypothesis (H₁):** Random success rate > lean-auto (one-sided)

**Test:** One-proportion z-test  
**Significance Level:** α = 0.05

**Test Statistic:**
```python
from scipy.stats import proportions_ztest

# Data
random_success = ?  # From experiment
lean_auto_success = 38  # From H-E1
n = 244

# One-sided z-test
z, p = proportions_ztest(
    [random_success, lean_auto_success],
    [n, n],
    alternative='larger'
)
```

**Interpretation:**
- **p < 0.05:** Reject H₀, corpus contribution validated
- **p ≥ 0.05:** Fail to reject H₀, no significant corpus benefit

### Confidence Interval

**Wilson Score Interval (95%):**
```python
from statsmodels.stats.proportion import proportion_confint

lower, upper = proportion_confint(
    count=random_success,
    nobs=244,
    alpha=0.05,
    method='wilson'
)
```

**Expected:** [15.3%, 25.5%] for 20% success rate

---

## Stratification Analysis (Optional)

**By Problem Source** (if metadata available):

| Source | Expected Random | Expected lean-auto | Expected Δ |
|--------|----------------|-------------------|-----------|
| AMC | 22% | 20% | +2 pp |
| AIME | 19% | 15% | +4 pp |
| IMO | 18% | 12% | +6 pp |

**Hypothesis:** Corpus bias slightly favors easier problems (AMC) where standard tactics suffice.

**Test:** Stratified proportions comparison
```python
for source in ['AMC', 'AIME', 'IMO']:
    random_src = results[results.source == source].success.sum()
    lean_auto_src = h_e1_results[h_e1_results.source == source].success.sum()
    n_src = len(results[results.source == source])
    
    delta = random_src/n_src - lean_auto_src/n_src
    print(f"{source}: Δ = {delta*100:.1f} pp")
```

---

## Falsification Criteria

### REJECT Hypothesis IF:

**Condition 1:** Random success rate < 15%
- **Interpretation:** No corpus benefit (random ≤ lean-auto)
- **Action:** Reject 10% corpus contribution claim

**Condition 2:** Random success rate > 30%
- **Interpretation:** Corpus contribution >> predicted
- **Action:** Revise main hypothesis mechanism split

**Condition 3:** p-value > 0.05
- **Interpretation:** Difference not statistically significant
- **Action:** Corpus contribution not validated (weak evidence)

### PASS Hypothesis IF:

✅ Random success rate ∈ [18%, 25%]  
✅ Δ ∈ [3%, 10%] percentage points  
✅ p-value < 0.05 (statistically significant)

**Outcome:** Corpus contribution validated at ~5% (supports main hypothesis 10% claim)

---

## Execution Plan

### Phase 1: Setup (30 min)
1. Validate tactic distribution weights (spot-check Mathlib files)
2. Implement weighted random sampler
3. Test on 5 miniF2F problems (pilot validation)

### Phase 2: Evaluation (2.5 hours)
1. Run on 244 problems with 8 parallel workers
2. Log per-problem results (problem_id, outcome, tactics_used, wall_time, seed)
3. Aggregate statistics (success_rate, CI, Δ)

### Phase 3: Analysis (1 hour)
1. Statistical comparison (z-test, CI)
2. Stratification by source (if metadata available)
3. Failure mode breakdown
4. Tactic consumption analysis

---

## Output Format

### Per-Problem Results (JSONL)
```jsonl
{"problem_id": "mathd_algebra_478", "source": "AMC", "outcome": "solved", "tactics_used": 8, "wall_time": 45.2, "seed": 123, "tactic_sequence": ["simp", "intro", "ring", ...]}
{"problem_id": "aime_1983_p1", "source": "AIME", "outcome": "budget_exhausted", "tactics_used": 15, "wall_time": 120.5, "seed": 124, "tactic_sequence": [...]}
```

### Aggregate Statistics (YAML)
```yaml
h_m3_results:
  success_rate: 0.201
  ci_95: [0.154, 0.256]
  solved_count: 49
  
  delta_vs_lean_auto:
    value: 0.045  # 4.5 percentage points
    z_statistic: 2.34
    p_value: 0.0096
    significant: true
  
  tactic_consumption:
    mean: 9.8
    median: 8.0
    std: 3.2
    cv: 0.63
  
  failure_modes:
    budget_exhausted: 147
    timeout: 43
    error: 5
  
  stratification_by_source:
    AMC:
      success_rate: 0.219
      delta_vs_lean_auto: 0.038
    AIME:
      success_rate: 0.194
      delta_vs_lean_auto: 0.052
    IMO:
      success_rate: 0.178
      delta_vs_lean_auto: 0.048
```

---

## Reproducibility

### Deterministic Execution
- **RNG seeding:** `seed = problem_index` (problem 0 → seed 0, problem 1 → seed 1, ...)
- **Tactic order:** Deterministic weighted sampling given seed
- **Goal selection:** Deterministic given seed (random → deterministic with seed)

### Validation
- **Rerun 10% subset** (24 problems): Should match exactly
- **Full rerun:** Should match exactly (no stochastic variation)

---

## Comparison Baseline (H-E1)

**lean-auto Results:**
- **Success Rate:** 15.6% [11.5%, 20.3%]
- **Solved Count:** 38/244
- **Tactic Count:** mean=9.2±4.1, median=7.0
- **Timeout Rate:** 80.3%
- **Error Rate:** 10.7%

**Expected Δ:**
- **Random - lean-auto:** 4.4 percentage points (midpoint of [3%, 10%])
- **Mechanism:** Corpus frequency patterns (no semantic understanding)

---

## Quality Gates

### Pre-Execution
✅ Tactic distribution sums to 1.0 (validated)  
✅ RNG seeding deterministic (validated)  
✅ Pilot run on 5 problems successful  

### Post-Execution
✅ Error rate < 5%  
✅ Rerun 10% subset matches exactly  
✅ Tactic consumption within budget (mean < 15)  
✅ No infrastructure failures (worker crashes, OOM)

---

## Timeline

**Total Duration:** 4 hours

| Phase | Duration | Tasks |
|-------|----------|-------|
| Setup | 30 min | Implement sampler, pilot validation |
| Evaluation | 2.5 hours | 244 problems @ 300s timeout, 8 workers |
| Analysis | 1 hour | Statistical tests, stratification, report |

---

## Deliverables

### Code
1. `random_mathlib_sampler.lean` (weighted sampler implementation)
2. `evaluate_h_m3.sh` (evaluation harness)
3. `tactic_distribution.yaml` (empirical weights)

### Data
1. `h_m3_results.jsonl` (per-problem results)
2. `h_m3_aggregate.yaml` (statistics)
3. `h_m3_comparison.csv` (side-by-side with H-E1)

### Reports
1. `04_validation.md` (Phase 4 validation report)
2. `statistical_analysis.ipynb` (z-test, CI, visualization)

---

## References

- **H-E1 Baseline:** verification_state.yaml (lean-auto 15.6%)
- **miniF2F Tidy Baseline:** Han et al. 2021 PACT (18% deterministic)
- **Tactic Distribution:** LeanDojo (Yang & Song 2023), Structured Hints (arXiv:2601.16172)
- **Statistical Methods:** Wilson CI (Agresti & Coull 1998), One-proportion z-test
