"""run_experiment.py — Main experiment orchestrator for H-E1"""
import json
import sys
from pathlib import Path

import yaml

from analyze import bootstrap_ci, compute_deltas, load_results_as_arrays, make_figures, print_gate_decision
from evaluate import run_all
from train_rlef import train as train_rlef
from train_sft import train as train_sft


def main(config_path: str = "config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    # Setup directories
    for key in ["checkpoints_dir", "results_dir", "logs_dir"]:
        Path(cfg["paths"][key]).mkdir(parents=True, exist_ok=True)
    Path(cfg["paths"]["figures_dir"]).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)

    sft_dir = f"{cfg['paths']['checkpoints_dir']}/sft_baseline"
    rlef_dir = f"{cfg['paths']['checkpoints_dir']}/rlef_fraction"

    # Phase 1: SFT
    if not (Path(sft_dir) / "config.json").exists():
        print("\n" + "=" * 60)
        print("PHASE 1: SFT Training")
        print("=" * 60)
        train_sft(cfg)
    else:
        print(f"✓ SFT checkpoint exists: {sft_dir}")

    # Phase 2: RLEF-Fraction
    if not (Path(rlef_dir) / "config.json").exists():
        print("\n" + "=" * 60)
        print("PHASE 2: RLEF-Fraction Training")
        print("=" * 60)
        train_rlef(cfg)
    else:
        print(f"✓ RLEF checkpoint exists: {rlef_dir}")

    # Phase 3: Evaluation
    print("\n" + "=" * 60)
    print("PHASE 3: Evaluation")
    print("=" * 60)
    run_all(sft_dir, rlef_dir, cfg["paths"]["results_dir"])

    # Phase 4: Analysis
    print("\n" + "=" * 60)
    print("PHASE 4: Analysis")
    print("=" * 60)
    tasks = ["humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"]
    rlef_res, sft_res = load_results_as_arrays(cfg["paths"]["results_dir"], tasks)
    deltas = compute_deltas(rlef_res, sft_res)
    boot = bootstrap_ci(
        rlef_res, sft_res,
        n_boot=cfg["bootstrap"]["n_boot"],
        seed=cfg["bootstrap"]["seed"],
        ci_level=cfg["bootstrap"]["ci_level"],
        gate_ratio=cfg["bootstrap"]["gate_ratio"],
    )
    make_figures(rlef_res, sft_res, deltas, boot,
                 reward_log_path=cfg["logging"]["reward_monitoring"],
                 figures_dir=cfg["paths"]["figures_dir"])
    gate_pass = print_gate_decision(deltas, boot)

    output = {
        "deltas": {k: v for k, v in deltas.items() if k != "ratios"},
        "bootstrap": {k: v for k, v in boot.items() if k != "ratios"},
        "gate_pass": gate_pass,
    }
    results_json = Path(cfg["paths"]["results_dir"]) / "experiment_results.json"
    with open(results_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✓ Experiment complete. Results: {results_json}")
    return gate_pass


if __name__ == "__main__":
    cfg = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    ok = main(cfg)
    sys.exit(0 if ok else 1)
