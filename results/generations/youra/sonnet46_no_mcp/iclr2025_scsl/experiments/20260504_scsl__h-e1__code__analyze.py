import json
import os
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple

from config import ExperimentConfig


def compute_delta_series(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure delta column exists; recompute if needed."""
    df = df.copy()
    if "delta" not in df.columns:
        df["delta"] = df["spurious_acc"] - df["core_acc"]
    return df


def find_contiguous_window(
    delta_mean: np.ndarray,
    epochs: np.ndarray,
) -> Tuple[int, int, float]:
    """Find longest contiguous window where delta(t) > 0.
    Returns (start_epoch, end_epoch, window_fraction)."""
    total_epochs = int(epochs[-1]) if len(epochs) > 0 else 1
    best_start = 0
    best_end = 0
    best_len = 0
    cur_start = None

    for i, d in enumerate(delta_mean):
        if d > 0:
            if cur_start is None:
                cur_start = i
        else:
            if cur_start is not None:
                length = i - cur_start
                if length > best_len:
                    best_len = length
                    best_start = cur_start
                    best_end = i - 1
                cur_start = None

    if cur_start is not None:
        length = len(delta_mean) - cur_start
        if length > best_len:
            best_len = length
            best_start = cur_start
            best_end = len(delta_mean) - 1

    start_epoch = int(epochs[best_start]) if best_len > 0 else 0
    end_epoch = int(epochs[best_end]) if best_len > 0 else 0
    window_fraction = best_len / len(epochs) if len(epochs) > 0 else 0.0
    return start_epoch, end_epoch, window_fraction


def paired_ttest(delta_by_seed: np.ndarray) -> Tuple[float, float]:
    """Paired t-test: H0: mean(delta) <= 0 over contiguous window.
    delta_by_seed: (n_seeds, n_epochs) array of delta values in window.
    Returns (t_stat, p_value) one-sided."""
    seed_means = delta_by_seed.mean(axis=1)  # mean per seed over window
    t_stat, p_two = stats.ttest_1samp(seed_means, popmean=0.0)
    p_one = p_two / 2 if t_stat > 0 else 1.0
    return float(t_stat), float(p_one)


def find_t_star(delta_mean: np.ndarray, epochs: np.ndarray,
                threshold: float = 0.02, consecutive: int = 3) -> int:
    """Find first epoch where delta < threshold for `consecutive` checkpoints."""
    count = 0
    for i, d in enumerate(delta_mean):
        if d < threshold:
            count += 1
            if count >= consecutive:
                return int(epochs[i - consecutive + 1])
        else:
            count = 0
    return int(epochs[-1])


def evaluate_gate(
    window_fraction: float,
    p_value: float,
    cfg: ExperimentConfig,
) -> dict:
    gate_pass = (
        window_fraction >= cfg.gate.min_window_fraction
        and p_value < cfg.gate.p_threshold
    )
    decision = "PASS" if gate_pass else "FAIL"
    return {
        "pass": gate_pass,
        "window_fraction": window_fraction,
        "p_value": p_value,
        "gate": "MUST_WORK",
        "decision": decision,
        "criteria": {
            "min_window_fraction": cfg.gate.min_window_fraction,
            "p_threshold": cfg.gate.p_threshold,
        },
    }


def run_analysis(results_df: pd.DataFrame, cfg: ExperimentConfig) -> dict:
    """Orchestrate delta computation, window detection, t-test, gate, and JSON save."""
    results_df = compute_delta_series(results_df)
    seeds = sorted(results_df["seed"].unique())
    epochs_all = sorted(results_df["epoch"].unique())
    epochs_arr = np.array(epochs_all)

    # Mean delta across seeds per epoch
    delta_pivot = results_df.pivot_table(
        index="epoch", columns="seed", values="delta"
    ).reindex(epochs_arr)
    delta_matrix = delta_pivot.values  # (n_epochs, n_seeds)
    delta_mean = np.nanmean(delta_matrix, axis=1)

    start_ep, end_ep, window_fraction = find_contiguous_window(delta_mean, epochs_arr)

    # Extract window indices for t-test
    window_mask = (epochs_arr >= start_ep) & (epochs_arr <= end_ep)
    if window_mask.sum() > 0 and len(seeds) >= 2:
        delta_window = delta_matrix[window_mask, :].T  # (n_seeds, n_window)
        t_stat, p_value = paired_ttest(delta_window)
    else:
        t_stat, p_value = 0.0, 1.0

    gate_result = evaluate_gate(window_fraction, p_value, cfg)

    # Gap area per seed
    gap_areas = []
    per_seed_data = []
    t_stars = []
    for seed in seeds:
        df_s = results_df[results_df["seed"] == seed].sort_values("epoch")
        delta_s = df_s["delta"].values
        epochs_s = df_s["epoch"].values
        gap_area = float(np.sum(np.maximum(delta_s, 0)))
        gap_areas.append(gap_area)
        _, _, wf_s = find_contiguous_window(delta_s, epochs_s)
        t_star_s = find_t_star(
            delta_s, epochs_s,
            cfg.gate.t_star_delta_threshold,
            cfg.gate.t_star_consecutive,
        )
        t_stars.append(t_star_s)
        per_seed_data.append({
            "seed": int(seed),
            "window_fraction": float(wf_s),
            "gap_area": gap_area,
            "t_star": int(t_star_s),
            "delta_curve": [float(v) for v in delta_s],
            "spurious_curve": [float(v) for v in df_s["spurious_acc"].values],
            "core_curve": [float(v) for v in df_s["core_acc"].values],
            "epochs": [int(e) for e in epochs_s],
        })

    gap_mean = float(np.mean(gap_areas))
    n = len(gap_areas)
    gap_se = float(np.std(gap_areas, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
    t_ci = stats.t.ppf(0.975, df=max(n - 1, 1))
    gap_ci_low = gap_mean - t_ci * gap_se
    gap_ci_high = gap_mean + t_ci * gap_se

    output = {
        "hypothesis_id": "h-e1",
        "dataset": cfg.train.dataset,
        "gate_pass": gate_result["pass"],
        "window_fraction": window_fraction,
        "p_value": p_value,
        "t_stat": t_stat,
        "gap_area": {
            "mean": gap_mean,
            "ci_95_low": float(gap_ci_low),
            "ci_95_high": float(gap_ci_high),
        },
        "t_star_mean": float(np.mean(t_stars)),
        "t_star_std": float(np.std(t_stars)),
        "window_start_epoch": int(start_ep),
        "window_end_epoch": int(end_ep),
        "gate": gate_result,
        "per_seed": per_seed_data,
    }

    os.makedirs(cfg.results_dir, exist_ok=True)
    out_path = os.path.join(cfg.results_dir, "h-e1_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Analysis saved to {out_path}")
    print(f"Gate: {gate_result['decision']} | window={window_fraction:.3f} | p={p_value:.4f}")

    return output
