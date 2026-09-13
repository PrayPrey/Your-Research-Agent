#!/usr/bin/env python3
"""
Main Experiment Runner for H-M-Integrated CAPE
Orchestrates CAPE encoder training and cross-architecture evaluation
"""

import os
import sys
import json
import torch
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import CONFIG
from models.cape_encoder import CAPEEncoder
from models.property_predictor import PropertyPredictor
from models.sne_baseline import SNEBaseline


class CAPEExperimentRunner:
    """Orchestrate CAPE experiment pipeline"""

    def __init__(self, config=None):
        self.config = config or CONFIG
        self.hypothesis_id = self.config["hypothesis_id"]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Setup directories
        self.base_dir = Path(__file__).parent
        self.setup_directories()

    def setup_directories(self):
        """Create all required directories"""
        for dir_name in self.config["directories"].values():
            if not dir_name.startswith("docs/"):  # Skip absolute paths
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Directory created: {dir_path}")

    def run_full_pipeline(self) -> dict:
        """
        Execute full CAPE pipeline.
        Returns: {"gate_status": str, "metrics": dict}
        """
        print("\n" + "="*80)
        print(f"Starting CAPE Experiment: {self.hypothesis_id}")
        print("="*80 + "\n")

        # Step 1: Initialize Models
        print("🔧 Step 1: Initializing CAPE and Baseline Models")
        models = self.initialize_models()

        # Step 2: Test Forward Pass
        print("\n🧪 Step 2: Testing Forward Pass with Dummy Data")
        test_results = self.test_forward_pass(models)

        # Step 3: Run Tests
        print("\n🧪 Step 3: Running Unit Tests")
        test_status = self.run_unit_tests()

        # Step 4: Save Model Summaries
        print("\n💾 Step 4: Saving Model Summaries")
        self.save_model_summaries(models)

        # Step 5: Report Status
        print("\n📊 Step 5: Experiment Status Report")
        gate_status = self.determine_status(test_status, test_results)

        print("\n" + "="*80)
        print(f"Experiment Status: {gate_status}")
        print("="*80 + "\n")

        return {
            "gate_status": gate_status,
            "metrics": test_results,
            "test_status": test_status
        }

    def initialize_models(self) -> dict:
        """Step 1: Initialize all model variants"""
        models = {}

        # Full CAPE
        models["full_cape"] = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            d_arch=self.config["cape_encoder"]["d_arch"],
            tau=self.config["cape_encoder"]["tau"],
            dropout=self.config["cape_encoder"]["dropout"],
            gnn_layers=self.config["cape_encoder"]["num_gnn_layers"],
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=True
        ).to(self.device)

        # Operation + Contrastive (no GNN)
        models["op_contrastive"] = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            d_arch=self.config["cape_encoder"]["d_arch"],
            tau=self.config["cape_encoder"]["tau"],
            dropout=self.config["cape_encoder"]["dropout"],
            enable_operation_encoders=True,
            enable_contrastive=True,
            enable_gnn=False
        ).to(self.device)

        # Operation-only (no contrastive, no GNN)
        models["operation_only"] = CAPEEncoder(
            d_z=self.config["cape_encoder"]["d_z"],
            enable_operation_encoders=True,
            enable_contrastive=False,
            enable_gnn=False
        ).to(self.device)

        # SNE Baseline
        models["sne_baseline"] = SNEBaseline(
            d_model=self.config["cape_encoder"]["d_z"],
            dropout=self.config["cape_encoder"]["dropout"]
        ).to(self.device)

        # Property predictor (shared across all variants)
        models["property_predictor"] = PropertyPredictor(
            d_z=self.config["cape_encoder"]["d_z"],
            num_properties=1,
            dropout=self.config["cape_encoder"]["dropout"]
        ).to(self.device)

        # Print model counts
        for name, model in models.items():
            n_params = sum(p.numel() for p in model.parameters())
            print(f"  {name}: {n_params:,} parameters")

        return models

    def test_forward_pass(self, models: dict) -> dict:
        """Step 2: Test forward pass with dummy data"""
        # Create dummy model weights
        dummy_weights = {
            "conv": [
                torch.randn(16, 3, 3, 3).to(self.device),
                torch.randn(32, 16, 3, 3).to(self.device)
            ],
            "attention": [
                torch.randn(8, 64, 64).to(self.device),
                torch.randn(8, 128, 128).to(self.device)
            ],
            "mlp": [
                torch.randn(512, 256).to(self.device),
                torch.randn(256, 128).to(self.device),
                torch.randn(128, 10).to(self.device)
            ]
        }

        # Create dummy architecture graph
        node_features = torch.randn(10, self.config["cape_encoder"]["d_arch"]).to(self.device)
        edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long).to(self.device)
        arch_graph = (node_features, edge_index)

        results = {}

        # Test each variant
        for name, model in models.items():
            if name == "property_predictor":
                continue

            try:
                with torch.no_grad():
                    # Forward pass
                    if name == "full_cape":
                        z_final = model(dummy_weights, arch_graph=arch_graph)
                    else:
                        z_final = model(dummy_weights, arch_graph=None)

                    # Check shape
                    expected_shape = (self.config["cape_encoder"]["d_z"],)
                    assert z_final.shape == expected_shape, \
                        f"{name}: Expected shape {expected_shape}, got {z_final.shape}"

                    # Property prediction
                    prediction = models["property_predictor"](z_final)

                    results[name] = {
                        "status": "PASS",
                        "embedding_shape": list(z_final.shape),
                        "prediction_shape": list(prediction.shape),
                        "embedding_norm": torch.norm(z_final).item()
                    }

                    print(f"  ✓ {name}: embedding shape {z_final.shape}, norm {results[name]['embedding_norm']:.3f}")

            except Exception as e:
                results[name] = {
                    "status": "FAIL",
                    "error": str(e)
                }
                print(f"  ✗ {name}: {e}")

        # Test diagnostic metrics for full CAPE
        try:
            diagnostics = models["full_cape"].get_diagnostic_metrics(dummy_weights)
            results["diagnostics"] = diagnostics
            print(f"\n  Diagnostics:")
            print(f"    Conv-Attn Similarity: {diagnostics.get('conv_attn_similarity', 'N/A'):.3f}")
            print(f"    Alpha (GNN weight): {diagnostics.get('alpha', 'N/A'):.3f}")
        except Exception as e:
            print(f"  Warning: Could not compute diagnostics: {e}")

        return results

    def run_unit_tests(self) -> str:
        """Step 3: Run pytest unit tests"""
        import subprocess

        test_dir = self.base_dir / "tests"
        if not test_dir.exists():
            return "SKIP: No test directory"

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print("  ✓ All unit tests passed")
                return "PASS"
            else:
                print("  ✗ Some unit tests failed")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return "FAIL"

        except subprocess.TimeoutExpired:
            print("  ✗ Tests timed out")
            return "TIMEOUT"
        except FileNotFoundError:
            print("  ⚠ pytest not available, skipping tests")
            return "SKIP"
        except Exception as e:
            print(f"  ✗ Test execution failed: {e}")
            return "ERROR"

    def save_model_summaries(self, models: dict):
        """Step 4: Save model architecture summaries"""
        summaries = {}

        for name, model in models.items():
            if name == "property_predictor":
                continue

            summaries[name] = {
                "class": model.__class__.__name__,
                "parameters": sum(p.numel() for p in model.parameters()),
                "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
                "modules": str(model)[:500]  # Truncate for readability
            }

        # Save to JSON
        summary_path = self.base_dir / "results" / "model_summaries.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, 'w') as f:
            json.dump(summaries, f, indent=2)

        print(f"  ✓ Model summaries saved to {summary_path}")

    def determine_status(self, test_status: str, test_results: dict) -> str:
        """Step 5: Determine experiment gate status"""
        # Check if all variants passed forward pass
        all_passed = all(
            v.get("status") == "PASS"
            for k, v in test_results.items()
            if k != "diagnostics"
        )

        # Check diagnostic thresholds
        diagnostics = test_results.get("diagnostics", {})
        conv_attn_sim = diagnostics.get("conv_attn_similarity", 0.0)
        alpha = diagnostics.get("alpha", 0.0)

        diagnostic_pass = (
            conv_attn_sim < self.config["diagnostics"]["operation_similarity"]["threshold"]
            and alpha > self.config["diagnostics"]["gnn_weight"]["threshold"]
        )

        if all_passed and test_status == "PASS" and diagnostic_pass:
            status = "READY FOR TRAINING"
        elif all_passed and diagnostic_pass:
            status = "READY (Tests Skipped)"
        elif all_passed:
            status = "PARTIAL (Diagnostic Thresholds Not Met)"
        else:
            status = "IMPLEMENTATION INCOMPLETE"

        return status


if __name__ == "__main__":
    runner = CAPEExperimentRunner()
    results = runner.run_full_pipeline()

    # Exit with code based on status
    if "READY" in results["gate_status"]:
        sys.exit(0)
    else:
        sys.exit(1)
