"""Gate evaluation: Entropy reduction, Fisher increase, monotonicity"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict
from config import CONFIG


def compute_entropy_reduction(metrics_log: pd.DataFrame) -> float:
    """(baseline - full_curation) / baseline * 100"""
    baseline = metrics_log[metrics_log['condition'] == 'baseline'].iloc[-1]
    full_curation = metrics_log[metrics_log['condition'] == 'full_curation'].iloc[-1]

    reduction = 100 * (baseline['entropy'] - full_curation['entropy']) / baseline['entropy']
    return reduction


def compute_fisher_increase(metrics_log: pd.DataFrame) -> float:
    """(full_curation - baseline) / baseline * 100"""
    baseline = metrics_log[metrics_log['condition'] == 'baseline'].iloc[-1]
    full_curation = metrics_log[metrics_log['condition'] == 'full_curation'].iloc[-1]

    increase = 100 * (full_curation['fisher_trace'] - baseline['fisher_trace']) / baseline['fisher_trace']
    return increase


def check_monotonicity(metrics_log: pd.DataFrame) -> Dict[str, bool]:
    """Check dedup/filter/mix dimensions."""
    # Dedup dimension
    dedup_conditions = ['baseline', 'dedup_low', 'dedup_high']
    dedup_entropies = [
        metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy']
        for c in dedup_conditions
    ]
    dedup_monotonic = all(
        dedup_entropies[i] >= dedup_entropies[i+1]
        for i in range(len(dedup_entropies)-1)
    )

    # Filter dimension
    filter_conditions = ['baseline', 'filter_med', 'filter_high']
    filter_entropies = [
        metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy']
        for c in filter_conditions
    ]
    filter_monotonic = all(
        filter_entropies[i] >= filter_entropies[i+1]
        for i in range(len(filter_entropies)-1)
    )

    # Mix dimension
    mix_conditions = ['baseline', 'mix_only']
    mix_entropies = [
        metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy']
        for c in mix_conditions
    ]
    mix_monotonic = mix_entropies[0] >= mix_entropies[1]

    return {
        "dedup": dedup_monotonic,
        "filter": filter_monotonic,
        "mix": mix_monotonic,
        "all": dedup_monotonic and filter_monotonic and mix_monotonic
    }


def evaluate_gate(metrics_log: pd.DataFrame) -> str:
    """PASS/PARTIAL/FAIL decision."""
    config = CONFIG.evaluation

    entropy_reduction = compute_entropy_reduction(metrics_log)
    fisher_increase = compute_fisher_increase(metrics_log)
    monotonicity = check_monotonicity(metrics_log)

    if (entropy_reduction > config.entropy_reduction_threshold * 100 and
        fisher_increase > config.fisher_increase_threshold * 100 and
        (monotonicity["all"] or not config.monotonicity_required)):
        return "PASS"
    elif entropy_reduction > 10 or fisher_increase > 10:
        return "PARTIAL"
    else:
        return "FAIL"


def plot_gate_metrics(results: Dict, save_path: str) -> None:
    """Bar chart: entropy reduction %, Fisher increase %"""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ['Entropy Reduction (%)', 'Fisher Increase (%)']
    values = [results['entropy_reduction'], results['fisher_increase']]
    thresholds = [20, 15]

    x = np.arange(len(metrics))
    bars = ax.bar(x, values, color=['#4CAF50', '#2196F3'])

    # Threshold lines
    for i, thresh in enumerate(thresholds):
        ax.axhline(y=thresh, color='red', linestyle='--', alpha=0.7, label=f'Threshold ({thresh}%)' if i == 0 else '')

    ax.set_ylabel('Percentage (%)')
    ax.set_title('H-M1 Gate Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {save_path}")


def evaluate_all_conditions(metrics_log: pd.DataFrame) -> Dict:
    """Main evaluation function. Returns: gate results dict"""
    results = {
        'entropy_reduction': compute_entropy_reduction(metrics_log),
        'fisher_increase': compute_fisher_increase(metrics_log),
        'monotonicity': check_monotonicity(metrics_log),
        'gate_result': evaluate_gate(metrics_log)
    }

    print("\n" + "="*60)
    print("GATE EVALUATION RESULTS")
    print("="*60)
    print(f"Entropy Reduction: {results['entropy_reduction']:.2f}% (threshold: 20%)")
    print(f"Fisher Increase: {results['fisher_increase']:.2f}% (threshold: 15%)")
    print(f"Monotonicity: {results['monotonicity']}")
    print(f"\nGate Result: {results['gate_result']}")
    print("="*60)

    # Generate plots
    plots_dir = Path(CONFIG.evaluation.plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    plot_gate_metrics(results, str(plots_dir / "gate_metrics.png"))

    return results
