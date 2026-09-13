"""Experiment runner for SAT profiling validation."""

import json
import logging
from pathlib import Path
from typing import Union, List, Dict
import torch

from profiling.profiler import SATProfiler
from config import CNNConfig, TransformerConfig
from data.loader import get_cnn_dataloader, get_transformer_dataloader, inject_jitter_delay
from models.loader import load_cnn_model, load_transformer_model, get_optimizer, get_criterion
from evaluation.metrics import compute_degradation


logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Orchestrates SAT profiling experiments."""

    def __init__(self, output_dir: str):
        """
        Initialize experiment runner.

        Args:
            output_dir: Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.profiler = SATProfiler()

    def run_single_config(
        self,
        config: Union[CNNConfig, TransformerConfig],
        config_id: str
    ) -> Dict:
        """
        Run profiling for a single configuration.

        Args:
            config: Configuration object
            config_id: Unique identifier for this config

        Returns:
            Dictionary with profiling results
        """
        logger.info(f"Running config: {config_id}")

        try:
            # Load model
            if isinstance(config, CNNConfig):
                model = load_cnn_model(config, device=config.device)
                dataloader = get_cnn_dataloader(config, train=True, limit_batches=100)
            else:
                model = load_transformer_model(config, device=config.device)
                dataloader = get_transformer_dataloader(config, train=True, limit_batches=100)

            optimizer = get_optimizer(model, config)
            criterion = get_criterion(config)

            # Phase 1: Profile first N batches for SAT measurement
            self.profiler.reset()
            model.train()

            for i, batch in enumerate(dataloader):
                if i >= config.num_profiling_batches:
                    break

                try:
                    self.profiler.profile_step(model, batch, optimizer, criterion)
                except Exception as e:
                    logger.warning(f"Batch {i} failed: {e}")
                    continue

            # Compute SAT
            if len(self.profiler.batch_times) < 2:
                logger.error(f"Not enough batches profiled for {config_id}")
                return None

            SAT = self.profiler.compute_SAT()
            batch_times = self.profiler.get_batch_times()
            gpu_utils = self.profiler.get_gpu_utils()

            # Phase 2: Measure full epoch time (limited to 100 batches for PoC)
            self.profiler.reset()
            epoch_time = 0.0

            try:
                epoch_time = self.profiler.measure_epoch_time(model, dataloader, optimizer, criterion)
            except Exception as e:
                logger.warning(f"Epoch measurement failed: {e}")
                epoch_time = sum(batch_times)  # Fallback estimate

            # Compute baseline (estimate from median batch time)
            import numpy as np
            median_batch_time = np.median(batch_times)
            baseline_time = median_batch_time * len(dataloader)

            degradation = compute_degradation(epoch_time, baseline_time)

            result = {
                "config_id": config_id,
                "architecture": config.model_name,
                "dataset": config.dataset,
                "optimizer": config.optimizer,
                "batch_size": config.batch_size,
                "SAT": float(SAT),
                "epoch_time": float(epoch_time),
                "baseline_time": float(baseline_time),
                "degradation": float(degradation),
                "num_batches_profiled": len(batch_times),
                "avg_batch_time": float(np.mean(batch_times)),
                "median_batch_time": float(np.median(batch_times)),
                "p95_batch_time": float(np.percentile(batch_times, 95)),
                "avg_gpu_util": float(np.mean(gpu_utils)) if gpu_utils else 0.0
            }

            logger.info(f"Config {config_id}: SAT={SAT:.3f}, degradation={degradation*100:.1f}%")

            return result

        except Exception as e:
            logger.error(f"Config {config_id} failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_natural_workload(
        self,
        configs: List[Union[CNNConfig, TransformerConfig]]
    ) -> Dict:
        """
        Run profiling across all natural workload configurations.

        Args:
            configs: List of configurations

        Returns:
            Dictionary mapping config_id -> results
        """
        results = {}

        for i, config in enumerate(configs):
            config_id = f"config_{i:03d}"

            result = self.run_single_config(config, config_id)

            if result is not None:
                results[config_id] = result

            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return results

    def run_synthetic_jitter(
        self,
        config: Union[CNNConfig, TransformerConfig],
        delays: List[int]
    ) -> Dict:
        """
        Run synthetic jitter experiments.

        Args:
            config: Base configuration
            delays: List of delay values in milliseconds

        Returns:
            Dictionary mapping delay_ms -> SAT
        """
        logger.info("Running synthetic jitter experiments")

        jitter_results = {}

        try:
            # Load model once
            if isinstance(config, CNNConfig):
                model = load_cnn_model(config, device=config.device)
                base_dataloader = get_cnn_dataloader(config, train=True, limit_batches=100)
            else:
                model = load_transformer_model(config, device=config.device)
                base_dataloader = get_transformer_dataloader(config, train=True, limit_batches=100)

            optimizer = get_optimizer(model, config)
            criterion = get_criterion(config)

            for delay_ms in delays:
                logger.info(f"Testing delay: {delay_ms}ms")

                # Inject jitter
                if delay_ms > 0:
                    dataloader = inject_jitter_delay(base_dataloader, delay_ms)
                else:
                    dataloader = base_dataloader

                # Profile with jitter
                self.profiler.reset()
                model.train()

                for i, batch in enumerate(dataloader):
                    if i >= config.num_profiling_batches:
                        break

                    try:
                        self.profiler.profile_step(model, batch, optimizer, criterion)
                    except Exception as e:
                        logger.warning(f"Jitter batch {i} failed: {e}")
                        continue

                # Compute SAT
                if len(self.profiler.batch_times) >= 2:
                    SAT = self.profiler.compute_SAT()
                    jitter_results[delay_ms] = float(SAT)
                    logger.info(f"Delay {delay_ms}ms: SAT={SAT:.3f}")

                # Clear cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        except Exception as e:
            logger.error(f"Jitter experiment failed: {e}")
            import traceback
            traceback.print_exc()

        return jitter_results

    def save_results(self, results: Dict, filename: str) -> None:
        """
        Save results to JSON file.

        Args:
            results: Results dictionary
            filename: Output filename
        """
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_path}")
