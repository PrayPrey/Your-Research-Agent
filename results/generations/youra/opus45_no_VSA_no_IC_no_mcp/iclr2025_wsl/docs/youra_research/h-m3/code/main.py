import os
import json
from pathlib import Path

from config import ExperimentConfig
from synth_data import default_weight_shapes
from run_sweep import run_sweep
from metrics import aggregate_results, run_interaction_anova, check_success_criteria
from visualize import plot_gate_2x2_bar, plot_interaction, plot_training_curves, plot_diff_heatmap


def main():
    cfg = ExperimentConfig()
    cfg.weight_shapes = default_weight_shapes(cfg.hidden_dim)

    print("=" * 60)
    print("h-m3 Experiment: Architecture x Task Interaction")
    print("=" * 60)
    print(f"Tasks: {cfg.tasks}")
    print(f"Architectures: {cfg.architectures}")
    print(f"Seeds: {cfg.seeds}")
    print(f"Training: {cfg.n_train} samples, {cfg.epochs} epochs")
    print(f"Testing: {cfg.n_test} samples")
    print(f"Weight shapes: {cfg.weight_shapes}")
    print("=" * 60)

    results, histories = run_sweep(cfg)

    print("\n" + "=" * 60)
    print("Aggregating results...")
    print("=" * 60)

    stats = aggregate_results(results)
    for key, val in stats.items():
        print(f"  {key}: {val['mean']:.4f} +/- {val['std']:.4f}")

    print("\nRunning interaction ANOVA...")
    anova_result = run_interaction_anova(results)
    print(f"  F-stat: {anova_result['f_stat']:.4f}")
    print(f"  p-value: {anova_result['p_value']:.6f}")
    print(f"  Significant: {anova_result['significant']}")

    print("\nChecking success criteria...")
    criteria = check_success_criteria(stats, anova_result)
    for crit, passed in criteria.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {crit}: {status}")

    print("\nGenerating visualizations...")
    fig_dir = Path(cfg.fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)

    plot_gate_2x2_bar(stats, str(fig_dir / "gate_2x2_bar.png"))
    plot_interaction(stats, str(fig_dir / "interaction_plot.png"))
    plot_training_curves(histories, str(fig_dir / "training_curves.png"))
    plot_diff_heatmap(stats, "mlp", str(fig_dir / "diff_heatmap.png"))

    print(f"  Saved to {fig_dir}")

    output_dir = Path(cfg.results_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    results_data = {
        "hypothesis": "h-m3",
        "config": {
            "tasks": cfg.tasks,
            "architectures": cfg.architectures,
            "seeds": cfg.seeds,
            "n_train": cfg.n_train,
            "n_test": cfg.n_test,
            "epochs": cfg.epochs,
            "hidden_dim": cfg.hidden_dim,
        },
        "statistics": stats,
        "anova": anova_result,
        "success_criteria": {k: bool(v) for k, v in criteria.items()},
        "gate_result": "PASS" if all(criteria.values()) else "FAIL",
        "individual_results": [
            {
                "task": r.task,
                "architecture": r.architecture,
                "seed": r.seed,
                "metric_value": r.metric_value,
                "secondary_metric": r.secondary_metric,
                "train_time": r.train_time
            }
            for r in results
        ]
    }

    with open(cfg.results_path, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"\nResults saved to {cfg.results_path}")

    print("\n" + "=" * 60)
    overall = "PASS" if all(criteria.values()) else "FAIL"
    print(f"OVERALL GATE RESULT: {overall}")
    print("=" * 60)

    return results_data


if __name__ == "__main__":
    main()
