#!/usr/bin/env python
import os
import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="H-M1 Experiment Runner")
    parser.add_argument("--data-root", type=str, default="./data/waterbirds", help="Path to Waterbirds dataset")
    parser.add_argument("--results-dir", type=str, default="./outputs", help="Output directory")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size")
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4], help="Random seeds")
    parser.add_argument("--skip-train", action="store_true", help="Skip training, only evaluate")
    parser.add_argument("--device", type=str, default="cuda", help="Device")
    args = parser.parse_args()
    from config import Config, SEEDS
    import config
    config.SEEDS = args.seeds
    cfg = Config(
        data_root=args.data_root,
        results_dir=args.results_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
    )
    os.makedirs(cfg.results_dir, exist_ok=True)
    if not args.skip_train:
        print("=" * 60)
        print("Phase 1: Training")
        print("=" * 60)
        from train import train_one_seed
        import numpy as np
        all_results = []
        for seed in config.SEEDS:
            print(f"\n--- Training seed {seed} ---")
            result = train_one_seed(cfg, seed)
            all_results.append(result)
            with open(os.path.join(cfg.results_dir, f"seed_{seed}.json"), "w") as f:
                json.dump({"r_series": result["r_series"].tolist(), "sr_series": result["sr_series"].tolist()}, f)
        with open(os.path.join(cfg.results_dir, "all_seeds.json"), "w") as f:
            json.dump([{"seed": r["seed"], "r_series": r["r_series"].tolist(), "sr_series": r["sr_series"].tolist()} for r in all_results], f)
    print("\n" + "=" * 60)
    print("Phase 2: Evaluation")
    print("=" * 60)
    from evaluate import evaluate_all_seeds
    result = evaluate_all_seeds(cfg.results_dir)
    print(f"\nTau per seed: {result.get('tau_per_seed')}")
    print(f"Mean tau: {result.get('tau_mean'):.4f}")
    ci = result.get('tau_ci')
    print(f"95% CI: ({ci[0]:.4f}, {ci[1]:.4f})")
    gate_pass = result.get('gate_pass')
    print(f"\n{'='*30}")
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print(f"{'='*30}")
    with open(os.path.join(cfg.results_dir, "evaluation.json"), "w") as f:
        json.dump(result, f, indent=2)
    print("\n" + "=" * 60)
    print("Phase 3: Visualization")
    print("=" * 60)
    from visualize import plot_gate_metrics, plot_time_series, plot_tau_per_seed
    figures_dir = os.path.join(os.path.dirname(cfg.results_dir), "figures")
    os.makedirs(figures_dir, exist_ok=True)
    plot_gate_metrics(cfg.results_dir, os.path.join(figures_dir, "gate_metrics.png"))
    plot_time_series(cfg.results_dir, os.path.join(figures_dir, "time_series.png"))
    plot_tau_per_seed(cfg.results_dir, os.path.join(figures_dir, "tau_per_seed.png"))
    final_result = {
        "hypothesis_id": "h-m1",
        "gate_type": "MUST_WORK",
        "gate_pass": gate_pass,
        "tau_mean": result.get("tau_mean"),
        "tau_ci_low": ci[0],
        "tau_ci_high": ci[1],
        "tau_per_seed": result.get("tau_per_seed"),
        "epochs": cfg.epochs,
        "seeds": config.SEEDS,
    }
    with open(os.path.join(cfg.results_dir, "results.json"), "w") as f:
        json.dump(final_result, f, indent=2)
    print(f"\nResults saved to {cfg.results_dir}")
    print("EXPERIMENT COMPLETE")
    return 0 if gate_pass else 1

if __name__ == "__main__":
    sys.exit(main())
