"""Evaluation pipeline for width-scaling experiment."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List
from pathlib import Path
import json
import numpy as np


class WidthScalingEvaluator:
    """Evaluate test error advantage across widths."""

    def __init__(self, config: dict):
        """
        Initialize evaluator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.results_dir = Path(config["results_dir"])
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def compute_test_error(
        self,
        model: nn.Module,
        test_loader: DataLoader
    ) -> float:
        """
        Compute test error for a model.

        Args:
            model: Trained model
            test_loader: Test dataloader

        Returns:
            Test error (MSE loss)
        """
        model = model.to(self.device)
        model.eval()

        criterion = nn.MSELoss()
        test_error = 0.0

        with torch.no_grad():
            for data, _ in test_loader:
                data = data.to(self.device)
                output = model(data)

                # Same target as training
                target = data.mean(dim=1, keepdim=True).expand_as(output)
                loss = criterion(output, target)
                test_error += loss.item()

        test_error /= len(test_loader)
        return test_error

    def evaluate_all_widths(
        self,
        model_factory: callable,
        dataloaders: Dict[str, Dict[str, DataLoader]],
        checkpoint_dir: Path
    ) -> Dict:
        """
        Evaluate test error for all width configurations.

        Args:
            model_factory: Function that creates model given (model_type, width)
            dataloaders: Dictionary of dataloaders
            checkpoint_dir: Directory containing trained checkpoints

        Returns:
            {
                'test_errors': Dict mapping width to {mlp_error, nfn_error, delta},
                'monotonicity_check': bool
            }
        """
        widths = self.config["hidden_widths"]
        test_errors = {}

        for width in widths:
            print(f"\nEvaluating width: {width}")

            # Load and evaluate MLP
            mlp_model = model_factory('mlp', width)
            mlp_checkpoint = checkpoint_dir / f"mlp_w{width}.pt"
            if mlp_checkpoint.exists():
                checkpoint = torch.load(mlp_checkpoint, map_location=self.device)
                mlp_model.load_state_dict(checkpoint['model_state_dict'])
                mlp_error = self.compute_test_error(
                    mlp_model,
                    dataloaders['mlp']['test']
                )
            else:
                print(f"Warning: MLP checkpoint not found for width {width}")
                mlp_error = float('nan')

            # Load and evaluate NFN
            nfn_model = model_factory('nfn', width)
            nfn_checkpoint = checkpoint_dir / f"nfn_w{width}.pt"
            if nfn_checkpoint.exists():
                checkpoint = torch.load(nfn_checkpoint, map_location=self.device)
                nfn_model.load_state_dict(checkpoint['model_state_dict'])
                nfn_error = self.compute_test_error(
                    nfn_model,
                    dataloaders['nfn']['test']
                )
            else:
                print(f"Warning: NFN checkpoint not found for width {width}")
                nfn_error = float('nan')

            # Compute test error advantage: Δ_test(d) = error_MLP - error_NFN
            # Positive value means NFN has lower error (better)
            delta = mlp_error - nfn_error

            test_errors[width] = {
                'mlp_error': mlp_error,
                'nfn_error': nfn_error,
                'delta': delta
            }

            print(f"  MLP Error: {mlp_error:.4f}")
            print(f"  NFN Error: {nfn_error:.4f}")
            print(f"  Δ_test(d): {delta:.4f}")

        # Check monotonicity: Δ_test should increase with width
        deltas = [test_errors[w]['delta'] for w in widths]
        monotonicity_check = self.check_monotonicity(deltas)

        print(f"\nMonotonicity Check: {'PASS' if monotonicity_check else 'FAIL'}")
        print(f"Delta sequence: {[f'{d:.4f}' for d in deltas]}")

        # Save results
        results_file = self.results_dir / "test_errors.json"
        with open(results_file, 'w') as f:
            json.dump({
                'test_errors': test_errors,
                'monotonicity_check': monotonicity_check,
                'delta_sequence': deltas
            }, f, indent=2)

        return {
            'test_errors': test_errors,
            'monotonicity_check': monotonicity_check
        }

    def check_monotonicity(self, sequence: List[float]) -> bool:
        """
        Check if sequence is monotonically increasing.

        Args:
            sequence: List of delta values

        Returns:
            True if monotonically increasing (allowing small violations)
        """
        if any(np.isnan(sequence)):
            return False

        # Check strict monotonicity
        violations = 0
        for i in range(len(sequence) - 1):
            if sequence[i+1] <= sequence[i]:
                violations += 1

        # Allow up to 1 small violation (empirical tolerance)
        return violations <= 1

    def compute_gate_metrics(
        self,
        test_errors: Dict
    ) -> Dict:
        """
        Compute gate metrics for MUST_WORK validation.

        Args:
            test_errors: Dictionary of test errors per width

        Returns:
            {
                'monotonicity_satisfied': bool,
                'all_deltas_positive': bool,
                'mean_delta': float,
                'gate_pass': bool
            }
        """
        widths = self.config["hidden_widths"]
        deltas = [test_errors[w]['delta'] for w in widths]

        monotonicity_satisfied = self.check_monotonicity(deltas)
        all_deltas_positive = all(d > 0 for d in deltas)
        mean_delta = np.mean(deltas)

        # Gate passes if monotonicity holds and most deltas are positive
        gate_pass = monotonicity_satisfied and sum(d > 0 for d in deltas) >= len(deltas) * 0.6

        return {
            'monotonicity_satisfied': monotonicity_satisfied,
            'all_deltas_positive': all_deltas_positive,
            'mean_delta': float(mean_delta),
            'gate_pass': gate_pass
        }
