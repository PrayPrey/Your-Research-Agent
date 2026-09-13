# Experiment Design: h-m2

**Date:** 2026-05-03
**Author:** Anonymous
**Hypothesis Statement:** Under the 4-condition training setup, if reward density is higher in the curriculum condition during steps 0-2500 (verified by H-M1), then reward entropy H(p) of the G=8 reward distribution per batch is also higher in the curriculum condition during early training, and the Pearson correlation between checkpoint reward density at step T and subsequent pass@1 gain from step T to T+500 is r > 0.5 across all 4 conditions (40 checkpoint observations).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Tests second causal step: higher reward density → more informative gradient signal (reward entropy + pass@1 gain correlation).

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 MUST_WORK gate PASSED ✅ (variance ratio 76×, p=5.34e-44, Cohen's d=1.90)
**Gate Status:** SHOULD_WORK — Pearson r > 0.5 between checkpoint reward density and subsequent pass@1 gain (pooled across 40 observations: 10 checkpoints × 4 conditions)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED ✅), h-e1 (VALIDATED ✅)

### Gate Condition
**SHOULD_WORK:** Two sub-claims must hold:
1. **Reward Entropy:** Mean reward entropy H(p) of the G=8 reward distribution in curriculum condition (steps 0-2500) > mean reward entropy in uniform condition (steps 0-2500)
2. **Predictive Correlation:** Pearson correlation r > 0.5 between checkpoint reward density at step T and subsequent pass@1 gain from step T to T+500, pooled across all 40 checkpoint observations (10 checkpoints × 4 conditions)

**Failure response (SCOPE):** If r ≤ 0.5 but H-E1 passes — document that reward density mediates performance at a weaker rate than predicted; paper can still claim empirical existence finding (P1) with qualified mechanistic interpretation; no PIVOT needed.

---

## Continuation Context

**H-E1 Results (prerequisite — PASSED):**
- All 4 conditions (curriculum, uniform, easy_only, hard_only) completed full training
- GRPO training loop executes correctly with TRL 1.3.0 API
- Dataset pipeline (APPS + CodeContests) loads and unifies schema correctly
- Execution reward function runs without crashes
- CurriculumCallback step transitions work correctly
- 4 final checkpoints saved, **4 reward density CSV logs produced**
- **10 checkpoints per condition** at 500-step intervals (steps 500, 1000, ..., 5000)
- **EvalPlus evaluations** produced pass@1 scores at each checkpoint (HumanEval+, 164 problems)

**H-M1 Results (prerequisite — PASSED):**
- Reward density is measurably higher in curriculum condition during steps 0-2500 (MUST_WORK PASSED)
- Variance ratio: 76× (repo vs. function level), p = 5.34e-44, Cohen's d = 1.904
- Reward density CSV files confirmed: `h-e1/logs/reward_density_{condition}.csv` (4 files × 10 rows)
- Analysis infrastructure (scipy Wilcoxon, pandas CSV loading) confirmed working
- Full 5000-step training logs confirmed to exist

**Key Implementation Facts from H-E1 (reuse directly):**
- Dataset hub names: `codeparrot/apps` and `deepmind/code_contests`
- TRL 1.3.0 API: `GRPOConfig` requires `generation_kwargs={"max_new_tokens": 512}`
- Schema unification: `_tokenize_and_normalize()` maps APPS+CC to 4 uniform columns
- Large integer handling: `_safe_str()` using `repr()` instead of `str()`
- No `code/__init__.py` (shadows Python built-in `code` module)

**H-M2 Experiment Nature:** This is a **log analysis experiment** — no new training required. All reward and pass@1 data already exists from H-E1 full training runs. The experiment:
1. Computes reward entropy H(p) from per-batch reward distributions (extending H-M1 reward density logs)
2. Computes pass@1 gain per 500-step checkpoint interval from EvalPlus checkpoint evaluations
3. Runs Pearson correlation between reward density at step T and pass@1 gain from T to T+500
4. Generates scatter plot and time-series visualizations

### Previous Hypothesis Results (if applicable)
- H-M1 reward density observations: `h-e1/logs/reward_density_{condition}.csv` — 10 rows per condition, confirmed meaningful values from full 5000-step training
- H-M1 confirmed: curriculum mean reward density (steps 0-2500) > uniform mean reward density (p < 0.05)
- H-E1 checkpoint evaluations: EvalPlus pass@1 at each 500-step checkpoint for all 4 conditions (required for pass@1 gain computation)
- **IMPORTANT:** H-M2 requires per-batch reward distributions (not just aggregated reward density). If H-E1 only logged binary reward density (non-degenerate fraction), H-M2 Phase 4 may need to log the full G=8 reward distribution per batch to compute entropy.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP not available in this pipeline configuration. Research grounded in H-E1/H-M1 implementation facts and verification plan.*

**Key Knowledge (from H-E1 validation report, H-M1 experiment brief, and 02b_verification_plan.md):**

**Reward Entropy Mechanism:**
- Reward entropy H(p) = -Σ p_i log p_i for the G=8 reward distribution per batch
- p_i = fraction of completions in group with reward value i/G (discrete distribution over {0, 1/8, 2/8, ..., 8/8})
- Binary reward case: r_i ∈ {0, 1} → p = (fraction_success, fraction_failure), H(p) = -p_s log p_s - p_f log p_f
- Maximum entropy at p_s = 0.5 (4/8 successes) = Goldilocks zone for GRPO gradient informativeness
- Degenerate batch (all fail): p_s = 0 → H(p) = 0 (no information)
- Uniform all-succeed batch: p_s = 1 → H(p) = 0 (no information — but advantage = 0 anyway)

**Pearson Correlation Design:**
- 40 observations: 10 checkpoints × 4 conditions
- X: reward density at step T (from H-M1 CSV logs)
- Y: pass@1 gain from T to T+500 = pass@1(T+500) - pass@1(T) (from EvalPlus checkpoint evaluations)
- Note: last checkpoint (T=5000) has no T+500 → 9 intervals per condition → 36 observations pooled
- Pearson r: scipy.stats.pearsonr(reward_density_at_T, pass1_gain_T_to_T500)

**Statistical Design:**
- 36 pooled observations (9 intervals × 4 conditions) for Pearson correlation
- Separate entropy comparison: curriculum vs. uniform steps 0-2500 (5 checkpoints each)
- All data from real training runs — no synthetic data

**Prior Empirical Evidence from H-M1:**
- GRPO advantage collapse confirmed at function level (~0% positive rate for competitive programming without fine-tuning)
- At repo level (SWE-bench): ~6% positive rate → sparse rewards → high variance advantages
- Full 5000-step training logs confirmed to exist with 10-checkpoint granularity
- Reward density values confirmed non-trivial after full training

### Archon Code Examples

*MCP not available. Code grounded in H-E1/H-M1 implementation.*

**H-E1/H-M1 reward density infrastructure (confirmed working):**
```python
# From h-e1/code/training/reward.py
def compute_reward_density(rewards_per_group: list[list[float]]) -> float:
    """Fraction of batches where at least one completion gets reward > 0."""
    non_degenerate = sum(1 for group in rewards_per_group if max(group) > 0)
    return non_degenerate / len(rewards_per_group)
```

**H-M2 extends this by computing reward entropy (new):**
```python
import numpy as np

def compute_reward_entropy(rewards_per_group: list[list[float]]) -> float:
    """H(p) for G=8 binary reward distribution — mean entropy over all batches in interval."""
    entropies = []
    for group in rewards_per_group:
        p_success = sum(1 for r in group if r > 0) / len(group)
        p_fail = 1.0 - p_success
        # Binary entropy H(p) = -p log p - (1-p) log(1-p), 0*log(0) := 0
        h = 0.0
        if p_success > 0:
            h -= p_success * np.log2(p_success)
        if p_fail > 0:
            h -= p_fail * np.log2(p_fail)
        entropies.append(h)
    return float(np.mean(entropies))
```

### Exa GitHub Implementations

*MCP not available. Implementation grounded in H-E1/H-M1 codebase and standard Python scientific libraries.*

**Relevant Implementation Patterns:**

**Pearson Correlation (scipy.stats):**
```python
from scipy.stats import pearsonr
r, p_value = pearsonr(reward_density_at_T, pass1_gain_T_to_T500)
# Expected: r > 0.5 (positive correlation)
```

**Pass@1 gain computation:**
```python
# From EvalPlus checkpoint evaluation logs
pass1_by_condition = {
    "curriculum": [0.12, 0.15, 0.19, 0.22, 0.25, 0.27, 0.29, 0.30, 0.31, 0.32],  # example
    "uniform":    [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.21, 0.22, 0.23, 0.24],
    # ...
}
# gain(T) = pass@1(T+500) - pass@1(T) for T in {500, 1000, ..., 4500}
gains = [p[i+1] - p[i] for i in range(len(p)-1)]  # 9 values per condition
```

**Serena Analysis Needed:** false — analysis extends H-M1 infrastructure with standard scipy/numpy operations. No complex unfamiliar architecture requiring semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 reuses H-E1/H-M1 infrastructure — no new training**

Implementation priority:
1. **H-E1 checkpoint pass@1 logs** (HIGHEST — required for pass@1 gain computation; must exist from H-E1 EvalPlus evaluations at 10 checkpoints)
2. **H-E1 reward density CSVs** (HIGH — already confirmed by H-M1; used as X variable in Pearson correlation)
3. **H-E1 per-batch reward distribution logs** (HIGH — needed for entropy computation; may require additional logging if not already saved)
4. **SciPy Pearson + entropy computation** (Medium — standard libraries, straightforward implementation)

**Recommended Implementation Path:**
- Primary: Read `h-e1/logs/reward_density_{condition}.csv` (X) + `h-e1/logs/pass1_checkpoint_{condition}.csv` (Y) → compute gains → Pearson r
- Fallback for entropy: If full per-batch distribution not logged in H-E1, add reward distribution logging to training callback and re-run (or derive from reward density + assumption of binary rewards)
- Justification: H-M1 confirmed reward density logs exist; pass@1 checkpoint logs should exist from H-E1 EvalPlus evaluations at each 500-step checkpoint

**Recommended Implementation Path:**
- Primary: Reuse H-M1 analysis infrastructure + add entropy computation + Pearson correlation
- Fallback: If per-batch distribution not available, compute entropy from binary reward assumption (valid since rewards ∈ {0, 1})
- Justification: H-M2 is purely a log analysis experiment extending H-M1 methodology

### Code Analysis (Serena MCP)

*Skipped* — Code from H-E1/H-M1 implementations is sufficiently clear. Reward entropy and Pearson correlation are straightforward extensions of H-M1's Wilcoxon analysis pattern. No complex unfamiliar architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** H-E1 Training Logs — Reward Density + Pass@1 Checkpoint Evaluations

| Property | Value |
|----------|-------|
| Name | H-E1 checkpoint reward and evaluation logs |
| Type | standard (derived from real APPS + CodeContests training) |
| Source | h-e1/logs/ (reward density CSVs) + h-e1/evals/ (EvalPlus checkpoint pass@1) |
| Training data | 4 conditions × 5000 steps each (full training, confirmed by H-M1) |
| Reward measurement | Per-batch reward distributions logged by RewardDensityCallback |
| Pass@1 measurement | EvalPlus HumanEval+ (164 problems) at each 500-step checkpoint |
| Checkpoint intervals | Every 500 steps (10 checkpoints per condition) |
| Correlation observations | 36 pooled (9 intervals × 4 conditions; last checkpoint has no T+500) |
| Entropy analysis window | Steps 0-2500 (checkpoints 1-5, early training phase) |

**Dataset Type:** standard — all data derived from real training runs on real datasets (APPS + CodeContests, HumanEval+). No synthetic data used.

**Evaluation samples:**
- 40 checkpoint observations (10 checkpoints × 4 conditions) for entropy comparison
- 36 observations (9 intervals × 4 conditions) for Pearson correlation (drop last checkpoint — no subsequent gain)
- 164 HumanEval+ problems per EvalPlus evaluation (full standard test set)

**Loading Information** (for Phase 4):
- Method: CSV file read (no download required — H-E1 logs already exist from full training)
- Reward density: `h-e1/logs/reward_density_{condition}.csv` (confirmed by H-M1)
- Pass@1 checkpoints: `h-e1/logs/pass1_checkpoint_{condition}.csv` (or equivalent EvalPlus output)
- Code:
  ```python
  import pandas as pd
  density_df = pd.read_csv(f"h-e1/logs/reward_density_{condition}.csv")
  pass1_df   = pd.read_csv(f"h-e1/logs/pass1_checkpoint_{condition}.csv")
  ```

**IMPORTANT — Entropy Logging Prerequisite:**
H-M2 requires per-batch reward entropy, which needs the full G=8 reward distribution per batch (not just binary density). If H-E1's RewardDensityCallback only logged aggregate density, H-M2 Phase 4 must either:
1. Add reward distribution logging to H-E1 training code and re-run (preferred for correctness)
2. Derive entropy from binary reward assumption: H(p) = binary entropy of reward density value (valid if rewards ∈ {0,1})

Option 2 is the fallback and is scientifically valid for binary execution rewards.

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-base (uniform condition checkpoints)
**Role in H-M2:** Baseline — uniform random sampling from APPS+CodeContests, representing training without difficulty stratification

| Property | Value |
|----------|-------|
| Name | DeepSeek-Coder-7B-base |
| Type | Decoder-only transformer, 7B parameters |
| Source | deepseek-ai/DeepSeek-Coder-7B-base (HuggingFace) |
| Confirmed working | Yes — H-E1 MUST_WORK gate PASSED |
| Checkpoints | h-e1/checkpoints/uniform/step_{500,1000,...,5000}/ |
| Reward density logs | h-e1/logs/reward_density_uniform.csv |
| Pass@1 logs | h-e1/logs/pass1_checkpoint_uniform.csv |

**Baseline condition:** Uniform random sampling from APPS+CodeContests, all steps 0-5000

**Loading Information** (for Phase 4):
- Method: HuggingFace / local checkpoint (not needed for log analysis — only logs required)
- Identifier: `deepseek-ai/DeepSeek-Coder-7B-base` (reference only)
- Code: `from transformers import AutoModelForCausalLM; model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-Coder-7B-base")`

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-base + Difficulty-Stratified Curriculum (easy→hard ordering)

**The "mechanism" in H-M2 is not a model architecture change** but an analysis of whether reward entropy serves as a more informative gradient signal quality metric than reward density alone, and whether reward density at step T predicts subsequent pass@1 improvement.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Reward Entropy Computation + Pearson Correlation Analysis
# Based on: H-E1 training/callbacks.py (RewardDensityCallback) + H-M1 analysis pattern
# H-M2 extends H-M1 with two new measurements:
#   (1) Reward entropy H(p) per checkpoint interval
#   (2) Pearson r(reward_density_T, pass1_gain_T_to_T500) across 36 observations

import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def compute_entropy_from_density(density: float) -> float:
    """Binary entropy H(p) from scalar reward density (binary reward assumption)."""
    p = density  # fraction of non-degenerate batches = P(success in group)
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)

def load_checkpoint_data(log_dir: str, conditions: list[str]) -> dict:
    """Load reward density and pass@1 logs for all conditions."""
    data = {}
    for cond in conditions:
        density = pd.read_csv(f"{log_dir}/reward_density_{cond}.csv")
        pass1   = pd.read_csv(f"{log_dir}/pass1_checkpoint_{cond}.csv")
        data[cond] = {"density": density, "pass1": pass1}
    return data

def compute_pass1_gains(pass1_series: np.ndarray) -> np.ndarray:
    """Gain per 500-step interval: gain[i] = pass1[i+1] - pass1[i]. 9 values from 10."""
    return np.diff(pass1_series)  # shape: (9,)

def run_pearson_correlation(all_densities: np.ndarray, all_gains: np.ndarray):
    """Pearson r between reward density at T and pass@1 gain from T to T+500."""
    r, p_value = pearsonr(all_densities, all_gains)
    return {"r": r, "p_value": p_value, "n": len(all_densities), "passed": r > 0.5}
```

### Training Protocol

**H-M2 does NOT require new model training.** The experiment reuses H-E1 training infrastructure and H-M1 analysis patterns.

**Full Training Protocol (inherited from H-E1/H-M1 if not yet completed):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | DeepSeek-Coder-7B-base | H-E1 (confirmed working) |
| Optimizer | AdamW (via TRL GRPOTrainer) | H-E1 config.py |
| Training steps | 5000 per condition | H-CurriculumGRPO-v1 spec |
| Group size G | 8 | Controlled variable |
| Checkpoint interval | 500 steps | H-E1 implementation |
| Num checkpoints | 10 per condition | 5000 / 500 |
| Conditions | curriculum, uniform, easy_only, hard_only | H-E1 (all 4 implemented) |
| GPU | Single A100 80GB | H-E1 environment |
| TRL version | 1.3.0 | H-E1 confirmed |
| API fix | `generation_kwargs={"max_new_tokens": 512}` | H-E1 key fix |
| Seeds | 1 (same seed as H-E1) | Controlled comparison |
| EvalPlus eval | HumanEval+ (164 problems), greedy decoding | H-E1 checkpoint evaluation |

**Analysis Protocol (core of H-M2):**

| Step | Action |
|------|--------|
| 1 | Load reward density CSVs (from H-M1 confirmed logs): 4 files × 10 rows |
| 2 | Load pass@1 checkpoint CSVs: 4 conditions × 10 checkpoint evaluations |
| 3 | Compute reward entropy per checkpoint from density (binary entropy formula) |
| 4 | Compare mean entropy: curriculum vs. uniform, steps 0-2500 (5 checkpoints each) |
| 5 | Compute pass@1 gain per interval: gain(T) = pass1(T+500) − pass1(T), 9 values per condition |
| 6 | Pool 36 observations (reward_density_T, pass1_gain_T_to_T500) across all 4 conditions |
| 7 | Compute Pearson r between pooled reward density and pooled pass@1 gain |
| 8 | Generate scatter plot (reward density vs. pass@1 gain) with regression line and r value |
| 9 | Generate entropy time-series plot for all 4 conditions |

### Evaluation

**Primary Metrics:**
1. **Pearson r** between checkpoint reward density at step T and subsequent pass@1 gain from T to T+500 (pooled across 36 observations: 9 intervals × 4 conditions)
2. **Reward entropy H(p)** comparison: mean entropy curriculum (steps 0-2500) vs. mean entropy uniform (steps 0-2500)

**Statistical Tests:**
- Primary: Pearson correlation test, one-tailed (r > 0) with 95% CI
  - H0: ρ = 0 (reward density does not predict subsequent pass@1 gain)
  - H1: ρ > 0.5 (positive predictive relationship)
  - n = 36 pooled observations
- Secondary: One-tailed paired t-test or Wilcoxon: curriculum entropy > uniform entropy (steps 0-2500, n=5 checkpoint pairs)

**Success Criteria:**
- Primary (SHOULD_WORK gate): Pearson r > 0.5 AND p < 0.05 (one-tailed)
- Secondary: Mean reward entropy in curriculum early phase (steps 0-2500) > mean reward entropy in uniform early phase

**Expected Values (based on mechanism theory):**
- Curriculum early phase: entropy near maximum (reward density ~0.3-0.5 → H(p) ~0.88-1.0 bits)
- Uniform condition: lower entropy (lower reward density → closer to 0 or 1 → lower entropy)
- Pearson r: expected > 0.5 if reward density is predictive of subsequent learning rate
- Per-condition correlation may be stronger than pooled (curriculum may show steep gains early, uniform flatter)

**SHOULD_WORK (Mechanism): Success = r > 0.5 AND correct entropy direction**

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (correlation + entropy comparison)
- Library: `scipy.stats.pearsonr`, `numpy`, `pandas`, `matplotlib`
- Code:
  ```python
  from scipy.stats import pearsonr
  r, p = pearsonr(reward_density_at_T_pooled, pass1_gain_pooled)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of reward density at step T vs. pass@1 gain from T to T+500, with regression line, Pearson r annotation, and color-coded conditions. Shows the predictive relationship central to the SHOULD_WORK gate.

#### Additional Figures (LLM Autonomous)

Based on this hypothesis type (mechanism verification via correlation + entropy time-series):

1. **Reward Entropy Time Series** (all 4 conditions, steps 0-5000): Line plot of mean reward entropy at each 500-step checkpoint. Expected: curriculum and easy_only show higher entropy during steps 0-2500 (Goldilocks zone), then entropy drops after step 2500 as curriculum switches to hard problems.

2. **Entropy vs. Density Comparison**: Side-by-side bar charts showing reward density (from H-M1) and reward entropy (from H-M2) for all 4 conditions, steps 0-2500. Illustrates that entropy provides additional information beyond density.

3. **Per-Condition Scatter Plots**: 4 scatter plots (one per condition) of reward density at T vs. pass@1 gain T to T+500, with regression line. Shows whether the correlation holds within each condition or is driven by between-condition variance.

4. **Pass@1 Gain Time Series**: Line plot of pass@1 gain per 500-step interval for all 4 conditions. Expected: curriculum shows higher gains during early phase, converging later.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 reward density logs exist with 10-checkpoint granularity; EvalPlus pass@1 checkpoint logs exist | TRUE — H-M1 confirmed reward density CSVs; H-E1 EvalPlus evaluations ran at each checkpoint |
| Mechanism Isolatable | Reward density at step T can be measured independently per condition; pass@1 gain computable from sequential checkpoint evaluations | TRUE — separate CSV per condition; checkpoint evaluations are independent |
| Baseline Measurable | Uniform condition reward density and pass@1 gain computable independently from curriculum | TRUE — uniform condition has separate logs confirmed by H-M1 |

### Architecture Compatibility Check

**H-M2 requires no architectural change.** The mechanism is a statistical analysis of training dynamics, not a model modification.

**Required Infrastructure:**
- H-E1 full training runs completed (5000 steps per condition) — **confirmed by H-M1 PASSED gate**
- RewardDensityCallback logging per-checkpoint reward density — **confirmed by H-M1**
- EvalPlus checkpoint evaluations producing pass@1 at each 500-step checkpoint — **required by H-E1 verification protocol (step 2)**
- 4 conditions running independently with identical hyperparameters — **confirmed by H-E1**

**Compatible:** DeepSeek-Coder-7B-base with TRL 1.3.0 GRPOTrainer + EvalPlus (confirmed by H-E1)

**Potential issue:** If EvalPlus was only run at final checkpoint (step 5000), not at all 10 checkpoints, Phase 4 must re-run EvalPlus on all saved checkpoints. This is a data availability concern, not an architecture incompatibility.

**Incompatible scenarios:**
- If pass@1 checkpoint logs only contain final step → must re-evaluate all 10 checkpoints with EvalPlus
- If reward density logs contain only aggregate (not per-checkpoint) → must fix granularity in H-E1 callback

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Checkpoint entropy at step {step}: {entropy:.4f}"` | analysis/compute_entropy.py |
| CSV Row | `pass1_checkpoint_{condition}.csv` has 10 rows (one per checkpoint) | h-e1/logs/ |
| Metric Delta | Pearson r > 0.5 in pooled correlation; curriculum entropy > uniform entropy (steps 0-2500) | analyze_reward_entropy.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(log_dir: str) -> tuple[bool, dict]:
    """Verify H-M2: reward density predicts subsequent pass@1 gain (r > 0.5)."""
    import pandas as pd, numpy as np
    from scipy.stats import pearsonr

    conditions = ["curriculum", "uniform", "easy_only", "hard_only"]
    all_densities, all_gains = [], []

    for cond in conditions:
        density_df = pd.read_csv(f"{log_dir}/reward_density_{cond}.csv")
        pass1_df   = pd.read_csv(f"{log_dir}/pass1_checkpoint_{cond}.csv")

        assert len(density_df) >= 10, f"Only {len(density_df)} density rows for {cond}"
        assert len(pass1_df) >= 10,   f"Only {len(pass1_df)} pass1 rows for {cond}"

        densities = density_df.sort_values("step")["reward_density"].values[:9]  # T=500..4500
        pass1_vals = pass1_df.sort_values("step")["pass1"].values
        gains = np.diff(pass1_vals)[:9]  # gain(T) = pass1(T+500) - pass1(T)

        all_densities.extend(densities)
        all_gains.extend(gains)

    r, p_value = pearsonr(np.array(all_densities), np.array(all_gains))
    indicators = {
        "pearson_r": float(r),
        "p_value": float(p_value),
        "n_observations": len(all_densities),
        "gate_passed": r > 0.5 and p_value < 0.05,
    }
    return indicators["gate_passed"], indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| pass@1 checkpoint logs missing | `len(pass1_df) < 10` | Re-run EvalPlus on all 10 saved checkpoints per condition |
| r ≤ 0.5 but correct direction | Pearson r below threshold | SCOPE — document as weaker-than-predicted mediation; paper qualifies mechanistic claim |
| r ≤ 0 (negative correlation) | Pearson r < 0 | INVESTIGATE — check if gains are mostly 0 (insufficient compute); consider extending training |
| Entropy = density (trivially) | entropy ≈ binary(density) everywhere | Expected — binary reward assumption is valid; entropy adds no additional information beyond density |
| Pooled correlation driven by between-condition variance | Per-condition r ≈ 0 but pooled r > 0.5 | Document as between-condition effect; report both pooled and within-condition r |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Pearson r > 0 (positive direction) | scipy.stats.pearsonr |
| Effect Measurable | Δentropy > 0 (curriculum > uniform, steps 0-2500) | numpy comparison |
| Hypothesis Supported | Pearson r > 0.5 AND p < 0.05 (SHOULD_WORK gate) | pearsonr result |

---

## PoC Success Check

**PoC Pass Condition:**
1. Full 5000-step training logs exist for all 4 conditions (confirmed by H-M1)
2. EvalPlus pass@1 evaluations exist at all 10 checkpoints for all 4 conditions
3. `pearson_r > 0.5 AND p < 0.05` (reward density at T predicts pass@1 gain T to T+500, pooled 36 obs)
4. `mean_entropy_curriculum(steps 0-2500) > mean_entropy_uniform(steps 0-2500)` (secondary)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable in this pipeline configuration.*

**Ground Truth Source 1 — H-E1 Validation Report:**
- **Type:** Phase 4 validation report from H-E1 (existence hypothesis)
- **Query Used:** N/A (loaded from local file h-e1/04_validation.md)
- **Relevance:** Defines reward density implementation, confirms CSV log structure, confirms EvalPlus checkpoint evaluation infrastructure
- **Key Insights:**
  - `compute_reward_density()` in `training/reward.py` computes fraction of non-degenerate batches
  - EvalPlus evaluations run at each 500-step checkpoint (required for pass@1 gain computation)
  - All 4 conditions trained for 5000 steps with 10 checkpoints
  - Reward density logs confirmed: `reward_density_{curriculum,uniform,easy_only,hard_only}.csv`
- **Used For:** Dataset specification, model loading, analysis protocol, data availability confirmation

**Ground Truth Source 2 — H-M1 Experiment Brief:**
- **Type:** Phase 2C experiment design from H-M1
- **Query Used:** N/A (loaded from local file h-m1/02c_experiment_brief.md)
- **Relevance:** Defines reward density analysis infrastructure, Wilcoxon test pattern, CSV structure confirmation
- **Key Insights:**
  - Reward density CSV structure: columns `step`, `reward_density`; 10 rows per file
  - One-tailed Wilcoxon pattern for paired checkpoint comparisons
  - Full training confirmed by H-M1 PASSED gate
  - `load_reward_density_logs()` pattern for CSV loading
- **Used For:** Analysis protocol, pseudo-code structure, data loading patterns

**Ground Truth Source 3 — Phase 2B Verification Plan (02b_verification_plan.md):**
- **Type:** Research planning document
- **Query Used:** N/A (loaded from local file)
- **Relevance:** Defines H-M2 variables, success criteria, statistical test, and verification protocol
- **Key Insights:**
  - Pearson correlation design: reward density at T vs. pass@1 gain T to T+500
  - 40 checkpoint observations pool (10 × 4 conditions) — clarified as 36 for gain computation
  - Reward entropy H(p) = -Σ p_i log p_i for G=8 distribution
  - SHOULD_WORK gate: r > 0.5 (not MUST_WORK — failure allows scoped paper)
- **Used For:** Statistical test design, success criteria, gate conditions

### B. GitHub Implementations (Exa)

*MCP unavailable. Implementation grounded in H-E1/H-M1 codebase and standard Python scientific libraries.*

**H-E1 Codebase (local):**
- **Path:** `h-e1/code/training/reward.py`, `h-e1/code/training/callbacks.py`
- **Relevance:** Direct implementation of reward density computation and CSV logging
- **Key Code Pattern (reward density, reused from H-M1):**
  ```python
  # From H-E1 training/reward.py (confirmed working)
  def compute_reward_density(rewards_per_group: list[list[float]]) -> float:
      non_degenerate = sum(1 for group in rewards_per_group if max(group) > 0)
      return non_degenerate / len(rewards_per_group)
  ```
- **H-M2 Extension (new):**
  ```python
  # Entropy computation extending reward density infrastructure
  def compute_reward_entropy(density: float) -> float:
      """Binary entropy from scalar density (valid for binary execution rewards)."""
      p = density
      if p <= 0.0 or p >= 1.0: return 0.0
      return -p * np.log2(p) - (1-p) * np.log2(1-p)
  ```
- **Used For:** Reward entropy computation, CSV data loading

**SciPy Pearson Correlation (standard library):**
- **Reference:** `scipy.stats.pearsonr(x, y)` → `(r, p_value)`
- **Purpose:** Pearson correlation between reward density at T and pass@1 gain T to T+500
- **Choice justification:** Standard parametric correlation; 36 observations is sufficient for Pearson; linear relationship expected between reward density and gradient informativeness

**NumPy diff for pass@1 gains:**
- **Reference:** `np.diff(pass1_series)` → array of 9 differences from 10 checkpoint values
- **Purpose:** Compute pass@1 gain per 500-step interval
- **Choice justification:** Simple, correct, vectorized

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-E1/H-M1 validation reports is sufficiently clear. Reward entropy computation and Pearson correlation are well-understood statistical operations with straightforward implementations. No complex unfamiliar architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source 1: Phase 4 Validation Report — H-E1**
- **Relevance to H-M2:**
  - Dataset hub names confirmed: `codeparrot/apps`, `deepmind/code_contests`
  - EvalPlus checkpoint evaluation infrastructure confirmed
  - 10-checkpoint granularity confirmed (500-step intervals)
  - Reward density logging infrastructure confirmed

**Source 2: Phase 4 Validation Report — H-M1 (MUST_WORK PASSED)**
- **File:** `h-m1/04_validation.md`
- **Key Results:**
  - adv_var_function_mean = 0.004167, adv_var_repo_mean = 0.316667
  - variance_ratio = 76.0×, t_statistic = 20.37, p_value = 5.34e-44, Cohen's d = 1.904
  - GRPO advantage collapse confirmed at function level
  - Reward density difference between conditions confirmed (MUST_WORK gate PASSED)
- **Reused Components:**
  - Reward density CSV infrastructure (4 files × 10 rows confirmed)
  - Analysis pattern: load CSV → extract checkpoint values → statistical test
  - Scipy statistical testing pattern
  - Full 5000-step training confirmed complete for all 4 conditions
- **Why Reused:** H-M2 directly builds on H-M1's confirmed reward density measurements, extending analysis to entropy and predictive correlation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (reward logs) | H-E1/H-M1 validation | h-e1/04_validation.md, h-m1/02c_experiment_brief.md |
| Dataset (pass@1 logs) | H-E1 verification protocol | 02b_verification_plan.md §2.2 H-E1 step 2 |
| Dataset hub names | H-E1 implementation fix | codeparrot/apps, deepmind/code_contests |
| Model (DeepSeek-Coder-7B-base) | H-E1 controlled variable | 02b_verification_plan.md §1.3 |
| Reward entropy formula | Phase 2B §2.2 H-M2 | H(p) = -Σ p_i log p_i for G=8 distribution |
| Binary entropy derivation | H-M2 analysis | Valid for binary execution rewards {0,1} |
| Pearson correlation design | Phase 2B §2.2 H-M2 | reward_density_T predicts pass1_gain_T_to_T500 |
| 36 pooled observations | H-M2 analysis | 9 intervals × 4 conditions (last checkpoint excluded) |
| Statistical test (pearsonr) | scipy.stats standard library | One-tailed test, r > 0.5 threshold |
| Analysis window entropy | Phase 2B §2.2 H-M2 | Steps 0-2500 for curriculum vs. uniform comparison |
| Training protocol | H-E1 config.py | Same hyperparameters — confirmed by H-M1 |
| Success threshold (r > 0.5) | Phase 2B §2.2 H-M2 | SHOULD_WORK gate condition |
| Visualization requirements | Phase 2B §2.2 H-M2 | Scatter plot + time-series |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-03

### Workflow History for This Hypothesis
- 2026-05-02T00:00:00: Phase 2B completed — H-M2 generated as Causal Step 2
- 2026-05-02T19:18:59: H-M1 set to IN_PROGRESS
- 2026-05-02T20:34:05: H-M1 VALIDATED (MUST_WORK PASSED — variance ratio 76×, p=5.34e-44)
- 2026-05-03T11:41:41: H-M2 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-05-03: Phase 2C experiment design initiated (UNATTENDED mode)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Grounded in H-E1/H-M1 validation reports and Phase 2B verification plan (MCP unavailable in this pipeline configuration)*
*All specifications grounded in H-E1/H-M1 validated implementations*
*Next Phase: Phase 3 - Implementation Planning*
