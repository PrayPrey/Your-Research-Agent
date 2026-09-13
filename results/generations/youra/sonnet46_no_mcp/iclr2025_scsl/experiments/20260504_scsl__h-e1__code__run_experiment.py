"""
run_experiment.py — Top-level orchestration for H-E1 Checkpoint Linear Probe Battery.

Usage:
    python run_experiment.py --config configs/waterbirds.yaml --device cuda:0
    python run_experiment.py --config configs/celeba.yaml --device cuda:0
"""
import argparse
import os
import sys
import json
import pandas as pd

from config import load_config
import train as train_module
import probe as probe_module
import analyze as analyze_module
import visualize as visualize_module


def main(config_path: str, device: str, skip_train: bool = False) -> dict:
    print(f"\n{'='*60}")
    print(f"H-E1: Checkpoint Linear Probe Battery Experiment")
    print(f"Config: {config_path}")
    print(f"Device: {device}")
    print(f"{'='*60}\n")

    cfg = load_config(config_path)

    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    def resolve(p):
        return p if os.path.isabs(p) else os.path.join(script_dir, p)

    cfg.train.data_root = resolve(cfg.train.data_root)
    cfg.train.checkpoint_dir = resolve(cfg.train.checkpoint_dir)
    cfg.results_dir = resolve(cfg.results_dir)

    os.makedirs(cfg.train.checkpoint_dir, exist_ok=True)
    os.makedirs(cfg.results_dir, exist_ok=True)

    # Step 1: ERM Training
    if not skip_train:
        print("Step 1: ERM Training")
        train_module.main(cfg.train, device)
    else:
        print("Step 1: Skipping training (--skip-train)")

    # Step 2: Probe Battery
    print("\nStep 2: Running Checkpoint Linear Probe Battery")
    results_df = probe_module.run_all_seeds(cfg, device)

    # Save raw results
    csv_path = os.path.join(cfg.results_dir, "results.csv")
    results_df.to_csv(csv_path, index=False)
    print(f"Raw results saved to {csv_path}")

    # Step 3: Statistical Analysis + Gate Evaluation
    print("\nStep 3: Statistical Analysis")
    analysis = analyze_module.run_analysis(results_df, cfg)

    # Step 4: Visualization
    print("\nStep 4: Generating Figures")
    figures_dir = os.path.join(os.path.dirname(cfg.results_dir), "..", "figures")
    figures_dir = os.path.normpath(figures_dir)
    visualize_module.generate_all_figures(
        results_df, cfg,
        analysis_result=analysis,
        figures_dir=figures_dir,
    )

    # Final Gate Report
    print(f"\n{'='*60}")
    print(f"GATE RESULT: {analysis['gate']['decision']}")
    print(f"  Window fraction: {analysis['window_fraction']:.3f} (threshold: {cfg.gate.min_window_fraction})")
    print(f"  p-value:         {analysis['p_value']:.4f} (threshold: {cfg.gate.p_threshold})")
    print(f"  t* mean:         {analysis['t_star_mean']:.1f} epochs")
    print(f"{'='*60}\n")

    print("EXPERIMENT COMPLETE")
    return analysis


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Experiment")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--device", default="cuda:0", help="Device (cuda:0, cpu)")
    parser.add_argument("--skip-train", action="store_true",
                        help="Skip training, use existing checkpoints")
    args = parser.parse_args()
    main(args.config, args.device, skip_train=args.skip_train)
