"""
H-M2 Experiment: Variance Selection Reduces Zero-Gradient Groups in GRPO.
Runs two GRPO training conditions (variance-50 vs random-50) and evaluates
frac_reward_zero_std to test the hypothesis gate.
"""
import os
import sys
import json
import numpy as np
from pathlib import Path

# Run from project root so relative paths in config work
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # TEST_dl4c/
sys.path.insert(0, str(Path(__file__).parent))

from config import H_M2Config
from dataset import load_mbpp_subsets
from train import run_grpo
from analyze import extract_frac_zero_std, compute_gate_metrics, save_results
from visualize import generate_all_figures


def main(cfg: H_M2Config = None) -> None:
    if cfg is None:
        cfg = H_M2Config()

    # Change to project root so relative paths resolve
    os.chdir(PROJECT_ROOT)

    print("=" * 60)
    print("H-M2: Variance Selection Reduces Zero-Gradient Groups")
    print("=" * 60)

    # 1. Validate environment
    import trl
    import torch
    from packaging.version import Version
    assert Version(trl.__version__) >= Version(cfg.min_trl_version), (
        f"TRL >= {cfg.min_trl_version} required; got {trl.__version__}"
    )
    assert torch.cuda.is_available(), "CUDA required"
    assert Path(cfg.profiling_json).exists(), f"H-E1 JSON not found: {cfg.profiling_json}"
    print(f"[env] TRL {trl.__version__}, CUDA ok, H-E1 JSON ok")

    # 2. Load datasets
    variance_50_ds, random_50_ds, variance_50_ids, random_50_ids = load_mbpp_subsets(cfg)

    # 3. Train variance-50 condition
    var_output_dir = os.path.join(cfg.results_dir, "variance50")
    Path(var_output_dir).mkdir(parents=True, exist_ok=True)
    log_var = run_grpo(cfg, variance_50_ds, var_output_dir, "variance50")

    # 4. Train random-50 condition
    rnd_output_dir = os.path.join(cfg.results_dir, "random50")
    Path(rnd_output_dir).mkdir(parents=True, exist_ok=True)
    log_rnd = run_grpo(cfg, random_50_ds, rnd_output_dir, "random50")

    # 5. Extract frac_reward_zero_std
    frac_var = extract_frac_zero_std(log_var)
    frac_rnd = extract_frac_zero_std(log_rnd)
    print(f"[analyze] frac_zero_std steps extracted: variance={len(frac_var)}, random={len(frac_rnd)}")

    # 6. Compute gate metrics
    gate_metrics = compute_gate_metrics(frac_var, frac_rnd, cfg.gate_checkpoints)

    # 7. Save results
    save_results(cfg, gate_metrics, frac_var, frac_rnd, variance_50_ids, random_50_ids)

    # 8. Generate figures
    generate_all_figures(cfg, gate_metrics, frac_var, frac_rnd, log_var, log_rnd)

    # 9. Report gate result
    print("\n" + "=" * 60)
    print("GATE RESULTS")
    print("=" * 60)
    for N in cfg.gate_checkpoints:
        ck = gate_metrics[f"checkpoint_{N}"]
        status = "PASS" if ck["gate_pass"] else "FAIL"
        print(f"  Step {N:2d}: var={ck['mean_frac_var']:.4f} rnd={ck['mean_frac_rnd']:.4f} "
              f"gap={ck['gap_pp']:.4f} [{status}]")

    primary = gate_metrics["primary_gate_pass"]
    secondary = gate_metrics["secondary_gate_pass"]
    print(f"\nPrimary gate (all checkpoints): {'PASS' if primary else 'FAIL'}")
    print(f"Secondary gate (gap>=5pp@10):   {'PASS' if secondary else 'FAIL'}")

    gap_at_10 = gate_metrics["checkpoint_10"]["gap_pp"]
    assert gap_at_10 > 0, (
        f"H-M2 FAIL: variance-50 not lower frac_zero_std at step 10 (gap={gap_at_10:.4f})"
    )

    print("\nEXPERIMENT COMPLETE")
    return gate_metrics


if __name__ == "__main__":
    gate = main()
    sys.exit(0 if gate["primary_gate_pass"] else 1)
