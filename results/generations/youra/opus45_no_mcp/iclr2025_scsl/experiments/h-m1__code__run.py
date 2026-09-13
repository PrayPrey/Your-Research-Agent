#!/usr/bin/env python3
import os
import json
import argparse

from config import Config, CONFIG
from train import train
from inflection import compute_inflection_epoch, correlate_with_wga
from visualize import (
    plot_wga_curve, plot_second_derivative, plot_gradient_ratio_timeline,
    plot_wga_gradient_overlay, plot_per_group_gradient_norms, plot_gate_metrics_comparison
)

def main():
    parser = argparse.ArgumentParser(description="H-M1 Gradient Starvation Mechanism")
    parser.add_argument("--data_root", type=str, default="./data")
    parser.add_argument("--output_dir", type=str, default="./outputs")
    parser.add_argument("--checkpoint_dir", type=str, default="./checkpoints")
    parser.add_argument("--figures_dir", type=str, default="../figures")
    args = parser.parse_args()

    cfg = Config(
        data_root=args.data_root,
        output_dir=args.output_dir,
        checkpoint_dir=args.checkpoint_dir
    )
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)

    print("=" * 60)
    print("H-M1: Gradient Starvation Mechanism Experiment")
    print("=" * 60)

    dataset_name = "waterbirds"
    print(f"\nTraining on {dataset_name}...")
    results = train(dataset_name, cfg)

    wga_history = results["wga_history"]
    detector = results["detector"]
    gradient_ratio_history = results["gradient_ratio_history"]
    group_norm_history = results["group_norm_history"]
    n_epochs = results["n_epochs"]

    print("\nDetecting crystallization peak...")
    wga_peak_epoch, peak_value, is_significant = detector.detect_crystallization_peak(cfg.detection_threshold)
    d2 = detector.compute_second_derivative()

    print("\nComputing gradient inflection...")
    inflection_epoch, d1 = compute_inflection_epoch(gradient_ratio_history, cfg.smoothing_window)

    print("\nCorrelation analysis...")
    correlation_result = correlate_with_wga(
        inflection_epoch, wga_peak_epoch, gradient_ratio_history, wga_history, n_epochs
    )

    print("\nGenerating figures...")
    plot_wga_curve(wga_history, wga_peak_epoch, os.path.join(args.figures_dir, "wga_curve.png"))
    plot_second_derivative(d2, wga_peak_epoch, os.path.join(args.figures_dir, "wga_d2.png"))
    plot_gradient_ratio_timeline(gradient_ratio_history, inflection_epoch,
                                 os.path.join(args.figures_dir, "gradient_ratio_timeline.png"))
    plot_wga_gradient_overlay(wga_history, gradient_ratio_history,
                              os.path.join(args.figures_dir, "wga_gradient_overlay.png"))
    plot_per_group_gradient_norms(group_norm_history,
                                  os.path.join(args.figures_dir, "per_group_gradient_norms.png"))
    plot_gate_metrics_comparison(correlation_result,
                                 os.path.join(args.figures_dir, "gate_metrics_comparison.png"))

    experiment_results = {
        "dataset": dataset_name,
        "n_epochs": n_epochs,
        "wga_history": wga_history,
        "gradient_ratio_history": gradient_ratio_history,
        "wga_peak_epoch": wga_peak_epoch,
        "wga_peak_value": peak_value,
        "wga_peak_significant": is_significant,
        "inflection_epoch": inflection_epoch,
        "correlation": correlation_result,
        "gate_result": "PASS" if correlation_result["gate_pass"] else "FAIL"
    }

    results_path = os.path.join(cfg.output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"WGA Crystallization Peak: epoch {wga_peak_epoch} (d²WGA/dt² = {peak_value:.4f})")
    print(f"Gradient Inflection: epoch {inflection_epoch}")
    print(f"Correlation (r): {correlation_result['r']:.4f}")
    print(f"P-value: {correlation_result['p_value']:.4f}")
    print(f"Temporal Precedence: {correlation_result['temporal_precedence']}")
    print(f"Gate Criteria: r > 0.7 AND inflection < {n_epochs//2}")
    print("=" * 60)
    gate_status = "PASS" if correlation_result["gate_pass"] else "FAIL"
    print(f"GATE RESULT: {gate_status}")
    print("=" * 60)

    return experiment_results

if __name__ == "__main__":
    main()
