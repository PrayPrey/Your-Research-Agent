"""
Main experiment runner for causal data valuation.
"""

import torch
import numpy as np
import json
import sys
import logging
from datetime import datetime
from typing import Dict, List
from scipy.stats import spearmanr
from copy import deepcopy

# Import our modules
import config as cfg
from model import create_model
from data_generator import create_dataloaders
from trainer import MultiStageTrainer
from valuation_methods import (
    StageAwareInfluence, StandardInfluence, DataShapley,
    TracIn, RandomBaseline
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Main experiment runner."""

    def __init__(self):
        self.device = cfg.DEVICE
        self.results = {
            "config": {
                "model_size": cfg.EXPERIMENT_CONFIG["model_size"],
                "num_runs": cfg.EXPERIMENT_CONFIG["num_runs"],
                "device": str(self.device),
                "num_gpus": cfg.NUM_GPUS
            },
            "runs": []
        }

        logger.info(f"Device: {self.device}")
        logger.info(f"Number of GPUs: {cfg.NUM_GPUS}")

    def run_single_experiment(self, run_id: int) -> Dict:
        """Run a single experiment."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting Run {run_id + 1}/{cfg.EXPERIMENT_CONFIG['num_runs']}")
        logger.info(f"{'='*60}\n")

        # Set seed for reproducibility
        seed = cfg.DATA_CONFIG["seed"] + run_id
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Create model
        model_config = cfg.MODEL_CONFIGS[cfg.EXPERIMENT_CONFIG["model_size"]]
        model = create_model(model_config).to(self.device)

        logger.info(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")

        # Create dataloaders
        config_dict = {
            "model_config": model_config,
            "data_config": cfg.DATA_CONFIG,
            "stage_configs": cfg.STAGE_CONFIGS
        }
        dataloaders = create_dataloaders(config_dict)

        logger.info(f"Data loaded:")
        for stage, loader in dataloaders.items():
            logger.info(f"  {stage}: {len(loader.dataset)} samples")

        # Create trainer
        trainer = MultiStageTrainer(model, config_dict, self.device)

        # Train all stages
        logger.info("\nStarting multi-stage training...")
        training_metrics = trainer.train_all_stages(dataloaders, cfg.STAGE_CONFIGS)

        logger.info("\nTraining completed!")
        for stage, metrics in training_metrics.items():
            logger.info(f"{stage}:")
            logger.info(f"  Final Loss: {metrics['final_loss']:.4f}")
            if "test_loss" in metrics:
                logger.info(f"  Test Loss: {metrics['test_loss']:.4f}")
                logger.info(f"  Test Perplexity: {metrics['test_perplexity']:.4f}")

        # Evaluate valuation methods
        logger.info("\n" + "="*60)
        logger.info("Evaluating Valuation Methods")
        logger.info("="*60)

        valuation_results = {}

        for stage in ["pretraining", "instruction_tuning", "alignment"]:
            logger.info(f"\nEvaluating stage: {stage}")

            stage_results = self.evaluate_valuation_methods(
                model, trainer, dataloaders, stage, model_config
            )

            valuation_results[stage] = stage_results

        # Compile results
        run_results = {
            "run_id": run_id,
            "training_metrics": training_metrics,
            "valuation_results": valuation_results,
            "seed": seed
        }

        return run_results

    def evaluate_valuation_methods(self, model, trainer, dataloaders,
                                   stage: str, model_config: dict) -> Dict:
        """Evaluate all valuation methods for a specific stage."""
        stage_loader = dataloaders[stage]
        test_loader = dataloaders["test"]

        # Get a batch of training data
        train_batch = next(iter(stage_loader))
        test_batch = next(iter(test_loader))

        # Limit to num_samples for evaluation
        num_samples = min(
            cfg.VALUATION_CONFIG["num_samples"],
            len(train_batch["sample_ids"])
        )

        train_batch = {
            k: v[:num_samples] for k, v in train_batch.items()
        }

        results = {}

        # Get ground truth if enabled
        ground_truth = None
        if cfg.EXPERIMENT_CONFIG["compute_ground_truth"] and num_samples <= 20:
            logger.info("Computing ground truth values (this may take a while)...")
            try:
                ground_truth = trainer.compute_ground_truth_value(
                    stage_loader, test_loader, stage,
                    cfg.STAGE_CONFIGS[stage],
                    num_samples=num_samples
                )
                logger.info(f"Ground truth computed: {len(ground_truth)} values")
            except Exception as e:
                logger.warning(f"Failed to compute ground truth: {e}")
                ground_truth = None

        # Evaluate each method
        methods_config = {
            "device": self.device,
            "low_rank_dim": cfg.VALUATION_CONFIG["low_rank_dim"],
            "num_coalitions": cfg.VALUATION_CONFIG["num_coalitions"]
        }

        for method_name in cfg.EXPERIMENT_CONFIG["methods"]:
            logger.info(f"\nEvaluating method: {method_name}")

            try:
                start_time = datetime.now()

                if method_name == "stage_aware_influence":
                    valuator = StageAwareInfluence(model, methods_config)
                    values = valuator.compute_influence(
                        train_batch, test_batch,
                        trainer.stage_checkpoints, stage
                    )

                elif method_name == "standard_influence":
                    valuator = StandardInfluence(model, methods_config)
                    values = valuator.compute_influence(train_batch, test_batch)

                elif method_name == "tracin":
                    # Get checkpoints
                    checkpoints = []
                    for s in ["pretraining", "instruction_tuning", "alignment"]:
                        ckpt = trainer.get_checkpoint(s)
                        if ckpt is not None:
                            checkpoints.append(ckpt)

                    if len(checkpoints) > 0:
                        valuator = TracIn(model, methods_config)
                        values = valuator.compute_influence(
                            train_batch, test_batch, checkpoints
                        )
                    else:
                        logger.warning("No checkpoints available for TracIn")
                        values = np.zeros(num_samples)

                elif method_name == "random_baseline":
                    valuator = RandomBaseline(methods_config)
                    values = valuator.compute_influence(train_batch, test_batch)

                elif method_name == "data_shapley":
                    # Skip Data Shapley for efficiency (too slow)
                    logger.info("Skipping Data Shapley (too computationally expensive)")
                    values = np.zeros(num_samples)

                else:
                    logger.warning(f"Unknown method: {method_name}")
                    continue

                elapsed_time = (datetime.now() - start_time).total_seconds()

                logger.info(f"  Computed {len(values)} values in {elapsed_time:.2f}s")
                logger.info(f"  Value stats: mean={np.mean(values):.4f}, "
                          f"std={np.std(values):.4f}, "
                          f"min={np.min(values):.4f}, max={np.max(values):.4f}")

                # Compute correlation with ground truth if available
                correlation = None
                if ground_truth is not None and method_name != "data_shapley":
                    try:
                        correlation, p_value = spearmanr(values, ground_truth)
                        logger.info(f"  Spearman correlation with ground truth: "
                                  f"{correlation:.4f} (p={p_value:.4f})")
                    except Exception as e:
                        logger.warning(f"Failed to compute correlation: {e}")

                results[method_name] = {
                    "values": values.tolist(),
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "computation_time": elapsed_time,
                    "correlation_with_ground_truth": float(correlation) if correlation is not None else None
                }

            except Exception as e:
                logger.error(f"Error evaluating {method_name}: {e}")
                import traceback
                traceback.print_exc()

        if ground_truth is not None:
            results["ground_truth"] = {
                "values": ground_truth.tolist(),
                "mean": float(np.mean(ground_truth)),
                "std": float(np.std(ground_truth))
            }

        return results

    def run_all_experiments(self):
        """Run all experiments."""
        logger.info("="*60)
        logger.info("Causal Data Valuation Experiment")
        logger.info("="*60)
        logger.info(f"Configuration:")
        logger.info(f"  Model size: {cfg.EXPERIMENT_CONFIG['model_size']}")
        logger.info(f"  Number of runs: {cfg.EXPERIMENT_CONFIG['num_runs']}")
        logger.info(f"  Methods: {cfg.EXPERIMENT_CONFIG['methods']}")
        logger.info(f"  Device: {self.device}")

        # Run experiments
        for run_id in range(cfg.EXPERIMENT_CONFIG["num_runs"]):
            try:
                run_results = self.run_single_experiment(run_id)
                self.results["runs"].append(run_results)

                # Save intermediate results
                self.save_results()

            except Exception as e:
                logger.error(f"Error in run {run_id}: {e}")
                import traceback
                traceback.print_exc()

        # Aggregate results
        self.aggregate_results()

        # Save final results
        self.save_results()

        logger.info("\n" + "="*60)
        logger.info("All experiments completed!")
        logger.info("="*60)

    def aggregate_results(self):
        """Aggregate results across runs."""
        logger.info("\nAggregating results across runs...")

        if len(self.results["runs"]) == 0:
            logger.warning("No runs to aggregate")
            return

        # Aggregate valuation method performance
        aggregated = {}

        stages = ["pretraining", "instruction_tuning", "alignment"]
        methods = cfg.EXPERIMENT_CONFIG["methods"]

        for stage in stages:
            aggregated[stage] = {}

            for method in methods:
                correlations = []
                times = []

                for run in self.results["runs"]:
                    if stage in run["valuation_results"]:
                        stage_results = run["valuation_results"][stage]
                        if method in stage_results:
                            corr = stage_results[method].get("correlation_with_ground_truth")
                            if corr is not None:
                                correlations.append(corr)
                            times.append(stage_results[method]["computation_time"])

                if len(correlations) > 0:
                    aggregated[stage][method] = {
                        "mean_correlation": float(np.mean(correlations)),
                        "std_correlation": float(np.std(correlations)),
                        "mean_time": float(np.mean(times)),
                        "std_time": float(np.std(times))
                    }

                    logger.info(f"{stage} - {method}:")
                    logger.info(f"  Correlation: {np.mean(correlations):.4f} "
                              f"+/- {np.std(correlations):.4f}")
                    logger.info(f"  Time: {np.mean(times):.2f}s +/- {np.std(times):.2f}s")

        self.results["aggregated"] = aggregated

    def save_results(self):
        """Save results to JSON file."""
        output_file = "results.json"

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Results saved to {output_file}")


def main():
    """Main entry point."""
    runner = ExperimentRunner()
    runner.run_all_experiments()


if __name__ == "__main__":
    main()
