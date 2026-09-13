"""Timing benchmark for orbit-PE vs vanilla sequential-PE.

Measures wall-clock overhead per checkpoint using time.perf_counter().
"""
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import torch
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class CheckpointResult:
    checkpoint_id: str
    arch_family: str           # "cnn" | "transformer"
    t_vanilla: float           # seconds
    t_orbit: float             # seconds
    overhead_ratio: float      # t_orbit / max(t_vanilla, 1e-9)
    success: bool
    layer_types_seen: List[str]
    error: Optional[str] = None


def _time_vanilla(
    state_dict: Dict,
    baseline,
) -> float:
    """Return wall-clock seconds for sequential-PE on one checkpoint."""
    t0 = time.perf_counter()
    _ = baseline.forward(state_dict)
    return time.perf_counter() - t0


def _time_orbit(
    state_dict: Dict,
    orbit_computer,
    n_heads: int = 1,
) -> Tuple[float, bool, List[str]]:
    """Return (seconds, success, layer_types_seen) for orbit-PE on one checkpoint."""
    from orbit_pe_computer import compute_orbit_pe_all_layers
    from orbit_pe import _infer_type_from_name, SUPPORTED_LAYER_TYPES

    import logging as _logging
    layer_types_seen = []
    try:
        # Disable logging during timed region to match vanilla baseline (no logging in forward)
        _orbit_logger = _logging.getLogger("orbit_pe_computer")
        _prev_level = _orbit_logger.level
        _orbit_logger.setLevel(_logging.CRITICAL)
        t0 = time.perf_counter()
        _, success_flags = compute_orbit_pe_all_layers(state_dict, orbit_computer, n_heads)
        elapsed = time.perf_counter() - t0
        _orbit_logger.setLevel(_prev_level)

        for param_name, weight in state_dict.items():
            if not param_name.endswith(".weight") or weight.dim() < 2:
                continue
            lt = _infer_type_from_name(param_name, weight)
            if lt in SUPPORTED_LAYER_TYPES and lt not in layer_types_seen:
                layer_types_seen.append(lt)

        all_success = bool(success_flags) and all(success_flags.values())
        return elapsed, all_success, layer_types_seen
    except Exception as exc:
        return 0.0, False, layer_types_seen


def run_timing_benchmark(
    cnn_checkpoints: List[Dict],
    transformer_checkpoints: List[Dict],
    orbit_computer,
    baseline,
    cfg,
) -> List[CheckpointResult]:
    """Time vanilla-PE vs orbit-PE for each checkpoint.

    Returns List[CheckpointResult] length == len(cnn) + len(transformer).
    """
    results: List[CheckpointResult] = []

    all_checkpoints = [
        (ckpt, "cnn") for ckpt in cnn_checkpoints
    ] + [
        (ckpt, "transformer") for ckpt in transformer_checkpoints
    ]

    for ckpt_data, arch_family in tqdm(all_checkpoints, desc="Benchmarking"):
        ckpt_id = ckpt_data.get("checkpoint_id", "unknown")
        state_dict = ckpt_data.get("state_dict", {})

        try:
            t_vanilla = _time_vanilla(state_dict, baseline)
            t_orbit, success, layer_types = _time_orbit(state_dict, orbit_computer)
            overhead_ratio = t_orbit / max(t_vanilla, 1e-9)

            results.append(CheckpointResult(
                checkpoint_id=ckpt_id,
                arch_family=arch_family,
                t_vanilla=t_vanilla,
                t_orbit=t_orbit,
                overhead_ratio=overhead_ratio,
                success=success,
                layer_types_seen=layer_types,
                error=None,
            ))
        except Exception as exc:
            logger.warning("Benchmark failed for %s: %s", ckpt_id, exc)
            results.append(CheckpointResult(
                checkpoint_id=ckpt_id,
                arch_family=arch_family,
                t_vanilla=0.0,
                t_orbit=0.0,
                overhead_ratio=0.0,
                success=False,
                layer_types_seen=[],
                error=str(exc),
            ))

    return results
