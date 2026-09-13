# Hallucination Detection Guide

> Reference file for Phase 5 Step 1: Initialize Baseline Comparison
> Called by: step-01-init.md section 1.4 (via `{hallucination_detection}` frontmatter reference)
> Extracted to reduce step file size and enable reusability
>

---

## Purpose

Verify that Phase 4 results actually exist, were not fabricated, and were from real experiments (not synthetic/mock data).

---

## Basic Existence Checks

| Verification | Method | Criteria |
|--------------|--------|----------|
| **Code exists** | Check `train.py`, `model.py` files | At least 2 files exist |
| **Result data** | Read `results.csv` | Row count ≥ 10 |
| **Data diversity** | Check variance of psi, loss values | variance > 0 (not constant) |
| **Report match** | Compare `experiment_results.json` values with CSV data | Within 10% error |

---

## Synthetic/Mock Data Detection (CRITICAL!)

### Red Flag Indicators

| Check | Method | Red Flags |
|-------|--------|-----------|
| **Experiment log exists** | Check `{code_folder}/experiment.log` | Missing = likely mock |
| **Log has real content** | Read experiment.log, check for training output | Empty or placeholder text |
| **Checkpoint has PID** | Check `04_checkpoint.yaml` → `experiment_pid` | Missing or null = no execution |
| **Timestamp consistency** | Compare file creation times | All same time = bulk generated |
| **Data pattern analysis** | Check for suspicious patterns in results.csv | See patterns below |

### Suspicious Data Patterns

| Pattern | Description | Detection Method |
|---------|-------------|------------------|
| Too perfect values | Values exactly at 0.5, 1.0, etc. | All psi values are multiples of 0.1 |
| Identical values across seeds | Same results despite different random seeds | Unique values < 50% of total values |
| No training progression | Loss does not decrease during training | Initial loss ≤ final loss for same LR |
| Unrealistic precision | Consistently same decimal places | All values have exactly 16 decimal places |
| Sequential/patterned values | Values in perfect ascending/descending order | psi values are already sorted |

---

## Execution Evidence Verification

### Step 1: Check experiment log

| Check | Condition | Result |
|-------|-----------|--------|
| Log file exists | `{hypothesis_folder}/code/experiment.log` exists | FAIL if missing: "experiment may not have been executed" |
| Log has content | Log content length ≥ 1000 characters | WARNING if shorter: "suspiciously short" |
| Log has epoch info | Contains "Epoch" or "epoch" text | FAIL if missing: "likely not a real training run" |

### Step 2: Check checkpoint for execution evidence

| Check | Condition | Result |
|-------|-----------|--------|
| Experiment PID recorded | `04_checkpoint.yaml` → `experiment_pid` is not null | WARNING if null: "No experiment PID recorded" |
| Experiment completed | `partial_results.experiment_status` = "completed" | WARNING if not: "not marked as completed" |

### Step 3: Timestamp sanity check

| Check | Condition | Result |
|-------|-----------|--------|
| File creation timing | Time difference between experiment.log and results.csv ≥ 1 second | WARNING if < 1 second: "created simultaneously - suspicious" |

---

## Verification Result Decision Matrix

| Result | Action |
|--------|--------|
| All checks PASS | Proceed to next section |
| Minor warnings (1-2) | Log warnings, proceed with caution |
| Multiple warnings (3+) | STOP - "Possible hallucination/mock data detected" |
| Critical failure | STOP - "Hallucination detected" |

**On verification failure:**
- Clear error → STOP - "Hallucination detected"
- Multiple warnings → STOP - "Suspicious data patterns detected"
- Minor warning → Output warning and proceed with caution
