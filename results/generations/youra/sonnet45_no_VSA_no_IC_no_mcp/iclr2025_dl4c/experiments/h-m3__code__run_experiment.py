"""Main experiment runner for h-m3: Supervised AI Feedback Learning"""
import json
import os
from datetime import datetime
from config import get_config
from data_pipeline import load_and_prepare_data, set_seed
from model import SupervisedFeedbackModel
from evaluation import calculate_correlations, check_gate_criteria, compare_with_baseline
import numpy as np

def run_experiment():
    """Run complete h-m3 experiment"""

    # Load configuration
    config = get_config()
    set_seed(config.data.random_seed)

    print("=" * 60)
    print("h-m3: Supervised AI Feedback Learning Experiment")
    print("=" * 60)
    print()

    # Step 1: Data Pipeline
    print("Step 1: Loading and preparing data...")
    data = load_and_prepare_data(config.data)
    print(f"✓ Data loaded: {len(data['train'])} train, {len(data['val'])} val, {len(data['test'])} test")
    print()

    # Step 2: Model Setup
    print("Step 2: Initializing supervised feedback model...")
    model = SupervisedFeedbackModel(config.model, config.training)
    print()

    # Step 3: Training
    print("Step 3: Fine-tuning on human annotations...")
    trainer = model.train(data['train'], data['val'])
    print()

    # Step 4: Evaluation
    print("Step 4: Evaluating on test set...")
    predictions = model.predict(data['test'])

    # Extract ground truth human scores
    human_scores = np.array([ex['human_score'] for ex in data['test']])

    # Calculate metrics
    metrics = calculate_correlations(human_scores, predictions)

    print("Results:")
    print(f"  Spearman ρ: {metrics['spearman_rho']:.3f} (p={metrics['spearman_p']:.4f})")
    print(f"  Pearson r: {metrics['pearson_r']:.3f}")
    print(f"  MAE: {metrics['mae']:.3f}")
    print(f"  Test samples: {metrics['n_samples']}")
    print()

    # Step 5: Gate Check
    print("Step 5: Checking MUST_WORK gate criteria...")
    gate_satisfied, gate_explanation = check_gate_criteria(metrics, config)
    print(gate_explanation)
    print()

    if gate_satisfied:
        print("✓ GATE PASSED")
    else:
        print("✗ GATE FAILED")
    print()

    # Step 6: Baseline Comparison
    print("Step 6: Comparing with baseline (h-e1)...")
    comparison = compare_with_baseline(metrics, config.baseline_ai_human_corr)
    print(f"  Baseline (h-e1): ρ={comparison['baseline_correlation']:.3f}")
    print(f"  Supervised (h-m3): ρ={comparison['supervised_correlation']:.3f}")
    print(f"  Improvement: +{comparison['absolute_improvement']:.3f} ({comparison['relative_improvement_pct']:+.1f}%)")
    print()

    # Save results
    results = {
        'hypothesis_id': 'h-m3',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'model': config.model.model_name,
            'epochs': config.training.num_train_epochs,
            'learning_rate': config.training.learning_rate,
            'batch_size': config.training.per_device_train_batch_size
        },
        'data_stats': {
            'train_samples': len(data['train']),
            'val_samples': len(data['val']),
            'test_samples': len(data['test'])
        },
        'metrics': metrics,
        'gate': {
            'satisfied': gate_satisfied,
            'explanation': gate_explanation,
            'criteria': {
                'correlation_threshold': config.gate_correlation_threshold,
                'pvalue_threshold': config.gate_pvalue_threshold
            }
        },
        'comparison': comparison
    }

    # Create outputs directory
    os.makedirs('./outputs', exist_ok=True)

    # Save results
    results_path = './outputs/experiment_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {results_path}")
    print()

    # Save raw predictions for analysis
    results_csv_path = './outputs/results.csv'
    import csv
    with open(results_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_id', 'human_score', 'ai_prediction'])
        for i, (h, p) in enumerate(zip(human_scores, predictions)):
            writer.writerow([i, h, p])

    print(f"Raw results saved to: {results_csv_path}")
    print()

    print("=" * 60)
    print("Experiment complete!")
    print("=" * 60)

    return results

if __name__ == "__main__":
    results = run_experiment()
