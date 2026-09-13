"""Report generation for validation."""

import os
from datetime import datetime


class ReportGenerator:
    """Generate validation report."""

    def __init__(self, output_dir, figures_dir):
        self.output_dir = output_dir
        self.figures_dir = figures_dir

    def check_gate_conditions(self, layer_aurocs, gate_threshold):
        """Check MUST_WORK gate conditions."""
        layers = sorted(layer_aurocs.keys())
        aurocs = [layer_aurocs[l] for l in layers]

        peak_auroc = max(aurocs)
        peak_layer = layers[aurocs.index(peak_auroc)]

        # Final layer (L32)
        final_layer = layers[-1]
        final_auroc = layer_aurocs[final_layer]

        # Check conditions
        drop = peak_auroc - final_auroc
        gate_satisfied = (
            peak_layer in [18, 24] and  # Peak at mid-layers
            drop >= gate_threshold  # Final layer drops by threshold
        )

        return {
            'gate_type': 'MUST_WORK',
            'satisfied': gate_satisfied,
            'peak_layer': peak_layer,
            'peak_auroc': peak_auroc,
            'final_layer': final_layer,
            'final_auroc': final_auroc,
            'drop': drop,
            'threshold': gate_threshold,
            'reason': (
                f"Peak AUROC {peak_auroc:.4f} at L{peak_layer}, "
                f"Final L{final_layer} AUROC {final_auroc:.4f}, "
                f"Drop = {drop:.4f} {'≥' if drop >= gate_threshold else '<'} {gate_threshold}"
            )
        }

    def generate_validation_report(self, results, hypothesis_id, hypothesis_dir):
        """Generate 04_validation.md report."""
        gate_result = results['gate']
        layer_results = results['layer_results']
        baseline_results = results['baseline_results']

        report_path = os.path.join(hypothesis_dir, '04_validation.md')

        with open(report_path, 'w') as f:
            f.write(f"# Validation Report: {hypothesis_id}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Hypothesis:** Probe AUROC peaks at mid-layers (L∈{{18,24}}) and drops ≥3% at final layer\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"**Gate Type:** {gate_result['gate_type']}\n")
            f.write(f"**Gate Result:** {'✅ PASS' if gate_result['satisfied'] else '❌ FAIL'}\n")
            f.write(f"**Peak Layer:** L{gate_result['peak_layer']} (AUROC = {gate_result['peak_auroc']:.4f})\n")
            f.write(f"**Final Layer:** L{gate_result['final_layer']} (AUROC = {gate_result['final_auroc']:.4f})\n")
            f.write(f"**Drop:** {gate_result['drop']:.4f} (Threshold: {gate_result['threshold']})\n\n")

            # Results
            f.write("## Layer-wise Results\n\n")
            f.write("| Layer | AUROC | Notes |\n")
            f.write("|-------|-------|-------|\n")
            for layer in sorted(layer_results.keys()):
                auroc = layer_results[layer]['auroc']
                note = "🏆 Peak" if layer == gate_result['peak_layer'] else ""
                note += " 🔴 Final" if layer == gate_result['final_layer'] else ""
                f.write(f"| L{layer} | {auroc:.4f} | {note} |\n")
            f.write("\n")

            # Baselines
            f.write("## Baseline Comparison\n\n")
            f.write("| Method | AUROC |\n")
            f.write("|--------|-------|\n")
            for method, auroc in baseline_results.items():
                f.write(f"| {method} | {auroc:.4f} |\n")
            f.write("\n")

            # Gate Analysis
            f.write("## Gate Analysis\n\n")
            f.write(f"**Condition 1:** Peak at L18 or L24\n")
            condition1 = gate_result['peak_layer'] in [18, 24]
            f.write(f"- Result: {'✅ PASS' if condition1 else '❌ FAIL'} (Peak at L{gate_result['peak_layer']})\n\n")

            f.write(f"**Condition 2:** Final layer drop ≥ {gate_result['threshold']}\n")
            condition2 = gate_result['drop'] >= gate_result['threshold']
            f.write(f"- Result: {'✅ PASS' if condition2 else '❌ FAIL'} (Drop = {gate_result['drop']:.4f})\n\n")

            # Figures
            f.write("## Visualizations\n\n")
            f.write("![Layer AUROC Comparison](figures/layer_auroc_comparison.png)\n\n")
            f.write("![ROC Curves](figures/roc_curves.png)\n\n")
            f.write("![Confusion Matrices](figures/confusion_matrices.png)\n\n")

            # Conclusion
            f.write("## Conclusion\n\n")
            if gate_result['satisfied']:
                f.write("The experiment successfully validated the hypothesis. ")
                f.write("Probe AUROC peaks at mid-layers and shows the required drop at the final layer. ")
                f.write("This supports the claim that uncertainty information is encoded in mid-layer representations.\n")
            else:
                f.write("The experiment failed to validate the hypothesis. ")
                if not condition1:
                    f.write(f"Peak AUROC was at L{gate_result['peak_layer']}, not at mid-layers (L18 or L24). ")
                if not condition2:
                    f.write(f"Final layer drop ({gate_result['drop']:.4f}) was less than threshold ({gate_result['threshold']}). ")
                f.write("\n\n**Recommendation:** Review hypothesis assumptions or experimental setup.\n")

        print(f"\nValidation report saved to: {report_path}")
        return report_path
