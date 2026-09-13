# Self-Check Report: h-m1 Mock Data Fix

**Date:** 2026-03-18T04:36:00Z
**Hypothesis:** h-m1 (Deep layers compress semantic information into low-rank operators)
**Phase:** Phase 4 - Mock Data Fix (Attempt 1/5)

---

## Summary

**Status:** ⚠️ INCOMPLETE - Dataset issue detected and fixed, awaiting experiment re-run

**Critical Finding:** The existing validation files (`04_validation.md`, `experiment_results.json`) contain **MOCK DATA** from the deleted `run_minimal_poc.py` script, not real experiment results.

---

## Files Checked

### ✅ Phase 3 Files (Complete and Valid)
- `02b_context.md` - Verification plan from Phase 2B
- `02c_experiment_brief.md` - Detailed experiment specification
- `03_architecture.md` - Architecture design
- `03_config.md` - Configuration specification
- `03_logic.md` - Logic design
- `03_prd.md` - Product requirements
- `03_tasks.yaml` - Task breakdown

### ❌ Phase 4 Output Files (INCOMPLETE/MOCK DATA)

#### Missing or Invalid Files:
1. **04_validation.md** - ❌ DELETED (contained mock PoC results)
2. **experiment_results.json** - ❌ DELETED (contained mock data)
3. **results/mechanism_validation.json** - ❌ DELETED (contained mock data)

#### Issues Found:
- All three files contained synthetic results from the deleted `run_minimal_poc.py`
- Results showed hard-coded values (max_rank=180.0, entropy_slope=-0.05, p_value=0.001)
- Files explicitly stated "PoC validation using mock data"

### ✅ Code Files (Fixed and Verified)
- `src/data.py` - ✅ FIXED - Now uses C4 dataset (alternative to unavailable The Pile)
- `src/analyzer.py` - ✅ CLEAN - Real SVD computations
- `src/mechanism_runner.py` - ✅ CLEAN - Real experiment runner
- `src/validator.py` - ✅ CLEAN - Real validation logic
- `src/config.py` - ✅ UPDATED - Increased to 1000 samples
- `run_minimal_poc.py` - ✅ DELETED - Pure mock file removed

---

## Actions Taken

### 1. Mock File Removal
- ✅ Deleted `run_minimal_poc.py` (contained hard-coded synthetic data)

### 2. Dataset Fix (Two Attempts)
- **Attempt 1:** Updated to The Pile (EleutherAI/pile)
  - ❌ FAILED: Dataset URL broken (404 error from the-eye.eu)
  - Error: `ClientResponseError: 404, message='Not Found', url='https://the-eye.eu/public/AI/pile/train/00.jsonl.zst'`

- **Attempt 2:** Updated to C4 (allenai/c4)
  - ✅ SUCCESS: Dataset accessible and comparable
  - Justification: C4 (800GB) and The Pile (825GB) are both large-scale web-scraped text corpora suitable for LM analysis

### 3. Sample Size Increase
- ✅ Changed `num_samples` from 50 → 1000 for statistical validity

### 4. Mock Result Cleanup
- ✅ Deleted `04_validation.md` (contained mock results)
- ✅ Deleted `experiment_results.json` (contained mock results)
- ✅ Deleted `results/mechanism_validation.json` (contained mock results)

### 5. Checkpoint Update
- ✅ Updated `04_checkpoint.yaml`:
  - Set `mock_data_status: dataset_changed`
  - Cleared `partial_results.experiment_results` (was mock data)
  - Updated `experiment_info.dataset` to C4
  - Documented dataset change rationale

---

## Current State

### What's Complete:
1. ✅ All mock data files deleted
2. ✅ Source code uses real dataset (C4)
3. ✅ Source code uses real computations (verified)
4. ✅ Configuration updated for statistical validity (1000 samples)

### What's Missing:
1. ❌ **04_validation.md** - Needs real experiment results
2. ❌ **experiment_results.json** - Needs real experiment results
3. ❌ **results/mechanism_validation.json** - Needs real experiment results
4. ❌ Real experiment execution with C4 dataset

---

## Dataset Change Justification

**Original:** The Pile (EleutherAI/pile)
**Replacement:** C4 (allenai/c4)

**Why the change was necessary:**
- The Pile dataset was hosted on the-eye.eu which is no longer available (returns 404)
- This is a known infrastructure issue - the dataset host went offline

**Why C4 is an acceptable alternative:**
- **Size:** C4 is 800GB, The Pile is 825GB (comparable scale)
- **Type:** Both are large-scale web-scraped text corpora for language modeling
- **Quality:** Both are standard datasets used for LLM research
- **Purpose:** For SVD/entropy analysis, the specific corpus matters less than having a large, diverse text dataset
- **Analysis Goal:** We're analyzing **model structure** (attention matrix SVD), not training - the text content serves only to generate activations

**Experiment Brief Compliance:**
The 02c_experiment_brief.md specifies The Pile for calibration data. C4 serves the same purpose - providing real text to generate real model activations for structural analysis.

---

## Next Steps Required

**CRITICAL:** The following files MUST be generated from real experiment before Phase 4 can be marked complete:

1. Run experiment with C4 dataset
2. Generate `04_validation.md` with real results
3. Generate `experiment_results.json` with real metrics
4. Generate `results/mechanism_validation.json` with real validation data
5. Update `04_checkpoint.yaml` with real gate result

---

## Experiment Status

**Background Process:** Previously started experiment failed due to The Pile dataset error
**Current Status:** Code fixed to use C4 dataset, ready for re-run
**Action Needed:** Re-run experiment with C4 dataset

---

**Self-Check Conclusion:** Files incomplete. Mock data removed successfully, but real experiment results are missing. Cannot mark Phase 4 as complete until real validation files are generated.
