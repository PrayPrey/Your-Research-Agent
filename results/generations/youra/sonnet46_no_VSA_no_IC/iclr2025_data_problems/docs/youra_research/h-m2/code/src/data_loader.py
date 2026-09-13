"""Load H-E1 domain exposure arrays and apply floor filtering."""
from __future__ import annotations
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def load_exposure_arrays(model_size: str, base_dir: str = config.H_E1_EXPOSURE_DIR) -> np.ndarray:
    """Load H-E1 output for one model size. Returns (154, 22) float64."""
    path = Path(base_dir) / "code" / "outputs" / f"trajectories_{model_size}.npy"
    arr = np.load(path)  # shape (22, 154)
    return arr.T  # transpose to (154, 22) — checkpoints x domains


def align_checkpoint_indices(
    exposure: np.ndarray,
    eval_steps: list[int],
    reference_steps: list[int] = None,
) -> np.ndarray:
    """Reindex exposure rows to match eval_steps. Returns (T, 22)."""
    if reference_steps is None:
        reference_steps = config.CHECKPOINT_STEPS
    step_to_idx = {s: i for i, s in enumerate(reference_steps)}
    indices = [step_to_idx[s] for s in eval_steps if s in step_to_idx]
    return exposure[indices]


def verify_coverage(exposure: np.ndarray, model_size: str) -> None:
    """Assert shape (154, 22), finite, domain count matches."""
    assert exposure.shape == (154, 22), f"{model_size}: expected (154,22), got {exposure.shape}"
    assert np.all(np.isfinite(exposure)), f"{model_size}: non-finite values in exposure"
    assert exposure.shape[1] == len(config.PILE_DOMAINS), (
        f"{model_size}: domain count mismatch: {exposure.shape[1]} vs {len(config.PILE_DOMAINS)}"
    )


def apply_floor_filter(
    exposure: np.ndarray,
    scores: dict[str, np.ndarray],
    threshold: float = config.FLOOR_THRESHOLD,
    min_valid: int = config.MIN_VALID_CHECKPOINTS,
) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    """Filter checkpoints below floor threshold on any benchmark.
    Returns (exposure_filtered, scores_filtered, valid_mask)."""
    valid_mask = np.ones(exposure.shape[0], dtype=bool)
    for task_scores in scores.values():
        valid_mask &= (task_scores >= threshold)
    T_valid = valid_mask.sum()
    if T_valid < min_valid:
        raise ValueError(f"Floor filter left only {T_valid} checkpoints (min={min_valid})")
    return (
        exposure[valid_mask],
        {k: v[valid_mask] for k, v in scores.items()},
        valid_mask,
    )
