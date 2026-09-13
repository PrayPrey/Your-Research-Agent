"""Baseline experiment runner for comparison."""

import torch
import time
import logging
from typing import Dict, Any


class BaselineRunner:
    """Run baseline experiments for comparison."""

    def __init__(self, config, model_loader):
        self.config = config
        self.model_loader = model_loader
        self.logger = logging.getLogger(__name__)

    def run_baseline(self, name: str, use_quantization: bool,
                    use_lora: bool, input_ids: torch.Tensor) -> Dict[str, Any]:
        """Run a single baseline configuration."""
        self.logger.info(f"Running baseline {name}...")

        try:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

            model = self.model_loader.load_baseline(
                use_quantization=use_quantization,
                use_lora=use_lora
            )
            model.eval()

            device = next(model.parameters()).device
            input_ids = input_ids.to(device)

            start_time = time.time()

            with torch.no_grad():
                outputs = model(input_ids)

            latency_ms = (time.time() - start_time) * 1000

            peak_memory_mb = torch.cuda.max_memory_allocated() / (1024 ** 2)

            has_nan = torch.isnan(outputs.logits).any().item()
            has_inf = torch.isinf(outputs.logits).any().item()

            del model
            torch.cuda.empty_cache()

            return {
                'name': name,
                'success': True,
                'latency_ms': latency_ms,
                'peak_memory_mb': peak_memory_mb,
                'has_nan': has_nan,
                'has_inf': has_inf
            }

        except Exception as e:
            self.logger.error(f"Baseline {name} failed: {e}")
            return {
                'name': name,
                'success': False,
                'error': str(e)
            }

    def run_all_baselines(self, input_ids: torch.Tensor) -> Dict[str, Dict[str, Any]]:
        """Run all baseline configurations."""
        baselines = {
            'B1': {'use_quantization': False, 'use_lora': False},
            'B3': {'use_quantization': True, 'use_lora': False},
            'B2': {'use_quantization': False, 'use_lora': True},
        }

        results = {}

        for name, config in baselines.items():
            results[name] = self.run_baseline(
                name,
                config['use_quantization'],
                config['use_lora'],
                input_ids
            )

        return results
