"""
VarianceDecomposer for H-M2: decomposes trajectory variance into Var_perm and Var_GL.
Uses OrbitProjector to project checkpoint weights onto orbit-aligned subspaces.
"""
from typing import Dict, List, Tuple
import torch
import numpy as np
from torch import Tensor

from orbit_projector import OrbitProjector


class VarianceDecomposer:
    """Decomposes trajectory variance into Var_perm and Var_GL components."""

    def __init__(self, orbit_projector: OrbitProjector, eps: float = 1e-8):
        self.projector = orbit_projector
        self.eps = eps

    def compute_trajectory_variance_ratio(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, float]:
        """Compute Var_perm / (Var_perm + Var_GL) for one model trajectory.

        trajectory: list of T state_dicts, T >= min_checkpoints
        Returns: {ratio, var_perm, var_gl, n_checkpoints}
        """
        if not trajectory:
            return {"ratio": 0.0, "var_perm": 0.0, "var_gl": 0.0, "n_checkpoints": 0}

        # Compute orbit basis from first checkpoint (reference frame)
        orbit_basis = self.projector.get_orbit_basis(trajectory[0])  # [D, P]

        var_perm_total = 0.0
        var_gl_total = 0.0
        weight_names = self.projector.get_supported_weight_names(trajectory[0])

        for state_dict in trajectory:
            # Permutation orbit variance
            W_flat = self.projector.flatten_weights(state_dict)  # [P]
            _, var_perm_t = self.projector.compute_perm_orbit_projection(W_flat, orbit_basis)
            var_perm_total += var_perm_t

            # GL orbit variance: sum over supported layers
            for name in weight_names:
                if name not in state_dict:
                    continue
                weight = state_dict[name]
                layer_type = "Conv2d" if weight.dim() == 4 else "Linear"
                if self.projector._h_m1_available:
                    try:
                        layer_type = self.projector._infer_type_from_name(name, weight)
                    except Exception:
                        pass
                var_gl_total += self.projector.compute_gl_orbit_projection_layer(
                    weight, layer_type
                )

        ratio = var_perm_total / (var_perm_total + var_gl_total + self.eps)
        return {
            "ratio": float(ratio),
            "var_perm": float(var_perm_total),
            "var_gl": float(var_gl_total),
            "n_checkpoints": len(trajectory),
        }

    def compute_epoch_ratios(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> List[float]:
        """Per-epoch ratio: ratio at each checkpoint vs reference (epoch 0).
        Returns list of T floats.
        """
        if not trajectory:
            return []

        orbit_basis = self.projector.get_orbit_basis(trajectory[0])
        weight_names = self.projector.get_supported_weight_names(trajectory[0])
        ratios = []

        for state_dict in trajectory:
            W_flat = self.projector.flatten_weights(state_dict)
            _, var_perm_t = self.projector.compute_perm_orbit_projection(W_flat, orbit_basis)

            var_gl_t = 0.0
            for name in weight_names:
                if name not in state_dict:
                    continue
                weight = state_dict[name]
                layer_type = "Conv2d" if weight.dim() == 4 else "Linear"
                if self.projector._h_m1_available:
                    try:
                        layer_type = self.projector._infer_type_from_name(name, weight)
                    except Exception:
                        pass
                var_gl_t += self.projector.compute_gl_orbit_projection_layer(weight, layer_type)

            ratio_t = var_perm_t / (var_perm_t + var_gl_t + self.eps)
            ratios.append(float(ratio_t))

        return ratios

    def compute_layer_breakdown(
        self, trajectory: List[Dict[str, Tensor]]
    ) -> Dict[str, Dict[str, float]]:
        """Per-layer-type (Conv2d vs Linear) Var_perm and Var_GL breakdown.
        Returns: {'Conv2d': {var_perm, var_gl, ratio}, 'Linear': {...}}
        """
        if not trajectory:
            return {}

        weight_names = self.projector.get_supported_weight_names(trajectory[0])
        layer_types_seen = set()
        for name in weight_names:
            weight = trajectory[0][name]
            ltype = "Conv2d" if weight.dim() == 4 else "Linear"
            layer_types_seen.add(ltype)

        # Per-layer-type accumulators
        layer_stats: Dict[str, Dict[str, float]] = {
            lt: {"var_perm": 0.0, "var_gl": 0.0} for lt in layer_types_seen
        }

        orbit_basis = self.projector.get_orbit_basis(trajectory[0])

        for state_dict in trajectory:
            for name in weight_names:
                if name not in state_dict:
                    continue
                weight = state_dict[name].float()
                ltype = "Conv2d" if weight.dim() == 4 else "Linear"

                # Permutation variance for this layer only
                layer_flat = weight.flatten()
                # Build single-layer basis (project full basis onto this layer's dimensions)
                # Approximate: use the layer's contribution to W_flat
                W_full = self.projector.flatten_weights(state_dict)
                names_all = self.projector.get_supported_weight_names(state_dict)

                layer_offset = 0
                for n in names_all:
                    if n == name:
                        break
                    layer_offset += state_dict[n].numel()
                layer_size = weight.numel()

                if orbit_basis.shape[1] > layer_offset + layer_size:
                    sub_basis = orbit_basis[:, layer_offset:layer_offset + layer_size]
                    sub_basis_norm = torch.linalg.norm(sub_basis, dim=1, keepdim=True)
                    sub_basis_norm = torch.where(sub_basis_norm < self.eps,
                                                 torch.ones_like(sub_basis_norm),
                                                 sub_basis_norm)
                    sub_basis = sub_basis / sub_basis_norm
                    proj = sub_basis @ layer_flat
                    var_perm_layer = float((proj ** 2).sum().item())
                else:
                    var_perm_layer = 0.0

                var_gl_layer = self.projector.compute_gl_orbit_projection_layer(weight, ltype)

                layer_stats[ltype]["var_perm"] += var_perm_layer
                layer_stats[ltype]["var_gl"] += var_gl_layer

        # Compute ratios
        for ltype in layer_stats:
            vp = layer_stats[ltype]["var_perm"]
            vg = layer_stats[ltype]["var_gl"]
            layer_stats[ltype]["ratio"] = vp / (vp + vg + self.eps)

        return layer_stats


def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict[str, bool]]:
    """Check mechanism activation indicators. Fail-fast if any False.

    Checks:
      - n_trajectories > 100
      - orbit_basis_dim > 0
      - 0.0 <= var_ratio <= 1.0
      - var_perm > 0 and var_gl > 0

    Returns: (all_pass bool, {indicator_name: bool})
    """
    indicators = {}

    n_traj = results.get("n_models", results.get("n_trajectories", 0))
    indicators["n_trajectories_gt_100"] = n_traj > 100

    orbit_basis_dim = results.get("orbit_basis_dim", results.get("D", 0))
    indicators["orbit_basis_dim_gt_0"] = orbit_basis_dim > 0

    ratio = results.get("ratio_mean", results.get("ratio", -1.0))
    indicators["var_ratio_in_range"] = 0.0 <= ratio <= 1.0

    var_perm = results.get("var_perm_mean", results.get("var_perm", -1.0))
    var_gl = results.get("var_gl_mean", results.get("var_gl", -1.0))
    indicators["var_perm_positive"] = var_perm > 0
    indicators["var_gl_positive"] = var_gl > 0

    all_pass = all(indicators.values())
    for name, val in indicators.items():
        status = "✓" if val else "✗"
        print(f"  {status} {name}: {val}")

    if not all_pass:
        failed = [k for k, v in indicators.items() if not v]
        print(f"  ❌ Failed indicators: {failed}")

    return all_pass, indicators
