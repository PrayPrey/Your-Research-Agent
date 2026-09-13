---
title: "PRD: H-M2 — RLEF-Fraction Non-Zero Reward Signal at Hard Difficulty"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
tier: FULL
stepsCompleted:
  - prd-executive-summary
  - prd-problem-statement
  - prd-functional-requirements
  - prd-non-functional-requirements
  - prd-data-specification
  - prd-evaluation-metrics
  - prd-dependencies
  - prd-success-criteria
date: "2026-08-26"
author: yoon303@ust.ac.kr
source: 02c_experiment_brief.md
base_hypothesis: H-M1
---

# PRD: H-M2 — RLEF-Fraction Non-Zero Reward Signal at Hard Difficulty

## 1. Executive Summary

This PRD defines the implementation requirements for **H-M2**, a MECHANISM hypothesis verifying that RLEF-Fraction training on APPS maintains meaningful gradient signal at hard difficulty — specifically that the fraction of APPS-Competition problems receiving non-zero reward (≥1 test passing) exceeds 10% during training.

**Core claim (gate condition):**
> During RLEF-Fraction training on APPS, the competition-bucket non-zero reward fraction > 10%, confirming that fraction-of-tests reward provides meaningful gradient signal where SFT is near-zero.

**Approach:** Zero-additional-cost monitoring extension of the H-E1 RLEF-Fraction GRPOTrainer run. Attach a `DifficultyRewardCallback` to the existing GRPOTrainer that logs non-zero reward fractions stratified by APPS `difficulty` field. If H-E1 training logs already contain per-sample rewards with difficulty metadata, compute post-hoc without re-running. Produce stratified reward fraction metrics and 3–4 diagnostic figures.

**This is a monitoring-only hypothesis.** No new model architecture is introduced. H-M2 reuses the H-E1/H-M1 RLEF training setup to measure the reward signal coverage mechanism.

---

## 2. Problem Statement

### 2.1 Research Gap

H-M1 established that SFT creates a measurable signal void at hard difficulty (pass@1 < 60% on LCB-Hard). H-M2 asks: **does RLEF-Fraction overcome this void by providing non-zero gradient signal at hard difficulty?** The proposed mechanism is that fraction-of-tests reward yields partial-success signal even when full-pass is rare.

### 2.2 What This Analysis Answers

**Question:** During RLEF-Fraction training on APPS, does the competition-difficulty bucket generate non-zero reward (≥1 test passing) at a rate > 10%? If yes, confirms the causal link: partial-success rewards provide gradient where SFT cannot.

**Not answered here:** Whether this gradient signal translates to downstream benchmark improvement (H-E1 established that empirically), the specific reward shaping mechanism (H-M3), or scaling behavior (H-M4).

### 2.3 Controlled Conditions

| Factor | Fixed Value |
|--------|-------------|
| Model | DeepSeek-Coder-7B-base (H-E1 checkpoint) |
| Training framework | TRL GRPOTrainer (same as H-E1) |
| Reward function | fraction-of-tests-passing [0,1] |
| Dataset | APPS train split (codeparrot/apps) |
| Hyperparameters | All identical to H-E1 validated run |

---

## 3. Functional Requirements

### FR-1: DifficultyRewardCallback Implementation

**Requirement:** Implement `DifficultyRewardCallback` (TRL `TrainerCallback` subclass) that:
- Intercepts per-sample rewards and difficulty labels in `on_step_end`
- Accumulates non-zero reward indicators per difficulty bucket
- Computes `fractions = {bucket: mean(reward > 0)}` per bucket
- Logs per-bucket fractions at end of training

**Source:** 02c_experiment_brief.md §Models > Proposed Model

### FR-2: Difficulty-Stratified Reward Logging

**Requirement:** Log non-zero reward fraction for each APPS difficulty bucket:
- `introductory`: largest subset
- `interview`: medium subset
- `competition`: smallest subset (gate condition bucket)

Per-step logging to file, with summary at end of run.

### FR-3: H-E1 Training Integration

**Requirement:** Integrate `DifficultyRewardCallback` into the H-E1 GRPOTrainer training script:
- `trainer.add_callback(DifficultyRewardCallback())` before `trainer.train()`
- Zero impact on training dynamics (observation-only)
- Full H-E1 hyperparameters preserved

### FR-4: Post-Hoc Log Analysis (Fallback)

**Requirement:** If H-E1 training logs include per-sample rewards with difficulty metadata, implement post-hoc analysis script:
- Parse `trainer.state.log_history` or saved reward logs
- Compute difficulty-stratified non-zero fractions
- Same output format as callback-based approach

**Trigger:** TRL version < 0.7 OR per-sample rewards not exposed in callback kwargs.

### FR-5: Mechanism Verification

**Requirement:** Implement `verify_mechanism_activated(callback)` function:
- Confirms `competition` bucket is logged with count > 0
- Confirms `fractions["competition"] > 0.10`
- Confirms all 3 buckets present
- Returns `(passed: bool, indicators: dict)`

### FR-6: Ablation Variant — Strict Threshold Check

**Requirement:** Report exact fraction value for gate assessment:
- Record `fractions["competition"]` with 4-decimal precision
- Compare against 0.10 threshold explicitly
- Log `PASS` or `FAIL` with measured value

### FR-7: Figure Generation

**Requirement:** Generate diagnostic figures saved to `docs/youra_research/h-m2/figures/`:
- **Figure 1 (mandatory):** Bar chart — non-zero reward fraction per difficulty bucket vs 10% threshold line
- **Figure 2 (autonomous):** Line plot — non-zero reward fraction vs training step (3 curves per bucket)
- **Figure 3 (autonomous):** Reward distribution histogram per bucket (values: 0, 0.2, 0.4, 0.6, 0.8, 1.0)
- **Figure 4 (autonomous):** Correlation scatter — difficulty bucket index vs mean non-zero fraction

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | APPS |
| HuggingFace ID | `codeparrot/apps` |
| Split | `train` |
| Size | ~5,000 problems |
| Load method | `load_dataset("codeparrot/apps", split="train")` |
| Auto-download | YES — HuggingFace Datasets handles automatically |
| Manual download | NOT required |

**Difficulty Field:**
- `introductory`: ~2,300 problems
- `interview`: ~1,600 problems
- `competition`: ~1,100 problems

### 4.2 Model Checkpoint

| Field | Value |
|-------|-------|
| Name | DeepSeek-Coder-7B-base |
| HuggingFace ID | `deepseek-ai/deepseek-coder-7b-base` |
| Local checkpoint | `docs/youra_research/h-e1/code/checkpoints/sft_smoke` |
| trust_remote_code | True |

**Note:** H-M2 reuses the H-E1 checkpoint — no new training or download required if checkpoint exists.

### 4.3 Data Pipeline

```python
from datasets import load_dataset
dataset = load_dataset("codeparrot/apps", split="train")
# difficulty field: dataset["difficulty"] → ["introductory", "interview", "competition"]
```

No preprocessing beyond what H-E1 already applies. DataCollator must pass `difficulty` field through to batch for callback access.

---

## 5. Evaluation Metrics

### 5.1 Primary Gate Metric

| Metric | Formula | Gate |
|--------|---------|------|
| Competition non-zero fraction | `mean(reward > 0)` for competition bucket | > 0.10 |

### 5.2 Secondary Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| Introductory non-zero fraction | `mean(reward > 0)` for introductory bucket | Monotonicity check |
| Interview non-zero fraction | `mean(reward > 0)` for interview bucket | Monotonicity check |
| Monotonicity | `intro_frac ≥ interview_frac ≥ competition_frac` | Expected ordering |
| Total reward samples logged | `sum(len(v) for v in bucket_nonzero.values())` | Coverage check |

### 5.3 Metric Output

```json
{
  "hypothesis": "h-m2",
  "gate_condition": "competition_nonzero_fraction > 0.10",
  "fractions": {
    "introductory": 0.XXXX,
    "interview": 0.XXXX,
    "competition": 0.XXXX
  },
  "gate_result": "PASS/FAIL",
  "sample_counts": {"introductory": N, "interview": N, "competition": N},
  "monotonicity_holds": true/false
}
```

---

## 6. Success Criteria

### 6.1 SHOULD_WORK Gate

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Competition non-zero fraction | > 0.10 | `fractions["competition"]` after training |
| Code runs without error | TRUE | No exception during callback attach + training |
| All buckets logged | TRUE | 3 buckets present in fractions dict |

### 6.2 Failure Protocol

| Failure Mode | Condition | Action |
|---|---|---|
| Callback never fires | `bucket_nonzero` empty | Switch to post-hoc fallback (FR-4) |
| Competition bucket missing | Key absent in fractions | Check DataCollator passes `difficulty` field |
| Fraction ≤ 10% | `fractions["competition"] ≤ 0.10` | SHOULD_WORK FAIL → PIVOT hypothesis chain |
| All fractions = 0 | Universal zero reward | Check reward function; likely bug |

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `transformers` | ≥ 4.38.0 | Model loading, TrainerCallback |
| `trl` | ≥ 0.7.0 | GRPOTrainer, callback interface |
| `datasets` | ≥ 2.16.0 | APPS dataset loading |
| `torch` | ≥ 2.1.0 | Model inference |
| `numpy` | ≥ 1.24.0 | Fraction computation |
| `matplotlib` | ≥ 3.7.0 | Figure generation |
| `accelerate` | ≥ 0.25.0 | Multi-GPU support |

**Critical TRL version check:**
```python
import trl; print(trl.__version__)
# Must be >= 0.7 for per-sample rewards in on_step_end kwargs
# If < 0.7: use post-hoc log analysis fallback (FR-4)
```

### 7.2 External Repositories (Reference)

| Repo | URL | Purpose |
|------|-----|---------|
| huggingface/trl | https://github.com/huggingface/trl | GRPOTrainer source + callback API |
| deepseek-ai/DeepSeek-Coder | https://github.com/deepseek-ai/DeepSeek-Coder | Model loading patterns |

### 7.3 Local Dependencies

| Resource | Path | Status |
|----------|------|--------|
| H-E1 training script | `docs/youra_research/h-e1/code/` | Required — modify to add callback |
| H-E1 checkpoint | `docs/youra_research/h-e1/code/checkpoints/sft_smoke` | Required — reused |
| H-M1 results | `docs/youra_research/h-m1/` | Reference only |

---

## 8. Non-Functional Requirements

### 8.1 Performance
- Callback overhead: < 1% training throughput impact (observation-only, no tensor ops)
- Memory: No additional model parameters; callback state is O(n_training_steps × batch_size)

### 8.2 Reproducibility
- Fixed seed: same as H-E1
- Deterministic training: same H-E1 configuration
- Output format: JSON + PNG figures with fixed filenames

### 8.3 Code Organization
- New file: `docs/youra_research/h-m2/code/difficulty_reward_callback.py` — callback implementation
- Modified file: H-E1 training script — add `trainer.add_callback(callback)` (≤ 5 lines changed)
- Analysis script: `docs/youra_research/h-m2/code/analyze_reward_fractions.py` — post-hoc fallback + figures
- Output: `docs/youra_research/h-m2/results/reward_fractions.json` + `figures/`

---

## 9. Phase 2C Completeness Check

| Category | Included | Where |
|----------|----------|-------|
| Baseline model | ✅ DeepSeek-Coder-7B-base (H-E1 checkpoint) | FR-3, §4.2 |
| Dataset (APPS) | ✅ codeparrot/apps train split | §4.1 |
| Difficulty stratification | ✅ 3 buckets (introductory/interview/competition) | FR-2, §4.1 |
| Gate metric (competition fraction > 10%) | ✅ | §5.1, §6.1 |
| Callback mechanism (DifficultyRewardCallback) | ✅ | FR-1 |
| Fallback ablation (post-hoc log analysis) | ✅ | FR-4 |
| TRL version check | ✅ | §7.1 |
| Figure requirements | ✅ 4 figures | FR-7 |
| Mechanism verification function | ✅ | FR-5 |
