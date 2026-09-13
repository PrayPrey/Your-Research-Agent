"""Main Experiment Runner for H-E1: Repository Maintenance Classification."""

import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_collector import GitHubDataCollector
from feature_engineer import FeatureEngineer
from trainer import MaintenanceClassifier
from evaluator import GateEvaluator
from visualizer import ResultVisualizer
from config import ExperimentConfig


def main():
    """Execute end-to-end experiment pipeline."""
    print("=" * 70)
    print("H-E1: Repository Maintenance Classification Experiment")
    print("=" * 70)

    try:
        # Initialize configuration
        config = ExperimentConfig()
        print(f"\nConfiguration loaded:")
        print(f"  Dataset size: {config.dataset_size}")
        print(f"  Year range: {config.year_range}")
        print(f"  Test split: {config.model_config.test_size}")
        print(f"  Random seed: {config.model_config.random_state}")

        # Create output directories
        Path('data').mkdir(exist_ok=True)
        Path('models').mkdir(exist_ok=True)
        Path('outputs').mkdir(exist_ok=True)
        Path(config.figures_output_path).mkdir(exist_ok=True)

        # ===================================================================
        # STEP 1: Data Collection
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 1: Data Collection")
        print("-" * 70)

        # Check for GitHub token
        github_token = config.github_api_token
        if not github_token:
            github_token = os.environ.get('GITHUB_TOKEN', '')

        if not github_token:
            print("WARNING: No GitHub API token found. Using unauthenticated requests (limited rate).")
            print("Set GITHUB_TOKEN environment variable for higher rate limits.")

        collector = GitHubDataCollector(github_token)

        # Check if data already exists
        if os.path.exists(config.data_output_path):
            print(f"Loading existing data from {config.data_output_path}")
            import pandas as pd
            raw_data = pd.read_csv(config.data_output_path)
        else:
            # Collect repositories from Papers with Code
            pwc_repos = collector.collect_pwc_repos(
                year_range=config.year_range,
                min_stars=config.min_stars,
                max_repos=config.dataset_size
            )

            print(f"\nCollecting metadata for {len(pwc_repos)} repositories...")
            metadata_list = []

            for idx, row in pwc_repos.iterrows():
                if idx % 50 == 0:
                    print(f"  Progress: {idx}/{len(pwc_repos)}")

                repo_name = row['repo_name']
                metadata = collector.fetch_repo_metadata(repo_name)

                if metadata:
                    metadata['repo_id'] = repo_name
                    # Compute temporal features
                    temporal = collector.compute_temporal_features(repo_name)
                    metadata.update(temporal)
                    metadata_list.append(metadata)

            import pandas as pd
            raw_data = pd.DataFrame(metadata_list)

            # Save raw data
            collector.save_raw_data(raw_data, config.data_output_path)

        print(f"\nDataset summary:")
        print(f"  Total repositories: {len(raw_data)}")
        print(f"  Features: {raw_data.columns.tolist()}")

        # ===================================================================
        # STEP 2: Feature Engineering
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 2: Feature Engineering")
        print("-" * 70)

        engineer = FeatureEngineer()

        # Transform features
        X = engineer.transform_features(raw_data)
        print(f"\nTransformed features: {X.columns.tolist()}")

        # Create labels
        y = engineer.create_labels(raw_data, threshold_days=config.label_threshold_days)
        print(f"Labels created (threshold={config.label_threshold_days} days)")
        print(f"  Maintained (1): {(y == 1).sum()} ({(y == 1).sum() / len(y) * 100:.1f}%)")
        print(f"  Abandoned (0):  {(y == 0).sum()} ({(y == 0).sum() / len(y) * 100:.1f}%)")

        # Validate distributions
        validation = engineer.validate_distributions(X)
        print(f"\nDistribution validation (Shapiro-Wilk):")
        for feature, result in validation.items():
            status = "✓ Normal" if result['is_normal'] else "✗ Not normal"
            print(f"  {feature}: {status} (p={result['shapiro_p_value']:.4f})")

        # ===================================================================
        # STEP 3: Model Training
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 3: Model Training")
        print("-" * 70)

        classifier = MaintenanceClassifier(random_state=config.model_config.random_state)

        # Prepare train/test split
        X_train, X_test, y_train, y_test = classifier.prepare_data(
            X, y, test_size=config.model_config.test_size
        )
        print(f"\nData split:")
        print(f"  Train: {len(X_train)} samples")
        print(f"  Test:  {len(X_test)} samples")

        # Train model
        training_info = classifier.train(X_train, y_train)
        print(f"\nTraining completed:")
        print(f"  Converged: {training_info['converged']}")
        print(f"  Iterations: {training_info['n_iter']}")
        print(f"  Classes: {training_info['classes']}")

        # Feature importance
        importance = classifier.get_feature_importance()
        print(f"\nTop 5 Important Features:")
        for _, row in importance.head().iterrows():
            print(f"  {row['feature']:30s}: {row['coefficient']:+.4f}")

        # ===================================================================
        # STEP 4: Evaluation
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 4: Evaluation")
        print("-" * 70)

        evaluator = GateEvaluator(
            accuracy_threshold=config.eval_config.accuracy_threshold,
            f1_threshold=config.eval_config.f1_threshold
        )

        # Predict on test set
        y_pred = classifier.predict(X_test)
        y_proba = classifier.predict_proba(X_test)

        # Compute metrics
        metrics = evaluator.compute_metrics(y_test, y_pred, y_proba)

        # Check gate
        gate_passed, gate_explanation = evaluator.check_gate_status(metrics)

        # Print summary
        evaluator.print_summary(metrics, gate_passed, gate_explanation)

        # Classification report
        report = evaluator.generate_classification_report(y_test, y_pred)
        print(f"\nClassification Report:")
        print(report)

        # Save metrics
        metrics['gate_passed'] = gate_passed
        metrics['gate_explanation'] = gate_explanation
        metrics['training_info'] = training_info
        metrics['dataset_info'] = {
            'total_samples': len(raw_data),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features': X.columns.tolist()
        }

        evaluator.save_metrics(metrics, config.eval_config.report_path)

        # ===================================================================
        # STEP 5: Visualization
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 5: Visualization")
        print("-" * 70)

        visualizer = ResultVisualizer(
            output_dir=config.figures_output_path,
            dpi=config.figure_dpi,
            format=config.figure_format
        )

        targets = {
            'accuracy': config.eval_config.accuracy_threshold,
            'f1': config.eval_config.f1_threshold
        }

        visualizer.generate_all_figures(
            metrics=metrics,
            targets=targets,
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            y_train=y_train,
            y_test=y_test,
            coefficients=classifier.model.coef_[0],
            feature_names=X.columns.tolist()
        )

        # ===================================================================
        # STEP 6: Output Gate Decision
        # ===================================================================
        print("\n" + "=" * 70)
        print("EXPERIMENT COMPLETE")
        print("=" * 70)

        result = {
            'hypothesis_id': 'h-e1',
            'gate_type': 'MUST_WORK',
            'gate_passed': bool(gate_passed),
            'gate_explanation': gate_explanation,
            'metrics': {
                'accuracy': float(metrics['accuracy']),
                'precision': float(metrics['precision']),
                'recall': float(metrics['recall']),
                'f1': float(metrics['f1']),
                'roc_auc': float(metrics.get('roc_auc')) if metrics.get('roc_auc') else None
            },
            'thresholds': {
                'accuracy': float(config.eval_config.accuracy_threshold),
                'f1': float(config.eval_config.f1_threshold)
            },
            'completed_at': datetime.now().isoformat()
        }

        # Save experiment results
        results_path = 'outputs/experiment_results.json'
        with open(results_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\nResults saved to: {results_path}")
        print(f"Gate status: {'PASS' if gate_passed else 'FAIL'}")

        # Create results CSV for Phase 5
        results_df = raw_data.copy()
        results_df['predictions'] = 0  # Placeholder
        results_df.iloc[:len(y_pred), results_df.columns.get_loc('predictions')] = y_pred
        results_df.to_csv('outputs/results.csv', index=False)
        print(f"Results CSV saved to: outputs/results.csv")

        return 0 if gate_passed else 1

    except Exception as e:
        print(f"\n❌ ERROR: Experiment failed")
        print(f"Error: {str(e)}")
        print(f"\nTraceback:")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
