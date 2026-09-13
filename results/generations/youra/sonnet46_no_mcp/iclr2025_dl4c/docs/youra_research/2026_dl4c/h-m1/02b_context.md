# Phase 2B Context: H-M1
# JIT-Generated from 02b_verification_plan.md by Phase 2C Step 1
# Generated: 2026-05-02

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** H-E1 (VALIDATED ✅)

**Statement:**
Under the same 4-condition training setup as H-E1, if training data contains a higher fraction of APPS tier 0-2 problems during early training (steps 0-2500), then reward density (fraction of GRPO batches where max(rewards_per_group) > 0) is measurably higher in the curriculum condition than in the uniform condition during those steps, because GRPO advantage formula A_i = (r_i − mean) / std → 0 when all G=8 completions fail (std=0), and easier problems yield higher completion success rates.

**Rationale:**
This tests the first causal step: the mathematically guaranteed mechanism that difficulty composition controls reward density. The GRPO advantage collapse was empirically confirmed at repo level. This hypothesis measures whether the same mechanism operates at function level stratified by difficulty tier. It is MUST_WORK because it is the mechanistic foundation for H-M2 and H-M3.

---

## Variables

- **Independent:** Training data difficulty ordering condition (curriculum vs. uniform, first 2500 steps)
- **Dependent:** Reward density = fraction of training batches where max(rewards_per_group) > 0, logged per checkpoint
- **Controlled:** Same as H-E1; reward density logged from TRL GRPOTrainer per-batch reward output (zero additional cost)

---

## Experimental Setup

### Dataset
- **Name:** APPS + CodeContests (reward logs from H-E1 training runs)
- **Type:** standard
- **Source:** codeparrot/apps + deepmind/code_contests (HuggingFace; confirmed working in H-E1)
- **Path:** h-e1/logs/reward_density_{condition}.csv (4 CSVs, 10 checkpoints each)
- **Hypothesis Fit:** H-E1 produced per-batch reward logs for all 4 conditions at 10 checkpoints (every 500 steps). H-M1 reuses these logs to compute reward density per checkpoint per condition — zero additional training cost.

### Model
- **Name:** DeepSeek-Coder-7B-base (checkpoints from H-E1)
- **Type:** Decoder-only transformer, 7B parameters
- **Source:** deepseek-ai/DeepSeek-Coder-7B-base (HuggingFace)
- **Hypothesis Fit:** H-E1 produced 4 final checkpoints (curriculum, uniform, easy_only, hard_only). H-M1 reuses these checkpoints and their associated reward density CSV logs — no new training required.

---

## Verification Protocol

1. From the 4-condition training runs executed in H-E1, extract per-batch reward logs for all 10 checkpoints (every 500 steps).
2. Compute reward density per checkpoint per condition: count batches where max(G=8 rewards) > 0, divided by total batches in that interval.
3. Compute mean reward density for steps 0-2500 (checkpoints 1-5) for curriculum vs. uniform conditions.
4. Test: mean reward density (curriculum, steps 0-2500) > mean reward density (uniform, steps 0-2500) using one-tailed Wilcoxon signed-rank test across 5 checkpoint observations.
5. Plot reward density time series for all 4 conditions to visualize divergence pattern.

---

## Success Criteria

- **Primary:** Mean reward density in curriculum condition steps 0-2500 > mean reward density in uniform condition steps 0-2500 (one-tailed p < 0.05)
- **Secondary:** Reward density in easy-only condition ≥ curriculum early phase (confirming tier-difficulty correlation assumption A1)

---

## Baseline & Comparison Targets

| Baseline | Description |
|----------|-------------|
| Uniform condition (H-E1) | Uniform random sampling from APPS+CodeContests |
| Easy-only condition (H-E1) | Only tier 0-2 problems (upper bound on early reward density) |
| Hard-only condition (H-E1) | Only tier 3-4 problems (lower bound on early reward density) |

---

## Failure Response

- IF fails (no reward density difference between curriculum and uniform): EXPLORE — check if A1 violated (tier 0-2 problems also too hard for model at init); if so, document as assumption failure; paper can still report H-E1 empirical finding with different mechanistic attribution (problem coverage rather than gradient quality)

---

## Phase 2B Source

- Section 2.2 (H-M1 specification)
- Section 3.1 (dependency: H-E1 → H-M1)
- Section 4.1 (Risk R1: Tier Difficulty Mismatch, Risk R2: Reward Density ≠ Causation)
- Source: Phase 2A Causal Step 1, Assumption A2
