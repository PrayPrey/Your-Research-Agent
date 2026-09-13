#!/usr/bin/env python3
"""
Main Experiment Runner for H-E1
Orchestrates full pipeline from data collection to final report
"""

import os
import sys
import json
import gc
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import CONFIG
from model_zoo import ModelZooCollector
from feature_extractor import FeatureExtractor
from classifier import BinaryClassifier
from statistical_test import StatisticalTester
from visualizer import Visualizer


class ExperimentRunner:
    """Orchestrate full experiment pipeline"""

    def __init__(self, config=None):
        self.config = config or CONFIG
        self.hypothesis_id = self.config["hypothesis_id"]

        # Setup directories
        self.base_dir = Path(__file__).parent
        self.setup_directories()

    def setup_directories(self):
        """Create all required directories"""
        for dir_name in self.config["directories"].values():
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Directory created: {dir_path}")

    def run_full_pipeline(self) -> dict:
        """
        Execute full pipeline.
        Returns: {"gate_status": str, "metrics": dict, "filepaths": dict}
        """
        print("\n" + "="*80)
        print(f"Starting Experiment: {self.hypothesis_id}")
        print("="*80 + "\n")

        # Step 1: Model Zoo Collection
        print("📥 Step 1: Model Zoo Collection")
        metadata = self.collect_model_zoo()

        # Step 2: Feature Extraction
        print("\n📊 Step 2: Feature Extraction")
        X_full, X_baseline, y = self.extract_features(metadata)

        # Step 3: Train/Test Split
        print("\n✂️ Step 3: Train/Test Split")
        split_data = self.train_test_split(X_full, X_baseline, y)

        # Step 4: Train Classifiers & Ablation
        print("\n🤖 Step 4: Binary Classification Training")
        results = self.run_ablation_comparison(split_data)

        # Step 5: Statistical Testing
        print("\n🔬 Step 5: Statistical Significance Testing")
        stats_results = self.run_statistical_test(
            split_data["y_test"],
            results["full"]["predictions"],
            results["full"]["accuracy"]
        )

        # Step 6: Visualization
        print("\n📊 Step 6: Generating Visualizations")
        figures = self.generate_visualizations(split_data, results, stats_results)

        # Step 7: Save Results
        print("\n💾 Step 7: Saving Results")
        self.save_all_results(metadata, split_data, results, stats_results, figures)

        # Step 8: Determine Gate Status
        print("\n🚦 Step 8: Gate Decision")
        gate_status = self.determine_gate_status(results, stats_results)

        print("\n" + "="*80)
        print(f"Experiment Complete: {gate_status}")
        print("="*80 + "\n")

        return {
            "gate_status": gate_status,
            "metrics": results,
            "filepaths": figures
        }

    def collect_model_zoo(self) -> list:
        """Step 1: Download model zoo (metadata only, weights loaded on-demand)"""
        collector = ModelZooCollector(
            output_dir=str(self.base_dir / "data"),
            random_seed=self.config["random_seed"]
        )

        result = collector.collect_models(
            n_resnet=self.config["model_zoo"]["n_resnet"],
            n_vit=self.config["model_zoo"]["n_vit"]
        )

        metadata = result["models"]

        # Save metadata
        metadata_path = self.base_dir / "data" / "models_metadata.json"
        collector.save_metadata(metadata, str(metadata_path))

        print(f"✓ Collected {len(metadata)} models metadata")
        print("  (Weights will be downloaded on-demand during feature extraction)")
        return metadata

    def extract_features(self, metadata: list):
        """Step 2: Extract weight statistics (memory-efficient one-at-a-time)"""
        from model_zoo import ModelZooCollector
        import gc

        extractor = FeatureExtractor(
            include_spectral=self.config["features"]["include_spectral"]
        )

        collector = ModelZooCollector(
            output_dir=str(self.base_dir / "data"),
            random_seed=self.config["random_seed"]
        )

        X_full_list = []
        X_baseline_list = []
        y_list = []

        print(f"  Processing {len(metadata)} models one at a time to avoid OOM...")

        for i, model_info in enumerate(metadata):
            print(f"  [{i+1}/{len(metadata)}] Loading {model_info['model_id']}...")

            # Download model weights
            try:
                model_data = collector.download_model(model_info["model_id"])
                state_dict = model_data["state_dict"]

                # Extract features
                features_full = extractor.extract_from_state_dict(state_dict)
                features_baseline = extractor.extract_norms_only(state_dict)

                X_full_list.append(features_full)
                X_baseline_list.append(features_baseline)

                # Label: 0 for ResNet, 1 for ViT
                architecture = model_info["architecture"]
                y_list.append(0 if "resnet" in architecture.lower() else 1)

                # Free memory
                del model_data
                del state_dict
                gc.collect()
                torch.cuda.empty_cache() if torch.cuda.is_available() else None

            except Exception as e:
                print(f"    WARNING: Failed to process {model_info['model_id']}: {e}")
                continue

        # Pad features to same length (different architectures have different layer counts)
        max_len_full = max(len(f) for f in X_full_list)
        max_len_baseline = max(len(f) for f in X_baseline_list)

        X_full_padded = []
        X_baseline_padded = []

        for feat_full, feat_baseline in zip(X_full_list, X_baseline_list):
            if len(feat_full) < max_len_full:
                feat_full = np.pad(feat_full, (0, max_len_full - len(feat_full)))
            if len(feat_baseline) < max_len_baseline:
                feat_baseline = np.pad(feat_baseline, (0, max_len_baseline - len(feat_baseline)))

            X_full_padded.append(feat_full)
            X_baseline_padded.append(feat_baseline)

        X_full = np.array(X_full_padded)
        X_baseline = np.array(X_baseline_padded)
        y = np.array(y_list)

        # Save features
        features_path = self.base_dir / "data" / "weight_features.npz"
        np.savez(
            features_path,
            X_full=X_full,
            X_baseline=X_baseline,
            y=y,
            model_ids=[m["model_id"] for m in metadata if m["model_id"] in [metadata[j]["model_id"] for j in range(len(y))]]
        )

        print(f"✓ Features extracted: X_full={X_full.shape}, X_baseline={X_baseline.shape}, y={y.shape}")
        return X_full, X_baseline, y

    def train_test_split(self, X_full, X_baseline, y):
        """Step 3: Stratified train/test split"""
        X_train_full, X_test_full, y_train, y_test = train_test_split(
            X_full, y,
            test_size=self.config["train_test_split"]["test_size"],
            stratify=y,
            random_state=self.config["train_test_split"]["random_state"]
        )

        X_train_baseline, X_test_baseline, _, _ = train_test_split(
            X_baseline, y,
            test_size=self.config["train_test_split"]["test_size"],
            stratify=y,
            random_state=self.config["train_test_split"]["random_state"]
        )

        print(f"✓ Split: Train={len(y_train)}, Test={len(y_test)}")

        return {
            "X_train_full": X_train_full,
            "X_test_full": X_test_full,
            "X_train_baseline": X_train_baseline,
            "X_test_baseline": X_test_baseline,
            "y_train": y_train,
            "y_test": y_test
        }

    def run_ablation_comparison(self, split_data):
        """Step 4: Train both classifiers and compare"""
        # Train baseline (norms-only)
        print("\n  Training norms-only baseline...")
        clf_baseline = BinaryClassifier(
            C=self.config["classifier"]["C"],
            max_iter=self.config["classifier"]["max_iter"],
            random_state=self.config["classifier"]["random_state"]
        )
        clf_baseline.fit(split_data["X_train_baseline"], split_data["y_train"])
        baseline_results = clf_baseline.evaluate(split_data["X_test_baseline"], split_data["y_test"])

        # Save baseline model
        clf_baseline.save_model(str(self.base_dir / "models" / "classifier_norms_only.pkl"))

        # Train full (norms + spectral)
        print("\n  Training norms+spectral classifier...")
        clf_full = BinaryClassifier(
            C=self.config["classifier"]["C"],
            max_iter=self.config["classifier"]["max_iter"],
            random_state=self.config["classifier"]["random_state"]
        )
        clf_full.fit(split_data["X_train_full"], split_data["y_train"])
        full_results = clf_full.evaluate(split_data["X_test_full"], split_data["y_test"])

        # Save full model
        clf_full.save_model(str(self.base_dir / "models" / "classifier_full.pkl"))

        # Compute ablation delta
        ablation_delta = full_results["accuracy"] - baseline_results["accuracy"]

        print(f"\n  Ablation improvement: {ablation_delta:.3f} ({ablation_delta*100:.1f}%)")

        return {
            "baseline": baseline_results,
            "full": full_results,
            "ablation_delta": ablation_delta,
            "coefficients": clf_full.get_coefficients()
        }

    def run_statistical_test(self, y_test, y_pred, actual_accuracy):
        """Step 5: Permutation test"""
        tester = StatisticalTester(
            n_permutations=self.config["statistical_test"]["n_permutations"]
        )

        results = tester.permutation_test(y_test, np.array(y_pred), actual_accuracy)

        # Save results
        tester.save_results(results, str(self.base_dir / "results" / "permutation_test.json"))

        return results

    def generate_visualizations(self, split_data, results, stats_results):
        """Step 6: Generate all figures"""
        viz = Visualizer(
            output_dir=str(self.base_dir / "figures"),
            dpi=self.config["visualization"]["dpi"]
        )

        figures = {}

        # Required: Gate comparison
        figures["gate_comparison"] = viz.plot_gate_comparison(
            target=self.config["success_criteria"]["target_accuracy"],
            baseline=results["baseline"]["accuracy"],
            proposed=results["full"]["accuracy"]
        )

        # Confusion matrix
        figures["confusion_matrix"] = viz.plot_confusion_matrix(
            y_true=split_data["y_test"],
            y_pred=np.array(results["full"]["predictions"]),
            labels=["ResNet", "ViT"]
        )

        # Feature importance
        figures["feature_importance"] = viz.plot_feature_importance(
            coefficients=results["coefficients"],
            top_k=10
        )

        # Permutation distribution
        figures["permutation_dist"] = viz.plot_permutation_distribution(
            permuted_acc=stats_results["permuted_accuracies"],
            actual_acc=stats_results["actual_accuracy"]
        )

        return figures

    def save_all_results(self, metadata, split_data, results, stats_results, figures):
        """Step 7: Save all results"""
        # Save comprehensive metrics
        metrics = {
            "hypothesis_id": self.hypothesis_id,
            "timestamp": datetime.now().isoformat(),
            "model_zoo": {
                "total_models": len(metadata),
                "resnet_count": sum(1 for m in metadata if "resnet" in m["architecture"].lower()),
                "vit_count": sum(1 for m in metadata if "vit" in m["architecture"].lower())
            },
            "train_test_split": {
                "train_size": len(split_data["y_train"]),
                "test_size": len(split_data["y_test"])
            },
            "baseline": {
                "accuracy": results["baseline"]["accuracy"],
                "confusion_matrix": results["baseline"]["confusion_matrix"]
            },
            "full": {
                "accuracy": results["full"]["accuracy"],
                "confusion_matrix": results["full"]["confusion_matrix"]
            },
            "ablation_delta": results["ablation_delta"],
            "statistical_test": {
                "p_value": stats_results["p_value"],
                "permuted_mean": stats_results["permuted_mean"],
                "permuted_std": stats_results["permuted_std"]
            },
            "figures": figures
        }

        metrics_path = self.base_dir / "results" / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"✓ Metrics saved to {metrics_path}")

    def determine_gate_status(self, results, stats_results):
        """Step 8: Determine gate status"""
        accuracy = results["full"]["accuracy"]
        p_value = stats_results["p_value"]
        ablation_delta = results["ablation_delta"]

        target = self.config["success_criteria"]["target_accuracy"]
        partial_threshold = self.config["success_criteria"]["partial_threshold"]
        min_p = self.config["success_criteria"]["min_p_value"]
        min_ablation = self.config["success_criteria"]["min_ablation_improvement"]

        # Check all criteria
        meets_target = accuracy >= target
        meets_statistical = p_value < min_p
        meets_ablation = ablation_delta >= min_ablation

        if meets_target and meets_statistical and meets_ablation:
            gate_status = "PASS"
        elif accuracy >= partial_threshold and meets_statistical:
            gate_status = "PARTIAL"
        else:
            gate_status = "FAIL"

        print(f"\n  Accuracy: {accuracy:.3f} (target: {target:.3f}) - {'✓' if meets_target else '✗'}")
        print(f"  p-value: {p_value:.4f} (threshold: {min_p:.4f}) - {'✓' if meets_statistical else '✗'}")
        print(f"  Ablation: {ablation_delta:.3f} (min: {min_ablation:.3f}) - {'✓' if meets_ablation else '✗'}")
        print(f"\n  🚦 Gate Status: {gate_status}")

        return gate_status


if __name__ == "__main__":
    runner = ExperimentRunner()
    results = runner.run_full_pipeline()

    # Exit with code based on gate status
    if results["gate_status"] == "PASS":
        sys.exit(0)
    elif results["gate_status"] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)
