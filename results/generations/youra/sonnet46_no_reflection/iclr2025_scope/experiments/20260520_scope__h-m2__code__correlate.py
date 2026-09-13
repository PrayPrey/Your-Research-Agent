import numpy as np
from torch import Tensor
from scipy.stats import spearmanr
from config import ExperimentConfig


class SpearmanCorrelator:
    def __init__(self, config: ExperimentConfig):
        self.config = config

    def expand_kv_heads(self, cis_scores: Tensor) -> Tensor:
        """Expand (num_kv_heads, L) -> (num_query_heads, L) via repeat_interleave."""
        return cis_scores.repeat_interleave(self.config.kv_repeat, dim=0)  # (32, L)

    def _mask_padding(self, scores: Tensor, attention_mask: Tensor) -> Tensor:
        """Return scores[:, non_pad_indices] -> (num_heads, T)."""
        mask = attention_mask.squeeze(0).bool()  # (L,)
        return scores[:, mask]                    # (num_heads, T)

    def compute_per_layer_rho(
        self,
        lora_scores: Tensor,     # (32, L)
        cis_scores: Tensor,      # (8, L)
        attention_mask: Tensor,  # (1, L)
    ) -> np.ndarray:
        cis_expanded = self.expand_kv_heads(cis_scores)  # (32, L)

        lora_masked = self._mask_padding(lora_scores, attention_mask)   # (32, T)
        cis_masked = self._mask_padding(cis_expanded, attention_mask)   # (32, T)

        rhos = []
        for h in range(self.config.num_query_heads):
            lora_h = lora_masked[h].float().numpy()
            cis_h = cis_masked[h].float().numpy()
            if len(lora_h) < 3:
                rhos.append(0.0)
                continue
            rho, _ = spearmanr(lora_h, cis_h)
            rhos.append(float(rho) if not np.isnan(rho) else 0.0)
        return np.array(rhos)  # (32,)

    def compute_example_rho(
        self,
        lora_all_layers: list,   # list[32] of (32, L)
        cis_all_layers: list,    # list[32] of (8, L)
        attention_mask: Tensor,  # (1, L)
    ) -> tuple:
        per_layer_rho = []  # (32, 32) -> list of (32,)
        for layer_idx in range(self.config.num_layers):
            layer_rho = self.compute_per_layer_rho(
                lora_all_layers[layer_idx],
                cis_all_layers[layer_idx],
                attention_mask,
            )
            per_layer_rho.append(layer_rho)

        per_layer_rho_arr = np.array(per_layer_rho)  # (32, 32) [layers x heads]
        per_head_rho = per_layer_rho_arr.mean(axis=0)  # (32,) mean across layers
        mean_rho = float(per_head_rho.mean())
        return mean_rho, per_head_rho, per_layer_rho_arr

    def aggregate_results(
        self,
        per_example_rho: list,
        per_example_per_head: list,
        per_example_per_layer: list,
    ) -> dict:
        rho_arr = np.array(per_example_rho)
        head_arr = np.stack(per_example_per_head, axis=0)   # (N, 32)
        layer_arr = np.stack(per_example_per_layer, axis=0)  # (N, 32, 32)

        return {
            "mean_rho": float(rho_arr.mean()),
            "std_rho": float(rho_arr.std()),
            "per_head_mean": head_arr.mean(axis=0).tolist(),   # (32,)
            "per_layer_mean": layer_arr.mean(axis=0).tolist(), # (32, 32)
            "all_example_rhos": rho_arr.tolist(),
        }
