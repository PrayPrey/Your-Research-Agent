# cmi.py - Convergence Monotonicity Index
import numpy as np


def compute_cmi(trajectory: np.ndarray) -> np.ndarray:
    """
    Compute CMI from trajectory array.

    trajectory: [N, num_layers] per-layer entropy values
    returns: [N] CMI scores (higher = more monotonic entropy decrease)

    CMI = negative mean of layer-to-layer entropy differences.
    Positive CMI indicates entropy decreases across layers (convergence).
    """
    if trajectory.ndim != 2:
        raise ValueError(f"Expected 2D trajectory, got {trajectory.ndim}D")

    # Layer-to-layer differences: [N, num_layers-1]
    diffs = np.diff(trajectory, axis=1)

    # CMI = negative mean diff (so higher = more decreasing trend)
    cmi = -np.mean(diffs, axis=1)

    # Handle edge cases
    cmi = np.nan_to_num(cmi, nan=0.0, posinf=0.0, neginf=0.0)

    return cmi
