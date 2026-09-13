"""
Evaluation and visualization for h-e2.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from config import POC_GATE, PLOT_CONFIG


def check_poc_pass(results: dict, variance_threshold: float = 0.7) -> bool:
    """
    PoC gate: V_s/V_c < 0.7 AND F_s < F_c (directional only, no stats).

    results: output from run_single_experiment_with_tracking
    Returns: True if both conditions met
    """
    variance_ok = results['variance_ratio'] < variance_threshold
    forgetting_ok = results['forgetting_spurious'] < results['forgetting_core']

    return variance_ok and forgetting_ok


def plot_gate_metrics(results: dict, output_path: str):
    """
    Bar chart: variance_ratio, forgetting rates (spurious vs core).
    Saves to output_path.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Variance ratio
    axes[0].bar(['Variance Ratio'], [results['variance_ratio']], color=PLOT_CONFIG['color_spurious'])
    axes[0].axhline(POC_GATE['variance_ratio_max'], color='red', linestyle='--', label='Threshold (0.7)')
    axes[0].set_ylabel('V_spurious / V_core')
    axes[0].set_ylim(0, 1.2)
    axes[0].legend()
    axes[0].set_title('Gradient Variance Ratio')

    # Forgetting rates
    forgetting_data = [results['forgetting_spurious'], results['forgetting_core']]
    colors = [PLOT_CONFIG['color_spurious'], PLOT_CONFIG['color_core']]
    axes[1].bar(['Spurious', 'Core'], forgetting_data, color=colors)
    axes[1].set_ylabel('Forgetting Events per Sample')
    axes[1].set_title('Forgetting Rate Comparison')

    plt.tight_layout()
    plt.savefig(output_path, dpi=PLOT_CONFIG['dpi'])
    plt.close()
    print(f"  Saved gate metrics to {output_path}")


def plot_rolling_variance(results: dict, output_path: str):
    """
    Line plot: V_spurious(t), V_core(t) over epochs.
    x-axis: checkpoint epochs, y-axis: variance.
    """
    from config import GRADIENT_TRACKER_CONFIG
    epochs = GRADIENT_TRACKER_CONFIG['checkpoint_epochs']

    plt.figure(figsize=(8, 4))
    plt.plot(epochs, results['variance_spurious'], marker='o', label='Spurious',
             color=PLOT_CONFIG['color_spurious'], linewidth=2)
    plt.plot(epochs, results['variance_core'], marker='s', label='Core',
             color=PLOT_CONFIG['color_core'], linewidth=2)
    plt.xlabel('Epoch')
    plt.ylabel('Gradient Variance')
    plt.title('Rolling Gradient Variance Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=PLOT_CONFIG['dpi'])
    plt.close()
    print(f"  Saved rolling variance to {output_path}")


def generate_validation_report(results: dict, gate_passed: bool, output_path: str):
    """Generate markdown validation report."""
    with open(output_path, 'w') as f:
        f.write("# Validation Report: h-e2\n\n")
        f.write(f"**Dataset:** {results['dataset']}\n")
        f.write(f"**Seed:** {results['seed']}\n")
        f.write(f"**Gate Status:** {'PASS' if gate_passed else 'FAIL'}\n\n")

        f.write("## Convergence Metrics\n\n")
        f.write(f"- E_spurious: {results['E_spurious']} epochs\n")
        f.write(f"- E_core: {results['E_core']} epochs\n\n")

        f.write("## Gradient Variance Analysis\n\n")
        f.write(f"- Variance ratio (V_s/V_c): **{results['variance_ratio']:.4f}**\n")
        f.write(f"- Threshold: {POC_GATE['variance_ratio_max']}\n")
        f.write(f"- Status: {'✅ PASS' if results['variance_ratio'] < POC_GATE['variance_ratio_max'] else '❌ FAIL'}\n\n")

        f.write("### Per-Checkpoint Variances\n\n")
        f.write("| Epoch | V_spurious | V_core |\n")
        f.write("|-------|------------|--------|\n")
        from config import GRADIENT_TRACKER_CONFIG
        for i, epoch in enumerate(GRADIENT_TRACKER_CONFIG['checkpoint_epochs']):
            vs = results['variance_spurious'][i] if i < len(results['variance_spurious']) else 0.0
            vc = results['variance_core'][i] if i < len(results['variance_core']) else 0.0
            f.write(f"| {epoch} | {vs:.6f} | {vc:.6f} |\n")

        f.write("\n## Forgetting Event Analysis\n\n")
        f.write(f"- Forgetting (spurious): **{results['forgetting_spurious']:.4f}** events/sample\n")
        f.write(f"- Forgetting (core): **{results['forgetting_core']:.4f}** events/sample\n")
        forgetting_check = results['forgetting_spurious'] < results['forgetting_core']
        f.write(f"- Status: {'✅ PASS (F_s < F_c)' if forgetting_check else '❌ FAIL'}\n\n")

        f.write("## Gate Decision\n\n")
        if gate_passed:
            f.write("**RESULT: PASS**\n\n")
            f.write("Both conditions met:\n")
            f.write("1. Variance ratio < 0.7 ✅\n")
            f.write("2. Forgetting_spurious < Forgetting_core ✅\n")
        else:
            f.write("**RESULT: FAIL**\n\n")
            f.write("Gate conditions:\n")
            f.write(f"1. Variance ratio < 0.7: {'✅' if results['variance_ratio'] < POC_GATE['variance_ratio_max'] else '❌'}\n")
            f.write(f"2. Forgetting_spurious < Forgetting_core: {'✅' if forgetting_check else '❌'}\n")

        f.write("\n## Figures\n\n")
        f.write("- Gate metrics: `figures/gate_metrics.png`\n")
        f.write("- Rolling variance: `figures/rolling_variance.png`\n")

    print(f"  Saved validation report to {output_path}")
