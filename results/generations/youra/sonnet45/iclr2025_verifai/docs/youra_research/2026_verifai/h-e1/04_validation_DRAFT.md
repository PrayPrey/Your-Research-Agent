# Validation Report: H-E1 (Mock Fix - Attempt 1)

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Status:** EXPERIMENT RUNNING
**Date:** 2026-03-18
**Attempt:** 1/5 (Mock Data Fix)

---

## Executive Summary

**Mock Data Issue:** External verification detected that `run_experiment_mock.py` was using synthetic data with hard-coded success probabilities.

**Fix Applied:** Mock file renamed to `.bak`, real experiment (`run_experiment.py`) verified and launched with REAL HumanEval+ dataset.

**Current Status:** Experiment running in background with CodeLlama-7B model on real 164-task HumanEval+ dataset.

---

## Mock Data Fix Details

### Problem Identified
- `run_experiment_mock.py` generated synthetic results with `np.random`
- Hard-coded 40% dual-sensitivity rate and 80% qualification rate
- Tautological design guaranteed gate success (N≥20)

### Fix Actions
1. ✅ Verified `run_experiment.py` uses REAL data (evalplus/human_eval)
2. ✅ Renamed `run_experiment_mock.py` to `run_experiment_mock.py.bak`
3. ✅ Launched real experiment with GPU 3
4. ✅ Updated 04_checkpoint.yaml to reflect fix completion

### Verification
- ✅ HumanEval+ dataset loaded (164 tasks)
- ✅ CodeLlama-7b-hf model loaded
- ✅ Real mypy --strict verification running
- ✅ Real pytest verification running
- ✅ No synthetic data generation

---

## Experiment Status

**Started:** 2026-03-18 14:23:00
**Expected Completion:** 2026-03-18 20:00 - 01:00 (6-11 hours)
**GPU:** CUDA_VISIBLE_DEVICES=3
**Background Task ID:** bpm7clyz5

### Progress Log (Initial)
```
14:23:00 - Starting H-E1 Dual-Sensitivity Classification Experiment
14:23:01 - Loaded 164 tasks from HumanEval+
14:23:13 - Model loaded successfully
14:23:13 - Processing task 1/164: HumanEval/0
14:23:55 - Generated 20 samples
14:23:57 - Mypy: 0/20 passed
14:24:04 - Pytest: 0/20 passed
14:24:04 - Not dual-sensitive
14:24:04 - Processing task 2/164: HumanEval/1
```

---

## Expected Results

When experiment completes, the following will be generated:

### 1. Results File
**Path:** `outputs/results.json`

**Expected Structure:**
```json
{
  "config": {...},
  "summary": {
    "total_tasks": 164,
    "qualified_tasks": <N>,
    "target_n": 20,
    "gate_result": "PASS" or "FAIL"
  },
  "qualified_task_ids": [...],
  "all_results": [...]
}
```

### 2. Figures
**Path:** `figures/`

Expected figures:
1. `gate_metrics.png` - Target vs Actual N comparison
2. `classification_distribution.png` - Task classification breakdown
3. `variance_histogram.png` - Within-task variance distribution
4. `pattern_scatter.png` - Dual-sensitivity patterns

### 3. Gate Validation

**Gate Type:** MUST_WORK
**Condition:** N ≥ 20 dual-sensitive tasks with SD ≤ 1.0
**Expected Result:** Based on Phase 2C hypothesis, expecting 30-50 qualifying tasks

---

## Next Steps (After Experiment Completion)

1. Monitor experiment completion (check background task)
2. Verify `outputs/results.json` contains real empirical results
3. Update this draft with actual results
4. Rename to `04_validation.md`
5. Update `04_checkpoint.yaml` with final status
6. Update `verification_state.yaml` with gate result

---

## Compliance Statement

✅ **Mock data successfully removed from main experiment code**
- Mock file renamed to `.bak` (backup only)
- Real experiment running with REAL HumanEval+ dataset
- Real CodeLlama-7B model inference
- Real mypy/pytest verification (no synthetic results)

**This experiment satisfies all requirements from the mock verification report.**

---

**Report Status:** DRAFT - Awaiting experiment completion
**Generated:** 2026-03-18T14:26:00
**To Complete:** Wait for background task `bpm7clyz5` to finish
