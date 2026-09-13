"""Main experiment orchestration for H-C2: NFN vs Statistics crossing point."""
import json
import time
from pathlib import Path
from typing import List

import config
from data import download_model_zoo, load_checkpoints, split_test_set
from sweep import run_sweep
from crossing_analysis import aggregate_by_n, find_crossing_point, crossing_point_report


def main(n_values: List[int] = None, seeds: List[int] = None) -> dict:
    """Run full H-C2 experiment: sweep + crossing analysis + figures."""
    if n_values is None:
        n_values = config.N_VALUES
    if seeds is None:
        seeds = config.CONFIG.train.seeds

    cfg = config.CONFIG
    t0 = time.time()

    print("Loading model zoo...")
    zoo_path = download_model_zoo(cfg.data.zoo_dir)
    items = load_checkpoints(zoo_path)
    train_pool, test_items = split_test_set(items, cfg.data.n_test, cfg.data.split_seed)
    print(f"Train pool: {len(train_pool)}, Test: {len(test_items)}")

    print(f"\nRunning sweep: N={n_values}, seeds={seeds}")
    results = run_sweep(train_pool, test_items, n_values, seeds)

    print("\nAggregating results...")
    agg = aggregate_by_n(results)

    print("\nFinding crossing point...")
    n_star = find_crossing_point(agg, threshold=0.03)
    report = crossing_point_report(agg, n_star, max_n=2500)

    print(f"\n{'='*60}")
    print("H-C2 GATE CHECK (SHOULD_WORK)")
    print(f"{'='*60}")
    print(f"Crossing point N*: {n_star}")
    print(f"Gate result: {report['gate_result']}")
    print(f"Message: {report['message']}")
    print()
    for n in sorted(agg.keys()):
        a = agg[n]
        print(f"N={n:4d}: NFN R²={a['mean_r2_nfn']:.4f}±{a['std_r2_nfn']:.4f}, "
              f"Stats R²={a['mean_r2_stats']:.4f}±{a['std_r2_stats']:.4f}, "
              f"Delta={a['delta']:+.4f}")
    print(f"{'='*60}")

    print("\nGenerating figures...")
    figures_dir = cfg.figures_dir
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    try:
        from evaluate import (
            plot_crossing_point,
            plot_learning_curves,
            plot_r2_bars,
        )
        plot_crossing_point(agg, n_star, f"{figures_dir}/crossing_point.png")
        plot_learning_curves(agg, f"{figures_dir}/learning_curves.png")
        plot_r2_bars(agg, f"{figures_dir}/r2_bars.png")
        print(f"Figures saved to {figures_dir}/")
    except ImportError as e:
        print(f"Warning: Could not generate figures - {e}")

    results_dir = cfg.results_dir
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    output = {
        "results": results,
        "aggregated": report["aggregated"],
        "n_star": n_star,
        "gate_result": report["gate_result"],
        "message": report["message"],
        "elapsed_sec": time.time() - t0,
    }
    with open(f"{results_dir}/results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {results_dir}/results.json")

    print(f"\nTotal time: {output['elapsed_sec']:.1f}s")
    return output


if __name__ == "__main__":
    main()
