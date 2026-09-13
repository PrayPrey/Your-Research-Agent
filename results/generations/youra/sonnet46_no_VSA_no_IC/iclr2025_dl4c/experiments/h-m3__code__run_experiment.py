"""
H-M3 Experiment: Proxy Temporal Stability.
Warm-start GRPO (200 steps, lr=1e-6, max_completion_length=1024).
Tests whether variance-50 gap over random-50 persists across training steps.
"""
import os
import sys
import json
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]  # TEST_dl4c/
sys.path.insert(0, str(Path(__file__).parent))

from config import H_M3Config
from dataset import load_mbpp_subsets
from train import run_grpo
from analyze import (
    extract_frac_zero_std,
    extract_log_steps,
    compute_gate_metrics,
    compute_gap_trajectory,
    verify_warm_start_succeeded,
    save_results,
)
from visualize import generate_all_figures


def _validate_env(cfg: H_M3Config) -> None:
    """Validate TRL version, CUDA, H-E1 JSON presence. Raises on failure."""
    import importlib.metadata
    import torch
    from packaging.version import Version

    trl_version = importlib.metadata.version("trl")
    if Version(trl_version) < Version(cfg.min_trl_version):
        raise RuntimeError(f"TRL {trl_version} < required {cfg.min_trl_version}")
    print(f"[H-M3] TRL version: {trl_version} ok")

    if not torch.cuda.is_available():
        print("[H-M3] WARNING: CUDA not available — training will be very slow")
    else:
        print(f"[H-M3] CUDA: {torch.cuda.get_device_name(0)} ok")

    if not os.path.exists(cfg.profiling_json):
        raise FileNotFoundError(
            f"H-E1 profiling JSON not found: {cfg.profiling_json}\n"
            "Run H-E1 experiment first."
        )
    print(f"[H-M3] H-E1 JSON: {cfg.profiling_json} ok")

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)


def _handle_cold_start_explore(
    cfg: H_M3Config,
    log_var: list,
    log_rnd: list,
    warm_stats: dict,
    variance_50_ids: list,
    random_50_ids: list,
) -> None:
    """Save EXPLORE JSON with gap=None fields and print diagnostic."""
    print("[H-M3] EXPLORE: Warm-start failed — cold-start persists.")
    print(f"  max_reward_var50: {warm_stats['max_reward_var50']:.4f}")
    print(f"  max_reward_rnd50: {warm_stats['max_reward_rnd50']:.4f}")
    print("  Proxy temporal stability cannot be tested in cold-start regime.")
    print("  Recommendation: try warmer model or online selection for H-M4.")

    explore_results = {
        "hypothesis": "H-M3",
        "warm_start_succeeded": False,
        "gate_passed": False,
        "p1_pass": False,
        "p2_pass": False,
        "gap_by_checkpoint": {"10": None, "20": None, "50": None},
        "gap_retention": None,
        "max_rewards": warm_stats,
        "explore_finding": "cold_start_persists",
        "config": {
            "max_steps": cfg.max_steps,
            "learning_rate": cfg.learning_rate,
            "max_completion_length": cfg.max_completion_length,
            "num_generations": cfg.num_generations,
            "seed": cfg.seed,
        },
        "variance_50_ids": variance_50_ids,
        "random_50_ids": random_50_ids,
    }
    os.makedirs(cfg.results_dir, exist_ok=True)
    with open(f"{cfg.results_dir}/gate_results.json", "w") as f:
        json.dump(explore_results, f, indent=2)
    print(f"[H-M3] EXPLORE results saved: {cfg.results_dir}/gate_results.json")


def _print_gate_report(
    warm_start_ok: bool,
    p1_pass: bool,
    p2_pass: bool,
    gap_at_10: float,
    gap_at_20: float,
    gap_at_50: float,
    gap_retention: float,
) -> None:
    """Print structured gate report to stdout."""
    print("=" * 60)
    print("[H-M3] GATE REPORT")
    print("=" * 60)
    print(f"  Warm-start:              {'PASS' if warm_start_ok else 'FAIL (cold-start)'}")
    print(f"  P1 (gap>0 at 10,20,50): {'PASS' if p1_pass else 'FAIL'}")
    print(f"    gap_at_10 = {gap_at_10:.4f}")
    print(f"    gap_at_20 = {gap_at_20:.4f}")
    print(f"    gap_at_50 = {gap_at_50:.4f}")
    print(f"  P2 (retention>=0.5):    {'PASS' if p2_pass else 'FAIL'}")
    print(f"    gap_retention = {gap_retention:.4f} (threshold: 0.5)")
    print(f"  Gate: {'PASSED' if p1_pass else 'FAILED/EXPLORE'}")
    print("=" * 60)


def main(cfg: H_M3Config = None) -> dict:
    """
    Orchestrate warm-start GRPO experiment.
    Returns gate results dict (same schema as gate_results.json).
    sys.exit(1) if warm-start fails or gate fails.
    """
    if cfg is None:
        cfg = H_M3Config()

    # Change to project root so relative paths resolve
    os.chdir(PROJECT_ROOT)

    print("=" * 60)
    print("H-M3: Proxy Temporal Stability (Warm-Start GRPO)")
    print("=" * 60)

    # 1. Environment validation
    _validate_env(cfg)

    # 2. Load datasets
    variance_50_ds, random_50_ds, variance_50_ids, random_50_ids = load_mbpp_subsets(cfg)

    # 3. Run Condition A (variance-50)
    print("[H-M3] Training Condition A: variance-50 (warm-start)")
    var_output_dir = os.path.join(cfg.results_dir, "variance50")
    Path(var_output_dir).mkdir(parents=True, exist_ok=True)
    log_var, early_stopped_var = run_grpo(cfg, variance_50_ds, var_output_dir, "variance50")

    # 4. Run Condition B (random-50)
    print("[H-M3] Training Condition B: random-50 (warm-start)")
    rnd_output_dir = os.path.join(cfg.results_dir, "random50")
    Path(rnd_output_dir).mkdir(parents=True, exist_ok=True)
    log_rnd, early_stopped_rnd = run_grpo(cfg, random_50_ds, rnd_output_dir, "random50")

    # 5. Warm-start validation
    warm_start_ok, warm_stats = verify_warm_start_succeeded(log_var, log_rnd)
    if not warm_start_ok:
        _handle_cold_start_explore(
            cfg, log_var, log_rnd, warm_stats, variance_50_ids, random_50_ids
        )
        sys.exit(1)

    # 6. Extract frac_zero_std series
    frac_var = extract_frac_zero_std(log_var)
    frac_rnd = extract_frac_zero_std(log_rnd)
    log_steps_var = extract_log_steps(log_var)
    log_steps_rnd = extract_log_steps(log_rnd)
    print(f"[analyze] frac_zero_std steps: variance={len(frac_var)}, random={len(frac_rnd)}")

    # Use shorter series if runs differ (early-stop case)
    n = min(len(frac_var), len(frac_rnd))
    log_steps = log_steps_var[:n]
    frac_var = frac_var[:n]
    frac_rnd = frac_rnd[:n]

    # 7. Gap trajectory analysis
    gap_by_step, gap_at_10, gap_at_20, gap_at_50, gap_retention = compute_gap_trajectory(
        frac_var, frac_rnd, log_steps
    )

    # 8. Gate evaluation
    gate_metrics = compute_gate_metrics(frac_var, frac_rnd, cfg.gate_checkpoints)
    p1_pass = gap_at_10 > 0 and gap_at_20 > 0 and gap_at_50 > 0
    p2_pass = gap_retention >= 0.5 if gap_at_10 > 0 else False
    gate_passed = p1_pass

    # 9. Save results
    save_results(
        cfg, warm_start_ok, gap_by_step, gap_at_10, gap_at_20, gap_at_50,
        gap_retention, frac_var, frac_rnd, variance_50_ids, random_50_ids,
        gate_passed, p1_pass, p2_pass, warm_stats,
    )

    # 10. Generate figures
    generate_all_figures(
        cfg, gate_metrics, gap_by_step, gap_at_10, gap_at_20, gap_at_50,
        gap_retention, frac_var, frac_rnd, log_var, log_rnd,
    )

    # 11. Print gate report
    _print_gate_report(warm_start_ok, p1_pass, p2_pass, gap_at_10, gap_at_20, gap_at_50, gap_retention)

    return {
        "gate_passed": gate_passed,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "gap_retention": gap_retention,
        "warm_start_ok": warm_start_ok,
        "gap_at_10": gap_at_10,
        "gap_at_20": gap_at_20,
        "gap_at_50": gap_at_50,
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("gate_passed") else 1)
