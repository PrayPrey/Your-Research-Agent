#!/usr/bin/env python3
"""H-M3 Experiment: Alpha sweep for helpfulness maintenance.

Tests whether multi-objective RLHF maintains ≥95% of baseline AlpacaEval.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from config import ExperimentConfig, ALPHA_SWEEP_CONFIGS
from alpha_sweep import run_sweep, verify_gate, save_results
from visualize_m3 import generate_all_figures


def main():
    parser = argparse.ArgumentParser(description="H-M3: Alpha Sweep Experiment")
    parser.add_argument("--output_dir", type=str, default="outputs",
                        help="Output directory")
    parser.add_argument("--ppo_steps", type=int, default=100,
                        help="PPO training steps (100=PoC, 1000=full)")
    parser.add_argument("--alpaca_prompts", type=int, default=100,
                        help="AlpacaEval prompts (100=PoC, 805=full)")
    parser.add_argument("--poc", action="store_true",
                        help="PoC mode: 100 steps, 100 prompts")
    parser.add_argument("--full", action="store_true",
                        help="Full mode: 1000 steps, 805 prompts")
    args = parser.parse_args()

    if args.poc:
        args.ppo_steps = 100
        args.alpaca_prompts = 100
    elif args.full:
        args.ppo_steps = 1000
        args.alpaca_prompts = 805

    print("=" * 60)
    print(f"H-M3 Alpha Sweep Experiment")
    print(f"PPO Steps: {args.ppo_steps}, AlpacaEval Prompts: {args.alpaca_prompts}")
    print("=" * 60)

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    base_cfg = ExperimentConfig()
    base_cfg.ppo.total_steps = args.ppo_steps

    results = run_sweep(
        ALPHA_SWEEP_CONFIGS,
        base_cfg,
        args.output_dir,
        args.alpaca_prompts,
    )

    gate_passed = verify_gate(results)

    results_file = out_path / "experiment_results.json"
    save_results(results, str(results_file))

    figures_dir = out_path / "figures"
    generate_all_figures(results, str(figures_dir))

    summary = {
        "timestamp": datetime.now().isoformat(),
        "ppo_steps": args.ppo_steps,
        "alpaca_prompts": args.alpaca_prompts,
        "gate_passed": gate_passed,
        "b2_alpaca_lc": results.get("B2", {}).get("alpaca_lc", 0),
        "best_t_name": max(
            [k for k in results if k != "B2"],
            key=lambda k: results.get(k, {}).get("alpaca_lc", 0),
            default="N/A"
        ),
        "best_t_alpaca_lc": max(
            [results.get(k, {}).get("alpaca_lc", 0) for k in results if k != "B2"],
            default=0
        ),
    }

    with open(out_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print(f"Gate: {'PASS' if gate_passed else 'FAIL'}")
    print(f"B2: {summary['b2_alpaca_lc']:.4f}")
    print(f"Best T*: {summary['best_t_name']} = {summary['best_t_alpaca_lc']:.4f}")
    print(f"Results: {results_file}")
    print(f"Figures: {figures_dir}/")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit(main())
