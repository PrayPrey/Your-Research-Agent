"""Load H-E1 domain exposure fractions and benchmark eval results."""
from __future__ import annotations
import json
import logging
import math
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def load_h_e1_trajectories(
    h_e1_dir: str | Path,
    model_sizes: list[str],
    checkpoint_steps: list[int],
    pile_domains: list[str],
) -> dict[str, np.ndarray]:
    """
    Load H-E1 cumulative domain fraction trajectories.

    Returns dict: model_size -> ndarray shape (n_domains, n_checkpoints)
    Missing models get None (caller must handle).
    """
    h_e1_dir = Path(h_e1_dir)
    outputs_dir = h_e1_dir / "code" / "outputs"

    trajectories: dict[str, np.ndarray | None] = {}
    for size in model_sizes:
        npy_path = outputs_dir / f"trajectories_{size}.npy"
        if npy_path.exists():
            arr = np.load(npy_path)
            log.info(f"Loaded H-E1 trajectories for {size}: shape={arr.shape}")
            trajectories[size] = arr
        else:
            log.warning(f"H-E1 trajectories missing for {size}: {npy_path}")
            trajectories[size] = None

    available = [s for s, v in trajectories.items() if v is not None]
    log.info(f"H-E1 available model sizes: {available} ({len(available)}/{len(model_sizes)})")
    return trajectories


def load_eval_cache(
    eval_cache_dir: str | Path,
    model_sizes: list[str],
    checkpoint_steps: list[int],
    tasks: dict[str, dict],
) -> dict[str, dict[int, dict[str, float]]]:
    """
    Load benchmark eval results from cache JSON files.

    Returns: model_size -> {step -> {task -> score}}
    """
    eval_cache_dir = Path(eval_cache_dir)
    results: dict[str, dict[int, dict[str, float]]] = {}

    for size in model_sizes:
        size_dir = eval_cache_dir / size
        results[size] = {}
        if not size_dir.exists():
            continue
        for step in checkpoint_steps:
            json_path = size_dir / f"step{step:07d}.json"
            if json_path.exists():
                try:
                    data = json.loads(json_path.read_text())
                    scores = data.get("scores", {})
                    results[size][step] = {t: scores[t] for t in tasks if t in scores}
                except Exception as e:
                    log.warning(f"Failed to load {json_path}: {e}")

        n = len(results[size])
        log.info(f"Eval cache for {size}: {n} checkpoints loaded")

    return results


def build_panel_dataframe(
    trajectories: dict[str, np.ndarray | None],
    eval_results: dict[str, dict[int, dict[str, float]]],
    checkpoint_steps: list[int],
    pile_domains: list[str],
    tasks: dict[str, dict],
    model_params: dict[str, int],
    floor_threshold: float = 0.20,
    min_valid_checkpoints: int = 100,
) -> pd.DataFrame:
    """
    Build MultiIndex (model_size, checkpoint) panel DataFrame.

    Columns: 22 domain fractions + 4 benchmark scores + log_params.
    Applies floor filter: drop checkpoints where ALL benchmark scores < floor_threshold.
    """
    rows = []
    benchmarks = list(tasks.keys())

    for size, traj in trajectories.items():
        if traj is None:
            log.warning(f"Skipping {size}: no H-E1 trajectory")
            continue
        eval_for_size = eval_results.get(size, {})
        if not eval_for_size:
            log.warning(f"Skipping {size}: no eval cache")
            continue

        # traj shape: (n_domains, n_checkpoints) — align with checkpoint_steps
        n_domains, n_ckpts = traj.shape
        n_steps = min(n_ckpts, len(checkpoint_steps))

        log_params = math.log10(model_params.get(size, 1))
        valid_count = 0

        for t_idx, step in enumerate(checkpoint_steps[:n_steps]):
            scores = eval_for_size.get(step)
            if scores is None or not all(b in scores for b in benchmarks):
                continue
            # Floor filter: skip if all benchmarks below floor
            if all(scores[b] < floor_threshold for b in benchmarks):
                continue

            row = {
                "model_size": size,
                "checkpoint": step,
                "log_params": log_params,
            }
            for d_idx, domain in enumerate(pile_domains[:n_domains]):
                row[domain] = float(traj[d_idx, t_idx])
            for bench in benchmarks:
                row[bench] = float(scores[bench])

            rows.append(row)
            valid_count += 1

        if valid_count < min_valid_checkpoints:
            log.warning(f"{size}: only {valid_count} valid checkpoints (min={min_valid_checkpoints})")
        else:
            log.info(f"{size}: {valid_count} valid checkpoints")

    if not rows:
        raise ValueError("Panel is empty — no valid (model_size, checkpoint) observations")

    df = pd.DataFrame(rows)
    df = df.set_index(["model_size", "checkpoint"])
    df.index.names = ["model_size", "checkpoint"]
    log.info(f"Panel shape: {df.shape} ({len(df)} obs, {df.index.get_level_values('model_size').nunique()} entities)")
    return df


def verify_books3_variance(
    panel_df: pd.DataFrame,
    books3_col: str = "Books3",
    threshold: float = 1e-6,
) -> float:
    """Check Books3 within-entity variance. Raises if insufficient (H-M2 root cause)."""
    if books3_col not in panel_df.columns:
        raise ValueError(f"'{books3_col}' column not in panel_df")

    within_var = (
        panel_df[books3_col]
        .groupby(level="model_size")
        .transform(lambda x: x - x.mean())
        .var()
    )
    if within_var < threshold:
        raise ValueError(
            f"Books3 within-variation {within_var:.2e} < {threshold} — "
            "load full H-E1 output, not 600k-doc subsample (H-M2 root cause)"
        )
    log.info(f"Books3 within-variation check passed: {within_var:.4e}")
    return float(within_var)


if __name__ == "__main__":
    # quick self-check
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import PILE_DOMAINS, CHECKPOINT_STEPS, MODEL_SIZES, MODEL_PARAMS, TASKS, H_E1_EXPOSURE_DIR, EVAL_CACHE_DIR

    logging.basicConfig(level=logging.INFO)
    traj = load_h_e1_trajectories(H_E1_EXPOSURE_DIR, MODEL_SIZES, CHECKPOINT_STEPS, PILE_DOMAINS)
    available = [s for s, v in traj.items() if v is not None]
    assert len(available) > 0, "No H-E1 trajectories found"
    print(f"PASS: data_loader self-check — {len(available)} models available")
