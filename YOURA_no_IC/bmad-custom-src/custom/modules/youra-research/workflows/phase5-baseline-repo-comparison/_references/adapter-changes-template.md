# Adapter: CHANGES.md Template

> **Reference Guide for Phase 5 Step 7 - Section 7.6**
> Template for documenting all changes made to baseline repository

---

## Purpose

Document all changes made to baseline for reproducibility.

**File:** `{baseline_folder}/changes/{repo_name}/CHANGES.md`

---

## Template

```markdown
# CHANGES.md

## Baseline: {repo_name}
## Adaptation for YouRA Fair Comparison (Mode B)

### Overview

| Field | Value |
|-------|-------|
| Date | {timestamp} |
| Original Commit | {sha} |
| Branch | youra-baseline |

### Purpose (Mode B)

This baseline has been adapted for fair comparison using Mode B:
**Inject OUR algorithm into BASELINE's environment.**

BASELINE's environment is UNCHANGED:
- SAME model architecture (BASELINE's original)
- SAME dataset (BASELINE's original)
- SAME hyperparameters (BASELINE's original)

The ONLY difference is the **algorithm/optimizer**.

See: `_references/fair-comparison-principle.md`

---

### Files Created

| File | Type | Purpose | Lines |
|------|------|---------|-------|
| `adaptations/{repo}/algorithm_injection.py` | NEW | Our optimizer/algorithm injection | ~100 |
| `adaptations/{repo}/metrics.py` | NEW | Metric injection (psi tracking) | ~120 |
| `adaptations/{repo}/results_saver.py` | NEW | Results saver (CSV format) | ~80 |
| `adaptations/{repo}/tests/test_algorithm_injection.py` | NEW | Algorithm injection tests | ~60 |
| `adaptations/{repo}/tests/test_metrics.py` | NEW | Metric tests | ~40 |
| `adaptations/{repo}/tests/test_results_saver.py` | NEW | Results saver tests | ~30 |

**Total new lines:** ~430

---

### Files Modified

| File | Change | Lines Added | Lines Modified |
|------|--------|-------------|----------------|
| `train.py` | sys.path setup for adaptations module (STEP 0) | +3 | 0 |
| `train.py` | Import algorithm injection + metrics + results | +3 | 0 |
| `train.py` | Add --method argument (baseline vs ours) | +5 | 0 |
| `train.py` | Conditional optimizer replacement | +5 | ~2 |
| `train.py` | Add metric tracking hooks | +5 | 0 |
| `train.py` | Save results at end | +3 | 0 |

**Total modifications:** ~24 lines added, ~2 lines modified

---

### What Was NOT Modified (Mode B Principle)

- [ ] Data loading code — UNCHANGED (baseline's original)
- [ ] Model architecture — UNCHANGED (baseline's original)
- [ ] Hyperparameters (lr, momentum, etc.) — UNCHANGED (baseline's original)
- [ ] Loss function — UNCHANGED
- [ ] Evaluation logic — UNCHANGED
- [ ] Training loop structure — UNCHANGED (only optimizer swap)

---

### Verification

- [x] Algorithm injection replaces/wraps optimizer only
- [x] Baseline's model architecture preserved
- [x] Baseline's dataset loading preserved
- [x] Baseline's hyperparameters preserved
- [x] Metrics computed during training
- [x] Results saved in YouRA comparison format
- [x] --method argument switches between baseline/ours
- [x] All tests pass

---

### Reproduction

To run this adapted baseline:

```bash
# Activate environment
conda activate {conda_env_name}

# Run baseline method (original)
python train.py --method baseline --seed 42

# Run our method (algorithm injected)
python train.py --method ours --seed 42
```

---

### Notes

{Any specific notes about this baseline's adaptation}
```

---

## Related Files

| File | Purpose |
|------|---------|
| `step-07-adaptation-coding.md` | Orchestration step that generates this |
| `fair-comparison-principle.md` | Core principles documented here |
| `step-08-validation.md` | Validates the adapted code |
