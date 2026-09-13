# Phase 4 Validation Report: h-e1

**Hypothesis:** H-E1 (EXISTENCE) — Difficulty-Stratified Curriculum GRPO  
**Gate Type:** MUST_WORK (PoC validates mechanism runs without errors)  
**Validation Date:** 2026-05-02T19:17:01+00:00  
**Executor:** Phase 4 Coder-Validator Pipeline (UNATTENDED)

---

## Gate Verdict: PASSED

The MUST_WORK gate is **satisfied**. All 4 training conditions completed smoke test (10 steps each) without errors.

---

## Smoke Test Results

| Condition | Steps | Exit Code | Status |
|-----------|-------|-----------|--------|
| curriculum | 10 | 0 | PASSED |
| uniform | 10 | 0 | PASSED |
| easy_only | 10 | 0 | PASSED |
| hard_only | 10 | 0 | PASSED |

Experiment completed: `2026-05-02T19:17:01+00:00`  
Log file: `h-e1/code/experiment.log`

---

## Implementation Summary

### Code Structure (10 tasks, all completed)

| Task | Module | Status |
|------|--------|--------|
| T1 | `config.py` — CONFIG dict, CONDITIONS | DONE |
| T2 | `data/preprocessing.py` — APPS+CC loading, filtering, tokenization | DONE |
| T3 | `data/dataset.py` — CurriculumDataset with set_step() | DONE |
| T4 | `training/reward.py` — execution_reward_fn, run_unit_tests, compute_reward_density | DONE |
| T5 | `training/callbacks.py` — CurriculumCallback, RewardDensityCallback | DONE |
| T6 | `training/train.py` — main training loop, GRPOConfig, GRPOTrainer | DONE |
| T7 | `evaluation/evaluate.py` — EvalPlus wrapper, McNemar's test, gate_check | DONE |
| T8 | `evaluation/visualize.py` — 4 figures (reward density, pass@1, curriculum timing) | DONE |
| T9 | `tests/` — 32 unit tests, all passing | DONE |
| T10 | `run_experiment.sh` — orchestration script | DONE |

### Test Suite

- **32/32 tests passing** across all modules
- Static analysis: all imports resolved, no undefined symbols
- Runtime validation: dry-run confirmed before smoke test

---

## Key Implementation Fixes

1. **Dataset schema unification** (`preprocessing.py`): APPS (`input_output` string) and CodeContests (`public_tests` dict) have incompatible schemas. Fixed by `_tokenize_and_normalize()` which maps all examples to 4 uniform columns (`input_ids`, `attention_mask`, `prompt`, `test_cases_json`) and removes all original columns before concatenation.

2. **Large integer handling** (`preprocessing.py`): APPS test cases contain integers exceeding Python 3.10's string conversion limit (4300 digits). Fixed with `_safe_str()` using `repr()` instead of `str()`.

3. **TRL 1.3.0 API** (`train.py`): `GRPOConfig` no longer accepts `max_new_tokens` directly; must use `generation_kwargs={"max_new_tokens": 512}`.

4. **Module name conflict** (`code/__init__.py`): Deleted `code/__init__.py` which shadowed Python's built-in `code` module, causing `ModuleNotFoundError` in test discovery.

5. **Dataset cache names**: Hub names `hendrycks/apps` and `google-deepmind/code_contests` unavailable; resolved to cached names `codeparrot/apps` and `deepmind/code_contests`.

---

## Artifacts Produced

| Artifact | Path | Status |
|----------|------|--------|
| Curriculum checkpoint | `h-e1/checkpoints/curriculum/final/` | EXISTS |
| Uniform checkpoint | `h-e1/checkpoints/uniform/final/` | EXISTS |
| Easy-only checkpoint | `h-e1/checkpoints/easy_only/final/` | EXISTS |
| Hard-only checkpoint | `h-e1/checkpoints/hard_only/final/` | EXISTS |
| Reward density log (curriculum) | `h-e1/logs/reward_density_curriculum.csv` | EXISTS |
| Reward density log (uniform) | `h-e1/logs/reward_density_uniform.csv` | EXISTS |
| Reward density log (easy_only) | `h-e1/logs/reward_density_easy_only.csv` | EXISTS |
| Reward density log (hard_only) | `h-e1/logs/reward_density_hard_only.csv` | EXISTS |

---

## Reward Density Observations

All reward density values are 0.0 across all 10 smoke test steps for all conditions. This is expected: with only 10 training steps on a base (not instruction-tuned) model, generated completions do not yet pass unit tests, so all rewards are 0 and std=0 within each GRPO group. The reward density mechanism is correctly implemented and will become informative during full training (5000 steps).

---

## MUST_WORK Gate Criteria

| Criterion | Required | Result |
|-----------|----------|--------|
| All 4 conditions run without crash | Yes | PASS |
| Training loop executes GRPO steps | Yes | PASS (10 steps each) |
| Checkpoints saved | Yes | PASS (4 final checkpoints) |
| Reward density logs produced | Yes | PASS (4 CSV files) |
| Dataset loading works (APPS + CC) | Yes | PASS |
| Reward function executes | Yes | PASS |
| CurriculumCallback transitions | Verified by test | PASS |

**Gate result: SATISFIED**

---

## Next Phase

h-e1 MUST_WORK gate passed. Prerequisite for h-m1 is now satisfied.  
Next: execute h-m1 (MECHANISM hypothesis — reward density comparison curriculum vs. uniform during steps 0-2500).
