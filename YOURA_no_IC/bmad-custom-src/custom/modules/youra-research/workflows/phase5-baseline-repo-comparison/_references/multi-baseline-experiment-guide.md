# Multi-Baseline Experiment Execution Guide (Mode B)

> **Reference Guide for Phase 5 Step 9: Experiment Execution**
> Contains runner script templates, nohup patterns, and experiment orchestration

---

## Overview

**Mode B Principle:** We inject OUR algorithm into BASELINE's environment.
Each baseline uses THEIR OWN model, dataset, and config. The ONLY difference is the algorithm.

This guide provides detailed templates for executing experiments across:
- **N baselines** (from checkpoint): Each with their own environment
- **2 methods per baseline** (FIXED): `baseline_original` vs `ours_injected`
- **1 seed per run**: From baseline's config
- **Total: N×2 runs** (baselines × methods × seed — values from checkpoint SSoT)

---

## 1. Mode B Experiment Structure

### 1.1 Comparison Matrix

```
For EACH baseline (N total, from checkpoint.baselines_count):
┌────────────────────────────────────────────────────────────────┐
│ Baseline: {baseline.repo_name} │
├────────────────────────────────────────────────────────────────┤
│ Model: {baseline.model} (BASELINE's - unchanged) │
│ Dataset: {baseline.dataset} (BASELINE's - unchanged) │
│ Config: LR={baseline.lr}, ... (BASELINE's - unchanged) │
├────────────────────────────────────────────────────────────────┤
│ Run 1: --method baseline → Uses baseline's original algorithm │
│ Run 2: --method ours → Uses OUR injected algorithm │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Total Run Calculation

```
Total Runs = {baselines} baselines × {methods_per_baseline} methods × {seeds} seed = {total_runs} runs

Per baseline: 2 runs (baseline_original vs ours_injected)
- Run 1: python train.py --method baseline (baseline's algorithm)
- Run 2: python train.py --method ours (our injected algorithm)
```

---

## 2. Runner Script Templates

### 2.1 Per-Baseline Runner Template (Mode B)

This script runs BOTH methods (baseline vs ours) on a single baseline's environment.

```bash
#!/bin/bash
# =============================================================================
# Mode B Baseline Comparison Runner: {baseline.repo_name}
# =============================================================================
# Purpose: Compare baseline's algorithm vs our algorithm on BASELINE's environment
# Repository: {baseline.repo_url}
# Conda Environment: {baseline.conda_env}
#
# Mode B Principle: Use BASELINE's model, dataset, config. Only algorithm differs.
# =============================================================================

set -e # Exit on error

# === Configuration ===
CONDA_PATH="{conda_path}"
CONDA_ENV="{baseline.conda_env}"
CLONE_PATH="{baseline.clone_path}"
RESULTS_DIR="{baseline_folder}/experiments/{baseline.repo_name}"
LOG_FILE="$RESULTS_DIR/experiment.log"

# === Initialize Conda ===
source "$CONDA_PATH/etc/profile.d/conda.sh"

# === Baseline's Configuration (LOADED FROM BASELINE'S CONFIG - NOT OURS!) ===
# These values come from {baseline.clone_path}/config.yaml or defaults
SEED={baseline.seed} # From baseline's config

# === Methods to Compare ===
METHODS=("baseline" "ours")

# === Create Results Directory ===
mkdir -p "$RESULTS_DIR"

echo "=== {baseline.repo_name} Mode B Comparison ===" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Model: {baseline.model} (BASELINE's)" | tee -a "$LOG_FILE"
echo "Dataset: {baseline.dataset} (BASELINE's)" | tee -a "$LOG_FILE"
echo "Config: LR={baseline.lr}, Epochs={baseline.epochs} (BASELINE's)" | tee -a "$LOG_FILE"
echo "Total runs: ${#METHODS[@]} (baseline vs ours)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# === Run Both Methods ===
run_count=0

for method in "${METHODS[@]}"; do
    run_count=$((run_count + 1))
    echo "[Run $run_count/2] Method=$method, Seed=$SEED" | tee -a "$LOG_FILE"

    cd "$CLONE_PATH"

    # Execute training with selected method
    # --method argument switches between baseline's optimizer and our injected optimizer
    conda run -n "$CONDA_ENV" python train.py \
        --method "$method" \
        --seed "$SEED" \
        2>&1 | tee "$RESULTS_DIR/run_${method}_${SEED}.log"

    # Check exit status
    if [ $? -eq 0 ]; then
        echo "[Run $run_count/2] SUCCESS" | tee -a "$LOG_FILE"
    else
        echo "[Run $run_count/2] FAILED" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
done

echo "=== Completed ===" | tee -a "$LOG_FILE"
echo "Finished: $(date)" | tee -a "$LOG_FILE"
echo "Total: $run_count runs" | tee -a "$LOG_FILE"
```

### 2.2 Master Runner Script (Mode B)

Orchestrates all experiments across PROCEED baselines.

```bash
#!/bin/bash
# =============================================================================
# Master Experiment Runner - Mode B (N Baselines × 2 Methods)
# =============================================================================
# Mode B Principle:
# - Each baseline uses THEIR OWN model, dataset, config
# - We only inject our algorithm and compare
# - This is "baseline's home turf" - strong evidence if we still win
# =============================================================================

EXPERIMENTS_DIR="{baseline_folder}/experiments"
MASTER_LOG="$EXPERIMENTS_DIR/master_experiment.log"

cd "$EXPERIMENTS_DIR"

echo "=================================================================" | tee -a "$MASTER_LOG"
echo "=== MODE B MASTER EXPERIMENT RUNNER ===" | tee -a "$MASTER_LOG"
echo "=================================================================" | tee -a "$MASTER_LOG"
echo "Started: $(date)" | tee -a "$MASTER_LOG"

# === Configuration (from checkpoint - SSoT: workflow.yaml) ===
TOTAL_BASELINES={checkpoint.baselines_count}
METHODS_COUNT={checkpoint.methods_per_baseline}
TOTAL_RUNS={checkpoint.total_runs}

echo "Total Baselines: $TOTAL_BASELINES" | tee -a "$MASTER_LOG"
echo "Methods per Baseline: $METHODS_COUNT (baseline vs ours)" | tee -a "$MASTER_LOG"
echo "Total Runs: $TOTAL_RUNS" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# === Run All Baselines (dynamic - works for any baselines_count) ===
baseline_idx=0
for runner in run_*_comparison.sh; do
    baseline_idx=$((baseline_idx + 1))
    baseline_name="${runner#run_}"
    baseline_name="${baseline_name%_comparison.sh}"
    echo "[$baseline_idx/$TOTAL_BASELINES] Running $baseline_name comparison..." | tee -a "$MASTER_LOG"
    bash "$runner"
    if [ $? -eq 0 ]; then
        echo "[$baseline_idx/$TOTAL_BASELINES] $baseline_name completed at $(date)" | tee -a "$MASTER_LOG"
    else
        echo "[$baseline_idx/$TOTAL_BASELINES] $baseline_name FAILED at $(date)" | tee -a "$MASTER_LOG"
    fi
    echo "" | tee -a "$MASTER_LOG"
done

echo "=================================================================" | tee -a "$MASTER_LOG"
echo "=== ALL EXPERIMENTS COMPLETED ($baseline_idx/$TOTAL_BASELINES baselines) ===" | tee -a "$MASTER_LOG"
echo "=================================================================" | tee -a "$MASTER_LOG"
echo "Finished: $(date)" | tee -a "$MASTER_LOG"
```

---

## 3. nohup Launch Pattern

### 3.1 Launch Command Sequence

```bash
# Step 1: Initialize conda
source {conda_path}/etc/profile.d/conda.sh

# Step 2: Navigate to experiments directory
cd {baseline_folder}/experiments

# Step 3: Make all scripts executable
chmod +x *.sh

# Step 4: Launch with nohup
nohup bash run_all_experiments.sh > experiment.log 2>&1 &

# Step 5: Save PID
echo $! > experiment.pid
```

### 3.2 Single-Line Launch (for Bash tool)

```bash
source {conda_path}/etc/profile.d/conda.sh && cd {baseline_folder}/experiments && chmod +x *.sh && nohup bash run_all_experiments.sh > experiment.log 2>&1 & echo $! > experiment.pid
```

---

## 4. Process Status Checking

### 4.1 Check if Process Running

```bash
# Read PID from file
PID=$(cat {baseline_folder}/experiments/experiment.pid)

# Check if running (returns process info if running, empty if not)
ps -p $PID --no-headers
```

### 4.2 Status Interpretation

| ps Output | Interpretation | Action |
|-----------|----------------|--------|
| Non-empty (process info) | Still running | Wait or monitor |
| Empty | Process finished | Check log for results/errors |

### 4.3 Monitor Progress

```bash
# Real-time log monitoring
tail -f {baseline_folder}/experiments/experiment.log

# Count completed runs
grep -c "SUCCESS" {baseline_folder}/experiments/experiment.log

# Check for errors
grep -i "error\|exception\|failed" {baseline_folder}/experiments/experiment.log
```

---

## 5. Progress Counting Script (Mode B)

```bash
#!/bin/bash
# Count completed runs across all baselines (Mode B)
# Configuration: {methods_per_baseline} methods × {seeds} seed per baseline

EXPERIMENTS_DIR="{baseline_folder}/experiments"

echo "=== Mode B Experiment Progress ==="

# Dynamic progress counting (works for any baselines_count)
total=0
baseline_idx=0
for baseline_dir in "$EXPERIMENTS_DIR"/*/; do
    [ -d "$baseline_dir" ] || continue
    baseline_idx=$((baseline_idx + 1))
    baseline_name=$(basename "$baseline_dir")
    b_baseline=$(ls -1 "$baseline_dir"/run_baseline_*.log 2>/dev/null | wc -l)
    b_ours=$(ls -1 "$baseline_dir"/run_ours_*.log 2>/dev/null | wc -l)
    b_total=$((b_baseline + b_ours))
    total=$((total + b_total))
    echo "Baseline $baseline_idx ($baseline_name): $b_total / $METHODS_COUNT"
done

echo "========================="
echo "Total Runs: $total / $TOTAL_RUNS"
```

---

## 6. Resume Handling

### 6.1 Session Resume Logic

```
IF checkpoint.experiment.status == "running_detached":
    1. Read PID from checkpoint.experiment.pid
    2. Check if ps -p {pid} returns process info

    IF process still running:
        - Count completed runs from logs
        - Display "Experiments still running"
        - STOP and wait for completion

    IF process NOT running:
        - Set checkpoint.experiment.status = "completed"
        - Save checkpoint
        - Proceed to result collection
```

---

## 7. Error Handling

### 7.1 Error Classification

| Error Pattern | Error Type | Auto-Fix Available |
|---------------|------------|-------------------|
| `CUDA out of memory` | CUDA_OOM | Yes (reduce batch size) |
| `ModuleNotFoundError` | MISSING_MODULE | Yes (pip install) |
| `FileNotFoundError` | FILE_NOT_FOUND | Partial |
| `RuntimeError: CUDA` | CUDA_ERROR | Partial |
| `Permission denied` | PERMISSION | Manual |
| Other | UNKNOWN | Manual |

### 7.2 Retry Logic

```
# max_retries from checkpoint.workflow_config.experiment_retries.max_retries
# SSoT: workflow.yaml config.max_experiment_retries (default: 2)
max_retries = checkpoint["workflow_config"]["experiment_retries"]["max_retries"]

FOR attempt IN 1..max_retries:
    1. Launch experiment
    2. Wait for result

    IF success:
        BREAK

    IF error:
        - Classify error type
        - Apply quick fix (if available)
        - Log fix attempt
        - Continue to next attempt

IF all max_retries attempts failed:
    - Set status = "partial"
    - Log final error
    - Proceed with partial results
```

---

## 8. Checkpoint Update Schema (Mode B)

After experiment launch:

```yaml
experiment:
  mode: "B"
  mode_description: "OUR algorithm vs BASELINE algorithm on BASELINE's environment"
  status: "running" # or "running_detached"
  pid: {pid_value}
  started_at: "{ISO8601}"
  completed_at: null
  total_baselines: {checkpoint.baselines_count} # SSoT: workflow.yaml
  methods_per_baseline: {checkpoint.methods_per_baseline} # SSoT: workflow.yaml
  total_runs: {checkpoint.total_runs} # SSoT: workflow.yaml
  successful_runs: 0
  failed_runs: 0
  baselines_completed: # One entry per PROCEED baseline (dynamic)
    - repo_name: "{baseline.repo_name}"
      baseline_model: "{baseline.model}"
      baseline_dataset: "{baseline.dataset}"
      baseline_result: null
      ours_result: null
      winner: null
      improvement: null
      status: "pending"
    # ... repeated for each PROCEED baseline
```

After experiment completion:

```yaml
experiment:
  mode: "B"
  status: "completed" # or "partial" if some failed
  successful_runs: {checkpoint.total_runs}
  failed_runs: 0
  baselines_completed:
    - repo_name: "{baseline_1.repo_name}"
      baseline_result: 0.72
      ours_result: 0.85
      winner: "ours"
      improvement: "+18.1%"
      status: "completed"
    # ... etc
```

---

## 9. Directory Structure (Mode B)

After experiments complete:

```
{baseline_folder}/experiments/
├── run_{baseline_N}_comparison.sh # One per PROCEED baseline
├── run_all_experiments.sh
├── experiment.pid
├── experiment.log
├── master_experiment.log
└── {baseline_N}/ # One dir per PROCEED baseline
    ├── run_baseline_{seed}.log # Baseline's original algorithm
    ├── run_ours_{seed}.log # Our injected algorithm
    └── experiment.log
```

---

## 10. comparison_data.csv Format (Mode B)

```csv
baseline_repo,baseline_model,baseline_dataset,method,lr,seed,primary_metric,secondary_metric,epochs_completed
repo1,ResNet18,CIFAR10,baseline,0.1,42,0.72,0.68,200
repo1,ResNet18,CIFAR10,ours,0.1,42,0.85,0.81,200
repo2,VGG16,CIFAR100,baseline,0.01,42,0.65,0.61,200
repo2,VGG16,CIFAR100,ours,0.01,42,0.71,0.67,200
repo3,MobileNet,ImageNet,baseline,0.001,42,0.58,0.55,100
repo3,MobileNet,ImageNet,ours,0.001,42,0.63,0.60,100
```

Note: Each baseline uses its OWN model, dataset, and config. The config columns (lr, seed, epochs) are from BASELINE's configuration.

---

## Related Files

| File | Purpose |
|------|---------|
| `step-09-experiment.md` | Main step file that references this guide |
| `fair-comparison-principle.md` | Why Mode B is the fair comparison approach |
| `result-collection-guide.md` | How to parse and aggregate results |
| `figure-generation-guide.md` | How to create comparison figures |
