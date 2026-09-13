---
name: 'step-09-experiment'
description: 'Execute experiments for all PROCEED baselines (Mode B - OUR algorithm vs BASELINE algorithm on BASELINE environment)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'

# Reference Guides (READ when needed!)
experiment_guide: '{workflow_path}/_references/multi-baseline-experiment-guide.md'
result_guide: '{workflow_path}/_references/result-collection-guide.md'
fair_comparison_guide: '{workflow_path}/_references/fair-comparison-principle.md'

# File References
thisStepFile: '{workflow_path}/steps/step-09-experiment.md'
prevStepFile: '{workflow_path}/steps/step-08-validation.md'
nextStepFile: '{workflow_path}/steps/step-10-report.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
config_file: '{hypothesis_folder}/03_config.md'

# Output Files
results_folder: '{baseline_folder}/experiments/results'
comparison_data: '{baseline_folder}/experiments/comparison_data.csv'
experiment_log: '{baseline_folder}/experiments/experiment.log'

# Config: Read from checkpoint.workflow_config (Source: workflow.yaml)

# Long Experiment Support
use_nohup: true

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)

# Mock Detection Reference
mock_detection_ref: '{workflow_path}/_references/experiment-mock-detection.md'
adaptation_step: '{workflow_path}/steps/step-07-adaptation-coding.md'
---

# Step 9: Experiment Execution (Mode B - Algorithm Comparison)

> **Mode:** UNATTENDED (Fully Automatic)
> **Reference Guides:** READ `experiment_guide` for runner templates

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### 📖 File Reading Protocol (CRITICAL):

Complete execution of this step file **requires reading the entire file at once**.

**File Information**:
- 📏 Total length: ~580 lines (under 2000 lines)
- 📂 Read entire file before execution

**Required Reading Method**:
```python
# ✅ Correct Method (Recommended)
Read(file_path="{thisStepFile}") # Without limit/offset parameters

# ❌ Incorrect Method (Prohibited)
Read(file_path="{thisStepFile}", offset=0, limit=200) # Partial reading
```

### Step-Specific Rules:

- 🛑 NEVER skip experiment execution or fabricate results
- 📖 READ `{experiment_guide}` for runner script templates
- 📖 READ `{fair_comparison_guide}` to understand experiment setup
- 🎯 Execute experiments for **ALL 3 baselines** with **BOTH methods** (baseline vs ours)
- 🚫 FORBIDDEN to generate fake/synthetic results
- ✅ MUST use nohup for long-running experiments
- 📊 **{total_runs} runs** = {baselines} Baselines × {methods_per_baseline} Methods (baseline_original + ours_injected) × {seeds} Seed
  <!-- Values from checkpoint: total_runs, baselines_count, methods_per_baseline + workflow_config.experiment.seeds (SSoT: workflow.yaml) -->

---

## ⚠️ FAIR COMPARISON PRINCIPLE (MODE B)

> **READ `{fair_comparison_guide}` for complete explanation!**

**Summary:** We inject OUR **ALGORITHM** into BASELINE's **environment**.

```
FOR EACH BASELINE:
  ┌──────────────────────────────────────────────────────────────┐
  │ BASELINE's ENVIRONMENT │
  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
  │ │  Baseline │  │ Baseline │  │ Baseline │           │
  │ │   Model │  │ Dataset │  │ Config │           │
  │ └─────────────┘ └─────────────┘ └─────────────┘ │
  │ │
  │ Run 1: Baseline's Algorithm (--method baseline) │
  │ Run 2: Our Algorithm (--method ours) │
  │ │
  │ SAME model, SAME dataset, SAME config │
  │ ONLY the algorithm/optimizer differs │
  └──────────────────────────────────────────────────────────────┘
```

**The ONLY difference is the ALGORITHM being compared.**

---

## 9.0 Pre-Experiment Mock Detection (MANDATORY)

> **READ `{mock_detection_ref}` for complete verification logic!**

```python
from experiment_mock_detection import verify_pre_experiment_reality, handle_mock_detected

print("🔍 Pre-experiment mock detection...")

result = verify_pre_experiment_reality(
    baseline_folder=baseline_folder,
    checkpoint_file=f"{baseline_folder}/05_baseline_checkpoint.yaml",
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
)

IF result["detected"]:
    handle_mock_detected(checkpoint_file, result, "pre_experiment")
    print("🚨 Mock setup detected! Returning to Step 7 for fix...")
    Load, read entire file, then execute: {adaptation_step}
    EXIT

print("✅ Pre-experiment check passed - proceeding with real experiments")
```

---

## 9.1 Pre-Flight Checks

### Load Checkpoint

Required fields:
- `selection.baselines` - Array of 3 baselines with status, clone_path, conda_env
- `baselines[i].baseline_environment` - Model, dataset, config from baseline
- `baselines[i].injection_analysis` - Injection point information
- `conda_path` - Path to conda installation

```python
baselines = [b for b in checkpoint.selection.baselines if b.status == "PROCEED"]

# Each baseline has its own environment
for baseline in baselines:
    print(f"Baseline: {baseline.repo_name}")
    print(f" Model: {baseline.baseline_environment.model}")
    print(f" Dataset: {baseline.baseline_environment.dataset}")
    print(f" Config: {baseline.baseline_environment.config}")
```

### Verify Validation Passed

**FOR EACH baseline:**

| Condition | Action |
|-----------|--------|
| `runtime_passed` = true | Include in experiment list |
| `runtime_passed` ≠ true AND cycles ≥ 3 | Log warning, include anyway |
| `runtime_passed` ≠ true AND cycles < 3 | Skip this baseline |

**Minimum 1 baseline required to proceed.**

---

## 9.2 Environment Setup

1. Load `conda_path` from checkpoint (auto-detect if null)
2. Create results folder: `mkdir -p {results_folder}`

---

## 9.3 Dynamic Entry Point Discovery

Use Serena to find modified training script:

```
mcp__serena__search_for_pattern(
    pattern="from adaptations.*import|get_our_optimizer|--method",
    relative_path=clone_path
)
```

Verify training script has `--method` argument (baseline vs ours)

---

## 9.4 Execute Experiments (nohup)

> **READ `{experiment_guide}` for complete runner script templates!**

### 9.4.1 Create Runner Scripts (Mode B)

Generate these scripts for each baseline:

| Script | Purpose |
|--------|---------|
| `run_{baseline_1}_comparison.sh` | Baseline 1: baseline vs ours (2 runs) |
| `run_{baseline_2}_comparison.sh` | Baseline 2: baseline vs ours (2 runs) |
| `run_{baseline_3}_comparison.sh` | Baseline 3: baseline vs ours (2 runs) |
| `run_all_comparisons.sh` | Master orchestrator ({total_runs} total runs) |

**Runner Script Template (Mode B):**

```bash
#!/bin/bash
# Mode B Comparison: {baseline_name}
# Uses BASELINE's model, dataset, config
# Compares: baseline's algorithm vs our algorithm

BASELINE_NAME="{baseline_name}"
CLONE_PATH="{clone_path}"
CONDA_ENV="baseline-{baseline_name}"
RESULTS_DIR="{results_folder}/{baseline_name}"

mkdir -p $RESULTS_DIR

source {conda_path}/etc/profile.d/conda.sh
conda activate $CONDA_ENV
cd $CLONE_PATH

# Get baseline's config (from their code)
LR={baseline_lr}
EPOCHS={baseline_epochs}
BATCH_SIZE={baseline_batch_size}
SEED=42

echo "=== Running baseline's original algorithm ==="
python train.py --method baseline --lr $LR --epochs $EPOCHS --batch-size $BATCH_SIZE --seed $SEED \
    2>&1 | tee $RESULTS_DIR/baseline_log.txt

echo "=== Running our algorithm (injected) ==="
python train.py --method ours --lr $LR --epochs $EPOCHS --batch-size $BATCH_SIZE --seed $SEED \
    2>&1 | tee $RESULTS_DIR/ours_log.txt

echo "=== Comparison complete for $BASELINE_NAME ==="
```

**Values come from BASELINE's config:**
- `learning_rate` from baseline's README/config
- `epochs` from baseline's README/config
- `batch_size` from baseline's README/config

### 9.4.2 Launch with nohup

```bash
source {conda_path}/etc/profile.d/conda.sh && \
cd {baseline_folder}/experiments && \
chmod +x *.sh && \
nohup bash run_all_comparisons.sh > experiment.log 2>&1 & \
echo $! > experiment.pid
```

### 9.4.3 Save Experiment State

Update checkpoint:
```yaml
experiment:
  pid: {pid_value}
  started_at: "{timestamp}"
  status: "running"
  mode: "B"
  total_runs: {checkpoint.total_runs} # SSoT: workflow.yaml
  runs_per_baseline: {checkpoint.methods_per_baseline} # SSoT: workflow.yaml
```

---

## 9.5 Initial Status Check

1. Wait 60 seconds for early failures
2. Check if process still running: `ps -p {pid} --no-headers`

| Process Status | Log Contains Error? | Action |
|----------------|---------------------|--------|
| NOT running | Yes | Set status="failed", go to 9.7 (Error Handling) |
| NOT running | No | Set status="completed", go to 9.6 (Collect Results) |
| Running | - | Set status="running_detached", display monitor command |

### Resume Handling

When `status == "running_detached"`:
1. Check if PID still running
2. If running → wait
3. If not running → go to 9.6 (Collect Results)

---

## 9.6 Collect Results (Mode B)

> **READ `{result_guide}` for complete parsing and aggregation logic!**

### Result Sources (6 sets - Mode B)

| Baseline | Method | Location |
|----------|--------|----------|
| baseline_1 | baseline_original | `experiments/{baseline_1}/baseline_log.txt` |
| baseline_1 | ours_injected | `experiments/{baseline_1}/ours_log.txt` |
| baseline_2 | baseline_original | `experiments/{baseline_2}/baseline_log.txt` |
| baseline_2 | ours_injected | `experiments/{baseline_2}/ours_log.txt` |
| baseline_3 | baseline_original | `experiments/{baseline_3}/baseline_log.txt` |
| baseline_3 | ours_injected | `experiments/{baseline_3}/ours_log.txt` |

### Create comparison_data.csv (Mode B)

Required columns:
- `baseline_repo` - Which baseline repository
- `baseline_model` - Baseline's model architecture
- `baseline_dataset` - Baseline's dataset
- `method` - "baseline" or "ours"
- `lr` - Learning rate (from baseline's config)
- `seed` - Random seed
- `primary_metric` - Main metric value (e.g., psi, accuracy)
- `secondary_metric` - Secondary metric (e.g., loss)
- `epochs_completed` - Number of epochs

**{total_runs} rows expected ({baselines_count} baselines × {methods_per_baseline} methods)**

**Example comparison_data.csv (Mode B):**

```csv
baseline_repo,baseline_model,baseline_dataset,method,lr,seed,primary_metric,secondary_metric,epochs_completed
cifar-cnn-repo,ResNet18,CIFAR10,baseline,0.01,42,0.85,0.45,100
cifar-cnn-repo,ResNet18,CIFAR10,ours,0.01,42,0.87,0.42,100
pytorch-mnist,LeNet,MNIST,baseline,0.001,42,0.92,0.28,50
pytorch-mnist,LeNet,MNIST,ours,0.001,42,0.94,0.25,50
imagenet-trainer,ResNet50,ImageNet,baseline,0.1,42,0.76,0.89,90
imagenet-trainer,ResNet50,ImageNet,ours,0.1,42,0.78,0.85,90
```

---

## 9.6.5 Post-Experiment Mock Verification (MANDATORY)

> **READ `{mock_detection_ref}` for complete verification logic!**

🚨 **CRITICAL:** Verify collected results are from REAL experiments, not fabricated data.

```python
from experiment_mock_detection import verify_experiment_results_reality, handle_mock_detected

print("🔍 Post-experiment mock verification...")

result = verify_experiment_results_reality(
    comparison_data_file=f"{baseline_folder}/experiments/comparison_data.csv",
    experiment_log_file=f"{baseline_folder}/experiments/experiment.log",
    checkpoint_file=f"{baseline_folder}/05_baseline_checkpoint.yaml",
    experiment_brief_file=f"{hypothesis_folder}/02c_experiment_brief.md"
)

IF result["detected"]:
    handle_mock_detected(checkpoint_file, result, "post_experiment")
    print("🚨 Mock results detected! Returning to Step 7 for fix...")
    Load, read entire file, then execute: {adaptation_step}
    EXIT

print("✅ Post-experiment verification passed - results appear real")
checkpoint.mock_verification = {"pre": "PASSED", "post": "PASSED", "verified_at": now()}
SAVE checkpoint
```

---

## 9.7 Error Handling

> **READ `{experiment_guide}` Section 5 for error handling details!**

### Quick Fix (up to N attempts, from checkpoint)

```python
# Read max retries from checkpoint (SSoT: workflow.yaml → step-01-init → checkpoint)
max_experiment_retries = checkpoint["workflow_config"]["experiment_retries"]["max_retries"]
# Default: 2 (from workflow.yaml config.max_experiment_retries)
```

| Error Type | Fix |
|------------|-----|
| CUDA_OOM | Reduce batch_size (baseline's config may be too aggressive) |
| ModuleNotFoundError | pip install {package} in baseline's conda env |
| FileNotFoundError | Verify baseline's paths |

If all `max_experiment_retries` attempts fail: `status = "partial"`, proceed with partial results

---

## 9.8 LLM-Autonomous Comparison Figure Generation

> **Purpose:** Generate research-appropriate comparison figures showing OUR algorithm vs BASELINE's algorithm.
> **Key Principle:** LLM decides what figures best illustrate the algorithm comparison.

### 9.8.1 Create Figures Directory

```python
figures_folder = f"{baseline_folder}/figures"
Bash: mkdir -p {figures_folder}
```

### 9.8.2 Analyze Available Comparison Data (Mode B)

**Step 1: Read comparison data and understand structure**

```python
# Read comparison data
comparison_csv = f"{baseline_folder}/experiments/comparison_data.csv"
Read(comparison_csv)

# Identify available dimensions (Mode B)
data_analysis = {
    "baselines": [...], # baseline_1, baseline_2, baseline_3
    "methods": ["baseline", "ours"], # Two methods per baseline
    "baseline_models": [...], # Each baseline's model
    "baseline_datasets": [...], # Each baseline's dataset
    "metric_columns": [...], # primary_metric, secondary_metric
}
```

### 9.8.3 Analyze Research Context

**Step 2: Understand what this baseline comparison is about**

```python
# Read experiment brief for context
Read(f"{hypothesis_folder}/02c_experiment_brief.md")

# Extract comparison focus (Mode B)
research_context = {
    "hypothesis_type": "...", # What our algorithm improves
    "primary_metric": "...", # psi, accuracy, etc.
    "comparison_goal": "Show our algorithm outperforms baseline's on their own turf",
    "baseline_count": checkpoint["baselines_count"], # SSoT: workflow.yaml
    "methods_per_baseline": checkpoint["methods_per_baseline"], # SSoT: workflow.yaml
}
```

### 9.8.4 Mode B Figure Types

**Recommended figures for Mode B comparison:**

1. **Per-Baseline Comparison Bar Chart**
   - X-axis: Baselines (baseline_1, baseline_2, baseline_3)
   - Y-axis: Primary metric
   - Groups: baseline_original vs ours_injected
   - Shows: Head-to-head comparison on each baseline's turf

2. **Improvement Summary Chart**
   - Shows: % improvement of ours vs baseline for each baseline repo
   - Highlights: Where our algorithm wins/loses

3. **Win/Lose Matrix**
   - Rows: Baselines
   - Columns: Metrics
   - Cells: ours > baseline? (win/lose/tie)

4. **Cross-Baseline Generalization**
   - Shows: Does our algorithm consistently improve across different environments?

### 9.8.5 Generate Figure Code Dynamically

**Step 4: Write and execute matplotlib code**

```python
generate_figures_script = f"{baseline_folder}/experiments/generate_figures.py"

# LLM writes script based on actual Mode B comparison structure
script_content = '''
#!/usr/bin/env python3
"""
Mode B Comparison Figures: Our Algorithm vs Baseline's Algorithm
on Baseline's Environment (model, dataset, config)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path

COMPARISON_DATA = "{baseline_folder}/experiments/comparison_data.csv"
FIGURES_DIR = Path("{baseline_folder}/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(COMPARISON_DATA)
    print(f"Loaded {len(df)} rows")
    print(f"Baselines: {df['baseline_repo'].unique().tolist()}")
    print(f"Methods: {df['method'].unique().tolist()}")

    # 1. Per-Baseline Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    baselines = df['baseline_repo'].unique()
    x = np.arange(len(baselines))
    width = 0.35

    baseline_vals = df[df['method'] == 'baseline']['primary_metric'].values
    ours_vals = df[df['method'] == 'ours']['primary_metric'].values

    ax.bar(x - width/2, baseline_vals, width, label='Baseline Algorithm')
    ax.bar(x + width/2, ours_vals, width, label='Our Algorithm')

    ax.set_xlabel('Baseline Repository')
    ax.set_ylabel('Primary Metric')
    ax.set_title('Mode B Comparison: Our Algorithm vs Baseline on Their Environment')
    ax.set_xticks(x)
    ax.set_xticklabels(baselines, rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'mode_b_comparison.png', dpi=150)
    plt.close()

    # 2. Improvement Chart
    improvements = []
    for baseline in baselines:
        baseline_val = df[(df['baseline_repo'] == baseline) & (df['method'] == 'baseline')]['primary_metric'].values[0]
        ours_val = df[(df['baseline_repo'] == baseline) & (df['method'] == 'ours')]['primary_metric'].values[0]
        improvement = ((ours_val - baseline_val) / baseline_val) * 100
        improvements.append(improvement)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['green' if imp > 0 else 'red' for imp in improvements]
    ax.bar(baselines, improvements, color=colors)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Baseline Repository')
    ax.set_ylabel('Improvement (%)')
    ax.set_title('Our Algorithm Improvement over Baseline')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'improvement_summary.png', dpi=150)
    plt.close()

    print(f"Generated figures in {FIGURES_DIR}")

if __name__ == '__main__':
    main()
'''

Write(generate_figures_script, script_content)

# Execute
Bash: cd {baseline_folder}/experiments && conda run -n {conda_env} python generate_figures.py
```

### 9.8.6 Verify and Register Generated Figures

```python
# List generated figures
generated_figures = list_files(figures_folder, pattern="*.png")

# Update checkpoint
checkpoint.figures = {
    "generated": len(generated_figures) > 0,
    "folder": figures_folder,
    "files": generated_figures,
    "generation_method": "LLM-autonomous-mode-b",
    "generated_at": now()
}
SAVE checkpoint

print(f"✅ Generated {len(generated_figures)} comparison figures:")
FOR fig in generated_figures:
    print(f" - {fig}")
```

---

## 9.9 Generate Results Summary (Mode B)

> **READ `{result_guide}` Section 6 for summary template!**

Create `{baseline_folder}/results_summary.md` with:

```markdown
# Mode B Comparison Results Summary

## Fair Comparison Context

**Mode B:** We injected OUR algorithm into BASELINE's environment.
- Each baseline uses their OWN model, dataset, and config
- The ONLY difference is the algorithm/optimizer
- This is "baseline's home turf" - strong evidence if we win

## Results Per Baseline

### Baseline 1: {baseline_1_name}

| Component | Value |
|-----------|-------|
| Model | {baseline_1_model} |
| Dataset | {baseline_1_dataset} |
| Config | LR={lr}, Epochs={epochs} |

| Method | Primary Metric | Secondary Metric |
|--------|----------------|------------------|
| Baseline | {value} | {value} |
| Ours | {value} | {value} |
| **Improvement** | {+X.X%} | {+X.X%} |

### Baseline 2: {baseline_2_name}
...

### Baseline 3: {baseline_3_name}
...

## Overall Summary

| Baseline | Winner | Improvement |
|----------|--------|-------------|
| {baseline_1} | {ours/baseline} | {X.X%} |
| {baseline_2} | {ours/baseline} | {X.X%} |
| {baseline_3} | {ours/baseline} | {X.X%} |

**Win Rate:** {X}/{baselines_count} baselines

## Gate Evaluation Preview

```python
# Load gate config from checkpoint (Single Source of Truth: workflow.yaml)
threshold = checkpoint["workflow_config"]["gate"]["baseline_win_threshold"]
min_to_beat = checkpoint["workflow_config"]["gate"]["min_baselines_to_beat"]
```

| Metric | Threshold | Result |
|--------|-----------|--------|
| Win on ≥{min_to_beat} baselines | {threshold} | {PASS/FAIL} |
| Average improvement | >0% | {PASS/FAIL} |
```

---

## 9.10 Update Checkpoint

```yaml
current_step: 10
experiment:
  mode: "B"
  mode_description: "OUR algorithm vs BASELINE algorithm on BASELINE's environment"
  status: "completed"
  completed_at: "{timestamp}"
  total_runs: {checkpoint.total_runs} # SSoT: workflow.yaml
  successful_runs: {count}
  failed_runs: {count}
  baselines_completed:
    - repo_name: "{baseline_1}"
      baseline_model: "{model}"
      baseline_dataset: "{dataset}"
      baseline_result: {value}
      ours_result: {value}
      winner: "ours|baseline"
      improvement: "{X.X%}"
    - repo_name: "{baseline_2}"
      ...
    - repo_name: "{baseline_3}"
      ...
figures:
  generated: true
  folder: "{baseline_folder}/figures/"
results:
  comparison_data: "{comparison_data}"
  summary_file: "results_summary.md"
  win_count: {count}/{baselines_count}
```

---

## 9.11 Proceed to Next Step

| Condition | Action |
|-----------|--------|
| All runs completed | Load step-10-report.md |
| Partial completion (>70%) | Load step-10-report.md with warning |
| Major failure (<70%) | Log error, attempt recovery |

**MANDATORY:** Load and execute `step-10-report.md`

---

## Step Completion Criteria

- [ ] Runner scripts created for ALL 3 baselines
- [ ] Each script runs BOTH methods (baseline vs ours)
- [ ] All {total_runs} runs executed (or graceful degradation)
- [ ] comparison_data.csv created with baseline_repo/method columns
- [ ] Comparison figures generated (Mode B style)
- [ ] results_summary.md generated with win/lose analysis

---

## SUCCESS/FAILURE

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### ✅ SUCCESS:
- Runner scripts for all 3 baselines
- Each baseline runs BOTH methods (baseline vs ours)
- Scripts use BASELINE's config (lr, epochs, batch_size)
- Scripts launched with nohup, PID saved
- Results collected from ALL 6 result sets
- comparison_data.csv has baseline_repo AND method columns
- **Uses BASELINE's model, dataset, config** (Mode B)
- Comparison figures show baseline vs ours per baseline
- Win/lose analysis computed
- **Pre-experiment mock detection passed (Section 9.0)** ← 
- **Post-experiment mock verification passed (Section 9.6.5)** ← 

### ❌ FAILURE:
- Fabricating or generating synthetic results
- Running experiments for only 1 baseline
- **Using OUR model/dataset instead of baseline's** (Mode B violation!)
- **Replacing baseline's config with ours** (Mode B violation!)
- Not using nohup for long experiments
- Not saving PID to checkpoint
- comparison_data.csv missing baseline_repo/method columns
- Not attempting figure generation at all
- **Skipping pre-experiment mock detection (Section 9.0)** ← 
- **Skipping post-experiment mock verification (Section 9.6.5)** ← 
- **Proceeding after mock data detected without returning to step-07** ← 

---

**Next Step:** Load and execute `step-10-report.md`
