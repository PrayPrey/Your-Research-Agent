#!/usr/bin/env python3
"""h-m2: Sample efficiency experiment - DWS vs NFT locality bias."""

import json
from pathlib import Path

from config import Config
from run_sweep import run_sweep
from metrics import aggregate_stats, gap_closure, check_success_criteria
from visualize import (
    plot_learning_curves,
    plot_25pct_bar,
    plot_gap_closure,
    plot_auc_boxplots,
    plot_gate_metrics,
)


def main():
    cfg = Config()
    Path(cfg.fig_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_path).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("h-m2: Sample Efficiency Experiment")
    print("Testing: DWS locality bias -> sample efficiency advantage")
    print("=" * 60)

    # Run 27 training experiments
    results = run_sweep(cfg)

    # Aggregate stats
    stats = aggregate_stats(results)

    # Compute gap closure
    dws_aucs = {f: stats[f]['dws']['auc_mean'] for f in cfg.fractions}
    nft_aucs = {f: stats[f]['nft']['auc_mean'] for f in cfg.fractions}
    gap = gap_closure(dws_aucs, nft_aucs)

    # Check success criteria
    criteria = check_success_criteria(stats, cfg)

    # Generate visualizations
    print("\nGenerating visualizations...")
    plot_learning_curves(stats, f"{cfg.fig_dir}/learning_curves.png")
    plot_25pct_bar(stats, f"{cfg.fig_dir}/bar_25pct.png")
    plot_gap_closure(gap, f"{cfg.fig_dir}/gap_closure.png")
    plot_auc_boxplots(results, f"{cfg.fig_dir}/auc_boxplots.png")
    plot_gate_metrics(stats, criteria, f"{cfg.fig_dir}/gate_metrics.png")

    # Save results
    output = {
        'raw_results': {str(k): v for k, v in results.items()},
        'stats': {str(k): v for k, v in stats.items()},
        'gap_closure': {str(k): v for k, v in gap.items()},
        'success_criteria': criteria,
        'gate_verdict': 'PASS' if criteria['dws_gt_nft_at_25pct'] and criteria['both_gt_mlp'] else 'FAIL',
    }

    with open(cfg.results_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    print("\nAUC by (model, fraction):")
    for f in cfg.fractions:
        print(f"\n  {f*100:.0f}% data:")
        for m in ['mlp', 'dws', 'nft']:
            s = stats[f][m]
            print(f"    {m.upper():4s}: {s['auc_mean']:.4f} ± {s['auc_std']:.4f}")

    print("\nGap (DWS - NFT):")
    for f, g in gap.items():
        print(f"  {f*100:.0f}%: {g:+.4f}")

    print("\nSuccess Criteria:")
    for k, v in criteria.items():
        status = "✓" if v else "✗"
        print(f"  {status} {k}: {v}")

    print(f"\nGATE VERDICT: {output['gate_verdict']}")
    print(f"\nResults saved to: {cfg.results_path}")
    print(f"Figures saved to: {cfg.fig_dir}/")


if __name__ == "__main__":
    main()
