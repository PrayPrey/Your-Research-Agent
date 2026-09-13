"""Main experiment runner for h-m1."""
import sys
import os
import json
import numpy as np
from sklearn.model_selection import train_test_split

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import CONFIG
from src.data_loader import DataLoader
from src.classifier import ThresholdClassifier
from src.evaluator import Evaluator
from src.visualizer import plot_threshold_curve, plot_confusion_matrix, plot_entropy_distribution


class ThresholdExperiment:
    """Main experiment runner."""

    def __init__(self, config: dict):
        self.config = config
        self.loader = DataLoader()
        self.classifier = ThresholdClassifier()
        self.evaluator = Evaluator()

    def load_data(self):
        """Load h-e1 results. Returns (X, y) of shape (73,)."""
        results = self.loader.load_h_e1_results(self.config['data']['h_e1_results_path'])
        X, y = self.loader.extract_arrays(results)
        return X, y, results

    def train_test_split_data(self, X: np.ndarray, y: np.ndarray):
        """80/20 stratified split. Returns: X_train (60,), X_test (13,), y_train, y_test"""
        return train_test_split(
            X, y,
            test_size=self.config['split']['test_size'],
            stratify=y if self.config['split']['stratify'] else None,
            random_state=self.config['split']['random_state']
        )

    def run(self):
        """Execute full pipeline."""
        np.random.seed(self.config['seed'])

        # Load data
        print("Loading h-e1 results...")
        X, y, raw_results = self.load_data()
        print(f"Loaded {len(X)} samples")

        # Split
        print("Splitting train/test...")
        X_train, X_test, y_train, y_test = self.train_test_split_data(X, y)
        print(f"Train: {len(X_train)}, Test: {len(X_test)}")

        # Grid search
        print("Grid searching thresholds...")
        thresholds = np.linspace(
            self.config['classifier']['threshold_min'],
            self.config['classifier']['threshold_max'],
            self.config['classifier']['threshold_steps']
        )
        best_threshold, threshold_list, accuracy_list = self.classifier.fit(
            X_train, y_train, thresholds
        )
        print(f"Best threshold: {best_threshold:.3f}, Train accuracy: {self.classifier.train_accuracy:.3f}")

        # Test evaluation
        print("Evaluating on test set...")
        y_pred_test = self.classifier.predict(X_test)
        test_metrics = self.evaluator.evaluate(y_test, y_pred_test)
        print(f"Test accuracy: {test_metrics['accuracy']:.3f}")

        # Gate check
        gate_pass = self.evaluator.check_gate(
            test_metrics['accuracy'],
            self.config['gate']['threshold']
        )
        print(f"Gate (≥{self.config['gate']['threshold']}): {'PASS' if gate_pass else 'FAIL'}")

        # Baseline comparison
        np.random.seed(self.config['baseline']['random_state'])
        baseline_preds = np.random.choice([0, 1], size=len(y_test))
        baseline_acc = (baseline_preds == y_test).mean()
        print(f"Baseline (random) accuracy: {baseline_acc:.3f}")

        # Visualizations
        print("Generating visualizations...")
        os.makedirs(self.config['visualization']['figures_dir'], exist_ok=True)

        plot_threshold_curve(
            threshold_list, accuracy_list, best_threshold,
            os.path.join(self.config['visualization']['figures_dir'], 'threshold_curve.png')
        )

        plot_confusion_matrix(
            np.array(test_metrics['confusion_matrix']),
            os.path.join(self.config['visualization']['figures_dir'], 'confusion_matrix.png')
        )

        entity_entropies = raw_results['entity_entropies']
        non_entity_entropies = raw_results['non_entity_entropies']
        plot_entropy_distribution(
            entity_entropies, non_entity_entropies, best_threshold,
            os.path.join(self.config['visualization']['figures_dir'], 'entropy_distribution.png')
        )

        # Save results
        print("Saving results...")
        os.makedirs(os.path.dirname(self.config['output']['results_file']), exist_ok=True)
        results_out = {
            "best_threshold": float(best_threshold),
            "train_accuracy": float(self.classifier.train_accuracy),
            "test_accuracy": float(test_metrics['accuracy']),
            "test_metrics": test_metrics,
            "baseline_accuracy": float(baseline_acc),
            "gate_pass": gate_pass,
            "n_train": len(X_train),
            "n_test": len(X_test)
        }

        with open(self.config['output']['results_file'], 'w') as f:
            json.dump(results_out, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Experiment Complete")
        print(f"{'='*60}")
        print(f"Test Accuracy: {test_metrics['accuracy']:.3f}")
        print(f"Baseline Accuracy: {baseline_acc:.3f}")
        print(f"Gate Status: {'PASS' if gate_pass else 'FAIL'}")
        print(f"Results saved to: {self.config['output']['results_file']}")
        print(f"Figures saved to: {self.config['visualization']['figures_dir']}")

        return results_out


if __name__ == '__main__':
    experiment = ThresholdExperiment(CONFIG)
    results = experiment.run()
