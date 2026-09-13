# Experiment Design: h-m1

**Date:** 2026-05-02
**Author:** Anonymous
**Hypothesis Statement:** Under the same 4-condition training setup as H-E1, if training data contains a higher fraction of APPS tier 0-2 problems during early training (steps 0-2500), then reward density (fraction of GRPO batches where max(rewards_per_group) > 0) is measurably higher in the curriculum condition than in the uniform condition during those steps, because GRPO advantage formula A_i = (r_i − mean) / std → 0 when all G=8 completions fail (std=0), and easier problems yield higher completion success rates.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (MUST_WORK) Template** — Tests causal mechanism: reward density is controlled by difficulty composition.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 MUST_WORK gate PASSED ✅
**Gate Status:** MUST_WORK — requires p < 0.05 one-tailed Wilcoxon on reward density curriculum > uniform (steps 0-2500)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED ✅)

### Gate Condition
**MUST_WORK:** Mean reward density in curriculum condition steps 0-2500 > mean reward density in uniform condition steps 0-2500 (one-tailed Wilcoxon signed-rank test, p < 0.05 across 5 checkpoint observations).

---

## Continuation Context

**H-E1 Results (prerequisite — PASSED):**
- All 4 conditions (curriculum, uniform, easy_only, hard_only) completed 10-step smoke test successfully
- GRPO training loop executes correctly with TRL 1.3.0 API
- Dataset pipeline (APPS + CodeContests) loads and unifies schema correctly
- Execution reward function runs without crashes
- CurriculumCallback step transitions work correctly
- 4 final checkpoints saved, **4 reward density CSV logs produced**

**Key Implementation Facts from H-E1 (reuse directly):**
- Dataset hub names: `codeparrot/apps` and `deepmind/code_contests` (NOT hendrycks/apps or google-deepmind/code_contests)
- TRL 1.3.0 API: `GRPOConfig` requires `generation_kwargs={"max_new_tokens": 512}` (not `max_new_tokens` directly)
- Schema unification: `_tokenize_and_normalize()` maps APPS+CC to 4 uniform columns
- Large integer handling: `_safe_str()` using `repr()` instead of `str()`
- No `code/__init__.py` (shadows Python built-in `code` module)

**H-M1 Experiment Nature:** This is a **log analysis experiment** — no new training required. All reward data already exists from H-E1 runs. The experiment reads `h-e1/logs/reward_density_{condition}.csv`, computes statistics, runs Wilcoxon test, and generates figures.

### Previous Hypothesis Results (if applicable)
- H-E1 reward density observations: All values 0.0 across 10 smoke test steps (expected — base model, 10 steps insufficient for any completions to pass unit tests)
- **IMPORTANT:** H-M1 requires **full 5000-step training** (not 10-step smoke test) to observe meaningful reward density differences. The H-E1 smoke test validated code correctness only; H-M1 requires actual training logs.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP not available in this pipeline configuration. Research grounded in H-E1 implementation facts and verification plan.*

**Key Knowledge (from H-E1 validation report and 02b_verification_plan.md):**

**Reward Density Mechanism:**
- GRPO advantage formula: A_i = (r_i − mean(r)) / std(r)
- When all G=8 completions fail: all r_i = 0, mean = 0, std = 0 → advantage collapses to 0/0 (degenerate step)
- Reward density = fraction of batches where max(rewards_per_group) > 0 (at least one completion passes)
- Easier problems (APPS tier 0-2) → higher solve rate → higher reward density → informative gradient updates
- Hard problems (APPS tier 3-4) → near-zero solve rate → ~0% reward density → degenerate GRPO steps

**Statistical Design:**
- 5 checkpoint observations per condition (steps 500, 1000, 1500, 2000, 2500)
- One-tailed Wilcoxon signed-rank test: paired comparison curriculum vs. uniform across 5 checkpoints
- Secondary: easy-only ≥ curriculum (confirms tier-difficulty correlation A1)

**Prior Empirical Evidence:**
- GRPO advantage collapse was confirmed at repository level (~85% degenerate steps for repo-level patches)
- H-E1 smoke test (10 steps): all reward density = 0.0 (base model, insufficient training to solve any problems)
- Full 5000-step training needed to observe meaningful differences

### Archon Code Examples

*MCP not available. Code grounded in H-E1 implementation (training/reward.py, training/callbacks.py).*

**Existing H-E1 reward density implementation (from 04_validation.md):**
```python
# h-e1/code/training/reward.py — compute_reward_density (already implemented)
# Computes fraction of GRPO batches where max(rewards_per_group) > 0
# Output: h-e1/logs/reward_density_{condition}.csv
```

**H-M1 extends this by:**
1. Reading the 4 CSV files produced by H-E1 full training
2. Computing per-checkpoint statistics (mean, std across batches in each 500-step interval)
3. Running Wilcoxon signed-rank test on checkpoints 1-5 (steps 0-2500)
4. Generating time-series visualization

### Exa GitHub Implementations

*MCP not available. Implementation grounded in H-E1 codebase and SciPy statistical library.*

**Relevant Implementation Pattern — Wilcoxon signed-rank test:**
```python
from scipy.stats import wilcoxon
# One-tailed: alternative='greater' for curriculum > uniform
stat, p_value = wilcoxon(curriculum_densities, uniform_densities, alternative='greater')
```

**Reward density CSV structure (from H-E1 training/callbacks.py):**
- Columns: `step`, `reward_density` (fraction of non-degenerate batches in 500-step window)
- 10 rows per file (one per checkpoint)
- Files: `h-e1/logs/reward_density_curriculum.csv`, `h-e1/logs/reward_density_uniform.csv`, `h-e1/logs/reward_density_easy_only.csv`, `h-e1/logs/reward_density_hard_only.csv`

**Serena Analysis Needed:** false — H-E1 reward density code is already implemented and understood from validation report.

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M1 reuses H-E1 infrastructure — no new training**

This is a log analysis experiment. Implementation priority:
1. **H-E1 reward density CSVs** (HIGHEST — primary data source, already exists from H-E1)
2. **H-E1 training/reward.py** (Reference for reward density definition)
3. **SciPy Wilcoxon** (Statistical test implementation)

**Recommended Implementation Path:**
- Primary: Read `h-e1/logs/reward_density_{condition}.csv` → compute checkpoint-level means → Wilcoxon test
- Fallback: If full-training CSVs only contain smoke-test data (10 steps), must first run full 5000-step training for all 4 conditions
- Justification: H-E1 only ran 10-step smoke test; full training logs may not exist yet. H-M1 may need to trigger full training first.

### Code Analysis (Serena MCP)

*Skipped* — Code from H-E1 implementation (training/reward.py, training/callbacks.py) is sufficiently clear from the 04_validation.md report. No complex unfamiliar architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** APPS + CodeContests — Reward Density Logs from H-E1 Training Runs

| Property | Value |
|----------|-------|
| Name | APPS + CodeContests (reward density logs) |
| Type | standard |
| Source | codeparrot/apps + deepmind/code_contests (HuggingFace) |
| Training data | 4 conditions × 5000 steps each |
| Measurement data | Per-batch rewards logged by RewardDensityCallback |
| Output logs | h-e1/logs/reward_density_{condition}.csv (4 files, 10 rows each) |
| Checkpoint intervals | Every 500 steps (10 checkpoints per condition) |
| Analysis window | Steps 0-2500 (checkpoints 1-5, early training phase) |

**Dataset Type:** standard (APPS + CodeContests are real, established datasets)
**No synthetic data used.**

**Evaluation samples:**
- 40 total checkpoint observations (10 checkpoints × 4 conditions)
- 5 observations per condition for Wilcoxon test (steps 0-2500)
- Full reward density time series for visualization (all 10 checkpoints)

**Loading Information** (for Phase 4):
- Method: CSV file read (no download required — H-E1 logs already exist)
- Identifier: `h-e1/logs/reward_density_{condition}.csv` where condition ∈ {curriculum, uniform, easy_only, hard_only}
- Code: `import pandas as pd; df = pd.read_csv('h-e1/logs/reward_density_curriculum.csv')`

**IMPORTANT — Full Training Prerequisite:**
H-E1 only ran a 10-step smoke test. The reward density logs currently contain only 10 steps of data (all 0.0). H-M1 Phase 4 must first run full 5000-step training for all 4 conditions to generate meaningful reward density logs, then perform the analysis.

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-base
**Role in H-M1:** Reference point — the uniform condition checkpoint represents GRPO training without difficulty stratification

| Property | Value |
|----------|-------|
| Name | DeepSeek-Coder-7B-base |
| Type | Decoder-only transformer, 7B parameters |
| Source | deepseek-ai/DeepSeek-Coder-7B-base (HuggingFace) |
| Confirmed working | Yes — H-E1 MUST_WORK gate PASSED |
| Checkpoints | h-e1/checkpoints/uniform/final/ (from H-E1) |
| Reward logs | h-e1/logs/reward_density_uniform.csv |

**Baseline condition:** Uniform random sampling from APPS+CodeContests (steps 0-2500)

**Loading Information** (for Phase 4):
- Method: HuggingFace / local checkpoint
- Identifier: `deepseek-ai/DeepSeek-Coder-7B-base` or `h-e1/checkpoints/uniform/final/`
- Code: `from transformers import AutoModelForCausalLM; model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-Coder-7B-base")`

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-base + Difficulty-Stratified Curriculum (easy→hard ordering)

**Core Mechanism:** The "mechanism" in H-M1 is not a model architecture change but a **training data ordering change**. The curriculum condition selects APPS tier 0-2 problems for steps 0-2500 and tier 3-4 for steps 2501-5000, creating higher reward density during early training.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Difficulty-Stratified Reward Density Analysis
# Based on: H-E1 training/callbacks.py (RewardDensityCallback)
# H-E1 source: training/reward.py (compute_reward_density)

import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def load_reward_density_logs(log_dir: str) -> dict[str, pd.DataFrame]:
    """Load per-condition reward density CSV logs from H-E1 training."""
    conditions = ["curriculum", "uniform", "easy_only", "hard_only"]
    return {
        cond: pd.read_csv(f"{log_dir}/reward_density_{cond}.csv")
        for cond in conditions
    }

def compute_early_phase_density(df: pd.DataFrame, max_step: int = 2500) -> np.ndarray:
    """Extract reward density for steps 0-2500 (5 checkpoints at 500-step intervals)."""
    early = df[df["step"] <= max_step].sort_values("step")
    return early["reward_density"].values  # shape: (5,)

def run_wilcoxon_test(curriculum_vals: np.ndarray, uniform_vals: np.ndarray):
    """One-tailed Wilcoxon: curriculum reward density > uniform (steps 0-2500)."""
    stat, p_value = wilcoxon(curriculum_vals, uniform_vals, alternative="greater")
    return {
        "statistic": stat,
        "p_value": p_value,
        "passed": p_value < 0.05,
        "curriculum_mean": np.mean(curriculum_vals),
        "uniform_mean": np.mean(uniform_vals),
        "delta": np.mean(curriculum_vals) - np.mean(uniform_vals),
    }

def verify_assumption_a1(easy_only_vals: np.ndarray, curriculum_vals: np.ndarray) -> bool:
    """Secondary: easy_only reward density >= curriculum early phase (A1 check)."""
    return np.mean(easy_only_vals) >= np.mean(curriculum_vals)
```

### Training Protocol

**H-M1 does NOT require new model training.** The experiment reuses H-E1 training infrastructure.

**Full Training Protocol (if H-E1 full runs not yet executed):**

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

**Analysis Protocol (core of H-M1):**

| Step | Action |
|------|--------|
| 1 | Load 4 × reward_density_*.csv files from h-e1/logs/ |
| 2 | Extract checkpoints 1-5 (steps 500-2500) per condition |
| 3 | Compute per-checkpoint mean reward density per condition |
| 4 | Run one-tailed Wilcoxon: curriculum > uniform (5 paired observations) |
| 5 | Check secondary: easy_only ≥ curriculum early phase |
| 6 | Generate time-series plot (all 4 conditions, steps 0-5000) |
| 7 | Generate bar chart (mean early-phase density, curriculum vs. uniform vs. easy_only vs. hard_only) |

### Evaluation

**Primary Metric:** Reward density = fraction of GRPO batches where max(rewards_per_group) > 0

**Measurement:**
- Per-checkpoint reward density already computed by `compute_reward_density()` in H-E1
- Logged to `h-e1/logs/reward_density_{condition}.csv`
- Analysis window: steps 0-2500 (early training, 5 checkpoints)

**Statistical Test:**
- One-tailed Wilcoxon signed-rank test
- H0: curriculum reward density ≤ uniform reward density (steps 0-2500)
- H1: curriculum reward density > uniform reward density (steps 0-2500)
- Significance: p < 0.05
- n = 5 paired checkpoint observations

**Success Criteria:**
- Primary: curriculum mean reward density (steps 0-2500) > uniform mean reward density AND p < 0.05 (one-tailed Wilcoxon)
- Secondary: easy_only mean reward density ≥ curriculum mean reward density (confirms A1: tier-difficulty correlation)

**Expected Values (based on mechanism theory):**
- Easy-only condition: highest reward density (≥20-40% batches non-degenerate)
- Curriculum condition early phase: moderate-high (tier 0-2 problems, ~15-35%)
- Uniform condition: lower (mixture of all tiers, ~5-20%)
- Hard-only condition: lowest (tier 3-4 problems, ~1-5%)

**EXISTENCE (PoC): Success = direction only (curriculum reward density > uniform)**

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (not classification/regression)
- Library: `scipy.stats.wilcoxon`, `pandas`, `numpy`, `matplotlib`
- Code: `from scipy.stats import wilcoxon; stat, p = wilcoxon(curriculum_vals, uniform_vals, alternative='greater')`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — mean reward density (steps 0-2500) per condition (curriculum, uniform, easy_only, hard_only) with error bars (std across 5 checkpoints)

#### Additional Figures (LLM Autonomous)

Based on this hypothesis type (mechanism verification via time-series comparison):

1. **Reward Density Time Series** (all 4 conditions, steps 0-5000): Line plot showing reward density at each 500-step checkpoint. Expected: curriculum and easy_only diverge from uniform and hard_only during steps 0-2500, then converge/cross after step 2500 (when curriculum switches to hard problems).

2. **Early vs. Late Phase Comparison**: Side-by-side bar charts — steps 0-2500 vs. steps 2501-5000 — showing curriculum's reward density advantage is specific to early phase.

3. **Wilcoxon Test Visualization**: Box plot of reward density distributions (curriculum vs. uniform, steps 0-2500) with p-value annotation.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 `compute_reward_density()` correctly computes fraction of non-degenerate batches | TRUE — confirmed in H-E1 04_validation.md |
| Mechanism Isolatable | Curriculum vs. uniform conditions are isolated by `CurriculumCallback` step transitions | TRUE — H-E1 confirmed CurriculumCallback works |
| Baseline Measurable | Uniform condition reward density measurable independently from curriculum | TRUE — separate CSV per condition |

### Architecture Compatibility Check

**H-M1 requires no architectural change.** The mechanism is training data ordering, not model modification.

**Required Infrastructure:**
- H-E1 full training runs completed (5000 steps per condition, not just 10-step smoke test)
- RewardDensityCallback logging per-batch rewards to CSV at each 500-step checkpoint
- 4 conditions running independently with identical hyperparameters

**Compatible:** DeepSeek-Coder-7B-base with TRL 1.3.0 GRPOTrainer (confirmed by H-E1)

**Incompatible scenarios:**
- If H-E1 logs only contain 10-step smoke test data → must run full training first
- If RewardDensityCallback only logs aggregate (not per-checkpoint) → must fix logging granularity

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Reward density at step {step}: {density:.4f}"` | training/callbacks.py:RewardDensityCallback |
| CSV Row | `reward_density_{condition}.csv` has 10 rows (not 0 or 1) | h-e1/logs/ |
| Metric Delta | curriculum mean density > uniform mean density (steps 0-2500) | analyze_reward_density.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(log_dir: str) -> tuple[bool, dict]:
    """Verify H-M1 mechanism: curriculum has higher reward density than uniform (steps 0-2500)."""
    import pandas as pd, numpy as np
    from scipy.stats import wilcoxon

    # Load logs
    curriculum = pd.read_csv(f"{log_dir}/reward_density_curriculum.csv")
    uniform = pd.read_csv(f"{log_dir}/reward_density_uniform.csv")

    # Check sufficient data (must have full training logs, not just smoke test)
    assert len(curriculum) >= 10, f"Only {len(curriculum)} checkpoints found — full training required"

    # Extract early phase (steps 0-2500)
    early_c = curriculum[curriculum["step"] <= 2500]["reward_density"].values
    early_u = uniform[uniform["step"] <= 2500]["reward_density"].values

    # Wilcoxon one-tailed test
    stat, p_val = wilcoxon(early_c, early_u, alternative="greater")

    indicators = {
        "curriculum_mean": float(np.mean(early_c)),
        "uniform_mean": float(np.mean(early_u)),
        "direction_correct": float(np.mean(early_c)) > float(np.mean(early_u)),
        "p_value": float(p_val),
        "gate_passed": p_val < 0.05,
        "n_checkpoints": len(early_c),
    }
    return indicators["gate_passed"], indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Logs contain only smoke test (10 steps) | `len(df) < 10` | Run full 5000-step training for all 4 conditions |
| No reward density difference | `np.mean(curriculum) <= np.mean(uniform)` | Check assumption A1 (tier difficulty correlation) |
| p ≥ 0.05 but correct direction | Wilcoxon not significant | EXPLORE — check if base model solve rate for tier 0-2 is still near 0% |
| easy_only < curriculum (A1 violated) | Secondary check fails | Document A1 assumption failure; paper attributes H-E1 finding to content coverage |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Reward density CSV has 10 rows (full training) | File row count check |
| Direction Correct | curriculum mean > uniform mean (steps 0-2500) | np.mean comparison |
| Hypothesis Supported | p < 0.05 (one-tailed Wilcoxon) | scipy.stats.wilcoxon |

---

## PoC Success Check

**PoC Pass Condition:**
1. Full 5000-step training logs exist for all 4 conditions
2. `curriculum_reward_density_mean(steps 0-2500) > uniform_reward_density_mean(steps 0-2500)` AND `p < 0.05` (one-tailed Wilcoxon)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP unavailable in this pipeline configuration.*

**Ground Truth Source (H-E1 Validation Report):**
- **Type:** Phase 4 validation report from preceding hypothesis
- **Relevance:** Defines reward density implementation, confirms CSV log structure, identifies key implementation fixes
- **Key Insights:**
  - `compute_reward_density()` in `training/reward.py` computes fraction of non-degenerate batches
  - `RewardDensityCallback` in `training/callbacks.py` logs per-condition reward density at each checkpoint
  - 4 CSVs produced: `reward_density_{curriculum,uniform,easy_only,hard_only}.csv`
  - Full training (not smoke test) required for meaningful values
- **Used For:** Dataset specification, model loading, analysis protocol

**Verification Plan (Phase 2B):**
- **Type:** Research planning document
- **Relevance:** Defines H-M1 variables, success criteria, statistical test, and verification protocol
- **Key Insights:**
  - Wilcoxon signed-rank test (one-tailed, curriculum > uniform, n=5 paired observations)
  - Secondary: easy_only ≥ curriculum (A1 check)
  - Analysis window: steps 0-2500 only (early training phase)
- **Used For:** Statistical test design, success criteria, evaluation metrics

### B. GitHub Implementations (Exa)

*MCP unavailable. Implementation grounded in H-E1 codebase.*

**H-E1 Codebase (local):**
- **Path:** `h-e1/code/training/reward.py`, `h-e1/code/training/callbacks.py`
- **Relevance:** Direct implementation of reward density computation and logging
- **Key Code Pattern:**
  ```python
  # From H-E1 training/reward.py (confirmed working)
  def compute_reward_density(rewards_per_group: list[list[float]]) -> float:
      """Fraction of batches where at least one completion gets reward > 0."""
      non_degenerate = sum(1 for group in rewards_per_group if max(group) > 0)
      return non_degenerate / len(rewards_per_group)
  ```
- **Used For:** Core analysis logic for H-M1

**SciPy Wilcoxon (standard library):**
- **Reference:** `scipy.stats.wilcoxon(x, y, alternative='greater')`
- **Purpose:** One-tailed paired non-parametric test for small samples (n=5)
- **Choice justification:** Non-parametric test appropriate for n=5 observations; one-tailed because directional hypothesis

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-E1 validation report is sufficiently clear. Reward density computation and CSV logging are straightforward and fully documented.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Dataset: APPS + CodeContests (codeparrot/apps + deepmind/code_contests) — confirmed working
  - Reward density logging infrastructure: RewardDensityCallback → CSV
  - All 4 condition training code: curriculum, uniform, easy_only, hard_only
  - Hyperparameters: same TRL GRPOTrainer config, G=8, 5000 steps
  - Key implementation fixes (dataset hub names, TRL API, schema unification, large int handling)
- **Why Reused:** H-M1 is a measurement experiment on H-E1 training artifacts — identical training infrastructure required for controlled comparison

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (reward logs) | H-E1 validation | h-e1/04_validation.md |
| Dataset hub names | H-E1 implementation fix | codeparrot/apps, deepmind/code_contests |
| Model (DeepSeek-Coder-7B-base) | H-E1 controlled variable | 02b_verification_plan.md §1.3 |
| Reward density definition | H-E1 training/reward.py | max(rewards_per_group) > 0 |
| CSV log structure | H-E1 validation report | 4 files × 10 checkpoints |
| Statistical test (Wilcoxon) | Phase 2B §2.2 H-M1 | One-tailed, n=5 checkpoints |
| Analysis window (steps 0-2500) | Phase 2B §2.2 H-M1 | Early training phase |
| Training protocol | H-E1 config.py | Same hyperparameters |
| Success threshold (p < 0.05) | Phase 2B §2.2 H-M1 | Gate condition |
| Visualization requirements | Phase 2B §2.2 H-M1 | Time-series + bar chart |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-02T19:18:59+00:00

### Workflow History for This Hypothesis
- 2026-05-02T00:00:00: Phase 2B completed — H-M1 generated as Causal Step 1
- 2026-05-02T19:18:59: H-M1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-05-02: Phase 2C experiment design initiated (UNATTENDED mode)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Grounded in H-E1 validation report and Phase 2B verification plan (MCP unavailable in this pipeline configuration)*
*All specifications grounded in H-E1 validated implementations*
*Next Phase: Phase 3 - Implementation Planning*
