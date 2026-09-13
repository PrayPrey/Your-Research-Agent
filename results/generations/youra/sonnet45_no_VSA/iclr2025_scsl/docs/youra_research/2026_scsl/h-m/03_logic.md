# Logic Design: h-m
# Dose-Response Validation with Statistical Inference

**Date:** 2026-07-11
**Hypothesis:** h-m (MECHANISM)
**Author:** Logic Agent (Phase 3)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from h-e1 actual code
**Analyzed Path**: docs/youra_research/h-e1/code/
**Relevant Symbols**: 
- `train_condition(condition: str)` - Single-seed training
- `get_dataloaders(condition: str, batch_size: int)` - Data pipeline
- `compute_per_class_accuracy(model, test_loader, device)` - Evaluation metrics
- `train_epoch()`, `test_epoch()` - Training utilities
- `MNISTNet` - Model architecture (100% reused)

**Critical Finding**: h-e1 uses single seed (n=1). h-m adds multi-seed orchestration (n=5) and statistical testing.

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual h-e1 Code)

The following APIs are called from h-e1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/model.py
class MNISTNet(nn.Module):
    """Standard CNN from PyTorch official MNIST example."""
    def __init__(self):
        # Uses MODEL_CONFIG from config.py
        ...
    
    def forward(self, x: Tensor) -> Tensor:
        """Forward pass. x: [B, 1, 28, 28] -> [B, 10] log_softmax"""
        ...

# From: docs/youra_research/h-e1/code/train.py
def train_epoch(model: nn.Module, train_loader: DataLoader, 
                optimizer: optim.Optimizer, device: torch.device) -> float:
    """Single training epoch. Returns average loss."""
    ...

def test_epoch(model: nn.Module, test_loader: DataLoader, 
               device: torch.device) -> float:
    """Single test epoch. Returns accuracy (%)."""
    ...

def train_condition(condition: str) -> dict:
    """
    Train model for single condition (h-e1 version - no seed param).
    
    Returns:
        {model, train_losses, test_accs}
    """
    ...

# From: docs/youra_research/h-e1/code/data.py
def get_dataloaders(condition: str, batch_size: int = None) -> Tuple[DataLoader, DataLoader]:
    """
    Get train/test dataloaders.
    
    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
        batch_size: Batch size (defaults to 64)
    
    Returns:
        (train_loader, test_loader)
    """
    ...

def get_transform(condition: str, train: bool = True) -> transforms.Compose:
    """Get transform pipeline for condition."""
    ...

# From: docs/youra_research/h-e1/code/evaluate.py
def compute_per_class_accuracy(model: nn.Module, test_loader: DataLoader, 
                                device: torch.device) -> dict:
    """
    Compute per-class accuracy.
    
    Returns:
        {per_class: [acc_0, ..., acc_9],
         symmetric_mean: float,
         asymmetric_mean: float,
         overall_acc: float}
    """
    ...
```

**Verified from**: docs/youra_research/h-e1/code/ (actual implementation)

**Key Difference**: h-e1's `train_condition()` does NOT take seed parameter. h-m will need wrapper function.

---

## M-1: Extend Configuration [Complexity: 6, Budget: 2]

**Applied**: Python dict configuration pattern

### API Signatures

```python
# config.py (extends h-e1/code/config.py)
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')
from config import MODEL_CONFIG, TRAINING_CONFIG, DATA_CONFIG, EXPERIMENT_CONFIG

# NEW: Multi-seed configuration
MULTI_SEED_CONFIG = {
    "seeds": [42, 123, 456, 789, 1011],  # 5 seeds for statistical testing
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],  # from h-e1
}

# NEW: Statistical testing configuration
STATS_CONFIG = {
    "correlation_method": "spearman",
    "alpha": 0.05,
    "flip_probabilities": [0.0, 0.3, 0.5, 0.9],  # for dose-response
}

# EXTENDED: Output paths for per-seed results
OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-m",
    "figures_dir": "docs/youra_research/h-m/figures",
    "results_file": "per_seed_results.csv",
    "stats_file": "dose_response_stats.json",
    "checkpoints_dir": "model_checkpoints",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Add multi-seed constants | Seeds list + conditions |
| L-1-2 | Add stats + output config | Spearman config + paths |

---

## M-2: Add Seed Control to Data [Complexity: 7, Budget: 2]

**Applied**: PyTorch random seed setting pattern

### API Signatures

```python
# data.py (extends h-e1 data.py)
import torch
import numpy as np
import random

def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def get_dataloaders_with_seed(condition: str, batch_size: int, seed: int) -> Tuple[DataLoader, DataLoader]:
    """
    Get dataloaders with seed control.
    
    Args:
        condition: Augmentation condition
        batch_size: Batch size
        seed: Random seed for reproducibility
    
    Returns:
        (train_loader, test_loader)
    """
    set_seed(seed)
    # Reuse h-e1's get_dataloaders
    from h_e1_code.data import get_dataloaders
    return get_dataloaders(condition, batch_size)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Implement set_seed | All RNG seed control |
| L-2-2 | Wrapper for get_dataloaders | Add seed parameter |

---

## M-3: Extend Training Module [Complexity: 8, Budget: 2]

**Applied**: PyTorch checkpoint saving pattern

### API Signatures

```python
# train.py (extends h-e1 train.py)
import torch
from pathlib import Path

def train_condition_with_seed(condition: str, seed: int, epochs: int = 14) -> dict:
    """
    Train model for (condition, seed) pair.
    
    Args:
        condition: Augmentation condition
        seed: Random seed
        epochs: Number of epochs (default 14)
    
    Returns:
        {model, train_losses, test_accs, checkpoint_path}
    """
    from data import set_seed
    from h_e1_code.train import train_epoch, test_epoch
    from h_e1_code.model import MNISTNet
    from h_e1_code.data import get_dataloaders
    from config import TRAINING_CONFIG, OUTPUT_CONFIG
    
    # Set seed
    set_seed(seed)
    
    # Get data
    train_loader, test_loader = get_dataloaders(condition, TRAINING_CONFIG["batch_size"])
    
    # Initialize model
    device = torch.device(TRAINING_CONFIG["device"])
    model = MNISTNet().to(device)
    
    # Optimizer & scheduler (reuse h-e1 config)
    optimizer = torch.optim.Adadelta(model.parameters(), lr=TRAINING_CONFIG["lr"])
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, 
        step_size=TRAINING_CONFIG["step_size"],
        gamma=TRAINING_CONFIG["gamma"]
    )
    
    # Training loop
    train_losses = []
    test_accs = []
    
    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, device)
        test_acc = test_epoch(model, test_loader, device)
        scheduler.step()
        
        train_losses.append(train_loss)
        test_accs.append(test_acc)
    
    # Save checkpoint
    checkpoint_path = save_checkpoint(model, condition, seed, OUTPUT_CONFIG["output_dir"])
    
    return {
        "model": model,
        "train_losses": train_losses,
        "test_accs": test_accs,
        "checkpoint_path": checkpoint_path
    }

def save_checkpoint(model: nn.Module, condition: str, seed: int, output_dir: str) -> str:
    """
    Save trained model checkpoint.
    
    Args:
        model: Trained model
        condition: Condition name
        seed: Seed value
        output_dir: Output directory
    
    Returns:
        Path to saved checkpoint
    """
    ckpt_dir = Path(output_dir) / "model_checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    
    ckpt_path = ckpt_dir / f"{condition}_seed{seed}.pth"
    torch.save(model.state_dict(), ckpt_path)
    
    return str(ckpt_path)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Implement train_condition_with_seed | Wrapper with seed control |
| L-3-2 | Implement save_checkpoint | Per (condition, seed) saving |

---

## M-4: Implement Statistical Testing [Complexity: 11, Budget: 3]

**Applied**: scipy.stats.spearmanr + pandas aggregation

### API Signatures

```python
# statistics.py (NEW module)
from scipy.stats import spearmanr
import numpy as np
import pandas as pd
from typing import Dict

def compute_spearman_correlation(results_df: pd.DataFrame) -> Dict:
    """
    Test dose-response relationship (flip conditions only).
    
    Args:
        results_df: DataFrame with columns [condition, seed, asymmetric_acc]
    
    Returns:
        {rho: float, p_value: float, significant: bool, interpretation: str}
    """
    # Filter to flip conditions only (exclude rotation)
    flip_conditions = results_df[results_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])]
    
    # Map conditions to flip probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_conditions['flip_prob'] = flip_conditions['condition'].map(prob_map)
    
    # Compute Spearman correlation (n=20: 4 conditions × 5 seeds)
    rho, p_value = spearmanr(flip_conditions['flip_prob'], flip_conditions['asymmetric_acc'])
    
    interpretation = ""
    if p_value < 0.05:
        if rho < -0.7:
            interpretation = "Strong negative monotonic relationship"
        elif rho < -0.4:
            interpretation = "Moderate negative monotonic relationship"
        else:
            interpretation = "Weak negative monotonic relationship"
    else:
        interpretation = "No significant monotonic relationship"
    
    return {
        'rho': float(rho),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'interpretation': interpretation
    }

def aggregate_seed_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate results across seeds.
    
    Args:
        results_df: DataFrame with columns [condition, seed, overall_acc, asymmetric_acc, symmetric_acc]
    
    Returns:
        DataFrame with columns [condition, mean_overall, std_overall, mean_asym, std_asym, mean_sym, std_sym, n]
    """
    aggregated = results_df.groupby('condition').agg({
        'overall_acc': ['mean', 'std', 'count'],
        'asymmetric_acc': ['mean', 'std'],
        'symmetric_acc': ['mean', 'std']
    }).reset_index()
    
    # Flatten column names
    aggregated.columns = [
        'condition', 
        'mean_overall', 'std_overall', 'n',
        'mean_asym', 'std_asym',
        'mean_sym', 'std_sym'
    ]
    
    return aggregated

def test_rotation_control(results_df: pd.DataFrame) -> Dict:
    """
    Validate rotation shows no differential effect.
    
    Args:
        results_df: DataFrame with results
    
    Returns:
        {mean_diff: float, within_threshold: bool, passed: bool}
    """
    baseline = results_df[results_df['condition'] == 'baseline']['asymmetric_acc'].mean()
    rotation = results_df[results_df['condition'] == 'rotation']['asymmetric_acc'].mean()
    
    mean_diff = abs(rotation - baseline)
    within_threshold = mean_diff < 1.0  # <1% difference
    
    return {
        'baseline_asym': float(baseline),
        'rotation_asym': float(rotation),
        'mean_diff': float(mean_diff),
        'within_threshold': within_threshold,
        'passed': within_threshold
    }
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Implement compute_spearman_correlation | Spearman test on flip conditions |
| L-4-2 | Implement aggregate_seed_results | Group by condition, compute mean/std |
| L-4-3 | Implement test_rotation_control | Validate rotation control |

---

## M-5: Extend Visualization [Complexity: 12, Budget: 3]

**Applied**: Matplotlib dose-response + error bars pattern

### API Signatures

```python
# visualize.py (extends h-e1 visualize.py)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict

def plot_dose_response_curve(aggregated_df: pd.DataFrame, stats: Dict, save_path: str):
    """
    Dose-response with error bars + Spearman annotation.
    
    Args:
        aggregated_df: Aggregated results (from aggregate_seed_results)
        stats: Spearman test results (from compute_spearman_correlation)
        save_path: Output file path
    """
    # Filter to flip conditions
    flip_data = aggregated_df[aggregated_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])]
    
    # Map to probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_data['flip_prob'] = flip_data['condition'].map(prob_map)
    flip_data = flip_data.sort_values('flip_prob')
    
    # Plot
    plt.figure(figsize=(8, 6))
    plt.errorbar(
        flip_data['flip_prob'], 
        flip_data['mean_asym'],
        yerr=flip_data['std_asym'],
        marker='o', 
        markersize=10,
        linewidth=2,
        capsize=5,
        label='Asymmetric digits (2,3,5,6,7,9)'
    )
    
    # Add rotation control as separate point
    rotation_data = aggregated_df[aggregated_df['condition'] == 'rotation']
    plt.scatter(
        [0.5], 
        rotation_data['mean_asym'].values,
        marker='x',
        s=200,
        c='red',
        label='Rotation control',
        zorder=5
    )
    
    # Annotations
    plt.xlabel('Horizontal Flip Probability', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title('Dose-Response: Flip Probability Effect on Asymmetric Digits', fontsize=14)
    
    # Spearman annotation
    plt.text(
        0.05, 0.95,
        f"Spearman ρ = {stats['rho']:.3f}\np = {stats['p_value']:.4f}",
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_seed_variability_boxplot(results_df: pd.DataFrame, save_path: str):
    """
    Box plots showing distribution across seeds.
    
    Args:
        results_df: Raw per-seed results
        save_path: Output file path
    """
    plt.figure(figsize=(10, 6))
    
    # Order conditions
    order = ['baseline', 'flip30', 'flip50', 'flip90', 'rotation']
    
    sns.boxplot(
        data=results_df,
        x='condition',
        y='asymmetric_acc',
        order=order,
        palette='Set2'
    )
    
    plt.xlabel('Condition', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title('Seed Variability Across Conditions (n=5 seeds)', fontsize=14)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_scatter_with_regression(results_df: pd.DataFrame, stats: Dict, save_path: str):
    """
    Scatter plot with all 20 data points.
    
    Args:
        results_df: Raw per-seed results
        stats: Spearman test results
        save_path: Output file path
    """
    # Filter to flip conditions
    flip_data = results_df[results_df['condition'].isin(['baseline', 'flip30', 'flip50', 'flip90'])].copy()
    
    # Map to probabilities
    prob_map = {'baseline': 0.0, 'flip30': 0.3, 'flip50': 0.5, 'flip90': 0.9}
    flip_data['flip_prob'] = flip_data['condition'].map(prob_map)
    
    # Plot scatter
    plt.figure(figsize=(8, 6))
    plt.scatter(
        flip_data['flip_prob'],
        flip_data['asymmetric_acc'],
        alpha=0.6,
        s=100,
        edgecolors='black'
    )
    
    # Add trend line
    z = np.polyfit(flip_data['flip_prob'], flip_data['asymmetric_acc'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(0, 0.9, 100)
    plt.plot(x_line, p(x_line), 'r--', linewidth=2, label='Linear fit')
    
    plt.xlabel('Horizontal Flip Probability', fontsize=12)
    plt.ylabel('Asymmetric Digit Accuracy (%)', fontsize=12)
    plt.title(f'Dose-Response Scatter (n=20 data points)\nSpearman ρ={stats["rho"]:.3f}, p={stats["p_value"]:.4f}', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Implement plot_dose_response_curve | Error bars + Spearman annotation |
| L-5-2 | Implement plot_seed_variability_boxplot | Box plot for seed variance |
| L-5-3 | Implement plot_scatter_with_regression | Scatter + linear fit (n=20) |

---

## M-6: Implement Multi-Seed Orchestrator [Complexity: 14, Budget: 4]

**Applied**: Nested loop orchestration + pandas CSV persistence

### API Signatures

```python
# run_multi_seed.py (NEW module)
import pandas as pd
from pathlib import Path
from itertools import product
import json
from typing import Dict

def run_all_seeds_and_conditions() -> pd.DataFrame:
    """
    Execute 5 conditions × 5 seeds = 25 training runs.
    
    Returns:
        DataFrame with columns: [condition, seed, overall_acc, asymmetric_acc, symmetric_acc, class_0-9]
    """
    from train import train_condition_with_seed
    from h_e1_code.evaluate import compute_per_class_accuracy
    from h_e1_code.data import get_dataloaders
    from config import MULTI_SEED_CONFIG, TRAINING_CONFIG, OUTPUT_CONFIG
    
    results = []
    device = torch.device(TRAINING_CONFIG["device"])
    
    for condition, seed in product(MULTI_SEED_CONFIG["conditions"], MULTI_SEED_CONFIG["seeds"]):
        print(f"\n{'='*60}")
        print(f"Training: {condition} | Seed: {seed}")
        print(f"{'='*60}")
        
        # Train
        train_result = train_condition_with_seed(condition, seed, epochs=TRAINING_CONFIG["epochs"])
        
        # Evaluate
        _, test_loader = get_dataloaders(condition, TRAINING_CONFIG["batch_size"])
        metrics = compute_per_class_accuracy(train_result['model'], test_loader, device)
        
        # Store result
        row = {
            'condition': condition,
            'seed': seed,
            'overall_acc': metrics['overall_acc'],
            'asymmetric_acc': metrics['asymmetric_mean'],
            'symmetric_acc': metrics['symmetric_mean']
        }
        # Add per-class accuracies
        for i, acc in enumerate(metrics['per_class']):
            row[f'class_{i}'] = acc
        
        results.append(row)
        print(f"Overall: {metrics['overall_acc']:.2f}% | Asym: {metrics['asymmetric_mean']:.2f}% | Sym: {metrics['symmetric_mean']:.2f}%")
    
    return pd.DataFrame(results)

def save_results_csv(results_df: pd.DataFrame, output_path: str):
    """Save results in CSV format."""
    results_df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")

def generate_statistical_report(results_df: pd.DataFrame) -> Dict:
    """
    Compute all statistical tests.
    
    Returns:
        {spearman_test, rotation_control, aggregated_stats}
    """
    from statistics import compute_spearman_correlation, aggregate_seed_results, test_rotation_control
    
    # Compute tests
    spearman_test = compute_spearman_correlation(results_df)
    aggregated_stats = aggregate_seed_results(results_df)
    rotation_control = test_rotation_control(results_df)
    
    return {
        'spearman_test': spearman_test,
        'aggregated_stats': aggregated_stats.to_dict('records'),
        'rotation_control': rotation_control
    }

def validate_gate_criteria(stats: Dict) -> Dict:
    """
    Check SHOULD_WORK gate criteria.
    
    Returns:
        {passed, checks, action, details}
    """
    spearman = stats['spearman_test']
    rotation = stats['rotation_control']
    
    checks = {
        'spearman_negative': spearman['rho'] < 0,
        'spearman_significant': spearman['p_value'] < 0.05,
        'rotation_control_passed': rotation['within_threshold']
    }
    
    primary_passed = checks['spearman_negative'] and checks['spearman_significant']
    
    return {
        'passed': primary_passed,
        'checks': checks,
        'action': 'PROCEED' if primary_passed else 'DOCUMENT_LIMITATION',
        'gate_type': 'SHOULD_WORK',
        'details': {
            'rho': spearman['rho'],
            'p_value': spearman['p_value'],
            'interpretation': spearman['interpretation']
        }
    }

def main():
    """
    Main execution flow:
    1. Run 25 training runs
    2. Aggregate results
    3. Compute statistical tests
    4. Generate visualizations
    5. Save outputs
    6. Validate SHOULD_WORK gate
    """
    from visualize import plot_dose_response_curve, plot_seed_variability_boxplot, plot_scatter_with_regression
    from statistics import aggregate_seed_results
    from config import OUTPUT_CONFIG
    
    print("Starting H-M Experiment: Dose-Response Validation")
    print(f"Total runs: 5 conditions × 5 seeds = 25 runs\n")
    
    # Step 1: Run all experiments
    results_df = run_all_seeds_and_conditions()
    
    # Step 2: Save CSV
    output_dir = Path(OUTPUT_CONFIG['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    save_results_csv(results_df, str(output_dir / OUTPUT_CONFIG['results_file']))
    
    # Step 3: Compute statistics
    stats_report = generate_statistical_report(results_df)
    
    # Step 4: Save statistical report
    with open(output_dir / OUTPUT_CONFIG['stats_file'], 'w') as f:
        json.dump(stats_report, f, indent=2)
    print(f"Statistics saved to: {output_dir / OUTPUT_CONFIG['stats_file']}")
    
    # Step 5: Generate visualizations
    figures_dir = output_dir / OUTPUT_CONFIG['figures_dir']
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    aggregated_df = aggregate_seed_results(results_df)
    
    plot_dose_response_curve(
        aggregated_df, 
        stats_report['spearman_test'], 
        str(figures_dir / 'dose_response_curve.png')
    )
    plot_seed_variability_boxplot(
        results_df, 
        str(figures_dir / 'seed_variability_boxplot.png')
    )
    plot_scatter_with_regression(
        results_df, 
        stats_report['spearman_test'], 
        str(figures_dir / 'scatter_regression.png')
    )
    print(f"Figures saved to: {figures_dir}")
    
    # Step 6: Validate gate
    gate_decision = validate_gate_criteria(stats_report)
    
    # Save gate decision
    with open(output_dir / 'gate_decision.json', 'w') as f:
        json.dump({
            'hypothesis': 'h-m',
            'gate_type': 'SHOULD_WORK',
            'primary_passed': gate_decision['passed'],
            'action': gate_decision['action'],
            'checks': gate_decision['checks'],
            'spearman_test': stats_report['spearman_test'],
            'rotation_control': stats_report['rotation_control']
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"GATE VALIDATION: {gate_decision['action']}")
    print(f"{'='*60}")
    print(f"Spearman ρ: {gate_decision['details']['rho']:.3f}")
    print(f"p-value: {gate_decision['details']['p_value']:.4f}")
    print(f"Interpretation: {gate_decision['details']['interpretation']}")
    print(f"Checks: {gate_decision['checks']}")
    
    return 0 if gate_decision['passed'] else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Implement run_all_seeds_and_conditions | 25-run loop with progress tracking |
| L-6-2 | Implement generate_statistical_report | Aggregate all statistical tests |
| L-6-3 | Implement validate_gate_criteria | SHOULD_WORK gate validation |
| L-6-4 | Implement main | End-to-end orchestration |

---

## M-7: Integration Testing [Complexity: 15, Budget: 3]

**Note**: This task is for execution validation (not API design). Logic provides test criteria only.

### Test Validation Criteria

```python
# test_integration.py (execution phase)
"""
Integration tests for h-m experiment.

Test Cases:
1. Config loading: All 5 seeds, 5 conditions loaded
2. Single seed run: train_condition_with_seed(baseline, 42) completes
3. CSV structure: 25 rows, expected columns
4. Spearman computation: rho, p_value returned
5. Gate validation: All checks evaluated
6. Figure generation: 3 PNG files created
"""

def test_config():
    """Verify configuration loaded correctly."""
    assert len(MULTI_SEED_CONFIG["seeds"]) == 5
    assert len(MULTI_SEED_CONFIG["conditions"]) == 5
    ...

def test_single_run():
    """Verify single (condition, seed) run."""
    result = train_condition_with_seed("baseline", 42, epochs=1)
    assert "model" in result
    assert len(result["test_accs"]) == 1
    ...

def test_statistical_pipeline():
    """Verify statistical testing pipeline."""
    # Mock 25 results
    mock_df = create_mock_results()
    stats = generate_statistical_report(mock_df)
    assert "spearman_test" in stats
    assert "rho" in stats["spearman_test"]
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Config validation | Verify all constants loaded |
| L-7-2 | Single-run smoke test | 1 epoch baseline run |
| L-7-3 | Statistical pipeline test | Mock data through stats functions |

---

## Summary

**Total Tasks**: 7
**Total Subtasks**: 23/10 used
**Budget Overrun**: 13 subtasks (130% over budget)

**Critical Implementation Notes**:
- h-e1's `train_condition()` does NOT take seed parameter → need wrapper `train_condition_with_seed()`
- Spearman test uses n=20 (4 flip conditions × 5 seeds), excludes rotation
- CSV columns: condition, seed, overall_acc, asymmetric_acc, symmetric_acc, class_0-9
- Gate passes if: ρ < 0 AND p < 0.05
- All visualizations use aggregated data (mean ± std across seeds)

**MECHANISM Hypothesis Extensions**:
- Multi-seed infrastructure (5 seeds vs h-e1's 1 seed)
- Statistical correlation testing (Spearman rank correlation)
- Dose-response visualization (error bars + significance annotation)
- Gate validation requires statistical significance (not just directional evidence)

**Code Reuse from h-e1**:
- Model architecture: 100% reused (MNISTNet)
- Data pipeline: 95% reused (add seed control wrapper)
- Training loop: 90% reused (train_epoch, test_epoch)
- Evaluation: 100% reused (compute_per_class_accuracy)
- NEW: statistics.py (0% from h-e1)
- NEW: run_multi_seed.py (0% from h-e1)

---

*Logic design extends h-e1 with multi-seed statistical validation*
*Estimated implementation time: 8-10 hours (building on h-e1 foundation)*
*Next Phase: Configuration Design (file paths, logging, hyperparameters)*
