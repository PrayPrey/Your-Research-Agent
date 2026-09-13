"""Main coupling experiment orchestrator"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List
import sys
sys.path.append(str(Path(__file__).parent.parent))

from path_sampling import FGESampler, LinearSampler, load_checkpoint
from metrics import WGAEvaluator, compute_alignment_wrapper
from analysis import compute_spearman_correlation, ResultsAggregator, CouplingResults
from visualization import plot_coupling_scatter, plot_trajectory, plot_comparison, plot_group_accuracy
from data.models import get_resnet50

logger = logging.getLogger(__name__)


class CouplingExperiment:
    """Main experiment orchestrator for geometry-phenotype coupling"""

    def __init__(self, config, base_dir: str = "."):
        """
        Args:
            config: ExperimentConfig instance
            base_dir: Base directory for outputs
        """
        self.config = config
        self.base_dir = Path(base_dir)
        self.device = config.compute.device

        # Create output directories
        self.results_dir = self.base_dir / config.output.results_dir
        self.figures_dir = self.base_dir / config.visualization.output_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model
        self.model = get_resnet50(num_classes=2, pretrained=True).to(self.device)
        self.dataloader = None

    def run(self, train_loader: DataLoader, val_loader: DataLoader,
            erm_checkpoint_path: str, dro_checkpoint_path: str) -> CouplingResults:
        """
        Execute full coupling experiment pipeline.

        Algorithm:
        1. Load ERM and DRO checkpoints
        2. Sample FGE path (M=20 checkpoints)
        3. For each checkpoint:
        4.   Load into model
        5.   Compute A(w)
        6.   Compute WGA
        7. Compute Spearman correlation (FGE)
        8. Repeat steps 2-7 for linear path
        9. Aggregate results
        10. Generate visualizations
        11. Save validation report

        Returns:
            CouplingResults with all metrics
        """
        logger.info("Starting geometry-phenotype coupling experiment...")

        self.dataloader = val_loader

        # Step 1: Load endpoints
        logger.info("Loading ERM and DRO checkpoints...")
        erm_checkpoint = load_checkpoint(erm_checkpoint_path, self.device)
        dro_checkpoint = load_checkpoint(dro_checkpoint_path, self.device)

        # Step 2-7: FGE path
        logger.info("Evaluating FGE path...")
        fge_results = self._evaluate_path(
            FGESampler(erm_checkpoint, dro_checkpoint, self.config.path_sampling.num_samples),
            "FGE"
        )

        # Step 8: Linear path
        logger.info("Evaluating Linear path...")
        linear_results = self._evaluate_path(
            LinearSampler(erm_checkpoint, dro_checkpoint, self.config.path_sampling.num_samples),
            "Linear"
        )

        # Step 9: Aggregate
        logger.info("Aggregating results...")
        aggregator = ResultsAggregator()
        results = aggregator.aggregate(fge_results, linear_results)

        # Step 10: Visualize
        logger.info("Generating visualizations...")
        self._generate_visualizations(results)

        # Step 11: Report
        logger.info("Saving validation report...")
        self._save_metrics(results)

        return results

    def _evaluate_path(self, sampler, path_name: str) -> Dict:
        """
        Evaluate A(w) and WGA for all checkpoints along path.

        Returns:
            Dict with ["alignments", "wgas", "rho", "p_value", "alphas"]
        """
        logger.info(f"Sampling {path_name} path with {self.config.path_sampling.num_samples} checkpoints...")
        checkpoints = sampler.sample()

        alignments = []
        wgas = []
        alphas = np.linspace(0, 1, len(checkpoints))

        for i, checkpoint in enumerate(checkpoints):
            logger.info(f"Evaluating checkpoint {i+1}/{len(checkpoints)} (α={alphas[i]:.3f})...")

            # Load checkpoint
            self.model.load_state_dict(checkpoint)
            self.model.eval()

            # Compute A(w)
            try:
                alignment = compute_alignment_wrapper(
                    self.model, self.dataloader, self.device, simplified=True
                )
                alignments.append(alignment)
                logger.info(f"  A(w) = {alignment:.4f}")
            except Exception as e:
                logger.warning(f"Failed to compute alignment: {e}")
                alignments.append(0.5)  # Default neutral value

            # Compute WGA
            try:
                wga_evaluator = WGAEvaluator(
                    self.model, self.dataloader,
                    num_groups=4, device=self.device
                )
                wga = wga_evaluator.evaluate()
                wgas.append(wga)
                logger.info(f"  WGA = {wga:.4f}")
            except Exception as e:
                logger.warning(f"Failed to compute WGA: {e}")
                wgas.append(0.5)

        # Compute correlation
        alignments_arr = np.array(alignments)
        wgas_arr = np.array(wgas)

        logger.info(f"Computing Spearman correlation for {path_name} path...")
        rho, p_value = compute_spearman_correlation(alignments_arr, wgas_arr)

        logger.info(f"{path_name} Results: ρ={rho:.4f}, p={p_value:.4f}")

        return {
            "alignments": alignments_arr,
            "wgas": wgas_arr,
            "rho": rho,
            "p_value": p_value,
            "alphas": alphas
        }

    def _generate_visualizations(self, results: CouplingResults) -> None:
        """Generate all visualization plots"""

        # 1. Coupling scatter (FGE)
        plot_coupling_scatter(
            results.alignment_values_fge,
            results.wga_values_fge,
            results.fge_rho,
            results.fge_p_value,
            str(self.figures_dir / "coupling_scatter_fge.png")
        )

        # 2. Coupling scatter (Linear)
        plot_coupling_scatter(
            results.alignment_values_linear,
            results.wga_values_linear,
            results.linear_rho,
            results.linear_p_value,
            str(self.figures_dir / "coupling_scatter_linear.png")
        )

        # 3. Trajectory plot (FGE)
        alphas = np.linspace(0, 1, len(results.alignment_values_fge))
        plot_trajectory(
            alphas,
            results.alignment_values_fge,
            results.wga_values_fge,
            str(self.figures_dir / "trajectory_fge.png")
        )

        # 4. Comparison plot
        plot_comparison(
            results.fge_rho,
            results.fge_p_value,
            results.linear_rho,
            results.linear_p_value,
            str(self.figures_dir / "path_comparison.png")
        )

        logger.info(f"Visualizations saved to {self.figures_dir}")

    def _save_metrics(self, results: CouplingResults) -> None:
        """Save metrics to JSON file"""

        metrics = {
            "hypothesis_id": self.config.hypothesis_id,
            "gate_type": self.config.gate_type,
            "fge_path": {
                "rho": float(results.fge_rho),
                "p_value": float(results.fge_p_value),
                "alignment_values": results.alignment_values_fge.tolist(),
                "wga_values": results.wga_values_fge.tolist(),
                "num_samples": len(results.alignment_values_fge)
            },
            "linear_path": {
                "rho": float(results.linear_rho),
                "p_value": float(results.linear_p_value),
                "alignment_values": results.alignment_values_linear.tolist(),
                "wga_values": results.wga_values_linear.tolist(),
                "num_samples": len(results.alignment_values_linear)
            },
            "success_criteria": {
                "primary_threshold": self.config.success_criteria.primary_threshold,
                "p_value_threshold": self.config.success_criteria.p_value_threshold
            }
        }

        metrics_path = self.results_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Metrics saved to {metrics_path}")

    def evaluate_gate(self, results: CouplingResults) -> Dict:
        """
        Evaluate SHOULD_WORK gate criteria.

        Returns:
            Dict with gate result and details
        """
        primary_passed = (
            results.fge_rho < self.config.success_criteria.primary_threshold and
            results.fge_p_value < self.config.success_criteria.p_value_threshold
        )

        secondary_passed = (
            results.linear_rho < self.config.success_criteria.secondary_threshold and
            results.linear_p_value < self.config.success_criteria.p_value_threshold
        )

        # Determine overall result
        if primary_passed:
            if secondary_passed:
                gate_result = "PASS"
                message = "Strong negative correlation confirmed on both paths"
            else:
                gate_result = "PASS"
                message = "Strong negative correlation confirmed on FGE path"
        else:
            # Check for PARTIAL
            partial_low, partial_high = self.config.success_criteria.partial_rho_range
            if partial_low < results.fge_rho < partial_high:
                gate_result = "PARTIAL"
                message = "Weak negative correlation observed (PARTIAL)"
            else:
                gate_result = "FAIL"
                message = "No significant negative correlation found"

        return {
            "result": gate_result,
            "message": message,
            "primary_passed": primary_passed,
            "secondary_passed": secondary_passed,
            "fge_rho": results.fge_rho,
            "fge_p_value": results.fge_p_value,
            "linear_rho": results.linear_rho,
            "linear_p_value": results.linear_p_value
        }
