#!/usr/bin/env python3
import os
import json
import csv
from config import CONFIG
from train import train
from visualize import (
    plot_wga_curve, plot_second_derivative, plot_multi_benchmark,
    plot_smoothing_sensitivity, plot_group_divergence
)

def main():
    os.makedirs(CONFIG.output_dir, exist_ok=True)
    figures_dir = "../figures"
    os.makedirs(figures_dir, exist_ok=True)

    all_results = {}
    all_histories = {}
    success_count = 0

    for dataset_name in CONFIG.datasets:
        print(f"\n{'='*50}")
        print(f"Training on {dataset_name}")
        print(f"{'='*50}")

        result = train(dataset_name, CONFIG)
        wga_history = result["wga_history"]
        group_acc_history = result["group_acc_history"]
        detector = result["detector"]

        peak_epoch, peak_magnitude, is_significant = detector.detect_crystallization_peak(
            CONFIG.detection_threshold
        )

        print(f"\nResults for {dataset_name}:")
        print(f"  Peak epoch: {peak_epoch}")
        print(f"  Peak magnitude: {peak_magnitude:.6f}")
        print(f"  Significant (< {CONFIG.detection_threshold}): {is_significant}")

        if is_significant:
            success_count += 1

        all_results[dataset_name] = {
            "wga_history": wga_history,
            "peak_epoch": peak_epoch,
            "peak_magnitude": peak_magnitude,
            "is_significant": is_significant,
            "final_wga": wga_history[-1] if wga_history else None,
            "group_acc_final": group_acc_history[-1] if group_acc_history else {}
        }
        all_histories[dataset_name] = wga_history

        d2 = detector.compute_second_derivative()
        plot_wga_curve(wga_history, peak_epoch, os.path.join(figures_dir, f"{dataset_name}_wga.png"))
        plot_second_derivative(d2, peak_epoch, os.path.join(figures_dir, f"{dataset_name}_d2.png"))
        plot_group_divergence(group_acc_history, os.path.join(figures_dir, f"{dataset_name}_groups.png"))
        plot_smoothing_sensitivity(wga_history, CONFIG.ablation_smoothing_windows,
                                   os.path.join(figures_dir, f"{dataset_name}_smoothing.png"))

    plot_multi_benchmark(all_histories, os.path.join(figures_dir, "multi_benchmark.png"))

    overall_success = success_count >= 2
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS")
    print(f"{'='*50}")
    print(f"Datasets with significant crystallization: {success_count}/{len(CONFIG.datasets)}")
    print(f"Success criteria (2/3 benchmarks): {'PASS' if overall_success else 'FAIL'}")

    experiment_results = {
        "hypothesis": "H-E1",
        "success": overall_success,
        "datasets": all_results,
        "success_count": success_count,
        "total_datasets": len(CONFIG.datasets),
        "threshold": CONFIG.detection_threshold,
        "smoothing_window": CONFIG.smoothing_window
    }

    with open(os.path.join(CONFIG.output_dir, "experiment_results.json"), "w") as f:
        json.dump(experiment_results, f, indent=2)

    with open(os.path.join(CONFIG.output_dir, "results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "epoch", "wga", "peak_epoch", "peak_magnitude", "significant"])
        for ds, data in all_results.items():
            for epoch, wga in enumerate(data["wga_history"]):
                writer.writerow([ds, epoch, wga, data["peak_epoch"], data["peak_magnitude"], data["is_significant"]])

    return experiment_results

if __name__ == "__main__":
    main()
