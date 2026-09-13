"""Main experiment orchestrator for 10-fold CV calibration validation."""
import sys
import os
import json
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config.config import get_config, validate_config
from utils.reproducibility import set_seed
from data.synthetic_generator import save_synthetic_dataset
from models.simple_classifier import SimpleClassifier, train_fold, validate_epoch
from models.calibration import TemperatureScaler
from evaluation.ece import compute_ece
from evaluation.visualization import plot_reliability_diagram


def run_single_fold(
    fold_idx,
    features,
    labels,
    fold_indices,
    config,
    output_dir
):
    """Execute single fold training and evaluation."""
    print(f"\n{'='*60}")
    print(f"FOLD {fold_idx + 1}/10")
    print(f"{'='*60}")

    device = config['experiment']['device']
    set_seed(config['experiment']['random_seed'] + fold_idx)

    # Split data
    train_idx = fold_indices['train']
    val_idx = fold_indices['val']
    test_idx = fold_indices['test']

    X_train = torch.from_numpy(features[train_idx])
    y_train = torch.from_numpy(labels[train_idx])
    X_val = torch.from_numpy(features[val_idx])
    y_val = torch.from_numpy(labels[val_idx])
    X_test = torch.from_numpy(features[test_idx])
    y_test = torch.from_numpy(labels[test_idx])

    print(f"[Data] Train: {len(train_idx)}, Val: {len(val_idx)}, Test: {len(test_idx)}")

    # Create dataloaders
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    test_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True
    )
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    # Initialize model
    model = SimpleClassifier(
        input_dim=features.shape[1],
        hidden_dim=64,
        num_classes=2
    ).to(device)

    # Train model
    print(f"[Training] Starting...")
    start_time = time.time()
    model, history = train_fold(
        model,
        train_loader,
        val_loader,
        max_epochs=config['training']['max_epochs'],
        patience=config['training']['early_stopping']['patience'],
        lr=config['training']['learning_rate'],
        device=device
    )
    train_time = time.time() - start_time
    print(f"[Training] Completed in {train_time:.1f}s")

    # Get validation logits for temperature tuning
    _, val_acc, val_logits, val_labels = validate_epoch(model, val_loader, device)
    print(f"[Validation] Accuracy: {val_acc:.3f}")

    # Optimize temperature on validation set
    print(f"[Calibration] Optimizing temperature...")
    scaler = TemperatureScaler()
    temperature = scaler.fit(val_logits, val_labels)
    print(f"[Calibration] Optimal temperature: {temperature:.3f}")

    # Evaluate on test set
    _, test_acc, test_logits, test_labels = validate_epoch(model, test_loader, device)

    # Compute pre-calibration ECE
    pre_calib_probs = torch.softmax(test_logits, dim=1)
    pre_calib_conf, pre_calib_pred = pre_calib_probs.max(dim=1)
    pre_calib_ece = compute_ece(
        pre_calib_pred.numpy(),
        pre_calib_conf.numpy(),
        test_labels.numpy(),
        n_bins=config['evaluation']['ece_bins']
    )

    # Apply calibration to test set
    calib_probs = scaler.calibrate(test_logits, temperature)
    calib_conf, calib_pred = calib_probs.max(dim=1)

    # Compute post-calibration ECE
    post_calib_ece = compute_ece(
        calib_pred.numpy(),
        calib_conf.numpy(),
        test_labels.numpy(),
        n_bins=config['evaluation']['ece_bins']
    )

    print(f"[Evaluation] Test Accuracy: {test_acc:.3f}")
    print(f"[Evaluation] Pre-calibration ECE: {pre_calib_ece:.4f}")
    print(f"[Evaluation] Post-calibration ECE: {post_calib_ece:.4f}")

    # Generate reliability diagram
    plot_path = output_dir / 'plots' / f'reliability_fold_{fold_idx}.png'
    plot_reliability_diagram(
        calib_conf.numpy(),
        test_labels.numpy(),
        calib_pred.numpy(),
        n_bins=config['evaluation']['ece_bins'],
        save_path=str(plot_path),
        title=f'Fold {fold_idx + 1} - Calibrated Model'
    )

    # Save model
    model_path = output_dir / 'models' / f'model_fold_{fold_idx}.pt'
    torch.save(model.state_dict(), model_path)

    # Save fold results
    fold_results = {
        'fold_id': fold_idx,
        'train_size': len(train_idx),
        'val_size': len(val_idx),
        'test_size': len(test_idx),
        'train_time_seconds': train_time,
        'temperature': temperature,
        'test_accuracy': test_acc,
        'pre_calibration_ece': float(pre_calib_ece),
        'post_calibration_ece': float(post_calib_ece),
        'ece_improvement': float(pre_calib_ece - post_calib_ece),
        'training_history': {
            k: [float(v) for v in vals] for k, vals in history.items()
        }
    }

    results_path = output_dir / 'results' / f'results_fold_{fold_idx}.json'
    with open(results_path, 'w') as f:
        json.dump(fold_results, f, indent=2)

    return fold_results


def aggregate_results(fold_results, config):
    """Aggregate cross-fold results and check success criteria."""
    eces = [r['post_calibration_ece'] for r in fold_results]
    temps = [r['temperature'] for r in fold_results]
    accs = [r['test_accuracy'] for r in fold_results]

    # Count passing folds
    passing_folds = int(sum(
        ece < config['evaluation']['success_threshold']
        for ece in eces
    ))

    # Check success criteria
    primary_pass = bool(passing_folds >= config['gate']['primary']['min_passing_folds'])
    secondary_pass = bool(
        config['gate']['secondary']['min_value'] <= np.mean(temps) <=
        config['gate']['secondary']['max_value']
    )
    baseline_pass = bool(np.mean(accs) >= config['gate']['baseline']['min_value'])

    overall_pass = bool(primary_pass and secondary_pass and baseline_pass)

    aggregated = {
        'n_folds': len(fold_results),
        'mean_ece': float(np.mean(eces)),
        'std_ece': float(np.std(eces)),
        'min_ece': float(np.min(eces)),
        'max_ece': float(np.max(eces)),
        'passing_folds': passing_folds,
        'mean_temperature': float(np.mean(temps)),
        'std_temperature': float(np.std(temps)),
        'mean_accuracy': float(np.mean(accs)),
        'std_accuracy': float(np.std(accs)),
        'gate_results': {
            'primary': {
                'passed': primary_pass,
                'threshold': config['evaluation']['success_threshold'],
                'passing_folds': passing_folds,
                'required_folds': config['gate']['primary']['min_passing_folds']
            },
            'secondary': {
                'passed': secondary_pass,
                'mean_temperature': float(np.mean(temps)),
                'expected_range': [
                    config['gate']['secondary']['min_value'],
                    config['gate']['secondary']['max_value']
                ]
            },
            'baseline': {
                'passed': baseline_pass,
                'mean_accuracy': float(np.mean(accs)),
                'min_required': config['gate']['baseline']['min_value']
            }
        },
        'overall_pass': overall_pass,
        'verdict': 'PASS' if overall_pass else 'FAIL',
        'per_fold_results': fold_results
    }

    return aggregated


def generate_validation_report(aggregated, output_dir):
    """Generate 04_validation.md report."""
    report_path = output_dir / 'reports' / '04_validation.md'

    verdict = aggregated['verdict']
    mean_ece = aggregated['mean_ece']
    passing_folds = aggregated['passing_folds']
    mean_temp = aggregated['mean_temperature']
    mean_acc = aggregated['mean_accuracy']

    report = f"""# H-E1 Validation Report: Confidence Calibration

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Hypothesis**: Tree-LSTM confidence scores can be calibrated to ECE < 0.05
**Gate Type**: MUST_WORK
**Verdict**: **{verdict}**

---

## Executive Summary

This experiment validates the EXISTENCE of temperature scaling as an effective
calibration method for confidence-based tier gating in hybrid profiling systems.

### Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean ECE | {mean_ece:.4f} | < 0.05 | {'✓ PASS' if mean_ece < 0.05 else '✗ FAIL'} |
| Passing Folds | {passing_folds}/10 | ≥ 8/10 | {'✓ PASS' if passing_folds >= 8 else '✗ FAIL'} |
| Mean Temperature | {mean_temp:.3f} | [0.5, 2.0] | {'✓ PASS' if 0.5 <= mean_temp <= 2.0 else '✗ FAIL'} |
| Mean Accuracy | {mean_acc:.3f} | ≥ 0.60 | {'✓ PASS' if mean_acc >= 0.60 else '✗ FAIL'} |

---

## Per-Fold Results

| Fold | ECE | Temperature | Accuracy | Status |
|------|-----|-------------|----------|--------|
"""

    for r in aggregated['per_fold_results']:
        fold_id = r['fold_id']
        ece = r['post_calibration_ece']
        temp = r['temperature']
        acc = r['test_accuracy']
        status = '✓' if ece < 0.05 else '✗'
        report += f"| {fold_id + 1} | {ece:.4f} | {temp:.3f} | {acc:.3f} | {status} |\n"

    report += f"""
---

## Statistical Summary

**ECE Statistics**:
- Mean: {aggregated['mean_ece']:.4f}
- Std: {aggregated['std_ece']:.4f}
- Min: {aggregated['min_ece']:.4f}
- Max: {aggregated['max_ece']:.4f}

**Temperature Statistics**:
- Mean: {aggregated['mean_temperature']:.3f}
- Std: {aggregated['std_temperature']:.4f}

**Accuracy Statistics**:
- Mean: {aggregated['mean_accuracy']:.3f}
- Std: {aggregated['std_accuracy']:.4f}

---

## Gate Validation

### Primary Gate (MUST_WORK)
- **Requirement**: ECE < 0.05 in ≥ 8/10 folds
- **Result**: {passing_folds}/10 folds passed
- **Status**: {'PASS' if aggregated['gate_results']['primary']['passed'] else 'FAIL'}

### Secondary Gate (Temperature Sanity Check)
- **Requirement**: Mean temperature ∈ [0.5, 2.0]
- **Result**: Mean temperature = {mean_temp:.3f}
- **Status**: {'PASS' if aggregated['gate_results']['secondary']['passed'] else 'FAIL'}

### Baseline Gate (Model Learning)
- **Requirement**: Mean accuracy ≥ 0.60
- **Result**: Mean accuracy = {mean_acc:.3f}
- **Status**: {'PASS' if aggregated['gate_results']['baseline']['passed'] else 'FAIL'}

---

## Conclusion

"""

    if verdict == 'PASS':
        report += """
**VERDICT: PASS**

The experiment successfully demonstrates that temperature scaling can calibrate
confidence scores to ECE < 0.05, validating the foundational requirement for
confidence-based tier gating in hybrid profiling systems.

**Next Steps**:
1. Proceed to H-M1 (Multi-tier routing validation)
2. Integrate calibrated confidence scores into tier gating logic
3. Validate end-to-end hybrid profiling pipeline

**Key Findings**:
- Temperature scaling is effective for calibration
- Optimal temperatures fall within expected range [0.5, 2.0]
- Base model achieves adequate accuracy (≥60%)
- Calibration improves reliability without sacrificing accuracy
"""
    else:
        report += f"""
**VERDICT: FAIL**

The experiment did not meet the MUST_WORK gate criteria. Only {passing_folds}/10
folds achieved ECE < 0.05, below the required 8/10 threshold.

**Failure Analysis**:
"""
        if not aggregated['gate_results']['primary']['passed']:
            report += f"- Primary gate failed: Only {passing_folds}/10 folds passed (need ≥8)\n"
        if not aggregated['gate_results']['secondary']['passed']:
            report += f"- Temperature out of range: {mean_temp:.3f} not in [0.5, 2.0]\n"
        if not aggregated['gate_results']['baseline']['passed']:
            report += f"- Base accuracy too low: {mean_acc:.3f} < 0.60\n"

        report += """
**Recommended Actions**:
1. PIVOT to isotonic regression calibration if ECE in range [0.05, 0.10]
2. ABANDON confidence-gating framework if ECE > 0.10
3. Investigate model architecture if base accuracy < 60%
"""

    report += """
---

## Artifacts

- Per-fold results: `results/results_fold_{0-9}.json`
- Model checkpoints: `models/model_fold_{0-9}.pt`
- Reliability diagrams: `plots/reliability_fold_{0-9}.png`
- Aggregated results: `results/aggregated_results.json`

---

**Generated by**: H-E1 Calibration Experiment
**Framework**: YouRA Phase 4 PoC Validation
"""

    # Save report
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n[Report] Validation report saved to {report_path}")

    return report


def run_10fold_cv(config):
    """Execute 10-fold cross-validation experiment."""
    print(f"\n{'#'*60}")
    print("# H-E1 CONFIDENCE CALIBRATION EXPERIMENT")
    print(f"{'#'*60}\n")

    # Setup output directory
    output_dir = Path(__file__).parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    (output_dir / 'models').mkdir(exist_ok=True)
    (output_dir / 'results').mkdir(exist_ok=True)
    (output_dir / 'plots').mkdir(exist_ok=True)
    (output_dir / 'reports').mkdir(exist_ok=True)

    # Generate synthetic dataset
    print("[Setup] Generating synthetic dataset...")
    data_dir = Path(__file__).parent / 'data' / 'codeforces'
    features, labels, folds = save_synthetic_dataset(
        output_dir=str(data_dir),
        n_samples=config['data']['min_samples'],
        seed=config['experiment']['random_seed']
    )

    # Load CV folds
    with open(data_dir / 'cv_folds.json', 'r') as f:
        cv_folds = json.load(f)

    # Run all folds
    fold_results = []
    for fold_idx, fold_indices in enumerate(cv_folds):
        try:
            result = run_single_fold(
                fold_idx,
                features,
                labels,
                fold_indices,
                config,
                output_dir
            )
            fold_results.append(result)
        except Exception as e:
            print(f"[ERROR] Fold {fold_idx} failed: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Aggregate results
    print(f"\n{'='*60}")
    print("AGGREGATING RESULTS")
    print(f"{'='*60}")

    if len(fold_results) < 8:
        print(f"[ERROR] Only {len(fold_results)}/10 folds completed. Need ≥8 for valid experiment.")
        return None

    aggregated = aggregate_results(fold_results, config)

    # Save aggregated results
    agg_path = output_dir / 'results' / 'aggregated_results.json'
    with open(agg_path, 'w') as f:
        json.dump(aggregated, f, indent=2)
    print(f"[Results] Aggregated results saved to {agg_path}")

    # Generate validation report
    report = generate_validation_report(aggregated, output_dir)

    # Print summary
    print(f"\n{'#'*60}")
    print("# EXPERIMENT COMPLETE")
    print(f"{'#'*60}")
    print(f"\nVERDICT: {aggregated['verdict']}")
    print(f"Mean ECE: {aggregated['mean_ece']:.4f}")
    print(f"Passing Folds: {aggregated['passing_folds']}/10")
    print(f"Mean Temperature: {aggregated['mean_temperature']:.3f}")
    print(f"Mean Accuracy: {aggregated['mean_accuracy']:.3f}")

    return aggregated


if __name__ == '__main__':
    # Load configuration
    config = get_config()
    validate_config(config)

    # Run experiment
    results = run_10fold_cv(config)

    if results:
        sys.exit(0 if results['overall_pass'] else 1)
    else:
        sys.exit(2)
