"""Main experiment runner for h-m-integrated: mechanism validation."""
import json
import sys
from pathlib import Path

# Add current dir first to avoid h-e1 import collision
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import DataManager
from mechanism_validator import UQMechanismValidator
import visualize


def main():
    """Run mechanism validation experiment."""
    print("=" * 80)
    print("H-M-INTEGRATED: UQ Mechanism Validation")
    print("=" * 80)

    # Setup paths
    base_dir = Path(__file__).parent
    h_e1_dir = base_dir.parent.parent / "h-e1" / "code"
    figures_dir = base_dir.parent / "figures"
    results_dir = base_dir.parent / "results"

    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # === 1. Load h-e1 Artifacts ===
    print("\n[1/5] Loading h-e1 artifacts...")
    dm = DataManager(h_e1_dir=str(h_e1_dir))

    try:
        h_e1_data = dm.load_h_e1_artifacts()
        print(f" Loaded {len(h_e1_data['labels'])} test samples")
        print(f" UQ methods: {list(h_e1_data['uq_scores'].keys())}")
    except FileNotFoundError as e:
        print(f" ERROR: {e}")
        print(" Run h-e1 experiment first to generate artifacts.")
        return False

    # === 2. Validate Mechanism ===
    print("\n[2/5] Validating UQ mechanism...")
    validator = UQMechanismValidator(
        uq_scores=h_e1_data["uq_scores"],
        labels=h_e1_data["labels"]
    )

    results = validator.validate_all_methods()

    # Print results
    print("\n  Method         | Spearman ρ | AUROC | AUSE  | Pass")
    print("  " + "-" * 60)
    for method, metrics in results.items():
        mark = "✓" if metrics["pass_gate"] else "✗"
        print(f"  {method:14s} | {metrics['spearman_rho']:10.3f} | "
              f"{metrics['auroc']:5.3f} | {metrics['ause']:5.3f} | {mark}")

    # === 3. Check Gate ===
    print("\n[3/5] Checking gate conditions...")
    gate_passed, reason = validator.check_gate(results)
    print(f" Gate result: {'PASSED' if gate_passed else 'FAILED'}")
    print(f" Reason: {reason}")

    # === 4. Generate Visualizations ===
    print("\n[4/5] Generating visualizations...")

    # Gate metrics scatter
    visualize.plot_gate_metrics_scatter(results, str(figures_dir / "gate_metrics_scatter.png"))
    print(" ✓ gate_metrics_scatter.png")

    # Spearman comparison
    visualize.plot_spearman_comparison(results, str(figures_dir / "spearman_comparison.png"))
    print(" ✓ spearman_comparison.png")

    # AUSE vs AUROC
    visualize.plot_ause_vs_auroc(results, str(figures_dir / "ause_vs_auroc.png"))
    print(" ✓ ause_vs_auroc.png")

    # Sparsification curves
    sparsification_data = {}
    for method in results.keys():
        sparsification_data[method] = validator.compute_sparsification_data(method)

    visualize.plot_sparsification_curves(sparsification_data, str(figures_dir / "sparsification_curves.png"))
    print(" ✓ sparsification_curves.png")

    # === 5. Save Results ===
    print("\n[5/5] Saving results...")

    # Save metrics
    metrics_file = results_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f" ✓ {metrics_file}")

    # Save sparsification data
    sparsification_file = results_dir / "sparsification.json"
    with open(sparsification_file, "w") as f:
        json.dump(sparsification_data, f, indent=2)
    print(f" ✓ {sparsification_file}")

    # Save summary
    summary = {
        "gate_passed": gate_passed,
        "gate_reason": reason,
        "n_methods": len(results),
        "n_passed": sum(1 for m in results.values() if m["pass_gate"] and not m["is_degenerate"]),
        "auroc_scores": {m: results[m]["auroc"] for m in results.keys()},
        "spearman_scores": {m: results[m]["spearman_rho"] for m in results.keys()}
    }

    summary_file = results_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f" ✓ {summary_file}")

    # === 6. Generate Validation Report ===
    print("\n[6/6] Generating validation report...")
    report_lines = []
    report_lines.append("# Validation Report: h-m-integrated")
    report_lines.append("")
    report_lines.append("## Gate Results")
    report_lines.append("")
    report_lines.append(f"**Gate Status:** {'PASSED ✓' if gate_passed else 'FAILED ✗'}")
    report_lines.append(f"**Reason:** {reason}")
    report_lines.append("")
    report_lines.append("### Method Results")
    report_lines.append("")
    report_lines.append("| Method | Spearman ρ | AUROC | AUSE | Pass |")
    report_lines.append("|--------|------------|-------|------|------|")

    for method, metrics in results.items():
        mark = "✓" if metrics["pass_gate"] else "✗"
        degen = " (degenerate)" if metrics["is_degenerate"] else ""
        report_lines.append(
            f"| {method}{degen} | {metrics['spearman_rho']:.3f} | "
            f"{metrics['auroc']:.3f} | {metrics['ause']:.3f} | {mark} |"
        )

    report_lines.append("")
    report_lines.append("## Figures")
    report_lines.append("")
    report_lines.append("- [Gate Metrics Scatter](figures/gate_metrics_scatter.png)")
    report_lines.append("- [Spearman Comparison](figures/spearman_comparison.png)")
    report_lines.append("- [AUSE vs AUROC](figures/ause_vs_auroc.png)")
    report_lines.append("- [Sparsification Curves](figures/sparsification_curves.png)")
    report_lines.append("")
    report_lines.append("## Reflection")
    report_lines.append("")

    if gate_passed:
        report_lines.append("Mechanism validation PASSED. All non-degenerate UQ methods "
                          "produce uncertainty scores that correlate with incorrectness. "
                          "Pipeline works end-to-end at 8B scale.")
    else:
        failed_methods = [m for m in results.keys()
                         if not results[m]["pass_gate"] and not results[m]["is_degenerate"]]
        report_lines.append(f"Mechanism validation FAILED. {len(failed_methods)} non-degenerate "
                          f"methods ({', '.join(failed_methods)}) failed both Spearman and AUROC "
                          "thresholds. UQ mechanism does not generalize at 8B scale.")

    report_file = base_dir.parent / "04_validation.md"
    with open(report_file, "w") as f:
        f.write("\n".join(report_lines))
    print(f" ✓ {report_file}")

    print("\n" + "=" * 80)
    print(f"EXPERIMENT COMPLETE: {'PASSED' if gate_passed else 'FAILED'}")
    print("=" * 80)

    return gate_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
