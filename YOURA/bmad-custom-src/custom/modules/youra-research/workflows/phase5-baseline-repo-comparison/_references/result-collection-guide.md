# Result Collection Guide (Mode B)

> **Reference Guide for Phase 5 Step 9: Result Parsing and Aggregation**
> Contains templates for CSV parsing, aggregation, and summary statistics

---

## Overview

**Mode B Principle:** We inject OUR algorithm into BASELINE's environment.
Each baseline uses THEIR OWN model, dataset, and config.

This guide covers collecting results from:
- **{total_runs} result sets**: {baselines_count} Baselines × {methods_per_baseline} Methods (baseline_original vs ours_injected)
- **Total: {total_runs} runs** = {baselines_count} baselines × {methods_per_baseline} methods × {seeds} seed

---

## 1. Result Source Locations (Mode B)

### 1.1 Result Paths

| Baseline | Method | Location |
|----------|--------|----------|
| baseline_1 | baseline | `{baseline_folder}/experiments/{baseline_1}/run_baseline_{seed}.log` |
| baseline_1 | ours | `{baseline_folder}/experiments/{baseline_1}/run_ours_{seed}.log` |
| baseline_2 | baseline | `{baseline_folder}/experiments/{baseline_2}/run_baseline_{seed}.log` |
| baseline_2 | ours | `{baseline_folder}/experiments/{baseline_2}/run_ours_{seed}.log` |
| baseline_3 | baseline | `{baseline_folder}/experiments/{baseline_3}/run_baseline_{seed}.log` |
| baseline_3 | ours | `{baseline_folder}/experiments/{baseline_3}/run_ours_{seed}.log` |

### 1.2 Expected Result Counts

| Baseline | baseline_original | ours_injected | Total |
|----------|-------------------|---------------|-------|
| baseline_1 | 1 | 1 | 2 |
| baseline_2 | 1 | 1 | 2 |
| baseline_3 | 1 | 1 | 2 |
| **Total** | 3 | 3 | **6** |

---

## 2. Result Parsing Methods

### 2.1 Option 1: Find CSV Files (Serena MCP)

```python
# Using Serena to find CSV result files
mcp__serena__find_file(
    file_mask="*.csv",
    relative_path="{baseline_folder}/experiments/{baseline_repo}/"
)
```

### 2.2 Option 2: Parse from Logs (Serena MCP)

If results are logged to console rather than CSV:

```python
# Search for metric patterns in logs
mcp__serena__search_for_pattern(
    substring_pattern="{primary_metric}.*=|loss.*=|epoch.*completed",
    relative_path="{baseline_folder}/experiments/{baseline_repo}/",
    paths_include_glob="*.log",
    context_lines_after=1
)
```

### 2.3 Common Log Patterns

| Framework | Pattern Example |
|-----------|-----------------|
| PyTorch Lightning | `Epoch X: val_acc=0.95, val_loss=0.12` |
| Keras | `loss: 0.12 - accuracy: 0.95` |
| Custom | `[INFO] accuracy: 0.95 loss: 0.12` |
| JSON | `{"accuracy": 0.95, "loss": 0.12}` |

---

## 3. Result Parsing Script (Mode B)

### 3.1 Complete Parsing Logic

```python
#!/usr/bin/env python3
"""
collect_results.py - Parse and aggregate results from Mode B experiments

Mode B: {baselines_count} baselines × {methods_per_baseline} methods (baseline vs ours) = {total_runs} runs
Outputs: comparison_data.csv ({total_runs} rows)
"""

import pandas as pd
import re
from pathlib import Path
import json

# === Configuration ===
BASELINE_FOLDER = "{baseline_folder}"
BASELINES = [
    {
        "repo_name": "{baseline_1}",
        "model": "{baseline_1_model}",
        "dataset": "{baseline_1_dataset}",
        "lr": {baseline_1_lr},
    },
    {
        "repo_name": "{baseline_2}",
        "model": "{baseline_2_model}",
        "dataset": "{baseline_2_dataset}",
        "lr": {baseline_2_lr},
    },
    {
        "repo_name": "{baseline_3}",
        "model": "{baseline_3_model}",
        "dataset": "{baseline_3_dataset}",
        "lr": {baseline_3_lr},
    }
]
PRIMARY_METRIC = "{primary_metric}" # e.g., "accuracy", "psi"
SECONDARY_METRIC = "{secondary_metric}" # e.g., "loss"
SEED = {seed}

def main():
    all_results = []

    # === Collect results from each baseline ===
    for baseline in BASELINES:
        repo_name = baseline["repo_name"]
        print(f"Collecting: {repo_name}")

        exp_dir = Path(BASELINE_FOLDER) / "experiments" / repo_name

        for method in ["baseline", "ours"]:
            print(f" Method: {method}")
            result = parse_experiment_result(
                exp_dir,
                method,
                baseline
            )
            if result:
                all_results.append(result)
                print(f" Found: {result['primary_metric']}")
            else:
                print(f" WARNING: No result found")

    # === Create DataFrame ===
    df = pd.DataFrame(all_results)

    # Validate
    print(f"\n=== Total Results: {len(df)} / 6 ===")
    print(f"Baselines: {df['baseline_repo'].unique().tolist()}")
    print(f"Methods: {df['method'].unique().tolist()}")

    # === Save ===
    output_path = Path(BASELINE_FOLDER) / "experiments" / "comparison_data.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")

    return df

def parse_experiment_result(exp_dir: Path, method: str, baseline: dict) -> dict:
    """Parse experiment result for a specific method."""

    # Try different result file patterns
    patterns = [
        f"run_{method}_{SEED}.log",
        f"run_{method}.log",
        f"{method}_result.csv",
        f"{method}_result.json"
    ]

    for pattern in patterns:
        result_file = exp_dir / pattern
        if result_file.exists():
            return parse_result_file(result_file, method, baseline)

    return None

def parse_result_file(result_file: Path, method: str, baseline: dict) -> dict:
    """Parse a single result file."""
    suffix = result_file.suffix.lower()

    base_result = {
        'baseline_repo': baseline["repo_name"],
        'baseline_model': baseline["model"],
        'baseline_dataset': baseline["dataset"],
        'method': method,
        'lr': baseline["lr"],
        'seed': SEED,
    }

    if suffix == '.csv':
        df = pd.read_csv(result_file)
        row = df.iloc[-1] # Take last row (final result)
        base_result['primary_metric'] = row.get(PRIMARY_METRIC)
        base_result['secondary_metric'] = row.get(SECONDARY_METRIC)
        base_result['epochs_completed'] = row.get('epochs', row.get('epoch'))

    elif suffix == '.json':
        with open(result_file) as f:
            data = json.load(f)
        base_result['primary_metric'] = data.get(PRIMARY_METRIC)
        base_result['secondary_metric'] = data.get(SECONDARY_METRIC)
        base_result['epochs_completed'] = data.get('epochs')

    elif suffix == '.log':
        content = result_file.read_text()

        # Extract metrics from log
        primary_pattern = re.compile(rf'{PRIMARY_METRIC}[:\s=]+([0-9.]+)')
        secondary_pattern = re.compile(rf'{SECONDARY_METRIC}[:\s=]+([0-9.]+)')
        epoch_pattern = re.compile(r'epoch[s]?[:\s=]+(\d+)', re.IGNORECASE)

        primary_matches = primary_pattern.findall(content)
        secondary_matches = secondary_pattern.findall(content)
        epoch_matches = epoch_pattern.findall(content)

        base_result['primary_metric'] = float(primary_matches[-1]) if primary_matches else None
        base_result['secondary_metric'] = float(secondary_matches[-1]) if secondary_matches else None
        base_result['epochs_completed'] = int(epoch_matches[-1]) if epoch_matches else None

    return base_result

if __name__ == '__main__':
    main()
```

---

## 4. Comparison Data CSV Format (Mode B)

### 4.1 Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `baseline_repo` | string | Baseline repository name |
| `baseline_model` | string | Baseline's model architecture |
| `baseline_dataset` | string | Baseline's dataset name |
| `method` | string | "baseline" or "ours" |
| `lr` | float | Baseline's learning rate |
| `seed` | int | Random seed |
| `primary_metric` | float | Main evaluation metric |
| `secondary_metric` | float | Secondary metric (e.g., loss) |
| `epochs_completed` | int | Number of epochs |

### 4.2 Example CSV (Mode B)

```csv
baseline_repo,baseline_model,baseline_dataset,method,lr,seed,primary_metric,secondary_metric,epochs_completed
repo1,ResNet18,CIFAR10,baseline,0.1,42,0.72,0.35,200
repo1,ResNet18,CIFAR10,ours,0.1,42,0.85,0.22,200
repo2,VGG16,CIFAR100,baseline,0.01,42,0.65,0.42,200
repo2,VGG16,CIFAR100,ours,0.01,42,0.71,0.38,200
repo3,MobileNet,ImageNet,baseline,0.001,42,0.58,0.55,100
repo3,MobileNet,ImageNet,ours,0.001,42,0.63,0.48,100
```

Note: Each row pair (baseline + ours) uses the SAME baseline_model, baseline_dataset, and lr.
The ONLY difference is the method (algorithm being used).

---

## 5. Summary Statistics (Mode B)

### 5.1 Per-Baseline Comparison

```python
def compute_per_baseline_comparison(df: pd.DataFrame, metric: str) -> dict:
    """Compute comparison for each baseline (ours vs baseline_original)."""
    comparison = {}

    for baseline_repo in df['baseline_repo'].unique():
        baseline_df = df[df['baseline_repo'] == baseline_repo]

        baseline_result = baseline_df[baseline_df['method'] == 'baseline'][metric].values[0]
        ours_result = baseline_df[baseline_df['method'] == 'ours'][metric].values[0]

        ours_won = ours_result > baseline_result
        improvement = ((ours_result - baseline_result) / baseline_result) * 100

        comparison[baseline_repo] = {
            'baseline_result': baseline_result,
            'ours_result': ours_result,
            'ours_won': ours_won,
            'improvement': f"{improvement:+.1f}%",
            'baseline_model': baseline_df['baseline_model'].values[0],
            'baseline_dataset': baseline_df['baseline_dataset'].values[0]
        }

    return comparison
```

### 5.2 Win Count Calculation (Mode B)

```python
def compute_win_count(df: pd.DataFrame, metric: str) -> dict:
    """Compute how many baselines our algorithm beats."""
    comparison = compute_per_baseline_comparison(df, metric)

    wins = sum(1 for v in comparison.values() if v['ours_won'])
    total = len(comparison)

    return {
        'win_count': wins,
        'total_baselines': total,
        'threshold_met': wins >= min_baselines_to_beat, # from checkpoint gate config
        'per_baseline': comparison
    }
```

---

## 6. Results Summary Template (Mode B)

### 6.1 Markdown Template

```markdown
# Mode B Experiment Results Summary

## Date: {timestamp}
## Total Runs: {total_runs}
## Baselines: {baselines_count}
## Mode: B (Inject OUR algorithm into BASELINE's environment)

---

## Mode B Fair Comparison Context

> Each baseline uses THEIR OWN model, dataset, and config.
> The ONLY difference is the ALGORITHM being compared.
> This is "baseline's home turf" - strong evidence if we still win.

| Baseline | Model | Dataset | Config |
|----------|-------|---------|--------|
| {baseline_1} | {model_1} | {dataset_1} | LR={lr_1}, Epochs={epochs_1} |
| {baseline_2} | {model_2} | {dataset_2} | LR={lr_2}, Epochs={epochs_2} |
| {baseline_3} | {model_3} | {dataset_3} | LR={lr_3}, Epochs={epochs_3} |

---

## Results: Per-Baseline Comparison

| Baseline | Model | Dataset | Baseline Result | Ours Result | Winner | Improvement |
|----------|-------|---------|-----------------|-------------|--------|-------------|
| {baseline_1} | {model_1} | {dataset_1} | {result_1} | {ours_1} | {winner_1} | {improvement_1} |
| {baseline_2} | {model_2} | {dataset_2} | {result_2} | {ours_2} | {winner_2} | {improvement_2} |
| {baseline_3} | {model_3} | {dataset_3} | {result_3} | {ours_3} | {winner_3} | {improvement_3} |

---

## Gate Evaluation Preview

**Mode B Gate Criteria:** Beat ≥2/3 baselines (ours > baseline on their turf)

| Metric | Value |
|--------|-------|
| Baselines Won | {X}/{baselines_count} |
| Threshold | ≥{baseline_win_threshold} |
| **Gate Result** | {PASS/PARTIAL} |

---

## Interpretation

{If X >= min_baselines_to_beat}:
Our algorithm demonstrates superiority even when tested on baseline's own environments.
This provides strong evidence that our algorithm is genuinely better, not just tuned for our setup.

{If X < min_baselines_to_beat}:
Our algorithm did not consistently outperform baselines on their home turf.
This suggests the advantage may be environment-specific rather than algorithmic.
```

---

## 7. Execution

```bash
# Navigate to experiments directory
cd {baseline_folder}/experiments

# Run collection script
conda run -n {conda_env} python collect_results.py

# Verify output
wc -l comparison_data.csv # Should be 7 (6 data + 1 header)
```

---

## 8. Checkpoint Update (Mode B)

After result collection:

```yaml
experiment:
  mode: "B"
  status: "completed"
  completed_at: "{timestamp}"
  total_baselines: {checkpoint.baselines_count} # SSoT: workflow.yaml
  methods_per_baseline: {checkpoint.methods_per_baseline} # SSoT: workflow.yaml
  total_runs: {checkpoint.total_runs} # SSoT: workflow.yaml
  successful_runs: {count}
  failed_runs: {count}
  baselines_completed:
    - repo_name: "{baseline_1}"
      baseline_result: {value}
      ours_result: {value}
      winner: "ours|baseline"
      improvement: "{+X.X%}"
    - repo_name: "{baseline_2}"
      baseline_result: {value}
      ours_result: {value}
      winner: "ours|baseline"
      improvement: "{+X.X%}"
    - repo_name: "{baseline_3}"
      baseline_result: {value}
      ours_result: {value}
      winner: "ours|baseline"
      improvement: "{+X.X%}"

results:
  comparison_data: "{baseline_folder}/experiments/comparison_data.csv"
  summary_file: "results_summary.md"
```

---

## Related Files

| File | Purpose |
|------|---------|
| `step-09-experiment.md` | References this guide |
| `multi-baseline-experiment-guide.md` | Creates experiment outputs |
| `figure-generation-guide.md` | Uses comparison_data.csv |
| `05_baseline_report_template.md` | Final report template |
