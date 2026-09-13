"""Main experiment orchestration for H-M2."""
import json
import time
from pathlib import Path
from typing import List

import config
from data import download_model_zoo, load_checkpoints, split_test_set
from sweep import run_sweep
from stats import summarize_all
from evaluate import (
    plot_gate_comparison,
    plot_learning_curve,
    plot_seed_scatter,
    plot_box_distribution,
)


def main(n_values: List[int] = None, seeds: List[int] = None) -> dict:
    """Run full H-M2 experiment: sweep + stats + figures."""
    if n_values is None:
        n_values = config.N_VALUES
    if seeds is None:
        seeds = config.CONFIG.train.seeds

    cfg = config.CONFIG
    t0 = time.time()

    # Load data
    print("Loading model zoo...")
    zoo_path = download_model_zoo(cfg.data.zoo_dir)
    items = load_checkpoints(zoo_path)
    train_pool, test_items = split_test_set(items, cfg.data.n_test, cfg.data.split_seed)
    print(f"Train pool: {len(train_pool)}, Test: {len(test_items)}")

    # Run sweep
    print(f"\nRunning sweep: N={n_values}, seeds={seeds}")
    results = run_sweep(train_pool, test_items, n_values, seeds)

    # Statistics
    print("\nComputing statistics...")
    summary = summarize_all(results)

    # Gate check at PRIMARY_N
    gate = summary[config.PRIMARY_N]
    gate_pass = gate["pass"]
    print(f"\n=== GATE CHECK (N={config.PRIMARY_N}) ===")
    print(f"NFN R²: {gate['mean_r2_nfn']:.4f} ± {gate['std_r2_nfn']:.4f}")
    print(f"MLP R²: {gate['mean_r2_mlp']:.4f} ± {gate['std_r2_mlp']:.4f}")
    print(f"Delta:  {gate['mean_delta']:.4f} ± {gate['std_delta']:.4f}")
    print(f"p-value: {gate['p_value']:.4e}")
    print(f"PASS: {gate_pass} (target delta >= {config.R2_DELTA_TARGET}, p < {config.ALPHA})")

    # Figures
    print("\nGenerating figures...")
    figures_dir = cfg.figures_dir
    plot_gate_comparison(results, config.PRIMARY_N, f"{figures_dir}/gate_comparison.png")
    plot_learning_curve(results, n_values, f"{figures_dir}/learning_curve.png")
    plot_seed_scatter(results, config.PRIMARY_N, f"{figures_dir}/seed_scatter.png")
    plot_box_distribution(results, config.PRIMARY_N, f"{figures_dir}/box_distribution.png")
    print(f"Figures saved to {figures_dir}/")

    # Save results
    results_dir = cfg.results_dir
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    output = {
        "results": results,
        "summary": {str(k): v for k, v in summary.items()},
        "gate_n": config.PRIMARY_N,
        "gate_pass": gate_pass,
        "elapsed_sec": time.time() - t0,
    }
    with open(f"{results_dir}/results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {results_dir}/results.json")

    print(f"\nTotal time: {output['elapsed_sec']:.1f}s")
    return output


if __name__ == "__main__":
    main()
