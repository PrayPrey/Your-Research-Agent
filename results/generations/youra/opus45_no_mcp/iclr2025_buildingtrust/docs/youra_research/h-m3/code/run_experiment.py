#!/usr/bin/env python3
"""H-M3 Experiment Runner - Positional Analysis of Marker-Confidence Ordering."""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import H_M3_Config
from data_loader import load_h_m2_cache
from positional_analysis import analyze_all_outputs
from gate_metrics import compute_gate_metrics
from visualization import plot_gate_comparison


def run_h_m3_experiment(config: H_M3_Config = None) -> dict:
    """Run complete H-M3 positional analysis experiment."""
    if config is None:
        config = H_M3_Config()

    print(f"[H-M3] Loading H-M2 cache from: {config.h_m2_cache_path}")
    outputs = load_h_m2_cache(config.h_m2_cache_path)
    print(f"[H-M3] Loaded {len(outputs)} outputs")

    print("[H-M3] Analyzing positional relationships...")
    analyses = analyze_all_outputs(outputs, config.cot_position_threshold)

    print("[H-M3] Computing gate metrics...")
    gate_metrics = compute_gate_metrics(
        analyses,
        config.gate_1_threshold,
        config.gate_2_threshold
    )

    print("[H-M3] Generating visualization...")
    fig_path = config.figures_dir / 'gate_comparison.png'
    plot_gate_comparison(gate_metrics, fig_path, config.figure_dpi)
    print(f"[H-M3] Saved figure: {fig_path}")

    results = {
        'hypothesis_id': config.hypothesis_id,
        'hypothesis_type': config.hypothesis_type,
        'experiment_date': datetime.now().isoformat(),
        'gate_metrics': gate_metrics,
        'analysis_summary': {
            'total_analyzed': len(analyses),
            'with_confidence': sum(1 for a in analyses if a.has_confidence),
            'with_markers': sum(1 for a in analyses if len(a.hedging_markers) > 0),
            'cot_order_correct': gate_metrics['cot_order_count'],
        },
        'config': {
            'gate_1_threshold': config.gate_1_threshold,
            'gate_2_threshold': config.gate_2_threshold,
            'cot_position_threshold': config.cot_position_threshold,
        }
    }

    results_path = config.output_dir / 'h-m3_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[H-M3] Saved results: {results_path}")

    gate_path = config.output_dir / 'gate_metrics.yaml'
    with open(gate_path, 'w') as f:
        yaml.dump(gate_metrics, f, default_flow_style=False)
    print(f"[H-M3] Saved gate metrics: {gate_path}")

    print(f"\n[H-M3] === Results ===")
    print(f"  CoT Order Rate: {gate_metrics['cot_order_rate']:.2%} (threshold: >{gate_metrics['gate_1_threshold']:.0%})")
    print(f"  Markers Precede Rate: {gate_metrics['markers_precede_rate']:.2%} (threshold: >{gate_metrics['gate_2_threshold']:.0%})")
    print(f"  Gate 1 Pass: {gate_metrics['gate_1_pass']}")
    print(f"  Gate 2 Pass: {gate_metrics['gate_2_pass']}")
    print(f"  ALL GATES PASS: {gate_metrics['all_gates_pass']}")

    return results


if __name__ == '__main__':
    results = run_h_m3_experiment()
    sys.exit(0 if results['gate_metrics']['all_gates_pass'] else 1)
