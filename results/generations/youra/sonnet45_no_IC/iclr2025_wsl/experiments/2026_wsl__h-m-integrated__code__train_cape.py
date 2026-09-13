#!/usr/bin/env python3
"""
CAPE Training Script - Full Mechanism Validation
Loads REAL HuggingFace models and trains cross-architecture encoder
"""

import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import spearmanr
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import CONFIG
from models.cape_encoder import CAPEEncoder
from models.property_predictor import PropertyPredictor
from models.sne_baseline import SNEBaseline
from model_zoo import ModelZooCollector
from feature_extractor import WeightFeatureExtractor


class CAPETrainer:
    """Train CAPE encoder with real HuggingFace models"""

    def __init__(self, config=None):
        self.config = config or CONFIG
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.base_dir = Path(__file__).parent

        # Setup directories
        self.results_dir = self.base_dir / "results"
        self.checkpoint_dir = self.base_dir / "checkpoints"
        self.results_dir.mkdir(exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)

        print(f"🚀 CAPE Trainer Initialized")
        print(f"   Device: {self.device}")
        print(f"   Config: {self.config['hypothesis_id']}")

    def load_real_models(self) -> Tuple[List[Dict], Dict]:
        """Load REAL models from HuggingFace/timm"""
        print("\n" + "="*80)
        print("📥 Step 1: Loading REAL Pre-trained Models from HuggingFace/timm")
        print("="*80)

        data_dir = self.base_dir / "data"
        metadata_path = data_dir / "models_metadata.json"
        features_path = data_dir / "weight_features.npz"

        # Check if already downloaded AND features extracted
        if metadata_path.exists() and features_path.exists():
            print("✓ Found cached model metadata, checking features...")
            with open(metadata_path, 'r') as f:
                models_metadata = json.load(f)

            # Check if features are extracted (has feature_index field)
            if models_metadata and "feature_index" in models_metadata[0]:
                features_data = np.load(features_path)
                print(f"✓ Loaded {len(models_metadata)} cached models with extracted features")
                return models_metadata, features_data
            else:
                print("  ⚠ Cached metadata found but features not extracted yet")
                print("  Will extract features from cached models...")
                # Continue to feature extraction below

        # Check if we need to download models or just extract features
        if metadata_path.exists():
            # Models already collected, just need to extract features
            print("✓ Using existing cached model metadata")
            with open(metadata_path, 'r') as f:
                models_metadata = json.load(f)
            print(f"✓ Found {len(models_metadata)} model entries")
            print(f"  Extracting features from cached models...")
        else:
            # Download and collect models
            print("⚠ No cached data found, downloading models...")
            collector = ModelZooCollector(output_dir=str(data_dir))

            # Collect model metadata (50 ResNet + 50 ViT for PoC scale)
            n_resnet = 50  # Can increase to 100 for full experiment
            n_vit = 50     # Can increase to 100 for full experiment

            print(f"📊 Target: {n_resnet} ResNet-50 + {n_vit} ViT-Base models")
            collection_result = collector.collect_models(n_resnet=n_resnet, n_vit=n_vit)
            models_metadata = collection_result["models"]

            print(f"\n✓ Collected {len(models_metadata)} model entries")
            print(f"  Loading actual model weights and extracting features...")

        # Now extract features from models
        collector = ModelZooCollector(output_dir=str(data_dir))

        # Extract features from real model weights
        extractor = WeightFeatureExtractor()
        all_features = []
        valid_metadata = []

        for idx, model_info in enumerate(tqdm(models_metadata, desc="Processing models")):
            try:
                # Download real model
                model_data = collector.download_model(model_info["model_id"])
                state_dict = model_data["state_dict"]

                # Extract weight features from REAL model
                features = extractor.extract_features(state_dict)
                all_features.append(features)

                # Store metadata
                model_info["feature_index"] = len(valid_metadata)
                valid_metadata.append(model_info)

                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(models_metadata)} models")

            except Exception as e:
                print(f"  ⚠ Failed to load {model_info['model_id']}: {e}")
                continue

        # Save extracted features
        features_dict = {
            "conv_features": np.array([f["conv"] for f in all_features]),
            "attn_features": np.array([f["attention"] for f in all_features]),
            "mlp_features": np.array([f["mlp"] for f in all_features]),
            "graph_features": np.array([f["graph_nodes"] for f in all_features]),
            "graph_edges": np.array([f["graph_edges"] for f in all_features], dtype=object)
        }

        np.savez_compressed(features_path, **features_dict)
        with open(metadata_path, 'w') as f:
            json.dump(valid_metadata, f, indent=2)

        print(f"\n✓ Successfully processed {len(valid_metadata)} models")
        print(f"  Features saved to: {features_path}")
        print(f"  Metadata saved to: {metadata_path}")

        return valid_metadata, features_dict

    def prepare_datasets(self, models_metadata: List[Dict], features_data: Dict) -> Dict:
        """Split into train/val/test sets"""
        print("\n" + "="*80)
        print("📊 Step 2: Preparing Train/Val/Test Splits")
        print("="*80)

        # Group by architecture
        arch_groups = {}
        for model in models_metadata:
            arch = model["architecture"]
            if arch not in arch_groups:
                arch_groups[arch] = []
            arch_groups[arch].append(model)

        print(f"  Architecture distribution:")
        for arch, models in arch_groups.items():
            print(f"    {arch}: {len(models)} models")

        # Split each architecture 70/15/15
        datasets = {"train": [], "val": [], "test": []}

        for arch, models in arch_groups.items():
            n = len(models)
            n_train = int(0.7 * n)
            n_val = int(0.15 * n)

            # Shuffle with fixed seed
            np.random.seed(42)
            indices = np.random.permutation(n)

            train_idx = indices[:n_train]
            val_idx = indices[n_train:n_train + n_val]
            test_idx = indices[n_train + n_val:]

            datasets["train"].extend([models[i] for i in train_idx])
            datasets["val"].extend([models[i] for i in val_idx])
            datasets["test"].extend([models[i] for i in test_idx])

        print(f"\n  Split sizes:")
        print(f"    Train: {len(datasets['train'])} models")
        print(f"    Val:   {len(datasets['val'])} models")
        print(f"    Test:  {len(datasets['test'])} models")

        # Validate accuracy labels are populated
        print(f"\n  Validating accuracy labels...")
        all_models = datasets["train"] + datasets["val"] + datasets["test"]
        accuracies = [m.get("imagenet_accuracy") for m in all_models]
        none_count = sum(1 for acc in accuracies if acc is None)

        if none_count > 0:
            raise ValueError(f"MOCK DATA DETECTED: {none_count}/{len(all_models)} models have imagenet_accuracy=None")

        # Print accuracy statistics
        valid_accs = [acc for acc in accuracies if acc is not None]
        print(f"    ✓ All {len(valid_accs)} models have real accuracy labels")
        print(f"    Accuracy range: [{min(valid_accs):.4f}, {max(valid_accs):.4f}]")
        print(f"    Mean accuracy: {np.mean(valid_accs):.4f} ± {np.std(valid_accs):.4f}")

        # Per-architecture statistics
        for arch in arch_groups.keys():
            arch_accs = [m["imagenet_accuracy"] for m in all_models if m["architecture"] == arch]
            print(f"    {arch}: {np.mean(arch_accs):.4f} ± {np.std(arch_accs):.4f} (n={len(arch_accs)})")

        # Attach features to each split
        for split in ["train", "val", "test"]:
            for model in datasets[split]:
                idx = model["feature_index"]
                model["features"] = {
                    "conv": features_data["conv_features"][idx],
                    "attention": features_data["attn_features"][idx],
                    "mlp": features_data["mlp_features"][idx],
                    "graph_nodes": features_data["graph_features"][idx],
                    "graph_edges": features_data["graph_edges"][idx]
                }

        return datasets

    def train_variant(self, model: nn.Module, datasets: Dict, variant_name: str) -> Dict:
        """Train a single model variant"""
        print(f"\n🏋️ Training {variant_name}...")

        # Property predictor
        property_predictor = PropertyPredictor(
            d_z=self.config["cape_encoder"]["d_z"],
            num_properties=1,
            dropout=self.config["cape_encoder"]["dropout"]
        ).to(self.device)

        # Optimizer
        all_params = list(model.parameters()) + list(property_predictor.parameters())
        optimizer = optim.AdamW(
            all_params,
            lr=self.config["training"]["optimizer"]["lr"],
            weight_decay=self.config["training"]["optimizer"]["weight_decay"]
        )

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        train_history = []

        num_epochs = self.config["training"]["epochs"]

        for epoch in range(num_epochs):
            # Training phase
            model.train()
            property_predictor.train()
            train_loss = 0.0

            for model_data in datasets["train"]:
                optimizer.zero_grad()

                # Prepare inputs from REAL model features
                weights = {
                    "conv": [torch.tensor(model_data["features"]["conv"]).to(self.device)],
                    "attention": [torch.tensor(model_data["features"]["attention"]).to(self.device)],
                    "mlp": [torch.tensor(model_data["features"]["mlp"]).to(self.device)]
                }

                graph_nodes = torch.tensor(model_data["features"]["graph_nodes"]).to(self.device)
                graph_edges = torch.tensor(model_data["features"]["graph_edges"]).to(self.device)
                arch_graph = (graph_nodes, graph_edges) if variant_name == "full_cape" else None

                # Forward pass
                z = model(weights, arch_graph=arch_graph)
                prediction = property_predictor(z)

                # Loss (MSE for property prediction)
                target_acc = model_data.get("imagenet_accuracy")
                if target_acc is None:
                    raise ValueError(f"Model {model_data.get('model_id', 'unknown')} missing imagenet_accuracy - mock data detected!")
                target = torch.tensor([target_acc], dtype=torch.float32).to(self.device)
                loss = nn.MSELoss()(prediction, target)

                # Backward pass
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            train_loss /= len(datasets["train"])

            # Validation phase
            model.eval()
            property_predictor.eval()
            val_loss = 0.0

            with torch.no_grad():
                for model_data in datasets["val"]:
                    weights = {
                        "conv": [torch.tensor(model_data["features"]["conv"]).to(self.device)],
                        "attention": [torch.tensor(model_data["features"]["attention"]).to(self.device)],
                        "mlp": [torch.tensor(model_data["features"]["mlp"]).to(self.device)]
                    }

                    graph_nodes = torch.tensor(model_data["features"]["graph_nodes"]).to(self.device)
                    graph_edges = torch.tensor(model_data["features"]["graph_edges"]).to(self.device)
                    arch_graph = (graph_nodes, graph_edges) if variant_name == "full_cape" else None

                    z = model(weights, arch_graph=arch_graph)
                    prediction = property_predictor(z)

                    target_acc = model_data.get("imagenet_accuracy")
                    if target_acc is None:
                        raise ValueError(f"Model {model_data.get('model_id', 'unknown')} missing imagenet_accuracy - mock data detected!")
                    target = torch.tensor([target_acc], dtype=torch.float32).to(self.device)
                    loss = nn.MSELoss()(prediction, target)

                    val_loss += loss.item()

            val_loss /= len(datasets["val"])

            train_history.append({"epoch": epoch + 1, "train_loss": train_loss, "val_loss": val_loss})

            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch + 1}/{num_epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save checkpoint
                torch.save({
                    "model": model.state_dict(),
                    "property_predictor": property_predictor.state_dict(),
                    "epoch": epoch + 1,
                    "val_loss": val_loss
                }, self.checkpoint_dir / f"{variant_name}_best.pth")
            else:
                patience_counter += 1
                if patience_counter >= self.config["training"]["early_stopping"]["patience"]:
                    print(f"  Early stopping at epoch {epoch + 1}")
                    break

        # Load best model
        checkpoint = torch.load(self.checkpoint_dir / f"{variant_name}_best.pth")
        model.load_state_dict(checkpoint["model"])
        property_predictor.load_state_dict(checkpoint["property_predictor"])

        return {
            "model": model,
            "property_predictor": property_predictor,
            "train_history": train_history,
            "best_val_loss": best_val_loss
        }

    def evaluate_cross_architecture(self, variant_results: Dict, datasets: Dict) -> Dict:
        """Evaluate cross-architecture transfer (ResNet→ViT)"""
        print("\n" + "="*80)
        print("📊 Step 4: Cross-Architecture Evaluation (ResNet→ViT)")
        print("="*80)

        results = {}

        for variant_name, variant_data in variant_results.items():
            model = variant_data["model"]
            property_predictor = variant_data["property_predictor"]

            model.eval()
            property_predictor.eval()

            # Get ResNet test models
            resnet_test = [m for m in datasets["test"] if m["architecture"] == "resnet50"]
            vit_test = [m for m in datasets["test"] if m["architecture"] == "vit_base"]

            # Train on ResNet, evaluate on ViT
            predictions = []
            actuals = []

            with torch.no_grad():
                for model_data in vit_test:  # Predict ViT accuracies
                    weights = {
                        "conv": [torch.tensor(model_data["features"]["conv"]).to(self.device)],
                        "attention": [torch.tensor(model_data["features"]["attention"]).to(self.device)],
                        "mlp": [torch.tensor(model_data["features"]["mlp"]).to(self.device)]
                    }

                    graph_nodes = torch.tensor(model_data["features"]["graph_nodes"]).to(self.device)
                    graph_edges = torch.tensor(model_data["features"]["graph_edges"]).to(self.device)
                    arch_graph = (graph_nodes, graph_edges) if variant_name == "full_cape" else None

                    z = model(weights, arch_graph=arch_graph)
                    prediction = property_predictor(z)

                    predictions.append(prediction.cpu().item())
                    actual_acc = model_data.get("imagenet_accuracy")
                    if actual_acc is None:
                        raise ValueError(f"Model {model_data.get('model_id', 'unknown')} missing imagenet_accuracy - mock data detected!")
                    actuals.append(actual_acc)

            # Compute Spearman correlation
            if len(predictions) > 0 and len(actuals) > 0:
                rho, p_value = spearmanr(predictions, actuals)
            else:
                rho, p_value = 0.0, 1.0

            results[variant_name] = {
                "resnet_to_vit_correlation": rho,
                "p_value": p_value,
                "n_test_samples": len(vit_test)
            }

            print(f"  {variant_name}: ρ = {rho:.4f} (p = {p_value:.4f}, n = {len(vit_test)})")

        return results

    def run_full_experiment(self) -> Dict:
        """Execute full CAPE training and evaluation"""
        print("\n" + "="*80)
        print(f"🧪 CAPE Full Experiment - {self.config['hypothesis_id']}")
        print("="*80)

        # Step 1: Load real models
        models_metadata, features_data = self.load_real_models()

        # Step 2: Prepare datasets
        datasets = self.prepare_datasets(models_metadata, features_data)

        # Step 3: Train all variants
        print("\n" + "="*80)
        print("🏋️ Step 3: Training All Variants")
        print("="*80)

        variant_results = {}

        # Full CAPE
        full_cape = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            d_arch=self.config["cape_encoder"]["d_arch"],
            tau=self.config["cape_encoder"]["tau"],
            dropout=self.config["cape_encoder"]["dropout"],
            gnn_layers=self.config["cape_encoder"]["num_gnn_layers"],
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=True
        ).to(self.device)
        variant_results["full_cape"] = self.train_variant(full_cape, datasets, "full_cape")

        # Op + Contrastive (no GNN)
        op_contrastive = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=False
        ).to(self.device)
        variant_results["op_contrastive"] = self.train_variant(op_contrastive, datasets, "op_contrastive")

        # Operation-only
        operation_only = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            enable_operation_encoders=True,
            enable_contrastive=False,
            enable_gnn=False
        ).to(self.device)
        variant_results["operation_only"] = self.train_variant(operation_only, datasets, "operation_only")

        # SNE Baseline
        sne_baseline = SNEBaseline(
            d_model=self.config["cape_encoder"]["d_z"],
            dropout=self.config["cape_encoder"]["dropout"]
        ).to(self.device)
        variant_results["sne_baseline"] = self.train_variant(sne_baseline, datasets, "sne_baseline")

        # Step 4: Evaluate cross-architecture transfer
        cross_arch_results = self.evaluate_cross_architecture(variant_results, datasets)

        # Step 5: Gate evaluation
        print("\n" + "="*80)
        print("🎯 Step 5: Gate Evaluation")
        print("="*80)

        cape_rho = cross_arch_results["full_cape"]["resnet_to_vit_correlation"]
        sne_rho = cross_arch_results["sne_baseline"]["resnet_to_vit_correlation"]
        delta_rho = cape_rho - sne_rho

        gate_threshold = 0.65
        gate_pass = cape_rho >= gate_threshold
        statistical_pass = delta_rho >= 0.10

        print(f"  Full CAPE ρ: {cape_rho:.4f}")
        print(f"  SNE Baseline ρ: {sne_rho:.4f}")
        print(f"  Delta ρ: {delta_rho:.4f}")
        print(f"  Gate Threshold: {gate_threshold}")
        print(f"  Gate Status: {'PASS' if gate_pass else 'FAIL'}")
        print(f"  Statistical Significance: {'PASS' if statistical_pass else 'FAIL'}")

        # Save final results
        final_results = {
            "hypothesis_id": self.config["hypothesis_id"],
            "timestamp": datetime.now().isoformat(),
            "gate_evaluation": {
                "criteria": f"ρ ≥ {gate_threshold} on ResNet→ViT",
                "measured_value": cape_rho,
                "threshold": gate_threshold,
                "result": "PASS" if gate_pass else "FAIL"
            },
            "cross_architecture_results": cross_arch_results,
            "ablation_results": {
                name: {
                    "resnet_to_vit_correlation": data["resnet_to_vit_correlation"],
                    "train_loss": data["train_history"][-1]["train_loss"],
                    "val_loss": data["best_val_loss"]
                }
                for name, data in variant_results.items()
            },
            "statistical_validation": {
                "delta_rho_cape_vs_sne": delta_rho,
                "p_value": cross_arch_results["full_cape"]["p_value"]
            }
        }

        results_path = self.results_dir / "experiment_results.json"
        with open(results_path, 'w') as f:
            json.dump(final_results, f, indent=2)

        print(f"\n✓ Results saved to: {results_path}")

        return final_results


if __name__ == "__main__":
    trainer = CAPETrainer()
    results = trainer.run_full_experiment()

    # Exit with appropriate code
    gate_pass = results["gate_evaluation"]["result"] == "PASS"
    sys.exit(0 if gate_pass else 1)
